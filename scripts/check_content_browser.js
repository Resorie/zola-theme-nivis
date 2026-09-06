// AIGC: run with Playwright's run-code after opening the built site's root URL.
async (page) => {
  const base = page.url().replace(/\/?$/, '/');
  const browser = page.context().browser();
  const context = await browser.newContext();
  const results = [];
  const check = (condition, message) => { if (!condition) throw new Error(message); };
  try {
    const template = await (await context.request.get(base + 'about/')).text();
    const fixturePage = await context.newPage();
    const scripts = await fixturePage.evaluate(html => {
      const doc = new DOMParser().parseFromString(html, 'text/html');
      const serialize = root => [...root.querySelectorAll('script')]
        .filter(script => !/instant\.page|search\.js|livereload/.test(script.src))
        .map(script => script.outerHTML).join('');
      return { head: serialize(doc.head), body: serialize(doc.body) };
    }, template);
    await fixturePage.close();
    const cases = [
      { name: 'prose and currency', html: '<p>Ordinary prose. Price: $5.</p>', math: false },
      { name: 'ordinary code', html: '<p><code>print("$x$")</code></p><pre><code>$x$</code></pre>', math: false },
      { name: 'ignored region', html: '<div class="mathjax_ignore"><p>$x$</p><pre data-lang="math"><code>x</code></pre></div>', math: false },
      { name: 'inline dollars', html: '<p><code>$x$</code> and $y$.</p>', math: true },
      { name: 'inline parentheses', html: String.raw`<p><code>\(x\)</code></p>`, math: true },
      { name: 'display wrappers', html: '<div class="math-display">$$&#120;^2$$</div>', math: true },
      { name: 'display brackets', html: String.raw`<p>\[x^2\]</p>`, math: true },
      { name: 'environments', html: String.raw`<p>\begin{align}x &= y\end{align}</p>`, math: true },
      { name: 'references', html: String.raw`<p>\eqref{eq:x}</p>`, math: true },
      { name: 'list summaries', html: '<div class="article-block"><p class="description">$x$</p></div>', math: true },
      { name: 'math disabled', html: '<p><code>$x$</code></p><pre data-lang="math"><code>x</code></pre>', math: false, disabled: true },
      { name: 'failed CDN', html: '<p><code>$x$</code></p><pre><code>plain code</code></pre>', math: true, fail: true },
      { name: 'background motto', html: '<p data-mottos=\'["A long motto for testing background timers."]\'></p>', math: false, motto: true },
      { name: 'reduced motion', html: '<p data-mottos=\'["A static motto."]\'></p>', math: false, reducedMotion: true },
    ];
    for (const language of ['math', 'math-display', 'tex', 'latex']) {
      cases.push({ name: language + ' fence', html: `<pre data-lang="${language}"><code>x^2</code></pre>`, math: true });
    }
    cases.push({ name: 'class-based fence', html: '<pre><code class="language-TeX">x^2</code></pre>', math: true });
    cases.push({ name: 'slow CDN', html: '<p><code>$x$</code></p><pre data-lang="math"><code>x^2</code></pre>', math: true, delay: 250 });

    for (const fixture of cases) {
      const p = await context.newPage();
      if (fixture.motto) {
        await p.addInitScript(() => {
          window.testHidden = false;
          Object.defineProperty(document, 'hidden', { get: () => window.testHidden });
        });
      }
      if (fixture.reducedMotion) await p.emulateMedia({ reducedMotion: 'reduce' });
      const errors = [];
      let requests = 0;
      p.on('pageerror', error => errors.push(error.message));
      await p.route('**/mathjax@*/tex-svg.js', async route => {
        requests++;
        if (fixture.fail) return route.abort();
        if (fixture.delay) await p.waitForTimeout(fixture.delay);
        await route.fulfill({ contentType: 'text/javascript', body: `
          const initial = window.MathJax;
          window.mathPasses = [];
          const record = () => {
            const root = document.querySelector('.content');
            mathPasses.push({
              fences: root.querySelectorAll('pre[data-lang="math"], pre[data-lang="math-display"], pre[data-lang="tex"], pre[data-lang="latex"], code.language-TeX').length,
              inlineCode: [...root.querySelectorAll('p code')].filter(e => e.textContent.startsWith('$') || e.textContent.startsWith('\\\\(')).length,
              contentOnly: initial.startup?.elements?.[0] === root,
            });
            return Promise.resolve();
          };
          MathJax.typesetPromise = record;
          const startup = () => { if (initial.startup?.typeset !== false) record(); };
          if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', startup);
          else startup();
        ` });
      });
      await p.route('**/__parse-gate__.js', async route => {
        await p.waitForTimeout(100);
        await route.fulfill({ contentType: 'text/javascript', body: '' });
      });
      const bodyScripts = fixture.disabled ? scripts.body.replace('data-mathjax="true"', 'data-mathjax="false"') : scripts.body;
      await p.route('**/__content-test__', route => route.fulfill({
        contentType: 'text/html',
        body: `<!doctype html><html><head>${scripts.head}</head><body><div class="content">${fixture.html}</div><script src="${base}__parse-gate__.js"></script>${bodyScripts}</body></html>`,
      }));
      await p.goto(base + '__content-test__', { waitUntil: 'networkidle' });
      const state = await p.evaluate(() => ({
        passes: window.mathPasses || [],
        headers: document.querySelectorAll('.code-header').length,
        text: document.querySelector('.content').textContent,
        code: document.querySelector('.content p code')?.textContent,
      }));
      check(errors.length === 0, fixture.name + ': ' + errors.join('; '));
      check(requests === Number(fixture.math), fixture.name + ': unexpected MathJax requests: ' + requests);
      check(state.passes.length === Number(fixture.math && !fixture.fail), fixture.name + ': unexpected typeset count');
      for (const pass of state.passes) {
        check(pass.fences === 0 && pass.inlineCode === 0, fixture.name + ': typeset ran before normalization');
        check(pass.contentOnly, fixture.name + ': typeset should be scoped to content');
      }
      if (fixture.disabled) check(state.code === '$x$', 'Disabled math should preserve code');
      if (fixture.fail) check(state.text.includes('$x$') && state.headers === 1, 'CDN failure must preserve source and code controls');
      if (fixture.motto) {
        const paused = await p.evaluate(() => {
          window.testHidden = true;
          document.dispatchEvent(new Event('visibilitychange'));
          return document.querySelector('[data-mottos]').textContent;
        });
        await p.waitForTimeout(250);
        check(await p.locator('[data-mottos]').textContent() === paused, 'Motto must pause in the background');
        await p.evaluate(() => {
          window.testHidden = false;
          document.dispatchEvent(new Event('visibilitychange'));
        });
        await p.waitForTimeout(150);
        check(await p.locator('[data-mottos]').textContent() !== paused, 'Motto must resume in the foreground');
      }
      if (fixture.reducedMotion) check(state.text === 'A static motto.', 'Reduced motion must render the complete first motto');
      results.push({ name: fixture.name, requests, passes: state.passes.length });
      await p.close();
    }
    return results;
  } finally {
    await context.close();
  }
}
