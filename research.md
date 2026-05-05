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

* Finance + Programming combination
* Structured rules
* Discipline and consistency

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
* Position sizing discipline
* No emotional averaging
* Strict stop-loss

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

#### Option A: Personal Wealth Engine (Recommended)

* Private system
* Focus on capital growth

#### Option B: SaaS Tool

* Subscription insights

#### Option C: Signal Service

* Requires regulatory awareness

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

---

## 11. Key Principles

1. Strategy > Tools
2. Discipline > Intelligence
3. Risk Control > Profit
4. Consistency > Excitement
5. Data-driven decisions only

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

---

## 14. Next Step

Design:

👉 **Exact PSX Strategy Rules**

* Fundamental filters (ratios + thresholds)
* Technical triggers (entry/exit)
* Risk model (position sizing, stop-loss)
* First working implementation (Excel/Python)

---

**Status: READY FOR STRATEGY DESIGN PHASE**

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
- **As an edge-bearing investment system:** unproven (5/10) — edge is not yet named,
  rules are generic, falsification criterion is missing.
- **Recommendation:** resolve 15.1 (edge), 15.2 (backtest the rules), 15.4 (position
  math), and 15.7 (falsification) **before** any live capital.

These TODOs are tracked in this document. Each should either be resolved (rule
sharpened in research.md) or escalated to an ADR (architectural decision recorded
in `history/adr/`).


