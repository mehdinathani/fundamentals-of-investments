import sys
import json
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.macros import SECTOR_CODES, BENCHMARKS_DIR
from scripts.psx_data import get_market_watch
from scripts.category_benchmarks import compute_ratios_for_symbol

CACHE_PATH = BENCHMARKS_DIR / "sector_medians.json"


def compute_all_sector_medians():
    print("Loading market watch...")
    mw_df = get_market_watch()
    print(f"  {len(mw_df)} stocks loaded")

    result = {}
    for sector, symbols in SECTOR_CODES.items():
        if not symbols:
            continue
        print(f"\n{sector} ({len(symbols)} symbols)...")
        pe_vals = []
        eps_vals = []
        for sym in symbols:
            ratios = compute_ratios_for_symbol(sym, mw_df)
            pe = ratios.get("PE")
            eps = ratios.get("EPS")
            status = f"{sym}: PE={pe}, EPS={eps}" if pe else f"{sym}: no data"
            print(f"  {status}")
            if pe is not None:
                pe_vals.append(pe)
            if eps is not None:
                eps_vals.append(eps)

        result[sector] = {
            "symbols_in_sector": len(symbols),
            "PE_median": round(pd.Series(pe_vals).median(), 2) if pe_vals else None,
            "PE_count": len(pe_vals),
            "EPS_median": round(pd.Series(eps_vals).median(), 2) if eps_vals else None,
            "EPS_count": len(eps_vals),
        }
        print(f"  → PE median: {result[sector]['PE_median']} (n={len(pe_vals)})")

    BENCHMARKS_DIR.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved to {CACHE_PATH}")
    return result


if __name__ == "__main__":
    compute_all_sector_medians()
