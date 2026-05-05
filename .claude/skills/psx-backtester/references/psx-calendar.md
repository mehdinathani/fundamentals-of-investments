# PSX Trading Calendar

PSX trades Mon-Fri excluding gazetted holidays. Backtests must use the actual calendar — counting weekends as non-trading days is not enough.

## Trading hours (PKT)

| Session | Time |
|---------|------|
| Pre-open | 09:15 – 09:30 |
| Regular | 09:30 – 15:30 |
| Closing | 15:30 – 15:35 |

## Weekly schedule

Mon-Fri trading. Saturday/Sunday closed.

## Annual holiday closures (typical — verify yearly)

Recurring closures:
- **Kashmir Day** — Feb 5
- **Pakistan Day** — Mar 23
- **Labour Day** — May 1
- **Independence Day** — Aug 14
- **Iqbal Day** — Nov 9 (sometimes traded)
- **Quaid Day / Christmas** — Dec 25
- **Bank holiday** — Jul 1, Dec 31

Lunar (Hijri-based, dates shift each year):
- **Eid-ul-Fitr** — 3 days
- **Eid-ul-Adha** — 3 days
- **Ashura (9 & 10 Muharram)** — 2 days
- **Eid Milad-un-Nabi (12 Rabi-ul-Awwal)** — 1 day

Plus ad-hoc closures: muharram processions in some cities (Karachi often), election days, security situations, mourning days. SBP/PSX announces.

## Source

- PSX official notice: psx.com.pk/psx/themes/psx/uploads/Trading-Calendar.pdf (annual)
- SBP holidays: sbp.org.pk → Banking → Holidays

## Implementation pattern

```python
import pandas as pd
from pandas.tseries.holiday import AbstractHolidayCalendar, Holiday

class PSXCalendar(AbstractHolidayCalendar):
    rules = [
        Holiday("Kashmir Day", month=2, day=5),
        Holiday("Pakistan Day", month=3, day=23),
        Holiday("Labour Day", month=5, day=1),
        Holiday("Independence Day", month=8, day=14),
        Holiday("Iqbal Day", month=11, day=9),
        Holiday("Quaid Day", month=12, day=25),
        # Lunar holidays: load from external table per year
    ]

def trading_days(start, end):
    biz = pd.bdate_range(start, end)
    holidays = PSXCalendar().holidays(start, end)
    lunar = load_lunar_holidays(start.year, end.year)  # external CSV
    return biz.difference(holidays).difference(lunar)
```

Lunar holidays must be loaded from an external table (e.g., `data/psx_holidays_<year>.csv`) and reviewed each Jan against PSX's official calendar.
