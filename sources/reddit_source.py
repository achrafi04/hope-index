"""
Reddit collector (free API).

Setup: create an app at reddit.com/prefs/apps (type: 'script'), then set env vars:
    REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
Install: pip install praw

Returns normalised posts: {text, lang, engagement, ts, source}
"""
import os
import time

import config


def collect(keywords=None, limit=300):
    import praw
    kw = keywords or config.TARGET["keywords"]
    reddit = praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        user_agent=os.environ.get("REDDIT_USER_AGENT", "hope-index/0.1"),
    )
    query = " OR ".join(f'"{k}"' for k in kw[:8])  # Reddit search caps query length
    out, seen = [], set()
    for sub in config.SOURCES["reddit"]["subreddits"]:
        try:
            for c in reddit.subreddit(sub).search(query, sort="new",
                                                   time_filter="day", limit=limit):
                # title + body of submissions
                txt = f"{c.title}\n{getattr(c, 'selftext', '')}".strip()
                if c.id in seen or not txt:
                    continue
                seen.add(c.id)
                out.append({"text": txt, "lang": None,
                            "engagement": int(c.score),
                            "ts": c.created_utc, "source": f"reddit/r/{sub}"})
        except Exception as e:
            print(f"[reddit] r/{sub} skipped: {e}")
        time.sleep(1)  # be polite
    return out
