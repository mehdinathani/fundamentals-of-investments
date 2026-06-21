# Feature Specification: Evidence-Based Investment Signals

**Feature Branch**: `feature/evidence-signals`
**Created**: 2026-06-06
**Status**: Draft
**Input**: User scenario: student investor with basic knowledge competing against CA/ACCA analysts, needs visible evidence not blind AI trust

## User Scenarios & Testing

### User Story 1 — Daily Scan with Category Benchmarks (Priority: P1)

A student runs a daily scan. Every stock's ratios are compared against KSE-30, KSE-100, and ALLSHR medians so they know if a stock is genuinely good or just average for its category.

**Why this priority**: Without benchmark context, numbers mean nothing. A P/E of 8 sounds cheap but might be expensive for a declining sector. This is the core educational differentiator.

**Independent Test**: Run against 5 known stocks. ENGRO should show "ABOVE KSE-100 median" for ROE. Output must include `vs_KSE30`, `vs_KSE100`, `vs_ALLSHR`, `vs_sector` for each ratio.

**Acceptance Scenarios**:
1. **Given** a stock in KSE-100, **When** ratios are computed, **Then** output includes comparison against KSE-100 median with deviation % and "ABOVE/BELOW" verdict
2. **Given** a stock not in any index, **When** ratios are computed, **Then** output includes ALLSHR comparison with a note "not in KSE-30/KSE-100"
3. **Given** benchmark data is stale (>30 days old), **When** scan runs, **Then** output warns "Benchmarks may be stale — refresh with --update-benchmarks"

---

### User Story 2 — Evidence-Backed Signals (Priority: P1)

Every BUY/SELL/HOLD signal includes the complete reasoning chain: Layer 0 pass/fail with values, Layer 1 ratios vs benchmarks, Layer 2 technical conditions with actual numbers, Layer 3 risk approval with position size.

**Why this priority**: The student must never "trust the AI" — they must see the evidence and learn to verify it themselves.

**Independent Test**: Run signal generation on OGDC with known price data. Output must show MA20 value, MA50 value, crossover status, RSI value, volume ratio, and a plain-language reason string.

**Acceptance Scenarios**:
1. **Given** a stock triggers BUY, **When** signal is generated, **Then** output includes `evidence.reason` with all triggering conditions and their actual values
2. **Given** a stock is REJECTED at Layer 0, **When** signal is generated, **Then** output includes `failed_filter` name and the specific threshold that was violated
3. **Given** a stock is HOLD, **When** signal is generated, **Then** output includes which condition(s) prevented BUY/SELL

---

### User Story 3 — Visual Heatmaps & Trade Bars (Priority: P2)

The decision sheet includes an ASCII sector heatmap (5-day sector performance with color coding) and per-stock trade bars showing price, MA lines, and volume — so the student can visually verify signals.

**Why this priority**: A picture is worth 1000 numbers. Visual evidence builds confidence and understanding faster than tables.

**Independent Test**: Generate heatmap from sample sector data. Each sector must show 5-day performance with green/red indicators. Trade bar must show price line, MA20, MA50, and volume bars.

**Acceptance Scenarios**:
1. **Given** sector performance data, **When** heatmap is generated, **Then** output is a formatted ASCII table with sector names, 5 daily values, and color indicators
2. **Given** stock price/MA/volume data, **When** trade bar is generated, **Then** output shows price line with MA20/MA50 overlays and volume bars at bottom, with BUY marker at signal day

---

### User Story 4 — Full Pipeline Orchestration (Priority: P2)

One command runs the entire pipeline: fetch data → filter market → compute ratios → compare vs benchmarks → generate signals → size risk → output decision sheet with evidence + visuals.

**Why this priority**: Individual scripts are useful, but the full pipeline is the system. Without orchestration, the student has to run 5 separate commands.

**Independent Test**: Run `python run_scan.py --mode dry-run`. Output must be a single decision sheet at `data/runs/YYYY-MM-DD-HHMM.md` containing all sections.

**Acceptance Scenarios**:
1. **Given** no prior run today, **When** pipeline runs, **Then** it fetches fresh data, processes all layers, and writes a complete decision sheet
2. **Given** `--conservative` flag, **When** pipeline runs, **Then** liquidity thresholds are 2× tighter and position size is capped at 3% risk

### Edge Cases

- What happens when DPS portal is down? → Cache last successful data, flag "stale data" warning
- What happens when a stock has missing financials? → Skip ratio comparison, flag "financials unavailable"
- What happens when KSE-100 constituents change? → Recompute benchmarks on next `--update-benchmarks` run
- What happens for a newly listed stock? → No historical data = skip technicals, flag "insufficient history"
- What happens when no signals trigger? → Valid outcome. Decision sheet says "No signals today" — not an error.

## Requirements

### Functional Requirements

- **FR-001**: System MUST fetch and store KSE-30, KSE-100, and ALLSHR constituent lists from dps.psx.com.pk
- **FR-002**: System MUST compute median ROE, P/E, D/E, EPS, Dividend Yield for each index
- **FR-003**: System MUST compare each stock's ratios against its index benchmarks and output "ABOVE/BELOW median" verdict
- **FR-004**: System MUST generate BUY/SELL/HOLD signals with a complete evidence dict (MA values, RSI, volume ratio, crossover status)
- **FR-005**: System MUST apply Layer 0 market filter before any fundamental or technical analysis
- **FR-006**: System MUST apply Layer 3 risk sizing before any trade is "approved"
- **FR-007**: System MUST generate an ASCII sector performance heatmap for the last 5 trading days
- **FR-008**: System MUST generate per-stock trade bars showing price, MA20, MA50, and volume with signal markers
- **FR-009**: System MUST write a single decision sheet to `data/runs/YYYY-MM-DD-HHMM.md`
- **FR-010**: System MUST respect PSX 2-3s rate limiting between DPS requests
- **FR-011**: System MUST support `--dry-run` (default) and `--apply` modes
- **FR-012**: System MUST NOT connect to any broker or execute real trades
- **FR-013**: System MUST cache data to avoid redundant DPS requests within the same day
- **FR-014**: System MUST flag stale benchmark data (>30 days) and stale price data (>1 day)

### Key Entities

- **Stock**: Symbol, sector, price, volume, financials — the core entity
- **IndexBenchmark**: KSE-30, KSE-100, or ALLSHR — pre-computed median ratios
- **SignalResult**: Symbol, signal (BUY/HOLD/SELL), tier (1/2/3), evidence dict
- **FilterResult**: Symbol, verdict (TRADABLE/REJECT/CAUTION), failed_filter, reasons
- **DecisionSheet**: Complete pipeline output with all sections
- **SectorHeatmap**: Sector name, 5-day performance sequence, trend direction
- **TradeBar**: Price series, MA20/MA50 series, volume series, signal markers

## Success Criteria

### Measurable Outcomes

- **SC-001**: Full KSE-100 scan completes in under 5 minutes (including rate-limited data fetches)
- **SC-002**: Every signal output contains ≥5 evidence fields (MA crossover, RSI, volume, trend, reason string)
- **SC-003**: Benchmark comparison covers all 3 indexes (KSE-30, KSE-100, ALLSHR) + sector
- **SC-004**: Heatmap displays ≥10 sectors with 5-day performance and color indicators
- **SC-005: Pipeline runs with single command: `python run_scan.py`
- **SC-006**: Decision sheet is human-readable markdown, not raw JSON
