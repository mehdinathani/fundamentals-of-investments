# Feature Specification: Pre-Deployment Readiness

**Feature Branch**: `pre-deployment-readiness`
**Created**: 2026-05-30
**Status**: Updated (2026-05-31) — US4 analysis complete, pending skill implementation
**Input**: ADR-002 accepted decisions, constitution v2.0.0 TODO gates

## User Stories

### User Story 1 - Edge & Falsification Definition (Priority: P1) 🎯 MVP

Commit the edge sentence and falsification kill-switch into research.md and constitution, closing `TODO(EDGE_DEFINITION)` and `TODO(FALSIFICATION_NUMBERS)`.

**Why this priority**: These are blocking gates — no live capital until closed.

**Independent Test**: research.md §2.2 contains a concrete edge sentence; constitution Pre-Deployment Gates table shows both TODOs as resolved with values.

**Acceptance Scenarios**:
1. **Given** ADR-002 Decision 1 (edge = B+A), **When** research.md §2.2 and constitution are updated, **Then** `TODO(EDGE_DEFINITION)` is replaced with the edge sentence.
2. **Given** ADR-002 Decision 5 (falsification = D), **When** falsification numbers are set and written into research.md §11, **Then** `TODO(FALSIFICATION_NUMBERS)` is replaced with exact numeric thresholds.

---

### User Story 2 - Position Math Fix (Priority: P1) 🎯 MVP

Resolve the 7 positions × 20% vs 30% cash conflict per ADR-002 Decision 4 (Option B).

**Why this priority**: Non-negotiable before any live trade — current math is broken.

**Independent Test**: risk-management SKILL.md states max 10%/position; constitution Pre-Deployment Gates shows `TODO(POSITION_MATH_RECONCILIATION)` resolved.

**Acceptance Scenarios**:
1. **Given** the position-math conflict in constitution §III, **When** ADR-002 Decision 4 (B) is applied, **Then** risk-management skill enforces ≤10% per position and ≥30% cash.
2. **Given** the new cap, **When** 7 positions are at 10% each, **Then** total exposure = 70%, leaving ≥30% cash.

---

### User Story 3 - Backtest Gate (Priority: P1) 🎯 MVP

Run the psx-backtester on current rules against 2018-2024 PSX data with full frictions (commission, CGT, slippage, T+2).

**Why this priority**: If Sharpe <1.0, strategy must iterate — blocking all other decisions.

**Independent Test**: backtest produces a report with Sharpe, drawdown, win/loss, expectancy. Accept/reject decision recorded.

**Acceptance Scenarios**:
1. **Given** the backtester skill exists, **When** run against 2018-2024 PSX data with full frictions, **Then** results show net-of-costs Sharpe ratio.
2. **Given** backtest results, **When** Sharpe ≥1.0, max drawdown ≤15%, win/loss ≥2.0, **Then** gate passes and Phase 1 can proceed.
3. **Given** backtest results, **When** Sharpe <1.0, **Then** rules must be iterated and backtest repeated before deployment.

---

### User Story 4 - Macro Overlay Layer 1.5 (Priority: P2) ✅ COMPLETE

**Status:** ✅ Complete (2026-05-31)
- ADR-003 created ✅
- Macro states defined in `.claude/skills/psx-market-filter/references/macro-states.md` ✅
- Empirical analysis run via `scripts/macro_regime_analysis.py` ✅
- Results documented in `research.md §17` ✅

**Key Findings:**
- Pakistan was in RISK_OFF for 54.6% of 2018-2024
- Strategy returns +33.7% ann. in RISK_ON vs +11.5% in RISK_OFF — strongly regime-dependent
- Macro gate blocks 107 bad entries in IS, improves CAGR from -1.2% to +2.7%
- OOS (2024) was 100% RISK_ON — explains the 26% OOS CAGR

**Still blocking deployment:** Sharpe (0.45 vs 1.0 threshold) and Max DD (-26.9% vs -15%). Strategy is conditionally viable but needs iteration or threshold adjustment for PSX-specific context.

---

### User Story 5 - Tax-Aware Exit Logic (Priority: P2)

Add soft CGT-aware exit deferral to trade-rules-engine per ADR-002 Decision 7 (Option B).

**Why this priority**: CGT brackets (15% <6mo, 12.5% 6-12mo, 10% 12-24mo) materially impact net returns.

**Independent Test**: trade-rules-engine exit rules include CGT deferral logic; `TODO(CGT_EXIT_POLICY)` in constitution is resolved.

**Acceptance Scenarios**:
1. **Given** a profit-taking exit signal fires within 30 days of the 6-month CGT boundary, **When** technicals remain neutral, **Then** exit is deferred to cross the lower bracket.
2. **Given** a stop-loss or trend-reversal exit fires, **When** within the CGT window, **Then** CGT logic does not override risk-based exit.

---

### User Story 6 - Regime-Shift & No-Trade Discipline (Priority: P3)

Add regime-shift halt trigger and weekly entry cap to psx-orchestrator per ADR-002 Decisions 13 (A) and 6 (A).

**Why this priority**: Regime shifts cause clustered losses; entry cap prevents forcing trades.

**Independent Test**: orchestrator enforces max 2 entries/week and halts new entries when 3+ stops hit in 5 days. `TODO(REGIME_SHIFT_THRESHOLDS)` in constitution resolved.

**Acceptance Scenarios**:
1. **Given** 3+ open positions hit stops within 5 trading days, **When** regime-shift detector triggers, **Then** new entries halt pending macro reassessment.
2. **Given** 2 entries already this week, **When** a third signal fires, **Then** it is queued to next week.

---

### User Story 7 - Operational Features (Priority: P3)

Implement: (a) hard earnings blackout in risk-management, (b) sector momentum filter in trade-rules-engine, (c) Q4 tax-loss harvesting in psx-trade-journal, (d) Phase 5 deferral in research.md.

**Why this priority**: Important but non-blocking; can be done after backtest pass.

**Independent Test**: Each rule is documented in its respective skill's SKILL.md or references.

**Acceptance Scenarios**:
1. **Given** an earnings event for a held position, **When** the blackout rule applies, **Then** position is flat unless documented thesis requires holding.
2. **Given** a stock in a bottom-quartile sector, **When** sector momentum filter runs, **Then** the stock is excluded regardless of fundamentals.
3. **Given** Q4 arrives and there are unrealized losses on <12mo positions, **When** the tax-loss harvesting routine runs, **Then** losses are harvested to offset gains.
4. **Given** Phase 5 SaaS/Signal-Service is referenced, **When** research.md is checked, **Then** both are deferred to Year 2 of profitable Phase 1/2.

## Edge Cases

- Edge definition must be falsifiable — if proven wrong, edge must be restated.
- Backtest may require data that doesn't exist yet — document data gaps.
- Macro overlay thresholds must not trigger risk-off on every news cycle.
- CGT deferral must not override hard stop-losses.

## Requirements

### Functional Requirements

- **FR-001**: Edge sentence MUST be written into research.md §2.2
- **FR-002**: Falsification numbers MUST be written into research.md §11 and constitution
- **FR-003**: Position cap MUST be updated to ≤10% per position in risk-management skill
- **FR-004**: Backtester MUST run on 2018-2024 data with full PSX frictions
- **FR-005**: Macro overlay MUST define risk-on/neutral/risk-off states
- **FR-006**: CGT-aware exit MUST NOT override stop-loss or trend-reversal exits
- **FR-007**: Regime-shift detector MUST halt new entries when 3+ stops in 5 days
- **FR-008**: Entry cap MUST limit to max 2 entries/week

## Success Criteria

### Measurable Outcomes

- **SC-001**: All 7 constitution TODO gates closed in Pre-Deployment Gates table
- **SC-002**: Backtest produces auditable report with Sharpe, drawdown, win/loss
- **SC-003**: Skills updated: risk-management, trade-rules-engine, market-filter, orchestrator, trade-journal
- **SC-004**: ADR-003 created for macro overlay architecture
