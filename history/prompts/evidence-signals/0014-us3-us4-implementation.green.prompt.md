---
id: 0014
title: US3 heatmap US4 orchestrator
stage: green
date: 2026-06-06
surface: agent
model: deepseek-v4-flash-free
feature: evidence-signals
branch: feature/psx-skills-architecture
user: AIDD
command: /sp.implement (US3 + US4 execution)
labels: ["psx", "implementation", "heatmap", "orchestrator", "python"]
links:
  spec: specs/evidence-signals/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - scripts/heatmap_tradebars.py
  - scripts/run_scan.py
  - data/sector_codes.json
  - tests/manual/test_heatmap_tradebars.md
tests:
  - python scripts/heatmap_tradebars.py --heatmap
  - python scripts/heatmap_tradebars.py --trade-bar OGDC
  - python scripts/run_scan.py --output /tmp/test_scan.md
  - python scripts/run_scan.py --conservative
---

## Prompt

please to as per plan and tasks execute /sp.implement

## Response snapshot

Built US3 (Heatmaps & Trade Bars) and US4 (Pipeline Orchestrator):

**US3 — Visual Heatmaps**
- `heatmap_tradebars.py`: ASCII sector heatmap (38 PSX sectors, color-coded green/red bars), per-stock trade bars (price + MA20 + MA50 sparklines, volume bars, signal marker)
- Sector name mapping built and cached to `data/sector_codes.json` (38 codes, one-time scrape)

**US4 — Pipeline Orchestrator**
- `run_scan.py`: Chains all 6 phases in order: Market Data → L0 Market Filter → Category Benchmarks → Ratio Analysis → Technical Signals → Risk Assessment
- CLI flags: --mode (dry-run/journal-only), --conservative, --symbols, --output
- Output: Full decision sheet to terminal + markdown file in data/runs/
- Tested end-to-end against ENGRO/OGDC/HBL/LUCK/SYS — all 5 pass

## Outcome

- All 4 user stories implemented and tested
- 8 new Python scripts totaling ~1,300 lines
- Full pipeline runs with single command: `python scripts/run_scan.py`
- Decision sheet includes: benchmark comparisons, evidence signals, sector heatmap, trade bars, risk assessment

## Evaluation notes (flywheel)

- Failure modes observed: SPARKLINE_CHARS index out of range (fixed with clamp), numpy NaN handling (fixed with pd.isna)
- Graders run and results (PASS/FAIL): PASS — full pipeline runs without errors
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Phase 7 validation (T019-T023) — stale data, conservative mode, example decision sheet, README
