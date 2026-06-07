# Manual Test: Heatmaps & Trade Bars (US3)

## Prerequisites
- Python 3.11+ with `pip install requests pandas beautifulsoup4 lxml numpy`
- Sector code cache at `data/sector_codes.json` (build once: run heatmap once)

## Test 1: Sector Heatmap

```bash
python scripts/heatmap_tradebars.py --heatmap
```

**Check**:
- [ ] Shows ≥10 sectors
- [ ] Each sector has color-coded change % (green positive, red negative)
- [ ] Green/red bar proportional to magnitude
- [ ] Stock count per sector shown
- [ ] Runtime < 5 seconds (sector names loaded from cache)
- [ ] All sector codes resolved to names (no raw "0814" codes)

---

## Test 2: Single Trade Bar

```bash
python scripts/heatmap_tradebars.py --trade-bar OGDC
```

**Check**:
- [ ] Shows "TRADE BAR — OGDC" header
- [ ] 3 lines: Price, MA20, MA50
- [ ] Volume line below
- [ ] Date ticks at bottom
- [ ] Price range shown (min — max)
- [ ] No index errors

---

## Test 3: All Trade Bars

```bash
python scripts/heatmap_tradebars.py --all
```

**Check**:
- [ ] Heatmap displayed first
- [ ] Trade bars for all 5 validation symbols
- [ ] Each has proper sparklines
- [ ] Runtime < 30 seconds

---

## Test 4: Trade Bar with Signal Marker

Run the orchestrator and verify trade bars include signal markers:

```bash
python scripts/run_scan.py --symbols HBL
```

**Check**:
- [ ] HBL trade bar shows 🔴 SELL marker
- [ ] Marker position corresponds to last data point

---

## Test 5: Edge Cases

```bash
python scripts/heatmap_tradebars.py --trade-bar ZZZZZ
```

**Check**:
- [ ] Graceful error message ("No historical data for ZZZZZ")
- [ ] No crash

---

## Summary

| Test | Status | Notes |
|------|--------|-------|
| 1. Sector heatmap | ⬜ | |
| 2. Single trade bar | ⬜ | |
| 3. All trade bars | ⬜ | |
| 4. With signal marker | ⬜ | |
| 5. Edge case | ⬜ | |

**Pass criteria**: Tests 1-4 all pass without errors. Test 5 graceful as bonus.
