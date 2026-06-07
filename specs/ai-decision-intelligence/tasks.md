# Tasks: AI Decision Intelligence

**Input**: Design documents from `specs/ai-decision-intelligence/spec.md`, `specs/ai-decision-intelligence/plan.md`
**Prerequisites**: 8 PSX skills installed, scripts layer complete (ratio_calculator, evidence_signals, market_filter, macro_data, category_benchmarks)
**Tests**: Manual validation checklists

## Execution Log

| ID | Status | Date | Notes |
|----|--------|------|-------|
| T000 | ✅ Done | 2026-06-07 | GEMINI_API_KEY added to .env — AI service unblocked |
| T001 | ✅ Done | 2026-06-07 | compare_service.py — multi-context benchmark comparison + percentile_rank |
| T002 | ✅ Done | 2026-06-07 | sector_service.py — symbol→sector mapping + sector medians |
| T003 | ✅ Done | 2026-06-07 | benchmarks API endpoint + test |
| T004 | ✅ Done | 2026-06-07 | ai_service.py — prompt builder + Gemini LLM caller + response parser |
| T005 | ✅ Done | 2026-06-07 | analyze API endpoint + cache layer + test |
| T006 | ✅ Done | 2026-06-07 | BenchmarkChart.tsx — visual comparison bars |
| T007 | ✅ Done | 2026-06-07 | AIReportPanel.tsx — AI narrative display |
| T008 | ✅ Done | 2026-06-07 | SymbolDetail + MarketGrid + types/api client updated |
| T009 | ✅ Done | 2026-06-07 | POST /api/analyze/scan batch endpoint |
| T010 | ✅ Done | 2026-06-07 | AIScanSummary.tsx dashboard panel + App integration |
| T011 | ✅ Done | 2026-06-07 | ai-decision-analysis skill created |
| T012 | ✅ Done | 2026-06-07 | E2E test script (tests/test_ai_decision_e2e.py) |---

## Phase 1: Backend — Comparison Layer

**Purpose**: Compute multi-context benchmarks (sector, KSE30, KSE100, ALLSHR) per symbol

### T001 — `backend/services/compare_service.py`
- Extend `scripts/ratio_calculator.compare_stock()` to include **sector median** comparison
- Add `percentile_rank` — where the stock's metric falls within its sector
- Return full structured JSON matching `ComparisonResult` schema
- Handle edge cases: symbol not found, insufficient data, sector with 0 peers

### T002 — `backend/services/sector_service.py`
- Map any symbol to its sector using `SECTOR_CODES` from `macros.py`
- Compute sector medians from cached market data (market watch)
- Cache sector benchmarks (same pattern as KSE30/KSE100 `load_benchmarks()`)
- Handle: symbol in multiple sectors, unmapped symbols

### T003 — `backend/routers/analyze.py` (benchmarks endpoint) + test
- `GET /api/benchmarks/{symbol}` — returns ComparisonResult
- `GET /api/benchmarks/sector/{sector}` — returns all symbols in sector with their comparisons
- Test with `curl -u admin:psx2026 http://localhost:8000/api/benchmarks/ENGRO`

**Checkpoint**: Running `compare_stock("ENGRO")` shows P/E vs FERTILIZER sector, vs KSE30, vs KSE100, vs ALLSHR with deviation % and rank. API returns structured JSON.

---

## Phase 2: Backend — AI Analysis Layer

**Purpose**: Generate AI-powered decision narratives for each stock

### T004 — `backend/services/ai_service.py`
- Build structured prompt from: ratios + comparisons + technical evidence + market filter + macro state
- Implement `call_llm(prompt)` — wraps Gemini API (use `google-genai` SDK, model: `gemini-2.0-flash`)
- Implement `parse_response(raw)` — validate JSON matches expected schema
- Handle: API errors → fallback to rule-based template, rate limiting, timeouts
- Schema validation: verdict must be one of BUY/SELL/SHORT_SELL/BUY_BACK/STOP_LOSS/HOLD

### T005 — `backend/routers/analyze.py` (analyze endpoint) + cache + test
- `GET /api/analyze/{symbol}` — single symbol AI analysis
- `POST /api/analyze/scan` — batch analysis for multiple symbols
- In-memory cache with 30-min TTL (dict with timestamps)
- Cache invalidation on refresh
- Test with `curl -u admin:psx2026 http://localhost:8000/api/analyze/ENGRO`

**Checkpoint**: `GET /api/analyze/ENGRO` returns full AIAnalysisResult with executive summary, risk factors, action plan. Cache returns 304-hit on second call.

---

## Phase 3: Frontend — AI Display Components

**Purpose**: Visualize benchmark comparisons and AI narratives

### T006 — `frontend/src/components/BenchmarkChart.tsx`
- Horizontal bar chart showing stock value vs sector/KSE30/KSE100 medians
- Color-coded: green (above median), red (below median)
- Deviation % label on each bar
- Rank indicator (e.g., "3/12 in sector")
- Use existing `recharts` library (already installed)

### T007 — `frontend/src/components/AIReportPanel.tsx`
- **Verdict card** — large colored badge (green BUY, red SELL, yellow HOLD, etc.) with confidence meter (HIGH/MEDIUM/LOW)
- **Executive summary** — 2-3 sentence verdict
- **Collapsible sections**: Fundamental Analysis | Technical Analysis | Macro Context | Risk Factors
- **Action plan box** — entry zone, stop-loss, targets, time horizon in a styled card
- **Peer comparison** — stock vs sector peers table

### T008 — Update SymbolDetail + MarketGrid with AI integration
- **SymbolDetail.tsx**: Add tabs: Technical | Fundamentals | AI Analysis | Benchmarks
  - "AI Analysis" tab → `<AIReportPanel>` 
  - "Benchmarks" tab → `<BenchmarkChart>`
- **MarketGrid.tsx**: Add AI verdict column (small colored dot + BUY/SELL/HOLD text)
  - Click opens SymbolDetail on AI Analysis tab
- **api/client.ts**: Add `getBenchmarks(symbol)` and `getAIAnalysis(symbol)` methods
- **types/index.ts**: Add `ComparisonResult` and `AIAnalysisResult` interfaces

---

## Phase 4: Integration & Polish (Optional — post-MVP)

### T009 — Batch AI scan for pipeline
- `POST /api/analyze/scan` with proper batching (max 5 per request, sequential LLM calls)
- Portfolio-level AI summary text

### T010 — `AIScanSummary.tsx` dashboard panel
- Best bets section (top 3 opportunities by AI confidence)
- Red flags section (stocks with STOP_LOSS or SELL verdicts)
- Sector rotation signals

### T011 — Skill creation: `ai-decision-analysis`
- Skill file wrapping the prompt template + response parsing + API key setup
- Documents the ground-truth injection pattern

### T012 — E2E test
- Full pipeline: market data → benchmarks → AI analysis → frontend display
- Test with all 5 validation symbols (ENGRO, OGDC, HBL, LUCK, SYS)
- Verify each AI response has valid verdict, confidence, risk factors, action plan
