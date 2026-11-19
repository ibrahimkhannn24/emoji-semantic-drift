"""Why do the lexicons lose accuracy? Two follow-up tests to RQ2.

1. Direction test. For each emoji, the gap is the distance between how it is
   used (mean label: positive 1, neutral 0, negative -1) and VADER's own score
   for it. If drift away from VADER's score causes errors, emoji whose gap grew
   from 2016-17 to 2024-25 should lose the most accuracy. This replaces the
   planned size-of-drift test, which ignores direction and found no link.

2. Repair test. VADER's emoji scores are replaced with each emoji's current
   meaning, learned from one half of the 2024-25 labelled posts, and the other
   half is scored. Two folds, so no post is scored with scores learned from it.
   If out-of-date scores cause the errors, accuracy should recover.

Needs results/lexicon_error_<tag>[_2016-17].csv and scored_posts_<tag>.csv.

Usage: python src/why_error.py
"""
import hashlib

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from common import RESULTS

TAGS = ["teenagers", "memes"]
VALUE = {"pos": 1, "neu": 0, "neg": -1}
SCALES = [1.0, 2.0, 3.0]  # strength given to the new scores; VADER words run -4..+4
MIN_N = 20


def per_emoji(tag, suffix=""):
    d = pd.read_csv(RESULTS / f"lexicon_error_{tag}{suffix}.csv")
    d = d[(d["item"] != "none") & (d["item"] != "ALL emoji") & (d.n >= MIN_N)].set_index("item")
    d["gap"] = (d.human_valence - d.vader_alone).abs()
    return d


def direction_test():
    rows = []
    for tag in TAGS:
        then, now = per_emoji(tag, "_2016-17"), per_emoji(tag)
        for e in then.index.intersection(now.index):
            rows.append(dict(community=tag, emoji=e, vader_score=then.vader_alone[e],
                             use_then=then.human_valence[e], use_now=now.human_valence[e],
                             gap_then=then.gap[e], gap_now=now.gap[e], gap_change=now.gap[e] - then.gap[e],
                             cost_then=100 * then.emoji_cost[e], cost_now=100 * now.emoji_cost[e],
                             cost_change=100 * (now.emoji_cost[e] - then.emoji_cost[e])))
    d = pd.DataFrame(rows)
    rho, p = spearmanr(d.gap_change, d.cost_change)
    d.round(3).to_csv(RESULTS / "direction_test.csv", index=False, encoding="utf-8")
    return dict(test="direction: gap change vs cost change", n=len(d), rho=rho, p=p)


def to_class(c):
    return "pos" if c >= 0.05 else "neg" if c <= -0.05 else "neu"


def repair_test():
    d = pd.concat([pd.read_csv(RESULTS / f"scored_posts_{t}.csv").assign(community=t) for t in TAGS])
    d = d[d["item"] != "none"].copy()
    d["fold"] = [int(hashlib.md5(i.encode()).hexdigest(), 16) % 2 for i in d.id]
    rng = np.random.default_rng(0)
    summary, per_post = [], None
    for scale in SCALES:
        parts = []
        for f in (0, 1):
            train, test = d[d.fold != f], d[d.fold == f]
            meaning = train.groupby("item").label.apply(lambda x: x.map(VALUE).mean())
            vader = SentimentIntensityAnalyzer()
            for k, (e, m) in enumerate(meaning.items()):
                token = f"emojitok{k}x"
                vader.emojis[e] = token
                vader.lexicon[token] = m * scale
            parts.append(test.assign(repaired=test.body.map(lambda b: to_class(vader.polarity_scores(b)["compound"]))))
        t = pd.concat(parts)
        gain = ((t.repaired == t.label).astype(int) - (t.vader == t.label).astype(int)).values
        lo, hi = np.percentile([rng.choice(gain, len(gain)).mean() for _ in range(5000)], [2.5, 97.5])
        summary.append(dict(scale=scale, n=len(t), acc_vader=100 * (t.vader == t.label).mean(),
                            acc_text_only=100 * (t.vader_text == t.label).mean(),
                            acc_repaired=100 * (t.repaired == t.label).mean(),
                            gain=100 * gain.mean(), gain_ci_low=100 * lo, gain_ci_high=100 * hi))
        if scale == 2.0:
            per_post = t
    by_emoji = per_post.groupby("item").apply(lambda x: pd.Series(dict(
        n=len(x), acc_vader=100 * (x.vader == x.label).mean(),
        acc_text_only=100 * (x.vader_text == x.label).mean(),
        acc_repaired=100 * (x.repaired == x.label).mean())), include_groups=False)
    by_emoji.round(1).sort_values("n", ascending=False).to_csv(RESULTS / "repair_by_emoji.csv", encoding="utf-8")
    out = pd.DataFrame(summary).round(2)
    out.to_csv(RESULTS / "repair_test.csv", index=False, encoding="utf-8")
    return out


if __name__ == "__main__":
    print(direction_test())
    print(repair_test().to_string(index=False))
