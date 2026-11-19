"""RQ2: how much error do the 2015-era emoji lexicons introduce?

Scorers, each mapped to pos/neu/neg with VADER's usual +/-0.05 cut-offs:
  vader       VADER as shipped (emoji read through their names)
  vader_text  VADER with emoji removed
  esr         mean Emoji Sentiment Ranking score of the post's emoji
              (0, i.e. neutral, when none of its emoji are in ESR)

emoji_cost = accuracy(vader) - accuracy(vader_text). Negative means VADER's
emoji handling makes it worse than ignoring the emoji.

Usage: python src/lexicon_error.py <labelled.csv>
  e.g. python src/lexicon_error.py data/labels/labelled_teenagers.csv
"""
import sys
from pathlib import Path

import emoji
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from common import MAX_EMOJI, RESULTS, ROOT, emoji_tokens, strip_modifiers

VALUE = {"pos": 1, "neu": 0, "neg": -1}


def to_class(score):
    return "pos" if score >= 0.05 else "neg" if score <= -0.05 else "neu"


def esr_lexicon():
    d = pd.read_csv(ROOT / "data" / "lexicons" / "Emoji_Sentiment_Data_v1.0.csv")
    return dict(zip(d.Emoji.map(strip_modifiers), (d.Positive - d.Negative) / d.Occurrences))


def main(path):
    tag = Path(path).stem.replace("labelled_", "")
    df = pd.read_csv(path)
    df = df[df.body.map(lambda b: len(emoji_tokens(b)) <= MAX_EMOJI)]  # copypasta rule, as in load()
    vader, esr = SentimentIntensityAnalyzer(), esr_lexicon()

    def text_only(body):
        # Removes whole emoji sequences, skin tones and joiners included.
        return emoji.replace_emoji(body, replace=" ")

    def esr_score(body):
        s = [esr[e] for e in emoji_tokens(body) if e in esr]
        return sum(s) / len(s) if s else 0.0

    df["vader"] = df.body.map(lambda b: to_class(vader.polarity_scores(b)["compound"]))
    df["vader_text"] = df.body.map(lambda b: to_class(vader.polarity_scores(text_only(b))["compound"]))
    df["esr"] = df.body.map(lambda b: to_class(esr_score(b)))
    df.to_csv(RESULTS / f"scored_posts_{tag}.csv", index=False, encoding="utf-8")

    rows = []
    for item, g in list(df.groupby("item")) + [("ALL emoji", df[df.item != "none"])]:
        row = dict(item=item, n=len(g),
                   human_valence=g.label.map(VALUE).mean(),
                   literal_share=g.literal.mean() if item != "none" else float("nan"),
                   esr_score=esr.get(item, float("nan")),
                   vader_alone=vader.polarity_scores(item)["compound"] if item != "none" else float("nan"))
        for s in ["vader", "vader_text", "esr"]:
            row[f"acc_{s}"] = accuracy_score(g.label, g[s])
            row[f"f1_{s}"] = f1_score(g.label, g[s], average="macro", zero_division=0)
        row["emoji_cost"] = row["acc_vader"] - row["acc_vader_text"]
        rows.append(row)

    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / f"lexicon_error_{tag}.csv", index=False, encoding="utf-8")
    print(out.round(3).to_string())


if __name__ == "__main__":
    main(sys.argv[1])
