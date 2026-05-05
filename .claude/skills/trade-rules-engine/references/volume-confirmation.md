# Volume Confirmation Rules

## Core Rule: NO TRADE WITHOUT VOLUME

Every BUY signal MUST have volume confirmation. This is non-negotiable.

## Volume Metrics

```python
def volume_metrics(volumes, lookback=30):
    """
    Calculate volume indicators.
    volumes: list of daily volumes, most recent last
    Returns: dict with volume stats
    """
    recent_30 = volumes[-lookback:]
    avg_30 = sum(recent_30) / len(recent_30)
    today = volumes[-1]

    return {
        "avg_30d": avg_30,
        "today": today,
        "ratio": today / avg_30 if avg_30 > 0 else 0,
        "is_spike": today > 3 * avg_30,   # >300% = spike
        "is_confirmed": today >= 1.2 * avg_30,  # >=120% = confirmed
        "is_weak": today < avg_30,  # <100% = weak
    }
```

## Volume Confirmation Logic

```python
def volume_confirmation(volumes, signal_type="BUY"):
    """
    signal_type: 'BUY' or 'SELL'
    Returns: ('PASS'|'FAIL'|'CAUTION', reason)
    """
    metrics = volume_metrics(volumes)
    ratio = metrics["ratio"]

    if signal_type == "BUY":
        if ratio >= 1.5:
            return ("PASS", f"Strong volume ({ratio:.1f}x avg)")
        elif ratio >= 1.2:
            return ("PASS", f"Adequate volume ({ratio:.1f}x avg)")
        elif ratio >= 1.0:
            return ("FAIL", f"Weak volume ({ratio:.1f}x avg) — NO TRADE")
        else:
            return ("FAIL", f"Below-average volume ({ratio:.1f}x avg) — NO TRADE")

    elif signal_type == "SELL":
        # High volume on sell = confirmed breakdown
        if ratio >= 1.5:
            return ("PASS", f"High volume breakdown ({ratio:.1f}x avg)")
        else:
            return ("PASS", "Normal volume sell signal")
```

## Volume Spike Investigation

| Spike Level | Volume Ratio | Action |
|-------------|-------------|--------|
| Normal | 1.0 - 2.0x | No special action |
| Elevated | 2.0 - 3.0x | Check news, verify no manipulation |
| Spike | 3.0 - 5.0x | INVESTIGATE — possible pump/dump |
| Extreme | > 5.0x | AVOID — highly likely manipulated |

## PSX-Specific Notes

- PSX has low liquidity in many mid/small caps — 50,000 shares/day avg is the liquidity floor
- Volume spikes in PSX often indicate operator activity (manipulation)
- Always cross-check volume spikes with news from psx.com.pk/announcements
- If no news explains a >3x volume spike → WAIT for 2-3 days before entering
