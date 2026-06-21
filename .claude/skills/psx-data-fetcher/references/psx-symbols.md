# PSX Stock Symbols Quick Reference

## Large Cap (KSE-100 Constituents — High Liquidity)

| Symbol | Company | Sector |
|--------|---------|--------|
| HBL | Habib Bank Limited | Commercial Banks |
| UBL | United Bank Limited | Commercial Banks |
| MCB | MCB Bank Limited | Commercial Banks |
| ENGRO | Engro Corporation | Fertilizer/Chemical |
| OGDC | Oil & Gas Development Co. | Oil & Gas E&P |
| PPL | Pakistan Petroleum Limited | Oil & Gas E&P |
| LUCK | Lucky Cement Limited | Cement |
| HUBC | Hub Power Company | Power Generation |
| SYS | Systems Limited | Technology |
| MARI | Mari Petroleum | Oil & Gas E&P |
| ABOT | Abbott Laboratories | Pharmaceuticals |
| NML | Nishat Mills Limited | Textile |
| DGKC | D.G. Khan Cement | Cement |
| FFCL | Fauji Fertilizer | Fertilizer |
| KAPCO | Kapco | Power Generation |

## Symbol Format Rules

- 3-5 uppercase letters
- No numbers in standard symbols (some exceptions with numbers exist)
- No dashes or special characters
- Always uppercase in PSX data

## Finding the Full List

```python
# Scrape from PSX listing page
import requests
from bs4 import BeautifulSoup

url = "https://www.psx.com.pk/psx/listing/company-symbol-list"
resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(resp.text, "html.parser")

symbols = []
for row in soup.select("table tbody tr"):
    cols = row.find_all("td")
    if len(cols) >= 2:
        symbol = cols[0].text.strip()
        name = cols[1].text.strip()
        symbols.append((symbol, name))
```

Or use DPS portal:
```
https://dps.psx.com.pk/companies?page=1&limit=500
```
