from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STANDARD_ROOT = REPO_ROOT / "shared" / "paper-quality-standard"
RULE_HEADER = re.compile(r"^## ([A-Z]+-\d{3}) — .+$", re.MULTILINE)
RELATION_ID = re.compile(r"`([A-Z]+-\d{3})`")
REQUIRED_FIELDS = (
    "- **Normative Statement:**",
    "- **Scope:**",
    "- **Required Exceptions:**",
    "- **Relations:**",
)
EXPECTED_PREFIXES = {
    "academic-prose.md": "PROSE",
    "anti-ai-style.md": "AI",
    "anti-defensive-writing.md": "ADW",
    "argument-depth.md": "DEPTH",
    "claim-evidence.md": "CLAIM",
    "abstract-standard.md": "ABS",
    "section-structure.md": "STRUCT",
    "figure-table-standard.md": "FIG",
    "academic-format.md": "FMT",
    "number-unit-precision.md": "NUM",
    "terminology.md": "TERM",
    "reference-standard.md": "REF",
}
FORBIDDEN_ROLE_OR_STATE_TOKENS = (
    "READY_TO_SUBMIT",
    "writes_performed",
    "submission_status",
    "severity",
    "workflow",
    "Writer",
    "Reviewer",
    "Writing Skill",
    "Review Skill",
)


def _rule_files() -> list[Path]:
    return sorted(STANDARD_ROOT.glob("*.md"))


def _rule_blocks(text: str) -> list[tuple[str, str]]:
    matches = list(RULE_HEADER.finditer(text))
    blocks: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append((match.group(1), text[match.end() : end]))
    return blocks


def test_registry_and_expected_standard_files_exist() -> None:
    assert (STANDARD_ROOT / "README.md").is_file()
    actual = {path.name for path in _rule_files() if path.name != "README.md"}
    assert actual == set(EXPECTED_PREFIXES)


def test_figure_standard_includes_language_context_rule() -> None:
    text = (STANDARD_ROOT / "figure-table-standard.md").read_text(encoding="utf-8")
    assert "## FIG-008 — 图表语言与论文语境一致" in text
    assert "主要坐标轴名称、图例、方案或类别名称" in text
    assert "可以保留标准形式" in text


def test_shared_rules_cover_model_context_linkage_and_bounded_scope() -> None:
    depth = (STANDARD_ROOT / "argument-depth.md").read_text(encoding="utf-8")
    structure = (STANDARD_ROOT / "section-structure.md").read_text(encoding="utf-8")
    claims = (STANDARD_ROOT / "claim-evidence.md").read_text(encoding="utf-8")
    defensive = (STANDARD_ROOT / "anti-defensive-writing.md").read_text(
        encoding="utf-8"
    )

    for phrase in (
        "题目特征",
        "关键公式",
        "关键参数",
        "数值、单位、来源",
        "责任、输入输出",
    ):
        assert phrase in depth
    for phrase in ("自然对照", "题目要求的输出", "决策含义"):
        assert phrase in depth
    assert "实际传递的变量、参数、结果、约束或模型输出" in structure
    assert "现实、工程、物理或决策含义" in structure
    for phrase in ("适用对象", "必要条件", "验证层级", "不能外推"):
        assert phrase in claims
    assert "摘要和结论" in claims
    assert "破坏模型、数据或证据成立基础" in defensive


def test_shared_figure_rules_cover_responsibility_and_reading_guidance() -> None:
    text = (STANDARD_ROOT / "figure-table-standard.md").read_text(encoding="utf-8")
    assert "主要论证职责" in text
    assert "读图顺序" in text
    assert "重点区域" in text


def test_rule_ids_are_unique_and_match_file_prefixes() -> None:
    seen: dict[str, Path] = {}
    for path in _rule_files():
        if path.name == "README.md":
            continue
        blocks = _rule_blocks(path.read_text(encoding="utf-8"))
        assert blocks, f"No rules found in {path.name}"
        for rule_id, _ in blocks:
            assert rule_id.startswith(f"{EXPECTED_PREFIXES[path.name]}-")
            assert rule_id not in seen, f"Duplicate {rule_id}: {seen[rule_id]} and {path}"
            seen[rule_id] = path


def test_every_rule_has_the_complete_normative_shape() -> None:
    for path in _rule_files():
        if path.name == "README.md":
            continue
        for rule_id, block in _rule_blocks(path.read_text(encoding="utf-8")):
            for field in REQUIRED_FIELDS:
                assert block.count(field) == 1, f"{rule_id} must contain one {field}"


def test_normative_statements_are_not_duplicated() -> None:
    statements: dict[str, str] = {}
    for path in _rule_files():
        if path.name == "README.md":
            continue
        for rule_id, block in _rule_blocks(path.read_text(encoding="utf-8")):
            statement = block.split("- **Normative Statement:**", maxsplit=1)[1]
            statement = statement.split("\n", maxsplit=1)[0].strip()
            assert statement not in statements, (
                f"Duplicate normative statement: {statements[statement]} and {rule_id}"
            )
            statements[statement] = rule_id


def test_relations_reference_existing_rule_ids() -> None:
    texts = {
        path: path.read_text(encoding="utf-8")
        for path in _rule_files()
        if path.name != "README.md"
    }
    known_ids = {rule_id for text in texts.values() for rule_id in RULE_HEADER.findall(text)}
    referenced_ids: set[str] = set()
    for text in texts.values():
        for _, block in _rule_blocks(text):
            relations = block.split("- **Relations:**", maxsplit=1)[1]
            referenced_ids.update(RELATION_ID.findall(relations))
    assert referenced_ids <= known_ids


def test_shared_standard_contains_no_role_runtime_or_submission_state() -> None:
    for path in _rule_files():
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_ROLE_OR_STATE_TOKENS:
            assert token not in text, f"Forbidden token {token!r} found in {path.name}"
        assert not re.search(r"\bP[012]\b", text)
        assert "python " not in text.lower()


def test_shared_standard_is_not_an_invokable_skill_or_runtime() -> None:
    assert not (STANDARD_ROOT / "SKILL.md").exists()
    assert not (STANDARD_ROOT / "manifest.yaml").exists()
    assert not (STANDARD_ROOT / "scripts").exists()
