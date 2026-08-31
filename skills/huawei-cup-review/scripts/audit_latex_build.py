#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ERROR_PATTERNS = [
    (re.compile(r"^! LaTeX Error:", re.MULTILINE), "LaTeX Error"),
    (re.compile(r"Too many unprocessed floats", re.IGNORECASE), "too many unprocessed floats"),
    (re.compile(r"Float\(s\) lost", re.IGNORECASE), "lost float"),
    (re.compile(r"Float too large for page", re.IGNORECASE), "float too large"),
]

WARNING_PATTERNS = [
    (re.compile(r"Overfull \\hbox"), "overfull hbox"),
    (re.compile(r"Overfull \\vbox"), "overfull vbox"),
    (re.compile(r"undefined references", re.IGNORECASE), "undefined references"),
    (re.compile(r"Citation .* undefined", re.IGNORECASE), "undefined citation"),
    (re.compile(r"Reference .* undefined", re.IGNORECASE), "undefined reference"),
    (re.compile(r"Rerun to get cross-references right", re.IGNORECASE), "cross references need rerun"),
    (re.compile(r"Label\(s\) may have changed", re.IGNORECASE), "labels changed; rerun required"),
]

FLOAT_RE = re.compile(r"\\begin\{(?:figure|table)\}(?:\[([^\]]*)\])?")
INCLUDE_RE = re.compile(r"\\(?:input|include|subfile)\s*\{([^}]+)\}")


def strip_comments(text: str) -> str:
    out = []
    for line in text.splitlines():
        # Keep escaped percent signs. This is intentionally conservative, not a full TeX parser.
        pos = None
        for i, ch in enumerate(line):
            if ch == "%" and (i == 0 or line[i - 1] != "\\"):
                pos = i
                break
        out.append(line if pos is None else line[:pos])
    return "\n".join(out)


def resolve_include(parent: Path, target: str) -> Path:
    candidate = (parent / target).resolve()
    if candidate.suffix:
        return candidate
    return candidate.with_suffix(".tex")


def collect_tex_sources(master: Path) -> tuple[list[Path], list[str]]:
    seen: set[Path] = set()
    ordered: list[Path] = []
    missing: list[str] = []

    def visit(path: Path) -> None:
        path = path.resolve()
        if path in seen:
            return
        seen.add(path)
        if not path.is_file():
            missing.append(str(path))
            return
        ordered.append(path)
        text = strip_comments(path.read_text(encoding="utf-8", errors="replace"))
        for raw in INCLUDE_RE.findall(text):
            raw = raw.strip()
            # Dynamic macro paths cannot be resolved safely; leave them to TeX/log review.
            if not raw or "\\" in raw or "#" in raw:
                continue
            child = resolve_include(path.parent, raw)
            if child.exists():
                visit(child)
            else:
                missing.append(str(child))

    visit(master)
    return ordered, missing


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit LaTeX project source/log for float and layout risks.")
    ap.add_argument("tex", type=Path, help="Authoritative master .tex source")
    ap.add_argument("--log", type=Path, default=None)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    if not args.tex.exists():
        print(f"ERROR: tex not found: {args.tex}", file=sys.stderr)
        return 2

    sources, missing_includes = collect_tex_sources(args.tex)
    combined_parts = []
    for path in sources:
        combined_parts.append(f"% --- SOURCE: {path} ---\n")
        combined_parts.append(strip_comments(path.read_text(encoding="utf-8", errors="replace")))
    tex = "\n".join(combined_parts)

    log_path = args.log or args.tex.with_suffix(".log")
    log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""

    errors: list[str] = []
    warnings: list[str] = []

    if not log:
        warnings.append(f"build log not found: {log_path}")
    else:
        for pattern, label in ERROR_PATTERNS:
            n = len(pattern.findall(log))
            if n:
                errors.append(f"{label}: {n}")
        for pattern, label in WARNING_PATTERNS:
            n = len(pattern.findall(log))
            if n:
                warnings.append(f"{label}: {n}")

    for path in missing_includes:
        warnings.append(f"included TeX source not found or unresolved: {path}")

    floats = FLOAT_RE.findall(tex)
    h_count = sum(1 for opts in floats if opts and "H" in opts)
    if floats and h_count >= 3 and h_count / len(floats) >= 0.6:
        warnings.append(f"[H] float placement is used on {h_count}/{len(floats)} floats; review for rigid pagination")

    if re.search(r"\\clearpage\s*(?:%[^\n]*)?\n\s*\\section", tex):
        warnings.append("\\clearpage appears immediately before a section; verify it is intentional")

    print(f"SOURCE_FILES_SCANNED: {len(sources)}")
    for path in sources:
        print(f"SOURCE: {path}")
    for item in warnings:
        print(f"WARNING: {item}")
    for item in errors:
        print(f"ERROR: {item}", file=sys.stderr)

    print("NOTE: source/log audit cannot verify actual float placement. Use scope-appropriate PDF rendering and visual review on the current PDF.")

    if errors:
        return 1
    if args.strict and warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
