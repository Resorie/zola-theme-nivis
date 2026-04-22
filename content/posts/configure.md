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

Nivis theme supports Mathjax for rendering math contents. Add these contents to your `config.toml` to enable math rendering:
```toml
[extra]
math_display = "mathjax"
```

Due to the weirdsome escape rules of zola, some of your math content might not display correctly. I referred to [this post](https://zola.discourse.group/t/maths-support-via-mathjax/1000) for a solution. If your math content fails to display, follow the steps below:

After adding or changing your post, run `themes/nivis/scripts/wrap_math.py` to process the markdown files. After running the script, (or of course you can change them manually), your math contents should be wrapped in code blocks, e.g.:
`````markdown
This is an inline math example: `$e^{\pi i}=-1$`.

And this is a display math example:
```math-display
$$
\sum_{i=1}^n i^3=\frac{n^2(n+1)^2}{4}
$$
```
`````

To ensure the code block is rendered correctly, we need to tell zola to treat `math-display` as a language. Add the following to your `config.toml`:
```toml
[markdown.highlighting]
extra_grammars = [ "themes/nivis/syntaxes/math-display.json" ]
```

## Special Pages

Nivis theme provides About page, Archives page, Categories page and Links page to help you fully customize your site. Move on to [Special Pages](@/posts/sp-pages.md) for more information.
