# PSX Rate Limiting Reference

## Empirically Observed Limits

| Portal | Constraint | Observed Behavior |
|--------|-------------|-------------------|
| dps.psx.com.pk | ~30 req/min | 429 or timeout after ~5 rapid requests |
| www.psx.com.pk | ~60 req/min | More tolerant, still throttle after burst |
| financials.psx.com.pk | ~20 req/min | Strictest portal, light weighting |

## Recommended Delay Strategy

```python
import time, random

def rate_limited_fetch(url, session, min_delay=2.0, max_delay=3.5):
    """Fetch with rate limiting."""
    time.sleep(random.uniform(min_delay, max_delay))
    return session.get(url, timeout=30)
```

## Exponential Backoff for Errors

```python
import time

def fetch_with_backoff(url, max_retries=5):
    delay = 2.0
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 429:
                time.sleep(delay)
                delay *= 2
                continue
            return resp
        except (requests.Timeout, requests.ConnectionError):
            time.sleep(delay)
            delay *= 2
    raise Exception("Max retries exceeded")
```

## Session Management

```python
import requests

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
})
# Reuse session for all requests to same portal
```
