+++
title = "Configuration"
description = "Configure Nivis layouts, profile details, taxonomies, article metadata, and math rendering."
date = 1980-01-01

[taxonomies]
tags = ["guide"]

[extra]
toc = true
+++

Nivis-specific options are placed below `[extra]` in the site's `config.toml`. Zola's own settings, including feeds, taxonomies, and Markdown highlighting, stay at the top level.

## Homepage Layout

Nivis provides two homepage layouts:

```toml
[extra]
home_layout = "focus"
```

- `focus` centers the profile and navigation in a compact first screen.
- `horizontal` uses a wider, left-aligned presentation.

`focus` is the default. Unknown values also fall back to it.

## Profile and Avatar

The site `title` and `description` are shown with the optional avatar on the homepage and in the sidebar:

```toml
title = "Your Site"
description = "A short site description"

[extra]
avatar = "images/avatar.jpg"
```

The avatar path is resolved from `static/`, so this example expects `static/images/avatar.jpg`. Leave `avatar` empty to hide it.

## Motto

Mottos appear between the site description and social links. Hide them by default:

```toml
[extra]
motto_mode = "hide"
```

Show one static motto:

```toml
[extra]
motto_mode = "single"
motto = "Simplicity is the ultimate sophistication."
```

Rotate through multiple mottos with the built-in typewriter effect:

```toml
[extra]
motto_mode = "multi"
mottos = [
    "Code is poetry.",
    "Make the important things clear.",
]
```

When the browser requests reduced motion, the main template displays the first motto without the animation.

## Social Links

Each social link needs an icon name and URL:

```toml
[extra]
social_links = [
    { name = "github", url = "https://github.com/username" },
    { name = "email", url = "mailto:hello@example.com" },
    { name = "globe", url = "https://example.com" },
]
```

The generic names `email`, `rss`, `link`, and `globe` have dedicated icons. Other names are treated as Font Awesome brand names, including `github`, `mastodon`, and `bilibili`.

URLs are rendered exactly as provided. Use complete URLs when the site is deployed below a path prefix. Set `social_links = []` to show no icons.

## Navigation Sections

All five sections are enabled by default. Set individual entries to `false` to remove their links from the homepage, desktop navigation, mobile navigation, sidebar, and 404 page:

```toml
[extra.sections]
posts = true
about = true
archive = true
tags = true
links = false
```

This only controls theme navigation. It does not remove content or stop Zola from generating taxonomy pages.

## Taxonomy Modes

Nivis uses Zola's `tags` taxonomy internally and supports three presentation modes. Keeping one taxonomy name preserves existing front matter and `/tags/` URLs while the visible semantics change.

### Multiple Tags

This is the default mode:

```toml
taxonomies = [{ name = "tags", paginate_by = 5 }]

[extra]
taxonomy_mode = "tags"
```

Posts may contain any number of values:

```toml
[taxonomies]
tags = ["Zola", "Design"]
```

The taxonomy index is displayed as a tag cloud, and each value receives a `#` prefix in taxonomy and post metadata.

### One Category

Category mode keeps the same Zola taxonomy declaration:

```toml
taxonomies = [{ name = "tags", paginate_by = 5 }]

[extra]
taxonomy_mode = "category"
```

Each post may contain zero or one value:

```toml
[taxonomies]
tags = ["Research"]
```

The taxonomy index retains the same URLs and counts but removes `#` prefixes. A post with more than one value stops the build instead of silently choosing a category. An uncategorized post remains valid.

### No Taxonomy UI

Disable taxonomy rendering in Zola as well as the Nivis UI:

```toml
taxonomies = [{ name = "tags", render = false }]

[extra]
taxonomy_mode = "none"
```

`render = false` prevents Zola from generating `/tags/` and term pages while allowing existing `[taxonomies]` front matter to remain valid.

The older `[extra.sections] tags = false` switch remains supported and takes precedence over `taxonomy_mode`. It hides taxonomy navigation and post metadata but does not control Zola's generated pages.

## Post Metadata

Use `description` for the short summary shown in post lists and HTML metadata. An article may also define a subtitle and a longer article-page abstract:

```toml
+++
title = "Post title"
description = "A short summary for post lists."
date = 2026-01-01

[taxonomies]
tags = ["Notes"]

[extra]
subtitle = "An optional subtitle"
abstract = "A longer abstract shown only on the article page."
toc = true
+++
```

If `extra.abstract` is omitted, the article header uses `description`. Set `extra.toc = false` to suppress the table of contents even when the page has headings.

Set `extra.link` to change only the destination of the title in the post list:

```toml
[extra]
link = "https://example.com/external-article"
```

The local page is still generated and keeps its own permalink.

### Content Language And Sharing

> **AIGC disclosure:** This subsection was written with AI assistance and checked against the theme templates and local builds.

Set `[extra] content_lang = "zh-CN"` in the site's configuration to mark article pages and post-list entries as Chinese. A post can override this with its own `[extra] content_lang = "en"`. Empty or omitted values fall back to the site-level setting, then Zola's page language. This only changes the article container's HTML `lang` attribute; it does not change the surrounding navigation, `default_language`, URLs, feed languages or search configuration.

Article pages share the same plain-text description through `meta[name="description"]` and `og:description`, with the site title in `og:site_name`. The description uses `description`, then `summary`, then the article body, strips HTML, trims surrounding whitespace and truncates to 100 characters before HTML escaping. These metadata tags do not add a share button or preview image, and the receiving platform decides how to display a link preview.

## Pinned Posts

Pinned posts appear before the ordinary post list on its first page. Add paths relative to `content/` in `content/posts/_index.md`:

```toml
[extra]
pinned_posts = [
    "posts/first-post.md",
    "posts/second-post.md",
]
```

Each path must identify an existing page. Pinned pages are omitted from their normal positions so they do not appear twice.

## Site Footer

The copyright line appears below the Nivis and Zola credits only when a holder is provided:

```toml
[extra.footer]
copyright_holder = "Your Name"
copyright_since = 2025
```

The end year follows the year in which Zola builds the site. Set `copyright_since` to `0`, or omit it, to display only the current year.

## Math Display

Enable MathJax 4 in `config.toml`:

```toml
[extra]
math_display = "mathjax"
```

Write formulas with ordinary dollar delimiters:

`````markdown
Inline math: $e^{\pi i}=-1$.

Display math:

$$
\sum_{i=1}^n i^3=\frac{n^2(n+1)^2}{4}
$$
`````

Zola's Markdown parser can consume punctuation inside TeX before MathJax sees it. After adding or editing formulas, run the bundled processor from the site root:

```bash
python3 themes/nivis/scripts/process_math.py content
```

The processor:

- preserves dollar-delimited inline and display formulas;
- encodes Markdown-significant ASCII punctuation inside formulas;
- preserves spaces and blank lines outside formulas;
- skips fenced code blocks and ordinary inline code;
- migrates legacy backtick and `math-display` wrappers; and
- is idempotent, so it can be run repeatedly.

Blank lines around display math keep their normal Markdown meaning. A blank line starts a new paragraph; omitting it keeps the formula and adjacent text in the same paragraph.

Check without rewriting files:

```bash
python3 themes/nivis/scripts/process_math.py --check content
```

Restore readable TeX before editing or reviewing processed source:

```bash
python3 themes/nivis/scripts/restore_math.py content
```

The restoration command removes legacy wrappers and decodes formula bodies without changing paragraph boundaries. It also supports `--check`.

## Code Highlighting

Nivis ships light and dark class-based highlighting styles. Configure Zola to emit classes instead of inline colors:

```toml
[markdown.highlighting]
style = "class"
light_theme = "one-light"
dark_theme = "one-dark-pro"
```

If fenced `math-display` blocks are used, add the bundled grammar. A site with Nivis installed as a submodule uses:

```toml
extra_grammars = ["themes/nivis/syntaxes/math-display.json"]
```

The standalone example repository uses `syntaxes/math-display.json` because the theme itself is the site root.

## Legacy Defaults

`extra.main_section`, `extra.home_greeting`, and `extra.home_recent_posts` are still present in `theme.toml` for compatibility. Current templates do not read them, so changing these values has no visible effect.

Continue with [Components](@/posts/components.md) and [Special Pages](@/posts/sp-pages.md) for content-level examples.
