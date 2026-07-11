# Wiki Log

Append-only log of all wiki operations.

## Format

```
## [YYYY-MM-DD] ingest | Author et al. (Year) — Short Title
## [YYYY-MM-DD] synthesis | Synthesis Title
## [YYYY-MM-DD] lint | Full lint pass — N issues found, N fixed
## [YYYY-MM-DD] query | Query title (saved to wiki/synthesis/...)
```

---

## [2026-07-08] wiki-build | 2 rounds, 30 synthesis pages + 735 source pages
- Workspace: agent_tasks/wikipedia-rewrite_202607081200/
- Corpus: 735 bilingual abstracts from `股利文献_监管技术与股利政策_全文翻译.md` (regulation/governance → dividend policy). No PDFs; abstract-only corpus.
- Source pages added: 735 (generated deterministically by `scripts/parse_abstracts.py` from abstracts; not agent-written)
- Raw markdown: 735 `raw_markdown/papers/<slug>.md` (English abstract + Chinese translation)
- Synthesis pages created (30): concepts (9) — agency-costs-of-free-cash-flow, catering-theory-of-dividends, dividend-clienteles, dividend-payout-policy, dividend-signaling, dividend-smoothing, financial-flexibility-and-payout, investor-protection, ownership-structure-and-expropriation; mechanisms (7) — disclosure-and-information-environment, disgorging-free-cash-flow, dividends-as-bonding-device, insider-trading-law-channel, institutional-and-blockholder-monitoring, shareholder-activism-and-payout, tax-clientele-channel; debates (4) — dividend-repurchase-substitution, dividends-signaling-vs-free-cash-flow, investor-protection-and-payout, substitute-vs-outcome-model; methods (3) — cross-country-institutional-design, dividend-announcement-event-studies, natural-experiments-and-did-regulatory-shocks; measures (2) — lintner-model-and-smoothing-measures, payout-ratio-and-propensity-to-pay; synthesis (5) — bank-payout-and-prudential-regulation, international-evidence-on-dividends, mm-irrelevance-and-payout-puzzles, political-and-policy-uncertainty-and-payout, regulation-governance-and-payout-overview.
- Round 1: 30 pages written across 10 clusters; reviewed by 5 reviewers → 28 PASS / 2 REVISE (both mechanical: a misattributed mechanism on investor-protection, a frontmatter slug gap on political-and-policy-uncertainty); both fixed.
- Round 2: deepened 6 near-floor pages (agency-costs-of-free-cash-flow, disgorging-free-cash-flow, dividends-as-bonding-device, catering-theory-of-dividends, dividend-clienteles, shareholder-activism-and-payout) from ~1650–1710 to ~1950–2000 words; all 6 re-reviewed PASS.
- Adapted invariant: writers/reviewers grounded claims in the abstract text (fullest text available); pages carry abstract-level confidence and do not fabricate beyond the abstract.
- Lint: py_compile OK; check_links — no broken links; validate_frontmatter — passed; orphans — only log.md (structural).

## [2026-07-08] lint | Full lint pass — 0 real issues (template-placeholder links excluded)

## [2026-07-11] ingest | 35 full-text PDFs ingested — 11 abstract entries supplemented with full text, 23 new source pages created, synthesis/concept layer enriched; lint clean (1 structural orphan: log.md)
