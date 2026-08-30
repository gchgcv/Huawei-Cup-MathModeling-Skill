#!/usr/bin/env python3
"""Validate that every file path declared in manifest.yaml exists.

Uses only the Python standard library so it can run in minimal environments.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PATH_RE = re.compile(r"(?:^|:\s+|^-\s+)((?:static|references|templates|scripts)/[^\s#]+\.(?:md|yaml|json|py|tex|cls|sty|bib))\s*$")


def extract_paths(text: str) -> set[str]:
    paths: set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        match = PATH_RE.search(line)
        if match:
            paths.add(match.group(1).strip('"\''))
    return paths


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = Path(args.root).resolve()
    manifest = root / "manifest.yaml"
    if not manifest.is_file():
        print("ERROR: manifest.yaml missing", file=sys.stderr)
        return 2
    paths = extract_paths(manifest.read_text(encoding="utf-8"))
    if not paths:
        print("ERROR: no routed paths detected in manifest", file=sys.stderr)
        return 2
    missing = sorted(path for path in paths if not (root / path).is_file())
    if missing:
        for path in missing:
            print(f"MISSING: {path}")
        return 1
    print(f"OK: all manifest paths exist ({len(paths)} paths checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
