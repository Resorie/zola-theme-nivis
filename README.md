Nivis: A clean zola theme for bloggers.

> [!WARNING]
> This project is still a work-in-progress. I'm making major changes to it any time.

Live demo: [my blog](https://resorie.github.io/blog/).

## Installation

Simply clone the repo into your `themes/` directory, or use `git submodule`.
```bash
git clone https://github.com/Resorie/zola-theme-nivis.git themes/nivis/
```

Then, change your theme in `config.toml`:
```toml
theme = "nivis"
```

## Configurations

### Math display

Nivis theme supports both Mathjax and Katex for rendering math contents. Follow the steps below to enable math rendering:

First, add these contents to your `config.toml`:
```toml
[extra]
math = "mathjax" # or "katex"
```

Due to the weirdsome escape rules of zola, your math contents might not display correctly. I referred to [this post](https://zola.discourse.group/t/maths-support-via-mathjax/1000) for a solution. After adding or changing your post, run `themes/nivis/scripts/wrap_math.py` to process the markdown files. 

After running the script, your math contents should be wrapped in code blocks. e.g.:
`````markdown
This is a inline math example: `$e^{\pi i}=-1$`.

And this is a display math example:
```math-display
$$
\sum_{i=1}^n i^3=\frac{n^2(n+1)^2}{4}
$$
```
`````

Finally, zola would warn that it fails to find a render rule for language `math-display`. Of course, we don't need these warnings. Add the following lines to your `config.toml` to get rid of these warnings:
```toml
[markdown]
extra_syntaxes_and_themes = ["themes/nivis/syntaxes/"]
```

### Friend Links

Nivis suppors a page to display links to your friends' site. First, create `content/links/index.md`:
```markdown
+++
title = "Links"
template = "links.html"
+++

Friend Links.
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