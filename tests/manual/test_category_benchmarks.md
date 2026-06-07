# Manual Test: Category Benchmarks + Ratio Calculator (US1)

## Prerequisites
- Python 3.11+ with `pip install requests pandas beautifulsoup4 lxml`
- Internet connection (DPS portal access)
- Run `python scripts/category_benchmarks.py --update` first (takes ~3-5 min)

## Test 1: Benchmark Update

```bash
python scripts/category_benchmarks.py --update
```

**Expected**: Fetches data for KSE30 (30 stocks) and KSE100 (56 stocks), computes median P/E and EPS, saves to `data/benchmarks/`.

**Check**:
- [ ] KSE30: at least 25/30 stocks have EPS data
- [ ] KSE30: at least 20/30 have P/E data
- [ ] KSE100: at least 45/56 have EPS data
- [ ] KSE100: at least 35/56 have P/E data
- [ ] Files created: `data/benchmarks/kse30_ratios_latest.csv`, `data/benchmarks/kse100_ratios_latest.csv`
- [ ] CSV files have columns: PE, EPS, PE_count, EPS_count, total_symbols
- [ ] Median P/E is a reasonable number (typically 5-15 for PSX)

---

## Test 2: Show Benchmarks

```bash
python scripts/category_benchmarks.py --show
```

**Expected**: Table showing current KSE30 and KSE100 median P/E and EPS.

**Check**:
- [ ] KSE30 P/E shows a value (not N/A)
- [ ] KSE100 P/E shows a value (not N/A)
- [ ] KSE30 EPS shows a value (not N/A)
- [ ] KSE100 EPS shows a value (not N/A)
- [ ] No errors

---

## Test 3: Single Stock Comparison

```bash
python scripts/ratio_calculator.py --symbol ENGRO
```

**Expected**: ENGRO's P/E and EPS compared against KSE30 and KSE100 medians with deviation % and verdict.

**Check**:
- [ ] Price shown (e.g., PKR 262.21)
- [ ] P/E shown (e.g., 8.13) with vs KSE30 comparison
- [ ] P/E shown with vs KSE100 comparison
- [ ] Each comparison shows deviation % and "ABOVE median" or "BELOW median"
- [ ] EPS shown with same comparisons
- [ ] No errors

---

## Test 4: Multiple Symbols

```bash
python scripts/ratio_calculator.py --all
```

**Expected**: Runs for all 5 validation symbols (ENGRO, OGDC, HBL, LUCK, SYS).

**Check**:
- [ ] ENGRO output present
- [ ] OGDC output present
- [ ] HBL output present
- [ ] LUCK output present
- [ ] SYS output present
- [ ] Each symbol has price, P/E, and EPS with comparisons
- [ ] Each comparison has deviation % and verdict
- [ ] Total runtime < 60 seconds (should use cached market watch)

---

## Test 5: Benchmark Freshness Warning

If benchmarks haven't been updated in >30 days:
- [ ] Warning "⚠ STALE DATA" appears at top of output

If benchmarks are fresh (<30 days):
- [ ] No stale data warning

---

## Test 6: Re-run Benchmark (Fresh Update)

```bash
python scripts/category_benchmarks.py --update
```

**Expected**: Should be faster than first run (DPS rate limiting still applies but EPS extraction from company pages is the bottleneck).

**Check**:
- [ ] Successfully completes
- [ ] Median values are similar to first run (small differences expected due to market movement)

---

## Test 7: Edge Case — Missing EPS Stock

Some stocks won't have EPS on their company page. Example: PNSC.

```bash
python scripts/ratio_calculator.py --symbol PNSC
```

**Expected**:
- [ ] P/E shown as "N/A"
- [ ] EPS shown as "N/A"
- [ ] Comparisons show "median=N/A"
- [ ] No crash

---

## Summary

| Test | Status | Notes |
|------|--------|-------|
| 1. Benchmark update | ⬜ | |
| 2. Show benchmarks | ⬜ | |
| 3. Single stock | ⬜ | |
| 4. Multiple symbols | ⬜ | |
| 5. Freshness warning | ⬜ | |
| 6. Re-run update | ⬜ | |
| 7. Edge case | ⬜ | |

**Pass criteria**: Tests 1-4 all pass; tests 5-7 acceptable if partially passing.
