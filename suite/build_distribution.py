#!/usr/bin/env python3
"""Build a deterministic Huawei Cup Suite ZIP from a local Git tag."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import subprocess
import sys
import zipfile
from collections.abc import Iterable, Mapping
from pathlib import Path, PurePosixPath
from typing import Any

import yaml


def _git(repo: Path, *args: str, text: bool = True) -> str | bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=text,
        encoding="utf-8" if text else None,
    )
    return result.stdout


def _tag_commit(repo: Path, tag: str) -> str:
    output = _git(repo, "rev-parse", f"refs/tags/{tag}^{{commit}}")
    assert isinstance(output, str)
    return output.strip()


def _manifest_at_tag(repo: Path, tag: str) -> dict[str, Any]:
    output = _git(repo, "show", f"{tag}:suite/manifest.yaml")
    assert isinstance(output, str)
    value = yaml.safe_load(output)
    if not isinstance(value, dict):
        raise TypeError("Suite manifest at tag must be an object")
    return value


def _assert_release_preconditions(repo: Path, tag: str, commit: str) -> None:
    """Require a clean checkout at the exact tag before packaging."""
    head = _git(repo, "rev-parse", "HEAD")
    assert isinstance(head, str)
    if head.strip() != commit:
        raise ValueError(
            f"release tag must point to HEAD: tag={tag}, tag_commit={commit}, "
            f"head={head.strip()}"
        )

    status = _git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    assert isinstance(status, str)
    if status.strip():
        raise ValueError("release checkout must be clean before packaging")

    validator = repo / "suite" / "validate_suite.py"
    manifest = repo / "suite" / "manifest.yaml"
    if not validator.is_file() or not manifest.is_file():
        raise ValueError("release checkout lacks the Suite validator or manifest")
    result = subprocess.run(
        [sys.executable, str(validator), str(manifest)],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        detail = (result.stdout + result.stderr).strip()
        raise ValueError(f"Suite validation failed before packaging: {detail}")


def _matches_exclusion(path: PurePosixPath, exclusions: Iterable[str]) -> bool:
    parts = path.parts
    for exclusion in exclusions:
        normalized = exclusion.strip("/")
        if not normalized:
            continue
        if any(character in normalized for character in "*?["):
            if fnmatch.fnmatch(path.name, normalized) or fnmatch.fnmatch(
                path.as_posix(), normalized
            ):
                return True
        elif "/" in normalized:
            if path.as_posix() == normalized or path.as_posix().startswith(
                normalized + "/"
            ):
                return True
        elif normalized in parts:
            return True
    return False


def select_distribution_paths(
    paths: Iterable[str], distribution: Mapping[str, Any]
) -> list[str]:
    """Select distributable Git paths using the Suite manifest contract."""
    includes = [str(item).strip("/") for item in distribution.get("include", [])]
    exclusions = [str(item) for item in distribution.get("exclude", [])]
    selected: list[str] = []
    for raw_path in paths:
        path = PurePosixPath(raw_path)
        value = path.as_posix()
        included = any(
            value == item or value.startswith(item + "/") for item in includes
        )
        if included and not _matches_exclusion(path, exclusions):
            selected.append(value)
    return sorted(set(selected))


def build_distribution(repo: Path, tag: str, output: Path) -> dict[str, object]:
    """Build one deterministic ZIP and SHA-256 sidecar from a tagged Git tree."""
    repo = repo.resolve()
    commit = _tag_commit(repo, tag)
    _assert_release_preconditions(repo, tag, commit)
    manifest = _manifest_at_tag(repo, tag)
    distribution = manifest.get("distribution")
    suite = manifest.get("suite")
    if not isinstance(distribution, Mapping) or not isinstance(suite, Mapping):
        raise TypeError("Suite manifest lacks distribution or suite declaration")
    tree_output = _git(repo, "ls-tree", "-r", "--name-only", tag)
    assert isinstance(tree_output, str)
    paths = select_distribution_paths(tree_output.splitlines(), distribution)
    if not paths:
        raise ValueError("Distribution path selection is empty")

    version = str(suite.get("version"))
    prefix = f"huawei-cup-modeling-skills-{version}"
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in paths:
            blob = _git(repo, "show", f"{tag}:{path}", text=False)
            assert isinstance(blob, bytes)
            info = zipfile.ZipInfo(f"{prefix}/{path}", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, blob)

    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    checksum_path = output.with_suffix(output.suffix + ".sha256")
    checksum_path.write_text(f"{digest}  {output.name}\n", encoding="ascii")
    return {
        "status": "PASS",
        "tag": tag,
        "commit": commit,
        "suite_version": version,
        "file_count": len(paths),
        "zip": str(output),
        "sha256": digest,
        "checksum_file": str(checksum_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", default="v1.0.0-rc1")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dist/huawei-cup-modeling-skills-1.0.0-rc1.zip"),
    )
    parser.add_argument("--repo", type=Path, default=Path(__file__).parents[1])
    args = parser.parse_args()
    try:
        report = build_distribution(args.repo, args.tag, args.output)
    except (
        OSError,
        TypeError,
        ValueError,
        subprocess.CalledProcessError,
        yaml.YAMLError,
    ) as error:
        report = {"status": "BLOCKED", "errors": [str(error)]}
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    sys.stdout.buffer.write(output.encode("utf-8"))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
