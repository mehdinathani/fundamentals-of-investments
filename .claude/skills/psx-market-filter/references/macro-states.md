# Macro States (Layer 1.5 Overlay)

Defined per ADR-003. Three states derived from four data sources:

## Macro States Table

| State | SBP Policy | USD/PKR (30d) | IMF Status | KSE-100 P/E |
|-------|-----------|---------------|------------|-------------|
| **Risk-on** | Cutting or on hold | Stable or appreciating | On track, reviews passing | < 10-yr median |
| **Neutral** | Mixed signals | Range-bound (<3% move) | Program active, minor delays | Near 10-yr median |
| **Risk-off** | Hiking | Sharply weakening (>5% in 30d) | At risk, review missed | > 10-yr median + 1SD |

Any single risk-off input flips state to risk-off. Majority vote determines neutral vs risk-on.

## Pipeline Integration

Layer 1.5 sits between Layer 1 (Fundamental Screen) and Layer 2 (Technical Signals):

```
Layer 1 → Layer 1.5 (Macro State Check) → Layer 2
```

## Universe Rules by State

| State | Universe | Action |
|-------|----------|--------|
| **Risk-on** | Full tradable universe | Normal pipeline |
| **Neutral** | Full tradable universe | Conservative sizing (3% risk) |
| **Risk-off** | Defensives only (utilities, cash-rich, food) or 100% cash | Block new entries in non-defensives |

## Implementation

```python
def get_macro_state(sbp_policy, usdpkr_30d_pct, imf_status, kse100_pe, kse100_pe_10yr_median):
    risk_off_triggers = 0
    
    if sbp_policy == "hiking":
        risk_off_triggers += 1
    if usdpkr_30d_pct < -0.05:  # weakened >5% in 30 days
        risk_off_triggers += 1
    if imf_status in ("at_risk", "review_missed"):
        risk_off_triggers += 1
    if kse100_pe > kse100_pe_10yr_median * 1.15:  # > median + 1SD approx
        risk_off_triggers += 1
    
    if risk_off_triggers >= 1:
        return "RISK_OFF"
    
    # Neutral vs Risk-on by majority
    risk_on_count = 0
    if sbp_policy in ("cutting", "hold"):
        risk_on_count += 1
    if usdpkr_30d_pct >= -0.03:
        risk_on_count += 1
    if imf_status == "on_track":
        risk_on_count += 1
    if kse100_pe <= kse100_pe_10yr_median:
        risk_on_count += 1
    
    return "RISK_ON" if risk_on_count >= 3 else "NEUTRAL"
```

## Data Sources

| Input | Source | Frequency |
|-------|--------|-----------|
| SBP policy rate | SBP / MUFAP | Monthly |
| USD/PKR | PSX / forex portal | Daily |
| IMF status | IMF press releases | Event-driven |
| KSE-100 P/E | PSX data portal | Weekly |

## Empirical Validation (2018-2024)

Macro regime analysis was run against the momentum breakout strategy backtest.
See `scripts/macro_regime_analysis.py` and `research.md §17` for full results.

### Regime Distribution

| Regime | Days (2018-2024) | % |
|--------|-----------------|---|
| RISK_OFF | 1,397 | 54.6% |
| RISK_ON | 1,099 | 43.0% |
| NEUTRAL | 61 | 2.4% |

Pakistan was in macro risk-off for >54% of 2018-2024. This is the primary
cause of the backtest IS/OOS disparity.

### Strategy Returns by Regime

| Regime | Annualized Return |
|--------|-----------------|
| RISK_ON | +33.7% |
| RISK_OFF | +11.5% |
| NEUTRAL | +6.6% |

### Macro Gate Impact

Blocking entries during RISK_OFF improved IS CAGR from -1.2% to +2.7% and
reduced max drawdown from -36.4% to -31.3%. 107 bad entries were prevented
in the 2018-2023 period alone.

### Key Data

- Analysis script: `scripts/macro_regime_analysis.py`
- Macro data script: `scripts/macro_data.py`
- Results: `data/runs/macro_analysis_results.json`

## Reference

- ADR-003: `history/adr/ADR-003-psx-macro-overlay-layer.md`
- Constitution: `.specify/memory/constitution.md` §Macro Overlay
- Research results: `research.md §17`
