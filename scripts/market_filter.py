import sys
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.macros import (
    LIQUIDITY_MIN_DAILY_VOLUME, LIQUIDITY_MIN_DAILY_VALUE_PKR,
    LIQUIDITY_MIN_FREEFLOAT_PCT, LIQUIDITY_MIN_TRADED_DAYS,
    SPREAD_MAX_PCT, OPERATOR_PRICE_MOVE_PCT, OPERATOR_VOLUME_RATIO,
    VOLUME_SPIKE_CAUTION, VOLUME_SPIKE_REJECT,
    CIRCUIT_BREAKER_WINDOW, CIRCUIT_BREAKER_HITS,
    RISK_CONSERVATIVE_LOSS_PCT,
)
from scripts.psx_data import get_market_watch, get_historical_data

@dataclass
class FilterResult:
    symbol: str
    verdict: Literal["TRADABLE", "REJECT", "CAUTION"]
    failed_filter: str | None
    reasons: list[str] = field(default_factory=list)


def _get_30d_avg_volume(symbol):
    hist = get_historical_data(symbol)
    if hist.empty or len(hist) < 30:
        return None
    last_30 = hist.tail(30)
    return last_30["VOLUME"].mean()


def _get_30d_avg_value(today_close, avg_volume):
    return today_close * avg_volume


def _get_days_traded(symbol):
    hist = get_historical_data(symbol)
    if hist.empty:
        return 0
    last_30 = hist.tail(30)
    return len(last_30)


def market_reality_filter(symbol, capital_tier="standard"):
    reasons = []
    mw = get_market_watch()
    row = mw[mw["SYMBOL"] == symbol]
    if row.empty:
        for mw_sym in mw["SYMBOL"].tolist():
            if mw_sym.startswith(symbol):
                row = mw[mw["SYMBOL"] == mw_sym]
                break
    if row.empty:
        mw_sym = _lookup_symbol(symbol, mw)
        if mw_sym:
            row = mw[mw["SYMBOL"] == mw_sym]
    if row.empty:
        return FilterResult(symbol, "REJECT", "no_market_data",
                            ["Symbol not found in market watch"])

    r = row.iloc[0]
    current_price = r.get("CURRENT") or r.get("LDCP")
    if pd.isna(current_price):
        return FilterResult(symbol, "REJECT", "no_price",
                            ["No current price available"])
    current_price = float(current_price)

    today_volume_str = r.get("VOLUME", 0)
    today_volume = float(today_volume_str) if pd.notna(today_volume_str) else 0

    vol_floor = LIQUIDITY_MIN_DAILY_VOLUME * 2 if capital_tier == "conservative" else LIQUIDITY_MIN_DAILY_VOLUME
    val_floor = LIQUIDITY_MIN_DAILY_VALUE_PKR * 2 if capital_tier == "conservative" else LIQUIDITY_MIN_DAILY_VALUE_PKR

    avg_volume = _get_30d_avg_volume(symbol)
    days_traded = _get_days_traded(symbol)

    if avg_volume is not None:
        avg_value = _get_30d_avg_value(current_price, avg_volume)
    else:
        avg_value = None

    if avg_volume is not None and avg_volume < vol_floor:
        return FilterResult(symbol, "REJECT", "liquidity_volume",
                            [f"30d avg volume {avg_volume:,.0f} < {vol_floor:,.0f}"])

    if avg_value is not None and avg_value < val_floor:
        return FilterResult(symbol, "REJECT", "liquidity_value",
                            [f"30d avg value PKR {avg_value:,.0f} < PKR {val_floor:,.0f}"])

    if days_traded < LIQUIDITY_MIN_TRADED_DAYS:
        return FilterResult(symbol, "REJECT", "stale",
                            [f"Traded {days_traded} of last 30 days < {LIQUIDITY_MIN_TRADED_DAYS}"])

    change_pct = r.get("CHANGE (%)", 0)
    change_pct = float(change_pct) if pd.notna(change_pct) else 0
    move_pct = abs(change_pct) / 100.0
    vol_ratio = (today_volume / avg_volume) if (avg_volume and avg_volume > 0) else 0

    if move_pct > (OPERATOR_PRICE_MOVE_PCT / 100.0) and vol_ratio < OPERATOR_VOLUME_RATIO:
        return FilterResult(symbol, "REJECT", "operator",
                            [f"Price move {move_pct:.1%} on volume ratio {vol_ratio:.2f} (operator pattern)"])

    if vol_ratio > VOLUME_SPIKE_REJECT:
        return FilterResult(symbol, "REJECT", "volume_spike",
                            [f"Volume {vol_ratio:.1f}× avg — possible manipulation"])
    if vol_ratio > VOLUME_SPIKE_CAUTION:
        reasons.append(f"Caution: volume {vol_ratio:.1f}× avg — check news")

    verdict = "CAUTION" if reasons else "TRADABLE"
    return FilterResult(symbol, verdict, None, reasons)


def filter_universe(symbols, capital_tier="standard"):
    results = []
    for sym in symbols:
        result = market_reality_filter(sym, capital_tier)
        results.append(result)
    return results


def _lookup_symbol(symbol, mw_df):
    for mw_sym in mw_df["SYMBOL"].tolist():
        if mw_sym.startswith(symbol):
            return mw_sym
    return None


if __name__ == "__main__":
    import argparse
    from scripts.macros import VALIDATION_SYMBOLS
    parser = argparse.ArgumentParser(description="Layer 0 Market Reality Filter")
    parser.add_argument("--symbol", type=str, help="Single symbol to filter")
    parser.add_argument("--all", action="store_true", help="Run for all validation symbols")
    parser.add_argument("--conservative", action="store_true", help="Conservative capital tier")
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
        result = market_reality_filter(sym, tier)
        status = "✅ TRADABLE" if result.verdict == "TRADABLE" else \
                 "⚠️ CAUTION" if result.verdict == "CAUTION" else "❌ REJECT"
        print(f"{result.symbol}: {status}")
        for reason in result.reasons:
            print(f"  → {reason}")
