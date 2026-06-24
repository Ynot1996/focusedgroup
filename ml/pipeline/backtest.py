"""Walk-forward backtest — the honest core of the project.

We never let the model see the future: at each step we train on everything up to
day t and predict day t+horizon, walking forward through history. The resulting
out-of-sample predictions are scored against naive baselines so the headline
"accuracy" actually means something.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, roc_auc_score

from .features import FEATURE_COLUMNS, make_dataset
from .model import make_ensemble, make_quantile

TRADING_DAYS = 252


def _annualized_sharpe(daily_returns: np.ndarray) -> float:
    r = daily_returns[~np.isnan(daily_returns)]
    if r.std() == 0 or len(r) == 0:
        return 0.0
    return float(np.sqrt(TRADING_DAYS) * r.mean() / r.std())


def walk_forward(
    df: pd.DataFrame,
    horizon: int = 1,
    initial_train: int = 1000,
    step: int = 21,
    q_low: float = 0.1,
    q_high: float = 0.9,
) -> dict:
    """Run the expanding-window backtest and return metrics + arrays."""
    labelled, train_mask, _ = make_dataset(df, horizon)
    usable = labelled[train_mask].copy()
    X = usable[FEATURE_COLUMNS].to_numpy()
    y = usable["up"].to_numpy()
    fwd = usable["fwd_ret"].to_numpy()
    n = len(usable)

    rows = []  # (idx, prob_up, y, fwd_ret, q_lo, q_hi)
    component_probs: dict[str, list] = {}
    i = initial_train
    while i < n:
        end = min(i + step, n)
        ens = make_ensemble().fit(X[:i], y[:i])
        ql = make_quantile(q_low).fit(X[:i], fwd[:i])
        qh = make_quantile(q_high).fit(X[:i], fwd[:i])

        # GBDT is the served model (best in backtest); we still record the
        # other components and the soft-vote ensemble for an honest comparison.
        proba = ens.named_estimators_["gbdt"].predict_proba(X[i:end])[:, 1]
        lo = ql.predict(X[i:end])
        hi = qh.predict(X[i:end])
        # Per-component probabilities, to compare each model vs the ensemble.
        for name, est in ens.named_estimators_.items():
            component_probs.setdefault(name, []).extend(est.predict_proba(X[i:end])[:, 1])
        for k in range(end - i):
            rows.append((i + k, proba[k], y[i + k], fwd[i + k], lo[k], hi[k]))
        i = end

    res = pd.DataFrame(rows, columns=["idx", "prob_up", "y", "fwd_ret", "q_lo", "q_hi"])
    pred_up = (res["prob_up"] > 0.5).astype(int)
    y_arr = res["y"].to_numpy()

    def _acc(probs) -> float:
        return round(float(((np.asarray(probs) > 0.5).astype(int) == y_arr).mean()), 4)

    # Per-model accuracy + the soft-vote ensemble (mean of component probs).
    model_comparison = {name: _acc(p) for name, p in component_probs.items()}
    ensemble_avg = np.mean([component_probs[n] for n in component_probs], axis=0)
    model_comparison["ensemble"] = _acc(ensemble_avg)

    # --- direction metrics ---
    acc = float((pred_up == res["y"]).mean())
    base_rate = float(res["y"].mean())  # always-predict-up accuracy
    always_up_acc = max(base_rate, 1 - base_rate)
    # persistence: predict tomorrow's direction = today's realized 1-day sign
    realized_today = (usable["close"].pct_change() > 0).astype(int).to_numpy()
    persist_pred = realized_today[res["idx"].to_numpy()]
    persist_acc = float((persist_pred == res["y"].to_numpy()).mean())
    auc = float(roc_auc_score(res["y"], res["prob_up"])) if res["y"].nunique() > 1 else float("nan")
    brier = float(brier_score_loss(res["y"], res["prob_up"]))

    # --- simple strategy: long when prob_up > 0.5, else flat (1-day horizon) ---
    position = (res["prob_up"] > 0.5).astype(int).to_numpy()
    strat_daily = position * res["fwd_ret"].to_numpy()
    bh_daily = res["fwd_ret"].to_numpy()
    strat_total = float(np.nanprod(1 + strat_daily) - 1)
    bh_total = float(np.nanprod(1 + bh_daily) - 1)

    # --- range coverage (should be ~ q_high - q_low = 80%) ---
    inside = (res["fwd_ret"] >= res["q_lo"]) & (res["fwd_ret"] <= res["q_hi"])
    coverage = float(inside.mean())

    # --- chart series (downsampled) for the homepage dashboard ---
    eq_model = np.cumprod(1 + np.nan_to_num(strat_daily))
    eq_bh = np.cumprod(1 + np.nan_to_num(bh_daily))
    dates_oos = [usable.index[idx].date().isoformat() for idx in res["idx"].to_numpy()]
    stepd = max(1, len(eq_model) // 200)
    equity = {
        "dates": dates_oos[::stepd],
        "model": [round(float(v), 4) for v in eq_model[::stepd]],
        "buyhold": [round(float(v), 4) for v in eq_bh[::stepd]],
    }
    # Reliability: equal-count bins of predicted prob vs realized up-rate.
    order = np.argsort(res["prob_up"].to_numpy())
    p_sorted = res["prob_up"].to_numpy()[order]
    y_sorted = y_arr[order]
    n_bins = 8
    bin_sz = max(1, len(p_sorted) // n_bins)
    calibration = []
    for b in range(n_bins):
        s = b * bin_sz
        e = (b + 1) * bin_sz if b < n_bins - 1 else len(p_sorted)
        if e > s:
            calibration.append({
                "p_pred": round(float(p_sorted[s:e].mean()), 4),
                "p_actual": round(float(y_sorted[s:e].mean()), 4),
                "n": int(e - s),
            })

    return {
        "charts": {"equity": equity, "calibration": calibration},
        "n_predictions": int(len(res)),
        "oos_period": [
            usable.index[res["idx"].iloc[0]].date().isoformat(),
            usable.index[res["idx"].iloc[-1]].date().isoformat(),
        ],
        "direction": {
            "accuracy": round(acc, 4),
            "served_model": "gbdt",
            "model_comparison": model_comparison,
            "baseline_always_up": round(always_up_acc, 4),
            "baseline_persistence": round(persist_acc, 4),
            "auc": round(auc, 4),
            "brier": round(brier, 4),
        },
        "strategy_1d": {
            "model_total_return": round(strat_total, 4),
            "buy_hold_total_return": round(bh_total, 4),
            "model_sharpe": round(_annualized_sharpe(strat_daily), 3),
            "buy_hold_sharpe": round(_annualized_sharpe(bh_daily), 3),
        },
        "range": {
            "target_coverage": q_high - q_low,
            "actual_coverage": round(coverage, 4),
        },
    }
