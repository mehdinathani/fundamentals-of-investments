import sys
import pandas as pd
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from scripts.ratio_calculator import compare_stock, compute_ratios_for_symbol
from backend.services.sector_service import get_sector, get_sector_peers, get_sector_median
from scripts.psx_data import get_market_watch


def _compute_percentile_rank(symbol: str, ratio_field: str, stock_val: float, mw_df: pd.DataFrame) -> float | None:
    peers = get_sector_peers(symbol)
    values = []
    for p in peers:
        try:
            r = compute_ratios_for_symbol(p, mw_df)
            v = r.get(ratio_field)
            if v is not None:
                values.append(v)
        except Exception:
            continue
    if not values:
        return None
    values.append(stock_val)
    values.sort()
    rank = sum(1 for v in values if v <= stock_val)
    return round((rank / len(values)) * 100, 1)


def compare_stock_full(symbol: str, mw_df: pd.DataFrame | None = None) -> dict:
    if mw_df is None:
        mw_df = get_market_watch()
    base = compare_stock(symbol, mw_df=mw_df)
    sector = get_sector(symbol)
    peers = get_sector_peers(symbol)

    result = {
        "symbol": symbol,
        "sector": sector,
        "sector_peers": peers,
        "price": base.get("price"),
        "ratios": {},
    }

    for ratio_field in ["PE", "EPS"]:
        ratio_data = base.get("ratios", {}).get(ratio_field)
        if not ratio_data:
            continue
        stock_val = ratio_data.get("value")
        comparisons = dict(ratio_data.get("comparisons", {}))

        sec_median = get_sector_median(symbol, ratio_field)
        if sec_median and sec_median["median"] is not None and stock_val is not None:
            dev = ((stock_val - sec_median["median"]) / sec_median["median"]) * 100
            comparisons["SECTOR"] = {
                "median": sec_median["median"],
                "deviation_pct": round(dev, 1),
                "verdict": "ABOVE median" if stock_val > sec_median["median"] else "BELOW median",
                "sector_name": sec_median["sector"],
                "count": sec_median["count"],
                "symbols_in_sector": sec_median["symbols_in_sector"],
            }

        percentile = _compute_percentile_rank(symbol, ratio_field, stock_val, mw_df) if stock_val is not None else None

        result["ratios"][ratio_field] = {
            "value": stock_val,
            "name": ratio_data.get("name", ratio_field),
            "percentile_rank": percentile,
            "comparisons": comparisons,
        }

    return result
