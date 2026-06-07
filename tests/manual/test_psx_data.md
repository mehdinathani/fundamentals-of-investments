# Manual Test: psx_data.py — Data Fetching Wrapper

## Prerequisites
- Python 3.11+ with `pip install requests pandas beautifulsoup4 lxml`
- Internet connection (DPS portal access)

## Test 1: Market Watch Data

```bash
python3 -c "
import sys; sys.path.insert(0, '.')
from scripts.psx_data import get_market_watch
mw = get_market_watch()
print(f'Stocks: {len(mw)}')
print(f'Columns: {list(mw.columns)}')
print(mw.head(2))
"
```

**Expected**: ~460-500 stocks with columns: SYMBOL, SECTOR, LISTED IN, LDCP, OPEN, HIGH, LOW, CURRENT, CHANGE, CHANGE(%), VOLUME. Volume should be numeric (not string with commas).

**Check**:
- [ ] Returns DataFrame with ≥400 rows
- [ ] All 11 columns present
- [ ] VOLUME column is int64/float64 (not object/string)
- [ ] No NaN in SYMBOL column

---

## Test 2: Historical Data (Cached)

```bash
python3 -c "
import sys; sys.path.insert(0, '.')
from scripts.psx_data import get_historical_data
hist = get_historical_data('ENGRO')
print(f'Rows: {len(hist)}')
print(f'Columns: {list(hist.columns)}')
print(f'Date range: {hist[\"DATE\"].min()} to {hist[\"DATE\"].max()}')
print(hist.tail(3))
"
```

**Expected**: ENGRO historical data from cache (already in `data/historical/ENGRO.parquet`).

**Check**:
- [ ] Returns ≥2000 rows (ENGRO has decades of data)
- [ ] Columns: DATE, OPEN, HIGH, LOW, CLOSE, VOLUME
- [ ] All price columns are float64
- [ ] VOLUME is int64
- [ ] No NaN in CLOSE column
- [ ] Data is sorted by DATE ascending

---

## Test 3: Historical Data (Fresh Fetch)

```bash
python3 -c "
import sys; sys.path.insert(0, '.')
from scripts.psx_data import get_historical_data
hist = get_historical_data('ENGRO', use_cache=False)
print(f'Rows: {len(hist)}')
print(f'Last date: {hist[\"DATE\"].max()}')
"
```

**Expected**: ENGRO data fetched live from DPS portal (bypasses cache). Must take 2-4s (rate limited).

**Check**:
- [ ] Returns data (may be longer or shorter than cached version)
- [ ] Took ≥2 seconds (rate limiting works)
- [ ] No errors or timeouts

---

## Test 4: Unknown Symbol

```bash
python3 -c "
import sys; sys.path.insert(0, '.')
from scripts.psx_data import get_historical_data
hist = get_historical_data('ZZZZZ')
print(f'Rows: {len(hist)}')
print(f'Empty: {hist.empty}')
"
```

**Expected**: Empty DataFrame, no crash.

**Check**:
- [ ] Returns empty DataFrame (not None)
- [ ] No stack trace printed
- [ ] Script exits cleanly

---

## Test 5: List Cached Symbols

```bash
python3 -c "
import sys; sys.path.insert(0, '.')
from scripts.psx_data import list_cached_symbols
symbols = list_cached_symbols()
print(f'Cached symbols: {len(symbols)}')
print(f'First 5: {symbols[:5]}')
print(f'Has ENGRO: {\"ENGRO\" in symbols}')
print(f'Has OGDC: {\"OGDC\" in symbols}')
"
```

**Expected**: Lists all `.parquet` files in `data/historical/`.

**Check**:
- [ ] Returns list of strings (symbol names)
- [ ] ENGRO is in the list
- [ ] OGDC is in the list
- [ ] At least 5 symbols available

---

## Test 6: Company Info

```bash
python3 -c "
import sys; sys.path.insert(0, '.')
from scripts.psx_data import get_company_info
info = get_company_info('ENGRO')
for k, v in info.items():
    print(f'{k}: {v}')
"
```

**Expected**: Company details for ENGRO (symbol, name, sector, etc.).

**Check**:
- [ ] Returns dict with at least "symbol" key
- [ ] Has sector information
- [ ] No errors if symbol not found (graceful fallback)

---

## Summary

| Test | Status | Notes |
|------|--------|-------|
| 1. Market Watch | ⬜ | |
| 2. Historical (cached) | ⬜ | |
| 3. Historical (fresh) | ⬜ | |
| 4. Unknown symbol | ⬜ | |
| 5. List cached | ⬜ | |
| 6. Company info | ⬜ | |

**Pass criteria**: All 6 tests pass without crashes.
