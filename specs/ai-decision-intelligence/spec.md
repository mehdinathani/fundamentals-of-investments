# AI Decision Intelligence for PSX

**Goal:** Give finance students CA/ACCA-level analysis by combining fundamentals, technicals, macro, and market context into AI-powered descriptive decision reports.

## The Core Insight

Raw ratios (P/E, EPS, ROE) are already on PSX DPS and broker websites. The **differentiator** is:
1. **Comparison context** — every metric vs its sector, KSE30, KSE100, and ALLSHR median
2. **Multi-layer synthesis** — combining fundamentals + technicals + macro + market filter into one coherent view
3. **AI narrative** — natural language explaining WHY a stock should be bought, sold, short-sold, buy-back, or stop-loss triggered
4. **Student empowerment** — competing with CA/ACCA experience by automating the analytical reasoning they would do

## Feature Set

### US1: Multi-Context Benchmark Comparison
Compute and display every stock metric against 4 benchmarks:
- **Sector median** (e.g., ENGRO vs Fertilizer sector)
- **KSE30 median** (blue-chip index)
- **KSE100 median** (broad market)
- **ALLSHR median** (total market)

Display: rank percentile, deviation %, and visual bar.

### US2: AI-Powered Decision Narrative
For each stock, generate a structured AI analysis covering:
- **Executive Summary** — 2-3 sentence verdict
- **Fundamental Health** — narrative on ratios vs benchmarks
- **Technical Position** — trend, momentum, volume story
- **Market Context** — macro regime, sector health, liquidity
- **Composite Decision** — BUY / SELL / SHORT SELL / BUY BACK / STOP LOSS / HOLD with confidence level
- **Key Risks** — top 3 risk factors
- **Action Plan** — entry zone, stop-loss, target, time horizon

### US3: Decision Dashboard
Frontend component showing AI analysis with:
- Color-coded recommendation cards
- Comparison bar charts (stock vs sector vs KSE30 vs KSE100)
- Expandable narrative sections
- Confidence meter

### US4: Batch Scan with AI Summary
When running the full pipeline scan, generate:
- Per-stock AI analysis
- **Portfolio-level summary** — best opportunities, red flags, sector rotation signals
- **Comparison table** — how each symbol ranks within its peer group

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│  MarketGrid → SymbolDetail → AIReportPanel                   │
│  PipelineControls → AIScanSummary                           │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP
┌──────────────────────▼──────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│                                                              │
│  /api/analyze/{symbol}       → AI analysis for one stock     │
│  /api/analyze/scan           → AI analysis for all scanned   │
│  /api/benchmarks/{symbol}    → multi-context comparison      │
│                                                              │
│  ┌─────────────────┐  ┌──────────────────┐                   │
│  │ compare_service  │  │  ai_service      │                   │
│  │ • sector median  │  │ • build_prompt() │                   │
│  │ • KSE30/KSE100   │  │ • call_llm()     │                   │
│  │ • ALLSHR median  │  │ • parse_response │                   │
│  │ • rank/percentile│  │ • cache_results  │                   │
│  └────────┬─────────┘  └────────┬─────────┘                   │
│           │                     │                             │
│           └─────────┬───────────┘                             │
│                     ▼                                         │
│  ┌─────────────────────────────────────────┐                  │
│  │  Scripts Layer                           │                  │
│  │  ratio_calculator.py (compare_stock)     │                  │
│  │  evidence_signals.py (generate_signal)   │                  │
│  │  market_filter.py (market_reality_filter)│                  │
│  │  macro_data.py (classify_regime)         │                  │
│  │  category_benchmarks.py (load_benchmarks)│                  │
│  └─────────────────────────────────────────┘                  │
└──────────────────────────────────────────────────────────────┘
```

## Data Structures

### ComparisonResult (benchmarks)
```json
{
  "symbol": "ENGRO",
  "sector": "FERTILIZER",
  "price": 320.50,
  "comparisons": {
    "PE": {
      "value": 8.5,
      "sector": {"median": 10.2, "deviation_pct": -16.7, "rank": 3},
      "KSE30": {"median": 9.8, "deviation_pct": -13.3, "rank": 15},
      "KSE100": {"median": 11.5, "deviation_pct": -26.1, "rank": 42},
      "ALLSHR": {"median": 12.1, "deviation_pct": -29.8, "rank": 88}
    },
    "EPS": { "...similar..." },
    "ROE": { "...similar..." },
    "DE": { "...similar..." },
    "DIVIDEND_YIELD": { "...similar..." }
  }
}
```

### AIAnalysisResult
```json
{
  "symbol": "ENGRO",
  "verdict": "BUY",
  "confidence": "HIGH",
  "time_horizon": "MEDIUM_TERM (3-6 months)",
  "executive_summary": "ENGRO presents a compelling value...",
  "fundamental_analysis": "...",
  "technical_analysis": "...",
  "macro_context": "...",
  "risk_factors": ["Fertilizer subsidy policy risk", "...", "..."],
  "action_plan": {
    "entry_zone": "315-325",
    "stop_loss": "295 (-8%)",
    "target_1": "350 (+9%)",
    "target_2": "380 (+19%)",
    "position_sizing": "Standard tier"
  },
  "peer_comparison": "ENGRO trades at a discount to sector...",
  "generated_at": "2026-06-07T10:00:00Z"
}
```

## Implementation Plan

### Phase 1: Backend Services (Days 1-2)

1. **`backend/services/compare_service.py`** — Multi-context benchmark comparison
   - Extends `ratio_calculator.compare_stock()` to include sector medians
   - Adds percentile rank computation
   - Returns structured JSON for frontend

2. **`backend/services/ai_service.py`** — AI analysis engine
   - Builds structured prompt from all data sources
   - Calls Gemini API (via google-genai SDK, model: gemini-2.0-flash)
   - Parses structured JSON response
   - Caches results with TTL (30 min)

3. **New API endpoints** in `backend/routers/analyze.py`
   - `GET /api/analyze/{symbol}` — AI analysis for one symbol
   - `POST /api/analyze/scan` — Batch AI analysis
   - `GET /api/benchmarks/{symbol}` — Multi-context comparison data

4. **`backend/services/sector_service.py`** — Sector mapping and median computation
   - Maps any symbol to its sector
   - Computes sector medians from market data
   - Caches sector benchmarks

### Phase 2: Frontend Components (Days 2-3)

5. **`frontend/src/components/AIReportPanel.tsx`** — AI analysis display
   - Verdict card with confidence meter
   - Expandable narrative sections
   - Action plan box
   - Risk factors list

6. **`frontend/src/components/BenchmarkChart.tsx`** — Visual comparison bars
   - Stock value vs sector/KSE30/KSE100 medians
   - Color-coded deviation bars
   - Rank indicator

7. **Update `SymbolDetail.tsx`** — Integrate AI report and benchmarks tab
   - Tabs: Technical | Fundamentals | AI Analysis | Benchmarks

8. **Update `MarketGrid.tsx`** — Add AI verdict column
   - Show BUY/SELL/HOLD with confidence indicator
   - Quick-access AI analysis button

### Phase 3: Pipeline Integration (Day 3)

9. **Update `run_scan.py`** — Add AI summary to decision sheet
   - AI executive summary per symbol
   - Portfolio-level AI overview

10. **`frontend/src/components/AIScanSummary.tsx`** — Full scan AI summary
    - Best bets section
    - Red flags section
    - Sector rotation suggestions

### Phase 4: Skills Integration

11. Create/update skill: **`ai-decision-analysis`**
    - Wraps the AI prompt templates and response parsing
    - Ensures consistent output structure
    - Handles API key management

## Non-Goals
- Replacing human judgment — AI is advisory, not autonomous
- Real-time streaming — analysis is request-response
- Multi-language support — English only for v1

## Key Risks
1. **API cost** — Cache aggressively, batch requests
2. **Hallucination** — Constrain with structured prompts + ground truth data
3. **Latency** — AI calls take 5-15s; show loading states and cache
