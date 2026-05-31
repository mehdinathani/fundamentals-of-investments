"""Signal generation service — wraps trade-rules-engine logic."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pathlib import Path
from datetime import date, datetime
from typing import Optional
import pandas as pd
import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "historical"

# Config matching Iteration 8 (best all-round performer)
CONFIG = {
    "adx_threshold": 20,
    "volume_min_ratio": 1.2,
    "stop_loss": 0.05,
    "trailing_activate": 1.10,
    "trailing_stop": 0.92,
}


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    for p in [20, 50, 200]:
        d[f"MA{p}"] = d["CLOSE"].rolling(p).mean()

    delta = d["CLOSE"].diff()
    g = delta.where(delta > 0, 0.0)
    l = (-delta).where(delta < 0, 0.0)
    rs = g.rolling(14).mean() / l.rolling(14).mean().replace(0, np.nan)
    d["RSI"] = 100 - (100 / (1 + rs))

    d["VOL_MA"] = d["VOLUME"].rolling(30).mean()
    d["VOL_RATIO"] = d["VOLUME"] / d["VOL_MA"].replace(0, np.nan)
    d["HIGH_20D"] = d["HIGH"].rolling(20).max()
    d["BREAKOUT"] = d["CLOSE"] > d["HIGH_20D"].shift(1)

    d["TR"] = pd.concat([
        abs(d["HIGH"] - d["LOW"]),
        abs(d["HIGH"] - d["CLOSE"].shift(1)),
        abs(d["LOW"] - d["CLOSE"].shift(1)),
    ], axis=1).max(axis=1)
    d["ATR"] = d["TR"].rolling(14).mean()
    d["UP"] = d["HIGH"] - d["HIGH"].shift(1)
    d["DOWN"] = d["LOW"].shift(1) - d["LOW"]
    d["PDM"] = np.where((d["UP"] > d["DOWN"]) & (d["UP"] > 0), d["UP"], 0)
    d["MDM"] = np.where((d["DOWN"] > d["UP"]) & (d["DOWN"] > 0), d["DOWN"], 0)
    d["PDI"] = 100 * d["PDM"].ewm(span=14, adjust=False).mean() / d["ATR"].replace(0, np.nan)
    d["MDI"] = 100 * d["MDM"].ewm(span=14, adjust=False).mean() / d["ATR"].replace(0, np.nan)
    dx = 100 * abs(d["PDI"] - d["MDI"]) / (d["PDI"] + d["MDI"]).replace(0, np.nan)
    d["ADX"] = dx.ewm(span=14, adjust=False).mean()
    return d


def check_buy(row: pd.Series) -> tuple[Optional[str], Optional[str]]:
    if pd.isna(row.get("MA200")) or pd.isna(row.get("RSI")):
        return None, None
    if not row.get("BREAKOUT", False):
        return None, None
    if row["CLOSE"] <= row["MA200"]:
        return None, None
    adx_v = row.get("ADX", np.nan)
    if pd.notna(adx_v) and adx_v < CONFIG["adx_threshold"]:
        return None, None
    if row["RSI"] >= 70:
        return None, None
    if row["VOL_RATIO"] < CONFIG["volume_min_ratio"]:
        return None, None
    if row["VOL_RATIO"] >= 1.5 and 50 <= row["RSI"] <= 60:
        return "BUY", "Tier 1 (Strong)"
    if 50 <= row["RSI"] <= 65:
        return "BUY", "Tier 2 (Moderate)"
    return None, None


def scan_symbol(symbol: str, macro_state: str = "RISK_ON") -> Optional[dict]:
    path = DATA_DIR / f"{symbol}.parquet"
    if not path.exists():
        return None
    df = pd.read_parquet(path)
    df["DATE"] = pd.to_datetime(df["DATE"])
    df = df.sort_values("DATE").reset_index(drop=True)
    for col in ["OPEN", "HIGH", "LOW", "CLOSE"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["VOLUME"] = pd.to_numeric(df["VOLUME"], errors="coerce")

    df = compute_indicators(df)
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else None

    sig_type, sig_strength = check_buy(latest)

    result = {
        "symbol": symbol,
        "current_price": float(latest["CLOSE"]) if pd.notna(latest["CLOSE"]) else None,
        "prev_close": float(prev["CLOSE"]) if prev is not None and pd.notna(prev["CLOSE"]) else None,
        "ma20": float(latest["MA20"]) if pd.notna(latest.get("MA20")) else None,
        "ma50": float(latest["MA50"]) if pd.notna(latest.get("MA50")) else None,
        "ma200": float(latest["MA200"]) if pd.notna(latest.get("MA200")) else None,
        "rsi": float(latest["RSI"]) if pd.notna(latest["RSI"]) else None,
        "volume_ratio": float(latest["VOL_RATIO"]) if pd.notna(latest["VOL_RATIO"]) else None,
        "adx": float(latest["ADX"]) if pd.notna(latest.get("ADX")) else None,
        "breakout": bool(latest.get("BREAKOUT", False)),
        "signal": sig_type,
        "signal_strength": sig_strength,
        "macro_state": macro_state,
        "date": latest["DATE"].date() if hasattr(latest["DATE"], "date") else latest["DATE"],
    }

    # Calculate daily change
    if result["current_price"] and result["prev_close"] and result["prev_close"] > 0:
        result["change_pct"] = (result["current_price"] - result["prev_close"]) / result["prev_close"] * 100
    else:
        result["change_pct"] = 0

    return result


def scan_all_symbols(macro_state: str = "RISK_ON") -> list[dict]:
    results = []
    for path in sorted(DATA_DIR.glob("*.parquet")):
        result = scan_symbol(path.stem, macro_state)
        if result:
            results.append(result)
    return results
