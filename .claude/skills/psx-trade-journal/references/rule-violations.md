# Rule Violation Detector

Run after every closed trade. Tag the trade with violations; never silently fix.

## Detector rules

```python
def detect_violations(trade: dict, daily_data: dict) -> list[str]:
    violations = []

    # 1. Stop honored?
    # Allowed if exit triggered by gap-down below stop (no opportunity to exit at stop).
    if trade["exit_reason"] != "stop_loss":
        # Did stop ever get hit intraday and we didn't exit?
        if trade.get("min_price_during_hold", float("inf")) <= trade["stop_loss_price"]:
            if trade["exit_price"] > trade["stop_loss_price"]:
                violations.append("stop_violated")

    # 2. Position size limit
    if trade["position_pct_of_account"] > 0.20 + 1e-6:
        violations.append("oversized")

    # 3. Stop never moved DOWN
    initial_stop = trade["stop_loss_price"]
    final_stop = trade.get("final_stop_price", initial_stop)
    if final_stop < initial_stop - 1e-6:
        violations.append("stop_lowered")

    # 4. No averaging down
    # Detected at entry-time: count open entries in same symbol where avg cost > current price.
    if trade.get("averaged_down_flag"):
        violations.append("averaged_down")

    # 5. Volume confirmation at entry
    if trade.get("entry_volume_ratio", 1.0) < 1.20:
        violations.append("low_volume_entry")

    # 6. Risk in 3-5% band
    risk_pct = trade["max_loss_pkr"] / trade["account_balance_at_entry"]
    if not (0.03 - 1e-4 <= risk_pct <= 0.05 + 1e-4):
        violations.append("risk_violation")

    # 7. Entered during upper circuit
    if trade.get("entered_during_upper_circuit"):
        violations.append("circuit_entry")

    return violations
```

## Response policy

| Violations this month | Response |
|------------------------|----------|
| 0 | Continue normal operation |
| 1-2 | Note in monthly review; address in next cycle |
| 3-5 | Halt new entries for 1 week; root-cause analysis |
| > 5 | Stop trading; full strategy review; possible re-backtest |

## Why no auto-fix

The journal records what *actually* happened. Auto-fixing hides drift between intended rules and lived discipline. Visibility is the whole point of the journal.

## Linking to trade-rules-engine

When a `low_volume_entry` violation occurs, check whether the signal came from
trade-rules-engine — if yes, the rule was violated by the *trader*, not the engine.
If many such cases, the entry process needs review (signal source vs. execution gap).
