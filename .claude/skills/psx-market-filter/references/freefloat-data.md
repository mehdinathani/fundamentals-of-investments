# Freefloat Data Sources for PSX

Freefloat = % of issued shares actually available to public traders (excludes sponsor, government, strategic holdings, treasury).

## Why it matters

- Low freefloat → small number of buyers/sellers can swing price.
- < 25% freefloat is the manipulation red flag.
- Index inclusion (KSE-30, KSE-100) requires freefloat thresholds.

## Where to get it

| Source | Endpoint | Update frequency |
|--------|----------|------------------|
| PSX index methodology PDF | psx.com.pk → "Index Methodology" | Quarterly |
| PSX free-float data sheet | psx.com.pk/psx/themes/psx/uploads/Free-Float-Data.xlsx | Quarterly |
| Annual report (Pattern of Shareholding) | financials.psx.com.pk → company → Annual | Yearly |
| Brokerage research | Manual lookup | Variable |

## Caveats

- Freefloat reported by PSX is for index weighting; may differ from "tradable float" in practice.
- Recently listed companies (lock-in periods) have artificially constrained float for first 6-12 months.
- Strategic stakes acquired after listing don't always update the official freefloat number promptly — cross-check sponsor announcements.

## Default fallback

If freefloat unknown:
- KSE-30 stock → assume ≥ 25% (passes filter)
- KSE-100 stock → assume ≥ 20% (still review)
- Outside KSE-100 → REJECT until verified

## Caching

Cache freefloat per symbol with TTL = 90 days. Re-fetch on quarterly review.
