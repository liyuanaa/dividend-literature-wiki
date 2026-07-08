#!/usr/bin/env python3
"""Rebuild the synthesis-layer _index.md files (concepts/debates/mechanisms/
methods/measures/synthesis) by listing every page in each directory with its
frontmatter title as a one-line description. Deterministic; no academic judgment.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"

LAYERS = {
    "concepts": "Cross-paper concept definitions.",
    "debates": "Competing claims and open tensions across papers.",
    "mechanisms": "Causal-pathway pages identified across papers.",
    "methods": "Research design and identification-strategy pages.",
    "measures": "How key payout variables are operationalized.",
    "synthesis": "Higher-level cumulative interpretations across the collection.",
}

TITLE_RE = re.compile(r'^title:\s*"?(.*?)"?\s*$', re.M)


def title_of(md: Path) -> str:
    text = md.read_text(encoding="utf-8")
    m = TITLE_RE.search(text.split("---", 2)[1] if text.startswith("---") else text)
    return m.group(1) if m else md.stem


def main() -> None:
    for layer, blurb in LAYERS.items():
        d = WIKI / layer
        pages = sorted(p for p in d.glob("*.md") if p.name != "_index.md")
        lines = [
            f"# {layer.capitalize()}",
            "",
            blurb,
            "",
            "## Pages",
            "",
        ]
        for p in pages:
            lines.append(f"- [[{p.stem}]] — {title_of(p)}")
        lines += [
            "",
            "## Navigation",
            "",
            "- Return to [[wiki/_index]] for the full wiki map.",
            "",
        ]
        (d / "_index.md").write_text("\n".join(lines), encoding="utf-8")
        print(f"{layer}: {len(pages)} pages")


if __name__ == "__main__":
    main()
