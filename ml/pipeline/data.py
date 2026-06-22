"""Market data ingestion.

Pulls daily OHLCV from Yahoo Finance's public chart endpoint (no extra deps;
reuses ``requests``). Default symbol is the FTSE 100 index (^FTSE).
"""

from __future__ import annotations

import datetime as dt

import pandas as pd
import requests

CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
DEFAULT_SYMBOL = "^FTSE"


def fetch_ohlcv(symbol: str = DEFAULT_SYMBOL, years: int = 15) -> pd.DataFrame:
    """Return a daily OHLCV DataFrame indexed by date, oldest first.

    Columns: open, high, low, close, volume.
    """
    period2 = int(dt.datetime.now().timestamp())
    period1 = int((dt.datetime.now() - dt.timedelta(days=365 * years)).timestamp())
    params = {
        "period1": period1,
        "period2": period2,
        "interval": "1d",
        "events": "div,splits",
    }
    resp = requests.get(
        CHART_URL.format(symbol=requests.utils.quote(symbol)),
        params=params,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30,
    )
    resp.raise_for_status()
    result = resp.json()["chart"]["result"][0]

    timestamps = result["timestamp"]
    quote = result["indicators"]["quote"][0]
    df = pd.DataFrame(
        {
            "open": quote["open"],
            "high": quote["high"],
            "low": quote["low"],
            "close": quote["close"],
            "volume": quote["volume"],
        },
        index=pd.to_datetime(timestamps, unit="s").normalize(),
    )
    df.index.name = "date"
    # Drop rows with no close (holidays / bad ticks) and de-duplicate.
    df = df[df["close"].notna()]
    df = df[~df.index.duplicated(keep="last")].sort_index()
    return df


if __name__ == "__main__":
    d = fetch_ohlcv()
    print(f"{DEFAULT_SYMBOL}: {len(d)} rows, {d.index[0].date()} -> {d.index[-1].date()}")
    print(d.tail())
