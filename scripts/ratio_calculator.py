import sys
import pandas as pd
from pathlib import Path
from datetime import datetime, date

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.macros import (
    BENCHMARKS_DIR, RATIO_FIELDS, RATIO_DESCRIPTIONS,
    VALIDATION_SYMBOLS, STALE_DATA_DAYS,
)
from scripts.category_benchmarks import (
    compute_ratios_for_symbol, load_benchmarks,
)
from scripts.psx_data import get_market_watch

BENCHMARKS_DIR.mkdir(parents=True, exist_ok=True)

def load_benchmark_paths():
    b = load_benchmarks()
    return {
        "KSE30": b.get("KSE30", {}),
        "KSE100": b.get("KSE100", {}),
        "ALLSHR": b.get("ALLSHR", {}),
    }

def get_benchmark_age_days():
    from scripts.macros import KSE30_PATH, KSE100_PATH, ALLSHR_PATH
    paths = [KSE30_PATH, KSE100_PATH, ALLSHR_PATH]
    ages = []
    for p in paths:
        if p.exists():
            mtime = datetime.fromtimestamp(p.stat().st_mtime).date()
            ages.append((date.today() - mtime).days)
    return min(ages) if ages else 999

def compare_stock(symbol, price=None, mw_df=None):
    if mw_df is None:
        mw_df = get_market_watch()
    ratios = compute_ratios_for_symbol(symbol, mw_df)
    benchmarks = load_benchmark_paths()
    result = {
        "symbol": symbol,
        "price": ratios.get("PRICE"),
        "ratios": {},
    }
    for ratio_field in RATIO_FIELDS:
        stock_val = ratios.get(ratio_field)
        comparisons = {}
        for idx_name in ["KSE30", "KSE100", "ALLSHR"]:
            median = benchmarks[idx_name].get(ratio_field)
            comp = {"median": median, "deviation_pct": None, "verdict": None}
            if stock_val is not None and median is not None and median > 0:
                deviation = ((stock_val - median) / median) * 100
                comp["deviation_pct"] = round(deviation, 1)
                comp["verdict"] = "ABOVE median" if stock_val > median else "BELOW median"
            comparisons[idx_name] = comp
        result["ratios"][ratio_field] = {
            "value": stock_val,
            "name": RATIO_DESCRIPTIONS.get(ratio_field, ratio_field),
            "comparisons": comparisons,
        }
    return result

def print_comparison(result):
    sym = result["symbol"]
    price = result.get("price", "N/A")
    print(f"\n{'='*60}")
    print(f"  {sym} — Price: PKR {price}")
    print(f"{'='*60}")
    age = get_benchmark_age_days()
    if age > STALE_DATA_DAYS:
        print(f"  ⚠ STALE DATA: Benchmarks are {age} days old (max {STALE_DATA_DAYS})")
    print()
    for ratio_field, data in result["ratios"].items():
        val = data.get("value")
        name = data.get("name", ratio_field)
        val_str = f"{val:.2f}" if val is not None else "N/A"
        print(f"  {name}: {val_str}")
        print(f"  {'─'*50}")
        for idx_name, comp in data["comparisons"].items():
            median = comp.get("median")
            dev = comp.get("deviation_pct")
            verdict = comp.get("verdict")
            if median is not None:
                median_str = f"{median:.2f}"
                dev_str = f"{dev:+.1f}%" if dev is not None else "N/A"
                verdict_str = verdict or "N/A"
                print(f"    vs {idx_name:<8} median={median_str:<10} dev={dev_str:<10} {verdict_str}")
            else:
                print(f"    vs {idx_name:<8} median=N/A")
        print()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Compare stock ratios against category benchmarks")
    parser.add_argument("--symbol", type=str, help="Single symbol to analyze")
    parser.add_argument("--all", action="store_true", help="Run for all validation symbols")
    args = parser.parse_args()
    symbols = []
    if args.symbol:
        symbols = [args.symbol.upper()]
    elif args.all:
        symbols = VALIDATION_SYMBOLS
    else:
        parser.print_help()
        sys.exit(1)
    print("Loading market watch data...")
    mw = get_market_watch()
    for sym in symbols:
        result = compare_stock(sym, mw_df=mw)
        print_comparison(result)
