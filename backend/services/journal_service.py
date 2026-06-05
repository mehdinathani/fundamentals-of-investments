"""Trade journal service — performance metrics and trade tracking."""
from datetime import date, datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
import numpy as np

from backend.models import Trade, Signal, MacroState, PipelineRun
from backend.schemas import TradeCreate, TradeUpdate


def create_trade(db: Session, t: TradeCreate) -> Trade:
    trade = Trade(
        symbol=t.symbol,
        direction=t.direction,
        entry_date=t.entry_date,
        entry_price=t.entry_price,
        shares=t.shares,
        entry_signal=t.entry_signal,
        notes=t.notes,
    )
    db.add(trade)
    db.commit()
    db.refresh(trade)
    return trade


def close_trade(db: Session, trade_id: int, u: TradeUpdate) -> Optional[Trade]:
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not trade:
        return None
    for key, val in u.model_dump(exclude_unset=True).items():
        setattr(trade, key, val)
    if u.exit_price is not None and trade.entry_price:
        if trade.direction == "SHORT":
            gross = (trade.entry_price - u.exit_price) * trade.shares
        else:
            gross = (u.exit_price - trade.entry_price) * trade.shares
        trade.pnl_gross = round(gross, 2)
        trade.pnl_net = round(gross - (u.fees or 0), 2)
    db.commit()
    db.refresh(trade)
    return trade


def get_trades(db: Session, symbol: Optional[str] = None, limit: int = 50) -> list[Trade]:
    q = db.query(Trade)
    if symbol:
        q = q.filter(Trade.symbol == symbol)
    return q.order_by(Trade.entry_date.desc()).limit(limit).all()


def get_open_trades(db: Session) -> list[Trade]:
    return db.query(Trade).filter(Trade.exit_date.is_(None)).all()


def get_performance(db: Session) -> dict:
    trades = db.query(Trade).filter(Trade.exit_date.isnot(None)).all()
    if not trades:
        return {"total_trades": 0, "win_rate": 0, "avg_win": 0, "avg_loss": 0,
                "win_loss_ratio": 0, "expectancy": 0, "total_pnl_net": 0}

    winners = [t for t in trades if t.pnl_net and t.pnl_net > 0]
    losers = [t for t in trades if t.pnl_net and t.pnl_net <= 0]
    total_trades = len(trades)
    win_rate = len(winners) / total_trades if total_trades > 0 else 0

    avg_win = np.mean([t.pnl_net for t in winners]) if winners else 0
    avg_loss = abs(np.mean([t.pnl_net for t in losers])) if losers else 0
    wl_ratio = avg_win / avg_loss if avg_loss > 0 else 0
    expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
    total_pnl = sum(t.pnl_net or 0 for t in trades)

    return {
        "total_trades": total_trades,
        "win_rate": round(win_rate * 100, 1),
        "avg_win": round(avg_win, 0),
        "avg_loss": round(avg_loss, 0),
        "win_loss_ratio": round(wl_ratio, 2),
        "expectancy": round(expectancy, 0),
        "total_pnl_net": round(total_pnl, 0),
    }


def record_macro_state(db: Session, state: str, sbp_rate=None, usdpkr=None,
                       imf_status=None, kse100_pe=None) -> MacroState:
    record = MacroState(
        date=date.today(),
        state=state,
        sbp_rate=sbp_rate,
        usdpkr=usdpkr,
        imf_status=imf_status,
        kse100_pe=kse100_pe,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_latest_macro(db: Session) -> Optional[MacroState]:
    return db.query(MacroState).order_by(MacroState.date.desc()).first()


def create_pipeline_run(db: Session) -> PipelineRun:
    run = PipelineRun()
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def complete_pipeline_run(db: Session, run_id: int, status: str,
                          symbols_scanned=0, signals=0, macro_state=None,
                          error=None):
    run = db.query(PipelineRun).filter(PipelineRun.id == run_id).first()
    if not run:
        return
    run.status = status
    run.completed_at = datetime.utcnow()
    run.symbols_scanned = symbols_scanned
    run.signals_generated = signals
    run.macro_state = macro_state
    run.error = error
    db.commit()


def get_recent_signals(db: Session, limit: int = 20) -> list[Signal]:
    return db.query(Signal).order_by(Signal.date.desc()).limit(limit).all()


def save_signals(db: Session, signals: list[dict], macro_state: str):
    for sig in signals:
        if sig.get("signal"):
            record = Signal(
                symbol=sig["symbol"],
                signal_type=sig["signal"],
                signal_strength=sig.get("signal_strength"),
                entry_price=sig.get("current_price"),
                current_price=sig.get("current_price"),
                reason=f"RSI {sig.get('rsi', 'N/A'):.0f}, Vol {sig.get('volume_ratio', 'N/A'):.1f}x, ADX {sig.get('adx', 'N/A'):.0f}",
                macro_state=macro_state,
                date=sig.get("date", date.today()),
                is_active=True,
            )
            db.add(record)
    db.commit()
