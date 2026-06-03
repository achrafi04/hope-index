"""
Aggregation layer — turns a batch of scored posts into one Hope Index point,
and persists the time series to SQLite.

Hope Index (0–100):
    mood   = engagement-weighted mean sentiment, in [-1, 1]
    hope   = clamp( 50 * (1 + alpha * mood), 0, 100 )
    volume = number of posts in the window
    intensity = volume / rolling_median(volume)   # "how loud is the nation"

We store mood, hope, volume and intensity separately so the dashboard can layer
"valence" (are they happy?) against "attention" (are they even watching?).
"""
import math
import sqlite3
import statistics
from datetime import datetime, timezone

import config


def _wclamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))


def compute_point(posts):
    """posts: list of dicts {text, sentiment, engagement, ...} -> index dict."""
    if not posts:
        return {"hope": 50.0, "mood": 0.0, "volume": 0, "intensity": 0.0}
    weights, vals = [], []
    for p in posts:
        w = math.log1p(max(p.get("engagement", 0), 0) + 1)  # dampened engagement
        weights.append(w)
        vals.append(p["sentiment"])
    mood = sum(w * v for w, v in zip(weights, vals)) / sum(weights)
    hope = _wclamp(50.0 * (1 + config.ALPHA * mood))
    return {"hope": round(hope, 2), "mood": round(mood, 4),
            "volume": len(posts), "intensity": 0.0}


# ----------------------------- storage --------------------------------
def _conn():
    c = sqlite3.connect(config.DB_PATH)
    c.execute("""CREATE TABLE IF NOT EXISTS hope(
        ts TEXT, team TEXT, hope REAL, mood REAL,
        volume INTEGER, intensity REAL,
        stat_hope REAL, belief_gap REAL)""")
    return c


def save_point(point, team, stat_hope=None):
    c = _conn()
    # intensity = volume vs rolling median of recent volumes
    rows = c.execute("SELECT volume FROM hope WHERE team=? ORDER BY ts DESC LIMIT ?",
                     (team, config.ROLLING_BASELINE)).fetchall()
    vols = [r[0] for r in rows] or [point["volume"]]
    med = statistics.median(vols) or 1
    point["intensity"] = round(point["volume"] / med, 3)
    gap = round(point["hope"] - stat_hope, 2) if stat_hope is not None else None
    c.execute("INSERT INTO hope VALUES(?,?,?,?,?,?,?,?)",
              (datetime.now(timezone.utc).isoformat(), team, point["hope"],
               point["mood"], point["volume"], point["intensity"],
               stat_hope, gap))
    c.commit()
    c.close()
    return point, gap


def load_series(team):
    c = _conn()
    rows = c.execute("SELECT ts,hope,mood,volume,intensity,stat_hope,belief_gap "
                     "FROM hope WHERE team=? ORDER BY ts", (team,)).fetchall()
    c.close()
    keys = ["ts", "hope", "mood", "volume", "intensity", "stat_hope", "belief_gap"]
    return [dict(zip(keys, r)) for r in rows]
