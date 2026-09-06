const container = document.querySelector('.site-search');

if (container) {
  const toggle = container.querySelector('#search-toggle');
  const form = container.querySelector('form');
  const input = container.querySelector('input');
  const clear = container.querySelector('.search-clear');
  const panel = container.querySelector('.search-panel');
  const status = container.querySelector('.search-status');
  const retry = container.querySelector('.search-retry');
  const list = container.querySelector('.search-results');
  let open = false;
  let composing = false;
  let pendingIndex;
  let timer;
  let revision = 0;
  let resultsQuery = '';

  function decodeText(value) {
    // Decode the index's HTML entities without inserting its content into the page.
    const textarea = document.createElement('textarea');
    textarea.innerHTML = value;
    return textarea.value;
  }

  function loadIndex() {
    if (!pendingIndex) {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 12000);
      pendingIndex = Promise.all([
        import('./search-core.mjs'),
        fetch(container.dataset.searchIndex, { signal: controller.signal }).then((response) => {
          if (!response.ok) throw new Error('Search index unavailable');
          return response.json();
        }).finally(() => clearTimeout(timeout)),
      ]).then(([core, data]) => ({
        index: core.createSearchIndex(data, container.dataset.searchBase, decodeText),
        excerpt: core.resultExcerpt,
      })).catch((error) => {
        pendingIndex = undefined;
        throw error;
      });
    }
    return pendingIndex;
  }

  function highlighted(text, query) {
    const fragment = document.createDocumentFragment();
    const lower = text.toLocaleLowerCase();
    const term = query.toLocaleLowerCase();
    let offset = 0;
    let index = lower.indexOf(term);
    while (term && index >= 0) {
      fragment.append(document.createTextNode(text.slice(offset, index)));
      const mark = document.createElement('mark');
      mark.textContent = text.slice(index, index + query.length);
      fragment.append(mark);
      offset = index + query.length;
      index = lower.indexOf(term, offset);
    }
    fragment.append(document.createTextNode(text.slice(offset)));
    return fragment;
  }

  async function search() {
    const query = input.value.trim();
    const current = ++revision;
    resultsQuery = '';
    list.replaceChildren();
    retry.hidden = true;
    clear.hidden = !input.value;
    panel.hidden = !open || !query;
    if (!open || !query || composing) return;
    status.textContent = 'Searching...';
    panel.setAttribute('aria-busy', 'true');
    try {
      const { index, excerpt } = await loadIndex();
      if (!open || current !== revision || query !== input.value.trim()) return;
      const results = index.search(query);
      status.textContent = results.length === 0 ? 'No results.'
        : results.length > 20 ? `Showing 20 of ${results.length} results`
        : `${results.length} ${results.length === 1 ? 'result' : 'results'}`;
      for (const result of results.slice(0, 20)) {
        const item = document.createElement('li');
        const link = document.createElement('a');
        link.href = result.item.url;
        const title = document.createElement('span');
        title.className = 'search-result-title';
        title.append(highlighted(result.item.title, query));
        const snippet = document.createElement('span');
        snippet.className = 'search-result-snippet';
        snippet.append(highlighted(excerpt(result, query), query));
        link.append(title, snippet);
        item.append(link);
        list.append(item);
      }
      resultsQuery = query;
    } catch {
      if (!open || current !== revision) return;
      status.textContent = 'Search could not load.';
      retry.hidden = false;
    } finally {
      if (current === revision) panel.setAttribute('aria-busy', 'false');
    }
  }

  function setOpen(value, restoreFocus = false) {
    open = value;
    revision++;
    clearTimeout(timer);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close search' : 'Search');
    toggle.title = open ? 'Close search' : 'Search';
    form.inert = !open;
    if (open) {
      window.setFeedOpen?.(false);
      window.setSidebarOpen?.(false);
      input.focus({ preventScroll: true });
      loadIndex().catch(() => {});
      search();
    } else {
      panel.hidden = true;
      if (restoreFocus) toggle.focus({ preventScroll: true });
    }
  }

  toggle.addEventListener('click', () => setOpen(!open, open));
  input.addEventListener('compositionstart', () => {
    composing = true;
    revision++;
    clearTimeout(timer);
    list.replaceChildren();
    panel.hidden = true;
  });
  input.addEventListener('compositionend', () => {
    composing = false;
    clearTimeout(timer);
    search();
  });
  input.addEventListener('input', () => {
    revision++;
    clearTimeout(timer);
    clear.hidden = !input.value;
    list.replaceChildren();
    panel.hidden = true;
    if (!composing) timer = setTimeout(search, 120);
  });
  clear.addEventListener('click', () => {
    input.value = '';
    search();
    input.focus();
  });
  retry.addEventListener('click', search);
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    if (!composing && resultsQuery === input.value.trim()) list.querySelector('a')?.click();
  });
  container.addEventListener('keydown', (event) => {
    if (event.isComposing || composing) return;
    if (event.key === 'Escape') {
      event.preventDefault();
      event.stopPropagation();
      setOpen(false, true);
    }
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      const links = [...list.querySelectorAll('a')];
      const active = links.indexOf(document.activeElement);
      const target = event.key === 'ArrowDown' ? links[Math.min(active + 1, links.length - 1)]
        : active <= 0 ? input : links[active - 1];
      if (target) {
        event.preventDefault();
        target.focus();
      }
    }
  });
  document.addEventListener('click', (event) => {
    if (open && !container.contains(event.target)) setOpen(false);
  }, true);
  container.addEventListener('focusout', (event) => {
    // Keep moving toolbar targets in place until a pointer click has completed.
    if (open && event.relatedTarget && !container.contains(event.relatedTarget) && !event.relatedTarget.matches(':active')) setOpen(false);
  });
}
