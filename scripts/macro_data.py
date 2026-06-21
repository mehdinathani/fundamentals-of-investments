#!/usr/bin/env python3
"""
Macro Regime Data Collection — Pakistan 2018-2024
Sources: SBP annual reports, MUFAP, IMF press releases, PSX data portal.
"""
import pandas as pd
import numpy as np
from datetime import date, datetime

# ─── SBP Policy Rate History (monthly) ──────────────────────────────
# Sources: SBP Monetary Policy Statements, MUFAP
SBP_RATES = {
    date(2018,1,31): 6.00, date(2018,2,28): 6.00,
    date(2018,3,31): 6.00, date(2018,4,30): 6.00,
    date(2018,5,31): 6.50, date(2018,6,30): 6.50,
    date(2018,7,31): 7.50, date(2018,8,31): 7.50,
    date(2018,9,30): 7.50, date(2018,10,31): 8.50,
    date(2018,11,30): 8.50, date(2018,12,31): 10.00,
    date(2019,1,31): 10.00, date(2019,2,28): 10.00,
    date(2019,3,31): 10.75, date(2019,4,30): 10.75,
    date(2019,5,31): 12.25, date(2019,6,30): 12.25,
    date(2019,7,31): 13.25, date(2019,8,31): 13.25,
    date(2019,9,30): 13.25, date(2019,10,31): 13.25,
    date(2019,11,30): 13.25, date(2019,12,31): 13.25,
    date(2020,1,31): 13.25, date(2020,2,29): 13.25,
    date(2020,3,31): 11.00, date(2020,4,30): 9.00,
    date(2020,5,31): 8.00, date(2020,6,30): 7.00,
    date(2020,7,31): 7.00, date(2020,8,31): 7.00,
    date(2020,9,30): 7.00, date(2020,10,31): 7.00,
    date(2020,11,30): 7.00, date(2020,12,31): 7.00,
    date(2021,1,31): 7.00, date(2021,2,28): 7.00,
    date(2021,3,31): 7.00, date(2021,4,30): 7.00,
    date(2021,5,31): 7.00, date(2021,6,30): 7.00,
    date(2021,7,31): 7.00, date(2021,8,31): 7.00,
    date(2021,9,30): 7.00, date(2021,10,31): 7.00,
    date(2021,11,30): 7.00, date(2021,12,31): 7.00,
    date(2022,1,31): 9.75, date(2022,2,28): 9.75,
    date(2022,3,31): 9.75, date(2022,4,30): 12.25,
    date(2022,5,31): 12.25, date(2022,6,30): 13.75,
    date(2022,7,31): 15.00, date(2022,8,31): 15.00,
    date(2022,9,30): 15.00, date(2022,10,31): 15.00,
    date(2022,11,30): 16.00, date(2022,12,31): 16.00,
    date(2023,1,31): 17.00, date(2023,2,28): 17.00,
    date(2023,3,31): 17.00, date(2023,4,30): 17.00,
    date(2023,5,31): 17.00, date(2023,6,30): 22.00,
    date(2023,7,31): 22.00, date(2023,8,31): 22.00,
    date(2023,9,30): 22.00, date(2023,10,31): 22.00,
    date(2023,11,30): 22.00, date(2023,12,31): 22.00,
    date(2024,1,31): 22.00, date(2024,2,29): 22.00,
    date(2024,3,31): 22.00, date(2024,4,30): 22.00,
    date(2024,5,31): 22.00, date(2024,6,30): 20.50,
    date(2024,7,31): 19.50, date(2024,8,31): 19.50,
    date(2024,9,30): 17.50, date(2024,10,31): 15.00,
    date(2024,11,30): 15.00, date(2024,12,31): 13.00,
    date(2025,1,31): 13.00, date(2025,2,28): 12.00,
    date(2025,3,31): 12.00, date(2025,4,30): 12.00,
    date(2025,5,31): 11.00, date(2025,6,30): 11.00,
    date(2025,7,31): 11.00, date(2025,8,31): 11.00,
    date(2025,9,30): 11.00, date(2025,10,31): 11.00,
    date(2025,11,30): 11.00, date(2025,12,31): 10.50,
    date(2026,1,31): 10.50, date(2026,2,28): 10.50,
    date(2026,3,31): 10.50, date(2026,4,30): 11.50,
    date(2026,5,31): 11.50,
}

# ─── USD/PKR Monthly Close ──────────────────────────────────────────
# Sources: PSX forex data, SBP historical series
USDPKR = {
    date(2018,1,31): 110.0, date(2018,2,28): 111.5,
    date(2018,3,31): 111.0, date(2018,4,30): 112.0,
    date(2018,5,31): 114.0, date(2018,6,30): 121.0,
    date(2018,7,31): 122.0, date(2018,8,31): 123.5,
    date(2018,9,30): 122.0, date(2018,10,31): 125.0,
    date(2018,11,30): 134.0, date(2018,12,31): 139.0,
    date(2019,1,31): 138.0, date(2019,2,28): 140.0,
    date(2019,3,31): 139.5, date(2019,4,30): 140.0,
    date(2019,5,31): 147.0, date(2019,6,30): 150.0,
    date(2019,7,31): 155.0, date(2019,8,31): 154.0,
    date(2019,9,30): 154.5, date(2019,10,31): 153.0,
    date(2019,11,30): 155.0, date(2019,12,31): 155.5,
    date(2020,1,31): 154.0, date(2020,2,29): 154.5,
    date(2020,3,31): 162.0, date(2020,4,30): 160.0,
    date(2020,5,31): 161.0, date(2020,6,30): 163.0,
    date(2020,7,31): 164.0, date(2020,8,31): 165.0,
    date(2020,9,30): 164.5, date(2020,10,31): 160.0,
    date(2020,11,30): 158.0, date(2020,12,31): 160.0,
    date(2021,1,31): 159.0, date(2021,2,28): 158.0,
    date(2021,3,31): 153.0, date(2021,4,30): 152.0,
    date(2021,5,31): 153.0, date(2021,6,30): 157.0,
    date(2021,7,31): 160.0, date(2021,8,31): 164.0,
    date(2021,9,30): 168.0, date(2021,10,31): 172.0,
    date(2021,11,30): 174.0, date(2021,12,31): 176.5,
    date(2022,1,31): 175.0, date(2022,2,28): 178.0,
    date(2022,3,31): 179.0, date(2022,4,30): 183.0,
    date(2022,5,31): 189.0, date(2022,6,30): 204.0,
    date(2022,7,31): 223.0, date(2022,8,31): 235.0,
    date(2022,9,30): 235.0, date(2022,10,31): 222.0,
    date(2022,11,30): 225.0, date(2022,12,31): 226.0,
    date(2023,1,31): 255.0, date(2023,2,28): 265.0,
    date(2023,3,31): 270.0, date(2023,4,30): 283.0,
    date(2023,5,31): 285.0, date(2023,6,30): 275.0,
    date(2023,7,31): 285.0, date(2023,8,31): 295.0,
    date(2023,9,30): 290.0, date(2023,10,31): 282.0,
    date(2023,11,30): 285.0, date(2023,12,31): 282.0,
    date(2024,1,31): 280.0, date(2024,2,29): 279.0,
    date(2024,3,31): 278.5, date(2024,4,30): 278.0,
    date(2024,5,31): 278.5, date(2024,6,30): 278.0,
    date(2024,7,31): 278.5, date(2024,8,31): 279.0,
    date(2024,9,30): 278.0, date(2024,10,31): 277.5,
    date(2024,11,30): 278.0, date(2024,12,31): 278.0,
    date(2025,1,31): 278.5, date(2025,2,28): 279.0,
    date(2025,3,31): 279.5, date(2025,4,30): 279.0,
    date(2025,5,31): 279.0, date(2025,6,30): 278.5,
    date(2025,7,31): 279.0, date(2025,8,31): 279.5,
    date(2025,9,30): 279.0, date(2025,10,31): 278.5,
    date(2025,11,30): 278.5, date(2025,12,31): 279.0,
    date(2026,1,31): 279.0, date(2026,2,28): 279.0,
    date(2026,3,31): 278.5, date(2026,4,30): 278.8,
    date(2026,5,31): 278.9,
}

# ─── IMF Program Status ────────────────────────────────────────────
# on_track, minor_delays, at_risk, review_missed, program_active
IMF_STATUS = {
    date(2018,1,31): "program_active", date(2018,2,28): "program_active",
    date(2018,3,31): "program_active", date(2018,4,30): "program_active",
    date(2018,5,31): "program_active", date(2018,6,30): "program_active",
    date(2018,7,31): "program_active", date(2018,8,31): "at_risk",
    date(2018,9,30): "at_risk", date(2018,10,31): "at_risk",
    date(2018,11,30): "at_risk", date(2018,12,31): "at_risk",
    date(2019,1,31): "at_risk", date(2019,2,28): "at_risk",
    date(2019,3,31): "at_risk", date(2019,4,30): "at_risk",
    date(2019,5,31): "at_risk", date(2019,6,30): "at_risk",
    date(2019,7,31): "on_track",  # 3yr EFF approved July 2019
    date(2019,8,31): "on_track", date(2019,9,30): "on_track",
    date(2019,10,31): "on_track", date(2019,11,30): "on_track",
    date(2019,12,31): "on_track",
    date(2020,1,31): "on_track", date(2020,2,29): "on_track",
    date(2020,3,31): "on_track", date(2020,4,30): "minor_delays",
    date(2020,5,31): "minor_delays", date(2020,6,30): "minor_delays",
    date(2020,7,31): "minor_delays", date(2020,8,31): "minor_delays",
    date(2020,9,30): "minor_delays", date(2020,10,31): "minor_delays",
    date(2020,11,30): "minor_delays", date(2020,12,31): "minor_delays",
    date(2021,1,31): "minor_delays", date(2021,2,28): "minor_delays",
    date(2021,3,31): "on_track",  # 2nd review completed
    date(2021,4,30): "on_track", date(2021,5,31): "on_track",
    date(2021,6,30): "on_track", date(2021,7,31): "on_track",
    date(2021,8,31): "on_track", date(2021,9,30): "on_track",
    date(2021,10,31): "on_track", date(2021,11,30): "on_track",
    date(2021,12,31): "on_track",
    date(2022,1,31): "on_track", date(2022,2,28): "at_risk",
    date(2022,3,31): "at_risk", date(2022,4,30): "at_risk",
    date(2022,5,31): "at_risk", date(2022,6,30): "at_risk",
    date(2022,7,31): "at_risk", date(2022,8,31): "review_missed",
    date(2022,9,30): "review_missed", date(2022,10,31): "review_missed",
    date(2022,11,30): "review_missed", date(2022,12,31): "review_missed",
    date(2023,1,31): "review_missed", date(2023,2,28): "review_missed",
    date(2023,3,31): "review_missed", date(2023,4,30): "review_missed",
    date(2023,5,31): "review_missed", date(2023,6,30): "on_track",  # SBA $3B approved
    date(2023,7,31): "on_track", date(2023,8,31): "on_track",
    date(2023,9,30): "on_track", date(2023,10,31): "on_track",
    date(2023,11,30): "on_track", date(2023,12,31): "on_track",
    date(2024,1,31): "on_track", date(2024,2,29): "on_track",
    date(2024,3,31): "on_track",  # 2nd SBA review completed
    date(2024,4,30): "on_track", date(2024,5,31): "on_track",
    date(2024,6,30): "on_track", date(2024,7,31): "on_track",
    date(2024,8,31): "on_track", date(2024,9,30): "on_track",
    date(2024,10,31): "on_track", date(2024,11,30): "on_track",
    date(2024,12,31): "on_track",
    date(2025,1,31): "on_track", date(2025,2,28): "on_track",
    date(2025,3,31): "on_track", date(2025,4,30): "on_track",
    date(2025,5,31): "on_track", date(2025,6,30): "on_track",
    date(2025,7,31): "on_track", date(2025,8,31): "on_track",
    date(2025,9,30): "on_track", date(2025,10,31): "on_track",
    date(2025,11,30): "on_track", date(2025,12,31): "on_track",
    date(2026,1,31): "on_track", date(2026,2,28): "on_track",
    date(2026,3,31): "on_track", date(2026,4,30): "on_track",
    date(2026,5,31): "on_track",
}

# ─── KSE-100 P/E Ratio (monthly) ───────────────────────────────────
# Sources: PSX data portal, Bloomberg/KSE reports
KSE100_PE = {
    date(2018,1,31): 12.1, date(2018,2,28): 11.8,
    date(2018,3,31): 11.5, date(2018,4,30): 10.9,
    date(2018,5,31): 10.2, date(2018,6,30): 9.5,
    date(2018,7,31): 9.8, date(2018,8,31): 9.2,
    date(2018,9,30): 9.0, date(2018,10,31): 8.5,
    date(2018,11,30): 7.8, date(2018,12,31): 7.5,
    date(2019,1,31): 8.0, date(2019,2,28): 8.2,
    date(2019,3,31): 7.8, date(2019,4,30): 8.5,
    date(2019,5,31): 7.2, date(2019,6,30): 7.5,
    date(2019,7,31): 7.0, date(2019,8,31): 6.5,
    date(2019,9,30): 6.8, date(2019,10,31): 7.0,
    date(2019,11,30): 7.2, date(2019,12,31): 7.2,
    date(2020,1,31): 7.0, date(2020,2,29): 6.5,
    date(2020,3,31): 5.2, date(2020,4,30): 5.8,
    date(2020,5,31): 6.0, date(2020,6,30): 6.5,
    date(2020,7,31): 6.8, date(2020,8,31): 7.0,
    date(2020,9,30): 7.2, date(2020,10,31): 7.5,
    date(2020,11,30): 8.0, date(2020,12,31): 8.5,
    date(2021,1,31): 8.8, date(2021,2,28): 9.0,
    date(2021,3,31): 8.5, date(2021,4,30): 8.8,
    date(2021,5,31): 9.0, date(2021,6,30): 9.2,
    date(2021,7,31): 9.0, date(2021,8,31): 8.5,
    date(2021,9,30): 8.0, date(2021,10,31): 8.2,
    date(2021,11,30): 7.8, date(2021,12,31): 7.5,
    date(2022,1,31): 7.2, date(2022,2,28): 7.0,
    date(2022,3,31): 6.5, date(2022,4,30): 6.0,
    date(2022,5,31): 5.8, date(2022,6,30): 5.5,
    date(2022,7,31): 5.2, date(2022,8,31): 5.0,
    date(2022,9,30): 5.0, date(2022,10,31): 5.2,
    date(2022,11,30): 5.1, date(2022,12,31): 5.0,
    date(2023,1,31): 4.8, date(2023,2,28): 4.5,
    date(2023,3,31): 4.5, date(2023,4,30): 4.2,
    date(2023,5,31): 4.0, date(2023,6,30): 4.5,
    date(2023,7,31): 5.0, date(2023,8,31): 5.2,
    date(2023,9,30): 5.5, date(2023,10,31): 5.8,
    date(2023,11,30): 6.0, date(2023,12,31): 6.5,
    date(2024,1,31): 6.8, date(2024,2,29): 7.0,
    date(2024,3,31): 7.2, date(2024,4,30): 7.5,
    date(2024,5,31): 7.8, date(2024,6,30): 7.5,
    date(2024,7,31): 7.2, date(2024,8,31): 7.0,
    date(2024,9,30): 7.1, date(2024,10,31): 7.3,
    date(2024,11,30): 7.5, date(2024,12,31): 7.8,
    date(2025,1,31): 8.0, date(2025,2,28): 8.2,
    date(2025,3,31): 8.0, date(2025,4,30): 8.5,
    date(2025,5,31): 8.8, date(2025,6,30): 9.0,
    date(2025,7,31): 8.5, date(2025,8,31): 8.5,
    date(2025,9,30): 8.8, date(2025,10,31): 9.0,
    date(2025,11,30): 9.2, date(2025,12,31): 9.5,
    date(2026,1,31): 9.5, date(2026,2,28): 9.0,
    date(2026,3,31): 8.5, date(2026,4,30): 8.0,
    date(2026,5,31): 8.2,
}

def get_last_day_of_month(d):
    """Return last day of the month for a given date."""
    import datetime
    next_month = datetime.date(d.year + d.month // 12, d.month % 12 + 1, 1)
    return datetime.date(next_month.year, next_month.month, 1) - datetime.timedelta(days=1)

def get_macro_dataframe():
    """Build a monthly macro DataFrame with regime classification."""
    months = sorted(SBP_RATES.keys())
    rows = []
    for m in months:
        rows.append({
            "date": pd.Timestamp(m),
            "sbp_rate": SBP_RATES[m],
            "usdpkr": USDPKR[m],
            "imf_status": IMF_STATUS[m],
            "kse100_pe": KSE100_PE[m],
        })
    df = pd.DataFrame(rows)
    df["usdpkr_30d_pct"] = df["usdpkr"].pct_change()
    return df

def classify_regime(row) -> str:
    """Apply macro-states.md logic to classify a single row.
    Returns RISK_OFF, NEUTRAL, or RISK_ON.
    """
    # Determine SBP policy direction from previous month
    sorted_dates = sorted(SBP_RATES.keys())
    current_ts = row["date"]
    current_d = date(current_ts.year, current_ts.month, current_ts.day)
    prev_rate = None
    for i, sd in enumerate(sorted_dates):
        if sd >= current_d:
            if i > 0:
                prev_rate = SBP_RATES[sorted_dates[i-1]]
            break

    sbp_hiking = prev_rate is not None and row["sbp_rate"] > prev_rate
    sbp_cutting = prev_rate is not None and row["sbp_rate"] < prev_rate
    sbp_hold = prev_rate is None or row["sbp_rate"] == prev_rate

    # USD/PKR: positive pct_change = PKR weakening
    pct = row["usdpkr_30d_pct"]
    pkr_weakening = pct is not None and pct > 0.05
    pkr_stable = pct is not None and pct <= 0.03
    pkr_mixed = pct is not None and 0.03 < pct <= 0.05

    imf = row["imf_status"]
    pe = row["kse100_pe"]
    kse100_pe_10yr_median = 7.2

    # ─── Risk-off: any single trigger → risk-off ───
    if sbp_hiking:
        return "RISK_OFF"
    if pkr_weakening:
        return "RISK_OFF"
    if imf in ("at_risk", "review_missed"):
        return "RISK_OFF"
    if pe > kse100_pe_10yr_median * 1.15:
        return "RISK_OFF"

    # ─── Risk-on vs Neutral: majority vote ───
    risk_on_count = 0
    if sbp_cutting or sbp_hold:
        risk_on_count += 1
    if pkr_stable:
        risk_on_count += 1
    if imf == "on_track":
        risk_on_count += 1
    if pe <= kse100_pe_10yr_median:
        risk_on_count += 1

    return "RISK_ON" if risk_on_count >= 3 else "NEUTRAL"
