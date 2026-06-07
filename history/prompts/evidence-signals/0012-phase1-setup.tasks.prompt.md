---
id: 0012
title: Phase 1 setup directories macros
stage: tasks
date: 2026-06-06
surface: agent
model: deepseek-v4-flash-free
feature: evidence-signals
branch: feature/psx-skills-architecture
user: AIDD
command: what should be the next? (build prompt)
labels: ["psx", "setup", "macros", "evidence-signals"]
links:
  spec: specs/evidence-signals/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - scripts/macros.py
  - data/benchmarks/.gitkeep
  - data/runs/.gitkeep
  - tests/manual/.gitkeep
tests: []
---

## Prompt

Context: user asked "what should be the next?" — I proposed executing Phase 1 from tasks.md (T001-T003: directory structure + macros.py).

## Response snapshot

Executed Phase 1 Setup:
- Created directories: scripts/, data/benchmarks/, data/runs/, tests/manual/
- Added .gitkeep files to data/benchmarks/, data/runs/, tests/manual/
- Created scripts/macros.py with:
  - Path constants (PROJECT_ROOT, BENCHMARKS_DIR, RUNS_DIR, etc.)
  - PSX DPS portal URLs and rate-limiting constants (2.5-4s delay)
  - Full sector list with constituent symbols (SECTOR_CODES)
  - Technical analysis parameters (MA periods, RSI, volume confirmation)
  - Layer 0 market filter thresholds (liquidity, spread, operator detection, circuit breaker)
  - Risk management constants (max loss 5%, conservative 3%)
  - Ratio field definitions (ROE, PE, DE, EPS, DIVIDEND_YIELD)
  - Validation symbols list (ENGRO, OGDC, HBL, LUCK, SYS)

## Outcome

- Phase 1 Setup (T001-T003) ✅ Complete
- All downstream phases unblocked
- macros.py serves as the single source of truth for constants across all 8 scripts

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Phase 2 (T004-T005: psx_data.py) or skip to Phase 3 US1 MVP (T007-T008: category_benchmarks.py + ratio_calculator.py)
