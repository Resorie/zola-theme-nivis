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

Due to Zola's markdown escaping, some math content (especially `<`, `>`, `*` in LaTeX) may not render correctly. To handle this, run the provided script after adding or editing posts:

```bash
python themes/nivis/scripts/wrap_math.py
```

The script processes all markdown files in `content/` and:
- Wraps inline math `$...$` in backticks (`` ``$...$`` ``)
- Wraps display math `$$...$$` in HTML `<div class="math-display">` tags
- HTML-escapes special characters (`<`, `>`, `&`) inside display math
- Can be safely re-run (idempotent)

After processing, your math content will look like:
`````markdown
This is an inline math example: `$e^{\pi i}=-1$`.

And this is a display math example:

$$
\sum_{i=1}^n i^3=\frac{n^2(n+1)^2}{4}
$$
`````

If you prefer to process math manually, ensure that `<`, `>`, and `&` in LaTeX are HTML-escaped (`&lt;`, `&gt;`, `&amp;`) when using HTML wrappers.

## Special Pages

Nivis theme provides About page, Archives page, Categories page and Links page to help you fully customize your site. Move on to [Special Pages](@/posts/sp-pages.md) for more information.
