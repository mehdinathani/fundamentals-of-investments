"""Macro overlay service — wraps Layer 1.5 logic."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from datetime import date, datetime
from typing import Optional
from scripts.macro_data import (
    SBP_RATES, USDPKR, IMF_STATUS, KSE100_PE, classify_regime, get_macro_dataframe
)


def get_current_macro_state(as_of: Optional[date] = None) -> dict:
    """Get the current macro state with supporting data."""
    if as_of is None:
        as_of = date.today()

    # Find closest month-end <= as_of
    all_months = sorted(SBP_RATES.keys())
    closest = None
    for m in all_months:
        if m <= as_of:
            closest = m
        else:
            break

    if closest is None:
        return {"state": "UNKNOWN", "date": as_of, "sbp_rate": None, "usdpkr": None,
                "imf_status": None, "kse100_pe": None}

    import pandas as pd
    row = pd.Series({
        "date": pd.Timestamp(closest),
        "sbp_rate": SBP_RATES[closest],
        "usdpkr": USDPKR[closest],
        "imf_status": IMF_STATUS[closest],
        "kse100_pe": KSE100_PE[closest],
        "usdpkr_30d_pct": None,
    })

    # Compute usdpkr_30d_pct
    idx = all_months.index(closest)
    if idx > 0:
        prev = all_months[idx - 1]
        row["usdpkr_30d_pct"] = (USDPKR[closest] - USDPKR[prev]) / USDPKR[prev]

    state = classify_regime(row)

    return {
        "state": state,
        "date": closest,
        "sbp_rate": SBP_RATES[closest],
        "usdpkr": USDPKR[closest],
        "imf_status": IMF_STATUS[closest],
        "kse100_pe": KSE100_PE[closest],
    }
