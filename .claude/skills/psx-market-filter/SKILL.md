---
name: psx-market-filter
description: |
  Apply Layer 0 Market Reality Filter for PSX (Pakistan Stock Exchange) — reject
  manipulated, illiquid, or untradable stocks BEFORE any fundamental or technical
  analysis. This skill should be used when users ask to filter the PSX universe,
  detect operator-driven price action, screen for liquidity, identify pump-and-dump
  patterns, or build a tradable universe from raw PSX listings. This is the first
  gate in the PSX investment system — no stock proceeds to ratio analysis or signal
  generation without passing this filter.
allowed-tools: Read, Write, Bash
---

# PSX Market Filter (Layer 0)

## 👤 Who This Is For

**You are a student who knows the basics of investing.** You understand what a stock is, what "buy low, sell high" means, and maybe you've followed a few PSX stocks on a broker app. But you don't have:

- 10 years of market experience (the "old investor")
- ACCA/CA qualifications in financial analysis
- A research team producing reports

**That's fine.** This skill automates what experienced pros do instinctively — reject bad stocks before they waste your time (and money). While they use gut feel from years of watching the market, you use hard rules. And on PSX, rules beat gut feel.

---

## 🧠 Why This Matters — Student vs Pro

| What a CA/CFA analyst does | What this skill does for you |
|---|---|
| Scans 500+ stocks, mentally rejects illiquid ones from years of experience | Applies 6 hard filters automatically — no experience needed |
| Recognizes manipulation patterns from seeing them for 10+ years | Detects operator behavior with math (price + volume rules) |
| Knows which stocks become untradable due to circuit breakers | Flags circuit-locked stocks immediately |
| Calculates spread cost before entering | Rejects stocks where the spread alone destroys profit |

**You start with the same clean universe they start with — but you get there in seconds, not years.**

---

## What This Skill Does

- Rejects stocks with insufficient liquidity (volume, value traded, freefloat)
- Rejects stocks with wide bid-ask spreads (transaction cost too high)
- Detects operator-driven price action (price moves disproportionate to volume = manipulation)
- Detects suspicious volume spikes (potential pump activity — the #1 beginner trap on PSX)
- Flags circuit-locked stocks (unable to exit cleanly)
- Outputs a **tradable universe** — the only set allowed downstream

## What This Skill Does NOT Do

- Fetch raw market data (use `psx-data-fetcher`)
- Compute fundamentals (use `financial-ratios-psx`)
- Generate signals (use `trade-rules-engine`)
- Make trade decisions — it only decides *eligibility*

---

## Before Implementation

| Source | Gather |
|--------|--------|
| **Codebase** | Existing universe builder, watchlist source, data schema |
| **Conversation** | Capital tier, sector preferences, KSE-100 only vs full board |
| **Skill References** | Filter thresholds from `references/`, manipulation patterns |
| **User Guidelines** | Any whitelist (e.g., always allow ENGRO, OGDC) or blacklist |

---

## Filter Pipeline (apply in order; first failure = REJECT)

### 🔍 Filter 1 — Liquidity Floor (HARD)

**In plain language:** Can you actually buy and sell this stock without getting stuck?

Imagine you buy 1,000 shares of a stock, then try to sell them a week later — but nobody is buying. You're stuck. This filter prevents that.

- **Volume** = how many shares trade hands daily. Low volume = you might not find a buyer when you want to exit.
- **Value** = volume × price. PKR 5M/day means there's real money flowing through this stock.
- **Freefloat** = % of shares available to the public (not held by founders/family). Low freefloat = a few people control the price.
- **Days traded** = has this stock traded every day? Stale stocks don't move.

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| 30-day avg daily volume | ≥ 50,000 shares | Below = cannot exit cleanly |
| 30-day avg daily value | ≥ PKR 5,000,000 | Below = price impact on entry/exit |
| Freefloat | ≥ 25% of issued capital | Below = sponsor-controlled |
| Days traded in last 30 | ≥ 25 of 30 | Below = stale, untradable |

**Reject if any threshold fails.** Conservative tier (capital < PKR 1M) tightens these by 2×.

### 🔍 Filter 2 — Spread Check (HARD)

**In plain language:** How much do you lose the moment you buy?

The "spread" is the gap between what buyers are willing to pay (bid) and what sellers want (ask). When you buy a stock, you pay the ask price. If you immediately sold, you'd get the bid price. The spread is your instant loss.

- **Spread < 0.5%** = Top-tier liquid stock (like KSE-30). Great.
- **Spread 0.5-2%** = Acceptable for most KSE-100 stocks.
- **Spread > 2%** = Reject. You lose 2% before the stock even moves. An experienced trader knows this instinctively — this filter encodes it as a rule.

```
spread_pct = (best_ask - best_bid) / last_price × 100
```

| Spread | Action |
|--------|--------|
| < 0.5% | PASS (KSE-30 tier liquidity) |
| 0.5% – 2% | PASS (acceptable for KSE-100) |
| > 2% | REJECT (transaction cost destroys edge) |

For mid-caps, use 5-day average spread, not snapshot (intraday spreads spike).

### 🔍 Filter 3 — Operator-Behavior Detector (HARD)

**In plain language:** Is this stock being manipulated?

On PSX, some stocks are "operated" — a group of traders pushes the price up on low volume (cheap to manipulate), then dumps on retail buyers who jump in late. This is the #1 way beginners lose money on PSX.

- **Price moves > 5% but volume is normal or low** → Suspicious. Real demand requires real volume.
- **3+ days of >3% moves with declining volume** → Classic pump before dump.

A CA analyst spots this from experience. This filter gives you that same pattern recognition.

Operator-driven action = price moving without genuine demand. Pattern:

```
price_move_pct = abs((close - prev_close) / prev_close)
volume_ratio   = today_volume / 30d_avg_volume

Operator flag if:
  price_move_pct > 5% AND volume_ratio < 1.0
  (big move on average-or-below volume = artificial)

OR:
  3+ consecutive days of >3% moves with declining volume
  (classic mark-up before dump)
```

**Reject** flagged stocks for 10 trading days, then re-evaluate.

### Filter 4 — Volume Spike Investigation (CAUTION)

| Volume vs 30-day avg | Action |
|----------------------|--------|
| 100% – 200% | Normal — proceed |
| 200% – 300% | Note, check for news/results |
| 300% – 500% | CAUTION — require news justification, else WAIT |
| > 500% | REJECT for 5 days unless announced corporate action |

Volume spikes in mid-caps without news are the #1 PSX manipulation signature.

### 🔍 Filter 5 — Circuit-Lock Filter (HARD)

**In plain language:** Is this stock stuck at its daily price limit?

PSX limits how much a stock can move in one day (5% or 7.5% depending on the board). When a stock hits this limit, trading effectively stops — there are only buyers (upper circuit) or only sellers (lower circuit).

- **Upper circuit** → You can buy but the price is already maxed. If it opens lower tomorrow, you lose immediately.
- **Lower circuit** → You can't sell even if you want to. Your money is trapped.
- **Hit circuit 2+ times in 5 days** → This stock is too volatile. Avoid.

**Pro insight:** Beginners chase stocks hitting upper circuits (FOMO). Experienced investors know that once a stock hits circuit, the real game is when it reopens — not during the lock.

PSX has 5%/7.5% daily circuit breakers (varies by board).

| State | Action |
|-------|--------|
| Upper circuit (lock-up) | SKIP entry — buyer flood, can't size |
| Lower circuit (lock-down) | SKIP exit attempts — no buyers, slippage |
| Hit circuit ≥ 2 days in last 5 | REJECT — volatility too high |

### Filter 6 — Information Asymmetry Flag (ADVISORY)

| Signal | Action |
|--------|--------|
| Price gap > 3% on no-news day | INVESTIGATE — likely insider flow |
| Volume + price move 1 day before earnings | NOTE — possible pre-leak |
| Sponsor sale announcement within 30 days | DOWN-WEIGHT — supply overhang |

---

## Reference Implementation

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class FilterResult:
    symbol: str
    verdict: Literal["TRADABLE", "REJECT", "CAUTION"]
    failed_filter: str | None
    reasons: list[str]

def market_reality_filter(stock: dict, capital_tier: str = "standard") -> FilterResult:
    """
    stock keys required:
      symbol, last_price, prev_close, today_volume, vol_30d_avg,
      value_30d_avg, freefloat_pct, days_traded_30, bid, ask,
      consecutive_circuit_days_5
    """
    reasons = []

    vol_floor = 100_000 if capital_tier == "conservative" else 50_000
    val_floor = 10_000_000 if capital_tier == "conservative" else 5_000_000

    # Filter 1: Liquidity
    if stock["vol_30d_avg"] < vol_floor:
        return FilterResult(stock["symbol"], "REJECT", "liquidity_volume",
                            [f"30d avg volume {stock['vol_30d_avg']} < {vol_floor}"])
    if stock["value_30d_avg"] < val_floor:
        return FilterResult(stock["symbol"], "REJECT", "liquidity_value",
                            [f"30d avg value {stock['value_30d_avg']} < {val_floor}"])
    if stock["freefloat_pct"] < 0.25:
        return FilterResult(stock["symbol"], "REJECT", "freefloat",
                            [f"Freefloat {stock['freefloat_pct']:.1%} < 25%"])
    if stock["days_traded_30"] < 25:
        return FilterResult(stock["symbol"], "REJECT", "stale",
                            [f"Traded only {stock['days_traded_30']} of 30 days"])

    # Filter 2: Spread
    spread_pct = (stock["ask"] - stock["bid"]) / stock["last_price"] * 100
    if spread_pct > 2.0:
        return FilterResult(stock["symbol"], "REJECT", "spread",
                            [f"Spread {spread_pct:.2f}% > 2%"])

    # Filter 3: Operator behavior
    move_pct = abs((stock["last_price"] - stock["prev_close"]) / stock["prev_close"])
    vol_ratio = stock["today_volume"] / stock["vol_30d_avg"]
    if move_pct > 0.05 and vol_ratio < 1.0:
        return FilterResult(stock["symbol"], "REJECT", "operator",
                            [f"Move {move_pct:.1%} on volume ratio {vol_ratio:.2f}"])

    # Filter 4: Volume spike
    if vol_ratio > 5.0:
        return FilterResult(stock["symbol"], "REJECT", "volume_spike",
                            [f"Volume {vol_ratio:.1f}× avg — investigate"])
    if vol_ratio > 3.0:
        reasons.append(f"Caution: volume {vol_ratio:.1f}× avg")

    # Filter 5: Circuit
    if stock.get("consecutive_circuit_days_5", 0) >= 2:
        return FilterResult(stock["symbol"], "REJECT", "circuit",
                            ["Hit circuit ≥ 2 of last 5 days"])

    verdict = "CAUTION" if reasons else "TRADABLE"
    return FilterResult(stock["symbol"], verdict, None, reasons)
```

---

## Capital-Tier Adjustments

| Capital | Universe | Liquidity Threshold |
|---------|----------|---------------------|
| < PKR 500K | KSE-30 only (top 30 most liquid) | 2× standard |
| PKR 500K – 1M | KSE-100 top 50 | 1.5× standard |
| ≥ PKR 1M | KSE-100 (all 100) | Standard |
| ≥ PKR 5M | KSE-100 + select KMI-30 | Standard |

Smaller capital → narrower universe. This is from `research.md` §7.

---

---

## 🎯 Takeaway for a Student Investor

After this filter runs, you have **the same tradable universe a CA analyst would build** — minus the 10 years of market experience they needed to get there.

**What the pro does:** Mentally filters 500 stocks, rejects 400 by gut feel from experience.

**What this skill does:** Applies 6 mathematical filters, rejects the same 400 stocks with hard data.

**The difference:** None in the output. All in the process. Your output is cleaner because math doesn't have bad days.

---

## Output Checklist

- [ ] All 5 hard filters applied in order
- [ ] Verdict is one of: TRADABLE, REJECT, CAUTION
- [ ] REJECT includes specific failed_filter field for audit
- [ ] Capital tier adjusts thresholds (conservative tightens 2×)
- [ ] Operator-behavior check uses BOTH price move AND volume ratio (not either alone)
- [ ] Output is a list of TRADABLE symbols — the universe for downstream skills
- [ ] Filter run is logged with timestamp (for backtest reproducibility)

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/manipulation-patterns.md` | When tuning operator-detection logic |
| `references/liquidity-tiers.md` | When choosing capital-tier thresholds |
| `references/circuit-rules.md` | When handling circuit-locked stocks |
| `references/freefloat-data.md` | When sourcing freefloat percentages |

## Source

Research: `research.md` §3 (Market Reality), §4 Layer 0 (Market Reality Filter — CRITICAL).
Principle: "Discipline > Intelligence" — Layer 0 enforces discipline before analysis.

---

## Layer 1.5 — Macro Overlay (ADR-003)

After Layer 0 passes a stock, the macro state is checked before proceeding to fundamental/technical analysis. Macro state is checked per ADR-003 macro-states.md.

### Macro State Lookup

Before each pipeline run, determine macro state from `references/macro-states.md`:

**Risk-off triggers (any one → risk-off):**
- SBP hiking rates
- USD/PKR weakened >5% in 30 days
- IMF program at risk or review missed
- KSE-100 P/E > 10-yr median + 1SD

**Universe adjustment by state:**
- Risk-on → full tradable universe
- Neutral → full tradable universe, conservative sizing
- Risk-off → restrict to defensives (utilities, cash-rich, food) or 100% cash

When risk-off, the operator-behavior and volume-spike filters tighten by 1.5× (manipulation is more likely in macro stress).
