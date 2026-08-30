+++
title = "Components"
description = "components in Nivis theme"
date = 1980-01-01

[taxonomies]
tags = ["guide"]

[extra]
+++

Nivis provides various components for you to use in your posts.

## Images

To place an image in your post with alt text and message.

Template:
{% raw %}
```markdown
{{<image src="img src" alt="alt text" caption="caption text"/>}}
```
{% endraw %}

Example:

{{<image src="img src" alt="alt text" caption="caption text"/>}}

## Collapse

To place a collapse box in your post. Folded up by default, set `unfold` to true to unfold it by default.

Template:

{% raw %}
```markdown
{% <collapse summary="Summary"> %}
Content hidden by default.
{% </collapse> %}

{% <collapse summary="Summary" unfold={true}> %}
Content shown by default.
{% </collapse> %}
```
{% endraw %}

Example:

{% <collapse summary="Summary"> %}
Content hidden by default.
{% </collapse> %}

{% <collapse summary="Summary" unfold={true}> %}
Content shown by default.
{% </collapse> %}
