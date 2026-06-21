#!/usr/bin/env python3
"""E2E test: AI Decision Intelligence pipeline.

Tests full flow: market data → benchmarks → AI analysis → schema validation.

Usage:
    python tests/test_ai_decision_e2e.py              # test all 5 validation symbols
    python tests/test_ai_decision_e2e.py ENGRO        # test single symbol
    python tests/test_ai_decision_e2e.py --batch      # test POST /api/analyze/scan
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.services.compare_service import compare_stock_full
from backend.services.ai_service import build_prompt, parse_response, analyze_symbol, VERDICTS
from scripts.psx_data import get_market_watch

VALIDATION_SYMBOLS = ["ENGRO", "OGDC", "HBL", "LUCK", "SYS"]
PASS = 0
FAIL = 0


def check(description: str, condition: bool):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {description}")
    else:
        FAIL += 1
        print(f"  ❌ {description}")


def test_benchmarks(symbol: str):
    print(f"\n{'='*60}")
    print(f"  BENCHMARKS: {symbol}")
    print(f"{'='*60}")
    mw = get_market_watch()
    result = compare_stock_full(symbol, mw_df=mw)

    check("symbol matches", result.get("symbol") == symbol)
    check("price returned", result.get("price") is not None)
    check("sector identified", result.get("sector") is not None)
    check("has peers list", len(result.get("sector_peers", [])) > 0)

    ratios = result.get("ratios", {})
    check("PE ratio present", "PE" in ratios)
    check("EPS ratio present", "EPS" in ratios)

    for rf in ["PE", "EPS"]:
        r = ratios.get(rf, {})
        check(f"{rf} has value", r.get("value") is not None)
        check(f"{rf} has comparisons", len(r.get("comparisons", {})) >= 4)
        comps = r.get("comparisons", {})
        for idx in ["KSE30", "KSE100", "ALLSHR"]:
            c = comps.get(idx, {})
            check(f"{rf} vs {idx}: has median", c.get("median") is not None)
            check(f"{rf} vs {idx}: has deviation", c.get("deviation_pct") is not None)
        if "SECTOR" in comps:
            check(f"{rf} sector_name present", comps["SECTOR"].get("sector_name") is not None)
        check(f"{rf} percentile_rank present", r.get("percentile_rank") is not None)
        if r.get("percentile_rank") is not None:
            check(f"{rf} percentile_rank in range", 0 <= r["percentile_rank"] <= 100)


def test_ai_analysis(symbol: str):
    print(f"\n{'='*60}")
    print(f"  AI ANALYSIS: {symbol}")
    print(f"{'='*60}")
    result = analyze_symbol(symbol)

    check("symbol matches", result.get("symbol") == symbol)
    check("ai_available flag present", "ai_available" in result)

    if result.get("ai_available"):
        check("verdict is valid", result.get("verdict") in VERDICTS)
        check("confidence is valid", result.get("confidence") in ("HIGH", "MEDIUM", "LOW"))
        check("has executive summary", len(result.get("executive_summary", "")) > 10)
        check("has fundamental analysis", len(result.get("fundamental_analysis", "")) > 10)
        check("has technical analysis", len(result.get("technical_analysis", "")) > 10)
        check("has macro context", len(result.get("macro_context", "")) > 5)
        check("has risk factors", len(result.get("risk_factors", [])) >= 1)
        check("has action plan", result.get("action_plan") is not None)
        if result.get("action_plan"):
            ap = result["action_plan"]
            check("entry_zone set", len(ap.get("entry_zone", "")) > 0)
            check("stop_loss set", len(ap.get("stop_loss", "")) > 0)
        check("has peer comparison", len(result.get("peer_comparison", "")) > 5)
        check("has generated_at", result.get("generated_at") is not None)
    else:
        print("  ⚠ AI unavailable — testing fallback response")
        check("fallback verdict is valid", result.get("verdict") in VERDICTS)
        check("fallback confidence is LOW", result.get("confidence") == "LOW")
        check("fallback ai_available is False", result.get("ai_available") is False)


def test_prompt_builder(symbol: str):
    print(f"\n{'='*60}")
    print(f"  PROMPT BUILD: {symbol}")
    print(f"{'='*60}")
    prompt = build_prompt(symbol)

    check("prompt is non-empty", len(prompt) > 100)
    check("prompt contains symbol", symbol in prompt)
    check("prompt contains verdict instructions", "verdict" in prompt)
    check("prompt contains JSON output spec", "{" in prompt)
    check("prompt contains GROUND TRUTH", "GROUND TRUTH" in prompt)
    check("prompt offers IGNORE verdict", "IGNORE" in prompt)
    check("prompt uses mentor/student voice", "student" in prompt.lower())


def test_parse_response():
    print(f"\n{'='*60}")
    print(f"  RESPONSE PARSER")
    print(f"{'='*60}")

    valid = json.dumps({
        "verdict": "BUY",
        "confidence": "HIGH",
        "time_horizon": "MEDIUM_TERM (3-6 months)",
        "executive_summary": "Strong buy based on undervaluation.",
        "fundamental_analysis": "PE below sector median.",
        "technical_analysis": "RSI bullish.",
        "macro_context": "Favorable macro.",
        "risk_factors": ["Risk 1"],
        "action_plan": {"entry_zone": "100-110", "stop_loss": "95", "target_1": "120", "target_2": "130", "position_sizing": "standard"},
        "peer_comparison": "Cheapest in sector.",
    })
    parsed = parse_response(valid)
    check("valid JSON parses correctly", parsed is not None)
    check("verdict correctly extracted", parsed and parsed["verdict"] == "BUY")

    invalid_verdict = valid.replace("BUY", "MOON")
    parsed2 = parse_response(invalid_verdict)
    check("invalid verdict is rejected", parsed2 is None)

    ignore_verdict = valid.replace('"verdict": "BUY"', '"verdict": "IGNORE"')
    parsed_ignore = parse_response(ignore_verdict)
    check("IGNORE verdict accepted", parsed_ignore is not None and parsed_ignore["verdict"] == "IGNORE")

    with_fences = f"```json\n{valid}\n```"
    parsed3 = parse_response(with_fences)
    check("markdown code fences stripped", parsed3 is not None)

    parsed4 = parse_response("not json at all")
    check("garbage input returns None", parsed4 is None)


def main():
    parser = argparse.ArgumentParser(description="E2E test for AI Decision Intelligence")
    parser.add_argument("symbols", nargs="*", help="Symbols to test (default: all 5 validation symbols)")
    parser.add_argument("--batch", action="store_true", help="Test POST /api/analyze/scan endpoint")
    args = parser.parse_args()

    symbols = [s.upper() for s in args.symbols] if args.symbols else VALIDATION_SYMBOLS

    print(f"\n{'='*60}")
    print(f"  AI DECISION INTELLIGENCE — E2E TEST")
    print(f"  Symbols: {', '.join(symbols)}")
    print(f"{'='*60}")

    # 1. Response parser tests (no external deps)
    test_parse_response()

    # 2. Prompt builder tests (no LLM call)
    for sym in symbols:
        test_prompt_builder(sym)

    # 3. Benchmark comparison tests
    for sym in symbols:
        test_benchmarks(sym)

    # 4. AI analysis tests (may hit Gemini API if key is set)
    for sym in symbols:
        test_ai_analysis(sym)

    # Summary
    print(f"\n{'='*60}")
    print(f"  RESULTS: {PASS} passed, {FAIL} failed")
    print(f"{'='*60}")

    if args.batch:
        print("\n  Testing POST /api/analyze/scan...")
        from backend.routers.analyze import batch_analysis
        from pydantic import BaseModel
        class MockBody:
            symbols = symbols[:3]
            tier = "standard"
        resp = batch_analysis(MockBody())
        check("batch returns results", len(resp.get("results", [])) > 0)
        check("batch returns summary", len(resp.get("summary", "")) > 0)

    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
