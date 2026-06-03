"""
Central configuration for the Hope Index pipeline.
Everything tunable lives here so collectors / NLP / aggregation stay generic.
"""

# ----------------------------------------------------------------------
# The fan base we track. Add more teams later by copying this block.
# Keywords are multilingual on purpose: FR + EN + Arabic (MSA) + Darija
# (both Arabic script and Latin/Arabizi) — this is the edge most projects miss.
# ----------------------------------------------------------------------
TARGET = {
    "code": "MAR",
    "name": "Morocco",
    "keywords": [
        # English / French
        "Morocco", "Maroc", "Atlas Lions", "Lions de l'Atlas",
        # Arabic (MSA)
        "المغرب", "أسود الأطلس", "المنتخب المغربي",
        # Darija — Latin / Arabizi (how Moroccans actually type online)
        "lmghrib", "maghrib", "dima maghrib", "dima maroc",
        "sa3d", "nsroo",  # common chants/expressions ("we'll win", "happiness")
    ],
    # Elo opponent lookups use the canonical English name from results.csv
    "elo_name": "Morocco",
}

# ----------------------------------------------------------------------
# Sources — all free. Fill credentials via environment variables (see README).
# Toggle any source off if you don't have a key yet.
# ----------------------------------------------------------------------
SOURCES = {
    "reddit":  {"enabled": False,  "subreddits": ["soccer", "Morocco", "MoroccanFootball", "worldcup"]},
    "youtube": {"enabled": True,  "max_videos": 8, "comments_per_video": 200},
    "bluesky": {"enabled": True,  "max_posts": 300},
}

# ----------------------------------------------------------------------
# Aggregation
# ----------------------------------------------------------------------
WINDOW_MINUTES = 60          # one Hope Index point per hour (drop to 5–15 on match days)
DB_PATH = "hope.db"          # SQLite time series
ROLLING_BASELINE = 24        # windows used to normalise "volume -> attention intensity"

# Hope Index shape: 50*(1+mood). mood in [-1,1] -> hope in [0,100].
# alpha sharpens/dampens how strongly valence maps to hope.
ALPHA = 1.0
