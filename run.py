"""
Orchestrator — one pass = one Hope Index point.

Run it on a schedule (cron / Task Scheduler):
    every 60 min normally, every 5–15 min on Morocco match days.

    $ python run.py                      # live pass, all enabled sources
    $ python run.py --opponent Haiti     # also compute Belief Gap vs next foe
"""
from dotenv import load_dotenv
load_dotenv()
import argparse

import config
import index
import nlp
from belief_gap import current_ratings, statistical_hope


def gather():
    posts = []
    s = config.SOURCES
    if s["reddit"]["enabled"]:
        from sources import reddit_source
        posts += reddit_source.collect()
    if s["youtube"]["enabled"]:
        from sources import youtube_source
        posts += youtube_source.collect()
    if s["bluesky"]["enabled"]:
        from sources import bluesky_source
        posts += bluesky_source.collect()
    return posts


def run_pass(posts, opponent=None, neutral=True):
    """Score posts, compute Hope point, attach Belief Gap, persist."""
    for p in posts:
        p["sentiment"] = nlp.score(p["text"])
    point = index.compute_point(posts)

    stat = None
    if opponent:
        ratings = current_ratings()
        stat = statistical_hope(config.TARGET["elo_name"], opponent, ratings, neutral)

    point, gap = index.save_point(point, config.TARGET["code"], stat)

    print(f"Hope={point['hope']:>5}/100 | mood={point['mood']:+.3f} | "
          f"vol={point['volume']:>4} | intensity={point['intensity']:.2f}", end="")
    if stat is not None:
        verdict = "FAITH (crowd > model)" if gap > 0 else "DOUBT (crowd < model)"
        print(f" | stat_hope={stat} | gap={gap:+.1f}  -> {verdict}")
    else:
        print()
    return point, gap


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--opponent", default=None, help="next opponent (Elo canonical name)")
    ap.add_argument("--home", action="store_true", help="Morocco plays at home (not neutral)")
    a = ap.parse_args()
    run_pass(gather(), opponent=a.opponent, neutral=not a.home)
