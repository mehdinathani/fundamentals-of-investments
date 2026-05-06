<!--
Sync Impact Report (2026-05-06):
  Version change: 1.0.0 → 2.0.0 (MAJOR — system-level redefinition)
  Bump rationale:
    research.md §15 (added 2026-05-05) introduced 14 validation gaps that the
    v1.0.0 constitution does not encode. The application this constitution
    governs is no longer "discipline + a fixed trade-rules set"; it is a
    layered system with explicit pre-deployment gates, an unresolved edge
    statement, a falsifiable kill-switch, a macro overlay, a regime-shift
    protocol, and tax-aware exit logic. Adding two new principles AND
    reframing the v1.0.0 trading rules as "starting hypothesis" (not
    validated edge) crosses the MAJOR threshold per the v1.0.0 governance
    rules: principles redefined, scope of the system redrawn.
  Modified principles:
    I.   Strategy Over Tools                    → kept (no change)
    II.  Finance-First, Technology Second       → kept (no change)
    III. Risk Control Over Profit               → kept, sharpened (position-math
                                                   conflict noted; defers to ADR)
    IV.  Discipline Over Intelligence           → kept, sharpened (rules now
                                                   labeled "starting hypothesis,
                                                   not validated edge")
    V.   Data-Driven Decisions Only             → kept (no change)
    VI.  Consistent, Repeatable Process         → renamed → "Layered, Repeatable
                                                   Process"; expanded to include
                                                   Macro Overlay layer
    VII. Named, Defensible Edge                 → NEW (§15.1)
    VIII.Falsifiable Operation                  → NEW (§15.7)
  Added sections:
    - Pre-Deployment Gates (NEW)
    - Macro Overlay (NEW, §15.9)
    - Sector Rotation (NEW, §15.10)
    - Regime-Shift Protocol (NEW, §15.14)
    - Phase Gating (NEW, §8 + §15.12)
  Folded (not removed):
    - v1.0.0 Trading Rules (entry/exit/prohibited) preserved verbatim under
      "Trading Rules (Hypothesis Status, Not Validated)". Their authority
      changes: they are now a starting hypothesis pending Phase 1 backtest,
      not the validated system.
  Templates checked (per sp.constitution.md §4 propagation):
    ✅ .specify/templates/plan-template.md
       — Constitution Check gate is generic ("[Gates determined based on
         constitution file]"); reads this constitution at plan time. No edit.
    ✅ .specify/templates/spec-template.md
       — No constitution-specific sections; no edit.
    ✅ .specify/templates/tasks-template.md
       — Organized by user-story independence, not principles; no edit.
    ✅ .specify/templates/phr-template.prompt.md
       — Metadata template; no edit.
    ✅ .claude/commands/sp.constitution.md
       — References constitution.md generically; no edit.
  Deferred TODOs (each MUST be resolved by ADR before live capital):
    - TODO(EDGE_DEFINITION)              — §15.1 — name the edge in one sentence
    - TODO(POSITION_MATH_RECONCILIATION) — §15.4 — choose 3-4 positions @20% OR
                                                   7 positions @10% with ≥30% cash
    - TODO(CGT_EXIT_POLICY)              — §15.6 — tax-aware vs tax-agnostic exits
    - TODO(FALSIFICATION_NUMBERS)        — §15.7 — exact N, T, Sharpe-floor, KSE-100 gap
    - TODO(MACRO_OVERLAY_RULES)          — §15.9 — concrete risk-on/risk-off thresholds
    - TODO(REGIME_SHIFT_THRESHOLDS)      — §15.14 — exact stop-cluster trigger
  Cross-references:
    - history/adr/ADR-001-psx-skills-architecture.md      (Layer architecture)
    - history/adr/ADR-002-pre-deployment-strategy-decisions.md (Pre-deployment gates)
-->

# PSX Investment System Constitution

## Core Principles

### I. Strategy Over Tools

Every feature MUST start from a financial strategy. Technology supports execution; it does not drive decisions. AI enhances efficiency, not intelligence. Code is written to serve the trading system, not the other way around.

### II. Finance-First, Technology Second

Strategy defines success. Technical implementation MUST NEVER override financial logic. When a financial rule and a technical convenience conflict, the financial rule wins. "Quick technical fixes" that violate trading discipline are prohibited.

### III. Risk Control Over Profit

Capital preservation is the primary objective. Per-trade max loss MUST stay within 3-5%. No single position MAY exceed the limit set by the position-math reconciliation (see Pre-Deployment Gates). Emotional averaging down, moving stop-loss down, and revenge trading are STRICTLY FORBIDDEN. Risk rules are system safeguards — they are never optional.

**Note:** v1.0.0 stated "max 20% per position." research.md §15.4 surfaced a
conflict with the ≥30% cash reserve requirement. The hard cap is now governed
by `TODO(POSITION_MATH_RECONCILIATION)` and MUST be set by ADR before live
capital is deployed.

### IV. Discipline Over Intelligence

Rules are followed exactly as documented. The trade-rules-engine MA periods (20/50/200), RSI thresholds (30/70), and volume confirmation (≥120%) MUST NEVER be invented or modified without explicit user consent and ADR documentation. Consistency beats cleverness.

**Status (2026-05-06):** these specific rules are a **starting hypothesis** per
research.md §15.2, not a validated edge. They MUST pass the Phase 1 backtest
gate (see Pre-Deployment Gates) before any live capital is deployed against
them.

### V. Data-Driven Decisions Only

No news chasing. No random indicators. No blind AI predictions. Every buy/sell decision MUST be traceable to: (1) Market Reality Filter pass, (2) Fundamental screen pass, (3) Macro overlay check, (4) Technical signal with volume confirmation, (5) Risk check. If data is missing or unreliable, the system MUST NOT trade.

### VI. Layered, Repeatable Process

The system is a decision engine, not a prediction machine. Every trade MUST follow the same layered architecture (see Layered Architecture section). Skipping a layer is prohibited. Zero signals over a given week is a **correct outcome**, not a failure mode (per research.md §15.5) — forced trades during dry periods are the historical #1 destroyer of disciplined systems and are STRICTLY FORBIDDEN.

### VII. Named, Defensible Edge (NEW — §15.1)

The system MUST state, in one concrete sentence, **why it makes money on PSX** that other participants don't or can't replicate (structural, informational, behavioral, or time-horizon asymmetry). Discipline + finance knowledge + programming is necessary but not sufficient — many participants have all three and still lose.

**Status:** `TODO(EDGE_DEFINITION)`. Until written and recorded in an ADR, this is a discipline framework, not an edge-bearing system. **Live capital MUST NOT be deployed while this TODO is open.**

### VIII. Falsifiable Operation (NEW — §15.7)

The system MUST have a pre-committed, written kill-switch: an exact sample size N, time window T, performance floor (Sharpe), and benchmark gap (vs. KSE-100) that, if breached, triggers a full stop and re-evaluation. "If not profitable → STOP" is not specific enough; without numbers, every result can be rationalized.

**Status:** `TODO(FALSIFICATION_NUMBERS)`. Until set by ADR, the system has no objective failure criterion. **Live capital MUST NOT be deployed while this TODO is open.**

## Layered Architecture (Non-Negotiable)

Every trade decision MUST traverse these layers in order. Skipping or reordering layers is prohibited.

- **Layer 0 — Market Reality Filter** (research.md §4.0): reject illiquid, manipulated, or operator-driven stocks. Liquidity ≥ 50K avg volume, spread < 2%.
- **Layer 1 — Fundamental Screen** (research.md §4.1): revenue growth, profit growth, earnings consistency, debt levels, sector momentum. Sector-relative thresholds (per §15.3).
- **Layer 1.5 — Macro Overlay (NEW, §15.9):** SBP policy stance, USD/PKR trend, IMF program status, KSE-100 P/E vs. 10-year median. When macro signals "risk-off," the universe MUST tighten to defensives or cash.
- **Layer 2 — Technical Signals** (research.md §4.2): trend, breakouts, support/resistance, volume confirmation. No volume → no trade. No trend → no entry.
- **Layer 3 — Risk & Position Sizing** (research.md §4.3): max loss 3-5% per trade, position cap per `TODO(POSITION_MATH_RECONCILIATION)`, hard stops, no emotional averaging, macro-factor concentration limit (see §15.8 below).
- **Layer 4 — Trade Journal & Falsification:** every trade logged with attribution; CAGR, win/loss, max drawdown, Sharpe computed; falsification kill-switch checked against `TODO(FALSIFICATION_NUMBERS)`.

## Trading Rules (Hypothesis Status, Not Validated)

These rules are inherited verbatim from constitution v1.0.0. Their **authority is provisional** pending the Phase 1 backtest gate. They MUST NOT be treated as the validated edge until that gate passes.

### Entry Rules

- 20-day SMA MUST cross ABOVE 50-day SMA (golden cross)
- Price MUST be ABOVE 200-day SMA (long-term uptrend)
- RSI(14) between 30-60 (or crossing above 30)
- Volume ≥ 120% of 30-day average (MANDATORY)
- Stock MUST pass Market Reality Filter (Layer 0)
- Sector MUST NOT be in bottom-quartile sector momentum (see Sector Rotation)
- Macro overlay MUST be risk-on or neutral (Layer 1.5)
- No earnings event within blackout window (see Risk & Capital Rules)

### Exit Rules

- Stop-loss at 5% below entry (3% for conservative)
- Trail stop to breakeven after +10% gain
- Trail stop to +5% after +15% gain
- RSI > 70 with MA sell signal = exit
- 20-day SMA crosses BELOW 50-day SMA = exit
- CGT-aware adjustment per `TODO(CGT_EXIT_POLICY)` (§15.6)

### Prohibited Trading Behaviors

- Emotional averaging down (STRICTLY FORBIDDEN)
- Moving stop-loss down (STRICTLY FORBIDDEN)
- Trading without volume confirmation (STRICTLY FORBIDDEN)
- Revenge trading after losses (STRICTLY FORBIDDEN)
- Forcing a trade during a no-signal period (STRICTLY FORBIDDEN, §15.5)
- Over-concentration beyond the position cap (STRICTLY FORBIDDEN)
- More than 2 positions sharing a single macro factor (STRICTLY FORBIDDEN, §15.8)

## Pre-Deployment Gates (NEW)

Each gate is a hard blocker. **No live capital MAY be deployed while any gate is open.** Each gate is closed by an ADR documenting the resolution.

| Gate | Origin | Status |
|------|--------|--------|
| Edge stated in one sentence | §15.1 | `TODO(EDGE_DEFINITION)` |
| Backtest pass: 2018-2024 PSX, full frictions (commission, CGT, slippage, T+2), Sharpe ≥ 1.0 net of costs | §15.2 | open until backtest run |
| Position math reconciled | §15.4 | `TODO(POSITION_MATH_RECONCILIATION)` |
| Falsification kill-switch numbers set | §15.7 | `TODO(FALSIFICATION_NUMBERS)` |
| Macro overlay rules defined | §15.9 | `TODO(MACRO_OVERLAY_RULES)` |
| Regime-shift thresholds defined | §15.14 | `TODO(REGIME_SHIFT_THRESHOLDS)` |
| CGT exit policy chosen (tax-aware vs tax-agnostic) | §15.6 | `TODO(CGT_EXIT_POLICY)` |

## Risk & Capital Rules

- Per-trade max loss: 3-5% of account.
- Position size cap: per `TODO(POSITION_MATH_RECONCILIATION)` (§15.4).
- Cash reserve: ≥ 30% at all times.
- **No-trade-period legitimacy (§15.5):** zero signals = correct outcome. Maximum trade frequency: 2 entries per week (cap to discourage forcing).
- **Earnings blackout (§15.11):** flat into earnings unless thesis explicitly requires holding through. Document the why.
- **Corporate-action handler (§15.11):** on bonus issue, rights issue, or split, recalculate stop-loss on adjusted basis. Failure to adjust silently breaks risk math.
- **Tax-loss harvesting (§15.13):** Q4 routine to offset gains within tax year. Compatible with "cut losers fast" — sequence them.
- **Macro-factor concentration (§15.8):** at most 2 open positions exposed to the same macro factor (USD/PKR direction, interest rates, political-risk regime). Effective diversification ≠ stated diversification.

## Macro Overlay (NEW, §15.9)

Required inputs (read at watchlist refresh and before every entry):

- SBP policy stance (hiking / holding / cutting)
- USD/PKR trend (rolling 30-day direction)
- IMF program status / sovereign-risk indicators
- Aggregate market valuation (KSE-100 P/E vs. 10-year median)

When macro signals "risk-off," the tradable universe MUST tighten to defensives or cash. Specific risk-on / neutral / risk-off thresholds → `TODO(MACRO_OVERLAY_RULES)` ADR.

## Sector Rotation (NEW, §15.10)

Sector momentum gates the watchlist. **Bottom-quartile sectors are excluded regardless of how strong an individual name looks.** Sector ranking refreshed quarterly. In PSX, sector beats stock selection > 60% of the time (§15.10).

## Regime-Shift Protocol (NEW, §15.14)

**Trigger:** when 3+ open positions hit stops within 5 trading days, the system MUST halt new entries and re-evaluate the macro thesis. Resume only after a documented macro review. Specific stop-cluster threshold and review template → `TODO(REGIME_SHIFT_THRESHOLDS)` ADR.

Rationale: rules cover entry, exit, stop-loss. They do **not** cover the case where the macro regime you assumed flips. Without this protocol, you take 5-7 small losses one-by-one instead of recognizing the regime shift early.

## Data & Technology Standards

### PSX Data Handling

- Use PSX DPS portal (`dps.psx.com.pk`) as primary data source.
- Rate limit: 2-3 second delay between requests (~30 req/min max).
- Pagination: handle `?page=N` and `?limit=M` parameters.
- Dynamic pages (DPS, financials) require Playwright, not simple HTTP.
- PSX financial statements use SECP column names (not standard/international).

### Financial Ratio Standards (PSX-Specific)

- EPS: `Profit after taxation / Shares Outstanding`
- ROE: `PAT / Average Shareholders' Equity`
- P/E: `Market Price / TTM EPS`
- Debt-to-Equity: `(Non-current liabilities + Current borrowings) / Total Equity`
- Exclude operating payables from debt calculations.
- Thresholds MUST be sector-relative, not absolute (§15.3).

### AI Usage Boundaries

- AI MAY: extract financial data, calculate ratios, summarize news, generate alerts.
- AI MUST NOT: make autonomous trading decisions, predict prices, execute trades.
- Human remains the final decision-maker at all times.

## Development Standards

### Code Quality

- Python is the primary language (data handling, calculations).
- Excel/CSV for initial validation and manual analysis.
- No unnecessary abstractions — three similar lines beat premature abstraction.
- No comments unless the WHY is non-obvious.
- Smallest viable change; no unrelated edits.

### Testing

- Phase 1 (Strategy Validation) happens manually in Excel before any automation.
- Python scripts require validation tests (ratio calculations, signal logic).
- All trading rules MUST be independently testable.
- No deployment of untested signal logic.

### Security

- No secrets or tokens in code — use `.env` and docs.
- No hardcoded API keys or credentials.
- PSX portals use public data — no authentication secrets needed for reads.

## Phase Gating (NEW, §8 + §15.12)

Each phase from research.md §8 is a constitutional gate. A later phase MUST NOT begin before the prior phase passes its success criteria.

- **Phase 1 — Strategy Validation (manual, Excel):** MUST be profitable on tracked manual trades before any Phase 2 code is written.
- **Phase 2 — Semi-Automation:** MUST remain profitable in production before Phase 3 features.
- **Phase 3 — Intelligent Assistant Layer:** human remains final decision-maker.
- **Phase 4 — Frontend (optional):** built only if Phases 1-3 are profitable.
- **Phase 5A — Personal Wealth Engine:** the only active scaling target.
- **Phase 5B (SaaS) and Phase 5C (Signal Service): DEFERRED** ≥ 12 months of profitable Phase 1/2 operation (§15.12). SECP advisory regulations apply to 5C; PSX retail TAM is small. Premature scaling is prohibited.

## Governance

- This constitution supersedes all other practices and coding preferences.
- Amendments require: (1) user consent, (2) documented rationale, (3) ADR if architecturally significant.
- All PRs/reviews MUST verify constitution compliance.
- Versioning follows semantic versioning (MAJOR.MINOR.PATCH):
  - **MAJOR:** principle removal or redefinition; system scope redrawn.
  - **MINOR:** new principle or materially expanded guidance.
  - **PATCH:** clarifications, wording fixes.
- **Any change to trading rules** (MA periods, RSI thresholds, risk %, position cap) requires an ADR.
- **Any flip of a `TODO(...)` token to a concrete value requires an ADR.** The Constitution Check gate in `.specify/templates/plan-template.md` MUST verify all `TODO(...)` items are resolved before any "live capital" plan is approved.
- **Ratification date:** 2026-05-05 (preserved from v1.0.0).
- **Last Amended:** 2026-05-06 (v2.0.0 rewrite).

**Version:** 2.0.0 | **Ratified:** 2026-05-05 | **Last Amended:** 2026-05-06
