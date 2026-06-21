# Regime-Shift Protocol

Per ADR-002 D13. Detects when the assumed macro regime flips, preventing clustered losses from 5-7 sequential stop-outs.

## Trigger

**Halt new entries when:** 3+ open positions hit stops within 5 trading days.

## Detection

```python
def detect_regime_shift(trades_journal, lookback_days=5, stop_threshold=3):
    """
    Scan recent closed trades. If stop_threshold or more positions
    hit stops in lookback_days, signal regime shift.
    """
    recent = [
        t for t in trades_journal
        if t.exit_reason in ("stop_loss", "trailing_stop")
        and t.exit_date >= date.today() - timedelta(days=lookback_days)
    ]
    return len(recent) >= stop_threshold
```

## Halt Actions

When trigger fires:

1. **Halt new entries immediately.** Queue all BUY signals for next week.
2. **Surface ADR suggestion:** "Regime shift detected — review macro thesis."
3. **Run macro reassessment** (see template below).
4. **Review existing positions** — if macro thesis that justified the entry has flipped, exit defensively.

## Resume Criteria

New entries resume only after:

1. Macro reassessment completed and documented.
2. Macro state re-evaluated (see ADR-003 / `macro-states.md`).
3. Explicit consent to resume from user documented in decision sheet.
4. At least 3 trading days since last stop-out (cooling period).

## Macro Reassessment Template

```markdown
# Macro Reassessment — {date}

## Trigger
- {N} stops hit in {N} days
- Symbols: {list}

## Re-evaluation
- SBP policy: {hiking/holding/cutting}
- USD/PKR trend (30d): {up/down/flat — X%}
- IMF program status: {on_track/delayed/at_risk}
- KSE-100 P/E vs 10-yr median: {X} vs {Y}

## Verdict
- Previous macro state: {RISK_ON / NEUTRAL / RISK_OFF}
- Revised macro state: {RISK_ON / NEUTRAL / RISK_OFF}
- Was the original macro thesis wrong? {yes/no}

## Action
- [ ] Halt new entries until {date}
- [ ] Resume full pipeline
- [ ] Tighten universe to defensives only
- [ ] Exit specific positions: {list}

## Consent
- User review completed: {date}
- Resume approved: {yes/no}
```
