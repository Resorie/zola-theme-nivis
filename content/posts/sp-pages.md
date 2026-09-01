+++
title = "Special Pages"
description = "Create and configure the posts, about, archive, taxonomy, and friend-links pages used by Nivis."
date = 1980-01-01

[taxonomies]
tags = ["guide"]

[extra]
toc = true
+++

Nivis can link to five site sections: posts, about, archives, categories, and friend links. Their navigation switches are independent, but enabled routes must have the content or data expected by their templates.

## Navigation Switches

All sections are enabled by default:

```toml
[extra.sections]
posts = true
about = true
archive = true
tags = true
links = true
```

Set only the entries that need to differ from the defaults. For example:

```toml
[extra.sections]
links = false
```

| Key | Navigation target | Required source when enabled |
| --- | --- | --- |
| `posts` | `/posts/` | `content/posts/_index.md` |
| `about` | `/about/` and the sidebar action | `content/about/index.md` |
| `archive` | `/archive/` | `content/archive/index.md` and the posts section |
| `tags` | `/tags/` | Top-level Zola `tags` taxonomy with rendering enabled |
| `links` | `/links/` | `content/links/index.md` and `data/links.toml` |

Hiding a section removes theme navigation but does not delete its content.

## Posts Page

Create `content/posts/_index.md`:

```toml
+++
title = "Posts"
sort_by = "date"
template = "section.html"
page_template = "page.html"
paginate_by = 5

[extra]
pinned_posts = []
+++
```

Posts are ordinary Markdown pages below `content/posts/`. To pin pages above the first result page, list their paths relative to `content/`:

```toml
[extra]
pinned_posts = [
    "posts/getting-started.md",
    "posts/featured-post.md",
]
```

## About Page

Create `content/about/index.md`:

`````markdown
+++
title = "About Me"
template = "about.html"
+++

Introduce yourself here.
`````

The page body supports ordinary Markdown.

## Archive Page

Create `content/archive/index.md`:

```toml
+++
title = "Archives"
template = "archive.html"
+++
```

The archive template reads `content/posts/_index.md` and groups dated posts by year in reverse chronological order.

## Categories Page

Zola generates the taxonomy index and term pages, so no `content/tags/_index.md` file is required. The default declaration is:

```toml
taxonomies = [{ name = "tags", paginate_by = 5 }]
```

Nivis can show these values as multiple tags or one category per post. To hide taxonomy UI and stop generating taxonomy pages, use:

```toml
taxonomies = [{ name = "tags", render = false }]

[extra]
taxonomy_mode = "none"
```

See [Configuration](@/posts/configure.md) for all three modes and their front matter rules.

## Friend Links Page

Create `content/links/index.md`:

`````markdown
+++
title = "Links"
template = "links.html"

[extra]
show_content = true
+++

Optional introductory text.
`````

Set `show_content = false` or omit it to render only the link groups.

Then create `data/links.toml`:

```toml
[[groups]]
name = "Friends"
desc = "Personal sites I follow."

[[groups.items]]
name = "Someone"
url = "https://example.com/"
description = "A short description."
avatar = "https://example.com/avatar.jpg"

[[groups]]
name = "Projects"
desc = "Projects worth visiting."

[[groups.items]]
name = "Zola"
url = "https://www.getzola.org/"
description = "The static site generator used by Nivis."
avatar = "https://avatars.githubusercontent.com/u/43047029"
```

Each group needs `name`, `desc`, and `items`. Each item needs `name`, `url`, `description`, and `avatar`. Link cards open in a new tab with `rel="noopener noreferrer"`.

After adding or removing a special page, run `zola build --force` so missing routes or data files are caught before deployment.
