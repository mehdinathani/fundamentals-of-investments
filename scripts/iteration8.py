#!/usr/bin/env python3
"""
Iteration 8 — Combined Improvements
Tighter exits + stronger entries + regime-aware rules + macro gate.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import date, datetime
from dataclasses import dataclass, field
import json

from macro_data import SBP_RATES, USDPKR, IMF_STATUS, KSE100_PE, classify_regime, get_macro_dataframe
from psx_backtest import (
    load_data, compute_costs,
    Trade, BacktestResult,
    IS_START, IS_END, OOS_START, OOS_END, START_CAPITAL,
    SLIPPAGE_LARGE, SLIPPAGE_MID,
)

# ─── Regime-Aware Config ───────────────────────────────────────────

REGIME_CONFIG = {
    "RISK_ON": {
        "max_positions": 5,
        "position_cap": 0.10,
        "cash_floor": 0.50,
        "risk_per_trade": 0.05,
        "stop_loss": 0.05,
        "trailing_activate": 1.10,
        "trailing_stop": 0.92,
        "allow_tier2": True,
        "volume_min_ratio": 1.2,
    },
    "NEUTRAL": {
        "max_positions": 4,
        "position_cap": 0.08,
        "cash_floor": 0.60,
        "risk_per_trade": 0.03,
        "stop_loss": 0.04,
        "trailing_activate": 1.08,
        "trailing_stop": 0.92,
        "allow_tier2": False,
        "volume_min_ratio": 1.5,
    },
    "RISK_OFF": {
        "max_positions": 3,
        "position_cap": 0.07,
        "cash_floor": 0.70,
        "risk_per_trade": 0.03,
        "stop_loss": 0.04,
        "trailing_activate": 1.08,
        "trailing_stop": 0.92,
        "allow_tier2": False,
        "volume_min_ratio": 1.5,
    },
}

DEFAULT_CONFIG = {
    "max_positions": 5,
    "position_cap": 0.10,
    "cash_floor": 0.50,
    "risk_per_trade": 0.05,
    "stop_loss": 0.05,
    "trailing_activate": 1.10,
    "trailing_stop": 0.92,
    "allow_tier2": True,
    "volume_min_ratio": 1.2,
    "adx_threshold": 25,
    "partial_profit_pct": 0.20,
    "partial_profit_frac": 0.50,
    "cool_off_days": 3,
}

# ─── Enhanced Indicators ───────────────────────────────────────────

def compute_indicators_i8(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["MA20"] = d["CLOSE"].rolling(20).mean()
    d["MA50"] = d["CLOSE"].rolling(50).mean()
    d["MA200"] = d["CLOSE"].rolling(200).mean()

    # RSI(14)
    delta = d["CLOSE"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_g = gain.rolling(14).mean()
    avg_l = loss.rolling(14).mean()
    rs = avg_g / avg_l.replace(0, np.nan)
    d["RSI"] = 100 - (100 / (1 + rs))

    # Volume
    d["VOL_MA"] = d["VOLUME"].rolling(30).mean()
    d["VOL_RATIO"] = d["VOLUME"] / d["VOL_MA"].replace(0, np.nan)

    # Momentum breakouts
    d["HIGH_20D"] = d["HIGH"].rolling(20).max()
    d["LOW_10D"] = d["LOW"].rolling(10).min()
    d["LOW_20D"] = d["LOW"].rolling(20).min()
    d["BREAKOUT"] = d["CLOSE"] > d["HIGH_20D"].shift(1)

    # ADX (Average Directional Index)
    d["TR"] = pd.concat([
        abs(d["HIGH"] - d["LOW"]),
        abs(d["HIGH"] - d["CLOSE"].shift(1)),
        abs(d["LOW"] - d["CLOSE"].shift(1))
    ], axis=1).max(axis=1)
    d["ATR"] = d["TR"].rolling(14).mean()

    d["UP"] = d["HIGH"] - d["HIGH"].shift(1)
    d["DOWN"] = d["LOW"].shift(1) - d["LOW"]
    d["PLUS_DM"] = np.where((d["UP"] > d["DOWN"]) & (d["UP"] > 0), d["UP"], 0)
    d["MINUS_DM"] = np.where((d["DOWN"] > d["UP"]) & (d["DOWN"] > 0), d["DOWN"], 0)

    d["PLUS_DI"] = 100 * d["PLUS_DM"].ewm(span=14, adjust=False).mean() / d["ATR"].replace(0, np.nan)
    d["MINUS_DI"] = 100 * d["MINUS_DM"].ewm(span=14, adjust=False).mean() / d["ATR"].replace(0, np.nan)
    d["DX"] = 100 * abs(d["PLUS_DI"] - d["MINUS_DI"]) / (d["PLUS_DI"] + d["MINUS_DI"]).replace(0, np.nan)
    d["ADX"] = d["DX"].ewm(span=14, adjust=False).mean()

    return d

# ─── Signal Logic ──────────────────────────────────────────────────

def check_buy_signal_i8(row: pd.Series, config: dict, regime: str) -> str | None:
    if pd.isna(row["MA200"]) or pd.isna(row["RSI"]) or pd.isna(row["VOL_RATIO"]):
        return None
    if pd.isna(row.get("BREAKOUT", None)):
        return None

    # 1. Momentum breakout
    if not row["BREAKOUT"]:
        return None

    # 2. Long-term uptrend
    if row["CLOSE"] <= row["MA200"]:
        return None

    # 3. ADX trend strength (NEW)
    adx_val = row.get("ADX", np.nan)
    adx_threshold = config.get("adx_threshold", 25)
    if pd.notna(adx_val) and adx_val < adx_threshold:
        return None

    # 4. RSI filter
    if row["RSI"] >= 70:
        return None

    # 5. Volume confirmation
    vol_min = config.get("volume_min_ratio", 1.2)
    if row["VOL_RATIO"] < vol_min:
        return None

    # Tier classification
    is_strong = row["VOL_RATIO"] >= 1.5 and 50 <= row["RSI"] <= 60
    if is_strong:
        return "Tier 1 (Strong Buy)"

    allow_tier2 = config.get("allow_tier2", True)
    if allow_tier2 and 50 <= row["RSI"] <= 65:
        return "Tier 2 (Moderate Buy)"

    return None

def check_sell_signal_i8(row: pd.Series, entry_price: float, entry_date, current_date,
                          highest_price: float = None, config: dict = None,
                          partial_profit_taken: bool = False) -> str | None:
    if config is None:
        config = DEFAULT_CONFIG

    sl = config.get("stop_loss", 0.05)

    # 1. Hard stop-loss
    if row["CLOSE"] <= entry_price * (1 - sl):
        return "stop_loss"

    # 2. Partial profit exit (NEW)
    if not partial_profit_taken and config.get("partial_profit_pct"):
        pp_pct = config["partial_profit_pct"]
        if row["CLOSE"] >= entry_price * (1 + pp_pct):
            return "partial_profit"

    # 3. Breakdown below 20-day low
    if row["CLOSE"] < row.get("LOW_20D", 0):
        return "breakdown_sell"

    # 4. RSI extreme overbought
    if row.get("RSI", 50) > 85:
        return "rsi_overbought"

    # 5. Trailing stop
    trailing_activate = config.get("trailing_activate", 1.15)
    trailing_stop = config.get("trailing_stop", 0.88)

    if highest_price and highest_price >= entry_price * trailing_activate:
        if row["CLOSE"] <= highest_price * trailing_stop:
            return "trailing_stop"

    return None

# ─── Position Sizing ───────────────────────────────────────────────

def calc_position_size_i8(capital: float, current_price: float, config: dict) -> int:
    pos_cap = config.get("position_cap", 0.10)
    max_notional = capital * pos_cap
    shares = int(max_notional / current_price) if current_price > 0 else 0
    return shares

# ─── Backtest Loop ─────────────────────────────────────────────────

def run_backtest_i8(
    data: dict[str, pd.DataFrame],
    start: date,
    end: date,
    label: str,
    starting_capital: float = START_CAPITAL,
    macro_gate: dict = None,
    config: dict = None,
) -> tuple[BacktestResult, pd.DataFrame, dict]:
    if config is None:
        config = DEFAULT_CONFIG

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
    risk_off_blocked = 0
    cool_off_until = None

    for day in trading_days:
        day_dt = pd.Timestamp(day)

        # Determine regime for this day
        current_regime = "RISK_ON"
        if macro_gate is not None:
            current_regime = macro_gate.get(day, "RISK_ON")

        # Get regime-specific config
        regime_cfg = REGIME_CONFIG.get(current_regime, REGIME_CONFIG["RISK_ON"])
        merged_cfg = {**config, **regime_cfg}

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
            if sym not in data or day_dt not in data[sym]["DATE"].values:
                continue
            row = data[sym].loc[data[sym]["DATE"] == day_dt]
            if row.empty:
                continue
            row = row.iloc[0]
            if pd.isna(row["CLOSE"]) or row["CLOSE"] <= 0:
                continue

            pos = positions[sym]
            pos["highest_price"] = max(pos.get("highest_price", pos["entry_price"]), row["CLOSE"])

            exit_reason = check_sell_signal_i8(
                row, pos["entry_price"], pos["entry_date"], day,
                pos.get("highest_price"), merged_cfg,
                pos.get("partial_profit_taken", False)
            )
            if exit_reason is None:
                continue

            exit_price = row["CLOSE"]
            slippage = SLIPPAGE_MID
            exit_price_adj = exit_price * (1 - slippage)
            shares = pos["shares"]

            if exit_reason == "partial_profit":
                # Sell partial (50%)
                partial_shares = int(shares * config.get("partial_profit_frac", 0.5))
                if partial_shares <= 0:
                    continue
                remaining_shares = shares - partial_shares
                pos["shares"] = remaining_shares
                pos["partial_profit_taken"] = True
                notional_out = exit_price_adj * partial_shares
                cash += notional_out
                t2_queue.append((day + pd.Timedelta(days=2), notional_out))
                # Don't close the position, just reduce
                continue

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

            # Cool-off after stop-loss (NEW)
            if exit_reason in ("stop_loss", "breakdown_sell"):
                cool_off_until = day + pd.Timedelta(days=config.get("cool_off_days", 3))

        # Check entries
        max_pos = merged_cfg.get("max_positions", 5)
        cash_floor = merged_cfg.get("cash_floor", 0.50)

        if len(positions) >= max_pos:
            equity_curve.append((day, cash + pos_value))
            continue
        if cash < starting_capital * cash_floor:
            equity_curve.append((day, cash + pos_value))
            continue

        # Cool-off check
        if cool_off_until and day < cool_off_until:
            equity_curve.append((day, cash + pos_value))
            continue

        for sym in sorted(data.keys()):
            if sym in positions or sym not in data:
                continue
            if day_dt not in data[sym]["DATE"].values:
                continue
            row = data[sym].loc[data[sym]["DATE"] == day_dt]
            if row.empty:
                continue
            row = row.iloc[0]
            if pd.isna(row["CLOSE"]) or row["CLOSE"] <= 0:
                continue

            signal = check_buy_signal_i8(row, merged_cfg, current_regime)
            if signal is None:
                continue

            # Macro gate: block entry in RISK_OFF
            if current_regime == "RISK_OFF":
                risk_off_blocked += 1
                continue

            shares = calc_position_size_i8(cash, row["CLOSE"], merged_cfg)
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
                "partial_profit_taken": False,
            }

        total = cash + sum(
            data[sym].loc[data[sym]["DATE"] == day_dt, "CLOSE"].values[0] * pos["shares"]
            for sym, pos in positions.items()
            if sym in data and day_dt in data[sym]["DATE"].values
        )
        equity_curve.append((day, total))

    # Final close
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

    meta = {
        "risk_off_blocked": risk_off_blocked,
        "regime_shifts": {},
    }
    return result, equity_df, meta

# ─── Run ───────────────────────────────────────────────────────────

def run():
    print("=" * 70)
    print("  ITERATION 8 — Regime-Aware + ADX + Tighter Exits")
    print("=" * 70)

    # Build macro gate
    from macro_regime_analysis import build_regime_timeline
    regime_daily = build_regime_timeline()
    macro_gate = dict(zip(regime_daily["date"].dt.date, regime_daily["regime"]))

    # Load data with enhanced indicators
    print("\n[1/3] Loading data with ADX indicators...")
    data = load_data()
    for sym in data:
        data[sym] = compute_indicators_i8(data[sym])
    print(f"  Loaded {len(data)} symbols")

    # Run IS
    print("\n[2/3] Running IS (2018-2023)...")
    is_result, is_eq, is_meta = run_backtest_i8(
        data, IS_START, IS_END, "IS (2018-2023) - Iteration 8",
        macro_gate=macro_gate
    )

    # Run OOS
    print("\n[3/3] Running OOS (2024)...")
    oos_result, oos_eq, oos_meta = run_backtest_i8(
        data, OOS_START, OOS_END, "OOS (2024) - Iteration 8",
        macro_gate=macro_gate
    )

    def pr(r):
        print(f"\n  {r.label}")
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

    pr(is_result)
    pr(oos_result)

    # Compare with Iteration 7 baseline
    print("\n" + "=" * 70)
    print("  COMPARISON: Iteration 7 vs Iteration 8")
    print("=" * 70)
    print(f"\n  {'Metric':<18s} {'I7 IS':>10s} {'I8 IS':>10s} {'I7 OOS':>10s} {'I8 OOS':>10s}")
    print(f"  {'─'*58}")
    print(f"  {'CAGR':<18s} {'-1.2%':>10s} {is_result.cagr:>9.1%} {'26.0%':>10s} {oos_result.cagr:>9.1%}")
    print(f"  {'Sharpe':<18s} {'-0.02':>10s} {is_result.sharpe_ratio:>9.2f} {'0.45':>10s} {oos_result.sharpe_ratio:>9.2f}")
    print(f"  {'Max DD':<18s} {'-36.4%':>10s} {is_result.max_drawdown_pct:>8.1f}% {'-26.9%':>9s} {oos_result.max_drawdown_pct:>8.1f}%")
    print(f"  {'Win Rate':<18s} {'29.0%':>10s} {is_result.win_rate:>9.1%} {'48.6%':>10s} {oos_result.win_rate:>9.1%}")
    print(f"  {'W/L Ratio':<18s} {'1.49':>10s} {is_result.win_loss_ratio:>9.2f} {'3.04':>10s} {oos_result.win_loss_ratio:>9.2f}")
    print(f"  {'Trades':<18s} {'124':>10s} {is_result.total_trades:>9d} {'35':>10s} {oos_result.total_trades:>9d}")

    # Save
    output = {
        "iteration": 8,
        "description": "Regime-aware configs + ADX > 25 + volume > 150% + tighter trailing (8%/10%) + partial profit + cool-off",
        "is": {
            "cagr": is_result.cagr, "sharpe": is_result.sharpe_ratio,
            "max_dd": is_result.max_drawdown_pct, "win_rate": is_result.win_rate,
            "wl_ratio": is_result.win_loss_ratio, "trades": is_result.total_trades,
            "verdict": is_result.verdict,
        },
        "oos": {
            "cagr": oos_result.cagr, "sharpe": oos_result.sharpe_ratio,
            "max_dd": oos_result.max_drawdown_pct, "win_rate": oos_result.win_rate,
            "wl_ratio": oos_result.win_loss_ratio, "trades": oos_result.total_trades,
            "verdict": oos_result.verdict,
        },
        "risk_off_blocked_is": is_meta["risk_off_blocked"],
        "risk_off_blocked_oos": oos_meta["risk_off_blocked"],
    }
    out_path = Path("data/runs/iteration8_results.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\n  Results saved to {out_path}")

if __name__ == "__main__":
    run()
