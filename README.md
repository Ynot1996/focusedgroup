# Focused Group

A stock-market forecasting web app that predicts the **next-session direction**
(probability of a rise) and an **80% price range** for the major US & UK indices,
and can train a fresh model on demand for **any ticker you type in**. Built to be
honest: every number is earned by a walk-forward backtest against naive
baselines, not a cherry-picked accuracy.

**Live:** https://focusedgroup.onrender.com · Bilingual UI (English / 中文)

---

## What it does

The site opens on a splash screen and enters a four-tab dashboard at `/app`:

| Tab | What's there |
| --- | --- |
| **Overview** | Next-session forecast cards for FTSE 100, S&P 500, NASDAQ, Dow Jones (probability of up, 80% price range, last close, backtest accuracy) — plus **Predict any stock**: type a ticker, pick US/UK, and the server fetches data, trains a model, and returns a forecast live. |
| **Performance** | Four interactive charts per index: strategy equity curve vs buy & hold, model-vs-baseline accuracy, price with the predicted range, and a probability-calibration plot — each with a "Details" explanation. |
| **Model** | A pipeline diagram (data → features → model → backtest → serve), the stack, and an honest note on what the model can and can't do. |
| **News** | Live UK + US market headlines (The Guardian + MarketWatch RSS) with thumbnails. |

> **Honest by design:** daily index direction is close to unpredictable. The app
> openly reports ~54% accuracy (barely above an "always up" baseline) and shows
> the full model comparison and calibration rather than inflating the result.

---

## How the forecasting works

The **served model is a gradient-boosted tree** (scikit-learn
`HistGradientBoostingClassifier`) that outputs the probability of an up day, plus
two **quantile regressors** (`HistGradientBoostingRegressor`, q = 0.1 / 0.9) for
the 80% price range. A logistic model, an ExtraTrees model, and their soft-vote
ensemble are also trained and recorded purely for comparison.

- **Data** — daily OHLCV pulled straight from Yahoo Finance's chart endpoint
  (plain `requests`, no `yfinance` dependency).
- **Features** — 19 leakage-safe features from price/volume: lagged returns,
  momentum, rolling volatility, SMA ratios, RSI(14), high–low range, overnight
  gap, volume z-score, and day-of-week.
- **Backtest** — an **expanding-window walk-forward** (train on the past, predict
  forward, never peek) scored against two naive baselines (always-up and
  persistence), plus AUC, Brier score (calibration), a long/flat strategy vs
  buy & hold (Sharpe), and quantile coverage.
- **On-demand inference** — for an arbitrary ticker, `prediction/live.py` fetches
  ~12 years of history, trains a GBDT + quantile models on the fly (UK tickers
  get the `.L` London suffix), reports a hold-out accuracy, and caches the result
  per day. Typically ~3–6 s, which the UI covers with a step-by-step animation.

> The LSTM scripts under `ml/<index>/lstm_essence_*.py` are an **earlier
> deep-learning benchmark, kept for reference — they are not used by the live
> app.** On this task gradient-boosted trees were simpler, faster, deployable,
> and no worse, so they are what ships.

---

## Architecture

The web app is **decoupled from how predictions are produced**. Heavy work
(training + backtesting) runs offline and writes JSON artifacts; the app only
reads them. So the pre-computed index forecasts stay instant, while the same
pipeline also powers live single-ticker inference.

```
app.py                          # thin entry point: create_app() + dev server
focusedgroup/                   # Flask app (application factory + blueprints)
  __init__.py                   #   create_app(), registers blueprints + i18n,
                                #   seeds the news store on first run
  i18n.py                       #   EN/ZH translations, session-based switch
  main/routes.py                #   splash (/), team, /lang/<code>
  dash/routes.py                #   /app dashboard tabs + POST /app/api/predict
  stock/routes.py               #   legacy per-index pages (kept, unlinked)
  news/
    crawler.py                  #   crawl_news(): Guardian + MarketWatch RSS
    repo.py                     #   SQLite read/write (single data entry point)
  prediction/
    loader.py                   #   reads the offline JSON artifacts
    live.py                     #   on-demand train+predict for any ticker
ml/                             # offline ML (NOT installed on the web server*)
  pipeline/
    data.py                     #   Yahoo Finance OHLCV
    features.py                 #   leakage-safe feature engineering + labels
    model.py                    #   GBDT, logistic, ExtraTrees, ensemble, quantiles
    backtest.py                 #   walk-forward backtest + metrics
    run.py                      #   writes ml/artifacts/<index>/*.json
  <index>/lstm_essence_*.py     #   legacy LSTM benchmark (reference only)
templates/                      # Jinja: splash + app/* (base, overview, …)
static/assets/css/dashboard.css # custom design system (tokens + components)
.github/workflows/forecast.yml  # daily retrain -> commit artifacts -> redeploy
```

\* Live inference needs the ML stack, so `requirements.txt` does include
numpy/pandas/scikit-learn; the offline pipeline's deps live in
`requirements-ml.txt`.

### Routes

| Route | Purpose |
| --- | --- |
| `GET /` | Splash (enter the app) |
| `GET /app/` | Overview: index forecasts + predict-any-stock |
| `GET /app/performance` | Per-index charts |
| `GET /app/model` | Model & pipeline |
| `GET /app/news` | Market news |
| `POST /app/api/predict` | Live forecast: `{ticker, market}` → JSON |
| `GET /lang/<en\|zh>` | Switch language (session), redirect back |

---

## Tech stack

- **Backend:** Python, Flask (application factory + blueprints), gunicorn
- **ML:** scikit-learn (gradient boosting, quantile regression), pandas, numpy
- **Data/news:** Yahoo Finance chart API, RSS (stdlib `xml.etree`), SQLite
- **Frontend:** server-rendered Jinja, a hand-built CSS design system, ApexCharts, Inter
- **Ops:** GitHub Actions (daily retrain), Render (auto-deploy on push)

---

## Running locally

```bash
pip install -r requirements.txt
python news.py          # fetch the latest headlines into SQLite (optional)
python -m ml.pipeline.run   # regenerate index forecast artifacts (optional)
python app.py           # dev server on http://localhost:5000
```

Set `FLASK_DEBUG=1` for auto-reload. In production the app is served with
`gunicorn app:app` (see `render.yaml`).

## Automation

`.github/workflows/forecast.yml` reruns the pipeline on a weekday schedule,
commits the refreshed `ml/artifacts/`, and the push triggers a Render redeploy —
so the index forecasts stay current with no manual step.

---

*Educational project, not investment advice.*
