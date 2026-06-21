from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class TradeCreate(BaseModel):
    symbol: str
    direction: str = "LONG"
    entry_date: date
    entry_price: float
    shares: int
    entry_signal: Optional[str] = None
    notes: Optional[str] = None


class TradeUpdate(BaseModel):
    exit_date: Optional[date] = None
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None
    pnl_gross: Optional[float] = None
    pnl_net: Optional[float] = None
    fees: Optional[float] = None
    notes: Optional[str] = None


class TradeOut(BaseModel):
    id: int
    symbol: str
    direction: str
    entry_date: date
    entry_price: float
    exit_date: Optional[date] = None
    exit_price: Optional[float] = None
    shares: int
    entry_signal: Optional[str] = None
    exit_reason: Optional[str] = None
    pnl_gross: Optional[float] = None
    pnl_net: Optional[float] = None
    fees: Optional[float] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SignalOut(BaseModel):
    id: int
    symbol: str
    signal_type: str
    signal_strength: Optional[str] = None
    entry_price: Optional[float] = None
    current_price: Optional[float] = None
    reason: Optional[str] = None
    macro_state: Optional[str] = None
    date: date
    is_active: bool

    class Config:
        from_attributes = True


class MacroStateOut(BaseModel):
    id: int
    date: date
    state: str
    sbp_rate: Optional[float] = None
    usdpkr: Optional[float] = None
    imf_status: Optional[str] = None
    kse100_pe: Optional[float] = None

    class Config:
        from_attributes = True


class PerformanceOut(BaseModel):
    total_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    win_loss_ratio: float
    expectancy: float
    cagr: Optional[float] = None
    sharpe: Optional[float] = None
    max_drawdown: Optional[float] = None
    total_pnl_net: float


class PipelineStatus(BaseModel):
    id: int
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    symbols_scanned: Optional[int] = None
    signals_generated: Optional[int] = None
    macro_state: Optional[str] = None
    error: Optional[str] = None
