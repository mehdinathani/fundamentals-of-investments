---
name: psx-backtester
description: |
  Validate PSX (Pakistan Stock Exchange) trading strategies against historical data
  BEFORE deploying capital. This is the Phase 1 gate from research.md §8 — if a
  strategy is not profitable in backtest, deployment STOPS. This skill should be
  used when users ask to backtest a strategy, validate trade rules historically,
  measure CAGR/Sharpe/drawdown on past data, simulate trades with PSX constraints
  (circuit breakers, T+2 settlement, holidays), or decide whether a strategy is
  ready for live capital.
allowed-tools: Read, Write, Bash, mcp__context7__query-docs, mcp__context7__resolve-library-id
---

# PSX Backtester

## 👤 Who This Is For

**This is your safety net.** Before risking a single rupee, you can test your strategy against years of historical PSX data.

CA analysts model strategies in Excel to validate their edge. Old investors "backtest" by remembering what worked before. You have neither the Excel skills nor the experience — so this skill does the backtesting for you.

**The rule:** If a strategy doesn't work in backtest (on past data), it won't work in real life. Don't deploy it. This skill prevents you from making expensive mistakes that beginners typically learn the hard way.

---

Validates strategy profitability before live deployment. Per `research.md` §8 Phase 1: **"If not profitable → STOP"**. This skill is the gate. No strategy progresses to semi-automation (Phase 2) or live capital without passing here.

## What This Skill Does

- Replays trade rules over historical PSX data (price + volume + fundamentals)
- Applies PSX-specific frictions: circuit breakers, T+2 settlement, holidays, slippage
- Computes performance metrics: CAGR, Sharpe, max drawdown, win/loss, expectancy
- Generates trade-by-trade ledger for audit
- Outputs a PASS/FAIL verdict against minimum viability thresholds
- Supports walk-forward validation (out-of-sample testing)

## What This Skill Does NOT Do

- Generate signals from scratch (use `trade-rules-engine`)
- Filter the universe (use `psx-market-filter`)
- Size positions (use `risk-management`)
- Optimize / curve-fit parameters — backtesting validates, doesn't tune

---

## Before Implementation

| Source | Gather |
|--------|--------|
| **Codebase** | Existing backtest harness, data store, time-series schema |
| **Conversation** | Strategy version, date range, capital, universe scope |
| **Skill References** | Friction parameters, holiday calendar, slippage models |
| **User Guidelines** | Acceptance thresholds (e.g., minimum Sharpe 1.0) |

---

## PSX Backtest Frictions (MANDATORY)

A backtest that ignores PSX-specific frictions overstates returns. These MUST be modeled:

| Friction | Model |
|----------|-------|
| **Brokerage commission** | 0.15% per side (typical PSX retail) |
| **CDC charges** | 0.005% per trade |
| **CGT (Capital Gains Tax)** | 15% on gains (filer rate, holding < 1 yr) |
| **FED on commission** | 13% on brokerage |
| **Slippage (large-cap)** | 0.10% per side |
| **Slippage (mid-cap)** | 0.30% per side |
| **T+2 settlement** | Cash unavailable for 2 trading days post-sale |
| **Circuit breaker** | If stock locks up/down on signal day, defer to next open |
| **PSX holidays** | Use official calendar; weekends = no trade |
| **Trading hours** | 09:30 – 15:30 PKT (Mon-Fri) |

**Total round-trip cost (large-cap, conservative):** ~0.5% before tax. Strategies must beat this to be viable.

---

## Backtest Engine Structure

```python
from dataclasses import dataclass, field
from datetime import date

@dataclass
class Trade:
    symbol: str
    entry_date: date
    entry_price: float
    exit_date: date | None
    exit_price: float | None
    shares: int
    entry_signal: str    # "Tier 1" / "Tier 2" / etc from trade-rules-engine
    exit_reason: str | None  # "stop_loss" / "ma_sell" / "rsi_overbought" / "trailing"
    pnl_gross: float = 0.0
    pnl_net: float = 0.0  # after costs

@dataclass
class BacktestResult:
    start_date: date
    end_date: date
    starting_capital: float
    ending_capital: float
    cagr: float
    max_drawdown_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    win_rate: float
    avg_win_pct: float
    avg_loss_pct: float
    win_loss_ratio: float
    expectancy_pct: float
    total_trades: int
    trades: list[Trade] = field(default_factory=list)
    verdict: str = ""  # "PASS" / "FAIL"
    failed_thresholds: list[str] = field(default_factory=list)
```

---

## Minimum Viability Thresholds (PASS criteria)

A strategy must clear ALL of the following to PASS Phase 1:

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| CAGR | ≥ 15% | Beats KSE-100 long-term + risk-free buffer |
| Sharpe ratio | ≥ 1.0 | Risk-adjusted return acceptable |
| Max drawdown | ≤ 15% | Survival rule from `risk-management` |
| Win rate | ≥ 45% | With win/loss ≥ 2.0, expectancy stays positive |
| Win/loss ratio | ≥ 2.0 | Avg winner ≥ 2× avg loser |
| Expectancy per trade | > 0 (after costs) | Strategy actually has edge |
| Trade count | ≥ 30 | Statistical significance (avoid lucky-streak) |
| Out-of-sample period | ≥ 6 months | No curve-fit |

If ANY threshold fails → **verdict = FAIL → STOP**. Per research.md §8.

---

## Walk-Forward Validation (REQUIRED)

Single-period backtests are unreliable. Use walk-forward:

```
1. Split history into in-sample (IS) and out-of-sample (OOS):
   - IS: 70% (e.g., 2018-2023)
   - OOS: 30% (e.g., 2024-2026)

2. Define strategy on IS only. NO peeking at OOS.

3. Run backtest on OOS with IS-defined rules.

4. Verdict is based on OOS performance, not IS.

5. If OOS materially underperforms IS (e.g., Sharpe drops 50%+),
   the strategy is curve-fit → FAIL.
```

---

## Backtest Loop (skeleton)

```python
def run_backtest(
    strategy_fn,           # callable: (state, day) -> signals
    universe: list[str],
    price_data: dict,      # {symbol: DataFrame[date, OHLCV]}
    start: date,
    end: date,
    starting_capital: float,
    risk_pct: float = 0.05,
) -> BacktestResult:
    portfolio = {"cash": starting_capital, "positions": {}, "history": []}
    trades = []

    trading_days = build_psx_calendar(start, end)  # excludes holidays/weekends

    for day in trading_days:
        # 1. Update portfolio with EOD prices
        mark_to_market(portfolio, price_data, day)

        # 2. Apply T+2 settlement (release cash from trades 2 days ago)
        release_settled_cash(portfolio, day)

        # 3. Check exits FIRST (stops, trailing, signals)
        for symbol, position in list(portfolio["positions"].items()):
            exit_signal = check_exit(position, price_data[symbol], day)
            if exit_signal:
                price = apply_slippage(price_data[symbol].loc[day, "close"], "sell", symbol)
                if is_circuit_locked(price_data[symbol], day, "down"):
                    continue  # Defer; cannot exit
                trade = close_position(portfolio, symbol, price, day, exit_signal)
                trade.pnl_net = apply_costs(trade)
                trades.append(trade)

        # 4. Check entries (only after exits free up cash)
        signals = strategy_fn(price_data, day, universe)
        for sym, sig in signals.items():
            if sig != "BUY":
                continue
            if sym in portfolio["positions"]:
                continue
            if is_circuit_locked(price_data[sym], day, "up"):
                continue
            shares, _, _ = calculate_position_size(...)  # from risk-management
            price = apply_slippage(price_data[sym].loc[day, "close"], "buy", sym)
            open_position(portfolio, sym, shares, price, day, sig)

        snapshot(portfolio, day)

    return summarize(portfolio, trades, starting_capital)
```

---

## Metric Formulas

### CAGR
```
CAGR = (ending_capital / starting_capital) ** (1 / years) - 1
```

### Sharpe Ratio (annualized)
```
risk_free = 0.20  # PKR T-bill rate (approx — update from SBP)
daily_returns = portfolio_value.pct_change()
sharpe = (daily_returns.mean() * 252 - risk_free) / (daily_returns.std() * sqrt(252))
```

### Max Drawdown
```
running_max = portfolio_value.expanding().max()
drawdown = (portfolio_value - running_max) / running_max
max_drawdown_pct = drawdown.min() * 100
```

### Expectancy
```
expectancy = (win_rate × avg_win) - ((1 - win_rate) × avg_loss)
```

---

## Output Checklist

- [ ] All PSX frictions applied (commission, CGT, slippage, T+2)
- [ ] Holiday calendar respected (no trades on PSX closures)
- [ ] Circuit-locked days handled (defer entry/exit)
- [ ] Walk-forward split enforced (IS/OOS, no leakage)
- [ ] All 8 viability thresholds checked → explicit PASS/FAIL
- [ ] Trade ledger output (CSV) for audit
- [ ] Equity curve and drawdown chart generated
- [ ] Per-symbol breakdown (which stocks contributed P&L)
- [ ] Verdict block logged: if FAIL, list failed thresholds
- [ ] No look-ahead bias (signals computed only from data available at `day`)

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/psx-frictions.md` | When modeling commissions, CGT, slippage |
| `references/psx-calendar.md` | When building trading-day calendar |
| `references/walk-forward.md` | When splitting IS/OOS periods |
| `references/metrics-formulas.md` | When computing Sharpe, Sortino, drawdown |

## Source

Research: `research.md` §8 Phase 1 — Strategy Validation. Failure condition: "If not profitable → STOP".
Principle: "Consistency > Excitement" — only validated strategies progress.
