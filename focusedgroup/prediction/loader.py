"""Prediction results, decoupled from how they're produced.

Right now this returns pre-rendered chart images (mode A: the LSTM training in
``ml/`` is run offline and its output PNGs live under static/). The web app only
talks to this module, so swapping to live inference later (mode B: load a saved
model and predict on request) means changing only this file — routes and
templates stay the same.
"""

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
