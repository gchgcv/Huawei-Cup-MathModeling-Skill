#!/usr/bin/env python3
"""Audit canonical figure outputs and safely quarantine unexpected artifacts.

Default mode is dry-run. With --apply-trash, unexpected unreferenced image files are
moved into the configured .trash directory. Files are never deleted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".pdf", ".svg", ".eps", ".webp"}
TEXT_EXTS = {".tex", ".md", ".py", ".json", ".yaml", ".yml", ".txt", ".sty", ".cls"}
NUMBERED_RE = re.compile(r"^\d{1,3}[_-]")


def normalize_rel(value: str) -> str:
    return Path(value).as_posix().lstrip("./")


def collect_declared(data: dict) -> tuple[set[str], set[str]]:
    canonical: set[str] = set()
    for item in data.get("canonical", []):
        if isinstance(item, str):
            canonical.add(normalize_rel(item))
        elif isinstance(item, dict) and str(item.get("file", "")).strip():
            canonical.add(normalize_rel(str(item["file"])))
    allowed = {normalize_rel(str(x)) for x in data.get("allowed_files", []) if str(x).strip()}
    return canonical, allowed


def scan_references(project_root: Path, targets: set[str], trash_dir: Path) -> dict[str, list[str]]:
    refs: dict[str, list[str]] = {name: [] for name in targets}
    if not targets:
        return refs
    basenames = {name: Path(name).name for name in targets}
    for path in project_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTS:
            continue
        try:
            if trash_dir in path.parents:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel_source = path.relative_to(project_root).as_posix()
        for target, base in basenames.items():
            if target in text or base in text:
                refs[target].append(rel_source)
    return refs


def unique_destination(trash_dir: Path, source: Path) -> Path:
    dest = trash_dir / source.name
    if not dest.exists():
        return dest
    i = 1
    while True:
        candidate = trash_dir / f"{source.stem}.{i}{source.suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit canonical formal figure outputs.")
    ap.add_argument("manifest", type=Path)
    ap.add_argument("--project-root", type=Path, default=Path("."))
    ap.add_argument("--apply-trash", action="store_true", help="Move safe unexpected files to .trash; never delete")
    ap.add_argument("--confirm-plan-hash", default="", help="Required with --apply-trash; copy TRASH_PLAN_HASH from a prior dry-run")
    args = ap.parse_args()

    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read manifest: {exc}", file=sys.stderr)
        return 2

    project_root = args.project_root.resolve()
    figure_root_rel = normalize_rel(str(data.get("figure_root", "outputs/figures")))
    figure_root = (project_root / figure_root_rel).resolve()
    trash_rel = normalize_rel(str(data.get("trash_dir", f"{figure_root_rel}/.trash")))
    trash_dir = (project_root / trash_rel).resolve()

    if not figure_root.exists():
        print(f"ERROR: figure_root not found: {figure_root}", file=sys.stderr)
        return 2
    if project_root not in figure_root.parents and figure_root != project_root:
        print("ERROR: figure_root must stay inside project_root", file=sys.stderr)
        return 2
    if figure_root not in trash_dir.parents:
        print("ERROR: trash_dir must stay inside figure_root", file=sys.stderr)
        return 2

    canonical, allowed = collect_declared(data)
    if not canonical:
        print("ERROR: canonical list is empty", file=sys.stderr)
        return 2

    actual: set[str] = set()
    for path in figure_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTS:
            continue
        if trash_dir == path.parent or trash_dir in path.parents:
            continue
        actual.add(path.relative_to(figure_root).as_posix())

    missing = sorted(canonical - actual)
    unexpected = sorted(actual - canonical - allowed)
    nonnumbered = sorted(name for name in actual if not NUMBERED_RE.match(Path(name).name))
    refs = scan_references(project_root, set(unexpected), trash_dir)
    referenced_unexpected = {name: paths for name, paths in refs.items() if paths}
    plan_payload = json.dumps({
        "figure_root": figure_root_rel,
        "canonical": sorted(canonical),
        "allowed": sorted(allowed),
        "unexpected": unexpected,
        "referenced": referenced_unexpected,
    }, ensure_ascii=False, sort_keys=True).encode("utf-8")
    plan_hash = hashlib.sha256(plan_payload).hexdigest()[:16]

    print(f"MODE: {'APPLY_TRASH' if args.apply_trash else 'DRY_RUN'}")
    print(f"FIGURE_ROOT: {figure_root_rel}")
    print(f"CANONICAL_COUNT: {len(canonical)}")
    print(f"ACTUAL_COUNT: {len(actual)}")
    print(f"TRASH_PLAN_HASH: {plan_hash}")

    for name in missing:
        print(f"ERROR: missing canonical figure: {name}", file=sys.stderr)
    for name in unexpected:
        suffix = f" referenced_by={','.join(referenced_unexpected.get(name, []))}" if name in referenced_unexpected else ""
        print(f"UNEXPECTED: {name}{suffix}")
    for name in nonnumbered:
        print(f"WARNING: non-numbered figure filename: {name}")

    moved: list[str] = []
    blocked: list[str] = []
    if args.apply_trash:
        if not args.confirm_plan_hash:
            print("ERROR: --apply-trash requires --confirm-plan-hash from a prior dry-run", file=sys.stderr)
            return 2
        if args.confirm_plan_hash != plan_hash:
            print(
                f"ERROR: trash plan changed or hash is stale: expected {plan_hash}, got {args.confirm_plan_hash}",
                file=sys.stderr,
            )
            return 1
    if args.apply_trash and unexpected:
        trash_dir.mkdir(parents=True, exist_ok=True)
        for name in unexpected:
            if name in referenced_unexpected:
                blocked.append(name)
                print(f"BLOCKED: referenced unexpected figure not moved: {name}", file=sys.stderr)
                continue
            src = figure_root / name
            if not src.exists():
                continue
            dst = unique_destination(trash_dir, src)
            shutil.move(str(src), str(dst))
            moved.append(name)
            print(f"MOVED_TO_TRASH: {name} -> {dst.relative_to(project_root).as_posix()}")

    if not args.apply_trash and unexpected:
        print("NOTE: dry-run only; after reviewing references, rerun with --apply-trash --confirm-plan-hash <TRASH_PLAN_HASH>. Files will be moved, never deleted.")

    if missing or blocked:
        return 1
    if unexpected and not args.apply_trash:
        return 1
    if args.apply_trash and len(moved) != len(unexpected):
        return 1
    print("OK: canonical figure output set is clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
