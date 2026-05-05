# PSX Column Name Mapping

Maps PSX-specific financial statement column names to standard accounting terms.

## Statement of Comprehensive Income (Profit/Loss)

| PSX Column Name (exact) | Standard Term | Notes |
|--------------------------|--------------|-------|
| `Revenue from contracts with customers` | Revenue / Sales | Sometimes just `Sales` |
| `Cost of sales` | COGS | |
| `Gross profit` | Gross Profit | |
| `Distribution costs` | Selling Expense | |
| `Administrative expenses` | G&A Expense | |
| `Other income` | Other Income | |
| `Finance costs` | Interest Expense | |
| `Share of profit/(loss) of associates` | Associate Income | |
| `Profit before taxation` | EBT | |
| `Taxation` | Tax Expense | |
| `Profit after taxation` | Net Income (PAT) | **Key for ROE, EPS** |
| `Other comprehensive income` | OCI | |
| `Total comprehensive income` | Total Income | |
| `Earnings per share - basic` | Basic EPS | Often disclosed |
| `Earnings per share - diluted` | Diluted EPS | If applicable |
| `Number of shares` | Shares Outstanding | Often in notes |

## Statement of Financial Position (Balance Sheet)

| PSX Column Name (exact) | Standard Term | Notes |
|--------------------------|--------------|-------|
| `Non-current assets` | Long-term Assets | |
| `Current assets` | Current Assets | |
| `Total assets` | Total Assets | Balance check |
| `Non-current liabilities` | Long-term Debt | **Part of Debt-to-Equity** |
| `Current borrowings` | Short-term Debt | **Part of Debt-to-Equity** |
| `Trade and other payables` | A/P and Accrued | NOT debt |
| `Other current liabilities` | Operating Liabilities | NOT debt |
| `Current liabilities` | Current Liabilities | |
| `Total liabilities` | Total Liabilities | |
| `Equity attributable to owners of the parent` | Shareholders' Equity | **Key for ROE** |
| `Non-controlling interest` | Minority Interest | Exclude from ROE |
| `Total equity` | Total Equity | |
| `Retained earnings` | Retained Earnings | Part of equity |

## Key Unit Conventions

| Item | Typical Unit | Note |
|------|-------------|------|
| Revenue, PAT, Assets, Liabilities | PKR Millions | Most common |
| EPS | PKR per share | Disclosed directly |
| Shares Outstanding | Millions | Check: is it 1,000M or 1M? |

## Statement Date Formats

- **Annual**: Ends December 31 (reported as "December 2024")
- **Quarterly Q1**: Ends March 31
- **Quarterly Q2**: Ends June 30
- **Quarterly Q3**: Ends September 30

## Common PSX Statement Variations

1. **Consolidated vs Unconsolidated**: Always prefer consolidated (includes subsidiaries)
2. **Statement of Changes in Equity**: May be separate or within Balance Sheet notes
3. **Notes to Accounts**: Sometimes EPS shares count is only in notes, not main statement
4. **Appropriations section**: Shows dividend declarations (use for dividend yield)
