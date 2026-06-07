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

## 👤 Who This Is For

**You are a student competing against ACCA/CA analysts.** They spent years learning to read financial statements, calculate ratios, and compare companies. This skill does all of that for you — plus it compares each stock against the right benchmark (KSE-30, KSE-100, or ALLSHR) so you know if a company is genuinely good or just average for its category.

## 🧠 Why This Matters — Student vs Pro

| What a CA analyst does | What this skill does for you |
|---|---|
| Reads 3 years of annual reports manually | Parses PSX financials automatically |
| Computes ROE, P/E, D/E by hand or in Excel | Calculates all ratios in seconds |
| Knows sector medians from memory (years of experience) | Compares against KSE-30/KSE-100/ALLSHR benchmarks |
| Spots red flags (declining margins, rising debt) through pattern recognition | Flags data quality issues automatically |
| Spends 2-4 hours per stock | Takes 30 seconds per stock |

---

## What This Skill Does

- Maps PSX column names to standard financial metrics
- Computes ROE, P/E, EPS, Debt-to-Equity with PSX-specific formulas
- **Compares each stock against its category benchmark** — KSE-30, KSE-100, or ALLSHR (see Category Comparison section)
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

---

## 📊 Category Comparison — KSE-30, KSE-100, ALLSHR

**This is your edge against experienced investors.** A CA analyst knows from memory whether a P/E of 8 is good or bad for a given sector. You don't have that memory — but you don't need it. This skill compares every stock against the right benchmark.

### Benchmark Categories

| Category | What It Is | Who Should Use |
|----------|-----------|----------------|
| **KSE-30** | Top 30 largest, most liquid stocks | Capital < PKR 500K (safest universe) |
| **KSE-100** | Top 100 companies by market cap | Capital ≥ PKR 1M (standard universe) |
| **ALLSHR** | All listed companies on PSX | Full market context |

### How Category Comparison Works

For every ratio computed, the output shows:

```
Stock: ENGRO (Fertilizer Sector)
  P/E: 8.5x
  vs KSE-100 median: 9.2x  → BETTER (cheaper than index)
  vs Sector median: 11.3x  → BETTER (cheaper than sector peers)

Stock: TRG (Technology)
  P/E: 35.0x
  vs KSE-100 median: 9.2x  → WORSE (much more expensive than index)
  vs Sector median: 28.0x  → IN LINE (tech trades at premium)
```

**Why this matters:** A P/E of 35 looks terrible compared to KSE-100 (9.2x), but is normal for tech. Without category comparison, you'd make wrong decisions.

### Comparison Logic

```python
def compare_against_benchmarks(stock_ratio, stock_category, sector, benchmark_db):
    """
    stock_category: "KSE30" | "KSE100" | "ALLSHR" | "OTHER"
    benchmark_db contains pre-computed medians for each category + sector

    Returns dict with comparison verdict for each available benchmark.
    """
    results = {}
    for category in ["KSE30", "KSE100", "ALLSHR"]:
        if category in benchmark_db:
            cat_median = benchmark_db[category]["median_" + ratio_name]
            deviation = (stock_ratio - cat_median) / cat_median
            results[f"vs_{category}"] = {
                "median": cat_median,
                "stock_value": stock_ratio,
                "deviation_pct": round(deviation * 100, 1),
                "verdict": "ABOVE" if stock_ratio > cat_median else "BELOW"
            }

    # Sector comparison (if sector data available)
    if sector in benchmark_db.get("sectors", {}):
        sector_median = benchmark_db["sectors"][sector]["median_" + ratio_name]
        results["vs_sector"] = {
            "median": sector_median,
            "stock_value": stock_ratio,
            "deviation_pct": round((stock_ratio - sector_median) / sector_median * 100, 1),
        }

    return results
```

### Benchmark Data Sources

| Benchmark | Source | Refresh Frequency |
|-----------|--------|-------------------|
| KSE-30 medians | KSE-30 index constituents from dps.psx.com.pk | Monthly |
| KSE-100 medians | KSE-100 index constituents | Monthly |
| ALLSHR medians | All PSX listed companies | Quarterly |
| Sector medians | Companies grouped by PSX sector code | Quarterly |

Store pre-computed benchmarks in `data/benchmarks/` for reuse across pipeline runs.

---

## Core Ratio Formulas (PSX-Specific)

### 1. Earnings Per Share (EPS)

**In plain language:** How much profit does the company make per share?

If a company earns PKR 1 billion profit and has 100 million shares, each share earned PKR 10. EPS tells you the company's earning power per unit of ownership.

**What a CA analyst looks for:** Growing EPS over 3-5 years, consistency (no wild swings), and EPS that covers the dividend payment.

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

**In plain language:** How many years of profit does it take to buy this company at the current price?

If a stock costs PKR 100 and earns PKR 10 per share per year, P/E = 10 (you pay 10 years of earnings).

- **Low P/E (5-8x)** = Cheap, but could be cheap for a reason (declining business)
- **Medium P/E (8-15x)** = Normal range for most PSX stocks
- **High P/E (> 20x)** = Expensive relative to earnings. Market expects high future growth.

**What a CA analyst looks for:** P/E compared to:
1. The company's own historical average
2. KSE-100 average (typically 7-10x on PSX)
3. Sector peers
4. International peers (PSX trades at a discount to regional markets)

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

**In plain language:** For every PKR 100 the company's owners have invested, how much profit does the company generate?

ROE measures how efficiently the company uses its capital. If a company has PKR 1 billion in equity and earns PKR 200 million profit, ROE = 20%. That's excellent — PKR 1 of owner money generates PKR 0.20 of annual profit.

- **ROE > 20%** = Excellent. The company generates strong returns on capital.
- **ROE 10-20%** = Good. Normal for established businesses.
- **ROE < 10%** = Weak. You might be better off in a fixed income investment.

**What a CA analyst looks for:** Consistent ROE over 5+ years. High ROE with low debt = genuine operational quality. High ROE with high debt = risky (the returns are leveraged).

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

**In plain language:** How much debt does the company have compared to owner investment?

D/E of 0.5 means for every PKR 100 of owner money, the company has PKR 50 of debt. D/E of 1.5 means it has PKR 150 of debt for every PKR 100 of equity — riskier.

- **D/E < 0.3** = Very conservative (low risk, but maybe under-leveraged)
- **D/E 0.3-0.6** = Healthy range for most non-financial PSX companies
- **D/E 0.6-1.0** = Moderate leverage. Monitor in rising interest rate environment
- **D/E > 1.0** = High debt. Risky if earnings decline or rates rise

**⚠️ Exception:** Banks naturally have high D/E (accepting deposits = debt). For banks, use different benchmarks (typically 5-10x).

**What a CA analyst looks for:** Debt trend over 3-5 years. Is the company paying down debt or accumulating more? Can it service debt from operating cash flow?

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

---

## 🎯 Takeaway for a Student Investor

After this skill runs, you have the same ratio analysis a CA analyst would produce — but with benchmarks you'd need years of experience to know by heart.

**What the pro does:** Computes ratios by hand in Excel, compares against remembered sector medians.

**What this skill does:** Computes ratios automatically from PSX data, compares against KSE-30/KSE-100/ALLSHR benchmarks.

**The difference:** You get the analysis AND the context (category comparison) in one step.

---

## Output Checklist

- [ ] Correct PSX column names used (not standard/international names)
- [ ] Units normalized (typically PKR millions for amounts, PKR for EPS)
- [ ] TTM EPS used for P/E where possible
- [ ] Negative/zero denominators handled (return None, not crash)
- [ ] Debt-to-Equity excludes operating payables
- [ ] ROE uses average equity if both period-ends available
- [ ] Results labeled with period (Q1/Q2/Q3/Annual) and year
- [ ] **Category comparison included** — KSE-30, KSE-100, ALLSHR, and sector medians
- [ ] **Verdict relative to benchmark** — "ABOVE median" or "BELOW median" for each ratio

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
