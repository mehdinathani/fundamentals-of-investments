import sys
import pandas as pd
from pathlib import Path
from datetime import datetime, date

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.macros import DATA_DIR, STALE_DATA_DAYS, DPS_BASE_URL
from scripts.psx_data import _request, get_market_watch
from bs4 import BeautifulSoup

FINANCIALS_DIR = DATA_DIR / "financials"
FINANCIALS_DIR.mkdir(parents=True, exist_ok=True)

BS_LABEL_MAP = {
    "total equity": "TOTAL_EQUITY",
    "equity attributable to owners of the parent": "TOTAL_EQUITY",
    "total equity attributable to owners": "TOTAL_EQUITY",
    "non-current liabilities": "NON_CURRENT_LIABILITIES",
    "noncurrent liabilities": "NON_CURRENT_LIABILITIES",
    "current borrowings": "CURRENT_BORROWINGS",
    "short-term borrowings": "CURRENT_BORROWINGS",
    "current portion of long-term debt": "CURRENT_BORROWINGS",
    "total assets": "TOTAL_ASSETS",
    "current liabilities": "CURRENT_LIABILITIES",
    "non-current assets": "NON_CURRENT_ASSETS",
    "noncurrent assets": "NON_CURRENT_ASSETS",
    "current assets": "CURRENT_ASSETS",
    "trade and other payables": "PAYABLES",
}

PL_LABEL_MAP = {
    "profit after taxation": "PAT",
    "profit for the period": "PAT",
    "revenue from contracts with customers": "REVENUE",
    "sales": "REVENUE",
    "turnover": "REVENUE",
    "finance costs": "FINANCE_COSTS",
    "profit before taxation": "PBT",
    "earnings per share - basic": "EPS_DISCLOSED",
    "earnings per share": "EPS_DISCLOSED",
    "number of shares": "SHARES_OUTSTANDING",
}

COMPANY_LABEL_MAP = {
    "EPS": "eps",
    "Book Value Per Share": "bvps",
    "Dividend Per Share": "dps",
    "No. of Shares": "shares",
}

FINANCIALS_CACHE_TTL_DAYS = 7


def _cache_path(symbol: str) -> Path:
    return FINANCIALS_DIR / f"{symbol.upper()}_fin.parquet"


def _from_cache(symbol: str):
    path = _cache_path(symbol)
    if not path.exists():
        return None
    mtime = datetime.fromtimestamp(path.stat().st_mtime).date()
    age = (date.today() - mtime).days
    if age >= FINANCIALS_CACHE_TTL_DAYS:
        return None
    try:
        return pd.read_parquet(path).to_dict(orient="records")[0]
    except (IndexError, Exception):
        return None


def _to_cache(symbol: str, data: dict):
    path = _cache_path(symbol)
    df = pd.DataFrame([data])
    df.to_parquet(path, index=False)


def _parse_number(val) -> float | None:
    if val is None:
        return None
    cleaned = str(val).replace(",", "").replace("(", "-").replace(")", "").strip()
    if cleaned in ("", "-", "—", "N/A"):
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _match_label(label: str, mapping: dict) -> str | None:
    label_lower = label.strip().lower()
    for psx_name, normalized in mapping.items():
        if psx_name in label_lower:
            return normalized
    return None


def _find_value_in_table(table, label_map: dict) -> dict:
    rows = table.find_all("tr")
    if not rows:
        return {}
    headers = [h.get_text(strip=True) for h in rows[0].find_all("th")]
    if len(headers) < 2:
        return {}
    result = {}
    for row in rows[1:]:
        cells = row.find_all("td")
        if len(cells) < 2:
            continue
        row_label = cells[0].get_text(strip=True)
        normalized = _match_label(row_label, label_map)
        if normalized:
            val = _parse_number(cells[1].get_text(strip=True))
            if val is not None:
                result[normalized] = val
    return result


def _scrape_company_page(symbol: str) -> dict:
    url = f"{DPS_BASE_URL}/company/{symbol}"
    result = {}
    try:
        resp = _request("GET", url)
        soup = BeautifulSoup(resp.text, "html.parser")
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                labels = [c.get_text(strip=True) for c in cells]
                if len(labels) < 2:
                    continue
                normalized = None
                for psx_name, field in COMPANY_LABEL_MAP.items():
                    if labels[0] == psx_name:
                        normalized = field
                        break
                if normalized:
                    val = _parse_number(labels[1])
                    if val is not None:
                        result[normalized] = val
    except Exception:
        pass
    return result


def _scrape_financials_page(symbol: str) -> dict:
    url = f"{DPS_BASE_URL}/financials"
    result = {}
    try:
        resp = _request("POST", url, data={"symbol": symbol})
        soup = BeautifulSoup(resp.text, "html.parser")
        tables = soup.find_all("table")
        if not tables:
            tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            if len(rows) < 2:
                continue
            sample_text = " ".join(c.get_text(strip=True).lower() for c in rows[1].find_all("td"))
            is_bs = any(bs_label in sample_text for bs_label in ["equity", "liabilit", "assets"])
            is_pl = any(pl_label in sample_text for pl_label in ["profit", "revenue", "earnings"])
            if is_bs:
                bs_data = _find_value_in_table(table, BS_LABEL_MAP)
                result.update(bs_data)
            elif is_pl:
                pl_data = _find_value_in_table(table, PL_LABEL_MAP)
                result.update(pl_data)
    except Exception:
        pass
    return result


def parse_symbol_financials(symbol: str, force_refresh: bool = False) -> dict:
    symbol = symbol.upper()
    if not force_refresh:
        cached = _from_cache(symbol)
        if cached:
            return cached
    cp = _scrape_company_page(symbol)
    fin = _scrape_financials_page(symbol)
    combined = {**fin, **cp}
    result = {
        "symbol": symbol,
        "pat": combined.get("PAT") or combined.get("pat"),
        "total_equity": combined.get("TOTAL_EQUITY"),
        "non_current_liabilities": combined.get("NON_CURRENT_LIABILITIES"),
        "current_borrowings": combined.get("CURRENT_BORROWINGS"),
        "eps_disclosed": combined.get("EPS_DISCLOSED") or combined.get("eps"),
        "bvps": combined.get("bvps"),
        "dps": combined.get("dps"),
        "shares": combined.get("shares") or combined.get("SHARES_OUTSTANDING"),
        "source": "company_page" if (cp and not fin.get("TOTAL_EQUITY")) else "financials_page",
    }
    _to_cache(symbol, result)
    return result


def compute_roe(data: dict) -> float | None:
    pat = data.get("pat")
    equity = data.get("total_equity")
    if pat is not None and equity is not None and equity != 0:
        return round((pat / equity) * 100, 2)
    eps = data.get("eps_disclosed")
    bvps = data.get("bvps")
    if eps is not None and bvps is not None and bvps != 0:
        return round((eps / bvps) * 100, 2)
    return None


def compute_de(data: dict) -> float | None:
    ncl = data.get("non_current_liabilities")
    cb = data.get("current_borrowings")
    equity = data.get("total_equity")
    if ncl is None and cb is None:
        return None
    total_debt = (ncl or 0) + (cb or 0)
    if equity and equity != 0:
        return round(total_debt / equity, 2)
    return None


def compute_dividend_yield(data: dict, price: float | None = None) -> float | None:
    dps = data.get("dps")
    if dps is None or price is None or price == 0:
        return None
    return round((dps / price) * 100, 2)


def compute_ratios_for_symbol_financial(symbol: str, price: float | None = None) -> dict:
    data = parse_symbol_financials(symbol)
    roe = compute_roe(data)
    de = compute_de(data)
    div_yield = compute_dividend_yield(data, price)
    return {
        "ROE": roe,
        "DE": de,
        "DIVIDEND_YIELD": div_yield,
        "_fin_data": data,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Parse PSX financial statements for a symbol")
    parser.add_argument("symbol", type=str, help="Symbol to parse")
    parser.add_argument("--price", type=float, help="Current price (for dividend yield)")
    parser.add_argument("--refresh", action="store_true", help="Force refresh from DPS")
    args = parser.parse_args()
    data = parse_symbol_financials(args.symbol, force_refresh=args.refresh)
    print(f"\nFinancial data for {args.symbol.upper()}:")
    print(f"  PAT:               {data.get('pat')}")
    print(f"  Total Equity:      {data.get('total_equity')}")
    print(f"  Non-Cur Liabilities: {data.get('non_current_liabilities')}")
    print(f"  Current Borrowings: {data.get('current_borrowings')}")
    print(f"  BVPS:              {data.get('bvps')}")
    print(f"  DPS:               {data.get('dps')}")
    print(f"  EPS (disclosed):   {data.get('eps_disclosed')}")
    print(f"  Shares:            {data.get('shares')}")
    print(f"  Source:            {data.get('source')}")
    print()
    print("Computed Ratios:")
    print(f"  ROE:              {compute_roe(data)}")
    print(f"  D/E:              {compute_de(data)}")
    print(f"  Div Yield:        {compute_dividend_yield(data, args.price)}")
