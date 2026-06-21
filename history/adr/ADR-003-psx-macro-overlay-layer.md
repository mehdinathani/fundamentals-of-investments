# ADR-003: PSX Macro Overlay Layer (Layer 1.5)

> **Scope**: Macro-awareness layer for the PSX investment system. Defines risk-on/neutral/risk-off states, data sources, and automated universe-tightening rules.

- **Status:** Accepted
- **Date:** 2026-05-30
- **Feature:** pre-deployment-readiness
- **Parent:** ADR-002 Decision 8 — "Macro Overlay (Layer 1.5)"

<!-- Significance checklist
     1) Impact: YES — adds a new architectural layer between Layers 1 and 2,
        changes universe construction logic across all downstream skills.
     2) Alternatives: YES — micro-only vs macro-filter vs full overlay.
     3) Scope: YES — touches market-filter (universe), trade-rules (entry gates),
        orchestrator (pipeline), and constitution (Layered Architecture).
-->

## Context

PSX is macro-dominated. SBP rate decisions, IMF program reviews, USD/PKR trends, and CPI prints drive index direction more than stock-level fundamentals. The pre-existing architecture (research.md §4) had no macro-awareness layer — it went directly from fundamental screening (Layer 1) to technical signals (Layer 2).

The consequence: during macro-driven selloffs (e.g., SBP hiking, IMF at risk), individual stock fundamentals offered no protection. The system would generate BUY signals on fundamentally sound stocks that were getting swept down by macro. The stops would fire one-by-one, taking 5-7 small losses, instead of recognizing the regime shift early.

ADR-002 Decision 8 resolved: **Add Layer 1.5 Macro Overlay**.

## Decision

**Architecture: Rule-based Macro States with Automated Universe Tightening**

### Macro States

Three states derived from four data sources:

| State | SBP Policy | USD/PKR (30d) | IMF Status | KSE-100 P/E |
|-------|-----------|---------------|------------|-------------|
| **Risk-on** | Cutting or on hold | Stable or appreciating | On track, reviews passing | < 10-yr median |
| **Neutral** | Mixed signals | Range-bound (<3% move) | Program active, minor delays | Near 10-yr median |
| **Risk-off** | Hiking | Sharply weakening (>5% in 30d) | At risk, review missed | > 10-yr median + 1SD |

Any single "risk-off" input flips the state to risk-off. Majority vote determines neutral vs risk-on when inputs are mixed.

### Data Sources

| Input | Source | Frequency | Notes |
|-------|--------|-----------|-------|
| SBP policy rate | SBP website / MUFAP | Monthly (MPC meetings) | Best-effort — manual check if automated fetch fails |
| USD/PKR | PSX / forex portal | Daily | Use interbank rate |
| IMF program status | IMF press releases | Event-driven | Track program review dates |
| KSE-100 P/E | PSX data portal | Weekly | Compare to rolling 10-yr median |

### Universe Rules by State

| State | Universe | Action |
|-------|----------|--------|
| **Risk-on** | Full tradable universe | Normal pipeline execution |
| **Neutral** | Full tradable universe | Sharpen position sizing (use conservative 3% risk) |
| **Risk-off** | Defensives (utilities, cash-rich firms, food) OR 100% cash | Block all new entries in non-defensives; review existing positions |

### Implementation

- Layer 1.5 sits **between Layer 1 (Fundamental Screen) and Layer 2 (Technical Signals)** in the pipeline.
- The macro state is checked at the start of each pipeline run (psx-orchestrator Step 2.5).
- The macro state gates which stocks proceed to technical analysis.
- In risk-off, the market-filter skill restricts the tradable universe to defensives.
- The regime-shift protocol (ADR-002 D13) complements this — if 3+ stops hit in 5 days despite macro being risk-on, the macro assessment may be stale.

## Consequences

### Positive

- Closes the largest analytical gap for a PKR equity strategy — PSX is macro-dominated, and the framework now acknowledges it.
- Automated universe tightening prevents buying into macro-driven selloffs.
- Simple rule-based system avoids over-engineering — three states, four inputs, clear actions.

### Negative

- Adds data dependencies (SBP rates, USD/PKR, IMF) — these are manual/best-effort until automated.
- Risk-on → risk-off transition may lag if data updates are slow (e.g., SBP rates monthly).
- Defensive classification requires periodic review — a stock may shift sectors or risk profile.
- More complex pipeline (new orchestrator step).

## Alternatives Considered

**A. Stay micro-focused (rejected).** PSX is macro-dominated; ignoring this is structurally unsound.

**B. Macro as filter only (rejected).** Blocking new entries in risk-off without tightening the universe still risks existing positions in vulnerable sectors.

**C. Quantitative macro model (deferred).** Using macro futures/rates to quantify risk. Too complex for Phase 1; revisit after backtest validation.

## References

- Research: `research.md` §15.9 (Macro Overlay Missing), §15.14 (Regime-Shift Protocol)
- Constitution: `.specify/memory/constitution.md` §Macro Overlay, §Regime-Shift Protocol
- Parent ADR: `history/adr/ADR-002-pre-deployment-strategy-decisions.md` (Decision 8)
- Skill: `.claude/skills/psx-market-filter/SKILL.md` (Layer 1.5 implementation)
- Skill: `.claude/skills/psx-orchestrator/SKILL.md` (pipeline integration)
