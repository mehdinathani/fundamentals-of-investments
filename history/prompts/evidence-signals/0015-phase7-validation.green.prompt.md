---
id: 0015
title: Phase 7 validation documentation
stage: green
date: 2026-06-06
surface: agent
model: deepseek-v4-flash-free
feature: evidence-signals
branch: feature/psx-skills-architecture
user: AIDD
command: continue (implement remaining Phase 7 tasks)
labels: ["psx", "validation", "documentation", "phase-7"]
links:
  spec: specs/evidence-signals/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - scripts/run_scan.py
  - scripts/heatmap_tradebars.py
  - tests/manual/test_stale_conservative.md
  - data/runs/EXAMPLE.md
  - scripts/README.md
templates:
  - tests/manual/test_stale_conservative.md
tests:
  - python scripts/run_scan.py --conservative (header + footer tiers correct)
  - python scripts/run_scan.py --data-age 1 (stale warning logic)
  - python scripts/run_scan.py --symbols ENGRO OGDC LUCK SYS (no-signal day)
---

## Prompt

record phr

## Response snapshot

Completed all Phase 7 tasks (T019-T023):

**Code changes:**
- `run_scan.py`: Added `--data-age` CLI flag, stale benchmark detection via `get_benchmark_age_days()`, no-signal day summary ("No actionable signals today"), conservative tier display in header + footer
- `heatmap_tradebars.py`: `print_decision_sheet_header()` now accepts `capital_tier` parameter — header dynamically shows "standard" or "conservative"

**Test documentation:**
- `tests/manual/test_stale_conservative.md`: 4-test checklist covering stale data warning, custom threshold, no-signal day, conservative vs standard

**Artifacts:**
- `data/runs/EXAMPLE.md`: Full scan output (5 symbols, 6 phases, heatmap, trade bars) — reference decision sheet
- `scripts/README.md`: Usage guide with quick start, pipeline architecture diagram, full flag reference, data flow

## Outcome

All 23 tasks across 7 phases now complete. The full pipeline runs end-to-end with a single command. Key findings:
- KSE30 benchmark: P/E=8.12, EPS=27.57
- KSE100 benchmark: P/E=9.85, EPS=20.64
- ALLSHR: unavailable (no API list)
- HBL correctly flagged SELL (price below MA200)

## Evaluation notes (flywheel)

- Failure mode observed: header showed "standard" even with --conservative (fixed by passing `capital_tier` to `print_decision_sheet_header()`)
- Graders run and results (PASS/FAIL): PASS — all Phase 7 scenarios validated
- Next experiment: automated test suite, backtest gate, broker connectivity
