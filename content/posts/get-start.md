+++
title = "Getting Started"
description = "getting started with nivis"
date = 1980-01-01

[taxonomies]
tags = ["start"]

[extra]
+++

## Installation

Use `git submodule` to add the theme to your site:
```bash
git submodule add -b master --depth=1 https://github.com/Resorie/zola-theme-nivis.git themes/nivis/
git submodule update --init --recursive
```

Then, change your theme config in `config.toml`:
```toml
theme = "nivis"
```

Start your site by copying the example content and data into your site folder:
```bash
cp -r themes/nivis/content content
cp -r themes/nivis/data data
```

If you want to update the nivis theme, run the following command:
```bash
git submodule update --remote --merge
```

## Basic Configs

The following is a basic template for your `config.toml`:
```toml
base_url = "https://yours.site"

title = "Your Title"
description = "Your blog"

theme = "nivis"

generate_feeds = true
feed_filenames = ["rss.xml", "atom.xml"]

compile_sass = true

taxonomies = [{ name = "tags", paginate_by = 5 }]

[markdown]
render_emoji = true
github_alerts = true
bottom_footnotes = true

[markdown.highlighting]
style = "class"
light_theme = "one-light"
dark_theme = "one-dark-pro"

[extra]
main_section = "posts"
avatar = "images/avatar.jpeg" # In static/ folder

# Social links
social_links = [
    { name = "github", url = "https://github.com/your_username" },
]
```

Move on to [Configuration](@/posts/configure.md) for advanced configurations. 

---

If you like this theme, please give it a star on [github](https://github.com/Resorie/zola-theme-nivis). :kissing_heart:
