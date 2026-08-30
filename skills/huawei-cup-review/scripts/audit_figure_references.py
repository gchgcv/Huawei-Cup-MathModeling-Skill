#!/usr/bin/env python3
"""Read-only audit of LaTeX figure files, captions, labels, and references."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

FIGURE_RE = re.compile(r"\\begin\{figure\*?\}(.*?)\\end\{figure\*?\}", re.DOTALL)
SUBFIGURE_RE = re.compile(r"\\begin\{subfigure\}(.*?)\\end\{subfigure\}", re.DOTALL)
GRAPHIC_RE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
CAPTION_RE = re.compile(r"\\caption\{([^}]*)\}", re.DOTALL)
LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
REF_RE = re.compile(r"\\(?:ref|autoref|cref)\{([^}]+)\}")
INCLUDE_RE = re.compile(r"\\(?:input|include|subfile)\s*\{([^}]+)\}")
GRAPHIC_EXTENSIONS = (".pdf", ".png", ".jpg", ".jpeg", ".eps")


def strip_comments(text: str) -> str:
    """Remove unescaped LaTeX comments conservatively."""
    lines: list[str] = []
    for line in text.splitlines():
        cut = next(
            (index for index, char in enumerate(line) if char == "%" and (index == 0 or line[index - 1] != "\\")),
            None,
        )
        lines.append(line if cut is None else line[:cut])
    return "\n".join(lines)


def resolve_tex_sources(master: Path) -> tuple[list[Path], list[str]]:
    """Resolve static input/include/subfile paths without modifying sources."""
    seen: set[Path] = set()
    ordered: list[Path] = []
    missing: list[str] = []

    def visit(path: Path) -> None:
        resolved = path.resolve()
        if resolved in seen:
            return
        seen.add(resolved)
        if not resolved.is_file():
            missing.append(str(resolved))
            return
        ordered.append(resolved)
        text = strip_comments(resolved.read_text(encoding="utf-8", errors="replace"))
        for target in INCLUDE_RE.findall(text):
            if "\\" in target or "#" in target:
                continue
            child = (resolved.parent / target.strip()).resolve()
            if not child.suffix:
                child = child.with_suffix(".tex")
            visit(child)

    visit(master)
    return ordered, missing


def graphic_exists(source: Path, target: str) -> bool:
    """Check an explicit or extensionless graphic path relative to its source."""
    candidate = (source.parent / target).resolve()
    if candidate.suffix:
        return candidate.is_file()
    return any(candidate.with_suffix(extension).is_file() for extension in GRAPHIC_EXTENSIONS)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tex", type=Path, help="Authoritative master .tex source")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failure")
    args = parser.parse_args()
    if not args.tex.is_file():
        print(f"ERROR: tex not found: {args.tex}", file=sys.stderr)
        return 2

    sources, missing_sources = resolve_tex_sources(args.tex)
    warnings = [f"included TeX source not found: {path}" for path in missing_sources]
    labels: list[str] = []
    reference_required_labels: list[str] = []
    references: set[str] = set()
    figure_count = 0

    for source in sources:
        text = strip_comments(source.read_text(encoding="utf-8", errors="replace"))
        references.update(REF_RE.findall(text))
        for figure in FIGURE_RE.findall(text):
            figure_count += 1
            graphics = GRAPHIC_RE.findall(figure)
            all_figure_labels = LABEL_RE.findall(figure)
            outer_figure = SUBFIGURE_RE.sub("", figure)
            captions = CAPTION_RE.findall(outer_figure)
            figure_labels = LABEL_RE.findall(outer_figure)
            if not graphics:
                warnings.append(f"{source}: figure {figure_count} has no includegraphics")
            for target in graphics:
                if not graphic_exists(source, target):
                    warnings.append(f"{source}: graphic not found: {target}")
            if len(captions) != 1 or not captions[0].strip():
                warnings.append(f"{source}: figure {figure_count} must have one non-empty caption")
            if len(figure_labels) != 1:
                warnings.append(f"{source}: figure {figure_count} must have one label")
            labels.extend(all_figure_labels)
            reference_required_labels.extend(figure_labels)

    duplicate_labels = sorted({label for label in labels if labels.count(label) > 1})
    for label in duplicate_labels:
        warnings.append(f"duplicate figure label: {label}")
    for label in sorted(set(reference_required_labels) - references):
        warnings.append(f"figure label is not referenced in scanned text: {label}")

    print(f"SOURCE_FILES_SCANNED: {len(sources)}")
    print(f"FIGURES_SCANNED: {figure_count}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    print(f"FIGURE_REFERENCE_AUDIT: {len(warnings)} warning(s)")
    return 1 if args.strict and warnings else 0


if __name__ == "__main__":
    raise SystemExit(main())
