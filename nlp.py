"""
NLP layer — turns raw text into a sentiment valence in [-1, 1].

Primary model: cardiffnlp/twitter-xlm-roberta-base-sentiment
  - XLM-RoBERTa fine-tuned on multilingual tweets
  - handles English, French, Arabic (MSA) well out of the box
  - Darija is the known weak spot -> flagged as the research edge to fine-tune later
    (candidate base model: SI2M-Lab/DarijaBERT)

If transformers/torch or the model weights aren't available (e.g. first run, or a
sandbox with no internet), we fall back to a transparent lexicon scorer so the rest
of the pipeline still runs and can be demoed. The fallback is clearly marked.
"""
from functools import lru_cache

_MODEL = "cardiffnlp/twitter-xlm-roberta-base-sentiment"


@lru_cache(maxsize=1)
def _load_model():
    """Lazy-load the transformer once. Returns None if unavailable."""
    try:
        from transformers import (AutoTokenizer,
                                   AutoModelForSequenceClassification)
        import torch  # noqa
        tok = AutoTokenizer.from_pretrained(_MODEL)
        mdl = AutoModelForSequenceClassification.from_pretrained(_MODEL)
        mdl.eval()
        return ("hf", tok, mdl)
    except Exception as e:
        print(f"[nlp] transformer unavailable ({type(e).__name__}); "
              f"using lexicon fallback.")
        return None


# --- transparent multilingual fallback lexicon (tiny, just to keep things alive)
_POS = {"win", "winning", "won", "hope", "believe", "yes", "goal", "amazing",
        "espoir", "gagner", "victoire", "but", "incroyable", "allez", "on y croit",
        "نصر", "فوز", "هدف", "رائع",
        "dima", "nsroo", "sa3d", "tbarkallah", "zwin", "mzyan"}
_NEG = {"lose", "losing", "lost", "out", "eliminated", "fear", "scared", "penalty",
        "perdu", "perdre", "peur", "éliminé", "catastrophe", "honte",
        "خسارة", "هزيمة", "خوف",
        "khsara", "hzima", "khayb", "3yyit", "ma9drnach"}


def _fallback_score(text):
    t = text.lower()
    p = sum(w in t for w in _POS)
    n = sum(w in t for w in _NEG)
    if p == n == 0:
        return 0.0
    return (p - n) / (p + n)


def score(text):
    """Return sentiment valence in [-1, 1] (P(pos) - P(neg))."""
    m = _load_model()
    if m is None:
        return _fallback_score(text)
    _, tok, mdl = m
    import torch
    with torch.no_grad():
        enc = tok(text, return_tensors="pt", truncation=True, max_length=128)
        probs = mdl(**enc).logits.softmax(-1).squeeze()
    # label order for this model: 0=negative, 1=neutral, 2=positive
    return float(probs[2] - probs[0])


def score_many(texts):
    return [score(t) for t in texts]
