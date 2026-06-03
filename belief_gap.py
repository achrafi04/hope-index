"""
The "cold head" axis — statistical hope from our Elo engine (reused from the
Miracle Index). For an upcoming Morocco match we compute the Elo win expectation
and map it to 0–100. The Belief Gap = emotional hope (social) − statistical hope.

    gap > 0  -> the nation believes MORE than the model  ("faith")
    gap < 0  -> the nation is more pessimistic than the model

This is the whole point of the project: the story lives in the gap, not the curve.
"""
import pandas as pd

HOME_ADV = 100.0
DEFAULT = 1500.0


def _k(t):
    t = t.lower()
    if "world cup" in t and "qualif" not in t:
        return 60.0
    if any(x in t for x in ["qualif", "euro", "copa", "african", "asian",
                            "confederations", "nations league", "gold cup"]):
        return 40.0
    if "friendly" in t:
        return 20.0
    return 30.0


def _gd(gd):
    gd = abs(gd)
    return 1.0 if gd <= 1 else (1.5 if gd == 2 else (11.0 + gd) / 8.0)


def current_ratings(csv="results.csv"):
    """Build Elo ratings chronologically over all played internationals."""
    df = pd.read_csv(csv)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df = df.dropna(subset=["home_score", "away_score"])
    r = {}
    for x in df.itertuples(index=False):
        rh, ra = r.get(x.home_team, DEFAULT), r.get(x.away_team, DEFAULT)
        adv = 0.0 if str(x.neutral).upper() == "TRUE" else HOME_ADV
        eh = 1 / (1 + 10 ** ((ra - rh - adv) / 400))
        sh = 1.0 if x.home_score > x.away_score else (0.5 if x.home_score == x.away_score else 0.0)
        k, g = _k(x.tournament), _gd(x.home_score - x.away_score)
        r[x.home_team] = rh + k * g * (sh - eh)
        r[x.away_team] = ra + k * g * ((1 - sh) - (1 - eh))
    return r


def statistical_hope(team, opponent, ratings, neutral=True):
    """Elo win expectation for `team` vs `opponent`, mapped to 0–100."""
    rt = ratings.get(team, DEFAULT)
    ro = ratings.get(opponent, DEFAULT)
    adv = 0.0 if neutral else HOME_ADV
    e = 1 / (1 + 10 ** ((ro - rt - adv) / 400))
    return round(e * 100, 1)
