"""Build the live track record from each index's walk-forward metrics.

The forecast cards say "trust us, it's backtested." This turns that into a
public, running scorecard of the model's out-of-sample calls on the indices —
predict the next session, then score against what actually happened — reported
next to the naive "always up" baseline so the number means something. It reads
the per-index metrics the pipeline already wrote, so it needs no extra runs.

Headline numbers use the full out-of-sample period (a large, stable sample,
consistent with the Performance tab); the strip shows the most recent calls.

Writes ml/artifacts/track_record.json:
    {updated_at, period, overall: {...}, per_index: [...], recent: [...]}
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

ARTIFACTS = Path(__file__).resolve().parents[1] / "artifacts"

# Index key -> display label, in the order shown on the dashboard.
LABELS = [
    ("ftse", "FTSE 100"),
    ("sp500", "S&P 500"),
    ("nasdaq", "NASDAQ"),
    ("dowjones", "Dow Jones"),
]
_RECENT_PER_INDEX = 12  # recent calls per index contributed to the visual strip


def build_track_record() -> dict:
    per_index = []
    all_recent: list[dict] = []
    periods: list[str] = []
    sum_n = sum_acc = sum_base = sum_cov = 0.0

    for key, label in LABELS:
        path = ARTIFACTS / key / "metrics.json"
        if not path.exists():
            continue
        try:
            m = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            continue

        d = m.get("direction", {})
        n = m.get("n_predictions", 0)
        acc = d.get("accuracy")
        base = d.get("baseline_always_up")
        cov = m.get("range", {}).get("actual_coverage")
        if not n or acc is None:
            continue

        per_index.append({
            "key": key, "label": label, "n": n,
            "hit_rate": acc, "baseline": base, "coverage": cov,
        })
        sum_n += n
        sum_acc += acc * n
        sum_base += (base or 0) * n
        sum_cov += (cov or 0) * n
        if m.get("oos_period"):
            periods += m["oos_period"]
        for c in m.get("recent_calls", [])[-_RECENT_PER_INDEX:]:
            all_recent.append({**c, "key": key, "label": label})

    overall = None
    if sum_n:
        overall = {
            "n": int(sum_n),
            "hit_rate": round(sum_acc / sum_n, 4),
            "baseline": round(sum_base / sum_n, 4),
            "coverage": round(sum_cov / sum_n, 4),
        }

    all_recent.sort(key=lambda c: c["date"])
    payload = {
        "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "period": [min(periods), max(periods)] if periods else None,
        "overall": overall,
        "per_index": per_index,
        "recent": all_recent[-24:],  # newest last
    }
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS / "track_record.json").write_text(json.dumps(payload, indent=2))
    return payload


if __name__ == "__main__":
    tr = build_track_record()
    o = tr["overall"] or {}
    print(f"track record: {o.get('n')} calls, hit_rate={o.get('hit_rate')} "
          f"(baseline {o.get('baseline')}), coverage={o.get('coverage')}")
