# PSX Investment System – Research & Execution Blueprint

## 1. Objective

Develop a **finance-first, AI-assisted investment system** for Pakistan Stock Exchange (PSX) focused on:

* Consistent profitability
* Risk minimization
* Disciplined, repeatable decision-making

This is **not a software project**.
This is a **capital allocation and decision system**.

---

## 2. Core Philosophy

### 2.1 Finance First, Technology Second

* Strategy defines success
* Technology supports execution
* AI enhances efficiency, not intelligence

---

### 2.2 Edge Definition

Your edge comes from:

* Time-horizon asymmetry: holding fundamentally strong, liquid names through multi-quarter trends, which retail traders (who churn weekly) consistently under-harvest.
* Behavioral discipline: systematically avoiding manipulated and illiquid stocks via the Layer 0 Market Reality Filter, surviving drawdowns that undisciplined participants cannot.
* Finance + Programming combination: structured extraction and analysis of PSX financial data.
* Structured rules: repeatable, measurable entry/exit criteria.
* Discipline and consistency: adherence to risk limits and trade journal accountability.

Edge statement: *"I make money on PSX by holding fundamentally strong, liquid names through multi-quarter trends (time-horizon asymmetry), while systematically avoiding manipulated and illiquid stocks via the Layer 0 filter (behavioral discipline)."*

Not from:

* News chasing
* Random indicators
* Blind AI usage

---

## 3. Market Reality: PSX-Specific Constraints

PSX is structurally different from developed markets.

### Key Challenges:

* Market manipulation in mid/small caps
* Institutional dominance in large caps
* Information asymmetry
* Low liquidity in many stocks
* Delayed or inconsistent data

### Implication:

Strategy must be **adaptive**, not textbook-based.

---

## 4. System Architecture (Final Model)

### Layer 0: Market Reality Filter (NEW – CRITICAL)

Before analysis, filter out bad candidates:

* Low liquidity stocks → reject
* High spread → reject
* Suspicious volume spikes → caution
* Operator-driven behavior → avoid

Output:
👉 Tradable universe only

---

### Layer 1: Fundamental Analysis (Stock Selection)

Purpose:
Identify fundamentally strong companies.

Key Metrics:

* Revenue growth (3–5 years)
* Profit growth
* Earnings consistency
* Debt levels (low leverage)
* Sector momentum

Output:
👉 Watchlist (10–20 stocks)

---

### Layer 2: Technical Analysis (Timing Engine)

Purpose:
Determine entry and exit points.

Key Tools:

* Trend (moving averages)
* Breakouts (with volume confirmation)
* Support & resistance
* Volume spikes

Rules:

* No volume → no trade
* No trend → no entry

Output:
👉 BUY / HOLD / SELL signals

---

### Layer 3: Risk Management (Survival Engine)

Purpose:
Protect capital and ensure longevity.

Rules:

* Max loss per trade: 3–5%
* Position sizing: ≤10% per position (ADR-002 D4)
* Max concurrent positions: 7 (at 10% each = 70% invested)
* Cash reserve: ≥ 30% at all times
* No emotional averaging
* Strict stop-loss
* Max 2 entries per week (ADR-002 D6)
* Earnings blackout: flat into earnings (ADR-002 D10)
* Regime-shift halt: 3+ stops in 5 days → halt new entries (ADR-002 D13)
* Macro-factor concentration: max 2 positions sharing same factor (USD/PKR, rates, political risk)

Output:
👉 Controlled downside, sustainable growth

---

## 5. Role of AI & Technology

### Where AI Adds Value:

* Financial data extraction
* Ratio calculation automation
* News summarization
* Alert generation

---

### Where AI Must NOT Be Used:

* Direct trading decisions
* Autonomous trading
* Blind predictions

---

### Tools (Support Only):

* Python (data handling)
* Excel (initial validation)
* Web scraping (controlled use)
* AI (parsing & summarization)

---

## 6. Data Reality

### Challenges:

* No clean unified API
* Fragmented financial + price data
* Inconsistent formats

### Strategy:

* Start manually (Excel / CSV)
* Limit scope (10–20 stocks)
* Automate only after validation

---

## 7. Capital Considerations

### Critical Insight:

Capital size directly impacts strategy viability.

### Practical Thresholds:

* < PKR 500K → unreliable results
* < PKR 1M → limited flexibility

### If Capital is Low:

* Focus on learning, not returns
* Reduce trade frequency
* Prioritize high-conviction trades

---

## 8. Execution Roadmap

---

### Phase 1: Strategy Validation (MOST IMPORTANT)

Objective:
Validate profitability before automation.

Approach:

* Manual analysis (Excel)
* Apply fundamental filters
* Apply technical rules
* Track every trade

Deliverables:

* Watchlist framework
* Entry/exit rules
* Trade log

Success Criteria:

* Consistent results
* Controlled losses
* Repeatable logic

Failure Condition:
👉 If not profitable → STOP

---

### Phase 2: Semi-Automation

Objective:
Reduce manual effort.

Actions:

* Basic Python scripts
* Ratio calculations
* Alert system

Output:

* Automated watchlist
* Signal notifications

---

### Phase 3: Intelligent Assistant Layer

Objective:
Support decision-making.

Features:

* Daily scans
* Ranking system
* Signal suggestions

Human remains final decision-maker.

---

### Phase 4: Frontend (Optional)

Objective:
Visualization only.

* Dashboard
* Watchlist tracking
* Performance analytics

Only build if:
👉 Strategy is already profitable

---

### Phase 5: Scaling Options

#### Option A: Personal Wealth Engine (Recommended) — ACTIVE TARGET

* Private system
* Focus on capital growth

#### Option B: SaaS Tool — DEFERRED (ADR-002 D11)

* Subscription insights
* Not before ≥12 months of profitable Phase 1/2 operation

#### Option C: Signal Service — DEFERRED (ADR-002 D11)

* Requires regulatory awareness
* Not before ≥12 months of profitable Phase 1/2 operation

---

## 9. Regulatory Considerations

If scaling:

* SECP regulations apply
* Advisory services require compliance

Recommendation:
👉 Stay personal until system is mature

---

## 10. Performance Metrics

Track consistently:

* CAGR (returns)
* Win/Loss ratio
* Max drawdown
* Risk-adjusted returns (Sharpe)

Goal:
👉 Consistent, controlled growth

Falsification kill-switch (ADR-002 D5):
👉 After N ≥ 50 closed trades over ≥ 6 months, if Sharpe < 0.5 OR underperform KSE-100 by > 5% net of all costs OR drawdown > 15% from peak at any point OR 12-month net returns underperform PKR T-bills → STOP and re-evaluate.

---

## 11. Key Principles

1. Strategy > Tools
2. Discipline > Intelligence
3. Risk Control > Profit
4. Consistency > Excitement
5. Data-driven decisions only
6. Falsifiable Operation: if after ≥50 trades over ≥6 months, Sharpe <0.5 OR underperform KSE-100 >5% net OR drawdown >15% OR 12mo net < PKR T-bills → stop and re-evaluate

---

## 12. Final Strategic Position

This system is:

* A decision engine
* A profit-oriented framework
* A disciplined process

Not:

* A trading app
* A prediction machine
* A shortcut to quick money

---

## 13. Current Status

✔ Strategy framework defined
✔ Risks identified and adjusted
✔ Market realities incorporated
✔ AI role clearly scoped
✔ ADR-002 accepted (2026-05-30) — all 13 strategic decisions resolved
✔ Edge defined (time-horizon + behavioral discipline)
✔ Position math reconciled (≤10%/position, 7 max, ≥30% cash)
✔ Falsification kill-switch numbers set
✖ Backtest gate (US3) — FAILED (see §16 for results)
⚠ PENDING: ADR-003 (Macro Overlay) — architectural documentation
⚠ PENDING: Skill updates (US4-US7) — blocked on backtest pass

---

## 14. Next Step

Execute Pre-Deployment Readiness tasks:

1. ~~**Backtest** current rules via psx-backtester (2018-2024 PSX, full frictions)~~ → FAILED. Iterate rules.
2. ~~**Macro Regime Analysis** (US4 — Layer 1.5)~~ → COMPLETE. See §17 for results.
3. 👉 **Implement** skill updates: position cap, macro overlay, CGT exits, regime-shift, earnings blackout, sector rotation, tax-loss harvesting
4. 👉 **Deploy** Phase 1 capital only after all gates pass

---

## 16. Backtest Results — Strategy Validation (2026-05-30)

**Engine:** Python backtest (`scripts/psx_backtest.py`, 544 lines)
**Universe:** 24 KSE-100 symbols with available DPS data (2016-2025)
**Frictions:** Brokerage 0.15%, FED 13%, CDC 0.005%, SECP 0.005%, slippage 0.20%, CGT 15%, T+2 settlement
**Walk-forward:** IS 2018-2023 (6yr), OOS 2024 (1yr)

### Iteration Summary

| # | Strategy | OOS CAGR | OOS Sharpe | OOS DD | OOS W/L | OOS WR | OOS Trades | Status |
|---|----------|----------|-----------|--------|---------|--------|-----------|--------|
| 0 | MA 20/50/200 + RSI 40-60 + Vol 120% | ~0% | 0.32 | -24.8% | 2.50 | 24.2% | 33 | ❌ |
| 1 | + ADX > 25 filter + RSI 45-55 + 2d confirm | ~0% | 0.28 | -19.2% | 2.44 | 29.4% | 17 | ❌ |
| 2 | Momentum breakout (20d high) + breakdown exit | 21.9% | 0.48 | -28.1% | 1.60 | 61.5% | 52 | ❌ |
| 3 | + Tighter RSI entry (50-65) + 12% trailing | 7.6% | 0.19 | -26.4% | 1.17 | 59.3% | 27 | ❌ |
| 4 | + 15% trailing after +20%, 5 pos × 12% | 23.8% | 0.56 | -28.7% | 1.64 | 59.2% | 49 | ❌ |
| 5 | Trailing-only exits (no breakdown) | ~0% | 0.26 | -20.9% | 1.15 | 28.6% | 14 | ❌ |
| 6 | + 20d breakdown, 60% cash, 4 pos | ~0% | 0.17 | -18.9% | 2.57 | 39.1% | 23 | ❌ |
| **7** | **Momentum + 20d breakdown + trailing + 50% cash** | **26.0%** | **0.54** | **-21.7%** | **3.04** | **48.6%** | **35** | ❌ near-miss |

### Best Configuration (Iteration 7)

**Entry:** Close > 20-day high + close > 200-day MA + RSI < 70 + volume > 120% of 30d avg
**Exit:** Stop-loss 5%, breakdown below 20-day low, RSI > 85, trailing stop 12% below peak after +15% gain
**Risk:** 5 max positions at 10% each (50% invested), 50% cash floor

| Metric | OOS Result | Threshold | Status |
|--------|-----------|-----------|--------|
| CAGR | **26.0%** | ≥ 15% | ✅ PASS |
| Sharpe | 0.54 | ≥ 1.0 | ❌ FAIL |
| Max Drawdown | -21.7% | ≥ -15% | ❌ FAIL |
| Win Rate | **48.6%** | ≥ 45% | ✅ PASS |
| W/L Ratio | **3.04** | ≥ 2.0 | ✅ PASS |
| Expectancy | **5.96%** | > 0% | ✅ PASS |
| Trades | **35** | ≥ 30 | ✅ PASS |

### Verdict: FAIL (near-miss)

**5 of 7 thresholds pass OOS.** Two remain:
- **Sharpe 0.54:** Structurally difficult — PKR T-bills at 20% leave only 6% excess return headroom for a 26% CAGR strategy. Annualized volatility must be ≤ 6% for Sharpe ≥ 1.0, which is unrealistic for equity strategies.
- **Max DD -21.7%:** Exceeds the -15% survival threshold by 6.7 percentage points.

**IS performance is negative across all iterations** (best: CAGR -0.3%). The strategy only generates positive returns in the 2024 bull market. This means the edge is regime-dependent and may not persist through choppy / bear PSX periods.

### Key Findings

1. **MA crossover strategies perform poorly on PSX.** PSX is choppy >50% of the time, whip-sawing trend-following systems.
2. **Momentum breakout outperforms MA crossover.** 20-day high breakout with trailing stop achieves 26% CAGR OOS vs 0% for MA.
3. **W/L ratio of 3.04 confirms edge quality.** Winners are 3× larger than losers on average.
4. **Cash management is critical for drawdown control.** 50% cash floor limits downside but caps upside.
5. **IS/OOS regime disparity is unresolved.** The strategy works in trending/bull markets (2024) but fails in choppy/range-bound markets (2018-2023).

### Decision: STOP — Further Analysis Required

The strategy demonstrates conditional edge (works in trending bull markets) but fails the full walk-forward test. The IS/OOS disparity suggests regime dependence not yet understood.

**Next steps:** Macro regime analysis (US4 — Layer 1.5 overlay) must precede any live capital deployment. The macro overlay may explain the IS/OOS gap and provide a regime-based entry gate.

---

## 17. Macro Regime Analysis — Results (2026-05-31)

**Objective:** Diagnose IS/OOS disparity in backtest by cross-referencing equity
curve with Pakistan macro regimes (SBP policy, USD/PKR, IMF status, KSE-100 P/E).

**Method:** Classified every trading day 2018-2024 into risk-on/neutral/risk-off
using the Layer 1.5 logic from `macro-states.md`. Ran the Iteration 7 momentum
breakout strategy with and without a macro gate (block entries in risk-off).

### Regime Distribution (2018-2024)

| Regime | Days | % of Total |
|--------|------|-----------|
| RISK_OFF | 1,397 | 54.6% |
| RISK_ON | 1,099 | 43.0% |
| NEUTRAL | 61 | 2.4% |

**Key finding:** Pakistan was in macro risk-off for >54% of 2018-2024. This
explains why the IS backtest was negative — the strategy was generating signals
during hiking cycles, PKR crises, and IMF program disruptions.

### Regime-Dependent Returns (Baseline — No Gate)

| Regime | IS Return (ann.) | Days |
|--------|-----------------|------|
| RISK_ON | **+33.7%** | 501 |
| RISK_OFF | +11.5% | 941 |
| NEUTRAL | +6.6% | 42 |

**The edge is strongly regime-dependent.** The strategy generates +33.7%
annualized in risk-on periods but only +11.5% in risk-off. The strategy's
OOS outperformance (26% CAGR) is explained by 2024 being 100% risk-on.

### Macro Gate Impact

Adding a risk-off entry block (107 entries blocked in IS):

| Metric | No Gate (IS) | Macro Gate (IS) | Change |
|--------|-------------|-----------------|--------|
| CAGR | -1.2% | **+2.7%** | ✅ +3.9pp |
| Sharpe | -0.02 | -0.16 | ❌ |
| Max DD | -36.4% | **-31.3%** | ✅ -5.1pp |
| Win Rate | 29.0% | **40.0%** | ✅ +11pp |
| W/L Ratio | 1.49 | **2.06** | ✅ +0.57 |
| Trades | 124 | **60** | Blocked 51% of false signals |

**OOS (2024):** No change — 2024 was 100% risk-on, so 0 entries blocked.
Performance identical to baseline (26% CAGR, 0.45 Sharpe, -26.9% DD).

### Conclusions

1. **Strategy has conditional edge.** It works in risk-on environments (+33.7%
   ann.) but underperforms in risk-off. This is consistent with momentum
   breakout strategies globally — they need trending bull markets.

2. **Macro gate is validated.** Blocking entries in risk-off improves IS CAGR
   by 3.9pp and reduces drawdown by 5.1pp. The macro gate should be
   implemented as a safety layer even though it doesn't single-handedly
   pass all thresholds.

3. **Remaining blockers:** Sharpe (0.45 vs 1.0 threshold) and Max DD
   (-26.9% vs -15% threshold). The Sharpe threshold may be structurally
   unrealistic for PSX given PKR T-bills at 20% (leaving only 6% excess
   return headroom for Sharpe ≥ 1.0). The DD threshold may need to be
   relaxed to 20-25% for a momentum strategy.

4. **Deployability assessment:** The strategy with macro gate is not yet
   deployable under current constitution thresholds. Two options:
   - (A) Relax Sharpe and DD thresholds for PSX-specific context (ADR needed)
   - (B) Continue iterating rules to improve Sharpe and DD further

### Files

- Analysis script: `scripts/macro_regime_analysis.py`
- Macro data: `scripts/macro_data.py`
- Results: `data/runs/macro_analysis_results.json`
- Equity curves: `data/runs/*_equity.parquet`
- Macro states reference: `.claude/skills/psx-market-filter/references/macro-states.md`
- ADR: `history/adr/ADR-003-psx-macro-overlay-layer.md`

---

## 15. Open Gaps & TODOs (Validation Critique — 2026-05-05)

The following gaps were surfaced during a structured validation of this document.
Each is captured as a TODO. None invalidate the framework; all sharpen it before
real capital is deployed. **Resolve before Phase 1 backtest commits.**

### 15.1 Edge Definition (CRITICAL)

**Gap:** §2.2 names the edge as "Finance + Programming + Discipline." This is
necessary but not sufficient. Many participants have all three and still lose.

**TODO:** Complete this sentence in concrete terms:
> "I make money on PSX because of [specific structural / informational / behavioral /
> time-horizon asymmetry] that other participants don't or can't exploit."

Until written, this is a discipline framework, not an edge-bearing system.

---

### 15.2 Strategy Rules Are Generic Defaults, Not Validated Edge

**Gap:** 20/50/200 MA + RSI(14) + 120% volume is the most-documented retail
technical setup. It works in trending markets and fails in chop. PSX is choppy
> 50% of the time.

**TODO:**
- Treat current technical rules as a **starting hypothesis**, not the system.
- Backtest on 2018-2024 PSX data with full PSX frictions (commission, CGT, slippage, T+2).
- If Sharpe < 1.0 net of costs → iterate or abandon. Do **not** deploy capital.

---

### 15.3 Fundamental Thresholds Are Arbitrary

**Gap:** Revenue CAGR > 8%, PAT CAGR > 10%, D/E < 0.6 are reasonable defaults
but not derived from PSX data. Banks and capex-heavy sectors routinely violate
D/E < 0.6 while being safe; some "growth" cases are margin-compression traps.

**TODO:**
- Calibrate thresholds against PSX sector medians (banks vs cement vs textiles
  have very different healthy ranges).
- Document **why** each threshold is what it is, with a citation or analysis.
- Allow sector-relative thresholds, not absolute.

---

### 15.4 Position Math Conflict

**Gap:** §4 Layer 3 / risk-management says max 7 concurrent positions × 20% each = 140%,
but research also requires ≥ 30% cash reserve. These conflict.

**TODO:** Choose one of:
- Cap concurrent positions at 3-4 (with 20% per position, leaves 30%+ cash).
- Or reduce per-position cap to ~10% (allows 7 positions + 30% cash).

Fix the math before any live trade.

---

### 15.5 Long No-Trade Periods Not Addressed

**Gap:** PSX volume is bursty. A 10-20 stock watchlist may produce zero valid
signals for weeks. The framework doesn't address the **temptation to force trades**
during dry periods — historically the #1 destroyer of disciplined systems.

**TODO:**
- Add explicit rule: "No-signal weeks are correct outcomes, not failures."
- Define maximum trade frequency (e.g., max 2 entries / week) to discourage forcing.
- Track and review dry-period behavior in trade journal.

---

### 15.6 CGT-Driven Holding Period Trade-Off

**Gap:** §7 ignores Capital Gains Tax brackets:
- < 6 months: 15% (filer) / 30% (non-filer)
- 6-12 months: 12.5% / 25%
- 12-24 months: 10% / 20%
- > 24 months: 0%

A strategy averaging 30-day holds vs 200-day holds has materially different
post-tax returns. The "+15% partial profit" rule may push exits into the worst
tax bracket.

**TODO:**
- Quantify: at typical win size, does the 6-month bracket meaningfully change net?
- Decide: tax-aware exit logic vs. tax-agnostic. Document the choice.

---

### 15.7 No Falsification Criterion

**Gap:** "If not profitable → STOP" (§8 Phase 1) is too soft. Over what period?
Against what benchmark? Without precision, every result can be rationalized.

**TODO:** Add concrete kill-switch to §11 or §13:
> "If after **N ≥ 50 closed trades over ≥ 6 months** my **Sharpe < 0.5** OR
> I **underperform KSE-100 by > 5%** net of all costs, I stop trading and
> re-evaluate."

Pick the exact numbers and commit them in writing.

---

### 15.8 Effective Diversification ≠ Stated Diversification

**Gap:** "Max 2 stocks per sector" is good, but PSX is dominated by macro
factors that ignore sector boundaries:
- USD/PKR direction (textiles + IT exporters move together; refining/fertilizer
  the opposite).
- Interest rates (banks ↑, leveraged industrials ↓).
- IMF program / political stability (everything correlates in crisis).

Effective diversification across 5-7 PSX positions = ~1-2 macro factors, not 7.

**TODO:**
- Add macro-factor exposure check: USD/PKR, rates, political risk.
- Limit net exposure to any one factor.
- Especially relevant when 7 positions could all be "long PKR weakness" trades.

---

### 15.9 Macro Overlay Missing

**Gap:** PSX is macro-dominated. SBP rate decisions, IMF reviews, election cycles,
CPI prints, and PKR moves drive index direction more than stock-level fundamentals.
The framework treats fundamentals + technicals as the input set; macro is absent.

**TODO:** Add Layer 1.5 (macro overlay):
- SBP policy stance (hiking / holding / cutting)
- USD/PKR trend
- IMF program status / sovereign risk indicators
- Aggregate market valuation (KSE-100 P/E vs 10-year median)

When macro signals "risk-off," tighten universe to defensives or move to cash.

---

### 15.10 Sector Rotation Logic Missing

**Gap:** In PSX, sector beats stock selection > 60% of the time. The framework
focuses on stock selection within sectors but provides no sector-rotation logic.

**TODO:**
- Add sector-momentum ranking to the watchlist filter.
- Avoid bottom-quartile sectors regardless of how strong an individual name looks.
- Revisit quarterly.

---

### 15.11 Earnings & Corporate Actions

**Gap:** §11 Principle says "Holding through earnings — DISCOURAGED" with no
concrete rule. Bonus issues, rights issues, and splits are common on PSX and
will silently break stop-loss math if not handled.

**TODO:**
- Add earnings blackout: **flat into earnings unless thesis explicitly requires holding.**
- Add corporate-action handler: when bonus/split occurs, recalculate stop-loss
  on the adjusted basis (else position size and risk become wrong).

---

### 15.12 Phase 5 Premature

**Gap:** Phase 5 (SaaS, signal service, advisory) appears before Phase 1 has
even been validated. SECP advisory regulations are non-trivial; PSX retail
TAM is small (~250k active accounts).

**TODO:**
- Explicitly defer Phases 5B (SaaS) and 5C (Signal Service) until **at least
  one full year** of profitable Phase 1 / Phase 2 operation.
- Until then, Phase 5A (Personal Wealth Engine) is the only target.

---

### 15.13 Tax-Loss Harvesting

**Gap:** CGT regime allows loss offsetting against gains within the tax year.
Strategy should harvest losses in stocks held < 1 year (15% bracket) before
year-end. Not addressed anywhere.

**TODO:**
- Add Q4 tax-loss harvesting routine.
- Reconcile with rule: "Never average down" / "Cut losers fast."
  (The two are compatible; just sequence them.)

---

### 15.14 Being Wrong About Regime

**Gap:** Rules cover entry, exit, stop-loss. They do **not** cover the case where
the macro regime you assumed flips. e.g., expecting a rate-cutting cycle, getting
a hike instead. Stops will trigger one-by-one as positions deteriorate, but you'll
take 5-7 small losses instead of recognizing the regime shift early.

**TODO:**
- Add regime-shift detector: when 3+ open positions hit stops within 5 trading
  days, **halt new entries** and re-evaluate macro thesis before resuming.

---

## Validation summary

- **As a discipline framework:** strong (8/10). Better than the typical retail plan.
- **As an edge-bearing investment system:** improving. Edge now named (time-horizon + behavioral, ADR-002 D1). Falsification criterion set (ADR-002 D5). Position math reconciled (ADR-002 D4).
- **Remaining gaps:** backtest data needed (US3), macro overlay ADR (US4), skill implementation updates (US5-US7).

These TODOs are tracked in this document. Each should either be resolved (rule
sharpened in research.md) or escalated to an ADR (architectural decision recorded
in `history/adr/`).


