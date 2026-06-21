import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.psx_data import get_market_watch, get_historical_data
from scripts.macros import MA_PERIODS, RSI_PERIOD

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

SPARKLINE_CHARS = "▁▂▃▄▅▆▇█"

_SECTOR_NAME_CACHE = {}
_SECTOR_CACHE_PATH = Path(__file__).resolve().parent.parent / "data" / "sector_codes.json"

def _load_sector_cache():
    global _SECTOR_NAME_CACHE
    if _SECTOR_NAME_CACHE:
        return
    if _SECTOR_CACHE_PATH.exists():
        import json
        with open(_SECTOR_CACHE_PATH) as f:
            _SECTOR_NAME_CACHE = json.load(f)

def _get_sector_name(sector_code, mw_df=None):
    _load_sector_cache()
    return _SECTOR_NAME_CACHE.get(sector_code, sector_code)

def _normalize(val, min_v, max_v):
    if max_v == min_v:
        return 0
    return (val - min_v) / (max_v - min_v)

def sparkline(values, width=20):
    if not values:
        return ""
    arr = np.array(values, dtype=float)
    min_v, max_v = np.nanmin(arr), np.nanmax(arr)
    if max_v == min_v or np.isnan(min_v):
        return " " * width
    indices = np.linspace(0, len(arr) - 1, width, dtype=int)
    sampled = arr[indices]
    normalized = (sampled - min_v) / (max_v - min_v) if max_v > min_v else np.zeros(width)
    idxs = np.clip(np.floor(normalized * 7).astype(int), 0, 7)
    return "".join(SPARKLINE_CHARS[i] for i in idxs)

def sector_heatmap(mw_df=None):
    if mw_df is None:
        mw_df = get_market_watch()
    sector_groups = mw_df.groupby("SECTOR").agg(
        count=("SYMBOL", "count"),
        avg_change=("CHANGE (%)", "mean"),
        total_volume=("VOLUME", "sum"),
    ).sort_values("avg_change", ascending=False)
    print(f"\n{BOLD}SECTOR HEATMAP — Today's Performance{RESET}")
    print(f"{'Sector':<40} {'Chg%':<10} {'Stocks':<8} {'Bar':<25}")
    print("-" * 80)
    for code, row in sector_groups.iterrows():
        name = _get_sector_name(code)
        chg = row["avg_change"]
        color = GREEN if chg > 0 else RED if chg < 0 else YELLOW
        bar_len = max(1, min(20, int(abs(chg) * 2)))
        bar = "▓" * bar_len
        print(f"  {name:<38} {color}{chg:>+7.2f}%{RESET}  {int(row['count']):<8} {color}{bar}{RESET}")
    print()

def trade_bar(symbol, signal=None, width=60):
    hist = get_historical_data(symbol)
    if hist.empty or len(hist) < 50:
        print(f"No historical data for {symbol}")
        return
    close = hist["CLOSE"].values
    volume = hist["VOLUME"].values
    dates = hist["DATE"].values
    close_series = hist["CLOSE"]
    volume_series = hist["VOLUME"].astype(float)
    ma_20 = close_series.rolling(MA_PERIODS["fast"]).mean().values
    ma_50 = close_series.rolling(MA_PERIODS["medium"]).mean().values
    last_60 = min(width, len(close))
    idx_start = len(close) - last_60
    c = close[idx_start:]
    m20 = ma_20[idx_start:]
    m50 = ma_50[idx_start:]
    v = volume[idx_start:]
    d = dates[idx_start:]
    price_min, price_max = np.nanmin(c), np.nanmax(c)
    vol_max = np.nanmax(v) if np.nanmax(v) > 0 else 1
    def scale(val, mn, mx, steps=8):
        if mx == mn or pd.isna(val) or np.isnan(float(val)):
            return steps // 2
        idx = int((float(val) - mn) / (mx - mn) * (steps - 1))
        return max(0, min(steps - 1, idx))
    print(f"\n{BOLD}TRADE BAR — {symbol} (last {last_60} days){RESET}")
    print(f"  Price range: {price_min:.2f} — {price_max:.2f}")
    print()
    for row in range(3):
        line = "  "
        for i in range(len(c)):
            if row == 0:
                level = scale(c[i], price_min, price_max)
                ch = SPARKLINE_CHARS[level]
                if not pd.isna(m20[i]) and not np.isnan(float(m20[i])) and abs(c[i] - m20[i]) < 0.01:
                    ch = "●"
            elif row == 1:
                if not pd.isna(m20[i]) and not np.isnan(float(m20[i])):
                    level = scale(m20[i], price_min, price_max)
                    ch = SPARKLINE_CHARS[level]
                else:
                    ch = " "
            else:
                if not pd.isna(m50[i]) and not np.isnan(float(m50[i])):
                    level = scale(m50[i], price_min, price_max)
                    ch = SPARKLINE_CHARS[level]
                else:
                    ch = " "
            line += ch
        labels = ["Price", "MA20 ", "MA50 "]
        print(f"{labels[row]}{line}")
    vol_chars = " ▁▂▃▄▅▆▇█"
    vol_line = "  Vol "
    for i in range(len(v)):
        if pd.isna(v[i]) or np.isnan(float(v[i])):
            vol_line += " "
        else:
            idx = int(float(v[i]) / vol_max * 7) if vol_max > 0 else 0
            vol_line += vol_chars[min(idx, 7)]
    print(f"{vol_line}")
    if signal:
        sig_idx = min(len(c) - 1, last_60 - 1)
        marker_line = "       " + " " * sig_idx
        if signal == "BUY":
            marker_line += "🟢"
        elif signal == "SELL":
            marker_line += "🔴"
        else:
            marker_line += "🟡"
        print(f"{marker_line}  {signal}")
    print(f"  {'─' * last_60}")
    step = max(1, last_60 // 5)
    ticks = ""
    for i in range(0, last_60, step):
        ticks += f"{pd.Timestamp(d[i]).strftime('%m/%d'):<{step + 3}}"
    print(f"       {ticks}")
    print()

def print_decision_sheet_header(capital_tier="standard"):
    now = datetime.now()
    print(f"\n{'='*60}")
    print(f"{BOLD}  PSX DAILY SCAN{RESET} — {now.strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    print(f"  Mode: dry-run | Capital tier: {capital_tier}")
    print(f"  Data: DPS portal (≈5 min delayed)")
    print()

if __name__ == "__main__":
    import argparse
    from scripts.macros import VALIDATION_SYMBOLS
    parser = argparse.ArgumentParser(description="Generate ASCII heatmaps and trade bars")
    parser.add_argument("--heatmap", action="store_true", help="Show sector heatmap")
    parser.add_argument("--trade-bar", type=str, help="Show trade bar for symbol")
    parser.add_argument("--all", action="store_true", help="Show trade bars for all validation symbols")
    args = parser.parse_args()
    if args.heatmap:
        mw = get_market_watch()
        sector_heatmap(mw)
    if args.trade_bar:
        trade_bar(args.trade_bar.upper())
    if args.all:
        mw = get_market_watch()
        sector_heatmap(mw)
        for sym in VALIDATION_SYMBOLS:
            trade_bar(sym)
