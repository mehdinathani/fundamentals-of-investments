---
name: financial-ratios-psx
description: |
  Calculate financial ratios from PSX (Pakistan Stock Exchange) company financial statements.
  Handles PSX-specific column names and statement formats that differ from standard
  accounting presentations. This skill should be used when users ask to compute
  ROE, P/E, EPS, Debt-to-Equity, or any financial ratio from PSX financial data,
  parse PSX balance sheets or profit/loss statements, or analyze PSX company fundamentals.
allowed-tools: Read, Write, Bash, mcp__context7__query-docs, mcp__context7__resolve-library-id
---

# Financial Ratios PSX

Calculates financial ratios using PSX-specific financial statement formats. PSX companies file statements under SECP requirements with column naming that differs from international standards.

## What This Skill Does

- Maps PSX column names to standard financial metrics
- Computes ROE, P/E, EPS, Debt-to-Equity with PSX-specific formulas
- Handles PSX's quarterly (Mar/Jun/Sep) and annual (Dec) statement cycles
- Accounts for PSX-specific line items (e.g., "Profit after taxation" not "Net Income")
- Supports both consolidated and unconsolidated statement formats

## What This Skill Does NOT Do

- Fetch data from PSX (use `psx-data-fetcher` skill)
- Make buy/sell recommendations
- Adjust for inflation or currency effects
- Handle non-PSX financial statements

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing financial models, pandas usage, data schema |
| **Conversation** | Which companies, which ratios, which periods (quarterly/annual) |
| **Skill References** | PSX column mappings from `references/`, formula definitions |
| **User Guidelines** | Output format (DataFrame/CSV/JSON), rounding preferences |

Ensure all required context is gathered before implementing.

---

## PSX Financial Statement Structure

PSX companies publish three statements via `financials.psx.com.pk`:

1. **Statement of Comprehensive Income** (Profit/Loss Account)
2. **Statement of Financial Position** (Balance Sheet)
3. **Cash Flow Statement**

### PSX vs Standard Column Names

PSX uses SECP-prescribed formats. Key differences:

| Standard Term | PSX Column Name |
|---------------|-----------------|
| Revenue / Sales | `Revenue from contracts with customers` or `Sales` or `Turnover` |
| Cost of Goods Sold | `Cost of sales` |
| Gross Profit | `Gross profit` |
| Operating Expenses | `Distribution costs` + `Administrative expenses` |
| Operating Profit | `Profit from operations` |
| Finance Cost / Interest | `Finance costs` |
| Profit Before Tax | `Profit before taxation` |
| Net Income | `Profit after taxation` (PAT) |
| Retained Earnings | `Retained earnings` or `Accumulated losses` |
| Shareholders' Equity | `Total equity` (under "Equity attributable to owners") |
| Total Assets | `Total assets` |
| Total Debt | `Non-current liabilities` + `Current borrowings` (see formula) |
| EPS | `Earnings per share - basic` (disclosed, not calculated) |
| Shares Outstanding | `Number of shares` or in notes to accounts |

---

## Core Ratio Formulas (PSX-Specific)

### 1. Earnings Per Share (EPS)

```
EPS = Profit after taxation / Weighted Average Shares Outstanding
```

**PSX nuance:**
- PSX statements often disclose `Earnings per share - basic` directly
- If not disclosed, use: `Profit after taxation / Number of shares`
- Shares outstanding typically in millions; ensure unit consistency
- Use **diluted EPS** if disclosed and significant dilution exists

```python
def calculate_eps(pat, shares_outstanding_millions, shares_unit="million"):
    """PSX EPS calculation. pat in currency units (PKR millions typically)."""
    if shares_unit == "million":
        return pat / shares_outstanding_millions
    return pat / (shares_outstanding_millions * 1_000_000)
```

### 2. Price-to-Earnings (P/E)

```
P/E = Current Market Price / EPS
```

**PSX nuance:**
- Use **trailing twelve months (TTM)** EPS when available
- For quarterly: annualize quarterly EPS (Q1×4, Q2×2, Q3×1.33, Q4 = annual)
- Negative EPS → P/E is "N/A" or "Loss"
- Use **last closed price** from DPS portal, not intraday

```python
def calculate_pe(market_price, eps_ttm):
    if eps_ttm <= 0:
        return None  # Loss-making or zero EPS
    return market_price / eps_ttm
```

### 3. Return on Equity (ROE)

```
ROE = Profit after taxation / Average Shareholders' Equity
```

**PSX nuance:**
- `Total equity` = Equity attributable to owners of the parent (exclude non-controlling interest)
- Use **average** of opening and closing equity for the period
- If only closing equity available: `ROE = PAT / Closing Equity` (note limitation)
- Express as percentage

```python
def calculate_roe(pat, equity_opening, equity_closing=None):
    """PSX ROE. All values in same units (PKR millions)."""
    if equity_closing is not None:
        avg_equity = (equity_opening + equity_closing) / 2
    else:
        avg_equity = equity_opening  # Fallback, less accurate
    if avg_equity == 0:
        return None
    return (pat / avg_equity) * 100
```

### 4. Debt-to-Equity Ratio

```
Debt-to-Equity = Total Debt / Total Shareholders' Equity
```

**PSX nuance:**
- `Total Debt` = `Non-current liabilities` (long-term debt) + `Current borrowings` (short-term)
- Do NOT include trade payables, accrued expenses, or other operating liabilities
- `Total equity` from "Equity attributable to owners of the parent"
- Express as ratio (e.g., 0.45 = 45% debt-to-equity)

```python
def calculate_debt_to_equity(non_current_liabilities, current_borrowings, total_equity):
    """PSX Debt-to-Equity. Excludes operating payables."""
    total_debt = non_current_liabilities + current_borrowings
    if total_equity == 0:
        return None
    return total_debt / total_equity
```

---

## Additional PSX Ratios

### Dividend Yield

```
Dividend Yield = (DPS / Market Price) × 100
```
- DPS from corporate announcements on PSX or in `Appropriations` section of financials

### Book Value Per Share (BVPS)

```
BVPS = Total Equity / Shares Outstanding
```

### Current Ratio

```
Current Ratio = Current Assets / Current Liabilities
```
- Both from Balance Sheet (Statement of Financial Position)

### Gross Profit Margin

```
Gross Margin = (Gross Profit / Revenue) × 100
```

---

## PSX Financial Statement Parsing

### Typical PSX Income Statement Columns

| PSX Column (exact) | Maps To | Unit |
|---------------------|---------|------|
| `Revenue from contracts with customers` | Revenue | PKR millions |
| `Cost of sales` | COGS | PKR millions |
| `Gross profit` | Gross Profit | PKR millions |
| `Distribution costs` | Selling Expense | PKR millions |
| `Administrative expenses` | Admin Expense | PKR millions |
| `Other income` | Other Income | PKR millions |
| `Finance costs` | Interest Expense | PKR millions |
| `Profit before taxation` | EBT | PKR millions |
| `Taxation` | Tax Expense | PKR millions |
| `Profit after taxation` | Net Income (PAT) | PKR millions |
| `Earnings per share - basic` | EPS | PKR per share |

### Typical PSX Balance Sheet Columns

| PSX Column (exact) | Maps To | Unit |
|---------------------|---------|------|
| `Non-current assets` | Long-term Assets | PKR millions |
| `Current assets` | Current Assets | PKR millions |
| `Total assets` | Total Assets | PKR millions |
| `Non-current liabilities` | Long-term Debt | PKR millions |
| `Current borrowings` | Short-term Debt | PKR millions |
| `Trade and other payables` | Payables | PKR millions |
| `Current liabilities` | Current Liabilities | PKR millions |
| `Total liabilities` | Total Liabilities | PKR millions |
| `Equity attributable to owners of the parent` | Shareholders' Equity | PKR millions |
| `Non-controlling interest` | Minority Interest | PKR millions |
| `Total equity` | Total Equity | PKR millions |

---

## Data Quality Checks

Before computing ratios, validate:

- [ ] Revenue > 0 (statement sanity check)
- [ ] Total Assets = Total Liabilities + Total Equity (balance sheet identity)
- [ ] PAT sign consistent with `Profit before taxation` minus `Taxation`
- [ ] Shares outstanding > 0 and units consistent (millions vs actual)
- [ ] Quarterly vs Annual flag correctly set (affects annualization)
- [ ] Year-end is December (annual) or Mar/Jun/Sep (quarterly)

---

## Output Checklist

- [ ] Correct PSX column names used (not standard/international names)
- [ ] Units normalized (typically PKR millions for amounts, PKR for EPS)
- [ ] TTM EPS used for P/E where possible
- [ ] Negative/zero denominators handled (return None, not crash)
- [ ] Debt-to-Equity excludes operating payables
- [ ] ROE uses average equity if both period-ends available
- [ ] Results labeled with period (Q1/Q2/Q3/Annual) and year

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/psx-column-mapping.md` | When parsing any PSX financial statement |
| `references/ratio-formulas.md` | When implementing any ratio calculation |
| `references/statement-samples.md` | When handling edge cases in statement formats |
| `references/unit-conversions.md` | When normalizing PKR millions, thousands, shares |

## Source

PSX Financials: [financials.psx.com.pk](https://financials.psx.com.pk) | SECP: [www.secp.gov.pk](https://www.secp.gov.pk)
