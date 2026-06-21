#!/usr/bin/env python3
"""
Macro Regime Analysis — Cross-reference backtest equity curve with regimes.
Classifies 2018-2024 into risk-on/neutral/risk-off, then determines if
the strategy is regime-dependent. If so, adds a macro gate and re-runs.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import date, datetime
import json

from macro_data import SBP_RATES, USDPKR, IMF_STATUS, KSE100_PE, classify_regime, get_macro_dataframe

# ─── 1. Build full macro regime timeline ───────────────────────────

def build_regime_timeline() -> pd.DataFrame:
    """Build a daily DataFrame mapping every day to its macro state."""
    macro_df = get_macro_dataframe()
    macro_df["regime"] = macro_df.apply(classify_regime, axis=1)

    # Create daily timeline
    start = date(2018, 1, 1)
    end = date(2024, 12, 31)
    all_days = pd.date_range(start, end, freq="D")
    daily = pd.DataFrame({"date": all_days})
    daily["year_month"] = daily["date"].dt.to_period("M")

    macro_df["year_month"] = macro_df["date"].dt.to_period("M")
    daily = daily.merge(macro_df[["year_month", "regime", "sbp_rate", "usdpkr", "imf_status", "kse100_pe"]],
                        on="year_month", how="left")
    return daily

# ─── 2. Run backtest and capture equity curve ──────────────────────

sys.path.insert(0, str(Path(__file__).resolve().parent))
from psx_backtest import (
    run_backtest, load_data, print_result,
    IS_START, IS_END, OOS_START, OOS_END, START_CAPITAL,
    BacktestResult, Trade,
)

def run_with_equity_curve(data, start, end, label, starting_capital=START_CAPITAL):
    """Run backtest and return (result, equity_df)."""
    from psx_backtest import run_backtest as bt_run
    # Monkey-patch to capture equity curve
    _original = bt_run

    # We need a modified version that returns equity curve
    # Let's re-implement inline to capture it
    return run_backtest_capture(data, start, end, label, starting_capital)

def run_backtest_capture(data, start, end, label, starting_capital=START_CAPITAL, macro_gate=None):
    """
    Run backtest with optional macro gate.
    macro_gate: dict of {date: "RISK_ON"|"NEUTRAL"|"RISK_OFF"} for daily state
    """
    from psx_backtest import (
        compute_indicators, compute_costs,
        check_buy_signal, check_sell_signal, calc_position_size,
        START_CAPITAL as SC, RISK_PER_TRADE, MAX_POSITIONS, POSITION_CAP, CASH_FLOOR,
        BROKERAGE, FED_ON_BROKERAGE, CDC, SECP, SLIPPAGE_LARGE, SLIPPAGE_MID,
        CGT_RATE, STOP_LOSS, BacktestResult, Trade,
    )

    trading_days = sorted({
        d for df in data.values()
        for d in df["DATE"].dt.date
        if start <= d <= end
    })

    cash = starting_capital
    positions = {}
    trades = []
    equity_curve = []
    t2_queue = []
    missed_signals = 0
    risk_off_blocked = 0

    for day in trading_days:
        day_dt = pd.Timestamp(day)

        # Check macro gate
        current_regime = None
        if macro_gate is not None:
            current_regime = macro_gate.get(day, None)
            if current_regime == "RISK_OFF":
                # Risk-off: only allow trades in defensives (hardcoded list)
                # For Iteration 7 we just block new entries entirely in risk-off
                pass  # We handle entry filtering below

        # Release T+2 settled cash
        released = [amt for rd, amt in t2_queue if rd <= day]
        cash += sum(released) if released else 0
        t2_queue = [(rd, amt) for rd, amt in t2_queue if rd > day]

        # Mark to market
        pos_value = 0
        for sym in list(positions.keys()):
            if sym in data and day_dt in data[sym]["DATE"].values:
                row = data[sym].loc[data[sym]["DATE"] == day_dt].iloc[0]
                positions[sym]["current_price"] = row["CLOSE"]
                pos_value += row["CLOSE"] * positions[sym]["shares"]

        # Check exits
        for sym in list(positions.keys()):
            if sym not in data:
                continue
            if day_dt not in data[sym]["DATE"].values:
                continue
            row = data[sym].loc[data[sym]["DATE"] == day_dt]
            if row.empty:
                continue
            row = row.iloc[0]
            pos = positions[sym]
            pos["highest_price"] = max(pos.get("highest_price", pos["entry_price"]), row["CLOSE"])
            exit_reason = check_sell_signal(row, pos["entry_price"], pos["entry_date"], day, pos.get("highest_price"))
            if exit_reason is None:
                continue
            if pd.isna(row["CLOSE"]) or row["CLOSE"] <= 0:
                continue

            exit_price = row["CLOSE"]
            slippage = SLIPPAGE_MID
            exit_price_adj = exit_price * (1 - slippage)
            shares = pos["shares"]

            trade = Trade(
                symbol=sym,
                entry_date=pos["entry_date"],
                entry_price=pos["entry_price"],
                exit_date=day,
                exit_price=exit_price_adj,
                shares=shares,
                entry_signal=pos["entry_signal"],
                exit_reason=exit_reason,
            )
            notional_in = pos["entry_price"] * shares
            notional_out = exit_price_adj * shares
            if pd.isna(notional_out) or notional_out <= 0:
                continue
            trade.pnl_gross = notional_out - notional_in
            trade.pnl_net = compute_costs(pos["entry_price"], exit_price_adj, shares)
            t2_queue.append((day + pd.Timedelta(days=2), notional_out))
            trades.append(trade)
            del positions[sym]

        # Check entries
        if len(positions) >= MAX_POSITIONS:
            equity_curve.append((day, cash + pos_value))
            continue
        if cash < starting_capital * CASH_FLOOR:
            equity_curve.append((day, cash + pos_value))
            continue

        for sym in sorted(data.keys()):
            if sym in positions:
                continue
            if sym not in data:
                continue
            if day_dt not in data[sym]["DATE"].values:
                continue
            row = data[sym].loc[data[sym]["DATE"] == day_dt]
            if row.empty:
                continue
            row = row.iloc[0]
            if pd.isna(row["CLOSE"]) or row["CLOSE"] <= 0:
                continue

            signal = check_buy_signal(row)
            if signal is None:
                continue

            # Macro gate: block entry in risk-off
            if macro_gate is not None and current_regime == "RISK_OFF":
                risk_off_blocked += 1
                continue

            shares = calc_position_size(cash, row["CLOSE"])
            if shares <= 0:
                continue

            slippage = SLIPPAGE_MID
            entry_price = row["CLOSE"] * (1 + slippage)
            notional_out = entry_price * shares
            if pd.isna(notional_out) or notional_out <= 0:
                continue
            if notional_out > cash:
                shares = int(cash / entry_price) if entry_price > 0 else 0
                if shares <= 0:
                    continue
                notional_out = entry_price * shares
            cash -= notional_out
            positions[sym] = {
                "shares": shares,
                "entry_price": entry_price,
                "entry_date": day,
                "entry_signal": signal,
                "current_price": entry_price,
                "highest_price": entry_price,
            }

        total = cash + sum(
            data[sym].loc[data[sym]["DATE"] == day_dt, "CLOSE"].values[0] * pos["shares"]
            for sym, pos in positions.items()
            if sym in data and day_dt in data[sym]["DATE"].values
        )
        equity_curve.append((day, total))

    # Final accounting
    t2_pending = sum(amt for _, amt in t2_queue)
    for sym, pos in list(positions.items()):
        if sym not in data:
            continue
        sym_data = data[sym]
        last_row = sym_data[sym_data["DATE"].dt.date <= end]
        if last_row.empty:
            continue
        last = last_row.iloc[-1]
        exit_price = last["CLOSE"] * (1 - SLIPPAGE_MID)
        trade = Trade(
            symbol=sym,
            entry_date=pos["entry_date"],
            entry_price=pos["entry_price"],
            exit_date=last["DATE"].date(),
            exit_price=exit_price,
            shares=pos["shares"],
            entry_signal=pos["entry_signal"],
            exit_reason="end_of_period",
        )
        notional_in = pos["entry_price"] * pos["shares"]
        notional_out = exit_price * pos["shares"]
        trade.pnl_gross = notional_out - notional_in
        trade.pnl_net = compute_costs(pos["entry_price"], exit_price, pos["shares"])
        cash += notional_out
        trades.append(trade)

    ending_capital = cash + t2_pending
    if pd.isna(ending_capital):
        ending_capital = starting_capital
    years = (end - start).days / 365.25
    cagr = (ending_capital / starting_capital) ** (1 / years) - 1 if years > 0 else 0

    equity_df = pd.DataFrame(equity_curve, columns=["date", "value"])
    if len(equity_df) > 1:
        equity_df["return"] = equity_df["value"].pct_change(fill_method=None)
        daily_returns = equity_df["return"].dropna()
        risk_free_rate = 0.20
        rf_daily = risk_free_rate / 252
        sharpe = (daily_returns.mean() * 252 - risk_free_rate) / (daily_returns.std() * np.sqrt(252)) if daily_returns.std() > 0 else 0
        downside = daily_returns[daily_returns < 0]
        downside_std = np.sqrt((downside ** 2).mean() * 252) if len(downside) > 0 else 1
        sortino = (daily_returns.mean() * 252 - risk_free_rate) / downside_std if downside_std > 0 else 0
        rolling_max = equity_df["value"].cummax()
        drawdown = (equity_df["value"] - rolling_max) / rolling_max
        max_dd = drawdown.min() * 100
    else:
        sharpe = 0; sortino = 0; max_dd = 0

    closed_trades = [t for t in trades if t.exit_reason != "end_of_period"]
    if closed_trades:
        winners = [t for t in closed_trades if t.pnl_net > 0]
        losers = [t for t in closed_trades if t.pnl_net <= 0]
        win_rate = len(winners) / len(closed_trades)
        avg_win_pct = np.mean([t.pnl_net / (t.entry_price * t.shares) * 100 for t in winners]) if winners else 0
        avg_loss_pct = np.mean([t.pnl_net / (t.entry_price * t.shares) * 100 for t in losers]) if losers else 0
        wl_ratio = abs(avg_win_pct / avg_loss_pct) if avg_loss_pct != 0 else float('inf')
        expectancy = (win_rate * avg_win_pct / 100) - ((1 - win_rate) * abs(avg_loss_pct) / 100)
    else:
        win_rate = 0; avg_win_pct = 0; avg_loss_pct = 0; wl_ratio = 0; expectancy = 0

    result = BacktestResult(
        label=label,
        start_date=start,
        end_date=end,
        starting_capital=starting_capital,
        ending_capital=ending_capital,
        cagr=cagr,
        max_drawdown_pct=max_dd,
        sharpe_ratio=sharpe,
        sortino_ratio=sortino,
        win_rate=win_rate,
        avg_win_pct=avg_win_pct,
        avg_loss_pct=avg_loss_pct,
        win_loss_ratio=wl_ratio,
        expectancy_pct=expectancy * 100,
        total_trades=len(closed_trades),
        trades=closed_trades,
    )
    failed = []
    if result.cagr < 0.15:
        failed.append(f"CAGR {result.cagr:.1%} < 15%")
    if result.sharpe_ratio < 1.0:
        failed.append(f"Sharpe {result.sharpe_ratio:.2f} < 1.0")
    if result.max_drawdown_pct < -15:
        failed.append(f"Max DD {result.max_drawdown_pct:.1f}% < -15%")
    if result.win_rate < 0.45:
        failed.append(f"Win rate {result.win_rate:.1%} < 45%")
    if result.win_loss_ratio < 2.0:
        failed.append(f"W/L ratio {result.win_loss_ratio:.2f} < 2.0")
    if result.expectancy_pct <= 0:
        failed.append(f"Expectancy {result.expectancy_pct:.2f}% <= 0")
    if result.total_trades < 30:
        failed.append(f"Trades {result.total_trades} < 30")
    result.verdict = "PASS" if len(failed) == 0 else "FAIL"
    result.failed_thresholds = failed

    return result, equity_df, {"missed_signals": missed_signals, "risk_off_blocked": risk_off_blocked}

# ─── 3. Run analysis ───────────────────────────────────────────────

def run_analysis():
    print("=" * 70)
    print("  MACRO REGIME ANALYSIS — Layer 1.5 Overlay")
    print("=" * 70)

    # Step 1: Build regime timeline
    print("\n[1/5] Building regime timeline...")
    regime_daily = build_regime_timeline()
    regime_summary = regime_daily.groupby("regime").size()
    print(f"  Regime distribution (2018-2024):")
    for regime, count in regime_summary.items():
        pct = count / len(regime_daily) * 100
        print(f"    {regime:12s}: {count:5d} days ({pct:5.1f}%)")

    # Step 2: Load data
    print("\n[2/5] Loading market data...")
    from psx_backtest import load_data
    data = load_data()
    print(f"  Loaded {len(data)} symbols")

    # Step 3: Run baseline (no macro gate)
    print("\n[3/5] Running baseline backtest (no macro gate)...")
    is_result, is_equity, is_meta = run_backtest_capture(
        data, IS_START, IS_END, "IS (2018-2023) - No Macro Gate"
    )
    oos_result, oos_equity, oos_meta = run_backtest_capture(
        data, OOS_START, OOS_END, "OOS (2024) - No Macro Gate"
    )

    def print_result(r):
        print(f"  {r.label}")
        print(f"    CAGR:       {r.cagr:.1%}")
        print(f"    Sharpe:     {r.sharpe_ratio:.2f}")
        print(f"    Sortino:    {r.sortino_ratio:.2f}")
        print(f"    Max DD:     {r.max_drawdown_pct:.1f}%")
        print(f"    Win rate:   {r.win_rate:.1%}")
        print(f"    W/L ratio:  {r.win_loss_ratio:.2f}")
        print(f"    Expectancy: {r.expectancy_pct:.2f}%")
        print(f"    Trades:     {r.total_trades}")
        print(f"    Verdict:    {r.verdict}")
        if r.failed_thresholds:
            for f in r.failed_thresholds:
                print(f"      ✗ {f}")

    print_result(is_result)
    print_result(oos_result)

    # Step 4: Cross-reference equity curve with macro regimes
    print("\n[4/5] Cross-referencing equity curve with macro regimes...")
    is_equity["date"] = pd.to_datetime(is_equity["date"])
    is_equity["year_month"] = is_equity["date"].dt.to_period("M")
    oos_equity["date"] = pd.to_datetime(oos_equity["date"])
    oos_equity["year_month"] = oos_equity["date"].dt.to_period("M")

    is_equity = is_equity.merge(
        regime_daily[["date", "regime"]].rename(columns={"date": "date_r"}),
        left_on="date", right_on="date_r", how="left"
    ).drop(columns=["date_r"])
    oos_equity = oos_equity.merge(
        regime_daily[["date", "regime"]].rename(columns={"date": "date_r"}),
        left_on="date", right_on="date_r", how="left"
    ).drop(columns=["date_r"])

    # Calculate returns by regime
    def regime_performance(equity_df):
        equity_df["return"] = equity_df["value"].pct_change(fill_method=None)
        perf = equity_df.groupby("regime")["return"].agg(["mean", "std", "count"])
        perf.columns = ["avg_daily_return", "daily_vol", "days"]
        perf["annualized_return"] = perf["avg_daily_return"] * 252
        return perf

    is_perf = regime_performance(is_equity)
    oos_perf = regime_performance(oos_equity)

    print("\n  IS Regime Performance:")
    for regime, row in is_perf.iterrows():
        if pd.notna(regime):
            print(f"    {regime:12s}: ann.ret={row['annualized_return']:.1%}, "
                  f"days={int(row['days']):4d}")

    print("\n  OOS Regime Performance:")
    for regime, row in oos_perf.iterrows():
        if pd.notna(regime):
            print(f"    {regime:12s}: ann.ret={row['annualized_return']:.1%}, "
                  f"days={int(row['days']):4d}")

    # Build macro gate dict
    print("\n[5/5] Running backtest WITH macro gate (block entries in RISK_OFF)...")
    macro_gate = dict(zip(regime_daily["date"].dt.date, regime_daily["regime"]))

    is_result_g, is_equity_g, is_meta_g = run_backtest_capture(
        data, IS_START, IS_END, "IS (2018-2023) - With Macro Gate", macro_gate=macro_gate
    )
    oos_result_g, oos_equity_g, oos_meta_g = run_backtest_capture(
        data, OOS_START, OOS_END, "OOS (2024) - With Macro Gate", macro_gate=macro_gate
    )

    print_result(is_result_g)
    print_result(oos_result_g)

    # Compare
    print("\n" + "=" * 70)
    print("  COMPARISON: No Gate vs Macro Gate")
    print("=" * 70)

    def compare(no_gate, with_gate, label):
        print(f"\n  {label}:")
        print(f"    CAGR:       {no_gate.cagr:.1%} → {with_gate.cagr:.1%} "
              f"({'✅' if with_gate.cagr > no_gate.cagr else '❌'})")
        print(f"    Sharpe:     {no_gate.sharpe_ratio:.2f} → {with_gate.sharpe_ratio:.2f} "
              f"({'✅' if with_gate.sharpe_ratio > no_gate.sharpe_ratio else '❌'})")
        print(f"    Max DD:     {no_gate.max_drawdown_pct:.1f}% → {with_gate.max_drawdown_pct:.1f}% "
              f"({'✅' if with_gate.max_drawdown_pct > no_gate.max_drawdown_pct else '❌'})")
        if hasattr(with_gate, 'risk_off_blocked') or 'risk_off_blocked' in str(with_gate):
            pass
        print(f"    Trades:     {no_gate.total_trades} → {with_gate.total_trades}")

    compare(is_result, is_result_g, "IN-SAMPLE (2018-2023)")
    compare(oos_result, oos_result_g, "OUT-OF-SAMPLE (2024)")

    # Final assessment
    print("\n" + "=" * 70)
    print("  FINAL ASSESSMENT")
    print("=" * 70)

    if oos_result_g.verdict == "PASS":
        print("  ✅ STRATEGY PASSES WITH MACRO GATE — Proceed to Phase 1.")
    else:
        print("  ❌ STRATEGY STILL FAILS WITH MACRO GATE.")
        print("     Failed thresholds:")
        for f in oos_result_g.failed_thresholds:
            print(f"       ✗ {f}")

    # Print total blocked entries for reference
    try:
        print(f"\n  Entries blocked by macro gate (risk-off periods):")
        print(f"    IS:  {is_meta_g.get('risk_off_blocked', 'N/A')}")
        print(f"    OOS: {oos_meta_g.get('risk_off_blocked', 'N/A')}")
    except:
        pass

    # Save results
    output = {
        "no_gate": {
            "is": {"cagr": is_result.cagr, "sharpe": is_result.sharpe_ratio,
                   "max_dd": is_result.max_drawdown_pct, "verdict": is_result.verdict},
            "oos": {"cagr": oos_result.cagr, "sharpe": oos_result.sharpe_ratio,
                    "max_dd": oos_result.max_drawdown_pct, "verdict": oos_result.verdict},
        },
        "macro_gate": {
            "is": {"cagr": is_result_g.cagr, "sharpe": is_result_g.sharpe_ratio,
                   "max_dd": is_result_g.max_drawdown_pct, "verdict": is_result_g.verdict},
            "oos": {"cagr": oos_result_g.cagr, "sharpe": oos_result_g.sharpe_ratio,
                    "max_dd": oos_result_g.max_drawdown_pct, "verdict": oos_result_g.verdict},
        },
        "regime_distribution": regime_summary.to_dict(),
    }

    out_path = Path("data/runs/macro_analysis_results.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\n  Results saved to {out_path}")

    # Save equity curves for visualization
    is_equity.to_parquet("data/runs/baseline_is_equity.parquet")
    oos_equity.to_parquet("data/runs/baseline_oos_equity.parquet")
    is_equity_g.to_parquet("data/runs/gated_is_equity.parquet")
    oos_equity_g.to_parquet("data/runs/gated_oos_equity.parquet")
    print("  Equity curves saved to data/runs/")

if __name__ == "__main__":
    run_analysis()
