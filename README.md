# The Hope Index 🇲🇦

> Can we measure a nation's hope during the World Cup — and tell when its heart drifts from the math?

A real-time pipeline that tracks the **emotional hope** of a fan base (Morocco) from
free social sources, and contrasts it against the **statistical hope** from an Elo model.
The story lives in the gap between the two.

```
   FAITH zone  ┃   ╭─emotional hope (social)
        ▲      ┃  ╱
        │      ┃ ╱      ← Belief Gap = the whole point
   ─────┼──────╋╱──────────────────────  statistical hope (Elo)
        │      ┃
   DOUBT zone  ┃
               └── time → (per match, per hour)
```

## Why this design

- **No paid APIs.** X (Twitter) went pay-per-use in 2026 — out. We use **Reddit**,
  **YouTube comments**, and **Bluesky** (open, free, real-time). All free.
- **Multilingual on purpose.** YouTube comments + Bluesky give us Arabic / Darija /
  French / English reactions on the *same* match. The Darija angle is the edge —
  it's an underserved NLP space and it's authentically yours.
- **Reuses the Miracle Index engine.** The same Elo that ranked history's biggest
  upsets now produces the "cold head" axis. Nothing is wasted.

## Architecture

```
config.py              # teams, multilingual keywords, source toggles, window size
sources/
  reddit_source.py     # PRAW            (free app credentials)
  youtube_source.py    # Data API v3     (free 10k units/day)
  bluesky_source.py    # AT Protocol     (free app password) — the live spike detector
nlp.py                 # XLM-R multilingual sentiment -> valence [-1,1] (+ offline fallback)
index.py               # Hope Index formula + SQLite time series
belief_gap.py          # Elo statistical-hope axis (reused) + the gap
run.py                 # one pass = one Hope Index point (schedule it)
demo.py                # offline proof — runs with no keys, no internet
results.csv            # international match history (Elo input)
```

**Hope Index (0–100):** `hope = clamp(50 * (1 + mood))`, where `mood` is the
engagement-weighted mean sentiment. Volume is tracked separately as *attention
intensity* (how loud the nation is, vs its rolling baseline).

**Belief Gap:** `emotional_hope − statistical_hope`. Positive = the crowd believes
more than the model (faith); negative = more pessimistic than the model (doubt).

## Quick start

```bash
pip install pandas transformers torch praw google-api-python-client atproto

# 1) prove the brain with zero setup:
python demo.py

# 2) free credentials (env vars):
export REDDIT_CLIENT_ID=...      REDDIT_CLIENT_SECRET=...   REDDIT_USER_AGENT=hope-index/0.1
export YOUTUBE_API_KEY=...
export BSKY_HANDLE=you.bsky.social   BSKY_APP_PASSWORD=...

# 3) one live pass (also computes the gap vs your next opponent):
python run.py --opponent Haiti
```

Schedule `run.py` every 60 min (every 5–15 min on match days) via cron. Each pass
appends one point to `hope.db`.

## Roadmap

1. **Now → June 11:** get keys, run `run.py` on pre-tournament chatter so the
   pipeline is battle-tested before kickoff. Tune `ALPHA` and window size.
2. **During the cup:** dense windows on Morocco match days; the emotional curve vs
   the Elo line is your content.
3. **The research edge:** fine-tune a Darija sentiment model (base: `DarijaBERT`)
   to replace XLM-R on Darija text — this is what makes the project publishable, not
   just a portfolio piece.
4. **Dashboard:** a single HTML page reading `hope.db` — emotional curve, Elo line,
   shaded Belief Gap, per-match annotations. (Same broadcast aesthetic as the
   Miracle Index page.)

---
*Built on the road to FIFA World Cup 2026. Companion to The Miracle Index.*
