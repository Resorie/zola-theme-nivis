// AIGC: test runner only. Always use an isolated, headless browser.
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';

const [url, ...checks] = process.argv.slice(2);
if (!url || checks.length === 0) {
  throw new Error('Usage: node scripts/run_browser_checks.mjs SITE_ROOT CHECK.js [CHECK.js ...]');
}
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: 'domcontentloaded' });
  for (const filename of checks) {
    const source = await readFile(filename, 'utf8');
    const check = vm.runInNewContext('(' + source + '\n)', { URL }, { filename });
    console.log(JSON.stringify({ file: filename, results: await check(page) }));
  }
} finally {
  await browser.close();
}
