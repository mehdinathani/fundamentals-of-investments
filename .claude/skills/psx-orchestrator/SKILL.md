---
name: psx-orchestrator
description: |
  Run the end-to-end PSX (Pakistan Stock Exchange) investment pipeline by chaining
  the specialist skills in the correct order: fetch market data → apply Layer 0
  market filter → compute fundamentals → run trade rules → size positions →
  log to trade journal. Enforces the architectural ordering from research.md §4
  so no step is skipped. This skill should be used when users ask for a daily
  scan, end-to-end run, watchlist update, "what should I do today", or any
  workflow that touches more than one specialist skill.
allowed-tools: Read, Write, Bash, Skill
---

# PSX Orchestrator

The conductor of the PSX investment system. Every other skill is a single layer; this skill chains them in the order specified by `research.md` §4. Skipping a step (e.g., signals without Layer 0) is how disciplined systems become undisciplined.

## What This Skill Does

- Executes the daily/intra-day pipeline in the correct order
- Enforces gate-passing at each layer (no skipping Layer 0 → Layer 1 → ...)
- Aggregates outputs into a single decision document (today's actions)
- Calls each specialist skill with the right inputs
- Persists the run for audit (every decision is reproducible)
- Surfaces ADR-worthy moments (e.g., proposed override of a hard rule)

## What This Skill Does NOT Do

- Implement any layer's logic itself — it only orchestrates
- Execute trades automatically — output is a decision sheet, not an order
- Bypass any layer's hard rule — it cannot weaken the system

---

## Before Implementation

| Source | Gather |
|--------|--------|
| **Codebase** | Existing pipeline scripts, scheduler (cron/airflow), data store |
| **Conversation** | Account size, watchlist, run-mode (dry-run vs apply) |
| **Skill References** | Layer ordering, output contracts between skills |
| **User Guidelines** | Approved override list, blackout windows (earnings, holidays) |

---

## Pipeline (research.md §4 ordering — DO NOT REORDER)

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: psx-data-fetcher                                   │
│  → raw market data + financials for full PSX universe       │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: psx-market-filter   (Layer 0 — CRITICAL)           │
│  → tradable universe (rejects manipulated/illiquid)         │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: financial-ratios-psx   (Layer 1 — Fundamentals)    │
│  → per-stock ratio scorecard (ROE, P/E, D/E, growth)        │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: Fundamental Screen (built-in to this skill)        │
│  → watchlist of 10–20 stocks meeting research.md §4 Layer 1 │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: trade-rules-engine   (Layer 2 — Technical)         │
│  → BUY / HOLD / SELL signals with tier ratings              │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 6: risk-management   (Layer 3 — Survival)             │
│  → position sizes + stop-losses (or REJECT)                 │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 7: psx-trade-journal                                  │
│  → log proposed/executed trades for performance feedback    │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
                   Decision Sheet
```

**Hard rule:** if a step rejects a stock, it does NOT pass to the next step. There are no overrides for Layer 0 or Layer 3.

---

## Run Modes

| Mode | Behavior | Use When |
|------|----------|----------|
| `dry-run` | Run all steps, output decision sheet, write nothing | Daily review |
| `journal-only` | dry-run + write proposed trades to journal (status: pending) | Pre-market |
| `apply` | Mark journal entries as executed (broker fills entered manually) | After filling |

**Default = `dry-run`.** `apply` requires explicit user confirmation per run.

---

## Decision Sheet (output contract)

The orchestrator writes a single markdown report:

```
data/runs/YYYY-MM-DD-HHMM.md
```

Structure:

```markdown
# PSX Daily Run — 2026-05-05 09:15 PKT
Mode: dry-run | Account: PKR 2,000,000 | Capital tier: standard

## 0. Universe
- Total PSX listings considered: N
- After Layer 0 (market filter): M  (rejected: list with reasons)

## 1. Watchlist (after fundamental screen)
| Symbol | Sector | ROE | D/E | Rev CAGR 3y | Fund score |
|--------|--------|-----|-----|-------------|------------|
| ENGRO  | Fert.  | 22% | 0.4 | 11%         | 84/100     |
| ...

## 2. Today's Signals
| Symbol | Signal | Tier | Entry | Stop | Target | Volume conf | Notes |
|--------|--------|------|-------|------|--------|-------------|-------|
| OGDC   | BUY    | 1    | 102.5 | 97.4 | 117.9  | 145% avg    | ...   |

## 3. Risk-Approved Trades
| Symbol | Shares | PKR | % of acct | Max loss PKR | Stop |
|--------|--------|-----|-----------|--------------|------|
| OGDC   | 1,920  | 196,800 | 9.8%  | 9,792        | 97.4 |

## 4. Sells / Exits
| Symbol | Reason | Action |
|--------|--------|--------|
| ...

## 5. Skipped (with audit reason)
- LUCK: Layer 0 reject — operator behavior (5.4% move on 0.8× volume)
- HBL:  Layer 1 reject — D/E 0.78 > 0.6
- POWER: Layer 2 reject — RSI 78 > 70

## 6. Portfolio Snapshot
- Cash: PKR 600,000 (30%)
- Invested: PKR 1,400,000 (70%)
- Open positions: 4 / max 7
- Drawdown from peak: -2.1%

## 7. Flags & Notes
- (any rule-violation alerts from journal review)
- (ADR suggestions if any)
```

---

## Reference Pipeline Implementation

```python
def run_pipeline(account_balance, capital_tier="standard", mode="dry-run"):
    timestamp = now_pkt()
    run_id = timestamp.strftime("%Y-%m-%d-%H%M")
    decisions = []

    # Step 1: Fetch
    universe_raw = call_skill("psx-data-fetcher",
                              args={"action": "daily-bundle"})

    # Step 2: Layer 0 — Market filter
    tradable = []
    rejects_l0 = []
    for stock in universe_raw:
        result = call_skill("psx-market-filter",
                            args={"stock": stock, "capital_tier": capital_tier})
        (tradable if result.verdict == "TRADABLE" else rejects_l0).append(result)

    # Step 3: Layer 1 — Fundamentals
    scorecards = []
    for stock in tradable:
        ratios = call_skill("financial-ratios-psx",
                            args={"symbol": stock.symbol, "period": "TTM"})
        scorecards.append((stock, ratios))

    # Step 4: Fundamental screen (research.md §4 Layer 1 thresholds)
    watchlist = [
        s for s, r in scorecards
        if r["revenue_cagr_3y"] > 0.08
        and r["pat_cagr_3y"] > 0.10
        and r["debt_to_equity"] < 0.6
        and r["positive_pat_quarters_4"] >= 3
    ][:20]

    # Step 5: Layer 2 — Technical signals
    signals = []
    for stock in watchlist:
        sig = call_skill("trade-rules-engine",
                         args={"symbol": stock.symbol})
        if sig["signal"] in ("BUY", "SELL"):
            signals.append(sig)

    # Step 6: Layer 3 — Risk sizing (BUY only)
    sized = []
    for sig in (s for s in signals if s["signal"] == "BUY"):
        approved = call_skill("risk-management",
                              args={"action": "size",
                                    "entry": sig["entry"],
                                    "stop": sig["stop"],
                                    "account_balance": account_balance,
                                    "current_positions": load_positions()})
        if approved["approved"]:
            sized.append({**sig, **approved})

    # Step 7: Journal
    if mode in ("journal-only", "apply"):
        for trade in sized:
            call_skill("psx-trade-journal",
                       args={"action": "log-proposed", "trade": trade,
                             "status": "executed" if mode == "apply" else "pending"})

    write_decision_sheet(run_id, universe_raw, tradable, rejects_l0,
                         watchlist, signals, sized, mode)
    return run_id
```

---

## Hard Rules (NEVER VIOLATE)

1. **Order is fixed.** Data → L0 → L1 → screen → L2 → L3 → Journal. Never reorder.
2. **No skipping layers.** A stock cannot reach Layer 2 without passing L0 + L1.
3. **No silent overrides.** If a user override is requested, log it in the decision sheet AND surface as ADR-worthy.
4. **Default mode is `dry-run`.** Apply mode requires explicit confirmation.
5. **Single source of truth.** All run output goes to `data/runs/<run_id>.md`. No scattered logs.
6. **No new rules.** This skill orchestrates; it does NOT introduce filters or thresholds. New rules go in their owning specialist skill.

---

## ADR Triggers (suggest, do not auto-create)

Surface ADR suggestion when:

- User requests skipping or weakening Layer 0 / Layer 3 rule
- User requests changing a hard threshold (e.g., move stop from 5% to 7%)
- User requests adding a new layer or reordering existing layers
- Capital tier changes that materially expand the universe
- Strategy rules change after a journal review identifies systematic underperformance

Suggestion format:
```
📋 Architectural decision detected: <brief>. Document? Run `/sp.adr <title>`.
```

---

## Output Checklist

- [ ] All 7 steps executed in fixed order
- [ ] No step skipped (REJECT cascades, no override silently)
- [ ] Decision sheet written to `data/runs/<run_id>.md`
- [ ] Skipped stocks include audit reason (which layer + which rule)
- [ ] Run mode honored (dry-run = no writes, apply = explicit confirm)
- [ ] Portfolio snapshot included (cash %, position count, drawdown)
- [ ] ADR triggers surfaced if any rule override or threshold change requested
- [ ] Run is reproducible (same inputs → same decision sheet)
- [ ] Each specialist skill called via `Skill` tool, not reimplemented inline

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/pipeline-contract.md` | When adding/changing inter-skill data contracts |
| `references/run-modes.md` | When implementing dry-run/journal-only/apply |
| `references/decision-sheet-template.md` | When changing the decision sheet format |
| `references/override-policy.md` | When handling user-requested rule overrides |

## Source

Research: `research.md` §4 (System Architecture — full pipeline), §8 Phase 3 (Intelligent Assistant Layer).
Principle: "Discipline > Intelligence" — orchestration enforces the ordering that humans drift away from.
