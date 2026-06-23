"""Prediction results, decoupled from how they're produced.

Two things live here:
  * get_charts(): pre-rendered LSTM trend PNGs under static/ (legacy showcase).
  * get_forecast()/get_metrics(): the offline ML pipeline's JSON artifacts
    (ml/artifacts/<key>/), i.e. the current probabilistic forecast and its
    walk-forward backtest. The web app only talks to this module, so how the
    numbers are produced (offline batch now, live inference later) can change
    without touching routes or templates.
"""

import json
from pathlib import Path

_ARTIFACTS = Path(__file__).resolve().parents[2] / "ml" / "artifacts"


def _read(key: str, name: str) -> dict | None:
    path = _ARTIFACTS / key / name
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def get_forecast(key: str) -> dict | None:
    """Latest probabilistic forecast for an index key (e.g. 'sp500'), or None."""
    return _read(key, "latest.json")


def get_metrics(key: str) -> dict | None:
    """Walk-forward backtest metrics for an index key, or None."""
    return _read(key, "metrics.json")

# Forecast/trend charts per index, as static filenames under static/images/.
# Keys mirror the stock blueprint endpoints (sp500 / dowjones / nasdaq).
_CHARTS = {
    "sp500": {
        "trend": "images/sp500_trend.jpg",
        "weekly": "images/sp_5.png",
        "monthly": "images/sp_20.png",
        "quarterly": "images/sp_60.png",
    },
    "dowjones": {
        "trend": "images/dowjones_trend.jpg",
        "weekly": "images/dj_5.png",
        "monthly": "images/dj_20.png",
        "quarterly": "images/dj_60.png",
    },
    "nasdaq": {
        "trend": "images/nasdaq_trend.jpg",
        "weekly": "images/nasdaq_5.png",
        "monthly": "images/nasdaq_20.png",
        "quarterly": "images/nasdaq_60.png",
    },
}


def get_charts(index: str) -> dict:
    """Return the chart image map for an index, or {} if unknown."""
    return _CHARTS.get(index, {})
