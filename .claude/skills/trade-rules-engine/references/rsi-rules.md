# RSI Rules and Thresholds

## Parameters (DO NOT CHANGE)

| Parameter | Value | Notes |
|-----------|-------|-------|
| Period | 14 | Standard RSI(14) |
| Overbought | > 70 | Consider profit-taking |
| Oversold | < 30 | Potential buy zone |
| Neutral zone | 40-60 | Ideal entry zone |
| Recovery threshold | Cross above 30 | Momentum shift |

## RSI Calculation

```python
def calculate_rsi(prices, period=14):
    """Calculate RSI(14) from price list."""
    import pandas as pd
    df = pd.DataFrame({"close": prices})
    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]
```

## Signal Integration

```python
def rsi_signal(rsi_14, ma_crossover_signal):
    """
    Combine RSI with MA crossover.
    Returns: 'CONFIRM' | 'WARNING' | 'REJECT'
    """

    # RSI recovery from oversold + golden cross = STRONG
    if rsi_14 > 30 and rsi_14 <= 60 and ma_crossover_signal == 'BUY':
        return 'CONFIRM'

    # RSI in neutral zone with golden cross = GOOD
    if 40 <= rsi_14 <= 60 and ma_crossover_signal == 'BUY':
        return 'CONFIRM'

    # RSI overbought — caution even with golden cross
    if rsi_14 > 70:
        return 'WARNING'  # Consider partial profit

    # RSI oversold but no golden cross = not yet
    if rsi_14 < 30:
        return 'WARNING'  # Wait for recovery

    # RSI breakdown below 50 with sell signal = STRONG SELL
    if rsi_14 < 50 and ma_crossover_signal == 'SELL':
        return 'REJECT'  # Strong sell confirmation

    return 'CONFIRM'  # Default: no conflict
```

## RSI Signal Tiers

| RSI | MA Signal | Combined Action |
|-----|-----------|-----------------|
| 40-60 | Golden Cross + Volume | **Strong Buy** |
| 30-40 or 60-70 | Golden Cross + Volume | **Moderate Buy** |
| < 30 | Golden Cross | **Cautious Buy** (recovering) |
| > 70 | Any | **Warning** (overbought) |
| < 50 | Death Cross | **Strong Sell** |
| > 70 | Death Cross | **Strong Sell** (exit now) |

## CGT-Aware Deferral Logic (ADR-002 D7)

When an RSI-based exit signal fires, check if CGT deferral applies:

```python
def should_defer_for_cgt(entry_date, exit_signal_type, rsi_14, ma_signal,
                          macro_state):
    """
    Returns True if exit should be deferred to cross CGT bracket.
    """
    # Never defer stop-loss or trend-reversal
    if exit_signal_type in ("stop_loss", "trend_reversal"):
        return False

    # Never defer if macro is risk-off
    if macro_state == "RISK_OFF":
        return False

    # Check if within 30 days of 6-month boundary
    holding_days = (date.today() - entry_date).days
    days_to_6mo = 180 - holding_days

    if days_to_6mo > 30:
        return False  # Too far from boundary

    if days_to_6mo <= 0:
        return False  # Already past 6-month bracket

    # Check technicals are neutral
    if not (30 <= rsi_14 <= 70):
        return False  # RSI outside neutral = don't defer

    if ma_signal == "SELL":
        return False  # Trend reversal = don't defer

    return True
```
