# PSX Evidence-Based Investment Scan — Scripts

## Quick Start

```bash
# Full pipeline (5 validation symbols, ~2 min)
python scripts/run_scan.py

# Full pipeline with conservative tier for small account
python scripts/run_scan.py --conservative

# Scan specific symbols
python scripts/run_scan.py --symbols ENGRO OGDC

# Save decision sheet
python scripts/run_scan.py --output data/runs/myscan.md

# Stale data alert threshold (default 30 days)
python scripts/run_scan.py --data-age 35
```

## Pipeline Architecture

```
Phase 1 → Phase 2  → Phase 3     → Phase 4       → Phase 5     → Phase 6
Market    Market     Category       Ratio           Technical     Risk
Data      Reality    Benchmarks     Analysis        Signals       Assessment
(fetch)   Filter     (KSE30/100)    (vs index       (MA, RSI,     (stop-loss,
          (Layer 0)  (P/E, EPS)      medians)        volume)       sizing)
```

## Individual Scripts

| Script | Purpose | Run command |
|--------|---------|-------------|
| `run_scan.py` | Full pipeline orchestrator (6 phases) | `python scripts/run_scan.py` |
| `psx_data.py` | DPS portal data fetcher (rate-limited) | `python scripts/psx_data.py --list-cached` |
| `category_benchmarks.py` | Compute KSE30/KSE100 P/E/EPS medians | `python scripts/category_benchmarks.py --update` |
| `ratio_calculator.py` | Compare stock ratios vs benchmarks | `python scripts/ratio_calculator.py --all` |
| `market_filter.py` | Layer 0 reality filter (liquidity, operator, volume) | `python scripts/market_filter.py --all` |
| `evidence_signals.py` | Layer 2 technical signals (MA, RSI, volume) | `python scripts/evidence_signals.py --all` |
| `heatmap_tradebars.py` | ASCII sector heatmaps + per-stock trade bars | `python scripts/heatmap_tradebars.py --heatmap` |
| `macros.py` | Shared constants (paths, thresholds, sector lists) | (import only) |

## Flags

### run_scan.py

| Flag | Default | Description |
|------|---------|-------------|
| `--mode` | `dry-run` | `dry-run` or `journal-only` |
| `--conservative` | off | 2× liquidity floors, 3% max loss |
| `--symbols` | ENGRO OGDC HBL LUCK SYS | Space-separated symbol list |
| `--output` | auto (`data/runs/YYYY-MM-DD-HHMM.md`) | Decision sheet output path |
| `--data-age` | 30 | Max benchmark age (days) before stale warning |

### Individual scripts accept:
- `--symbol SYMBOL` — single symbol
- `--all` — all validation symbols
- `--conservative` — conservative capital tier
- `--update` — refresh benchmark medians from DPS
- `--heatmap` — show sector heatmap
- `--trade-bar SYMBOL` — show trade bar for symbol

## Data Flow

```
DPS Portal (dps.psx.com.pk)
  → psx_data.py (rate-limited, cached)
    → market_filter.py → market_filter.py (verdict: TRADABLE/REJECT/CAUTION)
    → category_benchmarks.py → data/benchmarks/*.csv (P/E, EPS medians)
    → ratio_calculator.py (deviation %, ABOVE/BELOW verdict)
    → evidence_signals.py (BUY/SELL/HOLD + evidence chain)
    → heatmap_tradebars.py (ASCII visualization)
```

## Output

Decision sheet written to `data/runs/` (terminal + markdown file):
- Sector heatmap (38 sectors, color-coded green/red)
- Per-stock trade bars (price, MA20, MA50 sparklines, volume)
- Benchmarks with deviation analysis
- Technical signal with full evidence chain
- Risk assessment with stop-loss levels

## Testing

```bash
# Manual test checklists in tests/manual/
ls tests/manual/
```

## Notes

- All scripts are `--dry-run` by default — no trades executed
- No broker connectivity or real-money execution
- DPS portal data is ≈5 min delayed
- EPS is the only fundamental ratio available from structured DPS data (PDF financials domain not yet parsed)
