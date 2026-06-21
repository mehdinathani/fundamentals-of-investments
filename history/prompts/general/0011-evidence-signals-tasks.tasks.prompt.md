---
id: 0011
title: Evidence signals task generation
stage: tasks
date: 2026-06-06
surface: agent
model: deepseek-v4-flash-free
feature: evidence-signals
branch: feature/psx-skills-architecture
user: AIDD
command: /sp.tasks please create tasks accordingly to latest plan
labels: ["psx", "tasks", "evidence-signals", "python", "pipeline"]
links:
  spec: specs/evidence-signals/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/evidence-signals/tasks.md
tests:
  - tests/manual/test_psx_data.md
  - tests/manual/test_category_benchmarks.md
  - tests/manual/test_evidence_signals.md
  - tests/manual/test_heatmap_tradebars.md
  - tests/manual/test_full_pipeline.md
---

## Prompt

/sp.tasks please create tasks accordingly to latest plan

## Response snapshot

Generated tasks.md at specs/evidence-signals/tasks.md with 23 tasks across 7 phases:

- Phase 1: Setup (3 tasks) — directories, gitkeep, macros.py
- Phase 2: Foundational (3 tasks) — psx_data.py, macros.py, manual tests
- Phase 3: US1 — Category Benchmarks P1 🎯MVP (3 tasks) — category_benchmarks.py, ratio_calculator.py, manual tests
- Phase 4: US2 — Evidence Signals P1 (3 tasks) — market_filter.py, evidence_signals.py, manual tests
- Phase 5: US3 — Visual Heatmaps P2 (2 tasks) — heatmap_tradebars.py, manual tests
- Phase 6: US4 — Pipeline Orchestration P2 (4 tasks) — run_scan.py, CLI flags, error handling, manual tests
- Phase 7: Validation (5 tasks) — stale data, no-signal, conservative mode, example, README

Parallel execution: US1+US2+US3 can run simultaneously after Phase 2. US4 depends on all three.

## Outcome

- ✅ Impact: 23 tasks generated with clear dependencies, parallel opportunities, and manual test criteria
- 🧪 Tests: 5 manual validation checklists (one per user story + foundational)
- 📁 Files: specs/evidence-signals/tasks.md
- 🔁 Next prompts: Begin Phase 1 (Setup) or skip to Phase 3 (US1 MVP)
- 🧠 Reflection: US1 (Category Benchmarks) is the MVP — delivers immediate value by adding benchmark context to ratios. Task structure allows parallel US1+US2+US3 after foundational phase.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): T001-T003 (Setup) or skip to T007-T008 (US1 MVP)
