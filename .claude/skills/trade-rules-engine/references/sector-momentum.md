# Sector Momentum Filter

Per ADR-002 D9: **bottom-quartile sectors are excluded regardless of how strong an individual name looks.**

## Rationale

In PSX, sector beats stock selection > 60% of the time (research.md §15.10). A fundamentally strong stock in a declining sector will be dragged down by macro/sector gravity.

## Rules

| Sector performance (rolling 3-month) | Action |
|--------------------------------------|--------|
| Top 50% | PASS — proceed to stock-level analysis |
| 50% – 25% | CAUTION — require stronger stock fundamentals (score > 70/100) |
| Bottom 25% | REJECT — regardless of individual stock quality |

## Implementation

```python
def sector_momentum_filter(symbol_sector, sector_performance_3m):
    """
    sector_performance_3m: dict of {sector: pct_return_3m}
    Returns: "PASS" | "CAUTION" | "REJECT"
    """
    sorted_sectors = sorted(sector_performance_3m.items(),
                            key=lambda x: x[1], reverse=True)
    total = len(sorted_sectors)
    rank = [s[0] for s in sorted_sectors].index(symbol_sector)
    percentile = rank / total

    if percentile >= 0.75:
        return "REJECT"
    elif percentile >= 0.50:
        return "CAUTION"
    else:
        return "PASS"
```

## Frequency

Sector rankings refreshed quarterly. Between refreshes, use the current ranking from the last quarter-end.
