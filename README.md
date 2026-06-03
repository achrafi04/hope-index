# The Miracle Index &nbsp;·&nbsp; The Hope Index

> Football is a machine for making the improbable feel inevitable. This project measures the improbable — and the hope that surrounds it.

**Two connected instruments, one Elo engine.**

- **The Miracle Index** — how unlikely was that result, really? A century and a half of football, scored by how far each outcome stood from what was expected.
- **The Hope Index** — how far does a nation's *heart* drift from the *math*? A live pipeline that reads the mood of a fan base during the World Cup and contrasts it with the cold expectation of the model.

🔗 **Live demo:** https://achrafi04.github.io/hope-index/

---

## Why this exists

When supporters say *"it was written,"* they reach for fate. But every result was once only probable. The same Elo engine that tells us how improbable the past was can tell us, in real time, when a crowd believes more than the numbers justify — the moment hope outruns probability. That gap is the whole story.

---

## 1 · The Miracle Index

An Elo model (World Football Elo style) is built chronologically over **49,363 international matches since 1872**. For any World Cup match it holds a pre-match expectation; when the underdog wins, the miracle index is `(1 − P(winner)) × 100`.

### Biggest single-match upsets (all-time)

| Rank | Match | Score | Win prob. | Miracle |
|----:|-------|:-----:|:---------:|:-------:|
| 1 | Cameroon over Brazil (2022) | 1–0 | 4.5% | **95.5** |
| 2 | United States over England (1950) | 1–0 | 7.7% | 92.3 |
| 3 | Saudi Arabia over Argentina (2022) | 2–1 | 7.8% | 92.2 |
| 4 | Switzerland over Spain (2010) | 1–0 | 11.7% | 88.3 |
| 5 | South Korea over Germany (2018) | 2–0 | 12.4% | 87.6 |

### The deeper miracle — surviving a tournament

A single upset is one thing; climbing a whole bracket against the odds is another. The pre-2022 Elo is **frozen at the eve of the tournament** (no hindsight) and the entire bracket is simulated **40,000 times** via Monte-Carlo. Knockout shootouts are modelled as a near coin-flip with only a mild edge to the stronger side.

| Team | Reached | Pre-tournament prob. | Miracle |
|------|---------|:--------------------:|:-------:|
| **Morocco** | **semi-final** | **2.5%** | **97.5** |
| Croatia | semi-final | 10.2% | 89.8 |
| France | final | 12.8% | 87.2 |
| Argentina | the title | 20.0% | 80.0 |

**Morocco's run to the semi-final — a 2.5% pre-tournament event — is the single greatest miracle in this dataset, deeper even than any one-match upset.** Their climb: round of 16 (30.5%) → quarter-final (9.9%) → semi-final (2.5%).

---

## 2 · The Hope Index

A live pipeline that measures a nation's emotional hope during the World Cup and plots it against statistical hope.

```
   FAITH  ┃   ╭─ emotional hope (the crowd)
          ┃  ╱
   ───────╋─────────────────────────  statistical hope (Elo)
          ┃ ╲
   DOUBT  ┃  ╰─ when the model believes more than the people
```

- **Emotional hope** — real posts from **YouTube comments** and **Bluesky** (both free), scored by a **multilingual** sentiment model across English, French, Arabic and Darija, then mapped to a 0–100 mood.
- **Statistical hope** — the Elo win expectation for the next opponent, from the same engine as the Miracle Index.
- **The Belief Gap** — `emotional − statistical`. Positive = faith; negative = doubt. The story lives in the gap.

It runs unattended (cron), stores a SQLite time series, and regenerates a self-contained editorial dashboard after every pass.

---

## How it works

```
Elo engine ──┬── Miracle Index (match-level)      → index.html
             ├── Monte-Carlo bracket (40k sims)    → qualification_miracles.py
             └── statistical-hope axis ─┐
                                        ├── Belief Gap → dashboard
 YouTube + Bluesky → multilingual NLP ──┘
```

| Layer | What it does | Key files |
|------|---------------|-----------|
| Ratings | World-Football-style Elo over all internationals | `belief_gap.py`, `miracle_index.py` |
| Improbability | match-level + Monte-Carlo tournament miracles | `qualification_miracles.py` |
| Collection | free multilingual social sources | `sources/youtube_source.py`, `sources/bluesky_source.py` |
| Sentiment | XLM-R multilingual valence (+ offline fallback) | `nlp.py` |
| Aggregation | Hope Index + Belief Gap + SQLite | `index.py`, `run.py` |
| Presentation | editorial pages, hand-drawn SVG, no chart libs | `index.html`, `build_dashboard.py` |

---

## Tech stack

`Python` · `pandas` · `transformers` / `torch` (XLM-R: `cardiffnlp/twitter-xlm-roberta-base-sentiment`) · `atproto` (Bluesky) · `google-api-python-client` (YouTube) · `SQLite` · vanilla `HTML` / `SVG` (Fraunces + Newsreader, no frameworks, no chart libraries).

## Run it yourself

```bash
python -m venv .venv && source .venv/bin/activate
pip install pandas transformers torch atproto google-api-python-client python-dotenv sentencepiece
curl -sL -o results.csv https://raw.githubusercontent.com/martj42/international_results/master/results.csv

python miracle_index.py            # the all-time match upsets
python qualification_miracles.py   # Monte-Carlo tournament miracles
python demo.py                     # the Hope Index brain, no API keys needed
```

For the live Hope Index, add free credentials to a `.env` file (`YOUTUBE_API_KEY`, `BSKY_HANDLE`, `BSKY_APP_PASSWORD`), then `python run.py --opponent Brazil`.

## Method & honest limitations

- **Elo is strength-only** — it has no explicit goals model; scorelines enter only through a margin-of-victory multiplier.
- **Shootouts** are modelled as a near coin-flip with a mild Elo tilt — defensible, but a simplification.
- **Group tiebreaks** in the Monte-Carlo use a random draw among equal points (goal difference isn't modelled).
- **Darija** is the sentiment model's weak spot; the strongest planned improvement is fine-tuning a dedicated Darija model. Until then, Darija leans on the multilingual baseline.
- **Social sampling** is keyword-based, not a representative survey — the Hope Index reads online discourse, not a nation in full.

## Roadmap

- [ ] Publish the live Hope Index dashboard once it has a real match-day curve
- [ ] Fine-tune a Darija sentiment model (research edge → publishable)
- [ ] Extend the Monte-Carlo to the 48-team 2026 format

## Data & credits

International match results: [martj42/international_results](https://github.com/martj42/international_results). Built on the road to the FIFA World Cup 2026.
