# Moving Average Crossover Logic

## Parameters (DO NOT CHANGE)

| MA Type | Period | Purpose |
|---------|--------|---------|
| Fast MA | 20-day SMA | Short-term momentum |
| Slow MA | 50-day SMA | Trend confirmation |
| Trend MA | 200-day SMA | Long-term bias filter |

## Crossover Detection

```python
def detect_crossover(ma_fast, ma_slow, prev_ma_fast, prev_ma_slow):
    """
    Detects if fast MA has crossed above/below slow MA.
    Returns: 'golden' | 'death' | None
    """
    # Golden cross: fast was below, now above
    if prev_ma_fast <= prev_ma_slow and ma_fast > ma_slow:
        return 'golden'

    # Death cross: fast was above, now below
    if prev_ma_fast >= prev_ma_slow and ma_fast < ma_slow:
        return 'death'

    return None
```

## Complete MA Signal Logic

```python
def ma_signal(ma_20, ma_50, ma_200, prev_ma_20, prev_ma_50,
              price, closes_3d, volume_today, vol_30d_avg):
    """
    Returns: 'BUY' | 'SELL' | 'HOLD'

    Golden cross requirements:
      - 20 SMA crosses ABOVE 50 SMA
      - Price is ABOVE 200 SMA
      - Volume >= 120% of 30-day average

    Death cross or 200 SMA breakdown = SELL
    """

    crossover = detect_crossover(ma_20, ma_50, prev_ma_20, prev_ma_50)

    # BUY: Golden cross with all confirmations
    if (crossover == 'golden' and
        price > ma_200 and
        volume_today >= 1.2 * vol_30d_avg):
        return 'BUY'

    # SELL: Death cross
    if crossover == 'death':
        return 'SELL'

    # SELL: Price below 200 SMA for 3 consecutive days
    if all(p < ma_200 for p in closes_3d[-3:]):
        return 'SELL'

    return 'HOLD'
```

## SMA Calculation

```python
import pandas as pd

def calculate_sma(prices, period):
    """Calculate simple moving average."""
    return pd.Series(prices).rolling(window=period).mean().iloc[-1]
```
