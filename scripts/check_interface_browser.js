// AIGC: headless checks for the shared topbar, loading hints and 404 behavior.
async (page) => {
  const base = page.url().replace(/\/?$/, '/');
  const context = await page.context().browser().newContext({ reducedMotion: 'reduce' });
  const results = [];
  const check = (value, message) => { if (!value) throw new Error(message); };
  try {
    const p = await context.newPage();
    const errors = [];
    p.on('pageerror', error => errors.push(error.message));
    await p.route('**/topbar.js?*', async route => {
      await p.waitForTimeout(100);
      await route.continue();
    });
    for (const path of ['about/', '404.html']) {
      await p.setViewportSize({ width: 390, height: 844 });
      await p.goto(base + path, { waitUntil: 'networkidle' });
      const theme = p.getByRole('button', { name: 'Toggle theme', exact: true });
      const initial = await theme.getAttribute('aria-pressed');
      await theme.click();
      check(await theme.getAttribute('aria-pressed') !== initial, path + ': theme toggle');
      const scheme = await p.evaluate(() => document.documentElement.style.colorScheme);
      await p.reload({ waitUntil: 'networkidle' });
      check(await p.evaluate(() => document.documentElement.style.colorScheme) === scheme, path + ': persisted scheme');
      const sidebar = p.getByRole('button', { name: 'Toggle sidebar', exact: true });
      await sidebar.click();
      check(await sidebar.getAttribute('aria-expanded') === 'true', path + ': sidebar opens');
      check(await p.locator('#sidebar').evaluate(el => !el.inert), path + ': sidebar becomes focusable');
      await p.keyboard.press('Escape');
      check(await sidebar.getAttribute('aria-expanded') === 'false', path + ': sidebar closes');
      const feed = p.locator('.feed-icon');
      await feed.click();
      check(await feed.getAttribute('aria-expanded') === 'true', path + ': feed opens');
      await p.keyboard.press('Escape');
      check(await feed.getAttribute('aria-expanded') === 'false', path + ': feed closes');
      await p.getByRole('button', { name: 'Search', exact: true }).click();
      await p.getByRole('searchbox').fill('Montgomery');
      await p.locator('.search-results a').first().waitFor();
      check(await p.locator('.search-results a').count() > 0, path + ': search still works');
      await p.keyboard.press('Escape');
      check(await p.locator('#search-toggle').getAttribute('aria-expanded') === 'false', path + ': search closes');
      if (path === '404.html') {
        const original = await p.locator('#tail').getAttribute('d');
        await p.waitForTimeout(150);
        check(await p.locator('#tail').getAttribute('d') === original, '404 respects reduced motion');
      }
      results.push({ path, controls: 'passed' });
    }
    await p.goto(base + 'posts/mogic/', { waitUntil: 'networkidle' });
    await p.evaluate(() => window.MathJax?.startup?.promise);
    for (const width of [390, 1440, 3440]) {
      await p.setViewportSize({ width, height: 1080 });
      await p.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
      const state = await p.evaluate(() => ({
        article: document.querySelector('.content-article').getBoundingClientRect().width,
        width: document.documentElement.scrollWidth,
        formulas: document.querySelectorAll('mjx-container').length,
        errors: document.querySelectorAll('mjx-merror').length,
      }));
      check(state.width <= width && state.article <= 1024.1, 'Layout overflow at ' + width);
      check(state.article > 0, 'Empty article layout at ' + width);
      check(state.formulas > 0 && state.errors === 0, 'Math rendering at ' + width);
      await p.screenshot({ path: '/tmp/nivis-performance-' + width + '.png' });
      results.push({ viewport: width, ...state });
    }
    check(errors.length === 0, errors.join('; '));
    return results;
  } finally {
    await context.close();
  }
}
