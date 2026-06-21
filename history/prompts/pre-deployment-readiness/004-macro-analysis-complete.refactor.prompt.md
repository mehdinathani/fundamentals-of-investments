---
id: 004
title: macro-analysis-complete
stage: refactor
date: 2026-05-31
surface: agent
model: deepseek-v4-flash-free
feature: pre-deployment-readiness
branch: main
user: architect
command: "yes please (proceed with macro regime analysis)"
labels: ["macro", "regime-analysis", "layer-1.5", "backtest", "completed"]
links:
  spec: specs/pre-deployment-readiness/spec.md
  ticket: null
  adr: history/adr/ADR-003-psx-macro-overlay-layer.md
  pr: null
files:
  - scripts/macro_data.py (new)
  - scripts/macro_regime_analysis.py (new)
  - research.md (updated §14, §17 added)
  - .specify/memory/constitution.md (updated version to 2.0.1, MACRO_OVERLAY_RULES marked resolved)
  - specs/pre-deployment-readiness/spec.md (US4 marked complete)
  - .claude/skills/psx-market-filter/references/macro-states.md (updated with empirical data)
  - data/runs/macro_analysis_results.json (new)
tests:
  - Backtest run with/without macro gate on IS (2018-2023) and OOS (2024)
  - Regime classification for 7 years of monthly PKR macro data (84 months)
  - Cross-reference equity curve by regime: RISK_ON +33.7%, RISK_OFF +11.5%
  - Macro gate blocks 107 entries in IS, improves CAGR -1.2% → +2.7%
---

## Prompt

User asked to proceed with Macro Regime Analysis (US4 / Layer 1.5 overlay). The
backtest Phase showed 26% CAGR OOS but negative IS CAGR across all iterations,
suggesting regime dependency. Plan: fetch SBP rates / USD/PKR / IMF / KSE-100 PE
(2018-2024), classify risk-on/neutral/risk-off, cross-reference equity curve,
add macro gate, re-run backtest, document.

## Response snapshot

Built macro data pipeline (scripts/macro_data.py + macro_regime_analysis.py) with
84 months of SBP rate, USD/PKR, IMF status, and KSE-100 P/E data. Classified
each trading day 2018-2024 into macro states. Cross-referenced equity curve
against regimes. Added risk-off entry block and re-ran backtest.

Key findings:
- Pakistan was RISK_OFF for 54.6% of 2018-2024 → explains IS failure
- Strategy returns +33.7% ann. in RISK_ON vs +11.5% in RISK_OFF
- Macro gate blocks 107 bad entries in IS, improves CAGR by 3.9pp
- OOS 2024 was 100% RISK_ON → explains 26% OOS CAGR
- Strategy still fails Sharpe (0.45) and Max DD (-26.9%) thresholds

## Outcome

- ✅ Impact: Macro overlay analysis complete. Strategy confirmed regime-dependent with conditional edge (works in risk-on, fails in risk-off). Macro gate validated as safety layer.
- 🧪 Tests: Dual backtest run (gate/no-gate) on IS + OOS. Regime performance cross-referenced.
- 📁 Files: 2 new scripts, 3 files updated, 1 new output
- 🔁 Next prompts: Implement skill updates: position cap in risk-management, CGT exits, regime-shift, earnings blackout, sector rotation, tax-loss harvesting. Decide: relax PSX-specific thresholds or iterate rules.
- 🧠 Reflection: The macro analysis confirmed the hypothesis. 54.6% risk-off explains why IS was negative — the strategy was generating signals during hiking cycles, PKR crises, and IMF disruptions. The macro gate is now validated empirical protection, not just theoretical.

## Evaluation notes (flywheel)

- Failure modes observed: None during analysis run. Initial import errors fixed (date conversion, proper from-psx_backtest imports).
- Graders run and results (PASS/FAIL): US4 macro analysis = PASS. Pre-Deployment Gate: FAIL (Sharpe/DD still block).
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Implement remaining skill updates (US5-US7), then re-evaluate. Or: relax Sharpe threshold for PSX-specific context via ADR.
