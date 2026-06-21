---
id: 003
title: macro-regime-analysis-next
stage: misc
date: 2026-05-30
surface: agent
model: deepseek-v4-flash-free
feature: pre-deployment-readiness
branch: main
user: architect
command: "what should be the next? -> yes -> record phr"
labels: ["macro", "regime-analysis", "layer-1.5", "next-steps", "phr"]
links:
  spec: specs/pre-deployment-readiness/spec.md
  ticket: null
  adr: history/adr/ADR-003-psx-macro-overlay-layer.md
  pr: null
files:
  - .claude/skills/psx-market-filter/references/macro-states.md
  - .claude/skills/psx-market-filter/SKILL.md
  - history/adr/ADR-003-psx-macro-overlay-layer.md
  - history/prompts/pre-deployment-readiness/003-macro-regime-analysis-next.misc.prompt.md
tests:
  - Backtest US3 complete: 37/37 tasks done
  - 7 iterations tested, best config: 26% CAGR OOS momentum breakout
  - IS negative across all iterations — regime dependency suspected
---

## Prompt

User asked: "what should be the next?"
Response: Recommended macro regime analysis (US4 Layer 1.5 overlay) to diagnose IS/OOS disparity.
User: "yes"
User: "record phr"

## Response snapshot

Proceeding with Macro Regime Analysis. Goal: classify 2018-2024 into risk-on/neutral/risk-off periods using SBP rates, USD/PKR, IMF status, KSE-100 P/E. Cross-reference backtest equity curve to see if strategy returns are regime-dependent. If so, add macro gate to block entries in risk-off — potentially fixing both IS losses (-1.2% CAGR) and drawdown (-21.7%).

## Outcome

- ✅ Impact: Backtest complete (37/37 tasks). Next phase defined: Macro Regime Analysis.
- 🧪 Tests: N/A — analysis phase
- 📁 Files: 1 new PHR
- 🔁 Next prompts: Fetch SBP/USD/PKR/IMF/KSE-100 PE data → classify regimes → cross-reference backtest → add macro gate → re-run → document findings
- 🧠 Reflection: The regime-dependency hypothesis is the most promising path forward. If macro gating turns IS positive, the strategy becomes deployable.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Fetch macro data and classify 2018-2024 regimes

