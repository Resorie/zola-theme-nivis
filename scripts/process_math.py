#!/usr/bin/env python3

"""Protect TeX from Markdown without changing paragraph boundaries."""

from __future__ import annotations

import argparse
import html
import re
import string
from pathlib import Path


CONTENT_DIR = Path(__file__).resolve().parents[3] / "content"

LEGACY_DISPLAY_RE = re.compile(
    r'<div[ \t]+class=(?P<quote>["\'])math-display(?P=quote)[ \t]*>'
    r'\s*(?P<math>\$\$[\s\S]*?\$\$)\s*</div>'
)
FENCE_OPEN_RE = re.compile(r"^(?P<indent> {0,3})(?P<fence>`{3,}|~{3,})(?P<info>[^\r\n]*)")


def _is_escaped(text: str, index: int) -> bool:
    backslashes = 0
    index -= 1
    while index >= 0 and text[index] == "\\":
        backslashes += 1
        index -= 1
    return backslashes % 2 == 1


def _find_display_end(text: str, start: int) -> int:
    index = start
    while True:
        index = text.find("$$", index)
        if index < 0 or not _is_escaped(text, index):
            return index
        index += 2


def _find_inline_end(text: str, start: int) -> int:
    index = start
    while index < len(text) and text[index] not in "\r\n":
        if (
            text[index] == "$"
            and not _is_escaped(text, index)
            and index > start
            and not text[index - 1].isspace()
        ):
            return index
        index += 1
    return -1


def _encode_math_body(body: str) -> str:
    """Encode Markdown-significant ASCII while preserving whitespace."""

    body = html.unescape(body)
    return "".join(
        f"&#{ord(char)};" if char in string.punctuation else char
        for char in body
    )


def _transform_math_token(token: str, restore_only: bool) -> str:
    delimiter_length = 2 if token.startswith("$$") else 1
    delimiter = "$" * delimiter_length
    body = token[delimiter_length:-delimiter_length]
    body = html.unescape(body) if restore_only else _encode_math_body(body)
    return f"{delimiter}{body}{delimiter}"


def _find_code_span_end(text: str, start: int, run_length: int) -> int:
    marker = "`" * run_length
    index = start
    while True:
        index = text.find(marker, index)
        if index < 0:
            return -1
        before_is_tick = index > 0 and text[index - 1] == "`"
        after = index + run_length
        after_is_tick = after < len(text) and text[after] == "`"
        if not before_is_tick and not after_is_tick:
            return index
        index = after


def _scan_plain_text(text: str, restore_only: bool) -> str:
    text = LEGACY_DISPLAY_RE.sub(lambda match: match.group("math"), text)

    output: list[str] = []
    index = 0
    while index < len(text):
        if text[index] == "`":
            run_end = index + 1
            while run_end < len(text) and text[run_end] == "`":
                run_end += 1
            run_length = run_end - index
            close = _find_code_span_end(text, run_end, run_length)
            if close < 0:
                output.append(text[index:run_end])
                index = run_end
                continue

            marker = "`" * run_length
            code = text[run_end:close]
            if (
                run_length == 1
                and "\n" not in code
                and code.startswith("$")
                and not code.startswith("$$")
                and code.endswith("$")
                and len(code) > 2
            ):
                output.append(_transform_math_token(code, restore_only))
            else:
                output.append(f"{marker}{code}{marker}")
            index = close + run_length
            continue

        if text.startswith("$$", index) and not _is_escaped(text, index):
            close = _find_display_end(text, index + 2)
            if close >= 0:
                token = text[index:close + 2]
                output.append(_transform_math_token(token, restore_only))
                index = close + 2
                continue

        if (
            text[index] == "$"
            and not _is_escaped(text, index)
            and index + 1 < len(text)
            and text[index + 1] not in "$\r\n\t "
        ):
            close = _find_inline_end(text, index + 1)
            if close >= 0:
                token = text[index:close + 1]
                output.append(_transform_math_token(token, restore_only))
                index = close + 1
                continue

        output.append(text[index])
        index += 1

    return "".join(output)


def _closing_fence_pattern(fence: str) -> re.Pattern[str]:
    char = re.escape(fence[0])
    return re.compile(rf"^ {{0,3}}{char}{{{len(fence)},}}[ \t]*(?:\r?\n)?$")


def process_body(body: str, restore_only: bool = False) -> str:
    """Process prose segments while leaving fenced code blocks untouched."""

    lines = body.splitlines(keepends=True)
    output: list[str] = []
    prose: list[str] = []
    index = 0

    def flush_prose() -> None:
        if prose:
            output.append(_scan_plain_text("".join(prose), restore_only))
            prose.clear()

    while index < len(lines):
        opening = FENCE_OPEN_RE.match(lines[index])
        if not opening:
            prose.append(lines[index])
            index += 1
            continue

        flush_prose()
        fence = opening.group("fence")
        closing_pattern = _closing_fence_pattern(fence)
        block = [lines[index]]
        index += 1
        while index < len(lines):
            block.append(lines[index])
            is_closing = closing_pattern.match(lines[index]) is not None
            index += 1
            if is_closing:
                break
        output.append("".join(block))

    flush_prose()
    return "".join(output)


def process_content(content: str, restore_only: bool = False) -> str:
    if not content.startswith("+++"):
        return content

    parts = content.split("+++", 2)
    if len(parts) < 3:
        return content

    return f"+++{parts[1]}+++{process_body(parts[2], restore_only)}"


def iter_markdown_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.rglob("*.md")))
        elif path.suffix == ".md":
            files.append(path)
    return files


def process_file(path: Path, restore_only: bool = False, check: bool = False) -> bool:
    content = path.read_text(encoding="utf-8")
    processed = process_content(content, restore_only=restore_only)
    changed = processed != content

    if changed and not check:
        path.write_text(processed, encoding="utf-8")

    state = "Needs processing" if changed and check else "Processed" if changed else "No changes"
    print(f"{path}: {state}")
    return changed


def process_paths(paths: list[Path], restore_only: bool = False, check: bool = False) -> bool:
    changed = False
    for path in iter_markdown_files(paths):
        if process_file(path, restore_only=restore_only, check=check):
            changed = True
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Encode TeX punctuation without changing Markdown paragraph boundaries."
    )
    parser.add_argument("paths", nargs="*", type=Path, help="Markdown files or directories")
    parser.add_argument("--check", action="store_true", help="Check without writing files")
    parser.add_argument(
        "--restore-only",
        action="store_true",
        help="Remove legacy wrappers and decode formula bodies without encoding them",
    )
    args = parser.parse_args()

    paths = args.paths or [CONTENT_DIR]
    changed = process_paths(paths, restore_only=args.restore_only, check=args.check)
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
