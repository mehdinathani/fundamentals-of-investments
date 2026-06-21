# PSX Trading Frictions (cost model)

Every backtest MUST include these. A friction-free backtest will overstate net returns by 1-3% per round trip.

## Per-trade costs

| Component | Rate | Notes |
|-----------|------|-------|
| Brokerage | 0.15% per side | Retail; institutional ~0.05% |
| FED on brokerage | 13% of brokerage | Federal Excise Duty |
| CDC charge | 0.005% per trade | Central Depository Co. |
| SECP fee | 0.005% per trade | Regulator |
| Sales tax | 16% on brokerage (Punjab/Sindh varies) | Province dependent |

## Capital Gains Tax (CGT)

| Holding | Filer rate | Non-filer rate |
|---------|------------|----------------|
| < 6 months | 15% | 30% |
| 6-12 months | 12.5% | 25% |
| 12-24 months | 10% | 20% |
| > 24 months | 0% | 0% |

(Rates as of FY24/25 — verify with FBR annually.)

## Slippage model

| Liquidity tier | Slippage per side |
|----------------|-------------------|
| KSE-30 | 0.10% |
| KSE-100 (outside KSE-30) | 0.20% |
| Mid-cap (outside KSE-100) | 0.30%-0.50% |
| Small-cap | reject (out of universe) |

## Round-trip total (typical KSE-100)

```
0.15% × 2 (brokerage)            = 0.30%
0.13 × 0.30%                      = 0.039% (FED)
0.005% × 2 (CDC) + 0.005% × 2     = 0.020%
0.20% × 2 (slippage)              = 0.40%
─────────────────────────────────────────
Subtotal (cost)                    ≈ 0.76%

Plus CGT on net gain only:
  Gain × 0.15 (filer, < 6mo)
```

A trade must clear ~1% to break even after costs. Stop-loss at 5% means a winner must average ~10% to maintain 2:1 win/loss ratio.

## Implementation

```python
def apply_costs(trade) -> float:
    notional_in = trade.entry_price * trade.shares
    notional_out = trade.exit_price * trade.shares
    gross = notional_out - notional_in

    brokerage = (notional_in + notional_out) * 0.0015
    fed = brokerage * 0.13
    cdc = (notional_in + notional_out) * 0.00005
    secp = (notional_in + notional_out) * 0.00005
    slip = (notional_in + notional_out) * 0.0020  # KSE-100 default

    pre_tax = gross - (brokerage + fed + cdc + secp + slip)
    cgt = max(0, pre_tax) * 0.15  # filer < 6mo
    return pre_tax - cgt
```
