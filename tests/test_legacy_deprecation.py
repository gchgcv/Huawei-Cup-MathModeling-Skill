from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
LEGACY_RELATIVE = Path("legacy/huawei-cup-modeling-writing-v0.9.1")
LEGACY_ROOT = REPO_ROOT / LEGACY_RELATIVE
ROUTER_ROOT = REPO_ROOT / "compat" / "huawei-cup-modeling"
BASELINE_TAG = "baseline-v0.9.1-writing"


def _git_bytes(*args: str) -> bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    return result.stdout


def _git(*args: str) -> str:
    return _git_bytes(*args).decode("utf-8")


def test_legacy_directory_matches_frozen_tag_byte_for_byte() -> None:
    prefix = LEGACY_RELATIVE.as_posix() + "/"
    tracked = [
        line
        for line in _git("ls-tree", "-r", "--name-only", BASELINE_TAG, prefix).splitlines()
        if line
    ]
    assert tracked
    assert not _git("diff", "--name-only", BASELINE_TAG, "--", prefix).strip()
    untracked = _git("ls-files", "--others", "--exclude-standard", "--", prefix)
    assert not untracked.strip()
    for tracked_path in tracked:
        worktree_path = REPO_ROOT / tracked_path
        assert worktree_path.read_bytes() == _git_bytes(
            "show", f"{BASELINE_TAG}:{tracked_path}"
        ), tracked_path


def test_legacy_identity_and_version_remain_historical() -> None:
    manifest = yaml.safe_load((LEGACY_ROOT / "manifest.yaml").read_text(encoding="utf-8"))
    skill = (LEGACY_ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert manifest["name"] == "huawei-cup-modeling"
    assert manifest["version"] == "0.9.1-writing"
    assert "论文写作与审校优先" in skill
    assert not (LEGACY_ROOT / "DEPRECATION.md").exists()


def test_compatibility_router_has_independent_contract() -> None:
    manifest = yaml.safe_load((ROUTER_ROOT / "manifest.yaml").read_text(encoding="utf-8"))
    assert manifest["name"] == "huawei-cup-modeling"
    assert manifest["role"] == "compatibility_router"
    assert manifest["routes"]["paper"]["target"] == "huawei-cup-writing"
    assert manifest["routes"]["audit"]["target"] == "huawei-cup-review"
    assert manifest["routes"]["audit"]["access"] == "read_only"
    assert manifest["dependencies"]["legacy_runtime_fallback"] is False


def test_router_contains_no_legacy_or_professional_policy() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in ROUTER_ROOT.rglob("*")
        if path.is_file() and path.suffix in {".md", ".yaml"}
    )
    assert "Do not read policy from `legacy/`" in text
    assert "BLOCKED_UNSUPPORTED_ROUTE" in text
    for forbidden in ("references/paper-writing.md", "quality-gates.md"):
        assert forbidden not in text
    manifest = yaml.safe_load((ROUTER_ROOT / "manifest.yaml").read_text(encoding="utf-8"))
    assert manifest["policy"]["owns_submission_state"] is False


def test_router_targets_exist_without_modifying_baseline() -> None:
    assert (REPO_ROOT / "skills" / "huawei-cup-writing" / "SKILL.md").is_file()
    assert (REPO_ROOT / "skills" / "huawei-cup-review" / "SKILL.md").is_file()
    assert not _git("diff", "--name-only", BASELINE_TAG, "--", str(LEGACY_RELATIVE)).strip()
