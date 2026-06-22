"""Feature engineering and labels for daily index forecasting.

All features are computed from information available *at the close of day t*,
and labels describe the move *into day t+horizon* — so there is no lookahead
leakage as long as we predict for t using only feature rows up to t.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# Feature column names produced by build_features (kept stable for the model).
FEATURE_COLUMNS = [
    "ret_1", "ret_2", "ret_3", "ret_5", "ret_10",
    "mom_5", "mom_10", "mom_20",
    "vol_5", "vol_10", "vol_20",
    "sma_ratio_10", "sma_ratio_20", "sma_ratio_50",
    "rsi_14",
    "hl_range", "gap",
    "vol_z_20",
    "dow",
]


def _rsi(close: pd.Series, window: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(window).mean()
    loss = (-delta.clip(upper=0)).rolling(window).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add feature columns to an OHLCV frame. Returns a copy."""
    out = df.copy()
    ret = out["close"].pct_change()

    for n in (1, 2, 3, 5, 10):
        out[f"ret_{n}"] = out["close"].pct_change(n)
    for n in (5, 10, 20):
        out[f"mom_{n}"] = ret.rolling(n).mean()
        out[f"vol_{n}"] = ret.rolling(n).std()
    for n in (10, 20, 50):
        out[f"sma_ratio_{n}"] = out["close"] / out["close"].rolling(n).mean() - 1

    out["rsi_14"] = _rsi(out["close"], 14)
    out["hl_range"] = (out["high"] - out["low"]) / out["close"]
    out["gap"] = out["open"] / out["close"].shift(1) - 1
    vol_mean = out["volume"].rolling(20).mean()
    vol_std = out["volume"].rolling(20).std()
    out["vol_z_20"] = (out["volume"] - vol_mean) / vol_std
    out["dow"] = out.index.dayofweek

    return out


def add_labels(df: pd.DataFrame, horizon: int = 1) -> pd.DataFrame:
    """Add the forward return and direction label for the given horizon.

    fwd_ret = close[t+h]/close[t] - 1 ; up = 1 if fwd_ret > 0 else 0.
    """
    out = df.copy()
    out["fwd_ret"] = out["close"].shift(-horizon) / out["close"] - 1
    out["up"] = (out["fwd_ret"] > 0).astype(int)
    return out


def make_dataset(df: pd.DataFrame, horizon: int = 1):
    """Return (features_df, frame_with_labels) cleaned of NaN rows.

    The last `horizon` rows have no label yet (future unknown) but are kept in
    `latest` so we can predict for them.
    """
    feat = build_features(df)
    labelled = add_labels(feat, horizon)
    # Rows usable for training: features present AND label present.
    train_mask = labelled[FEATURE_COLUMNS].notna().all(axis=1) & labelled["fwd_ret"].notna()
    # Latest row(s) with features but no label yet — what we actually forecast.
    latest_mask = labelled[FEATURE_COLUMNS].notna().all(axis=1) & labelled["fwd_ret"].isna()
    return labelled, train_mask, latest_mask
