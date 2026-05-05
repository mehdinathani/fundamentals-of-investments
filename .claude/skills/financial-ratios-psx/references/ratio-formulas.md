# Financial Ratio Formulas (PSX-Specific)

## 1. Earnings Per Share (EPS)

```python
def eps(profit_after_taxation, shares_outstanding):
    """
    profit_after_taxaton: PKR millions (from 'Profit after taxation' line)
    shares_outstanding: in millions (from 'Number of shares' or notes)
    Returns: PKR per share
    """
    if shares_outstanding == 0:
        return None
    return profit_after_taxaton / shares_outstanding
```

**Annualization for quarterly EPS:**
```python
def annualize_eps(quarterly_pat, quarter, shares):
    """Quarter: 1, 2, 3, or 4 (4 = annual)"""
    if quarter == 1:
        return (quarterly_pat * 4) / shares
    elif quarter == 2:
        return (quarterly_pat * 2) / shares
    elif quarter == 3:
        return (quarterly_pat / 3) * 4 / shares
    else:  # Q4 / Annual
        return quarterly_pat / shares
```

## 2. Price-to-Earnings (P/E)

```python
def pe_ratio(market_price, eps_ttm):
    """
    market_price: current market price (PKR)
    eps_ttm: trailing twelve months EPS (PKR)
    Returns: P/E ratio or None if EPS <= 0
    """
    if eps_ttm is None or eps_ttm <= 0:
        return None  # Loss-making
    return market_price / eps_ttm
```

**TTM Calculation:**
```python
def eps_ttm(q4_pat, q3_pat, q2_pat, q1_pat, shares_avg):
    """Sum all 4 quarters for TTM EPS."""
    annual_pat = q4_pat + q3_pat + q2_pat + q1_pat
    return annual_pat / shares_avg
```

## 3. Return on Equity (ROE)

```python
def roe(profit_after_tax, equity_opening, equity_closing=None):
    """
    profit_after_tax: from 'Profit after taxation'
    equity_opening: Equity at start of period
    equity_closing: Equity at end of period (if available)
    Returns: ROE as percentage
    """
    if equity_closing is not None:
        avg_equity = (equity_opening + equity_closing) / 2
    else:
        avg_equity = equity_opening  # Less accurate fallback

    if avg_equity == 0:
        return None
    return (profit_after_tax / avg_equity) * 100
```

## 4. Debt-to-Equity Ratio

```python
def debt_to_equity(non_current_liabilities, current_borrowings, total_equity):
    """
    non_current_liabilities: from Balance Sheet (long-term debt)
    current_borrowings: from Balance Sheet (short-term debt)
    total_equity: 'Equity attributable to owners of the parent'
    Returns: ratio (0.5 = 50% debt-to-equity)
    """
    total_debt = non_current_liabilities + current_borrowings
    if total_equity == 0:
        return None
    return total_debt / total_equity
```

**Important:** Do NOT include `Trade and other payables` or `Other current liabilities` in debt. Only actual borrowings.

## 5. Additional Ratios

### Dividend Yield
```python
def dividend_yield(dividend_per_share, market_price):
    return (dividend_per_share / market_price) * 100
```

### Book Value Per Share (BVPS)
```python
def bvps(total_equity, shares_outstanding):
    if shares_outstanding == 0:
        return None
    return total_equity / shares_outstanding
```

### Current Ratio
```python
def current_ratio(current_assets, current_liabilities):
    if current_liabilities == 0:
        return None
    return current_assets / current_liabilities
```

### Gross Profit Margin
```python
def gross_margin(gross_profit, revenue):
    if revenue == 0:
        return None
    return (gross_profit / revenue) * 100
```

### Revenue Growth (3-Year CAGR)
```python
def revenue_cagr(rev_year3, rev_year2, rev_year1, rev_year0):
    """rev_year0 = oldest (3 years ago), rev_year3 = latest"""
    if rev_year0 == 0:
        return None
    return ((rev_year3 / rev_year0) ** (1/3) - 1) * 100
```
