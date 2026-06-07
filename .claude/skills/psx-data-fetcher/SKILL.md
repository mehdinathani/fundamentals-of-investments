---
name: psx-data-fetcher
description: |
  Fetch market data, company fundamentals, and financial statements from PSX (Pakistan Stock Exchange)
  DPS portal and related PSX endpoints. This skill should be used when users ask to scrape PSX
  data, download PSX financials, access DPS portal endpoints, build PSX data pipelines,
  or automate data collection from psx.com.pk / dps.psx.com.pk / financials.psx.com.pk.
allowed-tools: Read, Write, Bash, WebFetch, mcp__context7__query-docs, mcp__context7__resolve-library-id
---

# PSX Data Fetcher

## 👤 Who This Is For

**This is the data pipeline that powers everything else.** A CA analyst spends hours gathering data from multiple sources (DPS portal, company websites, broker reports). This skill automates that — giving you the same raw data in minutes.

You never need to manually visit dps.psx.com.pk, search for a company, and copy-paste numbers. This skill does it all automatically.

---

## What This Skill Does

- Maps PSX DPS portal endpoints to data needs (market summary, company data, financials, historical prices)
- Handles PSX-specific pagination and rate limiting
- Provides Playwright-based scraping patterns for dynamic PSX pages
- Documents exact URL structures for all PSX data sources
- Handles PSX's inconsistent data formats and delays

## What This Skill Does NOT Do

- Execute trades or provide trading advice
- Predict stock prices or market movements
- Clean or transform data beyond raw extraction
- Store data (caller handles persistence)

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing data pipelines, Python environment, storage layer |
| **Conversation** | Which stocks, which data (prices/financials/announcements), date ranges |
| **Skill References** | Endpoint docs from `references/`, scraping patterns, rate limits |
| **User Guidelines** | Project-specific conventions, output format preferences |

Ensure all required context is gathered before implementing.

---

## PSX Data Portal Architecture

PSX exposes data through three main portals:

| Portal | Base URL | Purpose |
|--------|-----------|---------|
| **DPS Portal** | `https://dps.psx.com.pk` | Primary data portal - live quotes, market summary, historical data |
| **Main PSX** | `https://www.psx.com.pk` | Company listings, announcements, circulars, index data |
| **Financials** | `https://financials.psx.com.pk` | Company financial statements (balance sheet, PL, cash flow) |

### DPS Portal Endpoint Map

```
Base: https://dps.psx.com.pk

/                           → Dashboard (market summary, indices)
/companies                  → Listed companies directory
/companies/{symbol}         → Company detail page (price history, profile)
/companies/{symbol}/financials → Financial statements
/market/indices             → Market indices (KSE-100, KSE-30, etc.)
/market/summary             → Daily market summary
/screener                   → Stock screener
/historical                 → Historical price data download
/announcements              → Company announcements
```

### Main PSX Site Endpoint Map

```
Base: https://www.psx.com.pk

/psx/listing/company-symbol-list  → Full company symbol list (CSV/download)
/psx/announcements                → Regulatory announcements
/psx/market-watch                 → Live market watch
/psx/index-data                   → Index constituents and weights
```

---

## Rate Limiting Rules

PSX portals have no published rate limit API, but empirical observations show:

| Constraint | Value | Mitigation |
|-------------|-------|------------|
| **Requests per minute** | ~30 req/min (DPS portal) | Add 2-3 second delay between requests |
| **Concurrent connections** | Max 2-3 | Serialize requests, avoid parallel scraping |
| **Session timeout** | ~15 minutes idle | Re-establish session if idle |
| **IP-based throttling** | Unconfirmed | Use delays; rotate user-agent if blocked |
| **5-min delay on DPS** | Brief cooldown after bursts | Implement exponential backoff |

**Recommended delay pattern:**
```python
import time, random
time.sleep(random.uniform(2.0, 3.5))  # Between requests
```

---

## Pagination Handling

PSX DPS portal uses server-side pagination for data tables:

| Data Type | Pagination Style | Page Size | Notes |
|-----------|-----------------|-----------|-------|
| Company list | Query params `?page=N&limit=M` | 50-100 | `limit` max ~500 |
| Historical prices | Date-range based, no page param | N/A | Use `from` and `to` date params |
| Financials | Single page per period | N/A | One statement per quarter/annual |
| Announcements | `?page=N` incremental | 20-50 | Scan until empty result |

**Pagination pattern:**
```python
page = 1
while True:
    data = fetch(f"/companies?page={page}&limit=100")
    if not data or len(data) == 0:
        break
    process(data)
    page += 1
    time.sleep(2.5)
```

---

## Data Freshness & Timing

| Data Type | Freshness | Notes |
|-----------|-----------|-------|
| Live quotes | 5-minute delay | DPS shows "delayed by 5 minutes" |
| Daily settlement | After 4:00 PM PKT | Trading hours: 9:30 AM - 3:30 PM PKT |
| Financial statements | Quarterly (within 30 days) | Q1/Q2/Q3 (Mar/Jun/Sep), Annual (Dec) |
| Corporate announcements | Real-time | Immediate upon submission |

---

## Scraping Patterns

### Pattern 1: Static Page (requests + BeautifulSoup)
Use for: company lists, static announcements
```python
import requests
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0 ..."}
resp = requests.get("https://www.psx.com.pk/psx/listing/company-symbol-list", headers=headers)
soup = BeautifulSoup(resp.text, "html.parser")
```

### Pattern 2: Dynamic Page (Playwright)
Use for: DPS portal, financials portal (JavaScript-rendered)
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://dps.psx.com.pk/companies", wait_until="networkidle")
    page.wait_for_selector("table")  # Wait for data table
    html = page.content()
    browser.close()
```

See `references/playwright-patterns.md` for detailed Playwright recipes.

---

## Common PSX Symbols & Conventions

- **Symbol format**: 3-5 letter codes, e.g., `ENGRO`, `OGDC`, `LUCK`, `HBL`, `MCB`
- **Sector codes**: Sector names in PSX listings (Cement, Commercial Banks, Oil & Gas, etc.)
- **Index symbols**: `KSE100`, `KSE30`, `KSEALL`, `BKTI` (KMI-30)
- **Date format**: DD-MM-YYYY or YYYY-MM-DD depending on endpoint

---

## Output Checklist

- [ ] Correct PSX portal URL used for the data type
- [ ] Rate limiting delays implemented (2-3s between requests)
- [ ] Pagination handled for multi-page results
- [ ] Date ranges validated (trading days only, PSX calendar)
- [ ] Error handling for 404/timeout/throttle responses
- [ ] Symbols validated against PSX listing (no fake tickers)
- [ ] 5-minute delay respected for "live" data

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/endpoints.md` | When mapping a data need to specific URL |
| `references/playwright-patterns.md` | When scraping dynamic DPS/financials pages |
| `references/rate-limits.md` | When implementing request loops or bulk downloads |
| `references/data-dictionary.md` | When interpreting PSX column names and codes |
| `references/psx-symbols.md` | When validating stock symbols or sector lookups |

## Source

PSX Official: [www.psx.com.pk](https://www.psx.com.pk) | [dps.psx.com.pk](https://dps.psx.com.pk)
