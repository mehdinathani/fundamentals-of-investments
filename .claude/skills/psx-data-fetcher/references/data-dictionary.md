# PSX Data Dictionary

## Common Fields in PSX Data

| Field | Description | Example | Unit |
|-------|-------------|---------|------|
| `symbol` | Stock ticker | `ENGRO` | String |
| `company_name` | Full company name | `Engro Corporation Limited` | String |
| `sector` | PSX sector classification | `Fertilizer`, `Commercial Banks` | String |
| `ltp` | Last traded price (5-min delay) | `145.50` | PKR |
| `change` | Change from previous close | `+2.50` or `-1.25` | PKR |
| `change_pct` | Percentage change | `1.75%` | Percent |
| `volume` | Shares traded (day) | `125000` | Shares |
| `high` | Day's high | `148.00` | PKR |
| `low` | Day's low | `143.50` | PKR |
| `open` | Day's opening price | `144.00` | PKR |
| `prev_close` | Previous day close | `143.00` | PKR |
| `52w_high` | 52-week high | `160.00` | PKR |
| `52w_low` | 52-week low | `120.00` | PKR |
| `market_cap` | Market capitalization | `145000000000` | PKR |
| `shares_outstanding` | Total shares | `1000000000` | Shares (often millions) |

## Sector Codes (Common)

| Sector | Typical Stocks |
|--------|----------------|
| Commercial Banks | HBL, MCB, UBL, NBP |
| Oil & Gas Exploration | OGDC, PPL, MARI |
| Fertilizer | ENGRO, FFCL, FATIMA |
| Cement | LUCK, DGKC, CHCC |
| Pharmaceuticals | SEARL, FEROZ, ABOT |
| Textile | NML, ICI, COLG |
| Power Generation | HUBC, KAPCO |
| Technology | SYS, NETSOL |

## Index Symbols

| Symbol | Name | Description |
|--------|------|-------------|
| `KSE100` | KSE-100 Index | Top 100 companies by market cap |
| `KSE30` | KSE-30 Index | Top 30 companies |
| `KSEALL` | KSE-All Index | All listed companies |
| `BKTI` | KMI-30 Index | Top 30 Shariah-compliant |
