+++
title = "Components"
description = "Use Nivis image and collapsible-content components in Markdown posts."
date = 1980-01-01

[taxonomies]
tags = ["guide"]

[extra]
toc = true
+++

Nivis includes two Tera components: `image` for responsive images and captions, and `collapse` for Markdown content that can be opened and closed.

## Image

The image component resolves `src` through Zola's `get_url`, so paths normally refer to files below the site's `static/` directory.

| Parameter | Required | Default | Purpose |
| --- | --- | --- | --- |
| `src` | Yes | - | Static asset path passed to `get_url`. |
| `alt` | No | Empty | Alternative text for the image. |
| `caption` | No | Empty | Adds a `figure` and visible caption when non-empty. |
| `class` | No | Empty | Class applied to the `figure`, or to the image when there is no caption. |

Template:

{% raw %}
```markdown
{{<image src="images/example.jpg" alt="A precise description" caption="Optional caption" class="wide-image"/>}}
```
{% endraw %}

For example, the following source loads `static/images/screenshot.png`:

{% raw %}
```markdown
{{<image src="images/screenshot.png" alt="Nivis example site" caption="Nivis example site"/>}}
```
{% endraw %}

Rendered result:

{{<image src="images/screenshot.png" alt="Nivis example site" caption="Nivis example site"/>}}

Always provide useful alternative text for informative images. Leave `alt` empty only when an image is purely decorative.

## Collapse

The collapse component renders a native `details` element and parses its body as Markdown.

| Parameter | Required | Default | Purpose |
| --- | --- | --- | --- |
| `summary` | No | `Details` | Visible label for the disclosure control. |
| `unfold` | No | `false` | Starts the block open when set to `true`. |

Closed by default:

{% raw %}
```markdown
{% <collapse summary="Derivation"> %}
This paragraph is hidden initially.

- Markdown lists work here.
- So do **emphasis**, links, and code blocks.
{% </collapse> %}
```
{% endraw %}

Rendered result:

{% <collapse summary="Derivation"> %}
This paragraph is hidden initially.

- Markdown lists work here.
- So do **emphasis**, links, and code blocks.
{% </collapse> %}

Open by default:

{% raw %}
```markdown
{% <collapse summary="Shown initially" unfold={true}> %}
This content starts open but remains collapsible.
{% </collapse> %}
```
{% endraw %}

Rendered result:

{% <collapse summary="Shown initially" unfold={true}> %}
This content starts open but remains collapsible.
{% </collapse> %}

Keep summaries short and descriptive. A collapse block should not hide content that every reader must see to understand the article.
