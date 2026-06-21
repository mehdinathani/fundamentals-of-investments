import sys
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.macros import (
    MA_PERIODS, RSI_PERIOD, RSI_OVERSOLD, RSI_OVERBOUGHT,
    VOLUME_CONFIRMATION_RATIO, RISK_MAX_LOSS_PCT,
    RISK_CONSERVATIVE_LOSS_PCT,
)
from scripts.psx_data import get_market_watch, get_historical_data

@dataclass
class SignalResult:
    symbol: str
    signal: Literal["BUY", "SELL", "HOLD"]
    tier: Literal["strong", "moderate", "weak", None]
    evidence: dict = field(default_factory=dict)
    reasons: list[str] = field(default_factory=list)


def _compute_sma(series, period):
    return series.rolling(window=period).mean()


def _compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta.where(delta < 0, 0.0))
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def generate_signal(symbol, capital_tier="standard"):
    hist = get_historical_data(symbol)
    if hist.empty or len(hist) < 210:
        return SignalResult(
            symbol, "HOLD", None,
            {"error": "Insufficient historical data"},
            [f"Need ≥210 trading days, got {len(hist)}"]
        )

    close = hist["CLOSE"].values
    volume = hist["VOLUME"].values
    close_series = hist["CLOSE"]
    volume_series = hist["VOLUME"].astype(float)

    ma_20 = _compute_sma(close_series, MA_PERIODS["fast"])
    ma_50 = _compute_sma(close_series, MA_PERIODS["medium"])
    ma_200 = _compute_sma(close_series, MA_PERIODS["slow"])
    rsi_14 = _compute_rsi(close_series, RSI_PERIOD)

    latest = {
        "price": float(close[-1]),
        "ma_20": float(ma_20.iloc[-1]) if not pd.isna(ma_20.iloc[-1]) else None,
        "ma_50": float(ma_50.iloc[-1]) if not pd.isna(ma_50.iloc[-1]) else None,
        "ma_200": float(ma_200.iloc[-1]) if not pd.isna(ma_200.iloc[-1]) else None,
        "rsi_14": float(rsi_14.iloc[-1]) if not pd.isna(rsi_14.iloc[-1]) else None,
    }

    ma_20_prev = float(ma_20.iloc[-2]) if len(ma_20) >= 2 and not pd.isna(ma_20.iloc[-2]) else None
    ma_50_prev = float(ma_50.iloc[-2]) if len(ma_50) >= 2 and not pd.isna(ma_50.iloc[-2]) else None

    vol_30d_avg = float(volume_series.tail(30).mean())
    vol_today = float(volume[-1])
    vol_ratio = vol_today / vol_30d_avg if vol_30d_avg > 0 else 0.0

    ma_cross_status = "no_cross"
    if latest["ma_20"] is not None and latest["ma_50"] is not None:
        if latest["ma_20"] > latest["ma_50"] and (ma_20_prev is None or ma_20_prev <= ma_50_prev):
            ma_cross_status = "golden_cross"
        elif latest["ma_20"] < latest["ma_50"] and (ma_20_prev is None or ma_20_prev >= ma_50_prev):
            ma_cross_status = "death_cross"
        elif latest["ma_20"] > latest["ma_50"]:
            ma_cross_status = "above_50"
        else:
            ma_cross_status = "below_50"

    price_above_ma200 = (latest["price"] > latest["ma_200"]) if latest["ma_200"] is not None else False

    rsi_value = latest["rsi_14"]
    rsi_zone = "unknown"
    if rsi_value is not None:
        if rsi_value < RSI_OVERSOLD:
            rsi_zone = "oversold"
        elif rsi_value > RSI_OVERBOUGHT:
            rsi_zone = "overbought"
        elif 40 <= rsi_value <= 60:
            rsi_zone = "neutral"
        elif rsi_value < 40:
            rsi_zone = "bearish"
        else:
            rsi_zone = "bullish"

    max_loss = RISK_CONSERVATIVE_LOSS_PCT if capital_tier == "conservative" else RISK_MAX_LOSS_PCT

    evidence = {
        "ma_crossover": {
            "status": ma_cross_status,
            "ma_20": round(latest["ma_20"], 2) if latest["ma_20"] else None,
            "ma_50": round(latest["ma_50"], 2) if latest["ma_50"] else None,
            "ma_200": round(latest["ma_200"], 2) if latest["ma_200"] else None,
            "price_above_ma200": price_above_ma200,
        },
        "rsi": {
            "value": round(rsi_value, 2) if rsi_value else None,
            "zone": rsi_zone,
        },
        "volume": {
            "today": int(vol_today),
            "avg_30d": int(vol_30d_avg),
            "ratio": round(vol_ratio, 2),
        },
        "price": round(latest["price"], 2),
        "stop_loss_pct": max_loss,
    }

    reasons = []
    signal = "HOLD"
    tier = None

    if latest["ma_20"] is not None and latest["ma_50"] is not None:
        reasons.append(f"MA20={latest['ma_20']:.2f}, MA50={latest['ma_50']:.2f}: {ma_cross_status}")

    if rsi_value is not None:
        reasons.append(f"RSI(14)={rsi_value:.1f}: {rsi_zone} zone")

    reasons.append(f"Volume: {vol_today:,.0f} vs 30d avg {vol_30d_avg:,.0f} ({vol_ratio:.1f}×)")

    buy_conditions = (
        latest["ma_20"] is not None and latest["ma_50"] is not None
        and latest["ma_200"] is not None
        and ma_cross_status == "golden_cross"
        and price_above_ma200
        and rsi_value is not None and RSI_OVERSOLD <= rsi_value <= 60
        and vol_ratio >= VOLUME_CONFIRMATION_RATIO
    )

    sell_conditions = (
        ma_cross_status == "death_cross"
        or (latest["ma_200"] is not None
            and latest["price"] < latest["ma_200"]
            and len(hist) >= 3
            and all(close[-i] < (latest["ma_200"] or 0)
                    for i in range(1, 4) if len(close) > i))
    )

    if sell_conditions:
        signal = "SELL"
        reasons.append("Signal: SELL (death cross or price below MA200 3 days)")
        evidence["sell_reason"] = "death_cross" if ma_cross_status == "death_cross" else "below_ma200"
    elif buy_conditions:
        signal = "BUY"
        vol_strength = "strong" if vol_ratio >= 1.5 else "moderate"
        rsi_strength = "strong" if 40 <= (rsi_value or 0) <= 55 else "moderate"
        if vol_strength == "strong" and rsi_strength == "strong":
            tier = "strong"
        elif vol_strength == "moderate" and rsi_strength == "moderate":
            tier = "weak"
        else:
            tier = "moderate"
        reasons.append(f"Signal: {tier.upper()} BUY (golden cross + MA200 uptrend + RSI neutral + volume confirmed)")
        evidence["buy_tier"] = tier
    else:
        reasons.append("Signal: HOLD (conditions not met)")
        evidence["hold_reason"] = _get_hold_reason(
            ma_cross_status, price_above_ma200, rsi_value, vol_ratio
        )

    evidence["reasons"] = reasons
    return SignalResult(symbol, signal, tier, evidence, reasons)


def _get_hold_reason(ma_status, above_ma200, rsi, vol_ratio):
    parts = []
    if ma_status != "golden_cross":
        parts.append(f"MA: {ma_status}")
    if not above_ma200:
        parts.append("Below MA200")
    if rsi is not None and (rsi < 30 or rsi > 70):
        parts.append(f"RSI extreme ({rsi:.0f})")
    if vol_ratio < VOLUME_CONFIRMATION_RATIO:
        parts.append(f"Low volume ({vol_ratio:.1f}×)")
    return "; ".join(parts) or "No conditions met"


def print_signal(result: SignalResult):
    verdict_color = "🟢" if result.signal == "BUY" else \
                    "🔴" if result.signal == "SELL" else "🟡"
    tier_str = f" ({result.tier.upper()})" if result.tier else ""
    print(f"\n{'='*60}")
    print(f"  {verdict_color} {result.symbol}: {result.signal}{tier_str}")
    print(f"{'='*60}")

    ev = result.evidence
    ma = ev.get("ma_crossover", {})
    rsi = ev.get("rsi", {})
    vol = ev.get("volume", {})

    print(f"\n  📊 Moving Averages")
    print(f"     MA20:        {ma.get('ma_20', 'N/A')}")
    print(f"     MA50:        {ma.get('ma_50', 'N/A')}")
    print(f"     MA200:       {ma.get('ma_200', 'N/A')}")
    print(f"     Crossover:   {ma.get('status', 'N/A')}")
    print(f"     Price vs MA200: {'ABOVE ✅' if ma.get('price_above_ma200') else 'BELOW ❌'}")

    print(f"\n  📈 RSI(14)")
    print(f"     Value:       {rsi.get('value', 'N/A')}")
    print(f"     Zone:        {rsi.get('zone', 'N/A')}")

    print(f"\n  📉 Volume")
    print(f"     Today:       {vol.get('today', 'N/A'):,}")
    print(f"     30d avg:     {vol.get('avg_30d', 'N/A'):,}")
    print(f"     Ratio:       {vol.get('ratio', 'N/A'):.2f}×")

    print(f"\n  📝 Reasoning")
    for r in result.reasons:
        print(f"     → {r}")


if __name__ == "__main__":
    import argparse
    from scripts.macros import VALIDATION_SYMBOLS
    parser = argparse.ArgumentParser(description="Generate evidence-backed trading signals")
    parser.add_argument("--symbol", type=str, help="Single symbol")
    parser.add_argument("--all", action="store_true", help="All validation symbols")
    parser.add_argument("--conservative", action="store_true", help="Conservative tier")
    args = parser.parse_args()
    symbols = []
    if args.symbol:
        symbols = [args.symbol.upper()]
    elif args.all:
        symbols = VALIDATION_SYMBOLS
    else:
        parser.print_help()
        sys.exit(1)
    tier = "conservative" if args.conservative else "standard"
    for sym in symbols:
        result = generate_signal(sym, tier)
        print_signal(result)
