# AI Decision Intelligence — Architecture Plan

## 1. Scope & Dependencies

### In Scope
- Multi-context benchmark comparison (sector, KSE30, KSE100, ALLSHR)
- AI-powered descriptive analysis for each stock
- 5-action decision framework: BUY / SELL / SHORT SELL / BUY BACK / STOP LOSS / HOLD
- Frontend AI report panel with confidence meter, action plan, risk factors
- Batch AI analysis for full pipeline scan
- Caching layer to manage API costs

### Out of Scope (v1)
- Real-time streaming AI responses
- Historical AI analysis tracking
- User feedback loop on AI accuracy
- Portfolio-level AI recommendations across multiple strategies

### External Dependencies
- **Gemini API** (google-genai SDK) — for AI narrative generation via `gemini-2.0-flash`
- **Existing scripts** — ratio_calculator, evidence_signals, market_filter, macro_data, category_benchmarks (all already built)

## 2. Key Decisions & Rationale

### Decision 1: Structured JSON from AI
Use constrained prompting with JSON schema to get parseable structured output rather than free-form text. This lets the frontend render specific sections (risks, action plan) without NLP parsing.

### Decision 2: Comparison at the backend, not in AI prompt
Raw comparison data (deviations, ranks) is computed in Python and embedded in the prompt as facts. The AI interprets but doesn't fabricate numbers. Ground truth comes from the scripts layer.

### Decision 3: Cache with TTL
AI analysis is cached for 30 minutes. Batch scan invalidates cache. This keeps costs predictable — ~50 API calls/day max for active use.

### Decision 4: Separate compare service from AI service
The comparison logic is independent and reusable without AI. This lets users see "ENGRO P/E is 16% below sector median" even if they skip the AI narrative.

## 3. API Contracts

### `GET /api/benchmarks/{symbol}`
```
Response: ComparisonResult (see spec)
Errors: 404 (symbol not found), 503 (benchmarks stale)
```

### `GET /api/analyze/{symbol}`
```
Query params: tier (standard|conservative, default: standard)
Response: AIAnalysisResult (see spec)
Errors: 404, 503, 429 (rate limited)
```

### `POST /api/analyze/scan`
```
Body: { symbols?: string[], tier?: string }
Response: { results: AIAnalysisResult[], summary: string }
```

## 4. Non-Functional Requirements

| Aspect | Target |
|--------|--------|
| AI response time | < 15s per symbol |
| Cache hit rate | > 70% in active session |
| Cost per analysis | ~$0.00 (Gemini 2.0 Flash — free tier available) |
| Concurrent analysis | 5 symbols batch, sequential calls |
| Error resilience | Failed AI → fallback to rule-based narrative |

## 5. Data Flow

```
User clicks "Analyze ENGRO"
  → Frontend calls GET /api/analyze/ENGRO
  → Backend checks cache (Redis or in-memory dict with TTL)
     → HIT → return cached
     → MISS → continue
  → Backend gathers:
      • compare_stock("ENGRO") → ratios vs KSE30/KSE100/ALLSHR
      • generate_signal("ENGRO") → technical evidence
      • market_reality_filter("ENGRO") → liquidity/operator check
      • get_sector("ENGRO") → FERTILIZER
      • get_sector_medians("FERTILIZER") → sector benchmarks
      • get_current_macro_state() → macro regime
  → Backend builds structured prompt with all data
  → Backend calls Gemini API with prompt
  → Backend parses JSON response, validates schema
  → Backend caches result
  → Frontend renders AIReportPanel
```

## 6. AI Prompt Architecture

The prompt follows a strict template:

```
You are a CA/ACCA-level equity analyst analyzing {SYMBOL} on the Pakistan Stock Exchange.

## Data Provided (ground truth, do not alter):
Price: {PRICE}
Sector: {SECTOR}
Macro Regime: {MACRO_STATE}

### Fundamental Ratios vs Benchmarks:
{COMPARISON_TABLE}

### Technical Evidence:
{technical signal data}

### Market Filter:
{liquidity/operator verdict}

## Output Format — Return valid JSON only:
{
  "verdict": "BUY|SELL|SHORT_SELL|BUY_BACK|STOP_LOSS|HOLD",
  "confidence": "HIGH|MEDIUM|LOW",
  "time_horizon": "...",
  "executive_summary": "2-3 sentences",
  "fundamental_analysis": "paragraph",
  "technical_analysis": "paragraph",
  "macro_context": "1-2 sentences",
  "risk_factors": ["risk1", "risk2", "risk3"],
  "action_plan": {
    "entry_zone": "...",
    "stop_loss": "...",
    "target_1": "...",
    "target_2": "...",
    "position_sizing": "..."
  },
  "peer_comparison": "How this stock compares to sector peers"
}
```

## 7. Implementation Order

```
Week 1:
  T001 — compare_service.py (multi-context benchmarks)
  T002 — sector_service.py (symbol→sector mapping, sector medians)
  T003 — benchmarks API endpoint + tests
  T004 — ai_service.py (prompt builder + LLM caller + parser)
  T005 — analyze API endpoints + cache layer + tests
  T006 — BenchmarkChart.tsx + AIReportPanel.tsx
  T007 — Update SymbolDetail with tabs
  T008 — Update MarketGrid with AI column

Week 2:
  T009 — Batch scan analysis endpoint
  T010 — AIScanSummary.tsx
  T011 — Pipeline integration
  T012 — ai-decision-analysis skill creation
  T013 — End-to-end testing
```

## 8. Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| AI hallucinates numbers | Prompt says "ground truth, do not alter"; all numbers injected, AI only interprets |
| API down/slow | Rule-based fallback: "AI analysis unavailable. Technical: {signal}. Fundamentals: {comparison summary}." |
| Cost overruns | Cache aggressively; use Gemini 2.0 Flash (free tier); batch analysis processes sequentially with max 10 per request |
| Student misinterpretation | Add disclaimer: "AI-generated analysis is educational. Verify before trading." |
