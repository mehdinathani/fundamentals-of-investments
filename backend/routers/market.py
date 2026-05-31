from fastapi import APIRouter, Query
from typing import Optional

from backend.services.signal_service import scan_all_symbols, scan_symbol
from backend.services.macro_service import get_current_macro_state

router = APIRouter(prefix="/api/market", tags=["market"])


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
