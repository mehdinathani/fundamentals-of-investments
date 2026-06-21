# Decision Sheet Template

Path: `data/runs/<YYYY-MM-DD-HHMM>.md`

Single source of truth per orchestrator run. Markdown — human-readable, git-trackable, diff-friendly.

```markdown
# PSX Daily Run — {date} {time} PKT

**Mode:** {dry-run | journal-only | apply}
**Account:** PKR {balance:,}
**Capital tier:** {tier}
**Pipeline version:** v1

## 0. Universe
- Total PSX listings considered: {N}
- After Layer 0 (market filter): {M} TRADABLE, {R} REJECT, {C} CAUTION

### Top reject reasons
| Reason | Count |
|--------|-------|
| operator | {n} |
| spread | {n} |
| liquidity_volume | {n} |
| volume_spike | {n} |
| circuit | {n} |

## 1. Watchlist (post fundamental screen)
{<= 20 rows}

| Symbol | Sector | ROE | D/E | Rev CAGR 3y | PAT CAGR 3y | Fund score |
|--------|--------|-----|-----|-------------|-------------|------------|
| ENGRO  | Fert.  | 22% | 0.4 | 11%         | 14%         | 84         |

## 2. Today's Signals (BUY / SELL only)
| Symbol | Signal | Tier | Entry | Stop | Target | Volume conf | Rationale |
|--------|--------|------|-------|------|--------|-------------|-----------|

## 3. Risk-Approved Trades (BUY)
| Symbol | Shares | PKR invested | % of account | Max loss PKR | Stop |
|--------|--------|--------------|--------------|--------------|------|

### Risk rejections (if any)
| Symbol | Reason |
|--------|--------|

## 4. Sells / Exits
| Symbol | Held since | Reason | Action |
|--------|------------|--------|--------|

## 5. Skipped (audit trail)
- LUCK: Layer 0 reject — operator behavior (5.4% move on 0.8× volume)
- HBL:  Layer 1 reject — D/E 0.78 > 0.6
- POWER: Layer 2 reject — RSI 78 > 70

(Truncate beyond 50 entries; keep summary count.)

## 6. Portfolio Snapshot
- Cash: PKR {x:,} ({y}%)
- Invested: PKR {x:,} ({y}%)
- Open positions: {n} / max 7
- Drawdown from peak: {z}%
- Open positions detail:

| Symbol | Shares | Entry | Current | P&L % | Days held | Stop |
|--------|--------|-------|---------|-------|-----------|------|

## 7. Flags & Notes
- {Rule violations from journal review, if any}
- {ADR triggers, if any}
- {Stale signals or data gaps, if any}

## 8. Manifest (for reproducibility)
- Data fetched at: {iso timestamp}
- Number of stocks fetched: {N}
- Skill versions:
  - psx-data-fetcher: v1
  - psx-market-filter: v1
  - financial-ratios-psx: v1
  - trade-rules-engine: v1
  - risk-management: v1
  - psx-trade-journal: v1
- Run hash: {sha256 of inputs} (for tamper-evidence)
```

## Why markdown

- Diffable in git: see exactly what changed day-over-day.
- Human-readable: review on phone, in editor, on laptop.
- Greppable: easy to scan history for patterns.
- No vendor lock-in: not tied to a JSON viewer or DB tool.

## Why a manifest

If a decision is later questioned ("why did we buy LUCK on 2026-04-12?"), the manifest plus the source data lets the run be replayed exactly. Reproducibility is non-negotiable for a disciplined system.
