---
id: 002
title: backtest-execution-failed
stage: red
date: 2026-05-30
surface: agent
model: deepseek-v4-flash-free
feature: pre-deployment-readiness
branch: main
user: architect
command: "yes (continue from T015 backtest)"
labels: ["backtest", "momentum-breakout", "psx", "strategy-validation", "fail"]
links:
  spec: specs/pre-deployment-readiness/spec.md
  ticket: null
  adr: history/adr/ADR-002-pre-deployment-strategy-decisions.md
  pr: null
files:
  - scripts/psx_backtest.py (new)
  - scripts/fetch_kse100_data.py (new)
  - research.md (updated §13, §14, §16)
  - .specify/memory/constitution.md (updated backtest gate)
  - history/prompts/pre-deployment-readiness/002-backtest-execution-failed.red.prompt.md
tests:
  - "7 backtest iterations run (0-7)"
  - "IS 2018-2023: all iterations FAIL (negative CAGR)"
  - "OOS 2024: Iteration 7 reaches 26% CAGR, 3.04 W/L, 0.54 Sharpe, -21.7% DD"
  - "5/7 OOS thresholds pass; Sharpe and Max DD fail"
---

## Prompt

User asked: "yes" (proceed from T015 backtest execution) then:
- "Build Python backtest engine" (approach chosen)
- "Iterate rules & re-backtest" (after initial FAIL)
- "Momentum breakout (new strategy)" (after ADX iteration failed)
- "Tweak momentum (trailing stop, RSI filter)" (after momentum showed promise)
- "Simplify exits (trailing stop only)" (after tweaks lost improvement)
- "Stop — need more analysis" (final decision after 7 iterations)

## Response snapshot

Built complete Python backtest engine (544 lines, scripts/psx_backtest.py) with PSX-specific frictions, walk-forward validation, and 7 strategy iterations. Fetched 10 years of KSE-100 data from DPS portal for 24 symbols.

Results: MA crossover strategy fails completely on PSX (CAGR 2.6%, Sharpe 0.01). Momentum breakout (20-day high) achieves 26% CAGR OOS with 3.04 W/L ratio and 48.6% win rate, but misses Sharpe (0.54) and Max DD (-21.7%) thresholds. IS performance negative across all iterations, indicating regime dependency.

Decision: STOP — further macro regime analysis required before capital deployment.

## Outcome

- ✅ Impact: 7 backtest iterations completed across 2 strategy families (MA crossover → momentum breakout). Best config achieves 26% CAGR OOS with 35 trades and 3.04 W/L. Backtest engine and data pipeline built and reusable.
- 🧪 Tests: 7 iterations, IS + OOS runs per iteration, full PSX frictions modeled
- 📁 Files: 2 new (scripts/), 2 updated (research.md, constitution.md), 1 new PHR
- 🔁 Next prompts: Macro regime analysis (US4 — Layer 1.5 overlay) to diagnose IS/OOS disparity. Then decide: proceed with refined strategy or redesign.
- 🧠 Reflection: Momentum breakout outperforms MA crossover by a wide margin on PSX. The IS/OOS disparity suggests the strategy is regime-dependent (works in trending bull markets). Sharpe threshold ≥1.0 may be structurally unrealistic for PSX given 20% PKR T-bill rate. Backtest engine is now a reusable asset.

## Evaluation notes (flywheel)

- Failure modes observed: NaN propagation in T+2 settlement logic (fixed), BREAKOUT column missing from compute_indicators (fixed), entry/exit filters too aggressive in iterations 1,3,5,6
- Graders run and results (PASS/FAIL): US3 backtest gate = FAIL (5/7 OOS thresholds met, but IS negative)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Macro regime analysis (US4) to determine if IS failure is regime-dependent and whether bear-market rules can be added

