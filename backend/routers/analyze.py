import time
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from backend.auth import require_auth
from backend.services.ai_service import analyze_symbol
from backend.services.compare_service import compare_stock_full
from backend.services.sector_service import get_sector_benchmarks, get_sector

router = APIRouter(prefix="/api", tags=["analyze"], dependencies=[Depends(require_auth)])

_cache: dict[str, dict] = {}
CACHE_TTL = 1800


def _get_cached(key: str) -> dict | None:
    entry = _cache.get(key)
    if entry and (time.time() - entry["ts"]) < CACHE_TTL:
        return entry["data"]
    return None


def _set_cache(key: str, data: dict):
    _cache[key] = {"ts": time.time(), "data": data}


@router.get("/benchmarks/{symbol}")
def get_benchmarks(symbol: str):
    symbol = symbol.upper()
    cached = _get_cached(f"bm:{symbol}")
    if cached:
        return cached
    try:
        from scripts.psx_data import get_market_watch
        mw = get_market_watch()
        result = compare_stock_full(symbol, mw_df=mw)
        if not result.get("ratios"):
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found or no data available")
        _set_cache(f"bm:{symbol}", result)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmarks/sector/{sector}")
def get_sector_benchmarks_endpoint(sector: str):
    sector = sector.upper()
    benchmarks = get_sector_benchmarks()
    if sector not in benchmarks:
        raise HTTPException(status_code=404, detail=f"Sector {sector} not found")
    return {"sector": sector, "benchmarks": benchmarks[sector]}


@router.get("/analyze/{symbol}")
def get_analysis(symbol: str, tier: str = Query("standard", regex="^(standard|conservative)$")):
    symbol = symbol.upper()
    cache_key = f"ai:{symbol}:{tier}"
    cached = _get_cached(cache_key)
    if cached:
        return cached
    try:
        result = analyze_symbol(symbol, tier)
        _set_cache(cache_key, result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ScanRequest(BaseModel):
    symbols: list[str] | None = None
    tier: str = "standard"


@router.post("/analyze/scan")
def batch_analysis(body: ScanRequest):
    if body.symbols:
        symbols = [s.upper() for s in body.symbols][:5]
    else:
        from scripts.psx_data import get_market_watch
        mw = get_market_watch()
        symbols = mw["symbol"].str.upper().unique().tolist()[:5]

    buy_count = 0
    sell_count = 0
    hold_count = 0
    results: list[dict] = []

    for sym in symbols:
        cache_key = f"ai:{sym}:{body.tier}"
        cached = _get_cached(cache_key)
        if cached:
            result = cached
        else:
            result = analyze_symbol(sym, body.tier)
            _set_cache(cache_key, result)
        results.append(result)
        if result.get("ai_available"):
            v = result.get("verdict")
            if v in ("BUY", "BUY_BACK"):
                buy_count += 1
            elif v in ("SELL", "SHORT_SELL", "STOP_LOSS"):
                sell_count += 1
            else:
                hold_count += 1

    summary = f"Scanned {len(symbols)} symbols: {buy_count} bullish, {sell_count} bearish, {hold_count} neutral."
    return {"results": results, "summary": summary}
