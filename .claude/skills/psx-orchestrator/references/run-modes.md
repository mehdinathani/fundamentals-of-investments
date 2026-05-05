# Orchestrator Run Modes

Three modes, ordered by side-effect severity. Default is the safest.

## Mode 1: dry-run (DEFAULT)

- Reads everything (data fetch, ratios, signals).
- Writes ONLY the decision sheet under `data/runs/<run_id>.md`.
- Does NOT write to trade journal.
- Does NOT modify portfolio state.
- Safe to run as often as you want.

Use case: morning review, ad-hoc "what would we do today" check, debugging.

## Mode 2: journal-only

- Everything dry-run does, plus:
- Writes proposed trades to journal with status `pending`.
- Status `pending` = signal generated, sizing approved, but not yet executed.
- A trade in `pending` for > 1 trading day is auto-cancelled (signal stale).

Use case: pre-market preparation. You generate the proposed list before broker opens, then later mark which fills happened.

## Mode 3: apply

- Everything journal-only does, plus:
- Marks specified pending trades as `executed` with actual fill price/time.
- Updates portfolio state (cash, positions).
- Triggers post-execution journal entry (for live monitoring).

Use case: after broker fills are reconciled. NEVER auto-executes — the apply step accepts a list of `(trade_id, actual_fill_price, actual_fill_time)` from the user.

## Mode selection

| User intent | Mode |
|-------------|------|
| "Show me today's signals" | dry-run |
| "Prepare orders for market open" | journal-only |
| "Mark these as executed" | apply (with explicit trade_id list) |
| Anything ambiguous | dry-run + ask |

## Safety rules

1. `apply` requires explicit confirmation in the run input. Default to `dry-run` if unspecified.
2. `apply` cannot run on a stale `pending` set (>24h old) — must re-run journal-only first.
3. No mode can override Layer 0 or Layer 3 hard rules.
4. Each mode logs its own run-id under `data/runs/`. Re-running journal-only on the same trading day overwrites the prior journal-only file (single source of truth per day).

## Implementation contract

```python
def orchestrate(account_balance: float,
                capital_tier: str = "standard",
                mode: str = "dry-run",
                fills: list[dict] | None = None) -> str:
    assert mode in ("dry-run", "journal-only", "apply")
    if mode == "apply":
        assert fills, "apply mode requires fill list"
    ...
```
