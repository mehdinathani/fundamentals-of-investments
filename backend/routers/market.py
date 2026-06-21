from fastapi import APIRouter, Depends, Query
from typing import Optional
import pandas as pd

from backend.services.signal_service import scan_all_symbols, scan_symbol, compute_indicators
from backend.services.macro_service import get_current_macro_state
from backend.auth import require_auth
from scripts.psx_data import get_historical_data, get_market_watch
from scripts.heatmap_tradebars import _get_sector_name

router = APIRouter(prefix="/api/market", tags=["market"], dependencies=[Depends(require_auth)])


@router.get("/scan")
def scan_market(macro_state: Optional[str] = Query(None)):
    """Scan all symbols for buy signals."""
    if macro_state is None:
        macro_state = get_current_macro_state()["state"]
    results = scan_all_symbols(macro_state)
    buy_signals = [r for r in results if r["signal"] == "BUY"]
    return {
        "total_scanned": len(results),
        "buy_signals": len(buy_signals),
        "macro_state": macro_state,
        "symbols": results,
    }


@router.get("/symbol/{symbol}")
def get_symbol(symbol: str):
    """Get detailed data for a single symbol."""
    macro = get_current_macro_state()
    result = scan_symbol(symbol.upper(), macro["state"])
    if result is None:
        return {"error": f"Symbol {symbol} not found"}, 404
    result["macro"] = macro
    return result


@router.get("/history/{symbol}")
def get_history(symbol: str, days: int = Query(180, ge=20, le=2000)):
    """OHLC price history with moving-average overlays for the price chart."""
    symbol = symbol.upper()
    df = get_historical_data(symbol)
    if df is None or df.empty:
        return {"symbol": symbol, "candles": []}

    df = df.copy()
    df["DATE"] = pd.to_datetime(df["DATE"])
    df = df.sort_values("DATE").reset_index(drop=True)
    for col in ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = compute_indicators(df)
    df = df.tail(days)

    candles = []
    for _, r in df.iterrows():
        def _f(v):
            return float(v) if pd.notna(v) else None
        candles.append({
            "date": r["DATE"].strftime("%Y-%m-%d"),
            "open": _f(r["OPEN"]),
            "high": _f(r["HIGH"]),
            "low": _f(r["LOW"]),
            "close": _f(r["CLOSE"]),
            "volume": _f(r["VOLUME"]),
            "ma20": _f(r.get("MA20")),
            "ma50": _f(r.get("MA50")),
            "ma200": _f(r.get("MA200")),
        })
    return {"symbol": symbol, "candles": candles}


@router.get("/heatmap")
def get_heatmap():
    """Sector performance heatmap data (today's avg change per sector)."""
    mw = get_market_watch()
    if mw is None or mw.empty or "SECTOR" not in mw.columns:
        return {"sectors": []}

    grouped = mw.groupby("SECTOR").agg(
        count=("SYMBOL", "count"),
        avg_change=("CHANGE (%)", "mean"),
        total_volume=("VOLUME", "sum"),
    ).sort_values("avg_change", ascending=False)

    sectors = []
    for code, row in grouped.iterrows():
        avg_chg = row["avg_change"]
        sectors.append({
            "code": str(code),
            "name": _get_sector_name(code),
            "avg_change_pct": round(float(avg_chg), 2) if pd.notna(avg_chg) else 0.0,
            "stock_count": int(row["count"]),
            "total_volume": float(row["total_volume"]) if pd.notna(row["total_volume"]) else 0.0,
        })
    return {"sectors": sectors}
