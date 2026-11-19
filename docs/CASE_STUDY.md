# Focused Group — case study

How this project evolved from a first university team project into a small,
honest ML product. Written as background for a portfolio; the codebase and git
history are the primary record.

## TL;DR

A finance site that began as an LSTM "stock predictor" was rebuilt into an
**honest forecasting product**: gradient-boosted trees, a leakage-safe
walk-forward backtest, and on-demand inference for any ticker — with the results
framed truthfully (daily direction is ~54% accurate, barely above baseline)
instead of overclaimed. The engineering grew alongside it: an application
factory with blueprints, an offline-vs-online split, bilingual UI, a hand-built
design system, and a daily auto-retrain pipeline.

## Phases

### 1. Origin — a first formal team project
A 5-person university team built a Flask finance site: LSTM forecasts for NASDAQ
/ S&P / Dow (exported from Colab), a business-news crawler, and an HTML template.
As a first real project it carried the usual debt — a one-shot crawler with
broken encoding, no `.gitignore`, notebook-dump model scripts, and URLs that
leaked the folder structure.

### 2. Make it an engineered app
Refactored into a Flask **application factory + blueprints**, moved news into
**SQLite** behind a single repository module, rewrote the crawler as a proper
function with correct UTF-8, added clean URLs and **EN/ZH i18n**, and deployed to
Render.

### 3. The honest-ML pivot (the key decision)
"Predicting stock prices" isn't a credible goal — markets are near-efficient.
The project was re-framed around what ML *can* honestly do: a **calibrated
probability of the next session being up**, plus an 80% price range, proven by a
**walk-forward backtest** against naive baselines (always-up, persistence) with
AUC, Brier calibration, and a strategy-vs-buy-&-hold Sharpe.

An **LSTM was benchmarked against gradient-boosted trees**. On this task GBDT was
simpler, faster, deployable, and no worse — so GBDT was chosen to ship, and the
LSTM scripts were kept only as a reference benchmark. Reporting the honest ~54%
(and showing the full model comparison) became the project's point of
differentiation.

### 4. From page to product
Rebuilt the single page into a multi-tab dashboard: a splash entry, an
**Overview** with the index forecasts and a **"predict any stock"** tool that
trains a model live for any US/UK ticker, a **Performance** tab with four
interactive charts, a **Model** tab with the pipeline, and live **News**. The web
app stays thin by reading pre-computed JSON artifacts; a **GitHub Actions** job
retrains daily and triggers a redeploy.

### 5. Design & polish
Several design passes: a dark, custom **design system** (CSS tokens + components)
replacing the stitched-together template; a palette fix to drop green in favour
of a gold accent with **red-for-up** (Taiwan convention); and a news-image fix by
switching the US source to a feed (MarketWatch) whose RSS actually carries
thumbnails.

## What changed, honestly

- **Model:** LSTM → gradient-boosted trees (served); LSTM kept as a benchmark.
- **Claim:** "predict prices" → calibrated probability + range, with an honest,
  baseline-relative accuracy.
- **Shape:** static template → decoupled app (offline pipeline → artifacts →
  thin Flask app) with live inference and daily retraining.

## Lessons

- Pick the model the **evidence** supports, not the fashionable one.
- In a domain where the honest answer is "mostly unpredictable," **rigorous
  evaluation and transparency** are the real deliverable.
- Decoupling training from serving keeps a data product both cheap to run and
  able to grow.
