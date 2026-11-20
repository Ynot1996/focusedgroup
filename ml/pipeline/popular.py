"""Pre-compute today's forecast for a watchlist of widely-followed stocks.

The overview page shows these so a visitor sees real, actionable output without
having to type a ticker — the same model that powers on-demand prediction, just
run ahead of time and cached as an artifact. Refreshed by the daily job.

Writes ml/artifacts/popular.json:
    {generated_at, items: [{ticker, name, as_of, last_close, prob_up,
                            direction, confidence, range_low, range_high,
                            holdout_accuracy, spark: [...closes]}]}
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from .data import fetch_ohlcv
from .features import FEATURE_COLUMNS, make_dataset
from .model import make_gbdt, make_quantile

ARTIFACTS = Path(__file__).resolve().parents[1] / "artifacts"
_MIN_ROWS = 400
_SPARK_POINTS = 40

# Widely-searched US large caps. Ticker -> display name. Eight keeps the grid
# tidy (two rows of four) and the daily job quick.
POPULAR: list[tuple[str, str]] = [
    ("AAPL", "Apple"),
    ("NVDA", "NVIDIA"),
    ("TSLA", "Tesla"),
    ("MSFT", "Microsoft"),
    ("AMZN", "Amazon"),
    ("GOOGL", "Alphabet"),
    ("META", "Meta"),
    ("AMD", "AMD"),
]


def _forecast(symbol: str, name: str) -> dict | None:
    """Train a fresh model on ~12y of history and forecast the next session.

    Returns the forecast dict, or None if the symbol can't be modelled.
    """
    df = fetch_ohlcv(symbol, years=12)
    if df is None or len(df) < _MIN_ROWS:
        return None

    labelled, train_mask, latest_mask = make_dataset(df, horizon=1)
    train = labelled[train_mask]
    if len(train) < _MIN_ROWS or not latest_mask.any():
        return None

    X = train[FEATURE_COLUMNS].to_numpy()
    y = train["up"].to_numpy()
    fwd = train["fwd_ret"].to_numpy()

    # Honest hold-out accuracy: train on the first 80%, score the last 20%.
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

    spark = [round(float(c), 2) for c in df["close"].tail(_SPARK_POINTS)]

    return {
        "ticker": symbol,
        "name": name,
        "as_of": latest.index[0].date().isoformat(),
        "last_close": round(last_close, 2),
        "prob_up": round(prob_up, 4),
        "direction": "up" if prob_up > 0.5 else "down",
        "confidence": round(abs(prob_up - 0.5) * 2, 4),
        "range_low": round(last_close * (1 + lo), 2),
        "range_high": round(last_close * (1 + hi), 2),
        "holdout_accuracy": holdout_acc,
        "spark": spark,
    }


def build_popular() -> dict:
    """Compute every watchlist forecast and write the artifact. Best-effort:
    a single failing ticker is skipped, not fatal."""
    items = []
    for symbol, name in POPULAR:
        try:
            fc = _forecast(symbol, name)
        except Exception as exc:  # noqa: BLE001 - one bad ticker shouldn't stop the batch
            print(f"  ! {symbol}: {exc}")
            fc = None
        if fc:
            items.append(fc)
            print(f"  {symbol:6} P(up)={fc['prob_up']:.3f} dir={fc['direction']}")

    payload = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "as_of": items[0]["as_of"] if items else None,
        "items": items,
    }
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS / "popular.json").write_text(json.dumps(payload, indent=2))
    return payload


if __name__ == "__main__":
    build_popular()
