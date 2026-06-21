# Manual Test: Evidence Signals (US2)

## Prerequisites
- Python 3.11+ with `pip install requests pandas beautifulsoup4 lxml numpy`
- Historical data cached in `data/historical/` (≥210 trading days per symbol)

## Test 1: Market Filter — All Validation Symbols

```bash
python scripts/market_filter.py --all
```

**Expected**: All 5 validation symbols return TRADABLE verdict.

**Check**:
- [ ] ENGRO → TRADABLE
- [ ] OGDC → TRADABLE
- [ ] HBL → TRADABLE
- [ ] LUCK → TRADABLE
- [ ] SYS → TRADABLE
- [ ] No REJECT verdicts
- [ ] Runtime < 30 seconds

---

## Test 2: Market Filter — Conservative Tier

```bash
python scripts/market_filter.py --all --conservative
```

**Expected**: Stricter thresholds (2× liquidity floor). May still pass for large-cap stocks.

**Check**:
- [ ] Runs without errors
- [ ] Conservative tier logic applied (liquidity thresholds doubled)

---

## Test 3: Evidence Signal — Single Stock

```bash
python scripts/evidence_signals.py --symbol ENGRO
```

**Check**:
- [ ] Signal is BUY, SELL, or HOLD
- [ ] Moving Averages section shows MA20, MA50, MA200 values
- [ ] Crossover status shown (golden_cross, death_cross, above_50, below_50)
- [ ] Price vs MA200 shown (ABOVE or BELOW)
- [ ] RSI(14) value and zone shown (oversold, neutral, bullish, bearish, overbought)
- [ ] Volume section: today's volume, 30d avg, ratio
- [ ] Reasoning section has ≥3 bullet points
- [ ] No crashes

---

## Test 4: Evidence Signal — All Validation Symbols

```bash
python scripts/evidence_signals.py --all
```

**Check**:
- [ ] All 5 symbols processed
- [ ] Each has complete evidence chain
- [ ] Total runtime < 60 seconds
- [ ] No crashes from any symbol

---

## Test 5: SELL Signal Detection

HBL should show SELL signal (price below MA200).

```bash
python scripts/evidence_signals.py --symbol HBL
```

**Check**:
- [ ] Signal is SELL
- [ ] Price vs MA200 shows "BELOW ❌"
- [ ] Reasoning mentions MA200 or death cross

---

## Test 6: RSI Zone Verification

Check that RSI zones are correctly assigned:

```bash
python scripts/evidence_signals.py --symbol SYS
```

**Check**:
- [ ] RSI zone is correctly labeled (check the value vs zone):
  - RSI < 30 → oversold
  - RSI 30-40 → bearish
  - RSI 40-60 → neutral
  - RSI 60-70 → bullish
  - RSI > 70 → overbought

---

## Test 7: Evidence Dict Completeness

Verify evidence dict has all required fields by inspecting the output:

**Check**:
- [ ] Evidence includes: ma_crossover (with status, ma_20, ma_50, ma_200, price_above_ma200)
- [ ] Evidence includes: rsi (with value, zone)
- [ ] Evidence includes: volume (with today, avg_30d, ratio)
- [ ] Evidence includes: price, stop_loss_pct, reasons
- [ ] At least 5 distinct evidence fields present

---

## Summary

| Test | Status | Notes |
|------|--------|-------|
| 1. Market filter — all | ⬜ | |
| 2. Market filter — conservative | ⬜ | |
| 3. Signal — single stock | ⬜ | |
| 4. Signal — all symbols | ⬜ | |
| 5. SELL detection (HBL) | ⬜ | |
| 6. RSI zone | ⬜ | |
| 7. Evidence completeness | ⬜ | |

**Pass criteria**: Tests 1, 3, 4, 5, 7 all pass (≥5 evidence fields).
