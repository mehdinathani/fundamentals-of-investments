from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.auth import require_auth
from backend.services.macro_service import get_current_macro_state
from backend.services.journal_service import record_macro_state, get_latest_macro

router = APIRouter(prefix="/api/macro", tags=["macro"], dependencies=[Depends(require_auth)])


@router.get("/state")
def current_macro_state():
    """Get current macro state (risk-on/neutral/risk-off)."""
    return get_current_macro_state()


@router.post("/refresh")
def refresh_macro_state(db: Session = Depends(get_db)):
    """Fetch and save current macro state to database."""
    state = get_current_macro_state()
    record_macro_state(
        db, state["state"], state["sbp_rate"],
        state["usdpkr"], state["imf_status"], state["kse100_pe"]
    )
    return {"status": "saved", "state": state["state"]}
