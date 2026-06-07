import sys
import pandas as pd
import time
import random
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.macros import (
    BENCHMARKS_DIR, KSE30_PATH, KSE100_PATH, ALLSHR_PATH,
    RATIO_FIELDS, RATIO_DESCRIPTIONS, STALE_DATA_DAYS,
)
from scripts.psx_data import (
    get_market_watch, get_company_info, _request,
    DPS_BASE_URL, DPS_HEADERS,
)

BENCHMARKS_DIR.mkdir(parents=True, exist_ok=True)

INDEX_CONSTITUENTS = {
    "KSE30": [
        "ENGRO", "LUCK", "HBL", "OGDC", "MCB", "UBL", "PPL", "HUBC", "MARI",
        "POL", "EFERT", "FFBL", "NESTLE", "SEARL", "SYS", "PSO", "MEBL",
        "BAHL", "INDU", "LOTCHEM", "EPCL", "ASTL", "CHCC", "KEL", "NCPL",
        "PNSC", "AICL", "MTL", "GATI", "KOHC",
    ],
    "KSE100": [
        "ENGRO", "LUCK", "HBL", "OGDC", "MCB", "UBL", "PPL", "HUBC", "SYS",
        "MARI", "ABOT", "NML", "DGKC", "KAPCO", "POL", "FCCL", "EFERT",
        "FFBL", "NESTLE", "SEARL", "SHEL", "PSO", "MEBL", "BAHL", "BAFL",
        "FABL", "HMB", "NBP", "SCBPL", "INDU", "GLAXO", "AGP", "HINOON",
        "BIFO", "COLG", "LOTCHEM", "EPCL", "ICI", "ASTL", "MUGHAL",
        "CHCC", "POWER", "PKGS", "KEL", "PNSC", "PIBTL", "AICL", "THEM",
        "HASCOL", "PIOC", "NCPL", "ATIL", "KOHC", "MTL", "GATI", "WTL",
    ],
}

def _get_eps_from_company_page(symbol):
    """Scrape EPS (and profit) from the DPS company page."""
    url = f"{DPS_BASE_URL}/company/{symbol}"
    try:
        resp = _request("GET", url)
        soup = BeautifulSoup(resp.text, "html.parser")
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                labels = [c.get_text(strip=True) for c in cells]
                if labels and labels[0] == "EPS" and len(labels) >= 2:
                    vals = labels[1:]
                    numeric = []
                    for v in vals:
                        v = v.replace(",", "").strip()
                        try:
                            numeric.append(float(v))
                        except ValueError:
                            numeric.append(None)
                    numeric = [x for x in numeric if x is not None]
                    if numeric:
                        return {"eps": numeric[0]}
        return {}
    except Exception:
        return {}

def _lookup_symbol_in_mw(symbol, mw_df):
    mw_symbols = mw_df["SYMBOL"].tolist()
    if symbol in mw_symbols:
        return symbol
    for mw_sym in mw_symbols:
        if mw_sym.startswith(symbol):
            return mw_sym
    return None

def _get_current_price(symbol, mw_df):
    mw_sym = _lookup_symbol_in_mw(symbol, mw_df)
    if mw_sym is None:
        return None
    row = mw_df[mw_df["SYMBOL"] == mw_sym]
    if not row.empty:
        price = row.iloc[0].get("CURRENT") or row.iloc[0].get("LDCP")
        if pd.notna(price):
            return float(price)
    return None

def compute_ratios_for_symbol(symbol, mw_df):
    price = _get_current_price(symbol, mw_df)
    fin = _get_eps_from_company_page(symbol)
    eps = fin.get("eps")
    pe = (price / eps) if (price and eps and eps > 0) else None
    return {
        "EPS": eps,
        "PE": round(pe, 2) if pe else None,
        "PRICE": price,
    }

def compute_index_medians(symbols, mw_df, index_name):
    ratios_list = []
    total = len(symbols)
    for i, sym in enumerate(symbols):
        print(f"  [{i+1}/{total}] {sym}...", end=" ", flush=True)
        r = compute_ratios_for_symbol(sym, mw_df)
        r["SYMBOL"] = sym
        ratios_list.append(r)
        if all(v is None for v in [r.get("EPS"), r.get("PE")]):
            print("no data")
        else:
            print(f"EPS={r.get('EPS','?')} P/E={r.get('PE','?')}")
        time.sleep(random.uniform(2.0, 3.0))
    df = pd.DataFrame(ratios_list)
    medians = {}
    for field in ["PE", "EPS"]:
        vals = df[field].dropna()
        medians[field] = round(vals.median(), 2) if not vals.empty else None
        medians[f"{field}_count"] = len(vals)
    medians["total_symbols"] = total
    return medians

def update_benchmarks():
    print("Fetching market watch data...")
    mw_df = get_market_watch()
    print(f"  {len(mw_df)} stocks loaded")
    for idx_name, symbols in INDEX_CONSTITUENTS.items():
        print(f"\nComputing {idx_name} medians ({len(symbols)} symbols)...")
        medians = compute_index_medians(symbols, mw_df, idx_name)
        path = BENCHMARKS_DIR / f"{idx_name.lower()}_ratios_latest.csv"
        pd.DataFrame([medians]).to_csv(path, index=False)
        print(f"  Saved to {path}")
        print(f"  Median P/E: {medians.get('PE', 'N/A')} (n={medians.get('PE_count', 0)})")
        print(f"  Median EPS: {medians.get('EPS', 'N/A')} (n={medians.get('EPS_count', 0)})")
    print("\nBenchmarks updated.")

def load_benchmarks():
    result = {}
    for idx_name in ["KSE30", "KSE100", "ALLSHR"]:
        path = BENCHMARKS_DIR / f"{idx_name.lower()}_ratios_latest.csv"
        if path.exists():
            df = pd.read_csv(path)
            result[idx_name] = df.iloc[0].to_dict() if not df.empty else {}
        else:
            result[idx_name] = {}
    return result

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Compute KSE index benchmark medians")
    parser.add_argument("--update", action="store_true", help="Update benchmark medians from DPS")
    parser.add_argument("--show", action="store_true", help="Show current benchmark medians")
    args = parser.parse_args()
    if args.update:
        update_benchmarks()
    if args.show or not args.update:
        benchmarks = load_benchmarks()
        print("\nCurrent Benchmarks:")
        print(f"{'Index':<10} {'P/E':<10} {'EPS':<10}")
        print("-" * 30)
        for idx in ["KSE30", "KSE100", "ALLSHR"]:
            b = benchmarks.get(idx, {})
            pe = b.get("PE", "N/A")
            eps = b.get("EPS", "N/A")
            print(f"{idx:<10} {str(pe):<10} {str(eps):<10}")
