# Trade Journal Schema

## CSV columns (master log: `trades.csv`)

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| trade_id | str | yes | ULID, immutable |
| symbol | str | yes | PSX ticker |
| sector | str | yes | PSX sector code |
| entry_date | date | yes | YYYY-MM-DD |
| entry_time | str | yes | HH:MM PKT |
| entry_price | float | yes | PKR per share |
| shares | int | yes | Whole shares |
| pkr_invested | float | yes | shares × entry_price |
| entry_signal_tier | str | yes | Tier 1 / Tier 2 / Tier 3 |
| entry_rationale | str | yes | Free text — MA/RSI/vol summary |
| fundamental_score | float | no | 0-100 |
| stop_loss_price | float | yes | PKR |
| stop_loss_pct | float | yes | 0.03 or 0.05 |
| max_loss_pkr | float | yes | shares × (entry - stop) |
| target_price | float | no | PKR |
| account_balance_at_entry | float | yes | PKR |
| position_pct_of_account | float | yes | pkr_invested / account_balance |
| exit_date | date | no | null until closed |
| exit_time | str | no | null until closed |
| exit_price | float | no | PKR |
| exit_reason | str | no | enum below |
| pnl_gross_pkr | float | no | exit_value - entry_value |
| pnl_net_pkr | float | no | after costs |
| pnl_pct | float | no | net / pkr_invested |
| holding_days | int | no | exit_date - entry_date |
| rules_violated | str | no | semicolon-separated tags |
| notes | str | no | Free text addendum |

## exit_reason enum

- `stop_loss` — initial stop hit
- `trailing_stop` — trailing stop hit (was profitable)
- `ma_sell` — 20 below 50 MA crossover
- `rsi_overbought` — RSI > 70 + MA confirmation
- `target_hit` — pre-set target reached
- `partial_profit` — 50% sold at +15%
- `time_stop` — > 3 months without +10%
- `manual_override` — user closed for reason outside rules
- `earnings_exit` — closed before earnings to avoid gap
- `other` — must be explained in notes

## rules_violated tags

- `stop_violated` — exited materially below stop without gap
- `oversized` — position > 20% of account
- `stop_lowered` — stop moved down vs initial
- `averaged_down` — added shares while underwater
- `low_volume_entry` — entered with vol < 120% avg
- `risk_violation` — risk outside 3-5% band
- `circuit_entry` — entered during upper-circuit lock

## Append-only enforcement

- Open the CSV in append mode only
- Closed trades update via journal-tool that writes a NEW row marked `is_correction=True` referencing the original `trade_id`, never editing in place
- Daily rsync/git-commit of `trades.csv` for tamper evidence

## SQLite mirror schema

```sql
CREATE TABLE IF NOT EXISTS trades (
  trade_id TEXT PRIMARY KEY,
  symbol TEXT NOT NULL,
  sector TEXT NOT NULL,
  entry_date DATE NOT NULL,
  entry_time TEXT NOT NULL,
  entry_price REAL NOT NULL,
  shares INTEGER NOT NULL,
  pkr_invested REAL NOT NULL,
  entry_signal_tier TEXT NOT NULL,
  entry_rationale TEXT NOT NULL,
  fundamental_score REAL,
  stop_loss_price REAL NOT NULL,
  stop_loss_pct REAL NOT NULL,
  max_loss_pkr REAL NOT NULL,
  target_price REAL,
  account_balance_at_entry REAL NOT NULL,
  position_pct_of_account REAL NOT NULL,
  exit_date DATE,
  exit_time TEXT,
  exit_price REAL,
  exit_reason TEXT,
  pnl_gross_pkr REAL,
  pnl_net_pkr REAL,
  pnl_pct REAL,
  holding_days INTEGER,
  rules_violated TEXT,
  notes TEXT,
  inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_trades_symbol ON trades(symbol);
CREATE INDEX idx_trades_entry_date ON trades(entry_date);
CREATE INDEX idx_trades_open ON trades(exit_date) WHERE exit_date IS NULL;
```
