"""Application factory.

Builds the Flask app, wires the blueprints, and exposes the i18n helpers
(``t`` and ``lang``) to every template.
"""

import os
from pathlib import Path

from flask import Flask

from .i18n import get_lang, translate

BASE_DIR = Path(__file__).resolve().parents[1]


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )
    # Needed to store the language choice in the session.
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

    # Make translation helpers available in every template as t() and lang.
    @app.context_processor
    def inject_i18n():
        return {"t": translate, "lang": get_lang()}

    from .main.routes import main_bp
    from .stock.routes import stock_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(stock_bp)

    _seed_news_if_empty()

    return app


def _seed_news_if_empty() -> None:
    """On a fresh deploy the news DB is empty (it's gitignored, not shipped).

    Pull the latest headlines once at startup so the site isn't blank. Best
    effort — never let a news hiccup stop the app from booting.
    """
    try:
        from .news.crawler import crawl_news
        from .news.repo import get_latest, save_news

        if not get_latest(limit=1):
            save_news(crawl_news())
    except Exception:
        pass
