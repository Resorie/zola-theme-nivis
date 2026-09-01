+++
title = "Getting Started"
description = "Install Nivis and start a Zola site with a verified baseline configuration."
date = 1980-01-01

[taxonomies]
tags = ["start"]

[extra]
toc = true
+++

> **AIGC disclosure:** The Nivis guides in this example site were drafted in part with AIGC assistance and checked against the theme source and a local Zola build.

## Requirements

Nivis requires Zola 0.23.4 or later. Check the installed version before starting:

```bash
zola --version
```

Git is needed for the recommended submodule installation. Python 3 is only needed for the optional math-processing tools.

## Installation

From the root of an existing Zola site, add Nivis below `themes/`:

```bash
git submodule add -b master --depth=1 https://github.com/Resorie/zola-theme-nivis.git themes/nivis
git submodule update --init --recursive
```

Enable the theme in `config.toml`:

```toml
theme = "nivis"
```

For a new, otherwise empty site, copy the example content and link data:

```bash
cp -R themes/nivis/content/. content/
cp -R themes/nivis/data/. data/
```

These commands merge files into the destination directories. If the site already has content, copy only the example files you need so existing files are not replaced.

## Baseline Configuration

The following `config.toml` includes the Zola options expected by the default navigation and feed menu:

```toml
base_url = "https://example.com"
title = "Your Site"
description = "Your site description"
theme = "nivis"

compile_sass = true
generate_feeds = true
feed_filenames = ["rss.xml", "atom.xml"]
taxonomies = [{ name = "tags", paginate_by = 5 }]

[markdown]
render_emoji = true
github_alerts = true
bottom_footnotes = true

[markdown.highlighting]
style = "class"
light_theme = "one-light"
dark_theme = "one-dark-pro"
# Keep this only if fenced math-display blocks are used.
extra_grammars = ["themes/nivis/syntaxes/math-display.json"]

[extra]
avatar = ""
home_layout = "focus"
taxonomy_mode = "tags"
motto_mode = "hide"
social_links = []

[extra.footer]
copyright_holder = ""
copyright_since = 0

[extra.sections]
posts = true
about = true
archive = true
tags = true
links = true
```

An avatar path is resolved from the site's `static/` directory. For example, `avatar = "images/avatar.jpg"` expects `static/images/avatar.jpg`.

When Nivis itself is the Zola site root, as in this example repository, the grammar path is `syntaxes/math-display.json` instead of the submodule path shown above.

## Expected Content

Enabled navigation sections expect these files:

```text
content/
  _index.md
  about/index.md
  archive/index.md
  links/index.md
  posts/_index.md
data/
  links.toml
```

The templates and front matter for each route are covered in [Special Pages](@/posts/sp-pages.md). If a page is intentionally omitted, disable its navigation entry under `[extra.sections]`.

## Local Preview

Start Zola's development server from the site root:

```bash
zola serve
```

For a production-style check, build into `public/`:

```bash
zola build --force
```

Continue with [Configuration](@/posts/configure.md) for homepage, taxonomy, profile, article, and math options.

## Updating the Theme

Update only the Nivis submodule from the site root:

```bash
git submodule update --remote --merge themes/nivis
git add themes/nivis
```

Run a local build before committing the updated submodule pointer.
