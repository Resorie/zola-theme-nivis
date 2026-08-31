+++
title = "Configuration"
description = "configuration guide"
date = 1980-01-01

[taxonomies]
tags = ["guide"]

[extra]
toc = true
+++

## Social Links

Nivis enables you to display some of your social links . Add your social links in `config.toml` according to the following example:

```toml
[extra]
social_links = [
    { name = "github", url = "https://github.com/username" },
    { name = "email", url = "mailto:your@email.com" },
    { name = "twitter", url = "https://twitter.com/username" },
    { name = "rss", url = "/atom.xml" },
]
```

Supported icons include most brands (e.g., `github`, `twitter`, `bilibili`) and generic names like `email`, `rss`, `link`, `globe`.

## Site Footer

The optional copyright line appears below the Nivis and Zola credits. It is hidden unless you provide a holder:

```toml
[extra.footer]
copyright_holder = "Your name"
copyright_since = 2025
```

The end year follows the year in which Zola builds the site, and the holder name links to the site root. Set `copyright_since` to `0` or omit it to display only the current year.

## Pinned Posts

Nivis allows you to pin special posts so that they are placed at the frontmost of the post list. To pin posts, add the following to the front matter of your `posts/_index.md`:
```toml
[extra]
pinned_posts = [
    "posts/pinned_post1.md",
    "posts/pinned_post2.md"
]
```

## Math display

Nivis theme supports MathJax for rendering math contents. Add this to your `config.toml` to enable math rendering:
```toml
[extra]
math_display = "mathjax"
```

Zola's Markdown parser can consume punctuation inside TeX before MathJax sees it. This affects characters such as backslashes, underscores, braces, `<`, `>`, and `*`. Run the provided script after adding or editing posts so that MathJax receives the original formula:

```bash
python themes/nivis/scripts/process_math.py
```

The script processes all markdown files in `content/` and:
- Keeps inline math as `$...$` and display math as `$$...$$`
- Encodes ASCII punctuation inside formulas as numeric HTML entities, which Zola decodes without interpreting as Markdown
- Preserves every space and blank line outside formulas
- Skips fenced code blocks and ordinary inline code
- Migrates math previously wrapped in inline backticks or `<div class="math-display">`
- Can be safely re-run (idempotent)

Write formulas with ordinary dollar delimiters:
`````markdown
This is an inline math example: $e^{\pi i}=-1$.

And this is a display math example:

$$
\sum_{i=1}^n i^3=\frac{n^2(n+1)^2}{4}
$$
`````

Blank lines around display math retain their normal Markdown meaning. A blank line starts a new paragraph; omitting it keeps the formula and adjacent text in the same paragraph. `process_math.py` does not add or remove those blank lines.

Use `python themes/nivis/scripts/process_math.py --check` in CI or before publishing to verify that all posts have been processed without rewriting files. `--restore-only` removes legacy wrappers and decodes formula bodies without applying entity encoding; it is intended for migration or recovery, not the normal publishing workflow.

## Special Pages

Nivis theme provides About page, Archives page, Categories page and Links page to help you fully customize your site. Move on to [Special Pages](@/posts/sp-pages.md) for more information.
