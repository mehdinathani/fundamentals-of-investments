---
name: psx-trade-journal
description: |
  Track every PSX (Pakistan Stock Exchange) trade with full attribution: entry,
  exit, signal source, position size, P&L, and reason for outcome. Computes the
  performance metrics required by research.md §10 (CAGR, win/loss ratio, max
  drawdown, Sharpe ratio). This skill should be used when users ask to log a
  trade, review trading performance, audit recent trades, compute portfolio
  metrics, identify systematic mistakes, or build a feedback loop for strategy
  improvement.
allowed-tools: Read, Write, Bash
---

# PSX Trade Journal

## 👤 Who This Is For

**This skill turns your trading into a learning system.** Without a journal, you repeat the same mistakes. With one, every loss teaches you something.

CA analysts and institutional traders are required to maintain trade logs. It's part of their professional discipline. Old investors who survived decades have mental journals (they remember their painful losses vividly). You need a written one — because you don't have the years of experience to remember what went wrong.

**The most important sentence in this system:** You will learn more from your 10th losing trade than your 10th winning trade — but only if you've written down why each one happened.

## 🧠 Why This Matters — Student vs Pro

| What a CA/pro does | What this skill does for you |
|---|---|
| Reflects on years of trades mentally | Logs every trade with structured fields — finds patterns in data |
| Recognizes recurring mistakes from experience | Auto-flags rule violations (stop-loss ignored, oversized position) |
| Tracks performance in a spreadsheet | Computes CAGR, Sharpe, drawdown automatically |
| Adjusts strategy based on what worked | Generates monthly reviews with per-sector, per-tier breakdowns |
| Has the discipline to review regularly | Creates an immutable audit trail — you can't hide from bad trades |

**The difference:** A pro has 500 trades of experience in their head. This journal gives you the same data-driven feedback loop starting from trade #1.

---

## What This Skill Does

- Logs every trade with structured fields (entry, exit, signal, size, reason)
- Computes per-trade and portfolio-level metrics
- Identifies systematic patterns (which signals work, which sectors, which times)
- Flags rule violations (stop-loss not honored, oversized positions)
- Generates monthly/quarterly performance reports
- Maintains an immutable, append-only log (audit trail)

## What This Skill Does NOT Do

- Generate trades (use `trade-rules-engine`)
- Size positions (use `risk-management`)
- Backtest historical strategy (use `psx-backtester`)
- Predict future performance — only describes past

---

## Before Implementation

| Source | Gather |
|--------|--------|
| **Codebase** | Existing journal/storage layer, accounting integration |
| **Conversation** | Date range, account, specific trade IDs, report format |
| **Skill References** | Field schema, metric formulas, classification taxonomy |
| **User Guidelines** | Where to store (CSV/SQLite/Postgres), retention policy |

---

## Trade Record Schema (MANDATORY FIELDS)

Every trade entry must capture:

```python
@dataclass
class TradeJournalEntry:
    # Identification
    trade_id: str               # ULID or UUID
    symbol: str                 # PSX ticker (e.g., "ENGRO")
    sector: str                 # PSX sector (e.g., "Fertilizer")

    # Entry
    entry_date: date
    entry_time: str             # HH:MM PKT
    entry_price: float          # PKR per share
    shares: int
    pkr_invested: float         # shares × entry_price
    entry_signal_tier: str      # "Tier 1" | "Tier 2" | "Tier 3"
    entry_rationale: str        # MA/RSI/volume conditions met
    fundamental_score: float    # 0-100 from financial-ratios-psx

    # Risk parameters at entry
    stop_loss_price: float
    stop_loss_pct: float        # 3% or 5%
    max_loss_pkr: float
    target_price: float | None
    account_balance_at_entry: float
    position_pct_of_account: float

    # Exit
    exit_date: date | None
    exit_time: str | None
    exit_price: float | None
    exit_reason: str | None     # "stop_loss" | "trailing_stop" | "ma_sell" |
                                # "rsi_overbought" | "target_hit" | "time_stop" |
                                # "manual_override" | "earnings_exit"

    # Outcome
    pnl_gross_pkr: float = 0.0
    pnl_net_pkr: float = 0.0    # after costs (commission, CDC, FED, CGT estimate)
    pnl_pct: float = 0.0
    holding_days: int = 0

    # Compliance
    rules_violated: list[str] = field(default_factory=list)
    notes: str = ""
```

**Append-only.** Never edit a closed trade entry. Corrections go in a `notes` addendum.

---

## Storage Layout

Recommended file/path:

```
data/trade-journal/
├── trades.csv              # Append-only master log
├── trades.sqlite           # Queryable mirror (optional)
├── monthly/
│   ├── 2026-01.md          # Monthly review markdown
│   ├── 2026-02.md
└── reports/
    └── ytd-2026.md
```

CSV is the source of truth (human-readable, git-trackable). SQLite for queries.

---

## Performance Metrics (research.md §10)

### Required (NON-NEGOTIABLE)

| Metric | Formula | Target |
|--------|---------|--------|
| **CAGR** | `(end_value / start_value) ** (1/years) - 1` | ≥ 15% (long-term) |
| **Win Rate** | `winning_trades / total_trades` | ≥ 50% |
| **Win/Loss Ratio** | `avg_winner_pct / abs(avg_loser_pct)` | ≥ 2.0 |
| **Max Drawdown** | `min((value - running_peak) / running_peak)` | ≤ 15% |
| **Sharpe Ratio** | `(annualized_return - 0.20) / annualized_std` | ≥ 1.0 |

Risk-free rate 0.20 (~20%) is approximate PKR T-bill yield — update from SBP quarterly.

### Recommended additional

| Metric | Why |
|--------|-----|
| **Expectancy** | `(win_rate × avg_win) - ((1-win_rate) × avg_loss)` — must be > 0 |
| **Profit factor** | `sum(wins) / sum(losses)` — should be > 1.5 |
| **Avg holding period** | Detects strategy drift (day-trading vs swing) |
| **Per-sector P&L** | Reveals which sectors actually pay |
| **Per-tier P&L** | Validates Tier 1 > Tier 2 > Tier 3 ordering |
| **Stop-loss hit rate** | If > 60% of exits = stop, entry signals are weak |

---

## Reference Implementation

```python
import pandas as pd
import numpy as np
from datetime import date

def compute_metrics(trades_df: pd.DataFrame, equity_curve: pd.Series) -> dict:
    """
    trades_df: closed trades only (exit_date not null)
    equity_curve: daily portfolio value indexed by date
    """
    closed = trades_df[trades_df["exit_date"].notna()].copy()
    if len(closed) == 0:
        return {"error": "no closed trades"}

    wins = closed[closed["pnl_net_pkr"] > 0]
    losses = closed[closed["pnl_net_pkr"] <= 0]

    avg_win_pct = wins["pnl_pct"].mean() if len(wins) else 0
    avg_loss_pct = losses["pnl_pct"].mean() if len(losses) else 0

    # Sharpe (annualized, assumes daily equity curve)
    daily_ret = equity_curve.pct_change().dropna()
    risk_free_daily = 0.20 / 252
    excess = daily_ret - risk_free_daily
    sharpe = (excess.mean() / excess.std()) * np.sqrt(252) if excess.std() > 0 else 0

    # Drawdown
    peak = equity_curve.expanding().max()
    dd = (equity_curve - peak) / peak
    max_dd = dd.min() * 100

    # CAGR
    years = (equity_curve.index[-1] - equity_curve.index[0]).days / 365.25
    cagr = (equity_curve.iloc[-1] / equity_curve.iloc[0]) ** (1/years) - 1 if years > 0 else 0

    win_rate = len(wins) / len(closed)
    win_loss = abs(avg_win_pct / avg_loss_pct) if avg_loss_pct < 0 else float("inf")
    expectancy = (win_rate * avg_win_pct) + ((1 - win_rate) * avg_loss_pct)

    return {
        "cagr_pct": round(cagr * 100, 2),
        "win_rate_pct": round(win_rate * 100, 2),
        "win_loss_ratio": round(win_loss, 2),
        "max_drawdown_pct": round(max_dd, 2),
        "sharpe": round(sharpe, 2),
        "expectancy_pct": round(expectancy, 3),
        "total_trades": len(closed),
        "avg_win_pct": round(avg_win_pct, 2),
        "avg_loss_pct": round(avg_loss_pct, 2),
        "avg_holding_days": round(closed["holding_days"].mean(), 1),
    }
```

---

## Rule-Violation Detector

After every closed trade, check:

| Check | Failure mode | Auto-flag |
|-------|--------------|-----------|
| Stop-loss honored | Exit price < stop_loss_price (gap-down OK; manual hold = violation) | `stop_violated` |
| Position ≤ 20% of account | `position_pct_of_account > 0.20` | `oversized` |
| Stop never moved down | Detect by comparing initial vs final stop | `stop_lowered` |
| No averaging down | Multiple entries in same symbol while underwater | `averaged_down` |
| Volume confirmation at entry | Entry volume ≥ 120% of 30d avg | `low_volume_entry` |
| Risk between 3-5% | `max_loss_pkr / account_balance` outside [0.03, 0.05] | `risk_violation` |

Store violations in `rules_violated` field. Monthly review summarizes them.

---

## Monthly Review Template

```markdown
# Trade Journal Review — YYYY-MM

## Headline metrics
- Closed trades: N
- Win rate: X%  (target ≥ 50%)
- Win/Loss ratio: X.XX  (target ≥ 2.0)
- P&L (net): PKR X
- Drawdown this month: -X%

## What worked
- Tier 1 signals: N trades, X% win rate
- Best sector: <sector> (PKR X)

## What broke
- N rule violations: <list>
- Worst trade: <symbol> -X% (reason)

## Action items
- [ ] If stop-violation count > 0 → review discipline, no live trades for 1 week
- [ ] If win rate < 40% over 30 trades → re-run psx-backtester on current rules
- [ ] If avg holding < 5 days → check if strategy drifted to day-trading

## Decisions
- (none / list)
```

---

---

## 🎯 Takeaway for a Student Investor

**This is your learning accelerator.** Most investors need years and hundreds of trades to build the experience that makes them profitable. This journal compresses that learning into data.

After every 20 trades, review:
- Which signal tier produced the best results? (If Tier 3 isn't working, stop using it)
- Which sectors are you good at? (Specialize in what works)
- How many rule violations? (If >1, discipline needs work)
- Is your drawdown under control? (If >15%, tighten risk)

**What the pro does:** Has the experience of hundreds of trades in their memory.

**What this skill does:** Gives you the same data after 20 trades — plus trend analysis the pro can't do from memory alone.

**The difference:** You improve faster because you measure everything.

---

## Output Checklist

- [ ] Every trade has all mandatory fields populated (no nulls in entry block)
- [ ] Append-only — no edits to closed trade rows
- [ ] CGT and commission applied to `pnl_net_pkr` (not just gross)
- [ ] All 5 NON-NEGOTIABLE metrics computed (CAGR, win-rate, w/l, drawdown, Sharpe)
- [ ] Rule-violation flags populated automatically
- [ ] Monthly review file generated under `monthly/YYYY-MM.md`
- [ ] Per-tier and per-sector breakdown included
- [ ] Equity curve persisted (daily portfolio value)
- [ ] Storage path matches project layout (`data/trade-journal/`)

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/journal-schema.md` | When adding/changing trade fields |
| `references/metric-formulas.md` | When implementing CAGR/Sharpe/drawdown |
| `references/rule-violations.md` | When extending the violation detector |
| `references/review-templates.md` | When generating monthly/quarterly reports |

## Source

Research: `research.md` §10 Performance Metrics, §11 Principle 4 ("Consistency > Excitement").
This skill closes the loop: without journaling, no learning; without learning, no edge.
