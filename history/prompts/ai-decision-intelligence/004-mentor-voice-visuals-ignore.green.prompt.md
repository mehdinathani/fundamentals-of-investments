---
id: 004
title: Mentor-voice report, visuals, IGNORE verdict
stage: green
date: 2026-06-21
surface: agent
model: claude-opus-4-8[1m]
feature: ai-decision-intelligence
branch: feature/psx-skills-architecture
user: AIDD
command: build the "CA broker teaching a student" click-through experience
labels: ["ai", "frontend", "recharts", "mentor-voice", "ignore-verdict", "visuals"]
links:
  spec: specs/ai-decision-intelligence/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/services/ai_service.py
  - backend/routers/market.py
  - frontend/src/types/index.ts
  - frontend/src/api/client.ts
  - frontend/src/components/PriceChart.tsx
  - frontend/src/components/SectorHeatmap.tsx
  - frontend/src/components/RatioRadar.tsx
  - frontend/src/components/VerdictGauge.tsx
  - frontend/src/components/SymbolDetail.tsx
  - frontend/src/components/AIReportPanel.tsx
  - frontend/src/components/MarketGrid.tsx
  - frontend/src/components/Modal.tsx
  - frontend/src/components/BenchmarkChart.tsx (deleted)
  - .claude/skills/ai-decision-analysis/SKILL.md
  - tests/test_ai_decision_e2e.py
tests:
  - "offline parser/VERDICTS checks: IGNORE in VERDICTS, parser accepts IGNORE, rejects invalid, strips fences — PASS"
  - "mocked build_prompt: mentor/broker voice present, IGNORE offered, GROUND TRUTH kept, old analyst persona gone — PASS"
  - "frontend: npm run build + tsc -b — PASS (605kB bundle)"
---

## Prompt

as i discussed in last phr i want to build this application for a finance student who can beat CA or ACCA or Senior trader with help of AI [...] when i click on any script, instead of just ratios [...] it should generate high level visuals, heatmap, compare to this script with its category, kse30, kse100 and overall market, descriptive analysis that why this script should be buy, sell, shortsell, stoploss, buy back, hold, ignore etc. and support like a CA finalist old broker is explaining to a finance student.

## Response snapshot

Built the differentiated click-through experience on top of the existing AI Decision Intelligence backend. Four product decisions confirmed with the user first: (1) rewrite AI report itself to mentor voice, (2) build all four visuals, (3) add IGNORE verdict, (4) ship rich P/E+EPS visual now, defer ROE/D-E/Dividend (need a new financial-statement parser).

**Backend:**
- `ai_service.py`: added IGNORE to VERDICTS; rewrote `build_prompt()` persona from "CA/ACCA analyst" to "seasoned PSX broker (30 yrs) mentoring a finance student" — warm, defines jargon inline, explains why. Kept GROUND TRUTH block + JSON schema intact (anti-hallucination guard preserved). Added IGNORE verdict guide tied to Layer 0 market-filter REJECT.
- `market.py`: two new endpoints — `GET /api/market/history/{symbol}?days=N` (reuses `get_historical_data` + `compute_indicators` for MA20/50/200) and `GET /api/market/heatmap` (reuses the sector grouping from `heatmap_tradebars`, returns data instead of printing).

**Frontend (recharts, previously installed but unused):**
- New: `PriceChart` (close line + 3 MAs + volume, 3M/6M/1Y), `SectorHeatmap` (colored grid, highlights stock's own sector), `RatioRadar` (grouped bars stock vs sector/KSE30/KSE100/ALLSHR; maps over whatever ratios exist so it auto-extends), `VerdictGauge` (semicircular confidence dial, verdict-colored).
- `SymbolDetail`: new Chart + Market tabs, default to Chart, RatioRadar replaces flat BenchmarkChart, large modal.
- `AIReportPanel`: mounted VerdictGauge, added IGNORE style. `MarketGrid`: IGNORE dot. `Modal`: `size="lg"` + scroll. Deleted orphaned `BenchmarkChart.tsx`.

**Skill + tests:** synced `ai-decision-analysis/SKILL.md` (voice, IGNORE, new components, new endpoints, verdict table). Added IGNORE + mentor-voice assertions to E2E test.

## Outcome

- ✅ Impact: clicking a stock now opens price chart, on-screen sector heatmap, multi-benchmark visual, confidence gauge, and a plain-language broker-mentoring-a-student narrative with 7 verdicts incl. IGNORE.
- 🧪 Tests: backend logic + prompt verified offline (live-network E2E paths can't run in sandbox); frontend builds & typechecks clean.
- 📁 Files: 4 new components, 1 deleted, ~10 modified.

## Evaluation notes (flywheel)

- Failure modes observed: full E2E hangs in sandbox (build_prompt → get_market_watch makes live HTTP). Worked around with mocked + offline assertions.
- Constitution: AI stays advisory; IGNORE grounded in existing Layer 0 filter, not invented; no new unreliable data source added (ROE/D-E deferred).
- Next experiment (smallest change to try): run the dev server against live PSX data, spot-check mentor tone on 2-3 symbols + an illiquid one for IGNORE; then build the deferred ROE/D-E/Dividend parser so RatioRadar fills out.
