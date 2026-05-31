---
name: risk-management
description: |
  Enforce capital protection rules for the PSX investment system. Encodes the
  3-5% max loss per trade rule, position sizing formula, and stop-loss logic.
  This skill should be used when users ask to calculate position size, set stop-loss
  levels, compute max loss, manage trade risk, or enforce capital preservation
  rules for PSX stock positions.
allowed-tools: Read, Write, Bash
---

# Risk Management

Capital protection layer for the PSX investment system. Every rule in this skill is NON-NEGOTIABLE unless the user explicitly requests a change with justification.

## What This Skill Does

- Encodes the 3-5% maximum loss per trade rule
- Calculates position sizes based on account balance and risk tolerance
- Sets stop-loss levels (fixed percentage and trailing)
- Prevents prohibited behaviors (emotional averaging, moving stops down)
- Enforces portfolio-level exposure limits

## What This Skill Does NOT Do

- Generate buy/sell signals (use `trade-rules-engine` skill)
- Calculate financial ratios (use `financial-ratios-psx` skill)
- Fetch market data (use `psx-data-fetcher` skill)
- Execute trades or manage broker connections

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing risk modules, portfolio tracker, account balance source |
| **Conversation** | Account size (PKR), current positions, risk tolerance (3% or 5%) |
| **Skill References** | Formulas from `references/`, prohibited behaviors list |
| **User Guidelines** | Any account-specific constraints or overrides |

Ensure all required context is gathered before implementing.

---

## Core Risk Rules (NON-NEGOTIABLE)

### Rule 1: Maximum Loss Per Trade — 3% to 5%

**This is the system's survival mechanism. Never violate.**

```
Maximum loss per trade = Account Balance × Risk Percentage
```

| Risk Profile | Risk % | When to Use |
|--------------|--------|-------------|
| **Conservative** | 3% | Account < PKR 1M, new trader, high volatility stocks |
| **Standard** | 5% | Account ≥ PKR 1M, experienced, stable large-caps |
| **NEVER EXCEED** | 5% | Hard ceiling — no exceptions |

**Example:**
- Account: PKR 2,000,000
- Risk: 5%
- Max loss per trade: PKR 100,000

```python
def max_loss_per_trade(account_balance, risk_pct=0.05):
    """Calculate maximum acceptable loss for a single trade."""
    assert 0.03 <= risk_pct <= 0.05, "Risk must be between 3% and 5%"
    return account_balance * risk_pct
```

---

### Rule 2: Position Sizing Formula

Position size is derived from risk, NOT from how much you want to invest.

```
Position Size (shares) = Max Loss Amount / (Entry Price - Stop-Loss Price)
Position Size (PKR) = Position Size (shares) × Entry Price
```

**Step-by-step:**
1. Calculate max loss: `account_balance × risk_pct`
2. Calculate price risk: `entry_price - stop_loss_price`
3. Shares = `max_loss / price_risk`
4. PKR invested = `shares × entry_price`
5. Validate: PKR invested ≤ `account_balance × 0.10` (max 10% per position)

```python
def calculate_position_size(entry_price, stop_loss_price, account_balance, risk_pct=0.05):
    """
    Returns: (shares, pkr_invested, max_loss_amount)

    Raises: ValueError if position exceeds 20% of account or risk is invalid.
    """
    if not (0.03 <= risk_pct <= 0.05):
        raise ValueError("Risk percentage must be between 3% and 5%")

    max_loss = account_balance * risk_pct
    price_risk = entry_price - stop_loss_price

    if price_risk <= 0:
        raise ValueError("Stop-loss must be below entry price")

    shares = max_loss / price_risk
    pkr_invested = shares * entry_price

    # Portfolio concentration limit: max 10% in one position
    if pkr_invested > account_balance * 0.10:
        shares = (account_balance * 0.10) / entry_price
        pkr_invested = shares * entry_price

    return int(shares), round(pkr_invested, 2), round(max_loss, 2)
```

**Example calculation:**
```
Account: PKR 2,000,000
Risk: 5% → Max loss = PKR 100,000
Entry: PKR 100/share
Stop-loss: PKR 95/share (5% stop)
Price risk: PKR 5/share
Shares: 100,000 / 5 = 20,000 shares
Invested: 20,000 × 100 = PKR 2,000,000

⚠️ THIS EXCEEDS 20% LIMIT (PKR 2M = 100% of account)
ADJUSTED: Max 20% = PKR 400,000 → 4,000 shares
```

---

### Rule 3: Stop-Loss Logic

#### 3A. Initial Stop-Loss (MANDATORY)

```
Stop-Loss Price = Entry Price × (1 - stop_pct)
Default stop_pct = 5% (0.05)
Conservative stop_pct = 3% (0.03)
```

- Set stop-loss IMMEDIATELY upon entry (before any price movement)
- Stop-loss is a HARD exit — no negotiation, no exceptions
- Use intraday low or previous support as reference, minimum is the % rule

#### 3B. Trailing Stop (RECOMMENDED)

```
After +10% gain: Trail stop to entry price (breakeven)
After +15% gain: Trail stop to +5% from entry
After +25% gain: Trail stop to +15% from entry
```

```python
def calculate_trailing_stop(entry_price, current_price, stop_pct=0.05):
    """Calculate trailing stop-loss based on unrealized gain."""
    gain_pct = (current_price - entry_price) / entry_price

    if gain_pct >= 0.25:
        return entry_price * 1.15  # Lock in 15%
    elif gain_pct >= 0.15:
        return entry_price * 1.05  # Lock in 5%
    elif gain_pct >= 0.10:
        return entry_price  # Breakeven
    else:
        return entry_price * (1 - stop_pct)  # Initial stop
```

#### 3C. Stop-Loss Rules (NEVER VIOLATE)

| Rule | Action |
|------|--------|
| Stop-loss hit | SELL immediately — no second chances |
| Price approaches stop (within 1%) | Prepare exit, no new buying |
| NEVER move stop-loss DOWN | Only trail up |
| NEVER average down | Cut losers, let winners run |
| Gap-down below stop | Exit at market open (accept slippage) |

---

### Rule 4: Portfolio-Level Limits

| Limit | Value | Rationale |
|-------|-------|-----------|
| Max per position | 10% of account | Diversification + 30% cash reserve |
| Max in mid-caps | 30% of account | Liquidity constraint |
| Max concurrent positions | 5-7 stocks | Focus, manageable |
| Cash reserve | ≥ 30% of account | Opportunity fund, capital protection |
| Correlation check | Max 2 stocks from same sector | Sector diversification |

---

### Rule 5: Prohibited Behaviors

These behaviors destroy accounts. The system MUST prevent them:

| Behavior | Status | Consequence |
|----------|--------|-------------|
| **Emotional averaging down** | STRICTLY FORBIDDEN | Converts small losses to account killers |
| **Moving stop-loss down** | STRICTLY FORBIDDEN | Removes capital protection |
| **Ignoring stop-loss** | STRICTLY FORBIDDEN | Violates core survival rule |
| **Over-concentration** | STRICTLY FORBIDDEN | >10% in one position |
| **Revenge trading** | STRICTLY FORBIDDEN | Trading to recover losses |
| **Trading without volume** | STRICTLY FORBIDDEN | See `trade-rules-engine` |
| **Holding through earnings** | STRICTLY FORBIDDEN (ADR-002 D10) | Flat into earnings unless thesis documented in journal |

---

## Risk Metrics to Track

| Metric | Formula | Target |
|--------|---------|--------|
| **Win/Loss Ratio** | (Avg Win) / (Avg Loss) | > 2.0 |
| **Win Rate** | Winning Trades / Total Trades | > 50% |
| **Max Drawdown** | Max peak-to-trough decline | < 15% |
| **Sharpe Ratio** | (Return - Risk-free) / Std Dev | > 1.0 |
| **CAGR** | Compound Annual Growth Rate | > 15% (long-term) |

---

## Risk Check Before Every Trade

```python
def pre_trade_risk_check(account_balance, entry_price, stop_price,
                         planned_shares, current_positions):
    """
    Returns: (approved: bool, reason: str, adjusted_shares: int)
    """
    # 1. Validate risk percentage
    max_loss = account_balance * 0.05  # 5% max
    price_risk = entry_price - stop_price
    calc_shares = max_loss / price_risk if price_risk > 0 else 0
    pkr_invested = planned_shares * entry_price

    # 2. Check single position limit (10%)
    if pkr_invested > account_balance * 0.10:
        return False, "Exceeds 10% per-position limit", int(calc_shares)

    # 3. Check total exposure (max 70% invested, 30% cash)
    total_invested = sum(p["value"] for p in current_positions)
    if total_invested + pkr_invested > account_balance * 0.70:
        return False, "Exceeds 70% total exposure limit", 0

    # 4. Check position count
    if len(current_positions) >= 7:
        return False, "Maximum 7 concurrent positions", 0

    # 5. Validate stop is below entry
    if stop_price >= entry_price:
        return False, "Stop-loss must be below entry price", 0

    return True, "Approved", planned_shares
```

---

## Output Checklist

- [ ] Max loss per trade is 3-5% of account (never more)
- [ ] Position size derived from risk, not desire to invest
- [ ] Stop-loss set immediately upon entry
- [ ] Trailing stop logic implemented (breakeven at +10%, +5% at +15%)
- [ ] Never move stop-loss down (only trail up)
- [ ] Max 10% per position enforced
- [ ] Max 70% total exposure (30% cash reserve) — max 7 positions at 10%
- [ ] Emotional averaging down explicitly blocked
- [ ] All risk parameters are constants, not user-tweakable defaults

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/position-sizing.md` | When implementing size calculations |
| `references/stop-loss.md` | When implementing stop-loss logic |
| `references/portfolio-limits.md` | When checking portfolio-level constraints |
| `references/prohibited-behaviors.md` | When building trade validation |

## Source

Research: `research.md` (project root) — Section 4: Layer 3 Risk Management.
System principle: "Risk Control > Profit" (Section 11, Principle 3)
