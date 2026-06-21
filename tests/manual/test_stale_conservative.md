# Manual Test: Stale Data, No-Signal Day & Conservative Mode

## Test 1: Stale Data Warning

```bash
python scripts/run_scan.py --data-age 1
```

**Check**:
- [ ] If benchmarks are >1 day old: shows `⚠ STALE BENCHMARKS` warning with count
- [ ] Warning includes fix command: `python scripts/category_benchmarks.py --update`
- [ ] Pipeline continues despite stale data (graceful, not fatal)

To force stale data for testing:
```bash
# Touch benchmark files to set old timestamps
touch -t 202601010000 data/benchmarks/kse30_ratios_latest.csv
python scripts/run_scan.py --data-age 1
```

---

## Test 2: Stale Data With Custom Threshold

```bash
python scripts/run_scan.py --data-age 35
```

**Check**:
- [ ] No warning if benchmarks are <35 days old
- [ ] `--data-age` flag accepted without error

---

## Test 3: No-Signal Day (All HOLD)

The scan currently produces 1 SELL (HBL) + 4 HOLD. To simulate a no-signal day,
run with symbols that have no technical trigger:

```bash
python scripts/run_scan.py --symbols ENGRO OGDC LUCK SYS
```

**Check**:
- [ ] Phase 6 shows 0 BUY, 0 SELL
- [ ] Shows `→ No actionable signals today. All symbols in HOLD.`
- [ ] Pipeline completes normally

---

## Test 4: Conservative vs Standard Mode

```bash
python scripts/run_scan.py --conservative --symbols ENGRO
python scripts/run_scan.py --symbols ENGRO
```

**Check**:
- [ ] Conservative header: `Capital tier: conservative`
- [ ] Standard header: `Capital tier: standard`
- [ ] End of conservative output shows: `Conservative tier: stricter liquidity floors (2×), 3% max loss per trade`
- [ ] End of standard output shows: `Standard tier: default liquidity floors, 5% max loss per trade`

---

## Summary

| Test | Status | Notes |
|------|--------|-------|
| 1. Stale data warning | ⬜ | |
| 2. Custom threshold | ⬜ | |
| 3. No-signal day | ⬜ | |
| 4. Tier differences | ⬜ | |

**Pass criteria**: All 4 tests produce correct output without errors.
