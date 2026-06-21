# PSX Circuit Breaker Rules

PSX uses daily circuit breakers to limit single-day moves. Locked stocks cannot be sized into or exited.

## Circuit limits (as of 2025)

| Board | Daily limit |
|-------|-------------|
| Regular (most stocks) | ±7.5% |
| Mid-cap / less liquid | ±5% |
| Index futures | ±10% |

(Verify current limits with PSX rulebook quarterly — SECP can amend.)

## Lock states

- **Upper lock**: ask side empty at upper limit; only buyers, no sellers.
- **Lower lock**: bid side empty at lower limit; only sellers, no buyers.

Once locked, a stock typically stays locked through close.

## Decision rules

| Situation | Action |
|-----------|--------|
| Stock you want to BUY hits upper lock | SKIP — cannot fill at sane price |
| Position you hold hits lower lock | Must exit at next session open (accept slippage) |
| Stock locked ≥ 2 of last 5 days | REJECT — volatility too high, slippage will eat edge |
| Stock locked on signal day | Defer signal; re-evaluate after one normal session |

## How to detect from market data

```python
def is_locked(day_data):
    high = day_data["high"]; low = day_data["low"]
    close = day_data["close"]; prev = day_data["prev_close"]
    upper = prev * 1.075
    lower = prev * 0.925
    upper_lock = abs(high - upper) < 0.01 and abs(close - upper) < 0.01
    lower_lock = abs(low - lower) < 0.01 and abs(close - lower) < 0.01
    return "upper" if upper_lock else ("lower" if lower_lock else None)
```

Track 5-day rolling count for the "≥ 2 locks" filter.
