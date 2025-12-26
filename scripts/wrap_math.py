import os
import re
import glob

# Configuration
CONTENT_DIR = "../../../content"

def process_content(content):
    # Regex patterns
    # 1. Code blocks: ``` ... ``` (greedy matching for content, but non-greedy for the block?)
    #    Actually, ``` followed by anything until ```.
    #    We use [\s\S]*? to match across lines non-greedily.
    # 2. Inline code: ` ... ` (no backticks inside)
    # 3. Display math: $$ ... $$
    # 4. Inline math: $ ... $ (no newlines usually, but let's allow it if standard markdown allows? 
    #    Usually inline math is on one line. Let's stick to one line for safety).
    
    # We use a tokenizer approach: match the earliest occurring pattern.
    # The order in the regex OR matters.
    
    token_pattern = re.compile(r"""
        (```[\s\S]*?```) |                # Group 1: Code block
        (`[^`\n]+`) |                     # Group 2: Inline code
        (\$\$[\s\S]*?\$\$) |              # Group 3: Display math
        ((?<!\\)\$(?![\s$])[^\$\n]+(?<![\s\\])\$)  # Group 4: Inline math
        # Inline math regex explanation:
        # (?<!\\)\$      : Starts with $, not preceded by \
        # (?![\s$])      : Next char is not whitespace or $ (avoids matching $$ or $ space)
        # [^\$\n]+       : Content (no $ or newline)
        # (?<![\s\\])\$  : Ends with $, previous char not whitespace or \
    """, re.VERBOSE)

    def replace_func(match):
        code_block, inline_code, display_math, inline_math = match.groups()
        
        if code_block:
            return code_block
        if inline_code:
            return inline_code
        if display_math:
            # Wrap display math in a specific code block
            return f"\n```math-display\n{display_math}\n```\n"
        if inline_math:
            # Wrap inline math in inline code
            return f"`{inline_math}`"
            
        return match.group(0)

    return token_pattern.sub(replace_func, content)

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if front matter exists
    if not content.startswith("+++"):
        return

    parts = content.split("+++", 2)
    if len(parts) < 3:
        return
    
    front_matter = parts[1]
    body = parts[2]
    
    new_body = process_content(body)
    
    if new_body != body:
        new_content = f"+++{front_matter}+++{new_body}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Processed {filepath}")
    else:
        print(f"No changes in {filepath}")

def main():
    # Walk through all markdown files in content directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    content_path = os.path.join(base_dir, CONTENT_DIR)
    
    for root, dirs, files in os.walk(content_path):
        for file in files:
            if file.endswith(".md"):
                filepath = os.path.join(root, file)
                process_file(filepath)

if __name__ == "__main__":
    main()
