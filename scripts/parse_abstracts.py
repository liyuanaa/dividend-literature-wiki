#!/usr/bin/env python3
"""Parse the bilingual dividend-literature abstract file into the wiki corpus layer.

Input: a single markdown file where each paper is a `### N. Title` entry followed by
score / authors / journal-year-doi / matched-keywords / Chinese translation / English
abstract fields.

Outputs (deterministic, no LLM, English abstract is the only substantive text used):
    raw_markdown/papers/<slug>.md    one per paper  (abstract as navigable text)
    wiki/sources/<slug>.md           one per paper  (schema-valid source page)
    exports/corpus-index.json        all parsed records for the planner/reviewers

Usage:
    python scripts/parse_abstracts.py \
        --input "股利文献_监管技术与股利政策_全文翻译.md" \
        [--limit N]   # parse only first N entries (debugging)
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ENTRY_RE = re.compile(r"^### (.+?)\s*$", re.M)
# strip relevance-flag prefixes (？ ❌️) and the leading "N." from a heading
TITLE_CLEAN_RE = re.compile(r"^\s*([？?]|❌️)?\s*(\d+)\.\s*(.*)$")

FIELD_RES = {
    "score": re.compile(r"\*\*相关性得分\*\*[:：]\s*(.+?)\s*$", re.M),
    "authors": re.compile(r"\*\*作者\*\*[:：]\s*(.+?)\s*$", re.M),
    "journal": re.compile(r"\*\*期刊\*\*[:：]\s*(.+?)\s*(?:　|\||$)"),
    "year": re.compile(r"\*\*年份\*\*[:：]\s*(\d{4})"),
    "doi": re.compile(r"\*\*DOI\*\*[:：]\s*(\S+)"),
    "keywords": re.compile(r"\*\*匹配关键词\*\*[:：]\s*(.+?)\s*$", re.M),
}

CN_RE = re.compile(r"【中文翻译】\**\s*\n+(.*?)(?=\n+\**【英文摘要原文】|\Z)", re.S)
EN_RE = re.compile(r"【英文摘要原文】\**\s*\n+(.*?)(?=\n+---|\Z)", re.S)


def clean_title(title: str) -> str:
    """Strip footnote markers and broken HTML-entity fragments from a title."""
    t = title
    # broken numeric entities left over from conversion, e.g. "x2729;" / "&#x2729;"
    t = re.sub(r"&?#?x?[0-9a-fA-F]{3,5};", "", t)
    t = t.replace("&amp;", "&")
    # trailing footnote asterisk(s) and stray whitespace
    t = re.sub(r"\s*\*+\s*$", "", t)
    return t.strip()


def slugify(title: str, first_author_last: str, year: str) -> str:
    """author-year-shorttitle kebab-case, per wiki/schema/naming-rules.md."""
    author = re.sub(r"[^a-z0-9]+", "", first_author_last.lower()) or "anon"
    yr = year or "nd"
    words = re.findall(r"[a-z0-9]+", title.lower())
    short = "-".join(words[:8]) if words else "untitled"
    return f"{author}-{yr}-{short}"[:90].strip("-")


def first_author_last(authors_raw: str) -> str:
    """authors like 'Hail, L, Tahoun, A' -> 'Hail'."""
    if not authors_raw:
        return "anon"
    first = authors_raw.split(",")[0].strip()
    return re.sub(r"[^A-Za-z]", "", first) or "anon"


def pair_authors(authors_raw: str) -> list[str]:
    """'Hail, L, Tahoun, A, Wang, C' -> ['Hail, L', 'Tahoun, A', 'Wang, C'].

    The source lists authors as 'Last, Initial(s)' pairs separated by commas,
    so tokens must be recombined two at a time. A trailing unpaired token
    (a lone surname with no initials) is kept as-is.
    """
    if not authors_raw:
        return []
    tokens = [t.strip() for t in authors_raw.split(",") if t.strip()]
    authors: list[str] = []
    i = 0
    while i < len(tokens):
        surname = tokens[i]
        # An initials token is short and mostly uppercase letters/dots.
        if i + 1 < len(tokens) and re.fullmatch(r"[A-Za-z][A-Za-z.\- ]{0,6}", tokens[i + 1]):
            authors.append(f"{surname}, {tokens[i + 1]}")
            i += 2
        else:
            authors.append(surname)
            i += 1
    return authors


def parse_entries(text: str, limit: int | None = None) -> list[dict]:
    matches = list(ENTRY_RE.finditer(text))
    records: list[dict] = []
    seen_slugs: dict[str, int] = {}
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start:end]
        heading = m.group(1)

        tc = TITLE_CLEAN_RE.match(heading)
        if tc:
            flag_raw, entry_no, title = tc.group(1), tc.group(2), tc.group(3).strip()
            flag = {"？": "uncertain", "?": "uncertain", "❌️": "excluded"}.get(flag_raw or "", "")
        else:
            flag, entry_no, title = "", str(i + 1), heading.strip()
        title = clean_title(title)
        title = clean_title(title)

        rec: dict = {"entry_no": int(entry_no), "flag": flag, "title": title}
        for key, rx in FIELD_RES.items():
            mm = rx.search(block)
            rec[key] = mm.group(1).strip() if mm else ""

        rec["authors_raw"] = rec.get("authors", "")
        rec["authors_list"] = pair_authors(rec["authors_raw"])
        cn = CN_RE.search(block)
        en = EN_RE.search(block)
        rec["cn_abstract"] = (cn.group(1).strip() if cn else "")
        rec["en_abstract"] = (en.group(1).strip() if en else "")

        fa = first_author_last(rec["authors_raw"])
        base = slugify(title, fa, rec.get("year", ""))
        if base in seen_slugs:
            seen_slugs[base] += 1
            slug = f"{base}-{seen_slugs[base]}"
        else:
            seen_slugs[base] = 1
            slug = base
        rec["slug"] = slug
        records.append(rec)
        if limit and len(records) >= limit:
            break
    return records


def yaml_list(items: list[str]) -> str:
    if not items:
        return "[]"
    return "[" + ", ".join('"' + it.replace('"', "'") + '"' for it in items) + "]"


def theme_tags(keywords: str) -> list[str]:
    """Coarse tags from the matched-keyword groups, for browse/filter."""
    tags = []
    if "监管" in keywords or "治理" in keywords:
        tags.append("governance-regulation")
    if "股利" in keywords:
        tags.append("dividend-policy")
    if "影响机制" in keywords:
        tags.append("mechanism")
    return tags or ["dividend-policy"]


def write_raw_markdown(rec: dict) -> str:
    authors = ", ".join(rec["authors_list"]) or "n/a"
    lines = [
        f"# {rec['title']}",
        "",
        f"- **Authors:** {authors}",
        f"- **Journal:** {rec.get('journal') or 'n/a'}",
        f"- **Year:** {rec.get('year') or 'n/a'}",
        f"- **DOI:** {rec.get('doi') or 'n/a'}",
        f"- **Relevance score:** {rec.get('score') or 'n/a'}",
        f"- **Matched keywords:** {rec.get('keywords') or 'n/a'}",
        "",
        "> Source: abstract-only corpus. No full text available; the text below is the",
        "> published abstract. Do not attribute claims beyond what the abstract states.",
        "",
        "## Abstract (English)",
        "",
        rec["en_abstract"] or "_(no English abstract)_",
        "",
        "## 摘要（中文翻译）",
        "",
        rec["cn_abstract"] or "_(无中文翻译)_",
        "",
    ]
    return "\n".join(lines)


def write_source_page(rec: dict) -> str:
    slug = rec["slug"]
    tags = theme_tags(rec.get("keywords", ""))
    claim = rec["en_abstract"].split(". ")[0].strip()
    if claim and not claim.endswith("."):
        claim += "."
    claim = claim or rec["title"]
    fm = [
        "---",
        f'title: "{rec["title"].replace(chr(34), chr(39))}"',
        f"authors: {yaml_list(rec['authors_list'])}",
        f"year: {rec.get('year') or 'null'}",
        f"slug: {slug}",
        f"tags: {yaml_list(tags)}",
        f'journal: "{rec.get("journal", "")}"',
        f'doi: "{rec.get("doi", "")}"',
        f'raw_markdown: "[[raw_markdown/papers/{slug}]]"',
        "status: canonical",
        "---",
        "",
        f"# {rec['title']} ({rec.get('year') or 'n.d.'})",
        "",
        f"> **Paper claim** — {claim}",
        "",
        f"Raw markdown: [[raw_markdown/papers/{slug}]]",
        "",
        "## Bibliographic Record",
        "",
        f"- **Authors:** {', '.join(rec['authors_list']) or 'n/a'}",
        f"- **Journal:** {rec.get('journal') or 'n/a'}",
        f"- **Year:** {rec.get('year') or 'n/a'}",
        f"- **DOI:** {rec.get('doi') or 'n/a'}",
        f"- **Relevance score:** {rec.get('score') or 'n/a'}",
        f"- **Matched themes:** {rec.get('keywords') or 'n/a'}",
        "",
        "## Abstract",
        "",
        rec["en_abstract"] or "_(no English abstract available)_",
        "",
        "## 摘要（中文）",
        "",
        rec["cn_abstract"] or "_(无中文翻译)_",
        "",
        "## Notes",
        "",
        "Abstract-only record — no full text is available for this paper in the corpus. "
        "Synthesis pages citing this source draw on the abstract above.",
        "",
    ]
    return "\n".join(fm)


def score_num(score: str) -> float:
    m = re.search(r"[\d.]+", score or "")
    return float(m.group(0)) if m else 0.0


def write_sources_index(records: list[dict]) -> str:
    """Grouped, wikilinked index of all source pages (keeps them non-orphan)."""
    bands = [
        ("Highly relevant (score ≥ 12)", lambda s: s >= 12),
        ("Key relevance (score 8–12)", lambda s: 8 <= s < 12),
        ("General relevance (score 5–8)", lambda s: 5 <= s < 8),
        ("Reference (score 3–5)", lambda s: s < 5),
    ]
    out = [
        "# Sources",
        "",
        f"One canonical page per paper — {len(records)} abstract-only records, "
        "grouped by relevance score. Paper-specific navigation aids; synthesis "
        "pages are the deliverable.",
        "",
    ]
    for label, pred in bands:
        group = sorted(
            (r for r in records if pred(score_num(r.get("score", "")))),
            key=lambda r: (-score_num(r.get("score", "")), r["entry_no"]),
        )
        if not group:
            continue
        out.append(f"## {label} ({len(group)})")
        out.append("")
        for r in group:
            yr = r.get("year") or "n.d."
            jn = r.get("journal") or ""
            flag = f" _({r['flag']})_" if r.get("flag") else ""
            out.append(f"- [[{r['slug']}]] — {r['title']} ({yr}, {jn}){flag}")
        out.append("")
    out += ["## Navigation", "", "- Return to [[wiki/_index]] for the full wiki map.", ""]
    return "\n".join(out)


def write_sources_index(records: list[dict]) -> str:
    """Group all source slugs by relevance tier so every page is reachable."""
    def score_val(r: dict) -> float:
        m = re.search(r"[\d.]+", r.get("score", "") or "")
        return float(m.group()) if m else 0.0

    tiers = [
        ("Highly relevant (score > 12)", lambda s: s > 12),
        ("Key relevance (score 8–12)", lambda s: 8 <= s <= 12),
        ("General relevance (score 5–8)", lambda s: 5 <= s < 8),
        ("Reference (score 3–5)", lambda s: s < 5),
    ]
    lines = [
        "# Sources",
        "",
        "One canonical page per paper. Abstract-only bibliographic records "
        f"({len(records)} papers). Grouped by corpus relevance tier.",
        "",
    ]
    for label, pred in tiers:
        group = [r for r in records if pred(score_val(r))]
        if not group:
            continue
        lines.append(f"## {label} ({len(group)})")
        lines.append("")
        for r in sorted(group, key=lambda r: (-score_val(r), r["slug"])):
            flag = f" ⚑{r['flag']}" if r.get("flag") else ""
            lines.append(f"- [[{r['slug']}]] — {r['title']} ({r.get('year') or 'n.d.'}){flag}")
        lines.append("")
    lines += ["## Navigation", "", "- Return to [[wiki/_index]] for the full wiki map.", ""]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    text = Path(args.input).read_text(encoding="utf-8")
    records = parse_entries(text, args.limit)
    print(f"Parsed {len(records)} entries")

    raw_dir = ROOT / "raw_markdown" / "papers"
    src_dir = ROOT / "wiki" / "sources"
    raw_dir.mkdir(parents=True, exist_ok=True)
    src_dir.mkdir(parents=True, exist_ok=True)

    missing_en = 0
    for rec in records:
        (raw_dir / f"{rec['slug']}.md").write_text(write_raw_markdown(rec), encoding="utf-8")
        (src_dir / f"{rec['slug']}.md").write_text(write_source_page(rec), encoding="utf-8")
        if not rec["en_abstract"]:
            missing_en += 1

    (src_dir / "_index.md").write_text(write_sources_index(records), encoding="utf-8")

    idx = {
        "count": len(records),
        "missing_en_abstract": missing_en,
        "papers": [
            {
                "slug": r["slug"],
                "entry_no": r["entry_no"],
                "flag": r["flag"],
                "title": r["title"],
                "authors": r["authors_list"],
                "journal": r.get("journal", ""),
                "year": r.get("year", ""),
                "doi": r.get("doi", ""),
                "score": r.get("score", ""),
                "keywords": r.get("keywords", ""),
                "en_abstract": r["en_abstract"],
            }
            for r in records
        ],
    }
    exports = ROOT / "exports"
    exports.mkdir(exist_ok=True)
    (exports / "corpus-index.json").write_text(
        json.dumps(idx, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    (src_dir / "_index.md").write_text(write_sources_index(records), encoding="utf-8")
    print(f"Wrote {len(records)} raw_markdown + {len(records)} source pages")
    print(f"Missing English abstract: {missing_en}")
    print(f"corpus-index.json -> exports/corpus-index.json")


if __name__ == "__main__":
    main()

