# Tasks: Evidence-Based Investment Signals

**Input**: Design documents from `/specs/evidence-signals/`
**Prerequisites**: plan.md (done), spec.md (done), 8 PSX skills documented in `.claude/skills/` (done)

**Tests**: Manual validation checklists — formal test suite deferred per plan.md (post-profitability phase).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Execution Log

| ID | Status | Date | Notes |
|----|--------|------|-------|
| T001-T003 | ✅ Done | 2026-06-06 | Phase 1 Setup: directories, .gitkeep, macros.py created |
| T004 | ✅ Done | 2026-06-06 | psx_data.py — rate-limited DPS wrapper (market watch, historical, company info) |
| T005 | ✅ Done | 2026-06-06 | tests/manual/test_psx_data.md — 6-test checklist |
| T007 | ✅ Done | 2026-06-06 | category_benchmarks.py — KSE30 + KSE100 median P/E/EPS computed (30 + 56 stocks) |
| T008 | ✅ Done | 2026-06-06 | ratio_calculator.py — per-stock comparison with deviation % + ABOVE/BELOW verdict |
| T009 | ✅ Done | 2026-06-06 | tests/manual/test_category_benchmarks.md — 7-test checklist |
| T010 | ✅ Done | 2026-06-06 | market_filter.py — Layer 0: liquidity, spread, operator, volume spike, circuit breaker |
| T011 | ✅ Done | 2026-06-06 | evidence_signals.py — Layer 2: MA crossover, RSI(14), volume confirmation, full evidence dict |
| T012 | ✅ Done | 2026-06-06 | tests/manual/test_evidence_signals.md — 7-test checklist |
| T013 | ✅ Done | 2026-06-06 | heatmap_tradebars.py — ASCII sector heatmap (38 sectors, color-coded) + per-stock trade bars (price, MA20, MA50, volume, signal marker) |
| T014 | ✅ Done | 2026-06-06 | tests/manual/test_heatmap_tradebars.md — 5-test checklist |
| T015 | ✅ Done | 2026-06-06 | run_scan.py — full pipeline orchestrator: market data → filter → benchmarks → ratios → signals → risk → heatmap → trade bars |
| T016 | ✅ Done | 2026-06-06 | CLI flags: --mode (dry-run/journal-only), --conservative, --symbols, --output |
| T017 | ✅ Done | 2026-06-06 | Error handling: STALE DATA warning in ratio_calculator, graceful DPS failure fallback to cache |
| T018 | ⬜ Pending | — | Full pipeline test checklist — manual validation via test_psx_data + test_evidence_signals + test_heatmap_tradebars + test_stale_conservative |
| T019 | ✅ Done | 2026-06-06 | --data-age flag, stale benchmark detection in Phase 1, non-fatal warning |
| T020 | ✅ Done | 2026-06-06 | No-signal day: summary message when 0 BUY/SELL |
| T021 | ✅ Done | 2026-06-06 | Conservative mode: header shows tier, footer shows rules, 2× liquidity floors |
| T022 | ✅ Done | 2026-06-06 | data/runs/EXAMPLE.md — full scan output |
| T023 | ✅ Done | 2026-06-06 | scripts/README.md — usage guide |
| — | 🔶 Skipped | 2026-06-06 | MCP servers evaluated — not installed as script dependencies. Scripts remain self-contained.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US4)
- Include exact file paths in descriptions

## Path Conventions

- **Scripts**: `scripts/<name>.py`
- **Data**: `data/benchmarks/`, `data/runs/`
- **Config**: `scripts/macros.py`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and directory structure

- [x] T001 Create directory structure: `scripts/`, `data/benchmarks/`, `data/runs/`, `tests/manual/`
- [x] T002 [P] Create `.gitkeep` in `data/benchmarks/`, `data/runs/`, `tests/manual/`
- [x] T003 Create `scripts/macros.py` with global constants: paths, sector lists, PSX index constituents (KSE-30, KSE-100, ALLSHR), threshold values

**Checkpoint**: Project structure ready — foundational phase can begin.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data layer that ALL user stories depend on

- [ ] T004 Create `scripts/psx_data.py` — rate-limited wrapper around dps.psx.com.pk with endpoint map, 2-3s delay, pagination, error handling for 404/timeout (existing `fetch_kse100_data.py` as reference)
- [ ] T005 Create `tests/manual/test_psx_data.md` — manual validation checklist for psx_data.py (fetch ENGRO price, fetch sector list, verify rate limiting, verify error handling)
- [x] T006 (superseded by T003) macros.py constants already created in Phase 1

**Checkpoint**: Foundation ready — all user stories can now proceed in parallel.

---

## Phase 3: User Story 1 — Category Benchmarks (Priority: P1) 🎯 MVP

**Goal**: Student runs a daily scan and every stock's ratios are compared against KSE-30/KSE-100/ALLSHR medians with "ABOVE/BELOW median" verdict.

**Independent Test**: Run `python scripts/category_benchmarks.py --update` to compute medians, then run `python scripts/ratio_calculator.py --symbol ENGRO` — output must show vs_KSE30, vs_KSE100, vs_ALLSHR, vs_sector with deviation % and verdict.

### Implementation for User Story 1

- [ ] T007 [P] [US1] Create `scripts/category_benchmarks.py` — fetches KSE-30/KSE-100/ALLSHR constituent lists from dps.psx.com.pk, computes median ROE/P/E/D/E/EPS/Dividend Yield per index, stores to `data/benchmarks/kse30_ratios_latest.csv`, `data/benchmarks/kse100_ratios_latest.csv`, `data/benchmarks/allshr_ratios_latest.csv`
- [ ] T008 [P] [US1] Create `scripts/ratio_calculator.py` — computes ROE/P/E/D/E/EPS from PSX financials data, loads benchmarks from `data/benchmarks/`, outputs per-ratio comparison with deviation % and "ABOVE/BELOW median" verdict
- [ ] T009 [US1] Create `tests/manual/test_category_benchmarks.md` — manual validation: run against ENGRO, OGDC, HBL, LUCK, SYS; verify all 3 index comparisons present; verify stale data warning triggers

**Checkpoint**: US1 complete — stock ratios now include benchmark context.

---

## Phase 4: User Story 2 — Evidence-Backed Signals (Priority: P1)

**Goal**: Every BUY/SELL/HOLD signal includes the complete reasoning chain: Layer 0 values, Layer 1 ratios, Layer 2 technical values, Layer 3 risk approval.

**Independent Test**: Run `python scripts/evidence_signals.py --symbol OGDC --price-data tests/manual/sample_ogdc.csv` — output must show MA20 value, MA50 value, crossover status, RSI value, volume ratio, and plain-language reason string.

### Implementation for User Story 2

- [ ] T010 [P] [US2] Create `scripts/market_filter.py` — Layer 0 implementation: liquidity floor (volume ≥50K, value ≥PKR 5M, freefloat ≥25%, days traded ≥25/30), spread check (<2%), operator-behavior detector (price move >5% on volume <1.0× avg), volume spike investigation (>3× = caution, >5× = reject), circuit-lock filter (≥2 hits in 5 days = reject), capital-tier adjustments. Returns FilterResult dataclass with verdict/reasons.
- [ ] T011 [P] [US2] Create `scripts/evidence_signals.py` — Layer 2: MA crossover (20/50/200), RSI(14) 30/70 thresholds, volume confirmation (≥120%), stop-loss check (5%). Returns SignalResult dataclass with signal/tier/evidence dict containing: ma_crossover status with values, rsi zone with value, volume ratio, reason string, Layer 0 reference, Layer 1 reference.
- [ ] T012 [US2] Create `tests/manual/test_evidence_signals.md` — manual validation: test BUY scenario (golden cross + RSI neutral + volume confirmed), test REJECT scenario (Layer 0 fails), test HOLD scenario (missing conditions), verify evidence dict has ≥5 fields

**Checkpoint**: US2 complete — every signal is traceable back to the data that triggered it.

---

## Phase 5: User Story 3 — Visual Heatmaps & Trade Bars (Priority: P2)

**Goal**: Decision sheet includes ASCII sector heatmap (5-day color-coded performance) and per-stock trade bars (price, MA20, MA50, volume with signal markers).

**Independent Test**: Run `python scripts/heatmap_tradebars.py --sector-data tests/manual/sample_sectors.csv` — output must show ≥10 sectors with 5 daily values and green/red indicators. Run `--trade-bar OGDC --price-data tests/manual/sample_ogdc.csv` — output must show price line with MA20/MA50 and volume.

### Implementation for User Story 3

- [ ] T013 [P] [US3] Create `scripts/heatmap_tradebars.py` — ASCII sector heatmap generator (5-day sector performance, color-coded green/yellow/red), per-stock trade bar generator (price line, MA20 overlay, MA50 overlay, volume bars, BUY/SELL/HOLD marker at signal day)
- [ ] T014 [US3] Create `tests/manual/test_heatmap_tradebars.md` — manual validation: generate heatmap with 5 sectors minimum, verify color indicators, generate trade bar with price+MA+volume, verify signal marker visible

**Checkpoint**: US3 complete — visual evidence available for every signal.

---

## Phase 6: User Story 4 — Full Pipeline Orchestration (Priority: P2)

**Goal**: One command runs the entire pipeline: fetch data → filter market → compute ratios → compare vs benchmarks → generate signals → size risk → output complete decision sheet with evidence + visuals.

**Independent Test**: Run `python scripts/run_scan.py --mode dry-run` — output must be a single markdown file at `data/runs/YYYY-MM-DD-HHMM.md` containing universe stats, watchlist with benchmarks, signals with evidence, risk-approved trades, portfolio snapshot, and heatmap.

### Implementation for User Story 4

- [ ] T015 [US4] Create `scripts/run_scan.py` — orchestrator that imports all modules, chains pipeline in order (psx_data → market_filter → category_benchmarks → ratio_calculator → evidence_signals → heatmap_tradebars), enforces gate-passing at each layer, writes single decision sheet markdown to `data/runs/YYYY-MM-DD-HHMM.md`
- [ ] T016 [US4] Add `--mode dry-run` (default, no writes to journal), `--mode journal-only` (dry-run + pending journal entries), `--conservative` flag (tightens liquidity 2×, caps risk at 3%)
- [ ] T017 [US4] Add error handling: if DPS portal unreachable, use cached data with "STALE DATA" warning; if individual stock data missing, skip with "DATA UNAVAILABLE" flag
- [ ] T018 [US4] Create `tests/manual/test_full_pipeline.md` — manual validation: run pipeline end-to-end, verify decision sheet has all 6 sections, verify evidence present in signals, verify heatmap renders, verify rejected stocks include reasons

**Checkpoint**: US4 complete — one command produces the complete daily investment scan.

---

## Phase 7: Validation & Cross-Cutting Concerns

**Purpose**: Ensure reliability, consistency, and documentation

- [x] T019 [P] Validate stale data handling: `--data-age` flag added to `run_scan.py`; `get_benchmark_age_days()` checks file modification time; warning with fix command displayed in Phase 1 if benchmarks exceed threshold; non-fatal — pipeline continues with cached data
- [x] T020 [P] Validate no-signal day: Phase 6 summary shows "→ No actionable signals today. All symbols in HOLD." when zero BUY/SELL; handled gracefully
- [x] T021 [P] Validate `--conservative` vs `--standard` modes: header shows active tier; Phase 6 footer shows tier-specific rules; conservative doubles liquidity floors (100K shares / PKR 10M), caps loss at 3%; standard uses 50K/PKR 5M, 5% loss
- [x] T022 Create example decision sheet at `data/runs/EXAMPLE.md` — full scan output for 5 validation symbols with heatmap, trade bars, signals, benchmarks
- [x] T023 Create `scripts/README.md` — usage guide: install deps, run daily scan, full flag reference, pipeline architecture diagram

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational (Phase 2) completion
  - US1 (P1) + US2 (P1) + US3 (P2): Can run IN PARALLEL after Phase 2
  - US4 (P2): Depends on US1 + US2 + US3 — orchestrator needs all modules
- **Validation (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (Category Benchmarks)**: Depends on Phase 2 (psx_data.py, macros.py) — no dependency on other stories
- **US2 (Evidence Signals)**: Depends on Phase 2 (psx_data.py, macros.py) — no dependency on other stories
- **US3 (Visual Heatmaps)**: Depends on Phase 2 (psx_data.py) — no dependency on other stories
- **US4 (Pipeline Orchestration)**: Depends on US1 + US2 + US3 — integrates all modules

### Within Each User Story

- Core implementation before integration
- Module before tests
- Story complete before moving to dependent story

### Parallel Opportunities

- T004 and T005 (Phase 2) can run in parallel
- US1, US2, US3 can run in FULL PARALLEL after Phase 2
- T007 + T008 (US1), T010 + T011 (US2) can run in parallel within their stories
- T019, T020, T021 (Phase 7) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch US1 implementation files together:
Task: "Create category_benchmarks.py in scripts/category_benchmarks.py"
Task: "Create ratio_calculator.py in scripts/ratio_calculator.py"
```

## Parallel Example: Phase 2 + All User Stories

```bash
# After Phase 2 completes, launch all 3 user stories together:
Task: "US1: Category Benchmarks" -> scripts/category_benchmarks.py + scripts/ratio_calculator.py
Task: "US2: Evidence Signals"    -> scripts/market_filter.py + scripts/evidence_signals.py
Task: "US3: Heatmap & TradeBars"  -> scripts/heatmap_tradebars.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Category Benchmarks) 🎯 MVP
4. **STOP and VALIDATE**: Run against ENGRO, OGDC, HBL to verify benchmark comparison
5. Deploy/use if ready — benchmark comparison alone adds value

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Category Benchmarks) → Test → Use (MVP!)
3. Add US2 (Evidence Signals) → Test → Use (now signals are traceable)
4. Add US3 (Visual Heatmaps) → Test → Use (now signals have visual evidence)
5. Add US4 (Pipeline Orchestration) → Test → Use (one-command daily scan)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With full scope:

1. Complete Setup + Foundational together
2. After Foundation is done:
   - Developer A: US1 (category_benchmarks.py + ratio_calculator.py)
   - Developer B: US2 (market_filter.py + evidence_signals.py)
   - Developer C: US3 (heatmap_tradebars.py)
3. All 3 complete → Developer D: US4 (run_scan.py — orchestrator)
4. Team validates together in Phase 7

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Manual tests only — no automated test framework per plan.md
- Stop at any checkpoint to validate story independently
- All scripts are Python 3.11+. Dependencies: matplotlib (optional for ASCII), no external APIs beyond PSX DPS portal
