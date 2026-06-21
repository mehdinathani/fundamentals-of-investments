#!/usr/bin/env python3
"""
PSX Backtest Engine
Validates MA/RSI/Volume strategy on KSE-100 universe with full PSX frictions.
Walk-forward: IS 2018-2023, OOS 2024.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from dataclasses import dataclass, field
from datetime import date, datetime
import json

# ─── Config ────────────────────────────────────────────────────────────

START_CAPITAL = 1_000_000  # PKR 1M
RISK_PER_TRADE = 0.05      # 5% max loss per trade
MAX_POSITIONS = 5
POSITION_CAP = 0.10        # 10% per position (5 × 10% = 50% invested, 50% cash)
CASH_FLOOR = 0.50          # 50% minimum cash

# Frictions (from psx-frictions.md)
BROKERAGE = 0.0015         # 0.15% per side
FED_ON_BROKERAGE = 0.13    # 13% on brokerage
CDC = 0.00005              # 0.005% per side
SECP = 0.00005             # 0.005% per side
SLIPPAGE_LARGE = 0.0010    # 0.10% per side (KSE-30)
SLIPPAGE_MID = 0.0020      # 0.20% per side (KSE-100 outside KSE-30)
CGT_RATE = 0.15            # 15% filer <6mo

# Signal params (from trade-rules-engine)
MA_FAST = 20
MA_SLOW = 50
MA_TREND = 200
RSI_PERIOD = 14
VOLUME_LOOKBACK = 30
VOLUME_MIN_RATIO = 1.2     # 120% of avg
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
STOP_LOSS = 0.05           # 5%
MOMENTUM_LOOKBACK = 20     # 20-day high breakout
EXIT_LOW_LOOKBACK = 10     # 10-day low breakdown
RSI_ENTRY_MIN = 50         # tighter entry zone (Iteration 3)
RSI_ENTRY_MAX = 65         # tighter entry zone (Iteration 3)
TRAILING_STOP_ACTIVATE = 1.15  # trailing stop only after +15% gain
TRAILING_STOP_PCT = 0.88       # exit when close drops 12% below peak

# Walk-forward
IS_START = date(2018, 1, 1)
IS_END = date(2023, 12, 31)
OOS_START = date(2024, 1, 1)
OOS_END = date(2024, 12, 31)

DATA_DIR = Path("data/historical")

# ─── Data Structures ───────────────────────────────────────────────────

@dataclass
class Trade:
    symbol: str
    entry_date: date
    entry_price: float
    exit_date: date | None = None
    exit_price: float | None = None
    shares: int = 0
    entry_signal: str = ""
    exit_reason: str | None = None
    pnl_gross: float = 0.0
    pnl_net: float = 0.0

@dataclass
class BacktestResult:
    label: str
    start_date: date
    end_date: date
    starting_capital: float
    ending_capital: float
    cagr: float
    max_drawdown_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    win_rate: float
    avg_win_pct: float
    avg_loss_pct: float
    win_loss_ratio: float
    expectancy_pct: float
    total_trades: int
    trades: list = field(default_factory=list)
    verdict: str = ""
    failed_thresholds: list = field(default_factory=list)

# ─── Indicators ────────────────────────────────────────────────────────

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["MA20"] = d["CLOSE"].rolling(MA_FAST).mean()
    d["MA50"] = d["CLOSE"].rolling(MA_SLOW).mean()
    d["MA200"] = d["CLOSE"].rolling(MA_TREND).mean()

    delta = d["CLOSE"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_gain = gain.rolling(RSI_PERIOD).mean()
    avg_loss = loss.rolling(RSI_PERIOD).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    d["RSI"] = 100 - (100 / (1 + rs))

    d["VOL_MA"] = d["VOLUME"].rolling(VOLUME_LOOKBACK).mean()
    d["VOL_RATIO"] = d["VOLUME"] / d["VOL_MA"].replace(0, np.nan)
    # Momentum breakout indicators
    d["HIGH_20D"] = d["HIGH"].rolling(MOMENTUM_LOOKBACK).max()
    d["LOW_10D"] = d["LOW"].rolling(EXIT_LOW_LOOKBACK).min()
    d["LOW_20D"] = d["LOW"].rolling(20).min()
    d["BREAKOUT"] = d["CLOSE"] > d["HIGH_20D"].shift(1)

    d["MA_BELOW_50"] = d["MA20"] < d["MA50"]
    d["PRICE_BELOW_200"] = d["CLOSE"] < d["MA200"]
    d["PRICE_BELOW_200_3D"] = d["PRICE_BELOW_200"].rolling(3).min() >= 1
    return d

def compute_rsi_series(close):
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_g = gain.rolling(RSI_PERIOD).mean()
    avg_l = loss.rolling(RSI_PERIOD).mean()
    rs = avg_g / avg_l.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

# ─── Costs ─────────────────────────────────────────────────────────────

def compute_costs(entry_price: float, exit_price: float, shares: int, liquidity_tier: str = "mid") -> float:
    notional_in = entry_price * shares
    notional_out = exit_price * shares
    gross = notional_out - notional_in

    slip = SLIPPAGE_LARGE if liquidity_tier == "large" else SLIPPAGE_MID
    cost_brokerage = (notional_in + notional_out) * BROKERAGE
    cost_fed = cost_brokerage * FED_ON_BROKERAGE
    cost_cdc = (notional_in + notional_out) * CDC
    cost_secp = (notional_in + notional_out) * SECP
    cost_slippage = (notional_in + notional_out) * slip

    pre_tax = gross - (cost_brokerage + cost_fed + cost_cdc + cost_secp + cost_slippage)
    cgt = max(0, pre_tax) * CGT_RATE
    return pre_tax - cgt

# ─── Signal Logic ──────────────────────────────────────────────────────

def check_buy_signal(row: pd.Series) -> str | None:
    if pd.isna(row["MA200"]) or pd.isna(row["RSI"]) or pd.isna(row["VOL_RATIO"]):
        return None
    if pd.isna(row.get("BREAKOUT", None)):
        return None

    # Momentum breakout (Iteration 2)
    # 1. Price breaks above 20-day high
    if not row["BREAKOUT"]:
        return None

    # 2. Long-term uptrend context
    if row["CLOSE"] <= row["MA200"]:
        return None

    # 3. RSI not overbought
    if row["RSI"] >= RSI_OVERBOUGHT:
        return None

    # 4. Volume confirmation
    if row["VOL_RATIO"] < VOLUME_MIN_RATIO:
        return None

    if row["VOL_RATIO"] >= 1.5 and 50 <= row["RSI"] <= 65:
        return "Tier 1 (Strong Buy)"
    else:
        return "Tier 2 (Moderate Buy)"

def check_sell_signal(row: pd.Series, entry_price: float, entry_date, current_date, highest_price: float = None) -> str | None:
    # 1. Stop-loss (hard)
    if row["CLOSE"] <= entry_price * (1 - STOP_LOSS):
        return "stop_loss"

    # 2. Breakdown below 20-day low (momentum failed, wider lookback for fewer false exits)
    if row["CLOSE"] < row.get("LOW_20D", 0):
        return "breakdown_sell"

    # 3. RSI extreme overbought
    rsi_val = row.get("RSI", 50)
    if rsi_val > 85:
        return "rsi_overbought"

    # 4. Trailing stop: exit if close drops below threshold
    if highest_price and highest_price >= entry_price * TRAILING_STOP_ACTIVATE:
        if row["CLOSE"] <= highest_price * TRAILING_STOP_PCT:
            return "trailing_stop"

    return None

# ─── Position Sizing ──────────────────────────────────────────────────

def calc_position_size(capital: float, current_price: float) -> int:
    max_notional = capital * POSITION_CAP
    shares = int(max_notional / current_price)
    return shares

# ─── Backtest Loop ─────────────────────────────────────────────────────

def run_backtest(
    data: dict[str, pd.DataFrame],
    start: date,
    end: date,
    label: str,
    starting_capital: float = START_CAPITAL,
) -> BacktestResult:
    trading_days = sorted({
        d for df in data.values()
        for d in df["DATE"].dt.date
        if start <= d <= end
    })

    cash = starting_capital
    positions: dict[str, dict] = {}
    trades: list[Trade] = []
    equity_curve: list[tuple[date, float]] = []
    t2_queue: list[tuple[date, float]] = []  # (release_date, cash_amount)

    for day in trading_days:
        day_dt = pd.Timestamp(day)

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
            slippage = SLIPPAGE_MID  # default
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
            continue
        if cash < starting_capital * CASH_FLOOR:
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

    # Final accounting: cash + T2 pending + open positions
    t2_pending = sum(amt for _, amt in t2_queue)

    # Close any open positions at last day
    for sym, pos in list(positions.items()):
        if sym not in data:
            continue
        # Get last available price before/on end date
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
        cash += notional_out  # No T+2 on final close
        trades.append(trade)

    # Compute metrics
    ending_capital = cash + t2_pending
    if pd.isna(ending_capital):
        ending_capital = starting_capital
    years = (end - start).days / 365.25
    cagr = (ending_capital / starting_capital) ** (1 / years) - 1 if years > 0 else 0

    equity_df = pd.DataFrame(equity_curve, columns=["date", "value"])
    if len(equity_df) > 1:
        equity_df["return"] = equity_df["value"].pct_change(fill_method=None)
        daily_returns = equity_df["return"].dropna()
        risk_free_rate = 0.20  # PKR T-bill ~20%
        rf_daily = risk_free_rate / 252

        sharpe = (daily_returns.mean() * 252 - risk_free_rate) / (daily_returns.std() * np.sqrt(252)) if daily_returns.std() > 0 else 0

        downside = daily_returns[daily_returns < 0]
        downside_std = np.sqrt((downside ** 2).mean() * 252) if len(downside) > 0 else 1
        sortino = (daily_returns.mean() * 252 - risk_free_rate) / downside_std if downside_std > 0 else 0

        rolling_max = equity_df["value"].cummax()
        drawdown = (equity_df["value"] - rolling_max) / rolling_max
        max_dd = drawdown.min() * 100
    else:
        sharpe = 0
        sortino = 0
        max_dd = 0

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
        win_rate = 0
        avg_win_pct = 0
        avg_loss_pct = 0
        wl_ratio = 0
        expectancy = 0

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

    # Verdict
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
    return result

# ─── Main ──────────────────────────────────────────────────────────────

def load_data(symbols: list[str] = None) -> dict[str, pd.DataFrame]:
    data = {}
    parquet_files = sorted(DATA_DIR.glob("*.parquet"))
    if symbols:
        parquet_files = [p for p in parquet_files if p.stem in symbols]

    for path in parquet_files:
        df = pd.read_parquet(path)
        df["DATE"] = pd.to_datetime(df["DATE"])
        df = df.sort_values("DATE").reset_index(drop=True)
        for col in ["OPEN", "HIGH", "LOW", "CLOSE"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df["VOLUME"] = pd.to_numeric(df["VOLUME"], errors="coerce")
        df = compute_indicators(df)
        data[path.stem] = df
    return data

def print_result(r: BacktestResult):
    print(f"\n{'='*60}")
    print(f"  {r.label}")
    print(f"{'='*60}")
    print(f"  Period:         {r.start_date} to {r.end_date}")
    print(f"  Starting cap:   PKR {r.starting_capital:,.0f}")
    print(f"  Ending cap:     PKR {r.ending_capital:,.0f}")
    print(f"  CAGR:           {r.cagr:.1%}")
    print(f"  Sharpe:         {r.sharpe_ratio:.2f}")
    print(f"  Sortino:        {r.sortino_ratio:.2f}")
    print(f"  Max DD:         {r.max_drawdown_pct:.1f}%")
    print(f"  Win rate:       {r.win_rate:.1%}")
    print(f"  Avg win:        {r.avg_win_pct:.1f}%")
    print(f"  Avg loss:       {r.avg_loss_pct:.1f}%")
    print(f"  W/L ratio:      {r.win_loss_ratio:.2f}")
    print(f"  Expectancy:     {r.expectancy_pct:.2f}%")
    print(f"  Total trades:   {r.total_trades}")
    print(f"  Verdict:        {r.verdict}")
    if r.failed_thresholds:
        print(f"  Failed checks:")
        for f in r.failed_thresholds:
            print(f"    ✗ {f}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    print("Loading data...")
    data = load_data()
    print(f"Loaded {len(data)} symbols")

    print(f"\nRunning IS backtest ({IS_START} to {IS_END})...")
    is_result = run_backtest(data, IS_START, IS_END, "IN-SAMPLE (2018-2023)")
    print_result(is_result)

    print(f"\nRunning OOS backtest ({OOS_START} to {OOS_END})...")
    oos_result = run_backtest(data, OOS_START, OOS_END, "OUT-OF-SAMPLE (2024)")
    print_result(oos_result)

    print(f"\nFinal Assessment:")
    if is_result.verdict == "PASS" and oos_result.verdict == "PASS":
        if oos_result.sharpe_ratio >= is_result.sharpe_ratio * 0.5:
            print("  ✅ STRATEGY PASSES — All thresholds met. Proceed to Phase 1.")
        else:
            print("  ⚠️  OOS Sharpe degrades >50% from IS — possible curve-fit. FAIL.")
    else:
        print(f"  ❌ STRATEGY FAILS — Do NOT deploy capital.")
        print(f"     IS: {is_result.verdict}")
        print(f"     OOS: {oos_result.verdict}")
