import sys
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.macros import (
    RUNS_DIR, VALIDATION_SYMBOLS, BENCHMARKS_DIR,
    INDEX_KSE30, INDEX_KSE100, INDEX_ALLSHR,
)
from scripts.psx_data import get_market_watch
from scripts.market_filter import market_reality_filter, filter_universe
from scripts.category_benchmarks import compute_ratios_for_symbol, load_benchmarks
from scripts.ratio_calculator import compare_stock, print_comparison, get_benchmark_age_days
from scripts.evidence_signals import generate_signal, print_signal
from scripts.heatmap_tradebars import sector_heatmap, trade_bar, print_decision_sheet_header

BOLD = "\033[1m"
RESET = "\033[0m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"


def run_scan(mode="dry-run", capital_tier="standard", symbols=None, output_path=None, data_age_threshold=30):
    if symbols is None:
        symbols = VALIDATION_SYMBOLS
    output_lines = []
    def out(text=""):
        print(text)
        output_lines.append(text)

    print_decision_sheet_header(capital_tier)

    out(f"\n{BOLD}Phase 1: Market Data{RESET}")
    out("-" * 40)
    out(f"  Mode: {mode} | Capital tier: {capital_tier}")
    out("  Loading market watch and cached historical data...")
    mw_df = get_market_watch()
    out(f"  Market watch: {len(mw_df)} stocks loaded")
    cached = list((Path(__file__).resolve().parent.parent / "data" / "historical").glob("*.parquet"))
    out(f"  Historical cache: {len(cached)} symbols")
    bm_age = get_benchmark_age_days()
    if bm_age > data_age_threshold:
        out(f"  {RED}⚠ STALE BENCHMARKS: {bm_age} days old (max {data_age_threshold}){RESET}")
        out(f"  {YELLOW}  Run: python scripts/category_benchmarks.py --update{RESET}")
    else:
        out(f"  Benchmarks: {bm_age} days old")
    out()

    out(f"{BOLD}Phase 2: Market Reality Filter (Layer 0){RESET}")
    out("-" * 40)
    filter_results = []
    for sym in symbols:
        result = market_reality_filter(sym, capital_tier)
        filter_results.append(result)
        icon = "✅" if result.verdict == "TRADABLE" else "⚠️" if result.verdict == "CAUTION" else "❌"
        out(f"  {icon} {sym}: {result.verdict}")
        for reason in result.reasons:
            out(f"      → {reason}")
    tradable = [r.symbol for r in filter_results if r.verdict == "TRADABLE"]
    out(f"\n  Tradable universe: {len(tradable)}/{len(symbols)} symbols")
    out()

    out(f"{BOLD}Phase 3: Category Benchmarks{RESET}")
    out("-" * 40)
    benchmarks = load_benchmarks()
    for idx in [INDEX_KSE30, INDEX_KSE100, INDEX_ALLSHR]:
        b = benchmarks.get(idx, {})
        pe = b.get("PE", "N/A")
        eps = b.get("EPS", "N/A")
        pe_n = b.get("PE_count", 0)
        eps_n = b.get("EPS_count", 0)
        out(f"  {idx:<8} P/E={pe} (n={pe_n})  EPS={eps} (n={eps_n})")
    out()

    out(f"{BOLD}Phase 4: Ratio Analysis{RESET}")
    out("-" * 40)
    for sym in symbols:
        result = compare_stock(sym, mw_df=mw_df)
        price = result.get("price", "N/A")
        out(f"  {sym}: Price={price}")
        for ratio_field, data in result["ratios"].items():
            val = data.get("value")
            val_str = f"{val:.2f}" if val is not None else "N/A"
            verdicts = []
            for idx_name in [INDEX_KSE30, INDEX_KSE100]:
                comp = data["comparisons"].get(idx_name, {})
                v = comp.get("verdict")
                dev = comp.get("deviation_pct")
                if v:
                    verdicts.append(f"{idx_name}: {v} ({dev:+.1f}%)")
            out(f"      {ratio_field}={val_str}  {'; '.join(verdicts)}")
    out()

    out(f"{BOLD}Phase 5: Technical Signals (Layer 2){RESET}")
    out("-" * 40)
    for sym in symbols:
        result = generate_signal(sym, capital_tier)
        icon = "🟢" if result.signal == "BUY" else "🔴" if result.signal == "SELL" else "🟡"
        tier_str = f" ({result.tier.upper()})" if result.tier else ""
        out(f"  {icon} {sym}: {result.signal}{tier_str}")
        for reason in result.reasons:
            out(f"      → {reason}")
    out()

    out(f"{BOLD}Phase 6: Risk Assessment{RESET}")
    out("-" * 40)
    buys = []; sells = []; holds = []
    for sym in symbols:
        sig = generate_signal(sym, capital_tier)
        sl = sig.evidence.get("stop_loss_pct", 5)
        price = sig.evidence.get("price", 0)
        if sig.signal == "BUY":
            stop_price = price * (1 - sl / 100)
            out(f"  {sym}: BUY @ {price:.2f} | Stop-loss @ {stop_price:.2f} ({sl:.0f}%)")
            buys.append(sym)
        elif sig.signal == "SELL":
            out(f"  {sym}: SELL signal — no position")
            sells.append(sym)
        else:
            out(f"  {sym}: HOLD — monitoring")
            holds.append(sym)
    if not buys and not sells:
        out(f"\n  {YELLOW}→ No actionable signals today. All symbols in HOLD.{RESET}")
    out()

    sector_heatmap(mw_df)
    for sym in symbols:
        signal_result = generate_signal(sym, capital_tier)
        trade_bar(sym, signal=signal_result.signal)

    if capital_tier == "conservative":
        out(f"{YELLOW}Conservative tier: stricter liquidity floors (2×), 3% max loss per trade{RESET}")
    else:
        out(f"  Standard tier: default liquidity floors, 5% max loss per trade")

    if mode == "dry-run":
        out(f"\n{BOLD}Mode: DRY RUN{RESET} — No trades executed. Journal entries pending.")
    elif mode == "journal-only":
        out(f"\n{BOLD}Mode: JOURNAL ONLY{RESET} — Journal entries ready for review.")

    out(f"\n{BOLD}END OF SCAN{RESET}")
    out(f"{'='*60}")

    if output_path:
        with open(output_path, "w") as f:
            f.write("\n".join(output_lines))
        print(f"\n  Decision sheet saved to {output_path}")

    return output_lines


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PSX Daily Investment Scan Pipeline")
    parser.add_argument("--mode", choices=["dry-run", "journal-only"], default="dry-run",
                        help="Execution mode (default: dry-run)")
    parser.add_argument("--conservative", action="store_true",
                        help="Conservative capital tier (small account)")
    parser.add_argument("--symbols", type=str, nargs="+",
                        help="Specific symbols to scan (default: validation set)")
    parser.add_argument("--output", type=str,
                        help="Output file path (default: data/runs/YYYY-MM-DD-HHMM.md)")
    parser.add_argument("--data-age", type=int, default=30,
                        help="Max age of benchmark data in days before warning (default: 30)")
    args = parser.parse_args()

    tier = "conservative" if args.conservative else "standard"
    symbols = [s.upper() for s in args.symbols] if args.symbols else None
    now = datetime.now()
    output_path = args.output or str(RUNS_DIR / f"{now.strftime('%Y-%m-%d-%H%M')}.md")
    RUNS_DIR.mkdir(parents=True, exist_ok=True)

    run_scan(mode=args.mode, capital_tier=tier, symbols=symbols, output_path=output_path, data_age_threshold=args.data_age)
