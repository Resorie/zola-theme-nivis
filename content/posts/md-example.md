+++
title = "Markdown Example"
description = "markdown examples"
date = 1980-01-01

[taxonomies]
tags = ["example"]

[extra]
toc = true
+++

> **AIGC disclosure:** This Markdown example was generated with Gemini 3 and reviewed as part of the Nivis documentation.

## Text Basics
You can make text **bold** or *italic*. You can also use ~~strikethrough~~ or highlight `inline code` variables.

## Headings

Acknowledge that we recommend using `h1` (in markdown, single `#`) only for the title (that is, the `title` attribute in front matter). The titles in post content should start with `h2`.

### h3
#### h4

`h5` and `h6` are not recommended to use. (Actually I didn't implement a style for them lol) Try use lists to replace them.


## Lists & Checkboxes
**Unordered List:**
* Apple
* Banana
    * Cavendish
    * Plantain
* Cherry

**Ordered List:**
1.  Initialize repo
2.  Stage files
3.  Commit

**Task List:**
- [x] Draft content
- [ ] Review for typos
- [ ] Publish

## Links & Images
[Click here for Google](https://www.google.com)

![Placeholder Image](https://via.placeholder.com/150 "Tooltip Text")

## Code Blocks
**Python:**
```python
def greet(name):
    return f"Hello, {name}!"
```

**JavaScript:**

```javascript
const numbers = [1, 2, 3];
numbers.forEach(num => console.log(num));
```

## Tables

| Feature | Supported | Notes |
| --- | --- | --- |
| Tables | Yes | Pipes and dashes |
| Alignment | Yes | Colons define it |
| Complexity | Low | Keep it simple |

## Math Formulas (LaTeX)

Markdown renders math using LaTeX syntax. Refer to the [configuration post](@/posts/configure.md) for how to use it.

**Inline:** The mass-energy equivalence is $e&#61;mc&#94;2$.

**Block (Display):**

$$
f&#40;x&#41;&#61;&#92;int&#95;&#123;&#45;&#92;infty&#125;&#94;&#92;infty &#92;hat f&#40;&#92;xi&#41;e&#94;&#123;2&#92;pi i&#92;xi x&#125;d&#92;xi
$$

## Blockquotes

> "Code is like humor. When you have to explain it, it’s bad."
> — *Cory House*

## GitHub-Style Alerts

> [!NOTE]
> This is a note useful for the reader.

> [!TIP]
> Here is a helpful tip to improve your workflow.

> [!IMPORTANT]
> This information is crucial for correct functionality.

> [!WARNING]
> Be careful! This action might have side effects.

> [!CAUTION]
> This action causes data loss. Proceed with extreme care.

## Footnotes

Here is a sentence with a footnote reference[^1].

## Horizontal Rules

---

(The line above is a horizontal rule)

[^1]: This is the actual footnote content at the bottom of the page.
