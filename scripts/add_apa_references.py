#!/usr/bin/env python3
"""
add_apa_references.py

Adds APA-format reference lists to the bottom of every wiki
synthesis/concept/mechanism/debate/method/measure page.

Cited slugs are collected from:
  1. frontmatter `papers:` list
  2. [[wikilink]] patterns in the page body that match a known source slug

Each slug is resolved to wiki/sources/<slug>.md whose frontmatter supplies
the bibliographic data (title, authors, year, journal, doi).

Usage:
    python scripts/add_apa_references.py
"""

import re
import sys
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Repository layout
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
WIKI_DIR = REPO_ROOT / "wiki"
SOURCES_DIR = WIKI_DIR / "sources"

TARGET_DIRS = [
    WIKI_DIR / "concepts",
    WIKI_DIR / "mechanisms",
    WIKI_DIR / "debates",
    WIKI_DIR / "methods",
    WIKI_DIR / "measures",
    WIKI_DIR / "synthesis",
]

# ---------------------------------------------------------------------------
# YAML frontmatter helpers
# ---------------------------------------------------------------------------
_FM_RE = re.compile(r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n", re.DOTALL)


def split_frontmatter(text: str):
    """Return (frontmatter_dict, body_text). frontmatter_dict may be empty."""
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        fm = {}
    body = text[m.end():]
    return fm, body


# ---------------------------------------------------------------------------
# Source index — load all source frontmatters once
# ---------------------------------------------------------------------------
def load_source_index() -> dict:
    """slug → frontmatter dict"""
    index: dict = {}
    for src in SOURCES_DIR.glob("*.md"):
        slug = src.stem
        try:
            text = src.read_text(encoding="utf-8")
            fm, _ = split_frontmatter(text)
            if fm:
                index[slug] = fm
        except Exception:
            pass
    return index


# ---------------------------------------------------------------------------
# Slug extraction from page body wikilinks + frontmatter papers list
# ---------------------------------------------------------------------------
# Matches [[slug]], [[path/to/slug]], [[slug|Display Text]]
_WIKILINK_RE = re.compile(r"\[\[([^\]|#]+?)(?:\|[^\]]*)?\]\]")


def collect_slugs(fm: dict, body: str, source_slugs: set) -> list:
    """
    Collect cited source slugs, deduped, preserving first-encounter order.
    """
    seen: set = set()
    slugs: list = []

    # 1. Frontmatter papers: list
    papers = fm.get("papers", [])
    if isinstance(papers, list):
        for s in papers:
            s = str(s).strip()
            if s in source_slugs and s not in seen:
                seen.add(s)
                slugs.append(s)

    # 2. [[wikilink]] patterns in body
    for m in _WIKILINK_RE.finditer(body):
        raw = m.group(1).strip()
        # Strip any path prefix, e.g. "raw_markdown/papers/slug" → "slug"
        candidate = raw.split("/")[-1]
        if candidate in source_slugs and candidate not in seen:
            seen.add(candidate)
            slugs.append(candidate)

    return slugs


# ---------------------------------------------------------------------------
# APA author formatting
# ---------------------------------------------------------------------------

def _expand_initials(rest: str) -> str:
    """
    Expand the part after the last-name comma into dot-separated initials.

    "R"       → "R."
    "RW"      → "R. W."
    "MP"      → "M. P."
    "DJ"      → "D. J."
    "J Smith" → "J. S."   (space-separated tokens → first letter each)
    ""        → ""
    """
    rest = rest.strip()
    if not rest:
        return ""
    if " " in rest:
        # Space-separated words/tokens: take first letter of each
        # e.g. "Ian D." → ["Ian", "D."] → "I. D."
        # e.g. "Sa-Pyung Sean" → ["Sa-Pyung", "Sean"] → "S. S."
        parts = [w[0].upper() for w in rest.split() if w and w[0].isalpha()]
        return " ".join(p + "." for p in parts)
    else:
        # No spaces in the rest string.
        # Heuristic: if it contains any lowercase letter it is a full given
        # name (e.g. "Suraj", "Henry") — take only the first character.
        # Otherwise it is a string of concatenated initials in uppercase
        # (e.g. "JR", "MP", "WG") — expand each character.
        has_lower = any(c.islower() for c in rest)
        if has_lower and len(rest) > 1:
            # Full given name: just take the first letter
            return rest[0].upper() + "."
        else:
            # Concatenated uppercase initials
            return " ".join(c.upper() + "." for c in rest if c.isalpha())


def _normalise_lastname(last: str) -> str:
    """
    Normalise a last-name token.
    - All-caps (e.g. "CHRISTIE") → Title Case ("Christie")
    - Mixed-case preserved ("DeAngelo", "MacKinlay", "O'Brien" stay as-is)
    - Hyphenated: normalise each part
    """
    if not last:
        return last
    alpha = [c for c in last if c.isalpha()]
    if not alpha:
        return last
    upper_ratio = sum(1 for c in alpha if c.isupper()) / len(alpha)
    if upper_ratio < 0.85:
        return last          # already mixed case
    if "-" in last:
        return "-".join(_normalise_lastname(part) for part in last.split("-"))
    return last.capitalize()


def format_one_author(raw: str) -> str:
    """
    Format a single author string to APA.
    Input: "Last, FI"  or  "Last, F"  or  "Last, First Middle"
    Output: "Last, F. I."  or  "Last, F."  etc.
    """
    raw = raw.strip()
    comma_idx = raw.find(",")
    if comma_idx == -1:
        # No comma: treat whole string as last name
        return _normalise_lastname(raw)
    last = _normalise_lastname(raw[:comma_idx].strip())
    rest = raw[comma_idx + 1:].strip()
    expanded = _expand_initials(rest)
    if expanded:
        return f"{last}, {expanded}"
    return last


def format_authors_apa(authors: list) -> str:
    """
    Format an author list to APA-style author string.

    1 author : "Last, F. F."
    2 authors: "Last, F. F., & Last, G. G."
    3–7      : "A., B., C., D., E., F., & G."
    >7       : first 6, "... & Last."
    """
    if not authors:
        return ""
    formatted = [format_one_author(str(a)) for a in authors]
    n = len(formatted)
    if n == 1:
        return formatted[0]
    if n == 2:
        return f"{formatted[0]}, & {formatted[1]}"
    if n <= 7:
        return ", ".join(formatted[:-1]) + f", & {formatted[-1]}"
    # >7 authors: first 6, ellipsis, last
    first6 = ", ".join(formatted[:6])
    return f"{first6}, ... & {formatted[-1]}"


# ---------------------------------------------------------------------------
# Title / journal normalisation  (ALL-CAPS → Title Case)
# ---------------------------------------------------------------------------

# Minor words that stay lowercase unless they are the first word
_MINOR = {
    "a", "an", "the", "and", "but", "or", "nor", "for", "so", "yet",
    "as", "at", "by", "in", "of", "on", "to", "up", "via",
    "with", "from", "into", "onto", "over", "past", "than", "that",
    "upon", "vs", "vs.",
}


def _cap_word(word: str) -> str:
    """Capitalise the first alphabetic character in a word (handles hyphens)."""
    if "-" in word:
        return "-".join(_cap_word(part) for part in word.split("-"))
    if not word:
        return word
    for i, ch in enumerate(word):
        if ch.isalpha():
            return word[:i] + ch.upper() + word[i + 1:].lower()
    return word


def smart_titlecase(text: str) -> str:
    """
    Convert a fully-uppercase string to Title Case, lowercasing minor words
    except the first and last word.  Leaves strings that are NOT all-uppercase
    unchanged (already mixed case — trust the source).
    """
    stripped = text.strip()
    if not stripped:
        return text
    # Only normalise if the text is overwhelmingly uppercase.
    alpha_chars = [c for c in stripped if c.isalpha()]
    if not alpha_chars:
        return text
    upper_ratio = sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
    if upper_ratio < 0.85:          # mostly mixed-case already — leave alone
        return text

    words = stripped.split()
    result = []
    for i, word in enumerate(words):
        base = word.lower()
        is_first = i == 0
        is_last = i == len(words) - 1
        # Always capitalise first/last; lowercase minor words otherwise
        if is_first or is_last or base not in _MINOR:
            result.append(_cap_word(word))
        else:
            result.append(base)
    return " ".join(result)


# ---------------------------------------------------------------------------
# APA citation entry builder
# ---------------------------------------------------------------------------

def build_apa_entry(fm: dict) -> str:
    """
    Build one APA journal-article reference string from source frontmatter.

    Template: Authors (Year). Title. *Journal*. https://doi.org/DOI
    - No year → "n.d."
    - No journal → entry ends after title
    - No DOI → DOI portion omitted
    """
    # Title: yaml.safe_load already strips surrounding quotes, but be safe
    title = smart_titlecase(str(fm.get("title", "")).strip().strip('"').strip("'"))
    authors_raw = fm.get("authors", [])
    year = fm.get("year")
    journal = smart_titlecase(str(fm.get("journal", "")).strip().strip('"').strip("'"))
    doi = str(fm.get("doi", "")).strip().strip('"').strip("'")

    authors_str = format_authors_apa(authors_raw)
    year_str = str(int(year)) if year else "n.d."

    # Build entry incrementally
    entry = f"{authors_str} ({year_str}). {title}."
    if journal:
        entry += f" *{journal}*."
    if doi:
        entry += f" https://doi.org/{doi}"
    return entry


# ---------------------------------------------------------------------------
# Sort key: first-author last name (lowercased), then year
# ---------------------------------------------------------------------------

def _sort_key(entry_tuple):
    slug, fm = entry_tuple
    authors = fm.get("authors", [])
    first_author = str(authors[0]) if authors else ""
    last_name = (
        first_author.split(",")[0].strip().lower()
        if "," in first_author
        else first_author.lower()
    )
    year = fm.get("year") or 0
    return (last_name, year)


# ---------------------------------------------------------------------------
# References section builder
# ---------------------------------------------------------------------------

def build_references_section(slug_fm_pairs: list) -> str:
    """
    slug_fm_pairs: [(slug, fm_dict), ...], already sorted.
    Returns the full "## References\\n\\n...\\n" block.
    """
    entries = [build_apa_entry(fm) for _, fm in slug_fm_pairs]
    body = "\n\n".join(entries)
    return f"\n## References\n\n{body}\n"


# ---------------------------------------------------------------------------
# Regex to detect an existing ## References section to the end of file
# ---------------------------------------------------------------------------
_EXISTING_REF_RE = re.compile(r"\n## References\b.*", re.DOTALL)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    source_index = load_source_index()
    source_slugs = set(source_index.keys())

    pages_updated = 0
    pages_skipped = 0
    errors: list = []
    sample_entries: list = []

    for target_dir in TARGET_DIRS:
        if not target_dir.exists():
            continue
        for page_path in sorted(target_dir.glob("*.md")):
            if page_path.name == "_index.md":
                continue
            try:
                text = page_path.read_text(encoding="utf-8")
                fm, body = split_frontmatter(text)
                slugs = collect_slugs(fm, body, source_slugs)

                # Keep only slugs present in source index
                valid = [(s, source_index[s]) for s in slugs if s in source_index]
                if not valid:
                    pages_skipped += 1
                    continue

                # Sort: alpha by first-author last name, then year
                valid_sorted = sorted(valid, key=_sort_key)

                ref_section = build_references_section(valid_sorted)

                # Replace existing ## References section or append
                existing = _EXISTING_REF_RE.search(text)
                if existing:
                    new_text = text[: existing.start()] + ref_section
                else:
                    new_text = text.rstrip("\n") + "\n" + ref_section

                page_path.write_text(new_text, encoding="utf-8")
                pages_updated += 1

                # Collect sample entries from first few pages
                if len(sample_entries) < 8:
                    for _, fm_s in valid_sorted[:3]:
                        entry = build_apa_entry(fm_s)
                        if entry not in sample_entries:
                            sample_entries.append(entry)

            except Exception as exc:
                errors.append(f"{page_path.relative_to(REPO_ROOT)}: {exc}")

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------
    print(f"Pages updated              : {pages_updated}")
    print(f"Pages skipped (no sources) : {pages_skipped}")
    print(f"Errors                     : {len(errors)}")

    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  {e}")

    if sample_entries:
        print("\nSample APA entries (first few generated):")
        for e in sample_entries:
            print(f"  {e}")


if __name__ == "__main__":
    main()
