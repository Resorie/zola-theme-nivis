const MATH_LANGS = new Set(['math', 'math-display', 'tex', 'latex']);
const SKIP_MATH = 'script, noscript, style, textarea, pre, code, math, select, option, mjx-container, .mathjax_ignore';

export function hasMath(text) {
  // Only gate the download; MathJax remains responsible for parsing TeX.
  const unescaped = text.replace(/\\\\|\\\$/g, '');
  return /\$\$[\s\S]*?\$\$|\$[^$]+?\$|\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]|\\begin\{[^}]+\}|\\(?:eq)?ref\{[^}]+\}/.test(unescaped);
}

function prepareMath(root) {
  root.querySelectorAll('pre code').forEach(code => {
    if (code.closest('.mathjax_ignore')) return;
    const pre = code.parentElement;
    const lang = pre.dataset.lang || code.dataset.lang || [...code.classList].find(name => name.startsWith('language-'))?.slice(9);
    if (!MATH_LANGS.has(lang?.toLowerCase())) return;
    const div = document.createElement('div');
    div.className = 'math-display';
    const text = code.textContent.trim();
    div.textContent = text.startsWith('$$') || text.startsWith('\\[') ? text : '$$' + text + '$$';
    pre.replaceWith(div);
  });

  root.querySelectorAll('code').forEach(code => {
    if (code.closest('pre, .mathjax_ignore')) return;
    const text = code.textContent.trim();
    if ((text.startsWith('$') && text.endsWith('$') && !text.startsWith('$$')) ||
        (text.startsWith('\\(') && text.endsWith('\\)'))) {
      const span = document.createElement('span');
      span.textContent = text;
      code.replaceWith(span);
    }
  });
}

function containsMath(root) {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      if (node.nodeType === Node.ELEMENT_NODE) {
        return node.matches(SKIP_MATH) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_SKIP;
      }
      return NodeFilter.FILTER_ACCEPT;
    },
  });
  const text = [];
  while (walker.nextNode()) text.push(walker.currentNode.textContent);
  return hasMath(text.join('\n'));
}

function loadMath(root) {
  if (!containsMath(root) || document.getElementById('MathJax-script')) return;
  window.MathJax = {
    tex: {
      inlineMath: [['$', '$'], ['\\(', '\\)']],
      displayMath: [['$$', '$$'], ['\\[', '\\]']],
      processEscapes: true,
      processEnvironments: true,
    },
    startup: { elements: [root] },
  };
  const script = document.createElement('script');
  script.id = 'MathJax-script';
  script.src = 'https://cdn.jsdelivr.net/npm/mathjax@4.1.3/tex-svg.js';
  script.async = true;
  script.addEventListener('error', () => console.warn('MathJax could not load; TeX source remains visible.'));
  // The DOM and all legacy wrappers are ready before automatic startup can run.
  document.head.append(script);
}

function prepareCode(root) {
  root.querySelectorAll('pre code').forEach(code => {
    const pre = code.parentElement;
    if (pre.querySelector('.code-header')) return;
    const lang = pre.dataset.lang || code.dataset.lang || [...code.classList].find(name => name.startsWith('language-'))?.slice(9);
    if (lang) pre.dataset.lang = lang;
    const header = document.createElement('div');
    header.className = 'code-header';
    const dots = document.createElement('span');
    dots.className = 'code-dots';
    dots.innerHTML = '<span></span><span></span><span></span>';
    const right = document.createElement('span');
    right.className = 'code-header-right';
    if (lang) {
      const label = document.createElement('span');
      label.className = 'code-lang';
      label.textContent = lang.toUpperCase();
      right.append(label);
    }
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'code-copy-btn';
    button.setAttribute('aria-label', 'Copy code');
    button.innerHTML = '<i class="fa-regular fa-copy"></i>';
    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(code.textContent);
        button.innerHTML = '<i class="fa-solid fa-check"></i>';
        setTimeout(() => { button.innerHTML = '<i class="fa-regular fa-copy"></i>'; }, 1500);
      } catch {
        button.title = 'Copy failed';
      }
    });
    right.append(button);
    header.append(dots, right);
    pre.insertBefore(header, code);
  });
}

function startMottos() {
  document.querySelectorAll('[data-mottos]').forEach(el => {
    const mottos = JSON.parse(el.dataset.mottos);
    if (!mottos?.length) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      el.textContent = mottos[0];
      return;
    }
    let index = 0, charIndex = 0, deleting = false, timer;
    function tick() {
      if (document.hidden) return;
      const current = mottos[index];
      charIndex += deleting ? -1 : 1;
      el.textContent = current.substring(0, charIndex);
      let delay = deleting ? 35 : 80 + Math.random() * 40;
      if (!deleting && charIndex >= current.length) {
        deleting = true;
        delay = 2500;
      } else if (deleting && charIndex <= 0) {
        deleting = false;
        index = (index + 1) % mottos.length;
        delay = 400;
      }
      timer = setTimeout(tick, delay);
    }
    document.addEventListener('visibilitychange', () => {
      clearTimeout(timer);
      if (!document.hidden) tick();
    });
    tick();
  });
}

if (typeof document !== 'undefined') {
  const root = document.querySelector('.content');
  if (root) {
    if (document.getElementById('content-script')?.dataset.mathjax === 'true') {
      prepareMath(root);
      loadMath(root);
    }
    prepareCode(root);
  }
  startMottos();
}
