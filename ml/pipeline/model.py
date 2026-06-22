"""Model factories.

Primary direction model is a gradient-boosted tree (sklearn's
HistGradientBoosting — LightGBM-style, no extra deps). A logistic-regression
model and naive rules act as honest baselines. Quantile regressors give the
prediction range.
"""

from __future__ import annotations

from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
)
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def make_gbdt() -> HistGradientBoostingClassifier:
    """Gradient-boosted direction classifier (predicts P(up))."""
    return HistGradientBoostingClassifier(
        max_depth=3,
        learning_rate=0.05,
        max_iter=300,
        l2_regularization=1.0,
        early_stopping=True,
        validation_fraction=0.15,
        random_state=42,
    )


def make_logistic():
    """Linear baseline with standardized inputs."""
    return make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=1000, C=0.5),
    )


def make_quantile(quantile: float) -> HistGradientBoostingRegressor:
    """Quantile regressor for the forward-return band (e.g. 0.1 and 0.9)."""
    return HistGradientBoostingRegressor(
        loss="quantile",
        quantile=quantile,
        max_depth=3,
        learning_rate=0.05,
        max_iter=300,
        l2_regularization=1.0,
        random_state=42,
    )
