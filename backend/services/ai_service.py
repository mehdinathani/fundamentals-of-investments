import os
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.services.compare_service import compare_stock_full
from scripts.psx_data import get_market_watch
from scripts.evidence_signals import generate_signal
from scripts.market_filter import market_reality_filter
from backend.services.macro_service import get_current_macro_state

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

VERDICTS = ["BUY", "SELL", "SHORT_SELL", "BUY_BACK", "STOP_LOSS", "HOLD", "IGNORE"]


def build_prompt(symbol: str, tier: str = "standard") -> str:
    mw = get_market_watch()
    benchmarks = compare_stock_full(symbol, mw_df=mw)
    signal = generate_signal(symbol, tier)
    market_filter = market_reality_filter(symbol, tier)
    macro = get_current_macro_state()
    sector = benchmarks.get("sector", "Unknown")

    ratios_text = ""
    for rf, data in benchmarks.get("ratios", {}).items():
        val = data.get("value")
        comparisons = data.get("comparisons", {})
        ratios_text += f"\n{rf}={val}"
        for idx, comp in comparisons.items():
            dev = comp.get("deviation_pct")
            verdict = comp.get("verdict")
            ratios_text += f" | vs {idx}: {verdict} ({dev:+.1f}%)" if dev else f" | vs {idx}: N/A"

    tech = signal.evidence
    ma = tech.get("ma_crossover", {})
    rsi_data = tech.get("rsi", {})
    vol = tech.get("volume", {})

    return f"""You are a seasoned Pakistan Stock Exchange broker with 30 years on the trading floor, sitting beside a bright but inexperienced finance student. You are mentoring them on {symbol} (Sector: {sector}).

Speak the way a wise old broker actually talks to a student he respects: warm, plain, and direct. Explain WHY, not just what. Whenever you use a technical or accounting term (P/E, MA200, RSI, golden cross, liquidity, etc.), define it in a short phrase right there so the student learns. Never hide behind jargon. Be honest about risk — a good mentor protects the student's capital first.

The verdict and every narrative field must reflect this mentoring voice. Interpret ONLY the ground-truth numbers below — never invent or change a number.

## GROUND TRUTH DATA (do not alter these numbers):

Macro Regime: {macro['state']} | SBP Rate: {macro.get('sbp_rate', 'N/A')}% | USD/PKR: {macro.get('usdpkr', 'N/A')}

### Fundamental Ratios vs Benchmarks:{ratios_text}

### Market Filter: {market_filter.verdict}
Reasons: {'; '.join(market_filter.reasons[:3])}

### Technical Evidence:
- MA20: {ma.get('ma_20', 'N/A')} | MA50: {ma.get('ma_50', 'N/A')} | MA200: {ma.get('ma_200', 'N/A')}
- Crossover: {ma.get('status', 'N/A')}
- Price vs MA200: {'ABOVE' if ma.get('price_above_ma200') else 'BELOW'}
- RSI(14): {rsi_data.get('value', 'N/A')} ({rsi_data.get('zone', 'N/A')})
- Volume: Today={vol.get('today', 'N/A')} | 30d Avg={vol.get('avg_30d', 'N/A')} | Ratio={vol.get('ratio', 'N/A')}x

### Current Signal (rule-based): {signal.signal}{f' ({signal.tier.upper()})' if signal.tier else ''}
Reasons: {'; '.join(signal.reasons[:3])}

## VERDICT GUIDE (pick exactly one):
- BUY / BUY_BACK: strong setup worth the student's capital now.
- SELL / SHORT_SELL / STOP_LOSS: exit or bet against — explain the danger plainly.
- HOLD: own it, but no action today.
- IGNORE: not worth the student's attention — use this when the Market Filter verdict is REJECT (illiquid, manipulated, or operator-driven) or the data is too thin to judge. Tell the student WHY you'd walk away.

## OUTPUT — Return ONLY valid JSON. No markdown, no code fences, no commentary. Write every text field in the mentoring voice described above:
{{"verdict":"BUY|SELL|SHORT_SELL|BUY_BACK|STOP_LOSS|HOLD|IGNORE","confidence":"HIGH|MEDIUM|LOW","time_horizon":"SHORT_TERM (1-4 weeks)|MEDIUM_TERM (1-6 months)|LONG_TERM (6+ months)","executive_summary":"2-3 sentences, plain-language verdict as if telling the student your call and the single biggest reason","fundamental_analysis":"paragraph explaining the ratios vs benchmarks in teaching terms","technical_analysis":"paragraph explaining the chart/trend in teaching terms","macro_context":"1-2 sentences on the wider market mood","risk_factors":["risk1","risk2","risk3"],"action_plan":{{"entry_zone":"...","stop_loss":"...","target_1":"...","target_2":"...","position_sizing":"standard or conservative"}},"peer_comparison":"How {symbol} compares to sector peers, explained simply"}}"""


def call_llm(prompt: str) -> str | None:
    if not GEMINI_API_KEY:
        return None
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={
                "max_output_tokens": 1500,
                "temperature": 0.1,
            },
        )
        return resp.text
    except Exception:
        return None


def parse_response(raw: str) -> dict | None:
    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
            cleaned = cleaned.rsplit("\n```", 1)[0]
        result = json.loads(cleaned)
        if result.get("verdict") not in VERDICTS:
            return None
        return result
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


def build_fallback_response(symbol: str, tier: str = "standard") -> dict:
    signal = generate_signal(symbol, tier)
    return {
        "symbol": symbol,
        "verdict": signal.signal if signal.signal in VERDICTS else "HOLD",
        "confidence": "LOW",
        "time_horizon": "MEDIUM_TERM (1-6 months)",
        "executive_summary": f"AI analysis unavailable. Rule-based signal: {signal.signal}.",
        "fundamental_analysis": "AI analysis unavailable. Review the ratio comparison data via the benchmarks endpoint.",
        "technical_analysis": "; ".join(signal.reasons[:3]),
        "macro_context": "Check macro indicator for current regime.",
        "risk_factors": ["AI analysis unavailable — verify before trading", "Review market filter for liquidity risks"],
        "action_plan": {
            "entry_zone": "Use current market price",
            "stop_loss": f"{signal.evidence.get('stop_loss_pct', 5)}% below entry",
            "target_1": "Not available",
            "target_2": "Not available",
            "position_sizing": tier,
        },
        "peer_comparison": "AI analysis unavailable. Use benchmarks endpoint for peer comparison.",
        "generated_at": None,
        "ai_available": False,
    }


def analyze_symbol(symbol: str, tier: str = "standard") -> dict:
    symbol = symbol.upper()
    prompt = build_prompt(symbol, tier)

    if GEMINI_API_KEY:
        raw = call_llm(prompt)
        if raw:
            parsed = parse_response(raw)
            if parsed:
                parsed["symbol"] = symbol
                parsed["generated_at"] = str(datetime.now())
                parsed["ai_available"] = True
                return parsed

    return build_fallback_response(symbol, tier)
