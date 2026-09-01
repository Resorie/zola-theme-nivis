#!/usr/bin/env python3

"""Restore processed TeX to readable dollar-delimited source."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from .process_math import CONTENT_DIR, process_paths
except ImportError:
    from process_math import CONTENT_DIR, process_paths


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Decode processed TeX punctuation and remove legacy math wrappers "
            "without changing whitespace or paragraph boundaries."
        )
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Markdown files or directories; defaults to the site's content directory",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check whether restoration is needed without writing files",
    )
    args = parser.parse_args()

    paths = args.paths or [CONTENT_DIR]
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        parser.error(f"path does not exist: {', '.join(missing)}")

    changed = process_paths(paths, restore_only=True, check=args.check)
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
