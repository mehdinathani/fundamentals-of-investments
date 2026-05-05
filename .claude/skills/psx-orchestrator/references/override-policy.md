# Override Policy

The orchestrator enforces the system's discipline. Overrides are sometimes legitimate (e.g., known data gap, special situation) but must be EXPLICIT, LOGGED, and BOUNDED.

## What can NEVER be overridden

- Layer 0 hard filters (manipulation, illiquidity, circuit-lock).
- Layer 3 stop-loss execution.
- 3-5% max loss per trade.
- 20% max position size.
- 70% max total exposure.

These are non-negotiable. If the user requests bypassing one, the orchestrator REFUSES and surfaces an ADR suggestion. The conversation continues; the override does not.

## What CAN be overridden (with logging)

| Override | Mechanism | Required artifact |
|----------|-----------|-------------------|
| Skip a specific stock from watchlist | `skip_symbols` parameter | run note in decision sheet |
| Add a specific stock to watchlist (despite fundamentals fail) | `whitelist_symbols` | journal note explaining rationale |
| Use conservative tier instead of standard | `risk_pct=0.03` | none (just config) |
| Defer all entries until tomorrow | `entry_lock=True` | run note |
| Run during PSX holiday for analysis (no execution) | dry-run mode auto-allows | none |

## Override logging

Every override appears in the decision sheet under `## 7. Flags & Notes`:

```
- OVERRIDE: whitelist ENGRO despite D/E 0.62 > 0.6 — quarterly D/E temporarily elevated by working capital cycle, normalizes by Q4 (user note 2026-05-01)
```

## ADR triggers

Surface an ADR suggestion when an override:
1. Is requested for the THIRD time in 30 days for the same rule.
2. Would weaken a hard rule (rejected, but pattern is significant).
3. Suggests a structural change (e.g., "always whitelist these 5 stocks").

Wait for user consent before creating the ADR.

## Override expiry

- Single-run overrides: scope is one run.
- Standing overrides (in config): MUST have expiry date.
- An override without expiry is a rule change in disguise — promote to ADR.

## Anti-pattern: silent drift

Overrides that aren't logged become invisible policy. Within a year, the system bears no resemblance to the documented strategy and you don't know why. Logging is the antibody.

## Implementation

```python
@dataclass
class RunOverrides:
    skip_symbols: list[str] = field(default_factory=list)
    whitelist_symbols: list[dict] = field(default_factory=list)  # {symbol, reason}
    risk_pct: float = 0.05
    entry_lock: bool = False

def apply_overrides(stocks, overrides) -> list:
    if overrides.entry_lock:
        return []  # no entries; exits still process
    out = [s for s in stocks if s.symbol not in overrides.skip_symbols]
    for w in overrides.whitelist_symbols:
        if w["symbol"] not in [s.symbol for s in out]:
            out.append(load_stock(w["symbol"], whitelisted=True, reason=w["reason"]))
    return out
```
