# PSX Liquidity Tiers (capital-adjusted)

Liquidity floor scales with capital size. Smaller capital can move smaller stocks but cannot afford to be stuck in them.

## Tier table

| Capital | Universe | Min 30d vol | Min 30d value | Min freefloat |
|---------|----------|-------------|---------------|---------------|
| < 500K  | KSE-30 only | 200,000 sh | PKR 20M | 30% |
| 500K – 1M | KSE-100 top 50 | 100,000 sh | PKR 10M | 25% |
| 1M – 5M | KSE-100 (all 100) | 50,000 sh | PKR 5M | 25% |
| ≥ 5M | KSE-100 + KMI-30 selects | 50,000 sh | PKR 5M | 20% |

## Why these floors

- 50,000 sh / PKR 5M floor = ~1% of daily volume per trade for a 1M account.
  Below this, your own order moves the price.
- Freefloat < 25% means insiders/sponsors can swing price; not a true market.
- Days-traded < 25/30 means you can be stuck for days unable to exit.

## KSE-30 list (most liquid)

Always-allowed core (subject to update — refresh quarterly from PSX):
OGDC, PPL, MARI, POL, MEBL, UBL, HBL, BAFL, MCB, ENGRO, FFC, EFERT,
LUCK, DGKC, MLCF, FCCL, PSO, APL, HASCOL, NESTLE, UNILEVER, COLG,
PAKT, PIOC, SEARL, GLAXO, ABOT, SYS, NETSOL, TRG.

## Refresh policy

Re-rank the tradable universe weekly (not daily) — daily rotation creates noise.
Quarterly: full review of KSE-30 / KSE-100 changes.
