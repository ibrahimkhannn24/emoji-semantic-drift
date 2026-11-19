"""Did the lexicons get worse over time? 2016-17 against 2024-25.

Compares, for the seven emoji common to both periods, the cost of VADER's
emoji handling, ESR accuracy, the share of literal uses and the mean labelled
sentiment, with 5,000 bootstrap resamples of each period's posts.

Needs results/scored_posts_<tag>.csv and scored_posts_<tag>_2016-17.csv,
written by lexicon_error.py.

Usage: python src/over_time.py
"""
import numpy as np
import pandas as pd

from common import RESULTS

ITEMS = ["😭", "💀", "🙏", "🔥", "😩", "❤", "😂"]
VALUE = {"pos": 1, "neu": 0, "neg": -1}
GROUPS = [("r/teenagers", ["teenagers"]), ("Meme subs", ["memes"]), ("Pooled", ["teenagers", "memes"])]
rng = np.random.default_rng(0)


def scored(tag, suffix):
    d = pd.read_csv(RESULTS / f"scored_posts_{tag}{suffix}.csv")
    d["cost"] = (d.vader == d.label).astype(int) - (d.vader_text == d.label).astype(int)
    d["esr_ok"] = (d.esr == d.label).astype(int)
    d["value"] = d.label.map(VALUE)
    return d


def change(early, late, n=5000):
    """Mean of late minus mean of early, with a bootstrap 95% interval."""
    early, late = np.asarray(early), np.asarray(late)
    boot = [rng.choice(late, len(late)).mean() - rng.choice(early, len(early)).mean() for _ in range(n)]
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return late.mean() - early.mean(), lo, hi


def main():
    rows = []
    for name, tags in GROUPS:
        early = pd.concat([scored(t, "_2016-17") for t in tags])
        late = pd.concat([scored(t, "") for t in tags])
        for item in ITEMS + ["ALL"]:
            e = early[early["item"].isin(ITEMS)] if item == "ALL" else early[early["item"] == item]
            l = late[late["item"].isin(ITEMS)] if item == "ALL" else late[late["item"] == item]
            if min(len(e), len(l)) < 15:
                continue
            row = dict(community=name, item=item, n_early=len(e), n_late=len(l))
            for col, scale in [("cost", 100), ("esr_ok", 100), ("literal", 100), ("value", 1)]:
                d, lo, hi = change(e[col], l[col])
                row.update({f"{col}_early": scale * e[col].mean(), f"{col}_late": scale * l[col].mean(),
                            f"{col}_change": scale * d, f"{col}_lo": scale * lo, f"{col}_hi": scale * hi})
            rows.append(row)
    out = pd.DataFrame(rows).round(2)
    out.to_csv(RESULTS / "over_time_comparison.csv", index=False, encoding="utf-8")
    print(out[["community", "item", "n_early", "n_late", "cost_early", "cost_late",
               "cost_change", "cost_lo", "cost_hi"]].round(1).to_string(index=False))


if __name__ == "__main__":
    main()
