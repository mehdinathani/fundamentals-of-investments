from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.signal_service import scan_all_symbols
from backend.services.macro_service import get_current_macro_state
from backend.services.journal_service import (
    create_pipeline_run, complete_pipeline_run,
    save_signals, record_macro_state,
)
from backend.models import PipelineRun

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


@router.post("/run")
def run_pipeline(db: Session = Depends(get_db)):
    """Run the full PSX investment pipeline."""
    run = create_pipeline_run(db)

    try:
        macro = get_current_macro_state()
        record_macro_state(db, macro["state"], macro["sbp_rate"],
                          macro["usdpkr"], macro["imf_status"], macro["kse100_pe"])

        results = scan_all_symbols(macro["state"])
        buy_signals = [r for r in results if r["signal"] == "BUY"]

        save_signals(db, buy_signals, macro["state"])

        complete_pipeline_run(
            db, run.id, "completed",
            symbols_scanned=len(results),
            signals=len(buy_signals),
            macro_state=macro["state"],
        )

        return {
            "status": "completed",
            "run_id": run.id,
            "symbols_scanned": len(results),
            "signals_generated": len(buy_signals),
            "macro_state": macro["state"],
        }
    except Exception as e:
        complete_pipeline_run(db, run.id, "failed", error=str(e))
        return {"status": "failed", "run_id": run.id, "error": str(e)}


@router.get("/status")
def pipeline_status(db: Session = Depends(get_db)):
    """Get latest pipeline run status."""
    latest = db.query(PipelineRun).order_by(PipelineRun.id.desc()).first()
    if not latest:
        return {"status": "never_run"}
    return {
        "id": latest.id,
        "status": latest.status,
        "started_at": latest.started_at,
        "completed_at": latest.completed_at,
        "symbols_scanned": latest.symbols_scanned,
        "signals_generated": latest.signals_generated,
        "macro_state": latest.macro_state,
        "error": latest.error,
    }
