# Focused Group

A small Flask site showcasing LSTM-based stock-index forecasts (S&P 500, Dow
Jones, NASDAQ) with a business-news feed. English is the default UI language,
with a one-click switch to Chinese (中文).

Live: https://focusedgroup.onrender.com

## Architecture

The web app is decoupled from how data and predictions are produced, so the
static "showcase" version can grow into a live one without touching routes or
templates.

```
app.py                     # thin entry point: create_app() + dev server
focusedgroup/
  __init__.py              # application factory, registers blueprints + i18n
  i18n.py                  # EN/ZH translations, session-based language switch
  main/routes.py           # homepage, team page, /lang/<code> switcher
  stock/routes.py          # /stock overview, /stock/news, per-index pages
  news/
    crawler.py             # crawl_news(): fetch latest headlines (UTF-8)
    repo.py                # SQLite read/write — the only news data entry point
  prediction/loader.py     # prediction results (static charts now; live later)
ml/                        # offline LSTM training scripts + data (not deployed)
templates/                 # Jinja templates (homepage, member, FG finance/*)
static/                    # CSS/JS/images
data/news.db               # SQLite news store (generated, gitignored)
news.py                    # refresh script: crawl -> save to SQLite
```

### Clean URLs

| URL | Page |
| --- | --- |
| `/` | Homepage |
| `/team` | Team |
| `/stock/` | Market overview |
| `/stock/news` | Dynamic news |
| `/stock/sp500`, `/stock/dowjones`, `/stock/nasdaq` | Per-index pages |
| `/lang/en`, `/lang/zh` | Switch language (redirects back) |

## Run locally

```bash
pip install -r requirements.txt
python news.py        # populate data/news.db with the latest headlines
python app.py         # dev server on http://localhost:5000
```

Set `FLASK_DEBUG=1` for auto-reload. In production (see `render.yaml`) the app is
served with `gunicorn app:app`.

## Refreshing the news

`python news.py` crawls the latest business headlines and upserts them into
SQLite. To make the feed update automatically, schedule this on a cron / Render
job — `crawl_news()` and `save_news()` are plain functions ready to be called.
