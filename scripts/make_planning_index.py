#!/usr/bin/env python3
"""Build a compact planning index from exports/corpus-index.json.

Drops the full abstracts (keeps slug/title/year/journal/score/keywords/flag) so a
planner subagent can load the whole 735-paper corpus map cheaply. Also emits a
keyword-theme frequency table to help the planner see which topics dominate.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def score_num(s: str) -> float:
    m = re.search(r"[\d.]+", s or "")
    return float(m.group(0)) if m else 0.0


def sub_keywords(keywords: str) -> list[str]:
    """Pull the parenthetical English keyword tokens out of the matched-keyword string."""
    toks: list[str] = []
    for grp in re.findall(r"\(([^)]*)\)", keywords or ""):
        toks += [t.strip() for t in grp.split(",") if t.strip()]
    return toks


def main() -> None:
    src = json.load(open(ROOT / "exports" / "corpus-index.json", encoding="utf-8"))
    papers = src["papers"]
    kw_counter: Counter[str] = Counter()
    compact = []
    for p in papers:
        toks = sub_keywords(p.get("keywords", ""))
        kw_counter.update(toks)
        compact.append(
            {
                "slug": p["slug"],
                "no": p["entry_no"],
                "title": p["title"],
                "year": p.get("year", ""),
                "journal": p.get("journal", ""),
                "score": score_num(p.get("score", "")),
                "flag": p.get("flag", ""),
                "kw": toks,
            }
        )
    compact.sort(key=lambda x: x["score"], reverse=True)
    out = {
        "count": len(compact),
        "keyword_frequency": kw_counter.most_common(),
        "papers": compact,
    }
    dst = ROOT / "exports" / "planning-index.json"
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"planning-index.json -> {dst}  ({dst.stat().st_size} bytes)")
    print("top themes:", kw_counter.most_common(25))


if __name__ == "__main__":
    main()
