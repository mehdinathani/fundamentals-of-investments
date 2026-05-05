# Playwright Patterns for PSX DPS Portal

## Basic Page Load with Wait

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://dps.psx.com.pk/companies", wait_until="networkidle")
    page.wait_for_selector("table tbody tr")  # Wait for data rows
    html = page.content()
    browser.close()
```

## Handling Pagination

```python
from playwright.sync_api import sync_playwright
import time, random

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://dps.psx.com.pk/companies", wait_until="networkidle")

    all_data = []
    while True:
        page.wait_for_selector("table tbody tr")
        rows = page.query_selector_all("table tbody tr")
        for row in rows:
            all_data.append(row.inner_text())

        # Check for next button
        next_btn = page.query_selector("button[aria-label='Next']")
        if not next_btn or not next_btn.is_enabled():
            break

        next_btn.click()
        page.wait_for_load_state("networkidle")
        time.sleep(random.uniform(2.0, 3.5))  # Rate limit

    browser.close()
```

## Extracting Table Data

```python
# Get all rows as dicts
headers = [th.inner_text() for th in page.query_selector_all("table thead th")]

rows_data = []
for tr in page.query_selector_all("table tbody tr"):
    cells = [td.inner_text() for td in tr.query_selector_all("td")]
    rows_data.append(dict(zip(headers, cells)))
```

## Waiting for Dynamic Content

```python
# Wait for specific element
page.wait_for_selector(".company-data", timeout=30000)

# Wait for network to be idle (all XHR/fetch done)
page.wait_for_load_state("networkidle")

# Wait for specific response
with page.expect_response("**/api/companies*") as resp_info:
    page.goto("https://dps.psx.com.pk/companies")
response = resp_info.value
data = response.json()
```

## Downloading Files (Excel/CSV)

```python
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Set download path
    with page.expect_download() as download_info:
        page.click("a:has-text('Download Excel')")
    download = download_info.value
    download.save_as("/path/to/save/file.xlsx")

    browser.close()
```

## Common PSX Selectors

| Element | Selector |
|---------|----------|
| Company table | `table tbody tr` |
| Company symbol link | `a[href*='/companies/']` |
| Price column | `td:nth-child(2)` (varies by table) |
| Next pagination | `button[aria-label='Next'], .pagination-next` |
| Financials table | `table.financials-table` |
| Download button | `a:has-text('Excel'), a:has-text('CSV')` |
| Loading spinner | `.spinner, .loading` (wait for `state="hidden"`) |
