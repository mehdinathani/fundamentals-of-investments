from sqlalchemy import Column, Integer, Float, String, Date, DateTime, Text, Boolean
from sqlalchemy.sql import func
from backend.database import Base


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False, index=True)
    entry_date = Column(Date, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_date = Column(Date, nullable=True)
    exit_price = Column(Float, nullable=True)
    shares = Column(Integer, nullable=False)
    entry_signal = Column(String(50), nullable=True)
    exit_reason = Column(String(50), nullable=True)
    pnl_gross = Column(Float, nullable=True)
    pnl_net = Column(Float, nullable=True)
    fees = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False, index=True)
    signal_type = Column(String(10), nullable=False)  # BUY / SELL
    signal_strength = Column(String(20), nullable=True)  # Tier 1 / Tier 2
    entry_price = Column(Float, nullable=True)
    current_price = Column(Float, nullable=True)
    reason = Column(Text, nullable=True)
    macro_state = Column(String(10), nullable=True)
    date = Column(Date, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class MacroState(Base):
    __tablename__ = "macro_states"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True)
    state = Column(String(10), nullable=False)  # RISK_ON / NEUTRAL / RISK_OFF
    sbp_rate = Column(Float, nullable=True)
    usdpkr = Column(Float, nullable=True)
    imf_status = Column(String(20), nullable=True)
    kse100_pe = Column(Float, nullable=True)


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="running")  # running / completed / failed
    symbols_scanned = Column(Integer, nullable=True)
    signals_generated = Column(Integer, nullable=True)
    macro_state = Column(String(10), nullable=True)
    error = Column(Text, nullable=True)
