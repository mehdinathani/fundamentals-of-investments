#!/usr/bin/env python3
"""Fetch historical PSX data for KSE-100 symbols from DPS portal."""

import requests
import pandas as pd
import time
import random
from bs4 import BeautifulSoup
from pathlib import Path

KSE100_SYMBOLS = [
    "ENGRO", "LUCK", "HBL", "OGDC", "MCB", "UBL", "PPL", "HUBC", "SYS", "MARI",
    "ABOT", "NML", "DGKC", "FFCL", "KAPCO", "POL", "FCCL", "EFERT", "FFBL", "NESTLE",
    "SEARL", "SHEL", "PSO", "MEBL", "BAHL", "BAFL", "FABL", "HMB", "NBP", "SCBPL",
    "SNBL", "UBL", "INDU", "GLAXO", "AGP", "HINOON", "BIFO", "COLG", "LOTCHEM",
    "EPCL", "ICI", "ASTL", "MUGHAL", "INTERNL", "AGHA", "CHCC", "POWER", "PKGS",
    "JAKCAM", "PECO", "CSAP", "EFULL", "PSX", "TREET", "KEL", "PNSC", "PIBTL",
    "AICL", "THEM", "HASCOL", "PIOC", "NCPL", "ATIL", "KOHC", "MTL", "GATI", "WTL",
]

DATA_DIR = Path("data/historical")
DATA_DIR.mkdir(parents=True, exist_ok=True)

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})

def fetch_symbol(symbol):
    try:
        resp = session.get("https://dps.psx.com.pk/historical", timeout=15)
        resp = session.post(
            "https://dps.psx.com.pk/historical",
            data={"symbol": symbol},
            timeout=30,
        )
        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table", id="historicalTable")
        if not table:
            return None

        rows = table.find_all("tr")
        data = []
        for row in rows[1:]:
            cells = row.find_all("td")
            vals = [c.get_text(strip=True) for c in cells]
            if len(vals) >= 6:
                data.append(vals)

        if not data:
            return None

        df = pd.DataFrame(data, columns=["DATE", "OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"])
        df["DATE"] = pd.to_datetime(df["DATE"], format="mixed", dayfirst=True)
        df = df.sort_values("DATE").reset_index(drop=True)
        for col in ["OPEN", "HIGH", "LOW", "CLOSE"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df["VOLUME"] = pd.to_numeric(df["VOLUME"].str.replace(",", ""), errors="coerce")
        return df
    except Exception as e:
        print(f"  {symbol}: FAILED - {e}")
        return None

for symbol in KSE100_SYMBOLS:
    path = DATA_DIR / f"{symbol}.parquet"
    if path.exists():
        print(f"  {symbol}: already cached")
        continue

    print(f"  Fetching {symbol}...", end=" ")
    df = fetch_symbol(symbol)
    if df is not None and len(df) > 0:
        df.to_parquet(path)
        print(f"{len(df)} rows ({df['DATE'].min().date()} to {df['DATE'].max().date()})")
    else:
        print("no data")
    time.sleep(random.uniform(2.5, 4.0))

print("\nDone! Saved to data/historical/")
