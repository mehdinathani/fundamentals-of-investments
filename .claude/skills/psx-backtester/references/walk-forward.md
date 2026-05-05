# Walk-Forward Validation

Single-period backtests are dangerous: parameters can be tuned (consciously or not) to fit the test window. Walk-forward separates strategy DEFINITION from strategy EVALUATION.

## Two-window split (minimum)

```
Total history (e.g., 2018-01 to 2026-04):
├── In-sample (IS):  2018-01 to 2023-12  (70%)
└── Out-of-sample:   2024-01 to 2026-04  (30%)
```

Rules:
1. Define rules and thresholds using ONLY IS data.
2. Lock the rules. Document them (ADR).
3. Run on OOS without ANY parameter changes.
4. Verdict is on OOS, not IS.

## Multi-window walk-forward (preferred)

Better than a single split: roll forward in time.

```
Window 1: train 2018-2020 → test 2021
Window 2: train 2019-2021 → test 2022
Window 3: train 2020-2022 → test 2023
Window 4: train 2021-2023 → test 2024
Window 5: train 2022-2024 → test 2025
Window 6: train 2023-2025 → test 2026
```

Aggregate the test-window results. Strategy passes if performance is consistent across windows (Sharpe stable, drawdown bounded).

## Curve-fit detection

| Symptom | Diagnosis |
|---------|-----------|
| IS Sharpe 2.0, OOS Sharpe 0.4 | Severe overfit — REJECT |
| OOS performance varies wildly across windows | Strategy not robust — REJECT |
| Strategy has > 5 free parameters | Overspecified — simplify |
| Performance depends on a single trade | Lucky outlier — REJECT |
| Strategy "works" only with hindsight feature | Look-ahead leak — fix data pipeline |

## Look-ahead bias prevention

Common leaks:
- Using close price for a signal AND entering at the same close (you don't know close until after market).
- Using fundamental data dated for quarter Q to make decisions during quarter Q (financials are filed mid-Q+1).
- Using "current" PSX listing/symbol — survivorship bias.
- Using delisted-stock-removed price series — survivorship bias.

Rule: at any backtest day `t`, only data with `published_at <= t` is allowed.

## Statistical significance

Trade count matters:
- < 30 trades: not statistically meaningful (likely luck)
- 30-100 trades: borderline; require strong effect size
- > 100 trades: enough to trust win-rate / expectancy

If your strategy generates < 30 OOS trades, extend the OOS window or relax entry criteria — but DO NOT optimize on OOS.
