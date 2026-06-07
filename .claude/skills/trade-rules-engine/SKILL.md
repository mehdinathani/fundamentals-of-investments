---
name: trade-rules-engine
description: |
  Apply exact entry and exit rules for PSX (Pakistan Stock Exchange) equity trading.
  Encodes MA crossover logic, RSI thresholds, volume confirmation, and breakout
  rules specific to PSX's market structure. This skill should be used when users
  ask to define trading rules, generate buy/sell signals, set entry/exit criteria,
  or build a rules-based trading system for PSX stocks.
allowed-tools: Read, Write, Bash, mcp__context7__query-docs, mcp__context7__resolve-library-id
---

# Trade Rules Engine

## 👤 Who This Is For

**You are a student with basic investing knowledge.** You know what "buy low, sell high" means. You maybe understand that moving averages exist. But you don't have:

- 5,000+ hours of chart time (experienced traders)
- A CA/CFA qualification in technical analysis
- The discipline to follow rules when emotions run high

**This skill is your edge.** Experienced traders develop "chart intuition" from years of watching price action. You don't have that — but you have hard rules. On PSX, where manipulation is common and emotions kill returns, hard rules consistently outperform intuition.

## 🧠 Why This Matters — Student vs Pro

| What an experienced trader does | What this skill does for you |
|---|---|
| Looks at a chart and "feels" whether to buy | Applies MA crossover + RSI + volume rules — removes emotion |
| Spots golden crosses from memory | Calculates exact crossover points automatically |
| Reads volume as "heavy" or "light" | Compares against precise 30-day averages |
| Recognizes overbought/oversold from experience | Uses exact RSI 30/70 thresholds |
| Gets stopped out and learns the hard way | Encodes 5% stop-loss as a hard rule, not a suggestion |

**You follow rules. They follow feelings. Rules beat feelings over 100 trades.**

---

## What This Skill Does

- Defines exact MA crossover parameters (periods, confirmation rules)
- Sets RSI thresholds for overbought/oversold conditions
- Encodes volume confirmation requirements (minimum volume, spike detection)
- Documents breakout rules with PSX-specific constraints (circuit breakers, liquidity)
- Provides complete BUY / HOLD / SELL signal logic

## What This Skill Does NOT Do

- Fetch price data (use `psx-data-fetcher` skill)
- Calculate financial ratios (use `financial-ratios-psx` skill)
- Manage risk or position sizing (use `risk-management` skill)
- Execute trades or connect to brokers

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing signal generation code, pandas/TA-lib usage |
| **Conversation** | Which stocks/symbols, timeframe (daily/intraday), backtest vs live |
| **Skill References** | Rule definitions from `references/`, parameter tables |
| **User Guidelines** | Any overrides to standard thresholds, watchlist preferences |

Ensure all required context is gathered before implementing.

---

## Core Trading Rules (DO NOT MODIFY)

These rules are the system's edge. Changing them requires explicit user consent and ADR documentation.

### Rule 1: Market Reality Filter (Layer 0) — APPLY FIRST

Before any technical or fundamental analysis, reject untradable stocks.

| Filter | Condition | Action |
|--------|-----------|--------|
| **Liquidity** | 30-day avg volume < 50,000 shares | REJECT from watchlist |
| **Spread** | Bid-ask spread > 2% of last price | REJECT (use KSE-100 stocks only) |
| **Volume spike** | Single-day volume > 5× 30-day average | CAUTION — investigate news/manipulation |
| **Operator behavior** | Price moves > 5% on < 30-day avg volume | AVOID — likely manipulated |
| **Circuit breaker** | Stock in upper/lower lock (hit circuit) | SKIP — wait for normal trading |

**Output**: Tradable universe (subset of all PSX stocks)

---

### Rule 2: Fundamental Screen (Layer 1) — APPLY SECOND

From tradable universe, select fundamentally strong companies.

| Metric | Threshold | Action |
|--------|-----------|--------|
| Revenue growth | 3-year CAGR > 8% | KEEP |
| Profit growth | 3-year PAT CAGR > 10% | KEEP |
| Earnings consistency | Positive PAT in ≥ 3 of last 4 quarters | KEEP |
| Debt-to-Equity | < 0.6 | KEEP (lower is better) |
| Sector momentum | Sector in top 50% by index performance | KEEP |
| Sector bottom-quartile | Sector in bottom 25% of index performance | REJECT regardless of stock fundamentals (ADR-002 D9) |

**Output**: Watchlist of 10-20 stocks

---

### Rule 3: Technical Entry Rules (Layer 2)

Generate BUY signals only when ALL conditions are met:

#### 3A. Moving Average Crossover (MANDATORY)

**In plain language:** Is the stock trending up or down?

A "moving average" is just the average price over the last N days. It smooths out daily noise so you can see the real direction.

- **20-day SMA** = Short-term trend (last month)
- **50-day SMA** = Medium-term trend (last 2.5 months)
- **200-day SMA** = Long-term trend (last 10 months)

The "golden cross" (20-day crossing above 50-day) means the short-term trend is getting stronger than the medium-term trend — a classic buy signal. Being above the 200-day means the long-term trend is also up.

**What a pro does:** Glances at a chart and spots the crossover visually in seconds. This skill does the math — no chart reading required.

```
BUY signal triggers when ALL of:
  1. 20-day SMA crosses ABOVE 50-day SMA (golden cross short-term)
  2. Price is ABOVE 200-day SMA (long-term uptrend confirmation)
  3. Crossover occurs with volume > 120% of 30-day avg volume

SELL signal triggers when ANY of:
  1. 20-day SMA crosses BELOW 50-day SMA
  2. Price closes BELOW 200-day SMA for 3 consecutive days
```

**Parameters:**

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Fast MA | 20-day SMA | Captures short-term momentum |
| Slow MA | 50-day SMA | Filters noise, confirms trend |
| Trend MA | 200-day SMA | Long-term bias filter |
| Volume confirmation | > 120% of 30-day avg | Avoids low-conviction signals |

#### 3B. RSI Threshold (MANDATORY — use with MA crossover)

**In plain language:** Is the stock overbought or oversold?

The Relative Strength Index (RSI) measures how strong recent price changes are on a scale of 0-100. Think of it as a "momentum meter":

- **RSI < 30** = Oversold. The stock has fallen too fast and may bounce back. Consider buying.
- **RSI 30-40** = Weakening. The stock is losing momentum. Watch for recovery.
- **RSI 40-60** = Neutral. Normal range. No strong signal either way.
- **RSI 60-70** = Strengthening. The stock is gaining momentum but not yet overbought.
- **RSI > 70** = Overbought. The stock has risen too fast and may pull back. Consider selling.

**⚠️ PSX-specific:** On PSX, stocks can stay overbought (RSI > 70) for weeks in a strong uptrend. Never short a stock just because RSI is high — wait for the MA crossover to confirm a sell signal.

**What a pro does:** Knows these thresholds from experience and can spot them on a chart instantly. This skill removes the guesswork.

```
BUY: RSI(14) is between 40 and 60 (neutral zone, entering momentum)
     OR RSI(14) crosses ABOVE 30 (recovering from oversold)

SELL: RSI(14) > 70 (overbought — consider partial profit)
      OR RSI(14) crosses BELOW 50 with MA sell signal (momentum breakdown)
```

**RSI Parameters:**

| Parameter | Value |
|-----------|-------|
| Period | 14 days |
| Oversold | < 30 |
| Overbought | > 70 |
| Neutral zone | 40-60 |

#### 3C. Volume Confirmation (MANDATORY)

**In plain language:** Is anyone else buying this stock?

Volume measures how many shares are trading. Low volume means few people are interested. A price move on low volume is unreliable — it could be one big trader manipulating the price.

- **Volume > 120% of 30-day avg** = Genuine interest. Confident signal.
- **Volume < 100%** = Weak. Skip the trade — the move might not last.
- **Volume > 300%** = Spike. Check for news. Could be a pump that reverses tomorrow.

**⚠️ This is THE beginner trap on PSX:** Beginners see a stock moving up and buy without checking volume. The stock then reverses because there was no genuine demand. This rule prevents that mistake.

**What a pro does:** Scans volume bars on a chart and instantly knows if volume is "heavy" or "light." This skill gives you the same information as numbers.

```
Every BUY signal MUST have volume confirmation:
  - Day of signal: volume ≥ 120% of 30-day average
  - If volume < 100% of 30-day avg → NO TRADE (weak conviction)

Volume spike warning:
  - volume > 300% of 30-day avg → Investigate (news/pump)
  - If unexplained → WAIT for normalization
```

#### 3D. Support & Resistance (ADVISORY)

```
BUY: Price near identified support level (within 3%)
     with volume confirmation

SELL: Price near identified resistance level (within 3%)
      OR breakout above resistance with volume > 150% avg (hold for trend)
```

---

### Rule 4: Exit Rules

#### 4A. Stop-Loss (MANDATORY — see `risk-management` skill)

```
Stop-loss = Entry Price × (1 - max_loss%)
Default max_loss = 5% (conservative: 3%)
NEVER move stop-loss down. Only trail up.
```

#### 4B. Profit-Taking (ADVISORY)

```
Partial profit at +15%: Sell 50% of position
Trail stop to breakeven after +10%
Full exit at +25% OR technical sell signal
```

#### 4C. Time Stop (ADVISORY)

```
If position is open > 3 months without +10% gain → Re-evaluate fundamentals
If position is losing for > 2 months → Check for structural issues
```

#### 4D. CGT-Aware Exit Deferral (SOFT — ADR-002 D7)

When a profit-taking exit fires (e.g., MA sell signal, RSI > 70) within **30 calendar days of the 6-month holding boundary**, and technicals remain neutral, defer exit to cross the lower CGT bracket.

**CGT Brackets (filer rates):**
| Holding | Rate |
|---------|------|
| < 6 months | 15% |
| 6-12 months | 12.5% |
| 12-24 months | 10% |
| > 24 months | 0% |

**Deferral conditions (ALL must be met):**
1. Exit signal is profit-taking (NOT stop-loss, NOT trend-reversal)
2. Within 30 days of 6-month holding period
3. Technicals are neutral: RSI between 30-70, no MA crossover sell signal
4. No macro risk-off condition (check Layer 1.5)

**CGT deferral MUST NOT override:**
- Stop-loss exits (Rule 4A — hard rule)
- Trend-reversal exits (20-day SMA crosses below 50-day SMA)
- RSI > 70 with MA confirmation
- Risk-off macro state (cash preservation)

---

## Signal Output — Must Include Full Evidence

**Every signal must return the reasoning chain, not just the verdict.** The user should see exactly why each rule triggered.

```python
@dataclass
class SignalResult:
    symbol: str
    signal: Literal["BUY", "HOLD", "SELL"]
    tier: Literal["Tier 1", "Tier 2", "Tier 3", None] = None
    evidence: dict = field(default_factory=dict)
    # evidence = {
    #     "ma_crossover": {"ma20": 98.5, "ma50": 96.2, "status": "bullish_cross"},
    #     "rsi": {"value": 55.2, "zone": "neutral", "status": "pass"},
    #     "volume": {"current": 1.5e6, "avg_30d": 1.03e6, "ratio": 1.45, "status": "confirmed"},
    #     "trend": {"price": 102.5, "ma200": 88.0, "status": "above"},
    #     "reason": "MA20(98.5) crossed above MA50(96.2) with RSI 55.2 (neutral) and volume 145% of 30d avg"
    # }
```

## Complete Signal Logic

```python
def generate_signal(price_data, volume_data, ma_20, ma_50, ma_200, rsi_14):
    """
    Returns: SignalResult with signal + full evidence dict
    """
    evidence = {
        "ma_crossover": {"ma20": ma_20, "ma50": ma_50, "ma200": ma_200},
        "rsi": {"value": rsi_14, "zone": "neutral" if 40 <= rsi_14 <= 60 else "overbought" if rsi_14 > 70 else "oversold" if rsi_14 < 30 else "weak"},
        "volume": {"current": volume_today, "avg_30d": volume_30d_avg, "ratio": volume_today / volume_30d_avg},
        "trend": {"price": current_price, "ma200": ma_200},
    }

    # 1. Check stop-loss (highest priority)
    if current_price <= entry_price * 0.95:
        evidence["reason"] = f"Stop-loss hit: Price {current_price} ≤ entry {entry_price} × 0.95"
        return SignalResult("SELL", evidence=evidence)

    # 2. Check MA crossover sell
    if ma_20 < ma_50:
        evidence["reason"] = f"MA20({ma_20:.1f}) crossed below MA50({ma_50:.1f}) — trend reversal"
        evidence["ma_crossover"]["status"] = "bearish_cross"
        return SignalResult("SELL", evidence=evidence)

    if current_price < ma_200:
        evidence["reason"] = f"Price({current_price}) below MA200({ma_200:.1f}) for 3+ days — long-term downtrend"
        evidence["trend"]["status"] = "below"
        return SignalResult("SELL", evidence=evidence)

    # 3. Check RSI overbought with MA confirmation
    if rsi_14 > 70 and ma_20 < ma_50:
        evidence["reason"] = f"RSI({rsi_14:.1f}) overbought (>70) + MA20 below MA50 — momentum breakdown"
        evidence["rsi"]["zone"] = "overbought"
        return SignalResult("SELL", evidence=evidence)

    # 4. Check MA crossover buy with ALL confirmations
    vol_ratio = volume_today / volume_30d_avg
    if (ma_20 > ma_50 and
        current_price > ma_200 and
        30 <= rsi_14 <= 60 and
        vol_ratio > 1.2):

        evidence["ma_crossover"]["status"] = "bullish_cross"
        evidence["trend"]["status"] = "above"
        evidence["volume"]["status"] = "confirmed"

        # Determine tier
        tier = "Tier 3"
        if vol_ratio > 1.5 and 40 <= rsi_14 <= 55:
            tier = "Tier 1"
        elif vol_ratio > 1.2:
            tier = "Tier 2"

        evidence["reason"] = (
            f"MA20({ma_20:.1f}) crossed above MA50({ma_50:.1f}) [Golden cross] | "
            f"Price({current_price}) above MA200({ma_200:.1f}) [Uptrend] | "
            f"RSI({rsi_14:.1f}) in neutral zone [Not overbought] | "
            f"Volume {vol_ratio:.0%} of 30d avg [Confirmed]"
        )
        return SignalResult("BUY", tier=tier, evidence=evidence)

    # 5. Default — HOLD with explanation
    reasons = []
    evidence["ma_crossover"]["status"] = "neutral"
    evidence["volume"]["status"] = "unconfirmed"
    if vol_ratio < 1.2:
        reasons.append(f"Insufficient volume ({vol_ratio:.0%} of avg, need >120%)")
    if rsi_14 > 60:
        reasons.append(f"RSI too high ({rsi_14:.1f}, need ≤60)")
    if rsi_14 < 30:
        reasons.append(f"RSI too low ({rsi_14:.1f}, oversold — wait for recovery)")
    evidence["reason"] = "; ".join(reasons) if reasons else "No signal conditions met"

    return SignalResult("HOLD", evidence=evidence)
```

---

## Signal Quality Tiers

| Tier | Conditions | Action |
|------|-----------|--------|
| **Tier 1 (Strong Buy)** | MA cross + RSI 40-55 + volume > 150% + price near support | Full position |
| **Tier 2 (Moderate Buy)** | MA cross + RSI 30-40 or 55-60 + volume > 120% | Half position |
| **Tier 3 (Hold/Weak)** | MA cross without volume OR RSI outside range | Watch only |
| **Sell** | Any sell condition met | Exit (full or partial) |

---

---

## 🎯 Takeaway for a Student Investor

After this skill runs, you have the same technical analysis an experienced trader produces — without spending 5,000 hours watching charts.

**What the pro does:** Reads charts by eye, makes subjective judgments, and sometimes gets it wrong because emotions override logic.

**What this skill does:** Applies exact mathematical rules to every stock, every time, with no emotions and no shortcuts.

**The difference:** Your signals are consistent. The pro's signals depend on how they feel that day. Consistency wins over the long term.

---

## Output Checklist

- [ ] MA periods are exactly 20, 50, 200 (not 10, 20, 50 or other variants)
- [ ] RSI period is exactly 14, thresholds 30/70 (not 14/70/30 or other)
- [ ] Volume confirmation is MANDATORY (≥120% of 30-day avg)
- [ ] Market Reality Filter applied first (liquidity, spread, manipulation check)
- [ ] No BUY signal without volume confirmation
- [ ] No rule invented or modified — use values exactly as documented
- [ ] Signal includes tier rating (Strong/Moderate/Weak)
- [ ] 3-5% stop-loss encoded (default 5%, conservative 3%)

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/ma-crossover-logic.md` | When implementing moving average signals |
| `references/rsi-rules.md` | When implementing momentum filters |
| `references/volume-confirmation.md` | When implementing volume checks |
| `references/signal-examples.md` | When testing signal generation logic |

## Source

Research: `research.md` (project root) — Section 4: System Architecture, Layer 1-3
