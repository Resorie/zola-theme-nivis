import assert from 'node:assert/strict';
import test from 'node:test';
import { createSearchIndex, resultExcerpt } from '../static/search-core.mjs';

const base = 'https://example.org/blog';
const doc = (name, fields = {}) => ({ url: `${base}/${name}/`, title: name, ...fields });

test('title matches rank above the same term in body text', () => {
  const index = createSearchIndex([doc('Other', { body: 'Montgomery' }), doc('Montgomery')], base);
  assert.equal(index.search('Montgomery')[0].item.title, 'Montgomery');
});

test('Chinese phrases and matches at the end of a long article are retained', () => {
  const body = 'Ordinary text. '.repeat(2000) + '\u79bb\u6563\u5bf9\u6570 Pohlig-Hellman';
  const index = createSearchIndex([doc('Long article', { body })], base);
  assert.equal(index.search('\u79bb\u6563\u5bf9\u6570').length, 1);
  const match = index.search('Pohlig-Hellman')[0];
  assert.ok(resultExcerpt(match, 'Pohlig-Hellman').includes('Pohlig-Hellman'));
  assert.ok(resultExcerpt(match, 'Pohlig-Hellman').length <= 166);
});

test('description is searchable and provides a useful excerpt', () => {
  const index = createSearchIndex([doc('Title', { description: 'Quadratic sieve', body: 'Unrelated body.' })], base);
  const result = index.search('Quadratic')[0];
  assert.equal(resultExcerpt(result, 'Quadratic'), 'Quadratic sieve');
});

test('a matching description is preferred to a formula-heavy body excerpt', () => {
  const index = createSearchIndex([doc('Title', { description: 'Pohlig-Hellman algorithm', body: '$x = y$ Pohlig-Hellman $z = w$' })], base);
  const result = index.search('Pohlig-Hellman')[0];
  assert.equal(resultExcerpt(result, 'Pohlig-Hellman'), 'Pohlig-Hellman algorithm');
});

test('body excerpts use nearby sentence boundaries', () => {
  const body = '\u524d\u6587\u3002\u8fd9\u662f\u79bb\u6563\u5bf9\u6570\u7684\u5b9a\u4e49\u3002 $x = y$';
  const result = createSearchIndex([doc('Title', { body })], base).search('\u79bb\u6563\u5bf9\u6570')[0];
  assert.ok(resultExcerpt(result, '\u79bb\u6563\u5bf9\u6570').includes('\u8fd9\u662f\u79bb\u6563\u5bf9\u6570\u7684\u5b9a\u4e49\u3002'));
  assert.ok(!resultExcerpt(result, '\u79bb\u6563\u5bf9\u6570').includes('$x'));
});

test('search ignores letter case and tolerates a small typo', () => {
  const index = createSearchIndex([doc('Montgomery')], base);
  assert.equal(index.search('MONTGOMERY').length, 1);
  assert.equal(index.search('Montgomry').length, 1);
  assert.equal(index.search('unrelatedterm').length, 0);
});

test('result URLs stay within the current site and base path', () => {
  const index = createSearchIndex([
    doc('Needle'),
    { url: 'javascript:alert(1)', title: 'Needle' },
    { url: 'https://elsewhere.test/blog/', title: 'Needle' },
    { url: 'https://example.org/blog-other/', title: 'Needle' },
    { url: 'not a URL', title: 'Needle' },
    null,
  ], base);
  assert.equal(index.search('Needle').length, 1);
});

test('optional text decoding is applied before matching', () => {
  const index = createSearchIndex([doc('Title', { description: 'A &amp; B' })], base, value => value.replaceAll('&amp;', '&'));
  assert.equal(index.search('A & B')[0].item.description, 'A & B');
});

test('malformed index data fails instead of being silently accepted', () => {
  assert.throws(() => createSearchIndex({}, base), /Invalid search index/);
});

test('empty index and absent optional fields are supported', () => {
  assert.deepEqual(createSearchIndex([], base).search('anything'), []);
  assert.equal(createSearchIndex([doc('Minimal')], base).search('Minimal').length, 1);
});
