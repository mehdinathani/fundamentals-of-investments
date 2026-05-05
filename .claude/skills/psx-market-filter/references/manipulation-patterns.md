# PSX Manipulation Patterns

Common operator-driven patterns to detect and reject.

## Pattern 1: Mark-up before dump
- 3-5 consecutive days of 2-5% gains
- Volume DECLINES across the run
- Concentrated buyer (single broker dominates)
- **Action:** REJECT. The "rally" is one party walking the price.

## Pattern 2: Pump on rumor / WhatsApp tip
- Single-day move > 5% on volume > 5× 30d avg
- No corporate announcement, no sector news
- Price often gives back next 2 days
- **Action:** REJECT for 5 days. If still elevated with NO retracement, investigate news.

## Pattern 3: Sponsor-driven price support
- Stock holds at exact PKR level despite weak fundamentals
- Volume thin but consistent buying near support
- Common in companies with sponsor stake > 70%
- **Action:** AVOID. Price is engineered, not market-discovered.

## Pattern 4: Wash trading / circular volume
- High volume but price unchanged
- Same brokers on both sides (visible in market depth)
- **Action:** REJECT — volume is fictional.

## Pattern 5: Bear raid
- Sudden 5-7% drop on heavy volume
- Triggers stops, panic selling
- Price recovers next session
- **Action:** Do NOT enter on the bounce — wait 3 sessions for stabilization.

## Detection thresholds (matches SKILL.md)

| Pattern | Detector |
|---------|----------|
| Mark-up | move>2% × 3 days AND vol_today < vol_yesterday × 3 |
| Pump | move>5% AND vol_ratio>5 AND no_news |
| Operator | move>5% AND vol_ratio<1.0 |
| Wash | vol_ratio>3 AND abs(move)<0.5% |
