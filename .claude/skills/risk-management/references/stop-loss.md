# Stop-Loss Logic

## Initial Stop-Loss

```
Stop-Loss Price = Entry Price × (1 - stop_pct)
Default stop_pct = 5% (0.05)
Conservative stop_pct = 3% (0.03)
```

**Rules:**
- Set IMMEDIATELY upon entry (before any price movement)
- Never negotiate the stop-loss
- Never move stop-loss DOWN (only trail up)

## Trailing Stop Logic

```python
def trailing_stop(entry_price, current_price, stop_pct=0.05):
    """
    Calculate trailing stop based on unrealized gains.
    Returns stop price to use NOW.
    """
    gain_pct = (current_price - entry_price) / entry_price

    if gain_pct >= 0.25:      # +25%
        stop = entry_price * 1.15   # Lock 15% profit
    elif gain_pct >= 0.15:    # +15%
        stop = entry_price * 1.05   # Lock 5% profit
    elif gain_pct >= 0.10:    # +10%
        stop = entry_price          # Breakeven
    else:
        stop = entry_price * (1 - stop_pct)  # Initial stop

    return round(stop, 2)
```

## Stop-Loss Scenarios

| Scenario | Action |
|-----------|--------|
| Price hits stop-loss during day | SELL at market (accept slippage) |
| Gap-down open below stop | SELL at market open (no waiting) |
| Price approaches stop (within 1%) | Prepare exit, no new buys |
| Stop-loss trailed to breakeven | Now risk-free trade — can hold longer |
| Stop-loss trailed to +5% | Locked profit — let winner run |

## PSX-Specific Stop-Loss Notes

- PSX has circuit breakers at ±5% (upper/lower locks)
- If stock hits lower lock (-5%), it may not trade again that day
- Set stop-loss at 4.5% instead of 5% to avoid lock scenarios
- Gap-downs are common in PSX on earnings surprises — always use stops

## Mental Stop vs Hard Stop

| Type | Description | Status |
|------|-------------|--------|
| **Hard stop** (system) | `price <= stop_price → SELL` | MANDATORY |
| **Mental stop** | "I'll sell if it feels wrong" | FORBIDDEN |
| **Moving stop down** | "It'll come back" | FORBIDDEN |
| **Averaging down** | Buying more as price drops | FORBIDDEN |
