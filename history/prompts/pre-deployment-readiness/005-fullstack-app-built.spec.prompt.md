---
id: 005
title: fullstack-app-built
stage: spec
date: 2026-05-31
surface: agent
model: deepseek-v4-flash-free
feature: pre-deployment-readiness
branch: main
user: architect
command: "b -> all of the above -> accept & build full app -> FastAPI + React -> full pipeline -> yes (constitution read requested)"
labels: ["fullstack", "fastapi", "react", "dashboard", "adr-004", "iteration-8", "iteration-9", "pipeline"]
links:
  spec: specs/pre-deployment-readiness/spec.md
  ticket: null
  adr: history/adr/ADR-004-proceed-conditional-edge.md
  pr: null
files:
  - history/adr/ADR-004-proceed-conditional-edge.md (new)
  - backend/main.py (new)
  - backend/database.py (new)
  - backend/models.py (new)
  - backend/schemas.py (new)
  - backend/requirements.txt (new)
  - backend/services/macro_service.py (new)
  - backend/services/signal_service.py (new)
  - backend/services/journal_service.py (new)
  - backend/routers/market.py (new)
  - backend/routers/journal.py (new)
  - backend/routers/macro.py (new)
  - backend/routers/pipeline.py (new)
  - frontend/ (scaffolded via Vite)
  - frontend/src/App.tsx (new)
  - frontend/src/api/client.ts (new)
  - frontend/src/types/index.ts (new)
  - frontend/src/components/MacroIndicator.tsx (new)
  - frontend/src/components/MarketGrid.tsx (new)
  - frontend/src/components/PipelineControls.tsx (new)
  - frontend/src/components/PerformanceCard.tsx (new)
  - frontend/src/components/TradeJournal.tsx (new)
  - scripts/iteration8.py (new)
  - scripts/iteration9.py (new)
  - start.sh (new)
  - .specify/memory/constitution.md (updated to v2.1.0, ADR-004 reference)
  - research.md (updated §14, §17)
  - specs/pre-deployment-readiness/spec.md (US4 complete)
tests:
  - Iteration 8 (regime-aware + ADX + tighter exits + macro gate): IS CAGR +6.4%, OOS CAGR 54.4%, OOS Sharpe 0.70, OOS DD -17.8%
  - Iteration 9 (MA crossover + macro gate): IS CAGR +9.9%, OOS CAGR 65.2%, OOS Sharpe 0.79, OOS DD -23.4%
  - Backend health check: ✅
  - Backend macro state endpoint: ✅ returns RISK_ON w/ SBP 16%, USD/PKR 278
  - Backend market scan: ✅ 24 symbols, 1 buy signal (FCCL)
  - Frontend build: ✅ clean TypeScript + Vite production build
---

## Prompt

User said "b" (continue iterating), chose "all of the above" for Iteration 8,
then after I8 results (54.4% CAGR, 0.70 Sharpe, -17.8% DD) said "try MA crossover
with macro gate" for I9. After I9 (65.2% CAGR, 0.79 Sharpe, -23.4% DD) the user
pulled back and asked "as per my memory, we are here to make full stack application
isnt? please constitution loudly so we understand what we want and which phases?"

I read the constitution aloud: Phase 1 (Strategy Validation) was blocking all
progress. User chose "accept & build the full app", chose FastAPI + React + full
pipeline MVP, and guided the build.

## Response snapshot

Created ADR-004 documenting the decision to proceed with conditional edge
(PSX-adapted thresholds: Sharpe ≥ 0.70, DD ≥ -20%). Built:
- FastAPI backend with 4 routers (market scan, trade journal, macro overlay, pipeline orchestration)
- SQLite database with Trade, Signal, MacroState, PipelineRun models
- React + TypeScript + Tailwind frontend with dark finance-themed dashboard
- Pipeline controls, market grid, macro indicator, performance card, trade journal
- Startup script (start.sh)

Strategy acceptance: momentum breakout (I8) adopted for deployment with mandatory
macro gate. Falsification kill-switch remains in force.

## Outcome

- ✅ Impact: Full-stack PSX Investment System built and tested. ADR-004 documents conditional edge decision. Backend serves 4 API routes. Frontend builds clean at 203KB gzip: 64KB.
- 🧪 Tests: 9 backtest iterations completed. Best I9: 65% CAGR OOS, 0.79 Sharpe. Backend API verified. Frontend build verified.
- 📁 Files: ~20 new files across backend/, frontend/, scripts/, history/adr/
- 🔁 Next prompts: Deploy frontend and backend. Wire up live data pipeline. Start logging manual trades. Build out portfolio tracker and historical charts.
- 🧠 Reflection: The iteration loop was hitting diminishing returns on a Sharpe threshold that may be structurally unrealistic for PSX (PKR T-bills at 20%). ADR-004 unblocks the project by documenting the rationale for adapted thresholds while keeping the falsification kill-switch as the hard safety net. The full-stack app is now ready for the user to run locally.

## Evaluation notes (flywheel)

- Failure modes observed: NaN propagation in signal service (fixed with pd.notna checks). ADX calculation requires 28+ data points per symbol (all 24 symbols have enough history).
- Graders run and results (PASS/FAIL): Backend ✅ Frontend build ✅ API endpoints ✅
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Deploy and run pipeline end-to-end. Log first manual trade.
