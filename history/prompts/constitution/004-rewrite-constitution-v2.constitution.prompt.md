---
id: 004
title: Rewrite Constitution v2 from Research
stage: constitution
date: 2026-05-06
surface: agent
model: claude-opus-4-7
feature: none
branch: feature/psx-skills-architecture
user: architect
command: /sp.constitution
labels: [constitution, psx, research, validation-gaps, v2.0.0]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

based on @research.md if we want to start building complete application, can you write the consitution as per @.claude/commands/sp.constitution.md

## Response snapshot

Rewrote `.specify/memory/constitution.md` from v1.0.0 → v2.0.0 (MAJOR bump).

**Why MAJOR**: research.md §15 (added 2026-05-05) introduced 14 validation gaps
not encoded in v1.0.0. Two new principles added (Named Defensible Edge,
Falsifiable Operation), one renamed/expanded (Layered, Repeatable Process),
and the v1.0.0 trading rules reframed as "starting hypothesis" pending
backtest. The system scope was redrawn from "discipline + fixed rules" to
"layered application with explicit pre-deployment gates."

**Structure now includes**:
- 8 Core Principles (was 6)
- Layered Architecture with new Layer 1.5 Macro Overlay
- Trading Rules section explicitly marked "Hypothesis Status, Not Validated"
- Pre-Deployment Gates table (7 gates, six are TODOs requiring ADR resolution)
- Risk & Capital Rules with macro-factor concentration cap, earnings blackout,
  corporate-action handler, tax-loss harvesting hook
- Macro Overlay (§15.9), Sector Rotation (§15.10), Regime-Shift Protocol (§15.14)
- Phase Gating: 5B/5C deferred ≥ 12 months profitable Phase 1/2 (§15.12)

**Six deferred TODOs** (each blocks live capital, each requires an ADR):
- TODO(EDGE_DEFINITION) — §15.1
- TODO(POSITION_MATH_RECONCILIATION) — §15.4
- TODO(CGT_EXIT_POLICY) — §15.6
- TODO(FALSIFICATION_NUMBERS) — §15.7
- TODO(MACRO_OVERLAY_RULES) — §15.9
- TODO(REGIME_SHIFT_THRESHOLDS) — §15.14

**Templates**: all dependent templates (plan, spec, tasks, phr, sp.constitution
command) verified compatible — no edits required. Sync Impact Report at top of
constitution lists each as ✅.

**Ratification**: 2026-05-05 preserved. Last Amended: 2026-05-06.

User decisions captured (via AskUserQuestion):
1. Scope = MAJOR rewrite (v2.0.0), not minor amendment.
2. Edge = codify as open TODO, do not defer the whole constitution.
3. Concrete numbers (§15.4/15.6/15.7/15.9/15.14) = mark as TODO + ADR-required.

## Outcome

- ✅ Impact: Constitution now encodes the full system the application will
  enforce, including the §15 validation gaps. v1.0.0 superseded; trading
  rules reframed as hypothesis pending Phase 1 backtest.
- 🧪 Tests: none — documentation/governance change.
- 📁 Files: `.specify/memory/constitution.md` rewritten (v1.0.0 → v2.0.0).
- 🔁 Next prompts:
  1. `/sp.adr constitution-v2-rewrite` — record the redefinition itself.
  2. `/sp.adr edge-definition` — close TODO(EDGE_DEFINITION).
  3. `/sp.adr position-math-reconciliation` — close TODO(POSITION_MATH_RECONCILIATION).
  4. `/sp.adr falsification-criteria` — close TODO(FALSIFICATION_NUMBERS).
  5. Run Phase 1 backtest before any further code.
- 🧠 Reflection: The honest move was to name unresolved items as TODO inside
  the constitution rather than fabricate plausible defaults. Pre-Deployment
  Gates table makes the blockers visible at every plan-time Constitution
  Check, not just at first read.

## Evaluation notes (flywheel)

- Failure modes observed: none in this exchange. Risk: the six TODOs could
  remain open indefinitely; the gating language ("MUST NOT deploy live
  capital while open") is the safeguard.
- Graders run and results (PASS/FAIL): PASS — constitution has no stray
  `[ALL_CAPS]` placeholders, ISO dates, MUST/SHOULD language, version line
  matches Sync Impact Report, ratification date preserved.
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): when /sp.plan is next run,
  verify the Constitution Check gate surfaces the six TODOs as concrete
  blockers — this validates the constitution → plan-template integration.
