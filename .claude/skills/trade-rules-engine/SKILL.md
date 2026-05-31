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

Encodes the exact entry, exit, and signal logic for the PSX investment system. Claude Code MUST use these rules verbatim — never invent or modify thresholds.

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

## Complete Signal Logic

```python
def generate_signal(price_data, volume_data, ma_20, ma_50, ma_200, rsi_14):
    """
    Returns: "BUY" | "HOLD" | "SELL"

    Rules are applied in order. First matching rule wins.
    """

    # 1. Check stop-loss (highest priority)
    if current_price <= entry_price * 0.95:  # 5% stop
        return "SELL"  # Stop-loss hit

    # 2. Check MA crossover sell
    if (ma_20 < ma_50) or (price_below_ma200_3days):
        return "SELL"

    # 3. Check RSI overbought with MA confirmation
    if rsi_14 > 70 and ma_20 < ma_50:
        return "SELL"

    # 4. Check MA crossover buy with ALL confirmations
    if (ma_20 > ma_50 and
        price > ma_200 and
        rsi_14 >= 30 and rsi_14 <= 60 and
        volume_today > 1.2 * volume_30d_avg):
        return "BUY"

    # 5. Default
    return "HOLD"
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
