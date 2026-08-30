"""Compare protected manuscript elements before and after prose revision."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

SUPPORTED_SUFFIXES = {".md", ".tex", ".txt"}
NUMBER_BODY = r"[-+]?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][-+]?\d+)?%?"
NUMBER_PATTERN = re.compile(
    rf"(?<![A-Za-z0-9_\\]){NUMBER_BODY}(?![A-Za-z0-9_])"
)
CITATION_PATTERN = re.compile(
    r"\\(?:parencite|textcite|citep|citet|cite)\w*\*?"
    r"\s*(?:\[[^\]\r\n]*\]\s*)*\{[^{}\r\n]*\}"
)
LABEL_PATTERN = re.compile(r"\\label\s*\{[^{}\r\n]*\}")
REFERENCE_PATTERN = re.compile(
    r"\\(?:autoref|eqref|Cref|cref|ref)\*?\s*\{[^{}\r\n]*\}"
)
NUMERIC_BINDING_PATTERN = re.compile(
    rf"(?P<anchor>[A-Za-z][A-Za-z0-9_.-]{{0,31}}|[\u4e00-\u9fff]{{1,12}})"
    rf"\s*(?:取值为|等于|达到|为|=|:|：)\s*(?P<value>{NUMBER_BODY})(?![\w])"
)
FORMULA_PATTERN = re.compile(
    r"\\begin\{(?:equation|align|gather|multline)\*?\}.*?"
    r"\\end\{(?:equation|align|gather|multline)\*?\}"
    r"|\$\$.*?\$\$"
    r"|\\\[.*?\\\]"
    r"|\\\(.*?\\\)"
    r"|(?<!\$)\$(?!\$).*?(?<!\$)\$(?!\$)",
    re.DOTALL,
)


@dataclass(frozen=True)
class ProtectedSnapshot:
    """Immutable multiset representation of protected manuscript elements."""

    numbers: tuple[tuple[str, int], ...]
    formulas: tuple[tuple[str, int], ...]
    citations: tuple[tuple[str, int], ...]
    labels: tuple[tuple[str, int], ...]
    references: tuple[tuple[str, int], ...]


def _counter_tuple(values: list[str]) -> tuple[tuple[str, int], ...]:
    return tuple(sorted(Counter(values).items()))


def _normalize_formula(value: str) -> str:
    return re.sub(r"\s+", "", value)


def _latex_tokens(pattern: re.Pattern[str], text: str) -> list[str]:
    return [match.group(0) for match in pattern.finditer(text)]


def _normalize_anchor(value: str) -> str:
    return re.sub(r"\s+", "", value).casefold()


def _numeric_bindings(text: str) -> dict[str, list[str]]:
    bindings: dict[str, list[str]] = {}
    for match in NUMERIC_BINDING_PATTERN.finditer(text):
        anchor = _normalize_anchor(match.group("anchor"))
        bindings.setdefault(anchor, []).append(match.group("value"))
    return {anchor: sorted(values) for anchor, values in sorted(bindings.items())}


def _binding_conflicts(
    before: Mapping[str, list[str]], after: Mapping[str, list[str]]
) -> list[dict[str, object]]:
    return [
        {"anchor": anchor, "before": before[anchor], "after": after[anchor]}
        for anchor in sorted(before.keys() & after.keys())
        if Counter(before[anchor]) != Counter(after[anchor])
    ]


def _canonical_value(value: object) -> str | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return str(value) if isinstance(value, int) else format(value, ".15g")


def _canonical_numeric_bindings(
    project_facts: Mapping[str, Any] | None,
) -> dict[str, str]:
    if project_facts is None:
        return {}
    candidates: dict[str, set[str]] = {}

    def register(anchor: object, value: object) -> None:
        canonical = _canonical_value(value)
        if not isinstance(anchor, str) or not anchor.strip() or canonical is None:
            return
        candidates.setdefault(_normalize_anchor(anchor), set()).add(canonical)

    model = project_facts.get("model")
    if isinstance(model, Mapping):
        parameters = model.get("parameters", [])
        if isinstance(parameters, list):
            for item in parameters:
                if not isinstance(item, Mapping):
                    continue
                for field in ("id", "symbol", "meaning"):
                    register(item.get(field), item.get("value"))
    results = project_facts.get("results", [])
    if isinstance(results, list):
        for item in results:
            if isinstance(item, Mapping):
                register(item.get("id"), item.get("value"))
    return {
        anchor: next(iter(values))
        for anchor, values in sorted(candidates.items())
        if len(values) == 1
    }


def _canonical_conflicts(
    bindings: Mapping[str, list[str]], canonical: Mapping[str, str]
) -> list[dict[str, object]]:
    return [
        {"anchor": anchor, "expected": canonical[anchor], "observed": values}
        for anchor, values in sorted(bindings.items())
        if anchor in canonical and any(value != canonical[anchor] for value in values)
    ]


def snapshot(text: str) -> ProtectedSnapshot:
    """Extract protected elements as immutable multisets."""
    return ProtectedSnapshot(
        numbers=_counter_tuple(NUMBER_PATTERN.findall(text)),
        formulas=_counter_tuple(
            [_normalize_formula(value) for value in FORMULA_PATTERN.findall(text)]
        ),
        citations=_counter_tuple(_latex_tokens(CITATION_PATTERN, text)),
        labels=_counter_tuple(_latex_tokens(LABEL_PATTERN, text)),
        references=_counter_tuple(_latex_tokens(REFERENCE_PATTERN, text)),
    )


def compare(
    before: str,
    after: str,
    project_facts: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    """Return a deterministic comparison report."""
    before_snapshot = snapshot(before)
    after_snapshot = snapshot(after)
    changes: dict[str, dict[str, object]] = {}
    for field_name in ProtectedSnapshot.__dataclass_fields__:
        before_value = getattr(before_snapshot, field_name)
        after_value = getattr(after_snapshot, field_name)
        if before_value != after_value:
            changes[field_name] = {
                "before": before_value,
                "after": after_value,
            }
    before_bindings = _numeric_bindings(before)
    after_bindings = _numeric_bindings(after)
    binding_conflicts = _binding_conflicts(before_bindings, after_bindings)
    canonical = _canonical_numeric_bindings(project_facts)
    canonical_conflicts = _canonical_conflicts(after_bindings, canonical)
    if binding_conflicts:
        changes["numeric_bindings"] = {"conflicts": binding_conflicts}
    if canonical_conflicts:
        changes["project_facts"] = {"conflicts": canonical_conflicts}
    before_numbers = Counter(dict(before_snapshot.numbers))
    after_numbers = Counter(dict(after_snapshot.numbers))
    added_numbers = sorted((after_numbers - before_numbers).elements())
    removed_numbers = sorted((before_numbers - after_numbers).elements())
    return {
        "status": "PASS" if not changes else "FAIL",
        "protected_elements_unchanged": not changes,
        "changes": changes,
        "before": asdict(before_snapshot),
        "after": asdict(after_snapshot),
        "number_delta": {
            "added": added_numbers,
            "removed": removed_numbers,
        },
        "numeric_binding": {
            "before": before_bindings,
            "after": after_bindings,
            "conflicts": binding_conflicts,
        },
        "project_facts_validation": {
            "status": "NOT_PROVIDED"
            if project_facts is None
            else ("FAIL" if canonical_conflicts else "PASS"),
            "canonical_bindings": canonical,
            "conflicts": canonical_conflicts,
        },
    }


def _read_text(path: Path) -> str:
    if path.suffix.lower() not in SUPPORTED_SUFFIXES:
        raise ValueError(f"Unsupported manuscript format: {path.suffix}")
    return path.read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path, nargs="?")
    parser.add_argument("after", type=Path, nargs="?")
    parser.add_argument(
        "--stdin-json",
        action="store_true",
        help="Read an object with before and after strings from stdin.",
    )
    parser.add_argument("--before-text")
    parser.add_argument("--after-text")
    parser.add_argument(
        "--project-facts",
        type=Path,
        help="Optional validated Project Facts JSON used for canonical numeric checks.",
    )
    args = parser.parse_args()
    try:
        project_facts: Mapping[str, Any] | None = None
        if args.project_facts is not None:
            loaded_facts = json.loads(args.project_facts.read_text(encoding="utf-8"))
            if not isinstance(loaded_facts, dict):
                raise TypeError("Project Facts must be a JSON object")
            project_facts = loaded_facts
        if args.before_text is not None or args.after_text is not None:
            if args.before_text is None or args.after_text is None:
                parser.error("--before-text and --after-text must be used together")
            report = compare(args.before_text, args.after_text, project_facts)
        elif args.stdin_json:
            payload = json.load(sys.stdin)
            if not isinstance(payload, dict):
                raise TypeError("stdin JSON must be an object")
            before = payload.get("before")
            after = payload.get("after")
            if not isinstance(before, str) or not isinstance(after, str):
                raise TypeError("stdin JSON before and after must be strings")
            report = compare(before, after, project_facts)
        else:
            if args.before is None or args.after is None:
                parser.error(
                    "before and after paths are required without text input options"
                )
            report = compare(
                _read_text(args.before), _read_text(args.after), project_facts
            )
    except (json.JSONDecodeError, OSError, TypeError, UnicodeError, ValueError) as error:
        sys.stderr.write(f"ERROR: {error}\n")
        return 2
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    sys.stdout.buffer.write(output.encode("utf-8"))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
