"""
Bluesky collector (AT Protocol — free, open, real-time).

This is the live spike detector: open firehose / search, no paid tier, no gatekeeping.
Setup: create a free Bluesky account + an app password (Settings -> App Passwords), set:
    BSKY_HANDLE, BSKY_APP_PASSWORD
Install: pip install atproto

Returns normalised posts: {text, lang, engagement, ts, source}
"""
import os
from datetime import datetime, timezone

import config


def collect(keywords=None, max_posts=None):
    from atproto import Client
    kw = keywords or config.TARGET["keywords"]
    limit = max_posts or config.SOURCES["bluesky"]["max_posts"]

    client = Client()
    client.login(os.environ["BSKY_HANDLE"], os.environ["BSKY_APP_PASSWORD"])

    out, seen = [], set()
    per_term = max(25, limit // max(1, len(kw)))
    for term in kw:
        try:
            res = client.app.bsky.feed.search_posts({"q": term, "limit": min(per_term, 100)})
            for p in res.posts:
                uri = p.uri
                if uri in seen:
                    continue
                seen.add(uri)
                rec = p.record
                eng = (getattr(p, "like_count", 0) or 0) + (getattr(p, "repost_count", 0) or 0)
                ts = getattr(rec, "created_at", None)
                ts = (datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
                      if ts else datetime.now(timezone.utc).timestamp())
                out.append({"text": rec.text, "lang": getattr(rec, "langs", None),
                            "engagement": int(eng), "ts": ts, "source": "bluesky"})
                if len(out) >= limit:
                    return out
        except Exception as e:
            print(f"[bluesky] term '{term}' skipped: {e}")
    return out
