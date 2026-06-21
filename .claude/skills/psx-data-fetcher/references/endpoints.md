# PSX Endpoint Reference

## DPS Portal (dps.psx.com.pk)

| Path | Data | Format | Pagination |
|------|------|--------|------------|
| `/` | Market dashboard, indices | HTML (dynamic) | N/A |
| `/companies` | Company directory | HTML table (dynamic) | `?page=N&limit=M` |
| `/companies/{symbol}` | Company profile, price history | HTML (dynamic) | Date range |
| `/companies/{symbol}/financials` | Financial statements | HTML/PDF | Single page per period |
| `/market/indices` | Index values (KSE-100, etc.) | HTML (dynamic) | N/A |
| `/market/summary` | Daily market summary | HTML (dynamic) | N/A |
| `/screener` | Stock screener | HTML (dynamic) | `?page=N` |
| `/historical` | Historical price data | CSV download | Date range |
| `/announcements` | Company announcements | HTML (dynamic) | `?page=N` |

## Main PSX (www.psx.com.pk)

| Path | Data | Format |
|------|------|--------|
| `/psx/listing/company-symbol-list` | Full symbol list | HTML/CSV |
| `/psx/announcements` | Regulatory announcements | HTML |
| `/psx/market-watch` | Live market watch | HTML (dynamic) |
| `/psx/index-data` | Index constituents | HTML |
| `/psx/circuit-breakers` | Circuit breaker limits | HTML |

## Financials Portal (financials.psx.com.pk)

| Path | Data | Format |
|------|------|--------|
| `/` | Financial statement browser | HTML (dynamic) |
| `/company/{symbol}` | Company financials landing | HTML |
| `/company/{symbol}/balance-sheet` | Statement of Financial Position | HTML/Excel |
| `/company/{symbol}/profit-loss` | Statement of Comprehensive Income | HTML/Excel |
| `/company/{symbol}/cash-flow` | Cash Flow Statement | HTML/Excel |

## URL Patterns

```
Company page:    https://dps.psx.com.pk/companies/{SYMBOL}
Financials:      https://financials.psx.com.pk/company/{SYMBOL}/profit-loss
Historical CSV:  https://dps.psx.com.pk/historical?symbol={SYMBOL}&from={DD-MM-YYYY}&to={DD-MM-YYYY}
```

## Notes

- DPS portal uses JavaScript rendering — requires Playwright/puppeteer, not simple HTTP
- financials.psx.com.pk often has Excel download option (?format=xlsx)
- PSX trading hours: 9:30 AM - 3:30 PM PKT (Monday-Friday except holidays)
- Data is 5-minute delayed on public portals
