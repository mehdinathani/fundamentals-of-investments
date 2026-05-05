# Backtest Metric Formulas

Reference implementations for the metrics gating Phase 1 → Phase 2 transition.

## CAGR (Compound Annual Growth Rate)

```
CAGR = (V_end / V_start) ** (1 / years) - 1
years = (date_end - date_start).days / 365.25
```

```python
def cagr(equity: pd.Series) -> float:
    years = (equity.index[-1] - equity.index[0]).days / 365.25
    if years <= 0: return 0
    return (equity.iloc[-1] / equity.iloc[0]) ** (1/years) - 1
```

## Sharpe Ratio (annualized)

```
Sharpe = (R_p - R_f) / σ_p
```

Where R_p = annualized return, R_f = annualized risk-free, σ_p = annualized stdev.

```python
def sharpe(equity: pd.Series, risk_free_annual: float = 0.20) -> float:
    daily = equity.pct_change().dropna()
    rf_daily = risk_free_annual / 252
    excess = daily - rf_daily
    if excess.std() == 0: return 0
    return (excess.mean() * 252) / (excess.std() * np.sqrt(252))
```

For PKR markets, risk-free ~ 20% (SBP T-bill); update yearly.

## Sortino Ratio (downside-only Sharpe)

```python
def sortino(equity: pd.Series, risk_free_annual: float = 0.20) -> float:
    daily = equity.pct_change().dropna()
    rf_daily = risk_free_annual / 252
    excess = daily - rf_daily
    downside = excess[excess < 0].std()
    if downside == 0: return 0
    return (excess.mean() * 252) / (downside * np.sqrt(252))
```

## Max Drawdown

```python
def max_drawdown(equity: pd.Series) -> float:
    peak = equity.expanding().max()
    dd = (equity - peak) / peak
    return dd.min()  # returns negative number, e.g., -0.15
```

## Calmar Ratio

```
Calmar = CAGR / abs(MaxDD)
```

Quick robustness check; > 1.0 is decent.

## Win Rate / Win-Loss Ratio / Expectancy

```python
def trade_stats(trades: pd.DataFrame) -> dict:
    wins = trades[trades.pnl_net > 0]
    losses = trades[trades.pnl_net <= 0]
    n = len(trades)
    if n == 0: return {}
    win_rate = len(wins) / n
    avg_win = wins.pnl_pct.mean() if len(wins) else 0
    avg_loss = losses.pnl_pct.mean() if len(losses) else 0
    win_loss = abs(avg_win / avg_loss) if avg_loss < 0 else float("inf")
    expectancy = win_rate * avg_win + (1 - win_rate) * avg_loss
    return {"win_rate": win_rate, "avg_win": avg_win, "avg_loss": avg_loss,
            "win_loss": win_loss, "expectancy": expectancy}
```

## Profit Factor

```
PF = sum(winning P&L) / abs(sum(losing P&L))
```

PF > 1.5 is solid. PF < 1.0 means you're losing money.

## Why these together

A strategy can be high-Sharpe but bad: e.g., 95% win rate × 0.5% avg win × 5% rare loss = high Sharpe, terrible expectancy on tail.

PASS criteria require ALL of: CAGR ≥ 15%, Sharpe ≥ 1.0, MaxDD ≤ 15%, win-rate ≥ 45%, win/loss ≥ 2.0, expectancy > 0, trades ≥ 30, OOS ≥ 6mo.
