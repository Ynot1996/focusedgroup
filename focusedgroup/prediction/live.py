"""On-demand forecast for an arbitrary ticker.

Unlike the pre-computed index artifacts, this trains a fresh model per request
(fetch -> features -> fit GBDT + quantiles -> predict). It reuses the offline
pipeline in ml/ so there's one definition of features/model. Heavy imports are
deferred so the app still boots on a server without the ML stack installed.

Results are cached per (symbol, day) so repeat lookups are instant.
"""

from __future__ import annotations

import datetime as dt

_CACHE: dict[tuple[str, str], dict] = {}
_MIN_ROWS = 400  # need enough history to train + hold out


def _resolve(ticker: str, market: str) -> str:
    """Map a user ticker + market to a Yahoo symbol (UK = London suffix .L)."""
    t = ticker.strip().upper()
    if market.upper() == "UK" and not t.endswith(".L") and not t.startswith("^"):
        t = f"{t}.L"
    return t


def predict_ticker(ticker: str, market: str = "US") -> dict:
    """Forecast next-session direction + range for any ticker.

    Returns {ok: True, ...forecast} or {ok: False, error: "..."}.
    """
    symbol = _resolve(ticker, market)
    today = dt.date.today().isoformat()
    cache_key = (symbol, today)
    if cache_key in _CACHE:
        return _CACHE[cache_key]

    try:
        import numpy as np  # noqa: F401  (used transitively / kept explicit)

        from ml.pipeline.data import fetch_ohlcv
        from ml.pipeline.features import FEATURE_COLUMNS, make_dataset
        from ml.pipeline.model import make_gbdt, make_quantile
    except Exception:
        return {"ok": False, "error": "Prediction engine unavailable."}

    try:
        df = fetch_ohlcv(symbol, years=12)
    except Exception:
        return {"ok": False, "error": f"Could not fetch data for “{symbol}”."}

    if df is None or len(df) < _MIN_ROWS:
        return {"ok": False, "error": f"Not enough history for “{symbol}”."}

    labelled, train_mask, latest_mask = make_dataset(df, horizon=1)
    train = labelled[train_mask]
    if len(train) < _MIN_ROWS or not latest_mask.any():
        return {"ok": False, "error": f"Not enough usable data for “{symbol}”."}

    X = train[FEATURE_COLUMNS].to_numpy()
    y = train["up"].to_numpy()
    fwd = train["fwd_ret"].to_numpy()

    # Quick honest accuracy: train on the first 80%, score the held-out 20%.
    split = int(len(X) * 0.8)
    holdout_acc = None
    if len(X) - split > 30:
        gq = make_gbdt().fit(X[:split], y[:split])
        pred = (gq.predict_proba(X[split:])[:, 1] > 0.5).astype(int)
        holdout_acc = round(float((pred == y[split:]).mean()), 4)

    gbdt = make_gbdt().fit(X, y)
    ql = make_quantile(0.1).fit(X, fwd)
    qh = make_quantile(0.9).fit(X, fwd)

    latest = labelled[latest_mask].iloc[[-1]]
    x = latest[FEATURE_COLUMNS].to_numpy()
    prob_up = float(gbdt.predict_proba(x)[0, 1])
    last_close = float(latest["close"].iloc[0])
    lo, hi = float(ql.predict(x)[0]), float(qh.predict(x)[0])

    result = {
        "ok": True,
        "symbol": symbol,
        "ticker": ticker.strip().upper(),
        "market": market.upper(),
        "as_of": latest.index[0].date().isoformat(),
        "last_close": round(last_close, 2),
        "prob_up": round(prob_up, 4),
        "direction": "up" if prob_up > 0.5 else "down",
        "confidence": round(abs(prob_up - 0.5) * 2, 4),
        "range_low": round(last_close * (1 + lo), 2),
        "range_high": round(last_close * (1 + hi), 2),
        "holdout_accuracy": holdout_acc,
        "n_days": int(len(df)),
    }
    _CACHE[cache_key] = result
    return result
