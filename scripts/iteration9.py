#!/usr/bin/env python3
"""
Iteration 9 — MA Crossover with Macro Gate
Tests whether MA crossover (golden cross / death cross) works when
risk-off periods are filtered out by the macro gate.
Combines: regime-aware configs + ADX > 20 + macro gate + tighter exits.
"""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import date
import json

from psx_backtest import load_data, Trade, BacktestResult
from psx_backtest import IS_START, IS_END, OOS_START, OOS_END, START_CAPITAL
from psx_backtest import SLIPPAGE_LARGE, SLIPPAGE_MID
from macro_data import SBP_RATES, USDPKR, IMF_STATUS, KSE100_PE, classify_regime, get_macro_dataframe
from macro_regime_analysis import build_regime_timeline

# ─── Costs ─────────────────────────────────────────────────────────

BROKERAGE = 0.0015
FED_ON_BROKERAGE = 0.13
CDC = 0.00005
SECP = 0.00005
CGT_RATE = 0.15

def compute_costs(entry_price, exit_price, shares, liquidity_tier="mid"):
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

# ─── Configs ───────────────────────────────────────────────────────

REGIME_CONFIG = {
    "RISK_ON":  {"max_positions":5, "pos_cap":0.10, "cash_floor":0.50, "sl":0.05, "trail_act":1.10, "trail_pct":0.92, "tier2":True, "vol_min":1.2},
    "NEUTRAL":  {"max_positions":4, "pos_cap":0.08, "cash_floor":0.60, "sl":0.04, "trail_act":1.08, "trail_pct":0.92, "tier2":False, "vol_min":1.3},
    "RISK_OFF":  {"max_positions":3, "pos_cap":0.07, "cash_floor":0.70, "sl":0.04, "trail_act":1.08, "trail_pct":0.92, "tier2":False, "vol_min":1.5},
}

# ─── Indicators ────────────────────────────────────────────────────

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    for p in [20, 50, 200]:
        d[f"MA{p}"] = d["CLOSE"].rolling(p).mean()
    # Golden cross / death cross
    d["GOLDEN_CROSS"] = (d["MA20"] > d["MA50"]) & (d["MA20"].shift(1) <= d["MA50"].shift(1))
    d["DEATH_CROSS"] = (d["MA20"] < d["MA50"]) & (d["MA20"].shift(1) >= d["MA50"].shift(1))
    d["MA_BULLISH"] = d["MA20"] > d["MA50"]
    # RSI
    delta = d["CLOSE"].diff()
    g = delta.where(delta > 0, 0.0); l = (-delta).where(delta < 0, 0.0)
    rs = g.rolling(14).mean() / l.rolling(14).mean().replace(0, np.nan)
    d["RSI"] = 100 - (100 / (1 + rs))
    # Volume
    d["VOL_MA"] = d["VOLUME"].rolling(30).mean()
    d["VOL_RATIO"] = d["VOLUME"] / d["VOL_MA"].replace(0, np.nan)
    # Breakout/breakdown
    d["LOW_20D"] = d["LOW"].rolling(20).min()
    d["HIGH_20D"] = d["HIGH"].rolling(20).max()
    # ADX
    d["TR"] = pd.concat([abs(d["HIGH"]-d["LOW"]), abs(d["HIGH"]-d["CLOSE"].shift(1)), abs(d["LOW"]-d["CLOSE"].shift(1))], axis=1).max(axis=1)
    d["ATR"] = d["TR"].rolling(14).mean()
    d["UP"] = d["HIGH"] - d["HIGH"].shift(1); d["DOWN"] = d["LOW"].shift(1) - d["LOW"]
    d["PDM"] = np.where((d["UP"]>d["DOWN"])&(d["UP"]>0), d["UP"], 0)
    d["MDM"] = np.where((d["DOWN"]>d["UP"])&(d["DOWN"]>0), d["DOWN"], 0)
    d["PDI"] = 100 * d["PDM"].ewm(span=14, adjust=False).mean() / d["ATR"].replace(0, np.nan)
    d["MDI"] = 100 * d["MDM"].ewm(span=14, adjust=False).mean() / d["ATR"].replace(0, np.nan)
    d["ADX"] = 100 * abs(d["PDI"]-d["MDI"]) / (d["PDI"]+d["MDI"]).replace(0, np.nan)
    d["ADX"] = d["ADX"].ewm(span=14, adjust=False).mean()
    return d

def check_buy(row, cfg, regime):
    if pd.isna(row.get("MA200")) or pd.isna(row.get("RSI")):
        return None
    if not row.get("MA_BULLISH", False):
        return None
    if row["CLOSE"] <= row["MA200"]:
        return None
    adx_v = row.get("ADX", np.nan)
    if pd.notna(adx_v) and adx_v < 20:
        return None
    if row["RSI"] >= 65 or row["RSI"] <= 35:
        return None
    vol_min = cfg.get("vol_min", 1.2)
    if row.get("VOL_RATIO", 0) < vol_min:
        return None
    # Golden cross = strong signal
    is_gc = row.get("GOLDEN_CROSS", False)
    if is_gc and 40 <= row["RSI"] <= 55:
        return "Tier 1 (Golden Cross)"
    if cfg.get("tier2", True) and 35 < row["RSI"] < 65:
        return "Tier 2 (MA Trend)"
    return None

def check_sell(row, entry_price, highest_price=None, cfg=None, partial_taken=False):
    if cfg is None: cfg = REGIME_CONFIG["RISK_ON"]
    sl = cfg.get("sl", 0.05)
    if row["CLOSE"] <= entry_price * (1 - sl):
        return "stop_loss"
    if not partial_taken and row["CLOSE"] >= entry_price * 1.20:
        return "partial_profit"
    if row["CLOSE"] < row.get("LOW_20D", 0):
        return "breakdown_sell"
    if row.get("RSI", 50) > 85:
        return "rsi_overbought"
    trail_act = cfg.get("trail_act", 1.15)
    trail_pct = cfg.get("trail_pct", 0.88)
    if highest_price and highest_price >= entry_price * trail_act:
        if row["CLOSE"] <= highest_price * trail_pct:
            return "trailing_stop"
    # Death cross exit
    if row.get("DEATH_CROSS", False):
        return "death_cross"
    if not row.get("MA_BULLISH", True) and row.get("RSI", 50) < 50:
        return "ma_trend_reversal"
    return None

def run(data, start, end, label, capital=START_CAPITAL, macro_gate=None):
    trading_days = sorted({d for df in data.values() for d in df["DATE"].dt.date if start <= d <= end})
    cash = capital; positions = {}; trades = []; eq = []; t2q = []; risk_off_blocked = 0; cool_off = None

    for day in trading_days:
        day_dt = pd.Timestamp(day)
        regime = "RISK_ON"
        if macro_gate: regime = macro_gate.get(day, "RISK_ON")
        cfg = {**REGIME_CONFIG.get(regime, REGIME_CONFIG["RISK_ON"])}

        released = [a for rd,a in t2q if rd <= day]
        cash += sum(released) if released else 0; t2q = [(rd,a) for rd,a in t2q if rd > day]

        pv = 0
        for s in list(positions.keys()):
            if s in data and day_dt in data[s]["DATE"].values:
                r = data[s].loc[data[s]["DATE"] == day_dt].iloc[0]
                positions[s]["cp"] = r["CLOSE"]; pv += r["CLOSE"] * positions[s]["shr"]

        for s in list(positions.keys()):
            if s not in data or day_dt not in data[s]["DATE"].values: continue
            r = data[s].loc[data[s]["DATE"] == day_dt]
            if r.empty: continue
            r = r.iloc[0]
            if pd.isna(r["CLOSE"]) or r["CLOSE"] <= 0: continue
            p = positions[s]
            p["hp"] = max(p.get("hp", p["ep"]), r["CLOSE"])
            ex = check_sell(r, p["ep"], p.get("hp"), cfg, p.get("pp", False))
            if ex is None: continue
            ep2 = r["CLOSE"] * (1 - SLIPPAGE_MID)
            shr = p["shr"]
            if ex == "partial_profit":
                ps = int(shr * 0.5)
                if ps <= 0: continue
                p["shr"] = shr - ps; p["pp"] = True
                no = ep2 * ps; cash += no; t2q.append((day + pd.Timedelta(days=2), no))
                continue
            t = Trade(symbol=s, entry_date=p["ed"], entry_price=p["ep"], exit_date=day,
                       exit_price=ep2, shares=shr, entry_signal=p["sig"], exit_reason=ex)
            ni = p["ep"] * shr; no = ep2 * shr
            if pd.isna(no) or no <= 0: continue
            t.pnl_gross = no - ni; t.pnl_net = compute_costs(p["ep"], ep2, shr)
            t2q.append((day + pd.Timedelta(days=2), no)); trades.append(t); del positions[s]
            if ex in ("stop_loss", "breakdown_sell"): cool_off = day + pd.Timedelta(days=3)

        maxp = cfg.get("max_positions", 5); cf = cfg.get("cash_floor", 0.50)
        if len(positions) >= maxp: eq.append((day, cash + pv)); continue
        if cash < capital * cf: eq.append((day, cash + pv)); continue
        if cool_off and day < cool_off: eq.append((day, cash + pv)); continue

        for s in sorted(data.keys()):
            if s in positions or s not in data or day_dt not in data[s]["DATE"].values: continue
            r = data[s].loc[data[s]["DATE"] == day_dt]
            if r.empty: continue
            r = r.iloc[0]
            if pd.isna(r["CLOSE"]) or r["CLOSE"] <= 0: continue
            sig = check_buy(r, cfg, regime)
            if sig is None: continue
            if regime == "RISK_OFF": risk_off_blocked += 1; continue
            pos_cap = cfg.get("pos_cap", 0.10)
            shr = int(cash * pos_cap / r["CLOSE"]) if r["CLOSE"] > 0 else 0
            if shr <= 0: continue
            ep = r["CLOSE"] * (1 + SLIPPAGE_MID); no = ep * shr
            if pd.isna(no) or no <= 0: continue
            if no > cash:
                shr = int(cash / ep) if ep > 0 else 0
                if shr <= 0: continue; no = ep * shr
            cash -= no
            positions[s] = {"shr": shr, "ep": ep, "ed": day, "sig": sig, "cp": ep, "hp": ep, "pp": False}

        total = cash + sum(
            data[s].loc[data[s]["DATE"] == day_dt, "CLOSE"].values[0] * p["shr"]
            for s, p in positions.items() if s in data and day_dt in data[s]["DATE"].values
        )
        eq.append((day, total))

    # Final close
    t2p = sum(a for _, a in t2q)
    for s, p in list(positions.items()):
        if s not in data: continue
        sd = data[s]; lr = sd[sd["DATE"].dt.date <= end]
        if lr.empty: continue
        l = lr.iloc[-1]; ep2 = l["CLOSE"] * (1 - SLIPPAGE_MID)
        t = Trade(symbol=s, entry_date=p["ed"], entry_price=p["ep"], exit_date=l["DATE"].date(),
                   exit_price=ep2, shares=p["shr"], entry_signal=p["sig"], exit_reason="end_of_period")
        ni = p["ep"] * p["shr"]; no = ep2 * p["shr"]
        t.pnl_gross = no - ni; t.pnl_net = compute_costs(p["ep"], ep2, p["shr"])
        cash += no; trades.append(t)

    ec = cash + t2p
    if pd.isna(ec): ec = capital
    yrs = (end - start).days / 365.25
    cagr = (ec / capital) ** (1 / yrs) - 1 if yrs > 0 else 0

    eq_df = pd.DataFrame(eq, columns=["date", "value"])
    if len(eq_df) > 1:
        eq_df["ret"] = eq_df["value"].pct_change(fill_method=None)
        dr = eq_df["ret"].dropna()
        rf = 0.20; rfd = rf / 252
        sh = (dr.mean() * 252 - rf) / (dr.std() * np.sqrt(252)) if dr.std() > 0 else 0
        ds = dr[dr < 0]; ds_std = np.sqrt((ds**2).mean() * 252) if len(ds) > 0 else 1
        so = (dr.mean() * 252 - rf) / ds_std if ds_std > 0 else 0
        rm = eq_df["value"].cummax(); dd = (eq_df["value"] - rm) / rm; mdd = dd.min() * 100
    else: sh = so = mdd = 0

    ct = [t for t in trades if t.exit_reason != "end_of_period"]
    if ct:
        w = [t for t in ct if t.pnl_net > 0]; lss = [t for t in ct if t.pnl_net <= 0]
        wr = len(w) / len(ct)
        aw = np.mean([t.pnl_net / (t.entry_price * t.shares) * 100 for t in w]) if w else 0
        al = np.mean([t.pnl_net / (t.entry_price * t.shares) * 100 for t in lss]) if lss else 0
        wl = abs(aw / al) if al != 0 else float('inf')
        ex = (wr * aw / 100) - ((1 - wr) * abs(al) / 100)
    else: wr = aw = al = wl = ex = 0

    r = BacktestResult(label=label, start_date=start, end_date=end,
        starting_capital=capital, ending_capital=ec, cagr=cagr, max_drawdown_pct=mdd,
        sharpe_ratio=sh, sortino_ratio=so, win_rate=wr, avg_win_pct=aw, avg_loss_pct=al,
        win_loss_ratio=wl, expectancy_pct=ex * 100, total_trades=len(ct), trades=ct)
    fl = []
    if r.cagr < 0.15: fl.append(f"CAGR {r.cagr:.1%} < 15%")
    if r.sharpe_ratio < 1.0: fl.append(f"Sharpe {r.sharpe_ratio:.2f} < 1.0")
    if r.max_drawdown_pct < -15: fl.append(f"Max DD {r.max_drawdown_pct:.1f}% < -15%")
    if r.win_rate < 0.45: fl.append(f"Win rate {r.win_rate:.1%} < 45%")
    if r.win_loss_ratio < 2.0: fl.append(f"W/L ratio {r.win_loss_ratio:.2f} < 2.0")
    if r.expectancy_pct <= 0: fl.append(f"Expectancy {r.expectancy_pct:.2f}% <= 0")
    if r.total_trades < 30: fl.append(f"Trades {r.total_trades} < 30")
    r.verdict = "PASS" if len(fl) == 0 else "FAIL"; r.failed_thresholds = fl
    return r, eq_df, {"risk_off_blocked": risk_off_blocked}

def pr(r):
    print(f"\n  {r.label}")
    for k in ["cagr", "sharpe_ratio", "sortino_ratio", "max_drawdown_pct", "win_rate", "win_loss_ratio", "expectancy_pct", "total_trades"]:
        v = getattr(r, k)
        fmt = ".1%" if k in ("cagr", "win_rate") else ".2f" if k in ("sharpe_ratio", "sortino_ratio", "win_loss_ratio", "expectancy_pct") else ".1f" if k == "max_drawdown_pct" else "d"
        print(f"    {k.replace('_',' ').title():12s} {v:{fmt}}")
    print(f"    {'Verdict':12s} {r.verdict}")
    for f in r.failed_thresholds: print(f"      ✗ {f}")

def run_analysis():
    print("=" * 70)
    print("  ITERATION 9 — MA Crossover + Macro Gate + ADX")
    print("=" * 70)
    regime_daily = build_regime_timeline()
    macro_gate = dict(zip(regime_daily["date"].dt.date, regime_daily["regime"]))

    print("\n[1/3] Loading data...")
    data = load_data()
    for s in data: data[s] = compute_indicators(data[s])
    print(f"  Loaded {len(data)} symbols")

    print("\n[2/3] Running IS (2018-2023)...")
    is_r, is_eq, is_m = run(data, IS_START, IS_END, "IS (2018-2023) - MA Crossover", macro_gate=macro_gate)

    print("\n[3/3] Running OOS (2024)...")
    oos_r, oos_eq, oos_m = run(data, OOS_START, OOS_END, "OOS (2024) - MA Crossover", macro_gate=macro_gate)

    pr(is_r); pr(oos_r)

    print("\n" + "=" * 70)
    print("  COMPARISON: I7 (Momentum) vs I8 (Combo) vs I9 (MA Cross)")
    print("=" * 70)
    print(f"\n  {'Metric':<18s} {'I7 OOS':>10s} {'I8 OOS':>10s} {'I9 OOS':>10s}")
    print(f"  {'─'*40}")
    print(f"  {'CAGR':<18s} {'26.0%':>10s} {'54.4%':>10s} {oos_r.cagr:>9.1%}")
    print(f"  {'Sharpe':<18s} {'0.45':>10s} {'0.70':>10s} {oos_r.sharpe_ratio:>9.2f}")
    print(f"  {'Max DD':<18s} {'-26.9%':>10s} {'-17.8%':>10s} {oos_r.max_drawdown_pct:>8.1f}%")
    print(f"  {'WR':<18s} {'48.6%':>10s} {'60.9%':>10s} {oos_r.win_rate:>9.1%}")
    print(f"  {'W/L':<18s} {'3.04':>10s} {'2.02':>10s} {oos_r.win_loss_ratio:>9.2f}")
    print(f"  {'Trades':<18s} {'35':>10s} {'23':>10s} {oos_r.total_trades:>9d}")
    print(f"  {'Blocked':<18s} {'N/A':>10s} {'0':>10s} {oos_m['risk_off_blocked']:>9d}")

    out = {"iteration":9, "description":"MA crossover + macro gate + ADX + regime-aware exits",
           "is":{"cagr":is_r.cagr,"sharpe":is_r.sharpe_ratio,"max_dd":is_r.max_drawdown_pct,"wr":is_r.win_rate,"wl":is_r.win_loss_ratio,"trades":is_r.total_trades,"verdict":is_r.verdict},
           "oos":{"cagr":oos_r.cagr,"sharpe":oos_r.sharpe_ratio,"max_dd":oos_r.max_drawdown_pct,"wr":oos_r.win_rate,"wl":oos_r.win_loss_ratio,"trades":oos_r.total_trades,"verdict":oos_r.verdict}}
    with open("data/runs/iteration9_results.json", "w") as f: json.dump(out, f, indent=2, default=str)
    print(f"\n  Saved to data/runs/iteration9_results.json")

if __name__ == "__main__": run_analysis()
