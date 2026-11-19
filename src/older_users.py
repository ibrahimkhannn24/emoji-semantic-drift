"""Is ironic emoji use a young-community pattern? 2024-25 comparison of
r/teenagers with three older-skewing subreddits, pooled.

Predictions were written before the data was collected:
results/older_users_predictions.md

Steps:
  sample   draw up to N posts per emoji (and N with no emoji) from the older subs
  merge    join the labels (data/labels/labels_older.csv) onto the sample
  compare  older minus r/teenagers, per emoji and pooled, with 95% bootstrap CIs
           (run lexicon_error.py on data/labels/labelled_older.csv first)

Usage: python src/older_users.py sample|merge|compare [30|45]
  30 (default)  r/AskWomenOver30, r/AskMenOver30, r/AskOldPeople
  45            r/GenX, r/AskOldPeople
"""
import random
import sys

import numpy as np
import pandas as pd

from common import RESULTS, ROOT, emoji_tokens, load

GROUPS = {"30": ["AskWomenOver30", "AskMenOver30", "AskOldPeople"], "45": ["GenX", "AskOldPeople"]}
GROUP = sys.argv[2] if len(sys.argv) > 2 else "30"
OLDER = GROUPS[GROUP]
NAME = "older" if GROUP == "30" else "older45"
YEARS = [2024, 2025]
SEVEN = ["😭", "💀", "🙏", "😩", "🔥", "❤", "😂"]
N = 50
MAX_CHARS = 400
LABELS = ROOT / "data" / "labels"
VALUE = {"pos": 1, "neu": 0, "neg": -1}


def sample():
    rng = random.Random(7)
    pool = [(s, c) for s in OLDER for y in YEARS for c in load(s, y) if 3 <= len(c["body"]) <= MAX_CHARS]
    rng.shuffle(pool)
    picked, taken = [], set()
    for item in SEVEN:
        hits = [(s, c) for s, c in pool if c["id"] not in taken and item in emoji_tokens(c["body"])]
        for s, c in hits[:N]:
            taken.add(c["id"])
            picked.append(dict(id=c["id"], sub=s, item=item, body=c["body"]))
    plain = [(s, c) for s, c in pool if c["id"] not in taken and not emoji_tokens(c["body"])]
    for s, c in plain[:N]:
        picked.append(dict(id=c["id"], sub=s, item="none", body=c["body"]))
    out = pd.DataFrame(picked)
    out.to_csv(LABELS / f"sample_{NAME}.csv", index=False, encoding="utf-8")
    print(f"{len(pool):,} comments in the pool")
    print(out.groupby("item").size().to_string())


def merge():
    s = pd.read_csv(LABELS / f"sample_{NAME}.csv")
    lab = pd.read_csv(LABELS / f"labels_{NAME}.csv")
    d = s.merge(lab, on="id", how="inner")
    assert len(d) == len(s), f"{len(s) - len(d)} posts have no label"
    d.to_csv(LABELS / f"labelled_{NAME}.csv", index=False, encoding="utf-8")
    print(f"{len(d)} labelled posts written")


def measures(g):
    return dict(literal=100 * g.literal.mean(), value=g.label.map(VALUE).mean(),
                cost=100 * ((g.vader == g.label).astype(int) - (g.vader_text == g.label).astype(int)).mean())


def compare():
    young = pd.read_csv(RESULTS / "scored_posts_teenagers.csv")
    older = pd.read_csv(RESULTS / f"scored_posts_{NAME}.csv")
    young, older = young[young["item"].isin(SEVEN)], older[older["item"].isin(SEVEN)]
    rng = np.random.default_rng(0)
    rows = []
    for item in SEVEN + ["ALL"]:
        y = young if item == "ALL" else young[young["item"] == item]
        o = older if item == "ALL" else older[older["item"] == item]
        if len(o) < 10:
            rows.append(dict(item=item, n_young=len(y), n_older=len(o)))
            continue
        my, mo = measures(y), measures(o)
        row = dict(item=item, n_young=len(y), n_older=len(o))
        boots = {k: [] for k in my}
        for _ in range(5000):
            by, bo = measures(y.sample(len(y), replace=True, random_state=rng)), \
                measures(o.sample(len(o), replace=True, random_state=rng))
            for k in my:
                boots[k].append(bo[k] - by[k])
        for k in my:
            lo, hi = np.percentile(boots[k], [2.5, 97.5])
            row.update({f"{k}_young": my[k], f"{k}_older": mo[k], f"{k}_diff": mo[k] - my[k],
                        f"{k}_lo": lo, f"{k}_hi": hi})
        rows.append(row)
    out = pd.DataFrame(rows).round(2)
    out.to_csv(RESULTS / f"{NAME}_vs_teens.csv", index=False, encoding="utf-8")
    print(out.to_string(index=False))
    balanced(young, older)


MIN_SHARED = 20  # posts an emoji needs in both groups to enter the balanced comparison


def balanced(young, older):
    """The pooled row above mixes different emoji in each group (older users have
    almost no 🔥). Here each shared emoji counts equally in both groups."""
    SHARED = [e for e in SEVEN if (young["item"] == e).sum() >= MIN_SHARED
              and (older["item"] == e).sum() >= MIN_SHARED]
    print("shared emoji:", " ".join(SHARED))
    def m(d):
        per = [measures(g) for _, g in d[d["item"].isin(SHARED)].groupby("item")]
        return {k: np.mean([p[k] for p in per]) for k in per[0]}

    def resample(d, rng):
        return pd.concat([g.sample(len(g), replace=True, random_state=rng)
                          for _, g in d[d["item"].isin(SHARED)].groupby("item")])

    rng = np.random.default_rng(0)
    my, mo = m(young), m(older)
    boots = [m(resample(older, rng)) for _ in range(2000)], [m(resample(young, rng)) for _ in range(2000)]
    rows = []
    for k in my:
        diffs = [bo[k] - by[k] for bo, by in zip(*boots)]
        lo, hi = np.percentile(diffs, [2.5, 97.5])
        rows.append(dict(measure=k, young=my[k], older=mo[k], diff=mo[k] - my[k], ci_low=lo, ci_high=hi))
    out = pd.DataFrame(rows).round(2)
    out.to_csv(RESULTS / f"{NAME}_vs_teens_balanced.csv", index=False, encoding="utf-8")
    print("\nshared emoji, equal weight:\n" + out.to_string(index=False))


if __name__ == "__main__":
    {"sample": sample, "merge": merge, "compare": compare}[sys.argv[1]]()
