"""Main site: homepage, team page, and the language switcher."""

from flask import Blueprint, redirect, render_template, request, session, url_for

from ..i18n import SUPPORTED_LANGS

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    # Landing splash; clicking through enters the dashboard at /app.
    return render_template("splash.html")


@main_bp.route("/team")
def team():
    return render_template("member.html")


@main_bp.route("/lang/<lang>")
def set_language(lang):
    """Switch the active language and return to the page the user came from."""
    if lang in SUPPORTED_LANGS:
        session["lang"] = lang
    return redirect(request.referrer or url_for("main.home"))
