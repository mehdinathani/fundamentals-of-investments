# ADR-002: Pre-Deployment Strategy Decisions for PSX Investment System

> **Scope**: Captures the open strategic decisions surfaced by the 2026-05-05
> validation of `research.md`. These are decisions the architect must make
> **before** any live capital is deployed in Phase 1. Each decision has
> alternatives; this ADR records the option set and the path to commitment.

- **Status:** Accepted (2026-05-30)
- **Date:** 2026-05-05
- **Feature:** psx-investment-system
- **Resolution:** All 13 decisions resolved per preferred paths. Edge defined (B+A). ADR-003 (Macro Overlay) spawned per Decision 8.
- **Context:** Validation critique against `research.md` § 15 (Open Gaps & TODOs).

<!-- Significance checklist
     1) Impact: YES — these decisions determine whether the system has actual
        edge or is a disciplined index follower. They also determine how much
        capital can be safely committed in Phase 1.
     2) Alternatives: YES — every decision below has at least two viable paths
        and meaningful trade-offs.
     3) Scope: YES — cuts across strategy, risk, infrastructure, and roadmap.
-->

## Context

`research.md` defines a finance-first PSX investment system, but a structured
validation surfaced 14 open gaps (§15.1 – §15.14). They group into four
decision clusters that must be resolved before live deployment:

1. **Edge & Strategy** (§15.1, 15.2, 15.3, 15.7) — what asymmetry are we
   exploiting, do the rules actually capture it, and how do we know if we're
   wrong?
2. **Position & Risk Math** (§15.4, 15.5, 15.6) — internal rule conflicts
   (positions × concentration vs cash reserve), no-trade-period discipline,
   tax-aware exits.
3. **Macro & Diversification** (§15.8, 15.9, 15.10, 15.14) — PSX is
   macro-dominated; the framework is not.
4. **Operational** (§15.11, 15.12, 15.13) — earnings, corporate actions,
   Phase 5 deferral, tax-loss harvesting.

This ADR enumerates the decisions, lists viable options, and records the
preferred path. Each decision becomes a follow-up artifact (rule update in
research.md, or its own ADR if it spawns architectural change).

## Decisions Required

### Decision 1: Name the Edge (§15.1) — CRITICAL, BLOCKING

The single sentence: *"I make money on PSX because of [X] that other
participants don't or can't exploit."*

**Options:**
- **A. Behavioral edge.** Exploit retail panic / sponsor-driven manipulation
  cycles via Layer 0 filter + disciplined stop-loss. Edge = surviving
  drawdowns that retail can't, and avoiding manipulated names.
- **B. Time-horizon edge.** Hold winners longer than retail (which churns
  weekly), capture multi-quarter trends in fundamentally strong names with
  lower CGT (>12 months). Edge = patience + tax bracket arbitrage.
- **C. Information-processing edge.** Exploit slow PSX disclosure → reaction
  cycle. When Q-results land, retail/algos lag; you act in next-day open
  on parsed financials. Edge = speed of structured-data extraction.
- **D. Structural edge.** None — accept the system will earn ~KSE-100
  net of costs. Reframe goal as *risk-controlled index participation*,
  not alpha.

**Preferred path:** **B + partial A.** Behavioral discipline (A) protects
capital; time-horizon (B) is the source of net-of-CGT outperformance.
Information edge (C) requires infrastructure that doesn't yet exist.

**Action:** Edge sentence committed: *"I make money on PSX by holding fundamentally strong, liquid names through multi-quarter trends (time-horizon asymmetry), while systematically avoiding manipulated and illiquid stocks via the Layer 0 filter (behavioral discipline)."*

---

### Decision 2: Strategy Validation Gate (§15.2) — BLOCKING

**Options:**
- **A. Backtest current rules as-is.** Run `psx-backtester` on 2018-2024 PSX
  data. If Sharpe ≥ 1.0 net of all costs → proceed. If < 1.0 → iterate or stop.
- **B. Iterate first, then backtest.** Refine rules based on PSX-specific
  research (sector medians, macro overlays) before backtesting. Risk: more
  curve-fit pressure.
- **C. Skip backtest, deploy with small capital (paper-money equivalent).**
  Risk: 6-12 months wasted if rules are losing.

**Preferred path:** **A.** Test the documented strategy honestly. If it fails,
that's information — iterate or pivot. Skipping the backtest violates §8 Phase 1
which says "if not profitable → STOP."

**Action:** Run backtest before any live trade. Acceptance threshold:
Sharpe ≥ 1.0, max drawdown ≤ 15%, win/loss ≥ 2.0, expectancy > 0, ≥ 30 trades
in OOS window of ≥ 6 months.

---

### Decision 3: Calibrate Fundamental Thresholds (§15.3)

**Options:**
- **A. Keep hard thresholds** (Rev CAGR > 8%, PAT CAGR > 10%, D/E < 0.6).
  Simple but excludes banks/leveraged sectors.
- **B. Sector-relative thresholds.** Each metric vs the sector median. Captures
  more nuance; banks aren't punished for normal D/E.
- **C. Score-based ranking.** Replace hard cuts with a 0-100 fundamental score
  using sector-relative percentiles. Top-N by score enters watchlist.

**Preferred path:** **C.** Most flexible, most defensible, easiest to tune.
Hard thresholds remain as floors (e.g., positive PAT in 3 of 4 quarters
stays as a hard rule).

**Action:** Implement scoring in `financial-ratios-psx` skill before
Phase 1. Document scoring formula in `references/`.

---

### Decision 4: Resolve Position-Math Conflict (§15.4) — TRIVIAL, FIX NOW

Current rules: max 7 positions × 20% concentration = 140%, AND ≥ 30% cash. Conflicts.

**Options:**
- **A. Cap concurrent positions at 3-4.** 3 × 20% = 60% invested, 40% cash.
- **B. Reduce per-position cap to ~10%.** 7 × 10% = 70% invested, 30% cash.
- **C. Hybrid: max 5 positions × 14%.** 5 × 14% = 70% invested, 30% cash.

**Preferred path:** **B.** Maintains 7-stock optionality; tighter per-position
caps reduce single-name blowup risk. 10% per position aligns with conservative
PSX practice for retail.

**Action:** Update `risk-management/SKILL.md` and `research.md` §4 Layer 3.
This is non-negotiable before any live trade.

---

### Decision 5: Falsification Criterion (§15.7) — BLOCKING

**Options:**
- **A. Trade-count + Sharpe gate.** "After 50 trades over ≥ 6 months,
  if Sharpe < 0.5 OR I underperform KSE-100 by > 5% net, stop."
- **B. Drawdown gate.** "If account drawdown > 15% from peak at any point, stop."
- **C. Time gate.** "After 12 months of live trading, if net of costs and CGT
  I underperform PKR T-bills, stop."
- **D. All three (any-of).** Most rigorous; any single failure halts.

**Preferred path:** **D (any-of A, B, C).** Each captures a different failure
mode. Stopping is not an admission of permanent failure — it triggers
re-evaluation, possibly resumption with revised rules + new ADR.

**Action:** Add to `research.md` §11 (Key Principles) as Principle 6.
Numeric values must be committed in writing before Phase 1 begins.

---

### Decision 6: No-Trade-Period Discipline (§15.5)

**Options:**
- **A. Hard frequency cap.** Max 2 entries / week regardless of signal count.
- **B. Soft journaling rule.** Track and review; no hard cap.
- **C. Cash-deployment ceiling.** Force minimum days-between-entries based on
  current cash %.

**Preferred path:** **A.** Hard limits beat soft norms when willpower is the
constraint. Discipline > intelligence (Constitution).

**Action:** Update `risk-management` and `psx-orchestrator` to enforce the
weekly entry cap.

---

### Decision 7: Tax-Aware vs Tax-Agnostic Exits (§15.6)

**Options:**
- **A. Tax-agnostic.** Take signals when they fire. Simpler. Higher net CGT.
- **B. Soft tax-aware.** When a profit-taking exit fires within 30 days of
  the 6-month boundary, defer to cross 6-month CGT bracket if technicals
  remain neutral.
- **C. Hard tax-aware.** Optimize all exits around CGT brackets. Complex;
  risks turning a strategy into a tax-deferral scheme.

**Preferred path:** **B.** Acknowledges CGT impact without distorting strategy.

**Action:** Add tax-aware deferral logic to `trade-rules-engine` exit section.
Simulate the impact in backtest (compare A vs B net returns).

---

### Decision 8: Macro Overlay (Layer 1.5) (§15.9)

**Options:**
- **A. Add Layer 1.5 macro overlay.** SBP rates, USD/PKR, IMF status,
  KSE-100 valuation. Tightens universe in risk-off regimes.
- **B. Stay micro-focused.** Trust Layer 0 + Layer 1 + Layer 2 to do the work.
- **C. Macro as filter only (no allocation change).** Block new entries in
  risk-off; existing positions unchanged.

**Preferred path:** **A.** PSX is macro-dominated; ignoring this is the largest
unforced error a Pakistani equity strategy can make.

**Action:** This is architecturally significant — spawn ADR-003
("PSX Macro Overlay Layer") if accepted. Until then, document as a
research.md TODO.

---

### Decision 9: Sector Rotation (§15.10)

**Options:**
- **A. Sector momentum filter.** Avoid bottom-quartile sectors regardless
  of stock fundamentals.
- **B. No sector rotation.** Pick best stocks anywhere.
- **C. Sector budget.** Allocate position counts across top 3 sectors only.

**Preferred path:** **A.** Already partially in `trade-rules-engine` (Rule 2
"Sector momentum"). Strengthen and operationalize.

**Action:** Add concrete sector-momentum metric to `trade-rules-engine`
references. Quarterly review.

---

### Decision 10: Earnings Blackout (§15.11)

**Options:**
- **A. Hard blackout.** Flat into all earnings unless thesis explicitly
  requires holding (and is documented in journal).
- **B. Position reduction.** Halve positions before earnings; reinstate after.
- **C. Tighten stops only.** Move stop to breakeven or tighter pre-earnings.

**Preferred path:** **A.** Earnings gaps on PSX can exceed 20% — exceeds
risk-management's max-loss tolerance.

**Action:** Add earnings calendar awareness to `psx-data-fetcher`. Hard rule
in `risk-management`.

---

### Decision 11: Phase 5 Deferral (§15.12)

**Options:**
- **A. Defer Phase 5B (SaaS) and 5C (Signal Service) until Year 2 of
  profitable Phase 1/2.** Personal Wealth Engine (5A) only until then.
- **B. Keep Phase 5 in scope.** Risk: regulatory exposure, premature
  productization.
- **C. Remove Phase 5 entirely.** Personal capital growth only.

**Preferred path:** **A.** Deferral is reversible; premature SaaS isn't.

**Action:** Update `research.md` §8 Phase 5 with the deferral rule.

---

### Decision 12: Tax-Loss Harvesting (§15.13)

**Options:**
- **A. Annual Q4 routine.** Harvest losses on positions held < 12 months
  to offset realized gains.
- **B. Continuous.** Apply as opportunities arise.
- **C. None.** Skip; accept full CGT bill.

**Preferred path:** **A.** Concentrated effort once per year; doesn't
distort during-year strategy.

**Action:** Add to `psx-trade-journal` annual review template.

---

### Decision 13: Regime-Shift Detector (§15.14)

**Options:**
- **A. Halt trigger.** When 3+ open positions hit stops within 5 trading days,
  halt new entries pending macro reassessment.
- **B. Drawdown trigger.** When portfolio dd > 5% in 5 days, halt.
- **C. No detector.** Trust per-trade stops only.

**Preferred path:** **A.** Captures regime shifts that per-trade stops miss.
Aligns with Layer 0 philosophy — discipline beats reaction.

**Action:** Add to `psx-orchestrator` as a pre-pipeline check.

---

## Consequences

### Positive

- Forces explicit edge definition before capital deployment — biggest single
  risk reduction in the system.
- Resolves internal rule conflicts (especially §15.4) that would have caused
  silent failures in live trading.
- Adds falsification criterion — the system can recognize and respond to its
  own failure rather than rationalizing.
- Macro overlay closes the largest analytical gap for a PKR equity strategy.
- Defers SaaS/signal-service distraction until core strategy is proven.

### Negative

- Adds complexity to skills (sector scoring, macro overlay, regime detector,
  tax-aware logic) — more code surface, more test surface.
- Several decisions (1, 2, 5) are blocking — Phase 1 cannot start until they're
  resolved. May delay deployment by weeks.
- Tax-aware logic risks slipping into tax optimization rather than strategy.
- Macro overlay requires data sources (USD/PKR, SBP rates) not currently
  in `psx-data-fetcher` — additional skill scope.

## Alternatives Considered

**Cluster-level alternative — "Defer All Decisions, Trade Now":**
Skip these 13 decisions, deploy with current rules, learn from live PnL.

Rejected because:
- Violates Constitution Principle 3 (Risk Control > Profit) and Principle 4
  (Consistency > Excitement).
- §8 Phase 1 explicitly requires validation before deployment.
- The §15.4 position-math conflict alone would cause rule violations on the
  first multi-position day.

**Cluster-level alternative — "One Mega-ADR Per Decision":**
Spawn 13 ADRs, one per decision.

Rejected because:
- ADR template guidance says group related decisions; these all serve
  pre-deployment readiness.
- Individual ADRs would obscure the cluster nature of "what must be true
  before live trading."
- ADR-003 (Macro Overlay) is the only sub-cluster significant enough to
  warrant its own ADR if Decision 8 is accepted.

## References

- Research: `research.md` §15 (Open Gaps & TODOs) — added 2026-05-05
- Constitution: `.specify/memory/constitution.md`
- Skills: `.claude/skills/psx-*` (8 skills affected by these decisions)
- Predecessor ADR: `history/adr/ADR-001-psx-skills-architecture.md`
  (defined the 4-skill foundation; this ADR layers strategic decisions on top)
- Validation conversation: PHR `history/prompts/general/0003-psx-superpower-skills-expansion.general.prompt.md`
- Related future ADR: ADR-003 ("PSX Macro Overlay Layer") — to be created if
  Decision 8 is accepted
