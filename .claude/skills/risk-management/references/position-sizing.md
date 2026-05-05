# Position Sizing Formulas

## Core Formula

```
Position Size (shares) = Max Loss Amount / (Entry Price - Stop-Loss Price)
Position Size (PKR) = Position Size (shares) × Entry Price
```

## Extended Example

```
Account Balance: PKR 2,000,000
Risk Percentage: 5%
Max Loss Amount: PKR 100,000

Entry Price: PKR 150/share
Stop-Loss Price: PKR 142.50 (5% stop)
Price Risk: PKR 7.50/share

Shares = 100,000 / 7.50 = 13,333 shares
PKR Invested = 13,333 × 150 = PKR 2,000,000

⚠️ EXCEEDS 20% LIMIT (100% of account)!
Adjusted: Max 20% = PKR 400,000
Adjusted Shares = 400,000 / 150 = 2,666 shares
Actual Risk = 2,666 × 7.50 = PKR 19,995 (≈1% of account)

This shows the 20% limit may override the 5% risk rule.
```

## Conservative vs Standard Sizing

| Risk Profile | Risk % | Stop-Loss | When to Use |
|--------------|--------|-----------|-------------|
| Conservative | 3% | 3% | Account < PKR 1M, volatile stocks |
| Standard | 5% | 5% | Account ≥ PKR 1M, stable large-caps |

## Implementation

```python
def calculate_position(account_balance, entry_price, stop_pct=0.05,
                       risk_pct=0.05):
    """
    Returns: {
        "shares": int,
        "pkr_invested": float,
        "max_loss": float,
        "actual_risk_pct": float
    }
    """
    if not (0.03 <= risk_pct <= 0.05):
        raise ValueError("Risk must be 3-5%")

    stop_price = entry_price * (1 - stop_pct)
    price_risk = entry_price - stop_price
    max_loss = account_balance * risk_pct

    shares = int(max_loss / price_risk)
    pkr_invested = shares * entry_price

    # Enforce 20% max per position
    max_position = account_balance * 0.20
    if pkr_invested > max_position:
        shares = int(max_position / entry_price)
        pkr_invested = shares * entry_price
        max_loss = shares * price_risk

    return {
        "shares": shares,
        "pkr_invested": round(pkr_invested, 2),
        "stop_price": round(stop_price, 2),
        "max_loss": round(max_loss, 2),
        "actual_risk_pct": round((max_loss / account_balance) * 100, 2),
    }
```
