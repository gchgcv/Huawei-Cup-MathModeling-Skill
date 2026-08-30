"""Compare protected manuscript elements before and after prose revision."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

SUPPORTED_SUFFIXES = {".md", ".tex", ".txt"}
NUMBER_PATTERN = re.compile(
    r"(?<![\w\\])[-+]?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][-+]?\d+)?%?(?![\w])"
)
CITATION_PATTERN = re.compile(
    r"\\(?:cite|citep|citet|parencite|textcite)\w*"
    r"\s*(?:\[[^\]]*\]\s*)*\{([^}]*)\}"
)
LABEL_PATTERN = re.compile(r"\\label\{([^}]*)\}")
REFERENCE_PATTERN = re.compile(r"\\(?:ref|eqref|autoref|cref|Cref)\{([^}]*)\}")
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
    return re.sub(r"\s+", " ", value).strip()


def _citation_keys(text: str) -> list[str]:
    keys: list[str] = []
    for match in CITATION_PATTERN.finditer(text):
        keys.extend(key.strip() for key in match.group(1).split(",") if key.strip())
    return keys


def snapshot(text: str) -> ProtectedSnapshot:
    """Extract protected elements as immutable multisets."""
    return ProtectedSnapshot(
        numbers=_counter_tuple(NUMBER_PATTERN.findall(text)),
        formulas=_counter_tuple(
            [_normalize_formula(value) for value in FORMULA_PATTERN.findall(text)]
        ),
        citations=_counter_tuple(_citation_keys(text)),
        labels=_counter_tuple(LABEL_PATTERN.findall(text)),
        references=_counter_tuple(REFERENCE_PATTERN.findall(text)),
    )


def compare(before: str, after: str) -> dict[str, object]:
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
    args = parser.parse_args()
    try:
        if args.before_text is not None or args.after_text is not None:
            if args.before_text is None or args.after_text is None:
                parser.error("--before-text and --after-text must be used together")
            report = compare(args.before_text, args.after_text)
        elif args.stdin_json:
            payload = json.load(sys.stdin)
            if not isinstance(payload, dict):
                raise TypeError("stdin JSON must be an object")
            before = payload.get("before")
            after = payload.get("after")
            if not isinstance(before, str) or not isinstance(after, str):
                raise TypeError("stdin JSON before and after must be strings")
            report = compare(before, after)
        else:
            if args.before is None or args.after is None:
                parser.error(
                    "before and after paths are required without text input options"
                )
            report = compare(_read_text(args.before), _read_text(args.after))
    except (json.JSONDecodeError, OSError, TypeError, UnicodeError, ValueError) as error:
        sys.stderr.write(f"ERROR: {error}\n")
        return 2
    sys.stdout.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
