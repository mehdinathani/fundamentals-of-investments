import requests
import pandas as pd
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime, date
from pathlib import Path
from scripts.macros import (
    DPS_BASE_URL, DPS_HEADERS, DPS_DELAY_MIN, DPS_DELAY_MAX,
    DPS_RETRIES, DPS_TIMEOUT, HISTORICAL_DIR, STALE_DATA_DAYS,
)

_session = requests.Session()
_session.headers.update(DPS_HEADERS)
_last_request = 0.0

def _rate_limit():
    global _last_request
    now = time.time()
    elapsed = now - _last_request
    delay = random.uniform(DPS_DELAY_MIN, DPS_DELAY_MAX)
    if elapsed < delay:
        time.sleep(delay - elapsed)
    _last_request = time.time()

def _request(method, url, **kwargs):
    for attempt in range(DPS_RETRIES):
        _rate_limit()
        try:
            resp = _session.request(method, url, timeout=DPS_TIMEOUT, **kwargs)
            resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException as e:
            if attempt == DPS_RETRIES - 1:
                raise
            time.sleep(2 ** attempt)

def get_market_watch():
    url = f"{DPS_BASE_URL}/market-watch"
    resp = _request("GET", url)
    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table")
    if not table:
        return pd.DataFrame()
    rows = table.find_all("tr")
    if not rows:
        return pd.DataFrame()
    headers = [h.get_text(strip=True) for h in rows[0].find_all("th")]
    data = []
    for row in rows[1:]:
        cells = row.find_all("td")
        vals = [c.get_text(strip=True) for c in cells]
        if len(vals) >= len(headers):
            data.append(vals[:len(headers)])
    df = pd.DataFrame(data, columns=headers)
    for col in ["LDCP", "OPEN", "HIGH", "LOW", "CURRENT"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "VOLUME" in df.columns:
        df["VOLUME"] = pd.to_numeric(
            df["VOLUME"].str.replace(",", ""), errors="coerce"
        )
    if "CHANGE (%)" in df.columns:
        df["CHANGE (%)"] = pd.to_numeric(
            df["CHANGE (%)"].str.replace("%", ""), errors="coerce"
        )
    if "CHANGE" in df.columns:
        df["CHANGE"] = pd.to_numeric(df["CHANGE"], errors="coerce")
    return df

def get_historical_data(symbol, use_cache=True):
    symbol = symbol.upper()
    cache_path = HISTORICAL_DIR / f"{symbol}.parquet"
    if use_cache and cache_path.exists():
        df = pd.read_parquet(cache_path)
        max_date = df["DATE"].max()
        age_days = (date.today() - max_date.date()).days
        if age_days < STALE_DATA_DAYS:
            return df
    url = f"{DPS_BASE_URL}/historical"
    resp = _request("GET", url)
    resp = _request("POST", url, data={"symbol": symbol})
    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table", id="historicalTable")
    if not table:
        return _load_from_cache_or_empty(cache_path)
    rows = table.find_all("tr")
    data = []
    for row in rows[1:]:
        cells = row.find_all("td")
        vals = [c.get_text(strip=True) for c in cells]
        if len(vals) >= 6:
            data.append(vals)
    if not data:
        return _load_from_cache_or_empty(cache_path)
    df = pd.DataFrame(
        data, columns=["DATE", "OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]
    )
    df["DATE"] = pd.to_datetime(df["DATE"], format="mixed", dayfirst=True)
    df = df.sort_values("DATE").reset_index(drop=True)
    for col in ["OPEN", "HIGH", "LOW", "CLOSE"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["VOLUME"] = pd.to_numeric(
        df["VOLUME"].astype(str).str.replace(",", ""), errors="coerce"
    )
    HISTORICAL_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cache_path)
    return df

def _load_from_cache_or_empty(cache_path):
    if cache_path.exists():
        return pd.read_parquet(cache_path)
    return pd.DataFrame()

def get_index_constituents(index="KSE100"):
    url = f"{DPS_BASE_URL}/index/{index.lower()}"
    try:
        resp = _request("GET", url)
        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table")
        if not table:
            return []
        rows = table.find_all("tr")[1:]
        symbols = []
        for row in rows:
            cells = row.find_all("td")
            if cells:
                symbols.append(cells[0].get_text(strip=True))
        return symbols
    except Exception:
        return []

def get_company_info(symbol):
    symbol = symbol.upper()
    url = f"{DPS_BASE_URL}/company/{symbol}"
    try:
        resp = _request("GET", url)
        soup = BeautifulSoup(resp.text, "html.parser")
        info = {"symbol": symbol}
        rows = soup.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True).rstrip(":")
                val = cells[1].get_text(strip=True)
                info[key] = val
        return info
    except Exception:
        return {"symbol": symbol}

def get_financial_data(symbol, statement="balance-sheet"):
    symbol = symbol.upper()
    url = f"{DPS_BASE_URL}/financials"
    try:
        resp = _request("POST", url, data={"symbol": symbol})
        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table", id="financialTable")
        if not table:
            return pd.DataFrame()
        rows = table.find_all("tr")
        if not rows:
            return pd.DataFrame()
        headers = [h.get_text(strip=True) for h in rows[0].find_all("th")]
        data = []
        for row in rows[1:]:
            cells = row.find_all("td")
            vals = [c.get_text(strip=True) for c in cells]
            if len(vals) >= len(headers):
                data.append(vals[:len(headers)])
        return pd.DataFrame(data, columns=headers)
    except Exception:
        return pd.DataFrame()

def list_cached_symbols():
    if not HISTORICAL_DIR.exists():
        return []
    return sorted(
        p.stem for p in HISTORICAL_DIR.glob("*.parquet")
    )
