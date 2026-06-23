"""Stock section: market overview, dynamic news, and per-index pages."""

from flask import Blueprint, render_template

from ..news.repo import get_latest
from ..prediction.loader import get_forecast, get_metrics

stock_bp = Blueprint("stock", __name__, url_prefix="/stock")


@stock_bp.route("/")
def frontpage():
    return render_template("FG finance/frontpage.html")


@stock_bp.route("/news")
def news():
    items = get_latest(limit=10)

    # The template reads rows[1..4] as [title, link, date, image_url]
    # (rows[0] used to be the CSV header). Keep that shape for now.
    rows = [["", "", "", ""]]
    rows += [[n["title"], n["link"], n["date"], n["image_url"] or ""] for n in items]

    return render_template("FG finance/frontpage(dynamic news).html", rows=rows)


def _index_page(key, template):
    return render_template(
        template, forecast=get_forecast(key), metrics=get_metrics(key)
    )


@stock_bp.route("/sp500")
def sp500():
    return _index_page("sp500", "FG finance/sp500.html")


@stock_bp.route("/dowjones")
def dowjones():
    return _index_page("dowjones", "FG finance/dowjones.html")


@stock_bp.route("/nasdaq")
def nasdaq():
    return _index_page("nasdaq", "FG finance/nasdaq.html")
