# Unit Conversions for PSX Financials

## Common Units in PSX Statements

| Unit Label | Multiplier | Notes |
|------------|-------------|-------|
| `PKR (Million)` | × 1,000,000 | Most common |
| `PKR (Thousand)` | × 1,000 | Some smaller companies |
| `PKR (Billion)` | × 1,000,000,000 | Very large companies |
| `Rs. (Million)` | × 1,000,000 | Same as PKR M |
| `Rs. (000)` | × 1,000 | Same as PKR Thousand |

## Normalization Function

```python
def normalize_to_millions(value, unit_label):
    """
    Normalize any PSX amount to PKR Millions.
    value: raw number from statement
    unit_label: text from statement header (e.g., "PKR in Millions")
    Returns: value in PKR Millions
    """
    unit_label = unit_label.lower()

    if "thousand" in unit_label or "000" in unit_label:
        return value * 0.001  # Thousands → Millions
    elif "billion" in unit_label:
        return value * 1000  # Billions → Millions
    else:  # Assume millions
        return value

# Usage:
# Statement header says "PKR in Thousands"
pat_m = normalize_to_millions(25000000, "PKR in Thousands")  # → 25000
```

## Shares Outstanding

| Source | Typical Unit | Conversion |
|--------|-------------|-------------|
| Main statement | Million shares | Use as-is |
| Notes to accounts | Actual share count | ÷ 1,000,000 → Million |
| DPS portal | Actual share count | ÷ 1,000,000 → Million |

```python
def normalize_shares(shares, unit="million"):
    """Normalize shares to millions."""
    if unit == "actual":
        return shares / 1_000_000
    return shares  # Already in millions
```

## EPS Units

- EPS is always reported in **PKR per share** (not millions)
- If PAT is in millions and shares in millions: `EPS = PAT / shares` → correct PKR per share
- If PAT is in thousands and shares in millions: `EPS = (PAT × 0.001) / shares`
