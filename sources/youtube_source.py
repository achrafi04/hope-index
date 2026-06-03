"""
YouTube collector (Data API v3, free quota ~10k units/day).

Setup: enable YouTube Data API v3 in Google Cloud, create an API key, set:
    YOUTUBE_API_KEY
Install: pip install google-api-python-client

Why YouTube matters: comments under match-highlight videos are a goldmine of
Arabic / Darija / French / English reactions on the SAME event — exactly the
multilingual signal X can't give you for free anymore.

Returns normalised posts: {text, lang, engagement, ts, source}
"""
import os
from datetime import datetime, timezone

import config


def _client():
    from googleapiclient.discovery import build
    return build("youtube", "v3", developerKey=os.environ["YOUTUBE_API_KEY"])


def collect(query=None, max_videos=None, comments_per_video=None):
    yt = _client()
    cfg = config.SOURCES["youtube"]
    query = query or f'{config.TARGET["name"]} World Cup'
    max_videos = max_videos or cfg["max_videos"]
    per = comments_per_video or cfg["comments_per_video"]

    # 1) find recent relevant videos
    search = yt.search().list(q=query, part="id", type="video",
                              order="date", maxResults=max_videos).execute()
    vids = [i["id"]["videoId"] for i in search.get("items", [])]

    # 2) pull top comments from each
    out = []
    for vid in vids:
        try:
            req = yt.commentThreads().list(part="snippet", videoId=vid,
                                           maxResults=min(per, 100),
                                           order="relevance", textFormat="plainText")
            while req and len(out) < max_videos * per:
                res = req.execute()
                for it in res.get("items", []):
                    s = it["snippet"]["topLevelComment"]["snippet"]
                    out.append({
                        "text": s["textDisplay"],
                        "lang": None,
                        "engagement": int(s.get("likeCount", 0)),
                        "ts": datetime.fromisoformat(
                            s["publishedAt"].replace("Z", "+00:00")
                        ).timestamp(),
                        "source": f"youtube/{vid}",
                    })
                req = yt.commentThreads().list_next(req, res)
        except Exception as e:
            print(f"[youtube] video {vid} skipped: {e}")
    return out
