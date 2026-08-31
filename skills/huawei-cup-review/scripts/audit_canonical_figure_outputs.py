#!/usr/bin/env python3
"""Read-only audit of a manifest-backed canonical figure output set."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".pdf", ".svg", ".eps", ".webp"}
TEXT_EXTS = {".tex", ".md", ".py", ".json", ".yaml", ".yml", ".txt", ".sty", ".cls"}
NUMBERED_RE = re.compile(r"^\d{1,3}[_-]")


def normalize_rel(value: str) -> str:
    normalized = value.replace("\\", "/").strip()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def collect_declared(data: dict[str, Any]) -> tuple[set[str], set[str]]:
    canonical: set[str] = set()
    for item in data.get("canonical", []):
        if isinstance(item, str) and item.strip():
            canonical.add(normalize_rel(item))
        elif isinstance(item, dict) and str(item.get("file", "")).strip():
            canonical.add(normalize_rel(str(item["file"])))
    allowed = {
        normalize_rel(str(value))
        for value in data.get("allowed_files", [])
        if str(value).strip()
    }
    return canonical, allowed


def resolve_inside(root: Path, relative: str, field: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute():
        raise ValueError(f"{field} must be relative to its containing root: {relative}")
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{field} must stay inside its containing root: {relative}") from exc
    return resolved


def scan_references(
    project_root: Path,
    targets: set[str],
    ignored_root: Path,
) -> dict[str, list[str]]:
    references: dict[str, list[str]] = {name: [] for name in targets}
    if not targets:
        return references
    basenames = {name: Path(name).name for name in targets}
    for path in project_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTS:
            continue
        if path == ignored_root or ignored_root in path.parents:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        relative_source = path.relative_to(project_root).as_posix()
        for target, basename in basenames.items():
            if target in text or basename in text:
                references[target].append(relative_source)
    return references


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read manifest: {exc}") from exc
    if not isinstance(value, dict):
        raise TypeError("manifest root must be an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit canonical figure outputs without changing project files."
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat non-numbered unexpected filenames as an audit failure.",
    )
    args = parser.parse_args()

    try:
        manifest = load_manifest(args.manifest)
        project_root = args.project_root.resolve()
        figure_root_rel = normalize_rel(str(manifest.get("figure_root", "outputs/figures")))
        figure_root = resolve_inside(project_root, figure_root_rel, "figure_root")
        trash_rel = normalize_rel(
            str(manifest.get("trash_dir", f"{figure_root_rel}/.trash"))
        )
        trash_path = Path(trash_rel)
        try:
            trash_inside = trash_path.relative_to(Path(figure_root_rel))
        except ValueError:
            trash_inside = trash_path
        trash_dir = resolve_inside(figure_root, trash_inside.as_posix(), "trash_dir")
    except (TypeError, ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if not figure_root.is_dir():
        print(f"ERROR: figure_root not found: {figure_root}", file=sys.stderr)
        return 2

    canonical, allowed = collect_declared(manifest)
    if not canonical:
        print("ERROR: canonical list is empty", file=sys.stderr)
        return 2

    try:
        for name in canonical | allowed:
            resolve_inside(figure_root, name, "canonical/allowed file")
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    actual: set[str] = set()
    for path in figure_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTS:
            continue
        if path == trash_dir or trash_dir in path.parents:
            continue
        actual.add(path.relative_to(figure_root).as_posix())

    missing = sorted(canonical - actual)
    unexpected = sorted(actual - canonical - allowed)
    nonnumbered = sorted(
        name for name in unexpected if not NUMBERED_RE.match(Path(name).name)
    )
    references = scan_references(project_root, set(unexpected), trash_dir)
    referenced_unexpected = {
        name: paths for name, paths in references.items() if paths
    }

    print("MODE: READ_ONLY")
    print("MUTATIONS: none")
    print(f"FIGURE_ROOT: {figure_root_rel}")
    print(f"CANONICAL_COUNT: {len(canonical)}")
    print(f"ACTUAL_COUNT: {len(actual)}")

    for name in missing:
        print(f"ERROR: missing canonical figure: {name}", file=sys.stderr)
    for name in unexpected:
        print(f"UNEXPECTED: {name}")
        if name in referenced_unexpected:
            sources = ",".join(referenced_unexpected[name])
            print(f"REFERENCED_UNEXPECTED: {name} referenced_by={sources}")
    for name in nonnumbered:
        print(f"WARNING: non-numbered unexpected figure filename: {name}")

    if unexpected:
        print(
            "NOTE: unexpected outputs require review by the producing layer; "
            "this checker does not move or remove files."
        )

    if missing or unexpected or (args.strict and nonnumbered):
        return 1
    print("OK: canonical figure output set is clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
