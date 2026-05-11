import os
import re
import glob
import html

CONTENT_DIR = "../../../content"


def escape_html(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def process_content(content):
    # Step 1: Unwrap ALL existing math-display divs (decode HTML entities)
    def unwrap_div(match):
        math_content = match.group(1)
        return html.unescape(math_content)

    content = re.sub(
        r'<div class="math-display">\s*(\$\$[\s\S]*?\$\$)\s*</div>',
        unwrap_div,
        content, flags=re.DOTALL
    )

    # Step 2: Unwrap old ```math-display\n$$...$$\n``` blocks back to raw $$...$$
    old_math_block = re.compile(r"```math-display\s*\n\s*(\$\$[\s\S]*?\$\$)\s*\n```")
    content = old_math_block.sub(r"\1", content)

    # Step 3: Wrap raw math into HTML tags / backticks
    token_pattern = re.compile(r"""
        (```[\s\S]*?```) |
        (`[^`\n]+`) |
        (\$\$[\s\S]*?\$\$) |
        ((?<!\\)\$(?![\s$])[^\$\n]+(?<![\s\\])\$)
    """, re.VERBOSE)

    def replace_func(match):
        code_block, inline_code, display_math, inline_math = match.groups()

        if code_block:
            return code_block
        if inline_code:
            return inline_code
        if display_math:
            escaped = escape_html(display_math)
            return f'<div class="math-display">{escaped}</div>'
        if inline_math:
            return f"`{inline_math}`"

        return match.group(0)

    content = token_pattern.sub(replace_func, content)

    # Step 4: Normalize excessive blank lines around math-display divs
    content = re.sub(r'\n{3,}(<div class="math-display">)', r'\n\n\1', content)
    content = re.sub(r'(</div>)\n{3,}', r'\1\n\n', content)

    return content


def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.startswith("+++"):
        return

    parts = content.split("+++", 2)
    if len(parts) < 3:
        return

    rel_path = filepath.split("../")[-1]
    print(f"Detected file: {rel_path}; ", end="")

    front_matter = parts[1]
    body = parts[2]

    new_body = process_content(body)

    if new_body != body:
        new_content = f"+++{front_matter}+++{new_body}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Processed Successfully")
    else:
        print(f"No changes")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    content_path = os.path.join(base_dir, CONTENT_DIR)

    for root, dirs, files in os.walk(content_path):
        for file in files:
            if file.endswith(".md"):
                filepath = os.path.join(root, file)
                process_file(filepath)


if __name__ == "__main__":
    main()
