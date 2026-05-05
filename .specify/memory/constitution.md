<!--
Sync Impact Report (2026-05-05):
  Version change: N/A → 1.0.0 (initial constitution)
  Added sections: Core Principles (6), Trading Rules, Risk Management, Data & Technology, Governance
  Templates requiring updates:
    ✅ .specify/templates/plan-template.md — Constitution Check section exists, references [GUIDANCE_FILE]
    ✅ .specify/templates/spec-template.md — No constitution-specific changes needed
    ✅ .specify/templates/tasks-template.md — No constitution-specific changes needed
    ✅ .claude/commands/sp.constitution.md — References constitution.md correctly
  No deferred placeholders.
-->

# PSX Investment System Constitution

## Core Principles

### I. Strategy Over Tools

Every feature starts with a financial strategy. Technology supports execution; it does not drive decisions. AI enhances efficiency, not intelligence. Code is written to serve the trading system, not the other way around.

### II. Finance-First, Technology Second

Strategy defines success. Technical implementation must never override financial logic. When a financial rule and a technical convenience conflict, the financial rule wins. No "quick technical fixes" that violate trading discipline.

### III. Risk Control Over Profit

Capital preservation is the primary objective. A 3-5% max loss per trade is non-negotiable. No position exceeding 20% of account. No emotional averaging down. No moving stop-loss down. Risk rules are system safeguards — they are never optional.

### IV. Discipline Over Intelligence

Rules are followed exactly as documented. The trade-rules-engine MA periods (20/50/200), RSI thresholds (30/70), and volume confirmation (≥120%) must never be invented or modified without explicit user consent and ADR documentation. Consistency beats cleverness.

### V. Data-Driven Decisions Only

No news chasing. No random indicators. No blind AI predictions. Every buy/sell decision must be traceable to: (1) Market Reality Filter pass, (2) Fundamental screen pass, (3) Technical signal with volume confirmation. If data is missing or unreliable, do not trade.

### VI. Consistent, Repeatable Process

The system is a decision engine, not a prediction machine. Every trade must follow the same layered architecture: Market Filter → Fundamental Screen → Technical Signal → Risk Check. Shortcuts through layers are prohibited.

## Trading Rules (Non-Negotiable)

### Entry Rules

- 20-day SMA must cross ABOVE 50-day SMA (golden cross)
- Price must be ABOVE 200-day SMA (long-term uptrend)
- RSI(14) between 30-60 (or crossing above 30)
- Volume ≥ 120% of 30-day average (MANDATORY)
- Stock must pass Market Reality Filter (liquidity ≥ 50K avg volume, spread <2%)

### Exit Rules

- Stop-loss at 5% below entry (3% for conservative)
- Trail stop to breakeven after +10% gain
- Trail stop to +5% after +15% gain
- RSI > 70 with MA sell signal = exit
- 20-day SMA crosses BELOW 50-day SMA = exit

### Prohibited Trading Behaviors

- Emotional averaging down (STRICTLY FORBIDDEN)
- Moving stop-loss down (STRICTLY FORBIDDEN)
- Trading without volume confirmation (STRICTLY FORBIDDEN)
- Revenge trading after losses (STRICTLY FORBIDDEN)
- Over-concentration >20% in one position (STRICTLY FORBIDDEN)

## Data & Technology Standards

### PSX Data Handling

- Use PSX DPS portal (`dps.psx.com.pk`) as primary data source
- Rate limit: 2-3 second delay between requests (~30 req/min max)
- Pagination: handle `?page=N` and `?limit=M` parameters
- Dynamic pages (DPS, financials) require Playwright, not simple HTTP
- PSX financial statements use SECP column names (not standard/international)

### Financial Ratio Standards (PSX-Specific)

- EPS: `Profit after taxation / Shares Outstanding`
- ROE: `PAT / Average Shareholders' Equity`
- P/E: `Market Price / TTM EPS`
- Debt-to-Equity: `(Non-current liabilities + Current borrowings) / Total Equity`
- Exclude operating payables from debt calculations

### AI Usage Boundaries

- AI MAY: Extract financial data, calculate ratios, summarize news, generate alerts
- AI MUST NOT: Make autonomous trading decisions, predict prices, execute trades
- Human remains final decision-maker at all times

## Development Standards

### Code Quality

- Python as primary language (data handling, calculations)
- Excel/CSV for initial validation and manual analysis
- No unnecessary abstractions — three similar lines beat premature abstraction
- No comments unless the WHY is non-obvious
- Write the smallest viable change; no unrelated edits

### Testing

- Phase 1 (Strategy Validation) happens manually in Excel before any automation
- Python scripts require basic validation tests (ratio calculations, signal logic)
- All trading rules must be independently testable
- No deployment of untested signal logic

### Security

- No secrets or tokens in code — use `.env` and docs
- No hardcoded API keys or credentials
- PSX portals use public data — no authentication secrets needed for reads

## Governance

- Constitution supersedes all other practices and coding preferences
- Amendments require: (1) user consent, (2) documented rationale, (3) ADR if architecturally significant
- All PRs/reviews must verify constitution compliance
- Version follows semantic versioning (MAJOR.MINOR.PATCH):
  - MAJOR: Principle removal or redefinition
  - MINOR: New principle or materially expanded guidance
  - PATCH: Clarifications, wording fixes
- Ratification date: 2026-05-05 (initial)
- Any change to trading rules (MA periods, RSI thresholds, risk %) requires ADR

**Version**: 1.0.0 | **Ratified**: 2026-05-05 | **Last Amended**: 2026-05-05
