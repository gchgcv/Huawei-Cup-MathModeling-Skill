#!/usr/bin/env python3
"""Check DOCX parts for editable Word equations and obvious raw LaTeX."""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
}

LATEX_COMMAND_RE = re.compile(
    r"\\(?:frac|dfrac|tfrac|sum|int|iint|iiint|prod|sqrt|alpha|beta|gamma|delta|lambda|mu|sigma|theta|omega|begin|end|left|right|mathbf|mathrm|text|overline|hat|vec)\b"
)

PART_RE = re.compile(r"^word/(?:document|header\d+|footer\d+|footnotes|endnotes)\.xml$")


def load_parts(docx_path: Path):
    try:
        with zipfile.ZipFile(docx_path) as zf:
            names = [n for n in zf.namelist() if PART_RE.match(n)]
            if "word/document.xml" not in names:
                raise RuntimeError("word/document.xml not found; invalid DOCX")
            return {name: zf.read(name) for name in names}
    except zipfile.BadZipFile as exc:
        raise RuntimeError("file is not a valid DOCX/ZIP archive") from exc


def inspect_part(raw: bytes):
    root = ET.fromstring(raw)
    # Count only m:oMath. Each displayed oMathPara normally contains an oMath child,
    # so adding both would double-count one equation.
    equations = root.findall(".//m:oMath", NS)
    text = "\n".join((node.text or "") for node in root.findall(".//w:t", NS))
    hits = sorted(set(LATEX_COMMAND_RE.findall(text)))
    return len(equations), hits


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify DOCX math objects.")
    parser.add_argument("docx", help="Path to .docx file")
    parser.add_argument("--min-equations", type=int, default=1)
    args = parser.parse_args()

    path = Path(args.docx)
    if not path.is_file():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2

    try:
        parts = load_parts(path)
        total = 0
        all_hits = set()
        for name, raw in parts.items():
            count, hits = inspect_part(raw)
            total += count
            all_hits.update(hits)
            print(f"{name}: equations={count}, raw_latex={','.join(hits) if hits else 'none'}")
    except (RuntimeError, ET.ParseError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"total_omml_equations: {total}")
    failed = False
    if total < args.min_equations:
        print(f"ERROR: expected at least {args.min_equations} equation(s)", file=sys.stderr)
        failed = True
    if all_hits:
        print("ERROR: raw LaTeX commands found in normal text", file=sys.stderr)
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
