from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from backend.database import get_db
from backend.schemas import TradeCreate, TradeUpdate, TradeOut
from backend.services.journal_service import (
    create_trade, close_trade, get_trades, get_open_trades, get_performance,
)

router = APIRouter(prefix="/api/journal", tags=["journal"])


@router.get("/trades")
def list_trades(symbol: Optional[str] = None, limit: int = 50, db: Session = Depends(get_db)):
    trades = get_trades(db, symbol, limit)
    return [TradeOut.model_validate(t) for t in trades]


@router.get("/trades/open")
def list_open_trades(db: Session = Depends(get_db)):
    trades = get_open_trades(db)
    return [TradeOut.model_validate(t) for t in trades]


@router.post("/trades")
def add_trade(trade: TradeCreate, db: Session = Depends(get_db)):
    t = create_trade(db, trade)
    return TradeOut.model_validate(t)


@router.patch("/trades/{trade_id}")
def update_trade(trade_id: int, update: TradeUpdate, db: Session = Depends(get_db)):
    t = close_trade(db, trade_id, update)
    if not t:
        raise HTTPException(404, "Trade not found")
    return TradeOut.model_validate(t)


@router.get("/performance")
def get_trade_performance(db: Session = Depends(get_db)):
    return get_performance(db)
