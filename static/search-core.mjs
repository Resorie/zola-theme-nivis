import Fuse from './vendor/fuse-7.1.0.min.mjs';

export function createSearchIndex(entries, baseUrl, decode = (value) => value) {
  if (!Array.isArray(entries)) throw new Error('Invalid search index');
  const base = new URL(baseUrl);
  const prefix = `${base.pathname.replace(/\/$/, '')}/`;
  const documents = entries.flatMap((entry) => {
    if (!entry || typeof entry.url !== 'string') return [];
    let url;
    try { url = new URL(entry.url); } catch { return []; }
    if (!['http:', 'https:'].includes(url.protocol) || url.origin !== base.origin || !url.pathname.startsWith(prefix)) return [];
    return [{
      url: url.href,
      title: decode(String(entry.title || url.pathname)),
      description: decode(String(entry.description || '')),
      body: decode(String(entry.body || '')),
    }];
  });
  return new Fuse(documents, {
    keys: [{ name: 'title', weight: 0.55 }, { name: 'description', weight: 0.25 }, { name: 'body', weight: 0.2 }],
    includeMatches: true,
    ignoreLocation: true,
    ignoreFieldNorm: true,
    threshold: 0.25,
  });
}

export function resultExcerpt(result, query, length = 160) {
  const bodyMatch = result.matches?.find((match) => match.key === 'body');
  const descriptionMatch = result.matches?.find((match) => match.key === 'description');
  const useBody = bodyMatch && !descriptionMatch;
  const value = useBody ? result.item.body : result.item.description || result.item.body;
  const match = descriptionMatch || bodyMatch;
  const exact = value.toLocaleLowerCase().indexOf(query.toLocaleLowerCase());
  const position = exact >= 0 ? exact : match?.indices?.[0]?.[0] || 0;
  let start = Math.max(0, position - 40);
  for (const separator of ['\n', '\u3002', '. ']) {
    const boundary = value.lastIndexOf(separator, Math.max(0, position - 1));
    if (boundary >= start && boundary < position) start = boundary + separator.length;
  }
  let excerpt = Array.from(value.slice(start)).slice(0, length).join('');
  if (useBody) {
    const end = excerpt.slice(position - start + query.length).search(/[\n\u3002]|\. /);
    if (end >= 0) excerpt = excerpt.slice(0, position - start + query.length + end + 1);
  }
  return `${start > 0 ? '...' : ''}${excerpt}${start + excerpt.length < value.length ? '...' : ''}`;
}
