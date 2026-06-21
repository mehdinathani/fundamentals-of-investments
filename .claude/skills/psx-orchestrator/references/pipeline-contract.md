# Inter-Skill Pipeline Contract

The orchestrator is only as reliable as the contracts between skills. Each step has a defined input shape and output shape. Breaking changes require ADR.

## Step 1 → Step 2 (data-fetcher → market-filter)

**Input to market-filter (per stock):**
```json
{
  "symbol": "ENGRO",
  "last_price": 312.5,
  "prev_close": 309.0,
  "today_volume": 1450000,
  "vol_30d_avg": 1100000,
  "value_30d_avg": 340000000,
  "freefloat_pct": 0.42,
  "days_traded_30": 30,
  "bid": 312.0,
  "ask": 313.0,
  "consecutive_circuit_days_5": 0,
  "sector": "Fertilizer"
}
```

**Output from market-filter:**
```json
{
  "symbol": "ENGRO",
  "verdict": "TRADABLE | REJECT | CAUTION",
  "failed_filter": null,
  "reasons": []
}
```

## Step 2 → Step 3 (filter → ratios)

Pass through only `verdict=="TRADABLE"`. Input to financial-ratios-psx is the symbol + period.

**Output from ratios:**
```json
{
  "symbol": "ENGRO",
  "period": "TTM",
  "revenue_cagr_3y": 0.11,
  "pat_cagr_3y": 0.14,
  "positive_pat_quarters_4": 4,
  "debt_to_equity": 0.42,
  "roe_pct": 22.1,
  "pe": 7.8,
  "eps_ttm": 40.1,
  "fundamental_score": 84
}
```

## Step 4 (fundamental screen — built into orchestrator)

Pass-through to next step only if ALL true (research.md §4 Layer 1):
- `revenue_cagr_3y > 0.08`
- `pat_cagr_3y > 0.10`
- `positive_pat_quarters_4 >= 3`
- `debt_to_equity < 0.6`
- `sector_in_top_50pct_momentum`

Cap watchlist at 20 stocks (research.md §4 Layer 1 output).

## Step 4 → Step 5 (watchlist → trade-rules-engine)

**Input:** symbol + price/volume history (≥ 200 trading days for MA200).
**Output:**
```json
{
  "symbol": "ENGRO",
  "signal": "BUY | HOLD | SELL",
  "tier": "Tier 1 | Tier 2 | Tier 3",
  "entry": 312.5,
  "stop": 296.9,
  "target": 359.4,
  "rationale": "20>50 MA, price > 200MA, RSI 52, volume 145% avg"
}
```

## Step 5 → Step 6 (signals → risk-management)

**Input to risk-management `size` action:**
```json
{
  "action": "size",
  "entry_price": 312.5,
  "stop_loss_price": 296.9,
  "account_balance": 2000000,
  "current_positions": [...],
  "risk_pct": 0.05
}
```

**Output:**
```json
{
  "approved": true,
  "shares": 640,
  "pkr_invested": 200000,
  "max_loss_pkr": 9984,
  "position_pct": 0.10,
  "rejection_reason": null
}
```

## Step 6 → Step 7 (sized → journal)

Sized BUY trades + any SELL signals matched against open positions are written to journal as `proposed` (dry-run) or `pending` (journal-only) or `executed` (apply).

## Versioning

Each contract has version `v1`. Breaking changes (renamed field, type change, new required field) bump to `v2` AND require:
1. ADR documenting the reason.
2. Compat shim if dual-version coexistence needed.
3. Update to this file.
