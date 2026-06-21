---
id: 002
title: PSX skills architecture ADR
stage: constitution
date: 2026-05-05
surface: agent
model: claude-opus-4-7
feature: none
branch: master
user: AIDD
command: /sp.adr
labels: ["psx","adr","skills","architecture"]
links:
  spec: null
  ticket: null
  adr: history/adr/ADR-001-psx-skills-architecture.md
  pr: null
files:
  - history/adr/ADR-001-psx-skills-architecture.md
tests:
  - N/A (ADR creation)
---

## Prompt

/sp.adr psx-skills-architecture

## Response snapshot

Created ADR-001: PSX Skills Architecture documenting the decision to split PSX domain knowledge into 4 specialized skills (psx-data-fetcher, financial-ratios-psx, trade-rules-engine, risk-management) with embedded domain expertise and progressive disclosure.

Key decision: 4 skills with SKILL.md + references/ structure over monolithic doc or single config.
Alternatives considered: Monolithic document (rejected: no progressive disclosure), one skill per feature (rejected: trading/risk have independent change cycles), no skills with WebSearch (rejected: violates "AI must not invent rules"), hybrid with central config (rejected: constants not configuration).

## Outcome

- ✅ Impact: ADR created for skills architecture decision
- 🧪 Tests: N/A (ADR document)
- 📁 Files: 1 ADR file created
- 🔁 Next prompts: /sp.tasks (to generate implementation tasks)
- 🧠 Reflection: ADR properly clusters related decisions (4 skills as integrated architecture), lists 4 alternatives with rationale, covers positive/negative consequences

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): All 4 significance tests PASSED (impact: yes, alternatives: 4 considered, scope: cross-cutting)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
