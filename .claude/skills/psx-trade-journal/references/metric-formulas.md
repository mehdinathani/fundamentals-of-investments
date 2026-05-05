# Journal Metric Formulas

Same families as `psx-backtester/references/metrics-formulas.md`, but applied to LIVE trades.

## CAGR (live)

Use the daily mark-to-market equity curve, not just closed-trade P&L.

```python
def live_cagr(equity_daily: pd.Series) -> float:
    if len(equity_daily) < 2: return 0
    years = (equity_daily.index[-1] - equity_daily.index[0]).days / 365.25
    if years <= 0: return 0
    return (equity_daily.iloc[-1] / equity_daily.iloc[0]) ** (1/years) - 1
```

## Win Rate

```python
def win_rate(closed: pd.DataFrame) -> float:
    if len(closed) == 0: return 0
    return (closed["pnl_net_pkr"] > 0).sum() / len(closed)
```

## Win/Loss Ratio (avg winner % vs avg loser %)

```python
def win_loss_ratio(closed: pd.DataFrame) -> float:
    wins = closed[closed.pnl_net_pkr > 0].pnl_pct.mean()
    losses = closed[closed.pnl_net_pkr <= 0].pnl_pct.mean()
    if pd.isna(wins) or pd.isna(losses) or losses >= 0:
        return float("inf") if pd.notna(wins) else 0
    return abs(wins / losses)
```

## Max Drawdown

```python
def max_dd(equity_daily: pd.Series) -> float:
    peak = equity_daily.expanding().max()
    dd = (equity_daily - peak) / peak
    return dd.min()  # negative number
```

## Sharpe (annualized)

```python
def sharpe(equity_daily: pd.Series, rf_annual: float = 0.20) -> float:
    daily = equity_daily.pct_change().dropna()
    if len(daily) < 30: return 0
    rf_daily = rf_annual / 252
    excess = daily - rf_daily
    if excess.std() == 0: return 0
    return (excess.mean() * 252) / (excess.std() * np.sqrt(252))
```

## Per-tier breakdown

```python
def by_tier(closed: pd.DataFrame) -> pd.DataFrame:
    return closed.groupby("entry_signal_tier").agg(
        trades=("trade_id", "count"),
        win_rate=("pnl_net_pkr", lambda x: (x > 0).mean()),
        total_pnl=("pnl_net_pkr", "sum"),
        avg_pnl_pct=("pnl_pct", "mean"),
    )
```

## Per-sector breakdown

Same as per-tier, group by `sector`.

## PASS/WARN thresholds for monthly review

| Metric | PASS | WARN | FAIL |
|--------|------|------|------|
| Win rate | > 50% | 40-50% | < 40% |
| Win/loss | > 2.0 | 1.5-2.0 | < 1.5 |
| Max drawdown month | < 5% | 5-10% | > 10% |
| Stop violations | 0 | 1-2 | ≥ 3 |
| Trades count | 5-15 | < 5 or 15-25 | > 25 (overtrading) |

WARN → review and document. FAIL → halt new entries until cause identified.
