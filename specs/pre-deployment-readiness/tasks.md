# Tasks: Pre-Deployment Readiness

**Input**: Design documents from `/specs/pre-deployment-readiness/`
**Prerequisites**: ADR-002 accepted (done), constitution v2.0.0 (done), 8 skills built (done)

**Tests**: No code test suite — each task is validated by constitution gate closure and independent verification.

**Organization**: Tasks grouped by user story (P1 → P2 → P3) enabling sequential or parallel execution.

## Path Conventions

- **Skills**: `.claude/skills/<skill-name>/`
- **References**: `.claude/skills/<skill-name>/references/`
- **Constitution**: `.specify/memory/constitution.md`
- **Research**: `research.md`
- **ADR**: `history/adr/`
- **PHR**: `history/prompts/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Quick prep — everything is already built, just need a new spec directory.

- [X] T001 [P] Create `specs/pre-deployment-readiness/` directory structure

**Checkpoint**: Project structure ready — task execution can begin.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Update core documents with ADR-002 resolved values. These MUST be done before any skill edits.

- [X] T002 Update `research.md` §2.2 with the committed edge sentence: *"I make money on PSX by holding fundamentally strong, liquid names through multi-quarter trends (time-horizon asymmetry), while systematically avoiding manipulated and illiquid stocks via the Layer 0 filter (behavioral discipline)."*
- [X] T003 Update `research.md` §11 (Key Principles) with Principle 6 (Falsifiable Operation): After 50 trades over ≥6 months, if Sharpe < 0.5 OR underperform KSE-100 by >5% net OR drawdown >15% from peak OR 12-month net returns underperform PKR T-bills → STOP and re-evaluate.
- [X] T004 Update `research.md` §8 Phase 5 with deferral rule from ADR-002 Decision 11: Phase 5B (SaaS) and 5C (Signal Service) deferred until ≥12 months of profitable Phase 1/2 operation.
- [X] T005 Update `research.md` §4 Layer 3: position cap changed to ≤10% per position, max 7 concurrent positions, ≥30% cash reserve.
- [X] T006 Update constitution Pre-Deployment Gates table: replace `TODO(EDGE_DEFINITION)` with edge sentence, `TODO(FALSIFICATION_NUMBERS)` with concrete numbers, `TODO(POSITION_MATH_RECONCILIATION)` with "≤10%/position, 7 max, ≥30% cash", `TODO(CGT_EXIT_POLICY)` with "soft tax-aware (ADR-002 D7)", `TODO(MACRO_OVERLAY_RULES)` with "see ADR-003", `TODO(REGIME_SHIFT_THRESHOLDS)` with "3+ stops in 5 days".
- [X] T006b Add falsification criterion as Principle VIII to constitution (replace placeholder text with exact numbers).
- [X] T007 [P] Create ADR-003 `history/adr/ADR-003-psx-macro-overlay-layer.md` documenting the Layer 1.5 macro overlay architecture (per ADR-002 Decision 8).

**Checkpoint**: Foundation ready — all core documents updated with ADR-002 resolutions. User story implementation can now begin.

---

## Phase 3: User Story 1 - Edge & Falsification (Priority: P1) 🎯 MVP

**Goal**: Edge defined and falsification numbers committed in writing.

**Independent Test**: research.md §2.2 has concrete edge sentence; constitution Pre-Deployment Gates table shows `TODO(EDGE_DEFINITION)` and `TODO(FALSIFICATION_NUMBERS)` resolved.

- [X] T008 [P] [US1] Create PHR for this decision session at `history/prompts/pre-deployment-readiness/001-adr-002-acceptance-tasks-generation.plan.prompt.md`

**Checkpoint**: US1 complete — edge and falsification are committed.

---

## Phase 4: User Story 2 - Position Math Fix (Priority: P1) 🎯 MVP

**Goal**: risk-management skill updated with correct position-sizing math.

**Independent Test**: risk-management SKILL.md enforces ≤10%/position, ≥30% cash; constitution Pre-Deployment gate shows resolved.

### Implementation for User Story 2

- [X] T009 [P] [US2] Update `.claude/skills/risk-management/SKILL.md` position sizing: change max per-position from 20% to 10%, keep max 7 positions and ≥30% cash reserve.
- [X] T010 [P] [US2] Update `.claude/skills/risk-management/references/position-sizing.md` with the reconciled formula: `position_size = min(capital * 0.10, max_loss_budget / stop_loss_pct)`.
- [X] T011 [P] [US2] Update `.claude/skills/risk-management/references/portfolio-limits.md`: max 7 positions × 10% = 70% invested, 30% cash floor.

**Checkpoint**: US2 complete — position math conflict resolved.

---

## Phase 5: User Story 3 - Backtest Gate (Priority: P1) 🎯 MVP

**Goal**: Run psx-backtester on current rules with full PSX frictions; accept/reject the strategy.

**Independent Test**: Backtest report produced with Sharpe, drawdown, win/loss; gate decision recorded in research.md.

### Implementation for User Story 3

- [X] T012 [P] [US3] Review `.claude/skills/psx-backtester/SKILL.md` to confirm backtest configuration: 2018-2024 PSX data, full frictions (commission, CGT, slippage, T+2).
- [X] T013 [P] [US3] Review `.claude/skills/psx-backtester/references/psx-frictions.md` to confirm all cost parameters match real PSX rates.
- [X] T014 [P] [US3] Review `.claude/skills/psx-backtester/references/psx-calendar.md` for correct holiday/ex-dividend handling.
- [ ] T015 [US3] Run backtest via psx-backtester skill on 2018-2024 PSX data.
- [ ] T016 [US3] Record backtest outcome: Sharpe, max drawdown, win/loss ratio, expectancy, total trades.
- [ ] T017 [US3] If Sharpe ≥ 1.0, max drawdown ≤ 15%, win/loss ≥ 2.0, expectancy > 0, ≥ 30 trades in ≥6 month OOS: mark gate PASSED in constitution. Otherwise: document required rule iterations.

**Checkpoint**: US3 complete — strategy validated or iteration required.

---

## Phase 6: User Story 4 - Macro Overlay Layer 1.5 (Priority: P2)

**Goal**: Macro overlay rules defined and documented in psx-market-filter skill.

**Independent Test**: ADR-003 exists at `history/adr/ADR-003-psx-macro-overlay-layer.md`; market-filter references contain risk-on/neutral/risk-off thresholds; constitution `TODO(MACRO_OVERLAY_RULES)` resolved.

### Implementation for User Story 4

- [X] T018 [P] [US4] Define macro states in `.claude/skills/psx-market-filter/references/macro-states.md`:
  - Risk-on: SBP cutting rates, USD/PKR stable or improving, IMF program on track, KSE-100 P/E < 10-yr median.
  - Neutral: mixed signals.
  - Risk-off: SBP hiking, USD/PKR sharply weakening, IMF at risk, KSE-100 P/E > 10-yr median + 1SD.
- [X] T019 [P] [US4] Update `.claude/skills/psx-market-filter/SKILL.md` Layer 1.5 section: when macro = risk-off, universe tightens to defensives (utilities, cash-rich firms) or 100% cash.
- [X] T020 [P] [US4] Create ADR-003 at `history/adr/ADR-003-psx-macro-overlay-layer.md` with the Layer 1.5 architecture, data sources (SBP, USD/PKR, KSE-100 valuation), and macro state definitions.

**Checkpoint**: US4 complete — macro overlay operational.

---

## Phase 7: User Story 5 - Tax-Aware Exit Logic (Priority: P2)

**Goal**: Soft CGT-aware exit deferral in trade-rules-engine.

**Independent Test**: trade-rules-engine exit rules include CGT deferral; constitution `TODO(CGT_EXIT_POLICY)` resolved to "soft tax-aware (ADR-002 D7)".

### Implementation for User Story 5

- [X] T021 [P] [US5] Update `.claude/skills/trade-rules-engine/references/rsi-rules.md` exit section: add CGT deferral logic — if profit-taking exit fires within 30 days of 6-month hold, and technicals are neutral (RSI 30-70, no MA sell), defer to cross the 6-month CGT bracket.
- [X] T022 [P] [US5] Add carveout to `.claude/skills/trade-rules-engine/SKILL.md` exit rules: CGT deferral MUST NOT override (a) stop-loss exits, (b) trend-reversal exits (MA cross below), (c) RSI > 70 sell signals.
- [X] T023 [P] [US5] Add CGT bracket reference table to `.claude/skills/trade-rules-engine/references/signal-examples.md`: 0-6mo=15%, 6-12mo=12.5%, 12-24mo=10%, 24mo+=0%.

**Checkpoint**: US5 complete — CGT-aware exits operational.

---

## Phase 8: User Story 6 - Regime-Shift & No-Trade Discipline (Priority: P3)

**Goal**: Regime-shift detector and entry cap in psx-orchestrator.

**Independent Test**: orchestrator enforces max 2 entries/week and halts on 3+ stops in 5 days; constitution `TODO(REGIME_SHIFT_THRESHOLDS)` resolved.

### Implementation for User Story 6

- [X] T024 [P] [US6] Update `.claude/skills/psx-orchestrator/SKILL.md` pipeline: add regime-shift pre-check — before accepting new entries, check if 3+ open positions hit stops in last 5 trading days. If yes → halt, trigger macro reassessment.
- [X] T025 [P] [US6] Add entry cap to `.claude/skills/psx-orchestrator/SKILL.md`: max 2 entries per calendar week. Third+ signals are queued to next week.
- [X] T026 [P] [US6] Create `.claude/skills/psx-orchestrator/references/regime-shift-protocol.md` with halt trigger, reassessment template, and resume criteria.

**Checkpoint**: US6 complete — regime-shift protection and entry discipline enforced.

---

## Phase 9: User Story 7 - Operational Features (Priority: P3)

**Goal**: Earnings blackout, sector rotation, tax-loss harvesting, phase deferral.

**Independent Test**: Each rule documented in the respective skill; all documented below complete.

### Implementation for User Story 7

- [X] T027 [P] [US7] Add hard earnings blackout to `.claude/skills/risk-management/SKILL.md`: flat into earnings unless thesis explicitly requires holding (documented in journal).
- [X] T028 [P] [US7] Add earnings blackout details to `.claude/skills/risk-management/references/prohibited-behaviors.md`.
- [X] T029 [P] [US7] Strengthen sector momentum filter in `.claude/skills/trade-rules-engine/SKILL.md` entry rules: bottom-quartile sectors excluded regardless of stock fundamentals.
- [X] T030 [P] [US7] Add sector momentum metric reference to `.claude/skills/trade-rules-engine/references/sector-momentum.md`.
- [X] T031 [P] [US7] Add Q4 tax-loss harvesting routine to `.claude/skills/psx-trade-journal/references/review-templates.md`.
- [X] T032 [P] [US7] Ensure `.claude/skills/psx-trade-journal/SKILL.md` references the annual Q4 routine.

**Checkpoint**: All 7 user stories complete.

---

## Phase 10: Polish & Validation

**Purpose**: Verify all gates are closed and documents are consistent.

- [ ] T033 Validate constitution Pre-Deployment Gates table: all 7 rows resolved (no `TODO(...)` remaining).
- [ ] T034 Validate ADR-003 created and consistent with ADR-002 Decision 8.
- [ ] T035 Validate all skill edits preserve the <500 line SKILL.md guideline.
- [ ] T036 [P] Final cross-reference: ensure research.md §15 TODOs match resolved states.
- [ ] T037 [P] Create PHR for this pre-deployment readiness phase at `history/prompts/pre-deployment-readiness/`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories (core documents must be updated first)
- **US1 (Phase 3)**: Depends on Foundational — records the session PHR
- **US2 (Phase 4)**: Depends on Foundational — position math fix
- **US3 (Phase 5)**: Depends on Phase 2 — backtest validates all rules
- **US4-7 (Phases 6-9)**: All depend on Foundational (Phase 2)
  - Can run in parallel or sequentially
- **Polish (Phase 10)**: Depends on all user stories

### Parallel Opportunities

- T002-T007 in Phase 2 can run partially in parallel
- T008-T010 (US2) can run in parallel
- T012-T014 (US3 research) can run in parallel
- T018-T020 (US4) can run in parallel
- T021-T023 (US5) can run in parallel
- T024-T026 (US6) can run in parallel
- T027-T032 (US7) can run in parallel
- All of US4-US7 can run in parallel with each other

### User Story Dependencies

- **US1 (P1)**: No skill dependencies — pure documentation
- **US2 (P1)**: Independent — only modifies risk-management skill
- **US3 (P1)**: Independent — runs backtester skill
- **US4 (P2)**: Independent — only modifies market-filter skill + ADR
- **US5 (P2)**: Independent — only modifies trade-rules-engine
- **US6 (P3)**: Independent — only modifies orchestrator
- **US7 (P3)**: Independent — touches risk-management, trade-rules-engine, trade-journal

## Implementation Strategy

### MVP First (User Stories 1-3)

1. Complete Phase 1-2 (Setup + Foundational)
2. Complete US1 (Edge & Falsification documentation)
3. Complete US2 (Position math fix)
4. Complete US3 (Backtest) — this is the critical gate
5. If backtest passes → proceed to US4-7. If fails → iterate strategy rules and repeat US3.

### Incremental Delivery

1. Foundation updates (Phase 2) → all core docs aligned
2. P1 stories (US1-3) → blocking gates closed, backtest result known
3. P2 stories (US4-5) → macro overlay + tax-aware exits
4. P3 stories (US6-7) → discipline enforcement + operational polish

### Parallel Team Strategy

- Person A: US2 (position math) + US4 (macro) + US6 (regime)
- Person B: US5 (tax) + US7 (ops)
- Person C: US3 (backtest) — can run independently
- US1 is single-person doc work

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Each user story is independently completable and testable
- All skill edits are documentation-only (SKILL.md + references/ updates)
- Backtest US3 is the only execution task (runs actual backtester)
- Stop after US3 to evaluate: if strategy fails backtest, do NOT proceed to US4-7
