# Plan — Build the Dividend/Regulation Literature Wiki from 735 Abstracts

## Situation

- Source is a single 1.48 MB file, `股利文献_监管技术与股利政策_全文翻译.md`, holding **735 bilingual
  abstract records** (title, relevance score, authors, journal, year, DOI, matched keywords, Chinese
  translation, English abstract), grouped into 4 relevance tiers.
- **There are no PDFs and no full text.** The standard `/wiki-build` invariant "always read the raw
  paper, never the abstract" cannot hold. We adapt the pipeline to an abstract-only corpus.
- Decisions locked in: **English** pages; source pages generated **deterministically by script**;
  **standard 2-round** synthesis (~25–35 pages); **full stack + Chat** web UI at the end.

## Phase A — Parse + generate the corpus layer (deterministic, scripted)

1. Write `scripts/parse_abstracts.py` (chunked). It:
   - Splits the file on `^### ` entry headings; strips `？`/`❌️` relevance-flag prefixes and the
     leading number from titles, capturing `flag` + `entry_no` as metadata.
   - Extracts score, authors (list), journal, year, DOI, matched-keyword groups, Chinese + English
     abstracts.
   - Emits a canonical kebab-case slug `first-author-year-shorttitle` (per `naming-rules.md`),
     de-duplicating collisions with a numeric suffix.
   - Writes `raw_markdown/papers/<slug>.md` for all 735 (English abstract as body + a Chinese section,
     bibliographic header) so wikilinks + the RAG backend have real text to navigate.
   - Writes `wiki/sources/<slug>.md` for all 735 — schema-valid frontmatter + a source-page body
     (paper claim, abstract, matched-theme tags, `raw_markdown` link). Uses the English abstract only;
     no invented content.
   - Writes `exports/corpus-index.json` (all parsed records) for the planner + reviewers to consult
     without loading the 1.48 MB file.
2. Run it; verify counts (735/735 in both dirs), spot-check 3 pages, run
   `validate_frontmatter.py` + `check_links.py` on `wiki/sources`.
3. Regenerate `wiki/sources/_index.md` (scripted) grouping by tier/theme.

## Phase B — Synthesis layer (multi-agent, adapted `/wiki-build`, 2 rounds)

Workspace: `agent_tasks/wikipedia-rewrite_<DATE><HHMM>/`. Orchestrator spawns subagents; file handoff
only; ≤200-word status returns. **Adapted invariant:** writers/reviewers ground claims in the abstract
text in `raw_markdown/papers/<slug>.md` (the fullest text available) and must not fabricate results not
present in the abstract — pages state findings at abstract-level confidence.

- **Plan (1 planner subagent):** reads `exports/corpus-index.json`, proposes ~25–35 pages across
  concepts / mechanisms / debates / measures / methods / synthesis, clustered (6–10 clusters). Expected
  anchors given the corpus theme: substitute vs outcome model (central debate), agency costs of free
  cash flow, dividend signaling, investor/legal protection, insider-trading law, disclosure/IFRS,
  ownership structure & expropriation, board/governance, EPU & uncertainty, tax clienteles, payout
  measures, identification methods (DiD/natural experiments). Show you a summary; you may edit the plan.
- **Curate (1 curator):** one brief per page (outline, ≤10 ranked source slugs, cross-links,
  3 spot-check anchors, constraints).
- **Write (parallel cluster writers, cap 8):** Wikipedia-style English pages to `round-1/rewritten-wiki/`.
- **Review (parallel, 3 lenses):** synthesis quality / abstract-fidelity / coverage+cross-links →
  PASS/REVISE.
- **Revise (parallel):** → `round-1/round-output/`.
- **Round 2:** deepen thin pages, add deferred methods/measures, repair cross-links. → `round-2/round-output/`.
- **Finalise:** copy last round into `wiki/`; run full lint suite; update all `_index.md` + `wiki/log.md`.

## Phase C — Full stack web UI (Search / Browse / Chat)

1. `make install` (pip + `cd web && pnpm install`).
2. `python scripts/export_wiki.py --wiki-dir wiki` → `web/public/wiki-index.json`.
3. `make web-build` then `make web-start` → Search + Browse at :3000.
4. Chat: **Ollama is not installed**, so create `.env` from `.env.example` and point
   `RAG_OPENAI_BASE_URL` / `RAG_OPENAI_API_KEY` / `RAG_GEN_MODEL` at a hosted endpoint. **I'll need you
   to supply the endpoint + key** (or install Ollama). Then serve the API (:8000) + web (:3000);
   restart the web server after every build (the stale-manifest caveat).
5. Verify: a search term resolves, Browse lists pages by layer, a page renders (wikilinks/callouts/
   KaTeX), and a Chat query streams a cited answer.

## Cost / scale notes

- Phase A is ~free (pure Python). The 735 source pages are NOT written by LLMs.
- Phase B is the real spend: ~25–35 synthesis pages × (write+review+revise) × 2 rounds, parallelized in
  clusters (≤8 concurrent subagents).
- Phase C is deterministic except Chat, which is gated on you providing a generation endpoint.

## Deviations from stock `/wiki-build` (called out for approval)

1. Source pages are **scripted, not agent-written** (no PDFs; abstract-only ⇒ no academic judgment to add).
2. The "read the full raw paper" invariant is **relaxed to "read the abstract"** — it's all we have;
   pages carry abstract-level confidence and must not fabricate beyond the abstract.
3. Corpus layer feeds `raw_markdown/papers/` from abstracts so the RAG backend + wikilinks still work.
