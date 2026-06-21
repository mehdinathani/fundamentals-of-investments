---
id: 0013
title: US1 and US2 implementation
stage: green
date: 2026-06-06
surface: agent
model: deepseek-v4-flash-free
feature: evidence-signals
branch: feature/psx-skills-architecture
user: AIDD
command: yes (implement US2)
labels: ["psx", "implementation", "market-filter", "evidence-signals", "python"]
links:
  spec: specs/evidence-signals/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - scripts/psx_data.py
  - scripts/market_filter.py
  - scripts/evidence_signals.py
  - tests/manual/test_psx_data.md
  - tests/manual/test_category_benchmarks.md
  - tests/manual/test_evidence_signals.md
tests:
  - tests/manual/test_psx_data.md
  - tests/manual/test_category_benchmarks.md
  - tests/manual/test_evidence_signals.md
  - python scripts/ratio_calculator.py --all
  - python scripts/market_filter.py --all
  - python scripts/evidence_signals.py --all
---

## Prompt

yes (to US2 implementation)

## Response snapshot

Built US1 and US2 completely:

**US1 — Category Benchmarks (MVP)**
- `category_benchmarks.py`: Computes KSE30 + KSE100 median P/E and EPS by scraping company pages. Handles DPS symbol name mismatches (ENGRO→ENGROH). Rate-limited (2-3s between requests). ~3 min for full KSE100.
- `ratio_calculator.py`: Loads benchmarks, fetches stock EPS from DPS, computes P/E, compares against KSE30/KSE100 medians with deviation % and ABOVE/BELOW verdict.

Example: ENGRO P/E=8.13 vs KSE30 median=8.12 (dev=+0.1%, ABOVE), vs KSE100 median=9.85 (dev=-17.5%, BELOW)

**US2 — Evidence Signals**
- `market_filter.py`: Layer 0 — liquidity (30d avg volume/value), days traded, operator detection (price move on low vol), volume spike (3× caution, 5× reject), capital tier adjustments.
- `evidence_signals.py`: Layer 2 — MA crossover (20/50/200), RSI(14), volume confirmation (≥120%). Returns SignalResult with complete evidence dict (MA values, crossover status, RSI zone, volume ratio, reasons).

All 5 validation symbols tested and passing. HBL correctly flagged SELL (below MA200).

## Outcome

- US1 (Category Benchmarks) + US2 (Evidence Signals) — Complete
- 6 new files created, all tested against ENGRO/OGDC/HBL/LUCK/SYS
- Full evidence chain implemented: every signal includes MA values, RSI, volume ratio, stop-loss
- Limitations documented: no bid/ask spread data from DPS, ALLSHR benchmark pending

## Evaluation notes (flywheel)

- Failure modes observed: DPS symbol name mismatch (ENGRO→ENGROH) — handled via prefix matching
- Graders run and results (PASS/FAIL): PASS — all 5 validation symbols processed without error
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): US3 (heatmap_tradebars.py) or US4 (run_scan.py pipeline)
