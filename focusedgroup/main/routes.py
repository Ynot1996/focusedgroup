"""Main site: homepage, team page, and the language switcher."""

from flask import Blueprint, redirect, render_template, request, session, url_for

from ..i18n import SUPPORTED_LANGS
from ..news.repo import get_latest
from ..prediction.loader import get_forecast, get_series

# Indices featured on the homepage forecast band, in display order.
_HOME_INDICES = [
    ("ftse", "FTSE 100"),
    ("sp500", "S&P 500"),
    ("nasdaq", "NASDAQ"),
    ("dowjones", "Dow Jones"),
]

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    forecasts = []
    series = {}
    for key, label in _HOME_INDICES:
        fc = get_forecast(key)
        if fc:
            forecasts.append({**fc, "key": key, "label": label})
        s = get_series(key)
        if s:
            series[key] = s
    news = get_latest(limit=8)
    return render_template(
        "homepage.html", forecasts=forecasts, series=series, news=news
    )


@main_bp.route("/team")
def team():
    return render_template("member.html")


@main_bp.route("/lang/<lang>")
def set_language(lang):
    """Switch the active language and return to the page the user came from."""
    if lang in SUPPORTED_LANGS:
        session["lang"] = lang
    return redirect(request.referrer or url_for("main.home"))
