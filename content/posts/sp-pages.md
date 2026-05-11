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

By default, all 5 sections (posts, archives, tags, about, links) are enabled in `theme.toml`. They appear in the navigation bar automatically. If you want to disable a specific section, set it to `false` in your `config.toml`:

```toml
[extra.sections]
links = false
```

You don't need to declare sections you want to keep enabled — only override the ones you want to hide.

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

Nivis lists all your post tags in categories page. Clicking on the tag directs you to the lists of all posts with the tag. Create `content/tags/_index.md`:
```markdown
+++
title = "Categories"
template = "tags/list.html"
+++
```

## Friend Links

Nivis suppors a page to display links to your friends' site. First, create `content/links/index.md`:
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