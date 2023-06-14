import csv
from flask import Flask, render_template, url_for

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

    with open("news.csv", "r", encoding="big5") as f:
        data = f.readlines()

    rows = [row.strip().split(",") for row in data]

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
    app.run(host="0.0.0.0", debug=True)
