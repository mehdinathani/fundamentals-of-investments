import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from scripts.macros import SECTOR_CODES, BENCHMARKS_DIR

SECTOR_CACHE_PATH = BENCHMARKS_DIR / "sector_medians.json"
_sector_cache: dict | None = None


def _load_cache():
    global _sector_cache
    if _sector_cache is not None:
        return _sector_cache
    if SECTOR_CACHE_PATH.exists():
        with open(SECTOR_CACHE_PATH) as f:
            _sector_cache = json.load(f)
    else:
        _sector_cache = {}
    return _sector_cache


def get_sector(symbol: str) -> str | None:
    for sector, symbols in SECTOR_CODES.items():
        if symbol in symbols:
            return sector
    return None


def get_sector_peers(symbol: str) -> list[str]:
    sector = get_sector(symbol)
    if not sector:
        return []
    return [s for s in SECTOR_CODES[sector] if s != symbol]


def get_sector_benchmarks() -> dict:
    return _load_cache()


def get_sector_median(symbol: str, metric: str) -> dict | None:
    sector = get_sector(symbol)
    if not sector:
        return None
    cache = _load_cache()
    sector_data = cache.get(sector)
    if not sector_data:
        return None
    key = f"{metric}_median"
    return {
        "sector": sector,
        "median": sector_data.get(key),
        "count": sector_data.get(f"{metric}_count", 0),
        "symbols_in_sector": sector_data.get("symbols_in_sector", 0),
    }
