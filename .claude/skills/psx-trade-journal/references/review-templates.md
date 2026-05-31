# Review Templates

## Monthly review (auto-generated)

Path: `data/trade-journal/monthly/YYYY-MM.md`

```markdown
# Trade Journal Review — {month}

## Headline metrics
| Metric | This month | Target | Verdict |
|--------|-----------|--------|---------|
| Closed trades | {n} | 5-15 | {pass/warn/fail} |
| Win rate | {x}% | > 50% | {} |
| Win/Loss ratio | {x} | > 2.0 | {} |
| Net P&L | PKR {x} | > 0 | {} |
| Drawdown this month | {x}% | < 5% | {} |
| Sharpe (rolling 90d) | {x} | > 1.0 | {} |

## Per-tier performance
| Tier | Trades | Win rate | Avg P&L % | Total P&L |
|------|--------|----------|-----------|-----------|
| Tier 1 | ... | ... | ... | ... |
| Tier 2 | ... | ... | ... | ... |
| Tier 3 | ... | ... | ... | ... |

## Per-sector breakdown
{table}

## Rule violations this month
{count} violations:
- {tag}: {n} occurrences (trades: {ids})

## Best & worst trades
- **Best**: {symbol} +{x}% — {entry_rationale}
- **Worst**: {symbol} -{x}% — {exit_reason}

## Action items
- [ ] {auto-generated based on warn/fail flags}

## Decisions captured
- (manual addendum)
```

## Quarterly review (manual + automated)

Path: `data/trade-journal/quarterly/YYYY-Qn.md`

Sections:
1. Three-month metric trend (per-month table)
2. Strategy drift check — are we still trading per backtest assumptions?
3. Capital-tier review — has account size changed enough to shift universe?
4. Cost analysis — is friction (commission/slippage/CGT) eating into edge?
5. **Q4 only: Tax-loss harvesting review** — identify unrealized losses on <12mo positions for year-end offset
6. Decisions — any rule changes proposed (each → ADR)

## Annual / Q4 Tax-Loss Harvesting (ADR-002 D12)

Per ADR-002 Decision 12: annual Q4 routine to harvest losses on positions held < 12 months to offset realized gains.

**Process:**
1. Identify all open positions with unrealized losses held < 12 months.
2. For each, compare loss amount to realized YTD gains.
3. Harvest losses sufficient to offset gains to zero (no need to harvest more).
4. Sequence: "cut losers fast" rule takes priority — if stop-loss already triggered, that loss counts automatically.
5. Do NOT hold a position just for tax-loss harvesting — if the signal says sell, sell.

**Checklist:**
- [ ] All positions < 12 months reviewed for harvest opportunity
- [ ] Realized YTD gains calculated
- [ ] Losses harvested to offset gains (or as much as practical)
- [ ] Harvested positions logged with exit_reason = "tax_loss_harvest"
- [ ] Annual CGT bill estimated for year-end accounting

## YTD review (annual)

Path: `data/trade-journal/reports/ytd-YYYY.md`

Compare YTD live performance to:
- Backtest expectation (Sharpe, CAGR)
- KSE-100 index return
- Risk-free rate (PKR T-bill)

Verdict:
- Beating index AND beating risk-free → strategy works
- Beating index, below risk-free → strategy adds alpha but absolute returns weak
- Below index → strategy is losing edge → halt and re-backtest
- Below risk-free → STOP. Capital better in T-bills until strategy fixed

## Auto-generation

```python
def generate_monthly(year: int, month: int):
    closed = load_trades_for_month(year, month)
    equity = load_equity_curve(year, month)
    violations = aggregate_violations(closed)
    ctx = {
        "month": f"{year}-{month:02d}",
        "n": len(closed),
        "win_rate": win_rate(closed) * 100,
        "win_loss": win_loss_ratio(closed),
        "net_pnl": closed["pnl_net_pkr"].sum(),
        "drawdown": max_dd(equity) * 100,
        "sharpe": sharpe(equity),
        "by_tier": by_tier(closed),
        "by_sector": by_sector(closed),
        "violations": violations,
        "best": closed.nlargest(1, "pnl_pct").to_dict("records")[0],
        "worst": closed.nsmallest(1, "pnl_pct").to_dict("records")[0],
        "actions": derive_actions(closed, equity, violations),
    }
    render_template("monthly.md.j2", ctx,
                    out=f"data/trade-journal/monthly/{year}-{month:02d}.md")
```
