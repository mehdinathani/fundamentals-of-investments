---
name: ai-decision-analysis
description: |
  Generate AI-powered decision narratives for PSX stocks by combining fundamental
  ratios, benchmark comparisons, technical evidence, market filter data, and macro
  context into structured BUY/SELL/HOLD analysis. Uses Gemini 2.0 Flash via the
  google-genai SDK. This skill should be used when users ask to analyze a stock,
  generate AI reports, run batch scans, or interpret AI verdicts for PSX equities.
allowed-tools: Read, Write, Bash
---

# AI Decision Analysis

## How It Works

The AI analysis pipeline gathers 5 data sources, injects them as ground truth into a structured prompt, and parses the LLM's JSON response into a typed schema.

```
Data Sources → Prompt Builder → Gemini 2.0 Flash → JSON Parser → AIAnalysisResult
```

### Data Sources (all injected as ground truth — AI never invents numbers)

1. **Fundamental Ratios** (from `scripts/ratio_calculator.compare_stock`)
   - PE, EPS values with comparisons vs SECTOR, KSE30, KSE100, ALLSHR medians
   - Deviation % and percentile rank within sector

2. **Benchmark Comparisons** (from `backend/services/compare_service.compare_stock_full`)
   - Multi-context: sector peers → KSE30 → KSE100 → ALLSHR
   - Rank percentile for each metric within sector peers

3. **Technical Evidence** (from `scripts/evidence_signals.generate_signal`)
   - MA crossover status (MA20/MA50/MA200)
   - RSI(14) value + zone (oversold/overbought/neutral)
   - Volume ratio (today vs 30d average)
   - ADX trend strength (if available)

4. **Market Reality Filter** (from `scripts/market_filter.market_reality_filter`)
   - Verdict: PASS (tradable) or FAIL (avoid)
   - Reasons for rejection (liquidity, operator activity, etc.)

5. **Macro Context** (from `backend/services/macro_service.get_current_macro_state`)
   - Regime: RISK_ON / NEUTRAL / RISK_OFF
   - SBP rate, USD/PKR, KSE100 P/E

### Prompt Architecture

The prompt instructs the LLM to act as a CA/ACCA-qualified equity analyst and return **only valid JSON** with no markdown fences or commentary:

```json
{
  "verdict": "BUY|SELL|SHORT_SELL|BUY_BACK|STOP_LOSS|HOLD",
  "confidence": "HIGH|MEDIUM|LOW",
  "time_horizon": "SHORT_TERM|MEDIUM_TERM|LONG_TERM",
  "executive_summary": "2-3 sentence verdict",
  "fundamental_analysis": "paragraph on ratios vs benchmarks",
  "technical_analysis": "paragraph on price action",
  "macro_context": "macro regime impact",
  "risk_factors": ["risk1", "risk2", "risk3"],
  "action_plan": {
    "entry_zone": "price range",
    "stop_loss": "level with %",
    "target_1": "first target",
    "target_2": "second target",
    "position_sizing": "standard|conservative"
  },
  "peer_comparison": "how stock compares to sector peers"
}
```

### Frontend Components

| Component | File | Purpose |
|-----------|------|---------|
| AIReportPanel | `frontend/src/components/AIReportPanel.tsx` | Displays AI verdict card + collapsible sections |
| BenchmarkChart | `frontend/src/components/BenchmarkChart.tsx` | Horizontal bar: stock value vs medians |
| AIScanSummary | `frontend/src/components/AIScanSummary.tsx` | Best bets, red flags, sector rotation |

### API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/analyze/{symbol}` | Single symbol AI analysis |
| POST | `/api/analyze/scan` | Batch AI analysis (max 5 symbols) |
| GET | `/api/benchmarks/{symbol}` | Multi-context comparison data |

### Error Handling

- **Missing API key**: AI service falls back to `build_fallback_response()` using rule-based signal
- **LLM timeout/error**: Returns fallback with `ai_available: false`
- **Invalid JSON response**: `parse_response()` returns None → fallback triggered
- **Cache**: 30-min TTL in-memory dict; invalidated on new scan

### Setup

```bash
# Required: Gemini API key
echo "GEMINI_API_KEY=your-key-here" >> .env

# Required dependency (already in requirements.txt)
pip install google-genai
```

### Verdict Interpretation

| Verdict | Meaning | Action |
|---------|---------|--------|
| BUY | Undervalued + positive technicals + favorable macro | Consider entry in action plan zone |
| SELL | Overvalued + deteriorating technicals | Exit or reduce position |
| SHORT_SELL | Strong sell with downside catalysts | Short entry with tight stop |
| BUY_BACK | Short position should be covered | Close short, take profit |
| STOP_LOSS | Stop loss triggered or imminent danger | Exit immediately |
| HOLD | No clear edge — wait for better setup | No action |
