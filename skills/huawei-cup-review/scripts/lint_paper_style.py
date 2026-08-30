#!/usr/bin/env python3
"""Flag templated/ornamental prose patterns in Chinese mathematical-modeling papers.

This is a conservative linter. It never rewrites text and must not be used to
replace domain terminology mechanically. High-risk rhetoric is reported as an
error in --strict mode; punctuation and context-dependent patterns remain
warnings for manual review.
"""
from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

HIGH_RISK_PHRASES = [
    "毋庸置疑", "不言而喻", "显而易见", "不难发现",
    "值得注意的是", "需要指出的是", "必须强调的是",
    "深刻揭示", "深刻体现", "切中要害", "不可磨灭的贡献",
    "范式转移", "颠覆性", "革命性", "里程碑式",
    "全面赋能", "有效赋能", "协同增效", "耦合内聚", "形成闭环",
    "本质性提升", "本质上实现", "为后续研究奠定坚实基础",
    "提供强有力支撑", "具有重要理论意义和现实意义",
    "卓越", "强大",
]

TEMPLATE_OPENERS = [
    "首先", "其次", "再次", "最后", "综上所述", "由此可见",
    "在这一背景下", "从某种意义上说", "具体而言", "进一步地",
]

COLON_TEMPLATES = [
    "结果表明：", "分析如下：", "具体如下：", "原因如下：",
    "具体而言：", "值得注意的是：", "需要指出的是：", "由此可见：",
]

SOFT_RISK_PHRASES = [
    "由此可见", "综上所述", "基于上述分析", "在这一背景下",
    "从某种意义上说", "深刻", "本质上", "先进",
]

# Context-dependent defensive writing patterns. These are warnings, not bans.
DEFENSIVE_SCOPE_RE = re.compile(
    r"(?:本文|本研究|本模型|该模型|该结果|上述结果).{0,18}"
    r"(?:不(?:能|应|宜|代表|意味着|声称|试图|旨在)|未(?:能|试图)|无法|无意).{0,22}"
    r"(?:证明|说明|代表|涵盖|覆盖|适用|推广|声称|意味着|解决|刻画)?"
)

CAVEAT_FIRST = (
    "尽管", "虽然", "诚然", "不可否认", "需要说明的是", "必须说明的是",
    "应当说明的是", "需要指出的是", "值得说明的是",
)

HEDGE_TERMS = (
    "可能", "或许", "也许", "似乎", "一定程度上", "在某种程度上", "潜在",
    "初步", "大概", "或可", "或能",
)

WORKLOG_MARKERS = (
    "首先", "随后", "然后", "接着", "之后", "最后",
)

VAGUE_EVALUATIONS = [
    "效果较好", "精度较高", "鲁棒性较强", "稳定性较好", "性能优越",
    "具有较强鲁棒性", "具有较好稳定性", "取得较好效果", "取得理想效果",
    "明显提升", "显著提升", "有效提升", "大幅提升", "结果合理",
]

# Parentheses that are normally technical rather than rhetorical.
TECH_PAREN_RE = re.compile(
    r"（(?:[A-Z][A-Z0-9+_.\-/]{1,15}|\d+(?:[-–—]\d+)?|"
    r"[+-]?\d+(?:\.\d+)?\s*(?:%|℃|°|kg|g|m|cm|mm|s|ms|h|Hz|kHz|MHz|GHz))）"
)

NUMERIC_EVIDENCE_RE = re.compile(
    r"(?:\d+(?:\.\d+)?\s*(?:%|％)?|RMSE|MAE|MAPE|F1|R\^?2|p\s*[<=>]|"
    r"表\s*\d+|图\s*\d+|式[（(]?\d+)"
)

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def extract_docx(path: Path) -> str:
    with zipfile.ZipFile(path) as zf:
        chunks: list[str] = []
        for name in zf.namelist():
            if not (name == "word/document.xml" or name.startswith("word/header") or name.startswith("word/footer")):
                continue
            try:
                root = ET.fromstring(zf.read(name))
            except ET.ParseError:
                continue
            for p in root.findall(f".//{{{W_NS}}}p"):
                text = "".join(t.text or "" for t in p.findall(f".//{{{W_NS}}}t"))
                if text.strip():
                    chunks.append(text.strip())
        return "\n\n".join(chunks)


def read_text(path: Path) -> str:
    if path.suffix.lower() == ".docx":
        return extract_docx(path)
    return path.read_text(encoding="utf-8", errors="ignore")


def strip_nonprose(text: str, suffix: str) -> str:
    # Markdown fenced code.
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    # LaTeX display/inline math and comments. Keep surrounding prose.
    if suffix.lower() == ".tex":
        text = re.sub(r"(?m)%.*$", "", text)
        text = re.sub(r"\\\[.*?\\\]", "", text, flags=re.S)
        text = re.sub(r"\$\$.*?\$\$", "", text, flags=re.S)
        text = re.sub(r"\$[^$]*\$", "", text)
        text = re.sub(r"\\begin\{(?:equation\*?|align\*?|gather\*?|cases)\}.*?\\end\{[^}]+\}", "", text, flags=re.S)
        text = re.sub(r"\\(?:cite|ref|eqref|label)\{[^}]*\}", "", text)
    # Markdown headings/tables are not continuous body prose.
    kept = []
    for line in text.splitlines():
        s = line.strip()
        if suffix.lower() in {".md", ".markdown"} and (s.startswith("#") or (s.startswith("|") and s.endswith("|"))):
            continue
        kept.append(line)
    return "\n".join(kept)


def paragraphize(text: str) -> list[tuple[int, str]]:
    paras: list[tuple[int, str]] = []
    line_no = 1
    start = 1
    buf: list[str] = []
    for line in text.splitlines():
        if line.strip():
            if not buf:
                start = line_no
            buf.append(line.strip())
        elif buf:
            paras.append((start, "".join(buf)))
            buf = []
        line_no += 1
    if buf:
        paras.append((start, "".join(buf)))
    return paras


def sentence_has_evidence(paragraph: str, phrase: str) -> bool:
    for sentence in re.split(r"[。！？!?]", paragraph):
        if phrase in sentence:
            return bool(NUMERIC_EVIDENCE_RE.search(sentence))
    return False


def split_sentences(paragraph: str) -> list[str]:
    return [s.strip() for s in re.split(r"[。！？!?]", paragraph) if s.strip()]


def chinese_char_count(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--strict", action="store_true", help="Treat high-risk rhetoric as errors")
    args = ap.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2
    if path.suffix.lower() not in {".txt", ".md", ".markdown", ".tex", ".docx"}:
        print("ERROR: supported types are .txt/.md/.markdown/.tex/.docx", file=sys.stderr)
        return 2

    try:
        raw = read_text(path)
    except (OSError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    text = strip_nonprose(raw, path.suffix)
    paras = paragraphize(text)

    errors: list[str] = []
    warnings: list[str] = []
    opener_hits: list[tuple[int, str]] = []

    for line, para in paras:
        for phrase in HIGH_RISK_PHRASES:
            if phrase in para:
                msg = f"L{line}: high-risk rhetorical phrase: {phrase}"
                (errors if args.strict else warnings).append(msg)

        for phrase in COLON_TEMPLATES:
            if phrase in para:
                warnings.append(f"L{line}: explanatory colon template: {phrase}")

        for phrase in SOFT_RISK_PHRASES:
            if phrase in para:
                warnings.append(f"L{line}: context-dependent AI-like phrase; review necessity: {phrase}")

        for phrase in VAGUE_EVALUATIONS:
            if phrase in para and not sentence_has_evidence(para, phrase):
                warnings.append(f"L{line}: vague evaluation without local evidence: {phrase}")

        quote_pairs = min(para.count("“"), para.count("”"))
        if quote_pairs:
            warnings.append(f"L{line}: {quote_pairs} Chinese quote pair(s); verify they are direct labels/quotations, not emphasis")

        tmp = TECH_PAREN_RE.sub("", para)
        paren_pairs = min(tmp.count("（"), tmp.count("）"))
        if paren_pairs >= 1:
            warnings.append(f"L{line}: {paren_pairs} non-technical parenthetical pair(s); integrate explanations into sentences")

        colon_count = para.count("：")
        if colon_count >= 2:
            warnings.append(f"L{line}: {colon_count} colons in one paragraph; check list-like/template prose")

        if "——" in para:
            warnings.append(f"L{line}: rhetorical em dash detected; prefer a complete sentence unless technically required")

        semis = para.count("；")
        if semis >= 3:
            warnings.append(f"L{line}: {semis} semicolons in one paragraph; consider splitting dense judgments")

        # Anti-defensive writing: flag negative scope framing for human classification.
        if DEFENSIVE_SCOPE_RE.search(para):
            warnings.append(
                f"L{line}: defensive/negative scope framing; classify as necessary scope, real limitation, or removable disclaimer"
            )

        if para.startswith(CAVEAT_FIRST):
            warnings.append(
                f"L{line}: caveat-first paragraph; consider leading with the claim/result and moving necessary limitation later"
            )

        for sentence in split_sentences(para):
            hedges = [term for term in HEDGE_TERMS if term in sentence]
            if len(hedges) >= 2:
                warnings.append(
                    f"L{line}: hedge stacking ({'/'.join(hedges[:4])}); state the source of uncertainty instead of layering vague qualifiers"
                )
            cjk_len = chinese_char_count(sentence)
            de_count = sentence.count("的")
            if cjk_len >= 50:
                warnings.append(
                    f"L{line}: long Chinese sentence ({cjk_len} Han characters); review hidden subject/predicate and split multiple logical relations"
                )
            if cjk_len >= 35 and de_count >= 4:
                warnings.append(
                    f"L{line}: dense attributive chain ({de_count} occurrences of 的); expose the main subject-predicate-object structure"
                )

        # Work-log narrative is only suspicious when several sequential markers accumulate locally.
        worklog_hits = [item for item in WORKLOG_MARKERS if item in para]
        if len(worklog_hits) >= 3:
            warnings.append(
                f"L{line}: work-log-like sequencing ({'/'.join(worklog_hits)}); rewrite around final problem-model-evidence logic if chronology is not analytically necessary"
            )

        opener = None
        for item in TEMPLATE_OPENERS:
            if para.startswith(item):
                opener = item
                break
        if opener:
            opener_hits.append((line, opener))

    # Flag mechanical sequences like 首先/其次/再次/最后 across adjacent paragraphs.
    seq = [op for _, op in opener_hits]
    for i in range(len(opener_hits) - 2):
        trio = seq[i:i+3]
        if trio == ["首先", "其次", "再次"] or trio == ["其次", "再次", "最后"]:
            lines = ",".join(str(x[0]) for x in opener_hits[i:i+3])
            warnings.append(f"L{lines}: mechanical paragraph transition sequence: {'/'.join(trio)}")

    for msg in warnings:
        print(f"WARNING: {msg}")
    for msg in errors:
        print(f"ERROR: {msg}", file=sys.stderr)

    print(f"STYLE_LINT: {len(errors)} error(s), {len(warnings)} warning(s)")
    if errors:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
