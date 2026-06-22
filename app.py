from flask import Flask, render_template, url_for

from focusedgroup.news.repo import get_latest

app = Flask(__name__)
app.static_folder = 'static'


@app.route("/")
def homepage():

    return render_template("homepage.html")


@app.route("/member.html")
def member():

    return render_template("member.html")


@app.route("/stock/templates/frontpage.html")
def frontpage():

    return render_template("FG finance/frontpage.html")


@app.route("/stock/templates/frontpage(dynamic news).html")
def frontpage_dynamic_news():

    news = get_latest(limit=10)

    # The template reads rows[1..4] as [title, link, date, image_url] (rows[0]
    # used to be the CSV header). Keep that shape so the template is untouched
    # for now; it gets cleaned up to a loop in the blueprint refactor.
    rows = [["", "", "", ""]]
    rows += [[n["title"], n["link"], n["date"], n["image_url"] or ""] for n in news]

    return render_template("FG finance/frontpage(dynamic news).html", rows=rows)


@app.route("/homepage.html")
def tohomepage():

    return render_template("homepage.html")


@app.route("/stock/templates/sp500.html")
def sp500():

    return render_template("FG finance/sp500.html")


@app.route("/stock/templates/dowjones.html")
def dowjones():

    return render_template("FG finance/dowjones.html")


@app.route("/stock/templates/nasdaq.html")
def nasdaq():

    return render_template("FG finance/nasdaq.html")


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
