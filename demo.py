"""
Offline demo — no API keys, no internet. Proves the brain.

Simulates the emotional arc of a knockout match (synthetic multilingual posts)
across several time windows and shows the Hope Index move, plus the Belief Gap
against a real Elo statistical-hope value.

    $ python demo.py
"""
import index
import nlp

# Synthetic windows: each is a snapshot of what the timeline "sounds like".
# Mixed FR / EN / Arabic / Darija on purpose.
WINDOWS = [
    ("Pre-match (nervous hope)", [
        ("Dima Maghrib! on y croit, les Lions vont le faire", 240),
        ("nsroo incha'allah, j'ai trop peur mais j'ai espoir", 88),
        ("أسود الأطلس راه غادي نربحو، dima maroc", 410),
        ("honestly scared, the opponent is strong but allez le Maroc", 35),
        ("Morocco believe! this is our year", 120),
    ]),
    ("Goal! Morocco scores (euphoria)", [
        ("BUUUUUT!!! incroyable, on gagne!! dima maghrib", 980),
        ("هدف رائع!! المغرب يفوز", 1200),
        ("amazing goal, we are winning!! this is unreal", 540),
        ("tbarkallah 3lihom, zwin had goal nsroo", 300),
        ("best day ever, victoire victoire", 220),
    ]),
    ("Opponent equalises late (panic)", [
        ("non non non, khsara, j'ai peur maintenant", 410),
        ("they scored, we are going to lose, catastrophe", 360),
        ("3yyit, khayb had match, peur de l'élimination", 150),
        ("penalty incoming, scared, ma9drnach", 90),
        ("هزيمة قريبة، خوف كبير", 280),
    ]),
    ("Final whistle: Morocco advance on penalties (relief)", [
        ("ON PASSE!! nsroo, dima maghrib, incroyable victoire", 1500),
        ("we won!! amazing, best feeling, allez", 700),
        ("المغرب يتأهل! فوز رائع، tbarkallah", 900),
        ("zwin bzaf, on y croyait, happiness", 260),
    ]),
]


def main():
    print(f"[nlp] backend: {'transformer' if nlp._load_model() else 'lexicon fallback'}\n")
    # one fixed statistical-hope value for the demo (Elo says Morocco underdog here)
    STAT_HOPE = 28.0  # e.g. Elo win expectation vs a stronger side, mapped 0-100
    print(f"Statistical hope (Elo, cold head): {STAT_HOPE}/100\n")
    print(f"{'WINDOW':<48}{'HOPE':>7}{'MOOD':>9}{'GAP':>8}  VERDICT")
    print("-" * 88)
    for label, raw in WINDOWS:
        posts = [{"text": t, "engagement": e, "sentiment": nlp.score(t)} for t, e in raw]
        pt = index.compute_point(posts)
        gap = pt["hope"] - STAT_HOPE
        verdict = "FAITH  (crowd > model)" if gap > 0 else "DOUBT  (crowd < model)"
        print(f"{label:<48}{pt['hope']:>7}{pt['mood']:>+9.3f}{gap:>+8.1f}  {verdict}")
    print("\nThe story is in the GAP column: how far the nation's heart drifts from the math.")


if __name__ == "__main__":
    main()
