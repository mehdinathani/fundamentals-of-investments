# Prohibited Behaviors (System Safety)

These behaviors are STRICTLY FORBIDDEN. No exceptions, no "just this once."

## 1. Emotional Averaging Down

```python
# ❌ NEVER DO THIS
if current_price < entry_price:
    buy_more(shares)  # "It'll come back!" → Account killer
```

**Why forbidden:** Converts small, manageable losses into catastrophic ones.
**Alternative:** Cut the loss at stop-loss. Re-enter only with a fresh BUY signal.

## 2. Moving Stop-Loss Down

```python
# ❌ NEVER DO THIS
if price_approaching_stop:
    stop_loss = stop_loss * 0.98  # "Give it more room" → Disaster
```

**Why forbidden:** Removes the one protection your capital has.
**Alternative:** Take the loss. That's what the stop is for.

## 3. Ignoring Stop-Loss

```python
# ❌ NEVER DO THIS
if price_below_stop:
    hold_and_hope()  # "Maybe it'll bounce" → More loss
```

**Why forbidden:** The stop-loss is the system's survival mechanism.
**Alternative:** Sell immediately. No second chances.

## 4. Revenge Trading

```python
# ❌ NEVER DO THIS
after_big_loss():
    increase_position_size()  # "Make it back fast" → Usually worse
```

**Why forbidden:** Emotional trading after losses leads to cascade failures.
**Alternative:** Stop trading for the day. Reassess with clear head.

## 5. Over-Concentration

```python
# ❌ NEVER DO THIS
single_position_value = account_balance * 0.40  # 40% in one stock!
```

**Why forbidden:** One bad move wipes out months of gains.
**Alternative:** Max 20% per position. Diversify.

## 6. Trading Without Volume Confirmation

```python
# ❌ NEVER DO THIS
if ma_crossover and rsi_good:
    buy()  # Forgot volume check!
```

**Why forbidden:** Low-volume signals have high failure rates.
**Alternative:** Always verify `volume ≥ 120% of 30-day avg`.

## 7. Holding Through Earnings (STRICTLY FORBIDDEN — ADR-002 D10)

```python
# ❌ NEVER DO THIS
hold_position_through_earnings_without_approval()
```

**Why forbidden:** PSX earnings gaps can exceed 20% — exceeds the system's max-loss tolerance of 5%. An earnings gap-down below stop-loss is unrecoverable.

**Exception:** Holding through earnings is permitted ONLY if the thesis explicitly requires it AND is documented in the trade journal with rationale.

**Action:** Flat into all earnings events unless thesis documented. Re-enter after earnings if the signal still holds.

## 8. Over-Concentration in Single Macro Factor (ADR-002 D4)

**Why forbidden:** PSX is macro-dominated. 7 positions all exposed to USD/PKR weakness = effective 1-position bet, not 7.

**Limit:** Max 2 open positions sharing the same macro factor (USD/PKR direction, interest rates, political risk).

## Enforcement in Code

```python
def enforce_prohibited_behaviors(signal, position, account):
    """Raise exceptions for prohibited behaviors."""

    # Check averaging down
    if signal == "BUY" and position.exists and position.unrealized_gain < 0:
        raise ViolationError("Averaging down is PROHIBITED")

    # Check stop-loss override
    if signal == "HOLD" and position.price < position.stop_loss:
        raise ViolationError("Stop-loss hit — MUST sell")

    # Check concentration
    if position.value > account.balance * 0.20:
        raise ViolationError("Position exceeds 20% limit")

    # Check moving stop down
    if signal == "UPDATE_STOP" and signal.new_stop < position.stop_loss:
        raise ViolationError("Moving stop-loss down is PROHIBITED")

    return True  # All clear
```
