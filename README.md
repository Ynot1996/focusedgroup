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

The crawler reads The Guardian's Business RSS feed (UK-focused, free, stable).
`python news.py` crawls the latest headlines and upserts them into SQLite; the
app also seeds an empty store on startup so a fresh deploy isn't blank.

## Forecasting — how it works, and an honest read of the results

The offline pipeline (`ml/pipeline/`) forecasts the **next-session direction**
of an index as a calibrated probability, plus an 80% price range, and proves
itself with a **walk-forward backtest** (train on the past, predict forward,
never peek). Features are leakage-safe (returns, momentum, volatility, RSI, SMA
ratios, volume z-score). We serve a gradient-boosted tree (GBDT) and record a
logistic model, an ExtraTrees model and their soft-vote ensemble for comparison.

Daily directional accuracy on ~11 years out-of-sample:

| Index | GBDT | ExtraTrees | Ensemble | Always-up baseline | Strategy Sharpe vs buy & hold |
| --- | --- | --- | --- | --- | --- |
| S&P 500 | 0.539 | 0.550 | 0.548 | 0.546 | 0.76 vs 0.78 |
| Dow Jones | 0.539 | 0.542 | 0.542 | 0.545 | 0.59 vs 0.69 |
| NASDAQ | 0.552 | 0.561 | 0.559 | 0.561 | 0.74 vs 0.83 |
| FTSE 100 | 0.538 | 0.528 | 0.533 | 0.535 | 0.49 vs 0.37 |

**The honest takeaway:** no model reliably beats a naive "always up" baseline —
the gaps are within noise (~1pp on ~2,000 samples). That is expected: daily
index direction is close to unpredictable (weak-form market efficiency). The
probability signal adds risk-adjusted value only sometimes (clearly for the
FTSE: Sharpe 0.49 vs 0.37; not for US indices over this window). We publish the
full comparison and baselines rather than a cherry-picked number — the
credibility is in the honest backtest, not an inflated accuracy.

This is **educational, not investment advice.**

Run it: `pip install -r requirements-ml.txt && python -m ml.pipeline.run`. A
GitHub Action (`.github/workflows/forecast.yml`) reruns it on weekday mornings
and commits refreshed `ml/artifacts/`, which redeploys the site with the latest
forecast.
