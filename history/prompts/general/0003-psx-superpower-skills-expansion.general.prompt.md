---
id: 0003
title: PSX superpower skills expansion
stage: general
date: 2026-05-05
surface: agent
model: claude-opus-4-7[1m]
feature: none
branch: feature/psx-skills-architecture
user: architect
command: (free-form)
labels: ["skills", "psx", "architecture", "expansion"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/psx-market-filter/SKILL.md
  - .claude/skills/psx-market-filter/references/manipulation-patterns.md
  - .claude/skills/psx-market-filter/references/liquidity-tiers.md
  - .claude/skills/psx-market-filter/references/circuit-rules.md
  - .claude/skills/psx-market-filter/references/freefloat-data.md
  - .claude/skills/psx-backtester/SKILL.md
  - .claude/skills/psx-backtester/references/psx-frictions.md
  - .claude/skills/psx-backtester/references/psx-calendar.md
  - .claude/skills/psx-backtester/references/walk-forward.md
  - .claude/skills/psx-backtester/references/metrics-formulas.md
  - .claude/skills/psx-trade-journal/SKILL.md
  - .claude/skills/psx-trade-journal/references/journal-schema.md
  - .claude/skills/psx-trade-journal/references/metric-formulas.md
  - .claude/skills/psx-trade-journal/references/rule-violations.md
  - .claude/skills/psx-trade-journal/references/review-templates.md
  - .claude/skills/psx-orchestrator/SKILL.md
  - .claude/skills/psx-orchestrator/references/pipeline-contract.md
  - .claude/skills/psx-orchestrator/references/run-modes.md
  - .claude/skills/psx-orchestrator/references/decision-sheet-template.md
  - .claude/skills/psx-orchestrator/references/override-policy.md
tests:
  - none (skills are documentation; runtime tests TBD when implementing)
---

## Prompt

first read @research.md then read these 4 skills  PSX Investment System (project-specific):
  - financial-ratios-psx — compute ratios from PSX statements
  - psx-data-fetcher — fetch PSX/DPS market & fundamental data
  - risk-management — position sizing, stop-loss, capital rules
  - trade-rules-engine — entry/exit signals (MA, RSI, volume) is this fine or need improvement, convert these skills in super power skills

(Follow-up answer: "a" — selected option A: create the 4 missing skills + populate references/ directories.)

## Response snapshot

Audited the existing 4 PSX skills against research.md. Verdict: solid foundation but
incomplete relative to research.md's full architecture. Identified 4 critical gaps:

1. Layer 0 Market Reality Filter not a first-class skill (research.md §4 calls it CRITICAL).
2. No backtesting/validation skill — research.md §8 Phase 1 says "if not profitable → STOP".
3. No trade journal / performance tracker — research.md §10 demands CAGR/Sharpe/drawdown.
4. No orchestrator — the 4 skills are siloed; nothing chains the pipeline.

Created 4 new skills + 16 reference docs, all aligned to research.md sections:

- psx-market-filter (Layer 0, research.md §4): liquidity, spread, operator behavior,
  volume spike, circuit-lock filters; capital-tier adjustments.
- psx-backtester (Phase 1 gate, research.md §8): PSX frictions (commission, CGT,
  slippage, T+2), holiday calendar, walk-forward validation, 8 PASS/FAIL thresholds.
- psx-trade-journal (research.md §10): append-only schema, metric formulas, rule-violation
  detector, monthly/quarterly/YTD review templates.
- psx-orchestrator (research.md §4 full pipeline): chains all 7 specialist skills in
  fixed order, three run modes (dry-run/journal-only/apply), decision-sheet output,
  override policy that refuses to weaken hard rules.

Existing skills unchanged. The 8-skill set now covers Layer 0 → Layer 3 plus
validation, journaling, and orchestration.

## Outcome

- ✅ Impact: PSX investment system now has end-to-end skill coverage matching research.md
- 🧪 Tests: none yet — skills are docs; tests come when implementing referenced code paths
- 📁 Files: 4 new SKILL.md + 16 reference .md files (20 files total under .claude/skills/)
- 🔁 Next prompts: implement orchestrator pipeline; build sample backtest run; wire data-fetcher to a real PSX symbol
- 🧠 Reflection: research.md is highly opinionated ("Discipline > Intelligence") — the new skills mirror that by encoding hard rules as non-negotiable, with explicit ADR triggers when overrides are requested

## Evaluation notes (flywheel)

- Failure modes observed: initial assessment incorrectly claimed reference/ files were vapor; verified they exist before final write
- Graders run and results (PASS/FAIL): n/a (no executable graders defined yet)
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): generate a sample decision sheet from synthetic data to validate the orchestrator's output contract
