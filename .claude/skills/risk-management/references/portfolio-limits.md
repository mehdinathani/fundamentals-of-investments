# Portfolio-Level Risk Limits

## Exposure Limits

| Limit | Value | Enforcement |
|-------|-------|-------------|
| Max per position | 10% of account | HARD — reject trade |
| Max total exposure | 70% of account (30% cash) | HARD — reject trade |
| Max mid-cap exposure | 30% of account | SOFT — warn |
| Max concurrent positions | 5-7 stocks | SOFT — warn |
| Min cash reserve | 30% of account | HARD — stop new buys |
| Max sector concentration | 2 stocks per sector | SOFT — warn |

## Portfolio Health Metrics

```python
def portfolio_health(positions, account_balance):
    """
    positions: list of dicts with keys:
      - symbol, sector, value, unrealized_gain_pct
    Returns: dict with health indicators
    """
    total_invested = sum(p["value"] for p in positions)
    exposure_pct = (total_invested / account_balance) * 100

    # Sector concentration
    from collections import Counter
    sector_counts = Counter(p["sector"] for p in positions)

    # Winners vs losers
    winners = [p for p in positions if p["unrealized_gain_pct"] > 0]
    losers = [p for p in positions if p["unrealized_gain_pct"] < 0]

    return {
        "exposure_pct": round(exposure_pct, 2),
        "cash_reserve_pct": round(100 - exposure_pct, 2),
        "position_count": len(positions),
        "max_sector_count": max(sector_counts.values()) if sector_counts else 0,
        "winners": len(winners),
        "losers": len(losers),
        "over_exposed": exposure_pct > 70,
        "sector_concentrated": max(sector_counts.values()) > 2 if sector_counts else False,
    }
```

## Actions by Health Status

| Condition | Action |
|-----------|--------|
| Exposure > 70% | REJECT new buys |
| Cash < 30% | REJECT new buys |
| > 7 positions | REJECT new buys (consolidate first) |
| > 2 stocks in same sector | WARN (diversify) |
| > 30% in mid-caps | WARN (liquidity risk) |
| Any position > 10% | SELL excess (partial) |
