import os
import re
import glob

CONTENT_DIR = "../../../content"

def process_content(content):
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
            return f"\n```math-display\n{display_math}\n```\n"
        if inline_math:
            return f"`{inline_math}`"
            
        return match.group(0)

    return token_pattern.sub(replace_func, content)

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
