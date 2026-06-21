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

## 👤 Who This Is For

**This is where everything comes together.** Think of a professional investment firm: they have a team of analysts (each specializing in one thing) and a portfolio manager who chains their work together.

- **Data team** fetches the numbers → `psx-data-fetcher`
- **Risk officer** rejects bad stocks → `psx-market-filter`
- **Fundamental analyst** computes ratios → `financial-ratios-psx`
- **Technical analyst** generates signals → `trade-rules-engine`
- **Risk manager** sizes positions → `risk-management`
- **Performance analyst** logs everything → `psx-trade-journal`

**You are the portfolio manager.** This skill is your team.

## 🧠 Why This Matters — Student vs Pro

| What a team of analysts does | What this skill does for you |
|---|---|
| Full-time data team fetches and cleans PSX data | Runs `psx-data-fetcher` in minutes |
| Risk officer screens for manipulation/liquidity | Applies Layer 0 filter before any analysis |
| CA analyst computes ratios and builds watchlist | Runs `financial-ratios-psx` + fundamental screen |
| Technical analyst reads charts for entry/exit | Runs `trade-rules-engine` for signals |
| Risk manager enforces position limits | Runs `risk-management` — blocking oversized trades |
| Performance analyst tracks all trades | Runs `psx-trade-journal` with auto-metrics |

**A full investment team costs PKR 5-20 million/year. This pipeline costs nothing and runs in minutes.**

---

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
│  STEP 0: Pre-Pipeline Checks (REGIME-SHIFT + ENTRY CAP)     │
│  → Check: 3+ stops in 5 trading days? → halt new entries    │
│  → Check: ≥ 2 entries this week? → queue remaining BUYs     │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
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

## 📊 Evidence-Based Signals — No Blind Trust

**Critical rule:** Every BUY/SELL/HOLD signal must include the complete evidence chain. The user should never have to "trust the AI" — they should see exactly why each decision was made.

A CA analyst justifies every trade recommendation with evidence (financial statements, charts, ratios). This system does the same — with clear, traceable reasoning.

### Signal Evidence Format

Every signal output must include:

```
BUY: OGDC @ 102.50
├─ Layer 0 (Market Filter): ✅ PASS
│   ├─ Volume: 1.2M (avg 800K) → ✅ Above liquidity floor
│   ├─ Spread: 0.35% → ✅ Below 2% threshold
│   └─ No operator behavior detected → ✅ Clean
├─ Layer 1 (Fundamentals): ✅ PASS
│   ├─ ROE: 18.5% (KSE-100 median: 14.2%) → ✅ ABOVE benchmark
│   ├─ D/E: 0.32 (KSE-100 median: 0.48) → ✅ BELOW benchmark (less debt)
│   ├─ Rev CAGR 3yr: 12.1% (KSE-100 median: 8.5%) → ✅ ABOVE benchmark
│   └─ PAT CAGR 3yr: 15.3% → ✅ Above 10% threshold
├─ Layer 2 (Technical): ✅ SIGNAL TRIGGERED
│   ├─ MA20 (98.5) crossed ABOVE MA50 (96.2) → ✅ Golden cross
│   ├─ Price (102.5) ABOVE MA200 (88.0) → ✅ Uptrend confirmed
│   ├─ RSI(14): 55.2 (neutral zone 40-60) → ✅ Not overbought
│   └─ Volume: 145% of 30-day avg → ✅ Confirmed
├─ Layer 3 (Risk): ✅ APPROVED
│   ├─ Position: 1,920 shares × 102.50 = PKR 196,800 (9.8% of account)
│   ├─ Stop-loss: 97.40 (5%) → Max loss: PKR 9,792 (0.49% of account)
│   └─ Account capacity: 4 open positions (7 max, 30% cash) → ✅
└─ Signal Quality: TIER 1 (Strong Buy)
```

### Heatmaps (Visual Evidence)

Generate sector-level heatmaps to show where the market is moving:

```python
# Sector Performance Heatmap (last 5 trading days)
# Colors: 🔥 Green = strong positive, 🟡 Yellow = flat, 🔴 Red = negative
#
# ┌────────────────────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
# │ Sector                 │ Mon      │ Tue      │ Wed      │ Thu      │ Fri      │
# ├────────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
# │ 🏭 Cement              │ +1.2%    │ -0.5%    │ +2.1%    │ +0.8%    │ +1.5%    │
# │ 🏦 Commercial Banks    │ +0.3%    │ +0.1%    │ -0.2%    │ +0.4%    │ -0.1%    │
# │ ⛽ Oil & Gas           │ -0.8%    │ -1.2%    │ +0.5%    │ -0.3%    │ +0.7%    │
# │ 💊 Pharma              │ +0.1%    │ -0.3%    │ -0.1%    │ +0.2%    │ -0.4%    │
# │ 💻 Technology          │ +3.5%    │ +2.8%    │ -1.0%    │ +4.2%    │ +1.8%    │
# └────────────────────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
```

**Purpose:** A student can immediately see which sectors are hot (green) and which are cooling (red) — without needing to interpret raw numbers.

### Trade Bars (Price Evidence)

For each signal, show the stock's recent price action with visual markers:

```
OGDC — Last 20 Trading Days
Price: ┤ 98  100  101  100  99   101  102  101  100  102  103  102  104  103  102  101  102  103  102  102.5
MA20:  ┤ 97   97   98   98   98   98   98   98   98   98   98   99   99   99   99   99   99   99   99   98.5
MA50:  ┤ 95   95   95   95   95   95   95   95   96   96   96   96   96   96   96   96   96   96   96   96.2
Vol:   ┤ 0.8  0.9  1.1  0.7  0.6  1.3  1.5  0.9  0.8  1.2  1.4  1.1  0.9  1.0  0.7  0.8  1.1  1.3  1.2  1.5
                                                                                              ↑BUY
Signal: MA20(98.5) crossed above MA50(96.2) on Day 20 with volume 1.5M (145% of avg)
```

**Purpose:** The student can visually see the crossover and volume spike that triggered the signal — evidence they can verify with their own eyes.

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

## 0. Market Overview — Heatmap
[Sector performance heatmap for last 5 days — see Heatmap section above]

## 1. Universe
- Total PSX listings considered: N
- After Layer 0 (market filter): M  (rejected: list with reasons)

## 2. Watchlist (after fundamental screen)
| Symbol | Sector | ROE | D/E | Rev CAGR 3y | vs KSE-100 | Fund score |
|--------|--------|-----|-----|-------------|------------|------------|
| ENGRO  | Fert.  | 22% | 0.4 | 11%         | ABOVE avg  | 84/100     |
| ...

## 3. Today's Signals — With Full Evidence
<for each BUY/SELL/HLD signal, include the full evidence block>
[See Signal Evidence Format above]

## 4. Risk-Approved Trades
| Symbol | Shares | PKR | % of acct | Max loss PKR | Stop |
|--------|--------|-----|-----------|--------------|------|
| OGDC   | 1,920  | 196,800 | 9.8%  | 9,792        | 97.4 |

## 5. Sells / Exits
| Symbol | Reason | Action |
|--------|--------|--------|
| ...

## 6. Skipped (with audit reason)
- LUCK: Layer 0 reject — operator behavior (5.4% move on 0.8× volume)
- HBL:  Layer 1 reject — D/E 0.78 > 0.6 (KSE-100 median: 0.48)
- POWER: Layer 2 reject — RSI 78 > 70 (overbought)

## 7. Portfolio Snapshot
- Cash: PKR 600,000 (30%)
- Invested: PKR 1,400,000 (70%)
- Open positions: 4 / max 7
- Drawdown from peak: -2.1%

## 8. Flags & Notes
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

    # Step 1b: Check entry cap (max 2 entries per week)
    week_entries = count_entries_this_week(trades_journal)
    if week_entries >= 2:
        log(f"Entry cap reached: {week_entries}/2 entries this week")
        # Still run pipeline, but queue BUY signals
        queue_buys_for_next_week = True
    else:
        queue_buys_for_next_week = False

    # Step 1c: Check regime-shift (3+ stops in 5 days)
    recent_stops = count_stops_last_5_days(trades_journal)
    if recent_stops >= 3:
        halt_new_entries = True
        log(f"REGIME SHIFT DETECTED: {recent_stops} stops in 5 days — halting new entries")
        surface_adr_suggestion("Regime shift detected — review macro thesis before resuming")
    else:
        halt_new_entries = False

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
