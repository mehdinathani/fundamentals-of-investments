---
id: 001
title: Create PSX skills and constitution
stage: constitution
date: 2026-05-05
surface: agent
model: claude-opus-4-7
feature: none
branch: master
user: AIDD
command: /sp.constitution
labels: ["psx","skills","constitution","finance"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/psx-data-fetcher/SKILL.md
  - .claude/skills/psx-data-fetcher/references/endpoints.md
  - .claude/skills/psx-data-fetcher/references/playwright-patterns.md
  - .claude/skills/psx-data-fetcher/references/rate-limits.md
  - .claude/skills/psx-data-fetcher/references/data-dictionary.md
  - .claude/skills/psx-data-fetcher/references/psx-symbols.md
  - .claude/skills/financial-ratios-psx/SKILL.md
  - .claude/skills/financial-ratios-psx/references/psx-column-mapping.md
  - .claude/skills/financial-ratios-psx/references/ratio-formulas.md
  - .claude/skills/financial-ratios-psx/references/statement-samples.md
  - .claude/skills/financial-ratios-psx/references/unit-conversions.md
  - .claude/skills/trade-rules-engine/SKILL.md
  - .claude/skills/trade-rules-engine/references/ma-crossover-logic.md
  - .claude/skills/trade-rules-engine/references/rsi-rules.md
  - .claude/skills/trade-rules-engine/references/volume-confirmation.md
  - .claude/skills/trade-rules-engine/references/signal-examples.md
  - .claude/skills/risk-management/SKILL.md
  - .claude/skills/risk-management/references/position-sizing.md
  - .claude/skills/risk-management/references/stop-loss.md
  - .claude/skills/risk-management/references/portfolio-limits.md
  - .claude/skills/risk-management/references/prohibited-behaviors.md
  - .specify/memory/constitution.md
tests:
  - N/A (constitution and skills creation)
---

## Prompt

read @research.md file to understand the project details, you are responsible to create high level skills using detail study of finance you are required to create for below .claude/skills/psx-data-fetcher.md Teaches Claude Code exactly how PSX's DPS portal is structured, which endpoints to scrape, rate limit rules, and how to handle pagination. .claude/skills/financial-ratios-psx.md Defines the exact formulas for ROE, P/E, EPS, Debt-to-Equity using PSX's specific financial statement format (their column names differ from standard). .claude/skills/trade-rules-engine.md Documents your exact entry/exit logic — MA crossovers, RSI thresholds, volume confirmation rules. Claude Code must never invent these. .claude/skills/risk-management.md Encodes your 3–5% max loss rule, position sizing formula, stop-loss logic. This is your capital protection layer — it must be explicit. using skills creater skills

## Response snapshot

Created 4 production-grade skills for the PSX investment system:

1. **psx-data-fetcher** — DPS portal endpoints, rate limits (2-3s delay, ~30 req/min), pagination patterns, Playwright scraping recipes, PSX URL structures
2. **financial-ratios-psx** — PSX column name mappings (e.g., "Profit after taxation" not "Net Income"), ratio formulas (ROE, P/E, EPS, Debt-to-Equity), unit conversions, statement samples
3. **trade-rules-engine** — MA(20/50/200) crossover logic, RSI(14) 30/70 thresholds, volume confirmation (≥120%), signal tiers, complete signal flow
4. **risk-management** — 3-5% max loss per trade, position sizing formula, trailing stop logic, prohibited behaviors (no averaging down, no moving stops down), portfolio limits

Also created initial constitution v1.0.0 with 6 core principles (Strategy Over Tools, Finance-First, Risk Control Over Profit, Discipline Over Intelligence, Data-Driven Decisions Only, Consistent Process) and updated governance.

## Outcome

- ✅ Impact: New skills + constitution for PSX investment system
- 🧪 Tests: N/A (documentation/skills creation)
- 📁 Files: 23 files created (4 SKILL.md + 19 reference files + constitution.md)
- 🔁 Next prompts: Implement Phase 1 strategy validation in Excel/Python
- 🧠 Reflection: Skills follow skill-creator-pro framework with domain discovery, embedded knowledge in references/, and zero-shot capable structure

## Evaluation notes (flywheel)

- Failure modes observed: WebSearch for PSX-specific data returned empty; worked around with WebFetch on PSX portals directly
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
