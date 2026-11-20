"""The product: dashboard tabs (/app) + the on-demand prediction API."""

from flask import Blueprint, jsonify, render_template, request

from ..news.repo import get_latest
from ..prediction.live import predict_ticker
from ..prediction.loader import (
    get_forecast,
    get_metrics,
    get_popular,
    get_series,
)

dash_bp = Blueprint("dash", __name__, url_prefix="/app")

# Indices featured across the dashboard, in display order.
INDICES = [
    ("ftse", "FTSE 100"),
    ("sp500", "S&P 500"),
    ("nasdaq", "NASDAQ"),
    ("dowjones", "Dow Jones"),
]


def _forecasts():
    out = []
    for key, label in INDICES:
        fc = get_forecast(key)
        if fc:
            out.append({**fc, "key": key, "label": label})
    return out


def _index_details():
    """Per-index data for the click-through detail modal: the forecast plus a
    recent close sparkline pulled from the chart series artifact."""
    details = {}
    for key, label in INDICES:
        fc = get_forecast(key)
        if not fc:
            continue
        spark = []
        s = get_series(key)
        if s and s.get("price", {}).get("close"):
            spark = s["price"]["close"][-60:]
        details[key] = {**fc, "label": label, "spark": spark}
    return details


@dash_bp.route("/")
def overview():
    return render_template(
        "app/overview.html",
        tab="overview",
        forecasts=_forecasts(),
        details=_index_details(),
        popular=get_popular(),
    )


@dash_bp.route("/performance")
def performance():
    series = {}
    metrics = {}
    for key, label in INDICES:
        s = get_series(key)
        if s:
            series[key] = s
        m = get_metrics(key)
        if m:
            metrics[key] = m
    return render_template(
        "app/performance.html", tab="performance",
        forecasts=_forecasts(), series=series, metrics=metrics,
    )


@dash_bp.route("/model")
def model():
    return render_template("app/model.html", tab="model")


@dash_bp.route("/news")
def news():
    return render_template("app/news.html", tab="news", news=get_latest(limit=12))


@dash_bp.route("/api/predict", methods=["POST"])
def api_predict():
    data = request.get_json(silent=True) or {}
    ticker = (data.get("ticker") or "").strip()
    market = (data.get("market") or "US").strip()
    if not ticker:
        return jsonify({"ok": False, "error": "Enter a ticker symbol."}), 400
    return jsonify(predict_ticker(ticker, market))
