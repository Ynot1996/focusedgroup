"""Run the offline pipeline for one or more indices and write artifacts.

  python -m ml.pipeline.run            # all configured indices
  python -m ml.pipeline.run sp500      # just one

For each index key it writes ml/artifacts/<key>/{metrics.json, latest.json}:
  metrics.json  — walk-forward backtest results (the credibility numbers)
  latest.json   — the current forecast (P(up), predicted price range)
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

from .backtest import walk_forward
from .data import fetch_ohlcv
from .features import FEATURE_COLUMNS, make_dataset
from .model import make_gbdt, make_quantile

ARTIFACTS = Path(__file__).resolve().parents[1] / "artifacts"
HORIZON = 1
Q_LOW, Q_HIGH = 0.1, 0.9

# Page key -> Yahoo symbol. Keys match the stock blueprint endpoints.
SYMBOLS = {
    "sp500": "^GSPC",
    "dowjones": "^DJI",
    "nasdaq": "^IXIC",
    "ftse": "^FTSE",
}


def run_symbol(key: str, symbol: str) -> dict:
    df = fetch_ohlcv(symbol)

    # 1) Honest backtest.
    metrics = walk_forward(df, horizon=HORIZON, q_low=Q_LOW, q_high=Q_HIGH)
    metrics.update(symbol=symbol, key=key, horizon_days=HORIZON,
                   generated_at=dt.datetime.now(dt.timezone.utc).isoformat())

    # 2) Final models on all labelled data -> forecast the latest close.
    labelled, train_mask, latest_mask = make_dataset(df, horizon=HORIZON)
    train = labelled[train_mask]
    X_train = train[FEATURE_COLUMNS].to_numpy()
    y_train = train["up"].to_numpy()
    fwd_train = train["fwd_ret"].to_numpy()

    gbdt = make_gbdt().fit(X_train, y_train)
    ql = make_quantile(Q_LOW).fit(X_train, fwd_train)
    qh = make_quantile(Q_HIGH).fit(X_train, fwd_train)

    latest = labelled[latest_mask].iloc[[-1]]
    x = latest[FEATURE_COLUMNS].to_numpy()
    prob_up = float(gbdt.predict_proba(x)[0, 1])
    last_close = float(latest["close"].iloc[0])
    lo_ret, hi_ret = float(ql.predict(x)[0]), float(qh.predict(x)[0])

    forecast = {
        "symbol": symbol,
        "key": key,
        "as_of": latest.index[0].date().isoformat(),
        "horizon_days": HORIZON,
        "last_close": round(last_close, 2),
        "prob_up": round(prob_up, 4),
        "direction": "up" if prob_up > 0.5 else "down",
        "confidence": round(abs(prob_up - 0.5) * 2, 4),
        "range_low": round(last_close * (1 + lo_ret), 2),
        "range_high": round(last_close * (1 + hi_ret), 2),
        "range_coverage": Q_HIGH - Q_LOW,
        "backtest_accuracy": metrics["direction"]["accuracy"],
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }

    out_dir = ARTIFACTS / key
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    (out_dir / "latest.json").write_text(json.dumps(forecast, indent=2))
    return forecast


def main(keys: list[str] | None = None) -> None:
    keys = keys or list(SYMBOLS)
    for key in keys:
        symbol = SYMBOLS[key]
        print(f"--- {key} ({symbol}) ---")
        fc = run_symbol(key, symbol)
        print(f"  P(up)={fc['prob_up']}  dir={fc['direction']}  "
              f"close={fc['last_close']}  range=[{fc['range_low']}, {fc['range_high']}]  "
              f"backtest_acc={fc['backtest_accuracy']}")


if __name__ == "__main__":
    main(sys.argv[1:] or None)
