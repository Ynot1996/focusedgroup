"""Run the full offline pipeline and write artifacts the web app serves.

  python -m ml.pipeline.run

Produces under ml/artifacts/:
  metrics.json  — walk-forward backtest results (the credibility numbers)
  latest.json   — the current forecast (P(up), predicted price range)
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from .backtest import walk_forward
from .data import DEFAULT_SYMBOL, fetch_ohlcv
from .features import FEATURE_COLUMNS, make_dataset
from .model import make_gbdt, make_quantile

ARTIFACTS = Path(__file__).resolve().parents[1] / "artifacts"
HORIZON = 1
Q_LOW, Q_HIGH = 0.1, 0.9


def main(symbol: str = DEFAULT_SYMBOL) -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    df = fetch_ohlcv(symbol)

    # 1) Honest backtest.
    metrics = walk_forward(df, horizon=HORIZON, q_low=Q_LOW, q_high=Q_HIGH)
    metrics["symbol"] = symbol
    metrics["horizon_days"] = HORIZON
    metrics["generated_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    (ARTIFACTS / "metrics.json").write_text(json.dumps(metrics, indent=2))

    # 2) Final models on all labelled data -> forecast the latest close.
    labelled, train_mask, latest_mask = make_dataset(df, horizon=HORIZON)
    train = labelled[train_mask]
    X_train, y_train, fwd_train = (
        train[FEATURE_COLUMNS].to_numpy(),
        train["up"].to_numpy(),
        train["fwd_ret"].to_numpy(),
    )
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
    (ARTIFACTS / "latest.json").write_text(json.dumps(forecast, indent=2))

    print("=== Backtest ===")
    print(json.dumps(metrics["direction"], indent=2))
    print(json.dumps(metrics["strategy_1d"], indent=2))
    print(json.dumps(metrics["range"], indent=2))
    print("=== Latest forecast ===")
    print(json.dumps(forecast, indent=2))


if __name__ == "__main__":
    main()
