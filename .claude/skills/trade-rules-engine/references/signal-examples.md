# Signal Examples

## Example 1: Strong Buy Signal

```
Stock: ENGRO
Date: 2024-10-15

Technical State:
  - 20 SMA: 145.00 (crossed ABOVE 50 SMA yesterday)
  - 50 SMA: 142.00
  - 200 SMA: 130.00
  - Price: 148.00 (ABOVE 200 SMA ✓)
  - RSI(14): 52 (in neutral zone ✓)
  - Volume today: 350,000
  - 30-day avg volume: 250,000
  - Volume ratio: 1.4x (≥1.2x ✓)

Signal: BUY (Tier 1 — Strong)
Action: Full position (per risk management sizing)
```

## Example 2: Moderate Buy Signal

```
Stock: SYS
Date: 2024-11-20

Technical State:
  - 20 SMA: 95.00 (crossed ABOVE 50 SMA yesterday)
  - 50 SMA: 93.00
  - 200 SMA: 88.00
  - Price: 97.00 (ABOVE 200 SMA ✓)
  - RSI(14): 38 (recovering from oversold ✓)
  - Volume today: 300,000
  - 30-day avg volume: 240,000
  - Volume ratio: 1.25x (≥1.2x ✓)

Signal: BUY (Tier 2 — Moderate)
Action: Half position (RSI not in ideal 40-60 range)
```

## Example 3: Sell Signal

```
Stock: LUCK
Date: 2024-12-05

Technical State:
  - 20 SMA: 580.00 (crossed BELOW 50 SMA yesterday)
  - 50 SMA: 590.00
  - 200 SMA: 560.00
  - Price: 565.00 (above 200 SMA but falling)
  - RSI(14): 42 (crossed below 50)
  - Volume today: 450,000
  - 30-day avg volume: 300,000
  - Volume ratio: 1.5x (confirmed breakdown)

Signal: SELL
Action: Exit full position
```

## Example 4: Hold (No Signal)

```
Stock: HBL
Date: 2024-09-10

Technical State:
  - 20 SMA: 105.00
  - 50 SMA: 103.00 (20 > 50, uptrend)
  - 200 SMA: 98.00
  - Price: 106.00
  - RSI(14): 65 (above neutral, no crossover)
  - No recent MA crossover

Signal: HOLD
Action: Keep existing position, no new entry
```

## Example 5: Rejected (No Volume)

```
Stock: FFCL
Date: 2024-08-20

Technical State:
  - 20 SMA crosses ABOVE 50 SMA
  - Price ABOVE 200 SMA
  - RSI(14): 48 (good)
  - Volume today: 180,000
  - 30-day avg volume: 220,000
  - Volume ratio: 0.82x (<1.0x ✗)

Signal: NO TRADE (rejected)
Reason: Volume confirmation failed — weak conviction
```

---

## CGT Bracket Reference (filer rates)

| Holding Period | CGT Rate |
|----------------|----------|
| < 6 months | 15% |
| 6–12 months | 12.5% |
| 12–24 months | 10% |
| > 24 months | 0% |

CGT-aware deferral (ADR-002 D7): profit-taking exits within 30 days of a bracket boundary may defer to the lower rate if technicals remain neutral. See `trade-rules-engine/SKILL.md` §4D.
