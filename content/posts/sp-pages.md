+++
title = "Special Pages"
description = "special pages in Nivis theme"
date = 1980-01-01

[taxonomies]
tags = ["guide"]

[extra]
toc = true
+++

Nivis theme provides About page, Archives page, Categories page and Links page to help you fully customize your site.

## Enable/Disable Sections

By default, all five navigation sections (posts, archives, categories, about, and links) are enabled in `theme.toml`. If you want to hide a specific section, set it to `false` in your `config.toml`:

```toml
[extra.sections]
links = false
```

You only need to declare sections that you want to hide.

## About Page

Nivis provides an about page to introduce yourself. Create `content/about/index.md`:
`````markdown
+++
title = "About Me"
template = "about.html"
+++

Show yourself! :smile:
`````

## Archive Page

Nivis shows all your posts sorted by publish time in the archives page. Create `content/archive/index.md`:
```markdown
+++
title = "Archives"
template = "archive.html"
+++
```

## Categories Page

Zola generates the Categories page from the `tags` taxonomy, so no `content/tags/_index.md` file is needed. Nivis can present it as multiple tags, one category per post, or no taxonomy UI. See [Configuration](@/posts/configure.md) for complete examples and the interaction with Zola's `render` option.

## Friend Links

Nivis supports a page for links to other sites. First, create `content/links/index.md`:
```markdown
+++
title = "Links"
template = "links.html"
+++

Friend Links. 

The content here will be shown if `extra.show_content` is set to true in the front matter.
```

Then, create `data/links.toml`. The theme will generate the page from this file. Follow the syntax:
```toml
[[groups]]
name = "Friends"
items = [
    # Add your friends here
    { name = "Someone", url = "https://example.site/", description = "Description", avatar = "Your Friend's Avatar" },
]

[[groups]]
name = "Projects"
items = [
    { name = "Zola", url = "https://www.getzola.org/", description = "The static site generator used for this blog.", avatar = "https://avatars.githubusercontent.com/u/43047029" },
]

```
