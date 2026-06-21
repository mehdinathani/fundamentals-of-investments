# Implementation Plan: Evidence-Based Investment Signals

**Branch**: `feature/evidence-signals` | **Date**: 2026-06-06 | **Spec**: `specs/evidence-signals/`
**Prerequisite**: 8 PSX skills documented in `.claude/skills/` (complete)
**Input**: Feature specification from `specs/evidence-signals/spec.md` (to be created)

## Summary

Build the executable Python layer that transforms 8 documented skills into a working daily investment scan for a student investor. Every signal output includes: (1) category benchmark comparison (KSE-30/KSE-100/ALLSHR), (2) full evidence chain showing why each rule triggered, and (3) visual heatmaps/trade bars so the investor can verify the AI's reasoning.

## Technical Context

| Area | Decision |
|------|----------|
| **Language** | Python 3.11+ |
| **Data** | CSV/Parquet files in `data/` — no database until validated profitable |
| **Visualization** | Matplotlib + tabulate (ASCII heatmaps for terminal) |
| **Benchmarks** | Pre-computed KSE-30/KSE-100/ALLSHR medians stored in `data/benchmarks/` |
| **Pipeline** | Single Python CLI: `python run_scan.py` → outputs `data/runs/YYYY-MM-DD-HHMM.md` |
| **Testing** | Manual validation against known stocks (e.g., ENGRO, OGDC) — formal tests later |
| **Target** | Linux CLI (no frontend — Phase 4 is deferred per constitution) |
| **Performance** | Full scan of KSE-100 in < 5 minutes |
| **Constraints** | No broker connectivity, no real-money execution, PSX 5-min data delay respected |

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **II (Finance-First, Technology Second)**: ✅ Pass — scripts serve the trading system, not the other way around
- **III (Risk Control Over Profit)**: ✅ Pass — risk-management is a hard gate in the pipeline
- **IV (Discipline Over Intelligence)**: ✅ Pass — rules are encoded verbatim from research.md, not guessed
- **V (Data-Driven Decisions Only)**: ✅ Pass — every signal includes traceable evidence chain
- **VII (Named Edge)**: ✅ Pass — time-horizon asymmetry + behavioral discipline
- **VIII (Falsifiable Operation)**: ✅ Pass — kill-switch numbers encoded in journal
- **Phase Gating**: ⚠️ Phase 1 (Strategy Validation) backtest is FAILED near-miss. Phase 2 scripts MUST include a backtest compatibility flag (`--dry-run` only) until backtest gate passes.

## Project Structure

```
scripts/
├── run_scan.py              # Entry point: daily pipeline orchestrator
├── category_benchmarks.py   # Compute KSE-30/KSE-100/ALLSHR medians
├── evidence_signals.py      # Generate signals with full evidence chain
├── heatmap_tradebars.py     # Generate visual evidence (ASCII heatmaps + trade bars)
├── psx_data.py              # Data fetching wrapper (calls psx-data-fetcher patterns)
├── ratio_calculator.py      # Ratio computation with benchmark comparison
├── market_filter.py         # Layer 0 implementation
└── macros.py                # Global constants (paths, thresholds, sector lists)

data/
├── benchmarks/              # Pre-computed KSE-30/KSE-100/ALLSHR medians
│   ├── kse30_ratios_latest.csv
│   ├── kse100_ratios_latest.csv
│   └── allshr_ratios_latest.csv
├── runs/                    # Daily scan outputs (one .md per run)
└── trade-journal/           # Append-only trade log (CSV + monthly reviews)

tests/
└── manual/                  # Manual validation checklists
```

## Complexity Tracking

No constitution violations. This is a standard single-package Python project.

## Deliverables by Phase

### Phase 0: Research

| Task | Description |
|------|-------------|
| R1 | Verify PSX data access: confirm dps.psx.com.pk endpoints for price + financial data |
| R2 | Collect sample KSE-30, KSE-100, ALLSHR constituent lists from DPS portal |
| R3 | Collect sample financial statements (ENGRO, OGDC, HBL, LUCK) for ratio computation |
| R4 | Document benchmark median computation: which stocks in each index, how to aggregate |

### Phase 1: Core Implementation

| Module | Description |
|--------|-------------|
| `category_benchmarks.py` | Fetches KSE-30/KSE-100/ALLSHR constituents, computes median ratios per index, stores to `data/benchmarks/` |
| `ratio_calculator.py` | Computes ROE/P/E/D/E/EPS from PSX financials, compares against benchmarks, outputs "ABOVE/BELOW median" verdict |
| `market_filter.py` | Layer 0: liquidity, spread, operator detection, volume spike, circuit breaker — outputs TRADABLE/REJECT/CAUTION |
| `evidence_signals.py` | Layer 2: MA crossover + RSI + volume confirmation — outputs SignalResult with full evidence dict |
| `heatmap_tradebars.py` | Generates ASCII sector heatmap + per-stock trade bar visualization |
| `psx_data.py` | Wrapper around dps.psx.com.pk scraping — rate-limited, paginated |
| `run_scan.py` | Orchestrator: chains all modules in order, writes decision sheet with evidence |

### Phase 2: Integration & Validation

| Task | Description |
|------|-------------|
| I1 | Wire full pipeline end-to-end: `python run_scan.py --mode dry-run` |
| I2 | Validate against 5 known stocks: ENGRO, OGDC, HBL, LUCK, SYS |
| I3 | Verify evidence output contains all required fields (reason chain, benchmark comparison, visual) |
| I4 | Test with `--conservative` (small account) and `--standard` (large account) modes |
| I5 | Document output format with example decision sheet |

## Key Rules

1. **No broker connectivity** — scripts produce decision sheets, not orders
2. **--dry-run is the default** — `--apply` requires explicit confirmation
3. **All outputs are reproducible** — same inputs = same decision sheet
4. **Evidence is mandatory** — no signal without a complete reasoning chain
5. **Benchmarks are pre-computed** — category medians computed once, stored in `data/benchmarks/`
6. **PSX 5-min delay respected** — scripts never claim "real-time" data
7. **Backtest gate is open** — Phase 2 scripts must not deploy real capital until ADR-004 resolves
