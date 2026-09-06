import assert from 'node:assert/strict';
import test from 'node:test';
import { hasMath } from '../static/content.mjs';

test('recognizes the supported TeX delimiters, environments and references', () => {
  for (const text of ['$x$', '$$x^2$$', '$x\n+ y$', String.raw`\(x\)`, String.raw`\[x\]`,
    String.raw`\begin{align*}x &= y\end{align*}`, String.raw`\ref{eq:x}`, String.raw`\eqref{eq:x}`]) {
    assert.equal(hasMath(text), true, text);
  }
});

test('ordinary prose, single currency amounts and escaped delimiters do not load MathJax', () => {
  for (const text of ['', 'Ordinary prose.', 'Price: $5.', String.raw`Prices: \$5 and \$10.`,
    String.raw`\\(literal\\)`, String.raw`\\begin{literal}`]) {
    assert.equal(hasMath(text), false, text);
  }
});

test('escaped dollars inside math and an even number of preceding backslashes are handled', () => {
  assert.equal(hasMath(String.raw`$x + \$5$`), true);
  assert.equal(hasMath(String.raw`\\$x$`), true);
});
