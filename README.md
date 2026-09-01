Nivis: A clean zola theme for bloggers.

![screenshot](screenshot.png)

Live demo: [Example Site](https://resorie.xyz/zola-theme-nivis/) | [My Blog](https://resorie.xyz/blog/).

This theme is inspired by (and derived from) themes [Float](https://float-theme.netlify.app/) and [anatole](https://longfangsong.github.io/). Check out these two wonderful themes as well! :smile:

## Features :star:

- Clean & Minimalist Design
- Elegant Typography
- Responsive Layout
- Dark/Light Mode Support

## Getting Started :rocket:

Nivis requires Zola 0.23.4 or later.

Use `git submodule` to add the theme to your site:
```bash
git submodule add -b master --depth=1 https://github.com/Resorie/zola-theme-nivis.git themes/nivis/
git submodule update --init --recursive
```

Then, change your theme config in `config.toml`:
```toml
theme = "nivis"

[extra]
# "focus" is the default; use "horizontal" for the left-aligned layout.
home_layout = "focus"
# "tags" is the default; use "category" or "none" for the other modes.
taxonomy_mode = "tags"
```

## Taxonomy Modes

Nivis provides three display modes while continuing to use Zola's `tags`
taxonomy internally. This keeps `/tags/` and existing post front matter stable
when switching between multiple tags and a single category.

| Mode | Values per post | Theme output |
| --- | --- | --- |
| `tags` | Any number | Tag cloud, `#` prefixes, navigation, and post metadata |
| `category` | Zero or one | The same index layout and count, without `#` prefixes |
| `none` | Ignored by the theme | No taxonomy navigation or post metadata |

The default `tags` mode and the `category` mode use the same top-level Zola
configuration:

```toml
taxonomies = [{ name = "tags", paginate_by = 5 }]

[extra]
taxonomy_mode = "category" # or "tags"
```

Post front matter also keeps the `tags` key. Assign several values in `tags`
mode, or one value in `category` mode:

```toml
[taxonomies]
tags = ["Research"]
```

Category mode rejects a page with more than one value instead of silently
choosing one. Pages without a category remain valid.

For `none`, disable rendering in Zola as well as hiding taxonomy UI in Nivis:

```toml
taxonomies = [{ name = "tags", render = false }]

[extra]
taxonomy_mode = "none"
```

Setting `render = false` lets existing taxonomy front matter remain valid while
preventing Zola from generating `/tags/` and term pages. See the
[Zola taxonomy documentation](https://www.getzola.org/documentation/content/taxonomies/)
for the top-level option.

The older `extra.sections.tags = false` option remains supported. It overrides
`taxonomy_mode` and hides all taxonomy UI, but it cannot stop Zola from
generating taxonomy pages. New configurations should normally use
`taxonomy_mode` and reserve the section switch for compatibility.

The optional copyright line is hidden by default. To show it as the second
line of the site footer, provide the holder and an optional start year:

```toml
[extra.footer]
copyright_holder = "Your name"
copyright_since = 2025
```

The end year follows the year in which Zola builds the site. The holder name
links to the site root. Leaving `copyright_holder` empty keeps the line hidden.

Start your site by copying the example content into your site folder:
```bash
cp -r themes/nivis/content content
cp -r themes/nivis/data data
```

Move on to the [example site](https://resorie.xyz/zola-theme-nivis/) for more info. Enjoy it! :kissing_heart:

## Todo :clipboard:

- [ ] Add transition when switching light/dark mode
- [ ] Better special page customization
- [ ] Minimize web resources
