# ADR-001: PSX Skills Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-05-05
- **Feature:** psx-investment-system

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
        YES — Skills define how all future PSX system development interacts with domain knowledge.
     2) Alternatives: Multiple viable options considered with tradeoffs?
        YES — Monolithic doc vs multi-skill vs skill-per-domain (see Alternatives).
     3) Scope: Cross-cutting concern (not an isolated detail)?
        YES — All 4 skills form the foundation for data fetching, analysis, trading, and risk.
-->

## Context

The PSX investment system needs domain expertise encoded so Claude Code can execute financial tasks without inventing market rules. The system requires: (1) PSX data portal knowledge, (2) PSX-specific financial ratio formulas, (3) Exact trading signal logic, and (4) Non-negotiable risk management rules.

Key constraints:
- PSX uses SECP-prescribed financial statement formats with non-standard column names
- Trading rules (MA periods, RSI thresholds, volume confirmation) must never be modified or invented
- Risk rules (3-5% max loss, position sizing, prohibited behaviors) are survival mechanisms
- The system is finance-first, technology-second per the constitution

## Decision

**Architecture: 4 Specialized Skills with Embedded Domain Expertise**

The domain knowledge is split into 4 focused skills, each with `SKILL.md` + `references/` structure:

| Skill | Type | Purpose |
|-------|------|---------|
| `psx-data-fetcher` | Automation | DPS portal endpoints, rate limits, pagination, Playwright patterns |
| `financial-ratios-psx` | Analyzer | PSX column mappings, ratio formulas (ROE/P/E/EPS/Debt-to-Equity), unit conversions |
| `trade-rules-engine` | Validator | MA(20/50/200) crossover, RSI(14) 30/70, volume ≥120%, signal tiers |
| `risk-management` | Validator | 3-5% max loss, position sizing formula, stop-loss (fixed + trailing), prohibited behaviors |

**Skill structure pattern (from skill-creator-pro):**
- `SKILL.md` (<500 lines): What/What NOT, Before Implementation, core rules, checklist
- `references/`: Domain expertise (endpoint maps, column mappings, formula implementations, examples)
- Progressive disclosure: Metadata → SKILL.md → references/

## Consequences

### Positive

- **Zero-shot expertise**: Claude Code becomes a PSX domain expert without runtime discovery
- **Non-negotiable rules protected**: Trading parameters (20/50/200 MA, 30/70 RSI, 3-5% risk) are hardcoded in skills, not tweakable defaults
- **Separaton of concerns**: Data fetching, analysis, signals, and risk are independent — changes to one don't cascade
- **Reusability**: Each skill handles variations (user's stocks, date ranges) while constants (PSX endpoints, formulas, thresholds) are embedded
- **Constitutional alignment**: Skills directly implement the 6 core principles (Strategy Over Tools, Risk Control Over Profit, etc.)

### Negative

- **Maintenance burden**: PSX portal changes (DPS endpoints, column names) require manual skill updates
- **Four separate skills**: More files to maintain vs a single monolithic document
- **No dynamic adaptation**: If PSX changes financial statement formats, skills don't auto-detect — manual update required
- **Skill count will grow**: As features expand (backtesting, dashboard), more skills needed

## Alternatives Considered

**Alternative A: Single Monolithic Document**
- One `psx-knowledge.md` containing all endpoints, formulas, rules, and ratios
- *Why rejected*: Would exceed 2000 lines, violates <500 lines/SKILL.md guideline, no progressive disclosure, Claude Code loads all knowledge even when only fetching data

**Alternative B: One Skill Per Feature (not per domain)**
- Merge `trade-rules-engine` + `risk-management` into one `trading-system` skill
- *Why rejected*: Trading rules and risk management are independent concerns with different change cycles — risk rules are constitutional (never change), trading rules change only with ADR

**Alternative C: No Skills, Rely on research.md + WebSearch**
- Keep `research.md` as the only knowledge source, let Claude Code discover PSX details at runtime
- *Why rejected*: Violates "AI MUST NOT invent trading rules" requirement, no guarantee Claude uses correct MA periods or RSI thresholds, WebSearch for PSX endpoints returned empty in testing

**Alternative D: Hybrid — Skills + Central Config**
- Skills reference a central `psx-config.json` for all parameters (MA periods, thresholds, endpoints)
- *Why rejected*: Adds indirection without benefit — parameters are non-negotiable constants, not configuration; risks accidental modification of critical values

## References

- Project Research: `research.md` (Section 4: System Architecture, Layers 0-3)
- Constitution: `.specify/memory/constitution.md` (v1.0.0, Principles I-VI)
- Skill Framework: `skill-creator-pro` (skill-creator-pro references/)
- Templates: `.specify/templates/adr-template.md`
