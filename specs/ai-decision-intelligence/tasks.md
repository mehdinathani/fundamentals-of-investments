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
| T012 | ✅ Done | 2026-06-07 | E2E test script (tests/test_ai_decision_e2e.py) |
| T013 | ✅ Done | 2026-06-21 | ai_service.py — mentor-voice persona + IGNORE verdict (ground-truth block intact) |
| T014 | ✅ Done | 2026-06-21 | market.py — GET /api/market/history/{symbol} (OHLC + MA overlays) |
| T015 | ✅ Done | 2026-06-21 | market.py — GET /api/market/heatmap (sector performance data) |
| T016 | ✅ Done | 2026-06-21 | types/index.ts + api/client.ts — Candle/Heatmap types, getHistory/getHeatmap |
| T017 | ✅ Done | 2026-06-21 | PriceChart.tsx — recharts close line + MA20/50/200 + volume |
| T018 | ✅ Done | 2026-06-21 | SectorHeatmap.tsx — colored sector grid, highlights stock's sector |
| T019 | ✅ Done | 2026-06-21 | RatioRadar.tsx — grouped bars vs SECTOR/KSE30/KSE100/ALLSHR (auto-extends) |
| T020 | ✅ Done | 2026-06-21 | VerdictGauge.tsx — semicircular confidence dial, verdict-colored |
| T021 | ✅ Done | 2026-06-21 | SymbolDetail Chart+Market tabs; RatioRadar replaces BenchmarkChart (deleted) |
| T022 | ✅ Done | 2026-06-21 | AIReportPanel gauge + IGNORE style; MarketGrid IGNORE dot; Modal size="lg" |
| T023 | ✅ Done | 2026-06-21 | Synced SKILL.md; added IGNORE + mentor-voice E2E assertions |
| T024 | ✅ Done | 2026-06-21 | scripts/financial_ratio_parser.py — BS/P&L parser → ROE, D/E, Dividend Yield with parquet caching |
| T025 | ✅ Done | 2026-06-21 | compute_ratios_for_symbol() + compare_stock_full() emit ROE/DE/DIVIDEND_YIELD (RATIO_FIELDS loop) |
| T026 | ✅ Done | 2026-06-21 | Stale-data guard (FINANCIALS_CACHE_TTL_DAYS=7) + graceful omission for unavailable statements |

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

---

## Phase 5: Differentiation Pass — "broker teaching a student" ✅ (2026-06-21)

**Purpose**: Turn the click-through view from raw ratios into the differentiated experience —
mentor-voice narrative, IGNORE verdict, and four on-screen visuals. Maps to spec US1 (benchmark
comparison), US2 (AI narrative), US3 (decision dashboard visuals). All tasks shipped; see PHR 004.

**Independent test**: Click any symbol → Chart tab shows price + MAs + volume; Market tab shows
sector heatmap with the stock's sector highlighted; Benchmarks tab shows grouped bars vs all 4
indices; AI Mentor tab opens with a confidence gauge and a plain-language broker explanation;
an illiquid symbol returns IGNORE.

- [x] T013 [US2] Add IGNORE to `VERDICTS` and rewrite `build_prompt()` persona to seasoned-broker-mentoring-a-student voice (jargon defined inline, ground-truth block + JSON schema unchanged) in `backend/services/ai_service.py`
- [x] T014 [P] [US3] Add `GET /api/market/history/{symbol}?days=N` (reuse `get_historical_data` + `compute_indicators` for MA20/50/200) in `backend/routers/market.py`
- [x] T015 [P] [US3] Add `GET /api/market/heatmap` (reuse sector grouping from `heatmap_tradebars`, return data not print) in `backend/routers/market.py`
- [x] T016 [US3] Add `Candle`/`HistoryResponse`/`HeatmapSector`/`HeatmapResponse` types + IGNORE to verdict union in `frontend/src/types/index.ts`; add `getHistory`/`getHeatmap` in `frontend/src/api/client.ts`
- [x] T017 [P] [US3] Build price chart (recharts ComposedChart: close + MA20/50/200 + volume, 3M/6M/1Y toggle) in `frontend/src/components/PriceChart.tsx`
- [x] T018 [P] [US3] Build sector heatmap (colored grid, highlights stock's own sector) in `frontend/src/components/SectorHeatmap.tsx`
- [x] T019 [P] [US1] Build multi-ratio benchmark visual (grouped bars vs SECTOR/KSE30/KSE100/ALLSHR; maps over `benchmarks.ratios` so it auto-extends) in `frontend/src/components/RatioRadar.tsx`
- [x] T020 [P] [US2] Build verdict/confidence gauge (semicircular SVG dial, verdict-colored incl. IGNORE) in `frontend/src/components/VerdictGauge.tsx`
- [x] T021 [US3] Add Chart + Market tabs (Chart default), swap `BenchmarkChart` for `RatioRadar`, delete orphaned `BenchmarkChart.tsx` in `frontend/src/components/SymbolDetail.tsx`
- [x] T022 [US2] Mount `VerdictGauge` + add IGNORE style in `frontend/src/components/AIReportPanel.tsx`; add IGNORE dot in `frontend/src/components/MarketGrid.tsx`; add `size="lg"` + scroll in `frontend/src/components/Modal.tsx`
- [x] T023 [US2] Sync verdict set/voice/components/endpoints in `.claude/skills/ai-decision-analysis/SKILL.md`; add IGNORE + mentor-voice assertions in `tests/test_ai_decision_e2e.py`

**Checkpoint**: ✅ `npm run build` + `tsc -b` clean; parser/VERDICTS/prompt verified offline. recharts (prev. unused) now drives all charts.

---

## Phase 6: Extended Ratio Parser ✅ (2026-06-21)

**Purpose**: Compute ROE / Debt-to-Equity / Dividend-Yield so the benchmark visual fills out.
`RatioRadar` already maps over all ratios, so no frontend change was needed. Parser caches to
parquet (7-day TTL) following constitution data-quality rules.

- [x] T024 [US1] Build PSX financial-statement parser (balance sheet + P&L → ROE, D/E, Dividend Yield) with parquet caching, following `financial-ratios-psx` skill formulas, in `scripts/financial_ratio_parser.py`
- [x] T025 [US1] Extend `compute_ratios_for_symbol()` / `compare_stock_full()` to emit ROE/DE/DIVIDEND_YIELD comparisons in `scripts/ratio_calculator.py` + `backend/services/compare_service.py`
- [x] T026 [US1] Add stale-data guard + graceful omission when statements unavailable (no invented values) across the new parser path

**Checkpoint**: `GET /api/benchmarks/ENGRO` returns ROE/DE/Dividend alongside P/E & EPS; RatioRadar renders all five with no frontend edit.

---

## Dependencies & Story Mapping

- **US1 (Benchmark comparison)**: T001-T003 ✅ + T019 ✅ (visual) → T024-T026 ⏸ (more ratios)
- **US2 (AI narrative)**: T004-T005, T007 ✅ + T013, T020, T022, T023 ✅ (mentor voice, gauge, IGNORE)
- **US3 (Decision dashboard)**: T006, T008 ✅ + T014-T018, T021 ✅ (chart, heatmap, tabs)
- **US4 (Batch scan)**: T009-T010 ✅ (unchanged this pass)
- Phase 6 (T024-T026) is independent and blocks nothing already shipped.

## Parallel Execution (Phase 5, as built)
- Backend T014 ‖ T015 (same file, distinct endpoints — independent logic)
- Frontend T017 ‖ T018 ‖ T019 ‖ T020 (four separate component files, no shared state)
- T013 (prompt) independent of all frontend tasks
