"""95% bootstrap intervals for the cost of VADER's emoji handling, 2024-25 posts.

Per emoji and community, then pooled across both communities for the three
emoji discussed in the findings. 5,000 resamples, fixed seed.

Needs results/scored_posts_<tag>.csv, written by lexicon_error.py.

Usage: python src/intervals.py
"""
import numpy as np
import pandas as pd

from common import RESULTS

POOLED = ["😭", "🤓", "🔥"]


def cost(g):
    return ((g.vader == g.label).astype(int) - (g.vader_text == g.label).astype(int)).values


def interval(rng, diff, n=5000):
    boot = [rng.choice(diff, len(diff)).mean() for _ in range(n)]
    return np.percentile(boot, [2.5, 97.5])


def main():
    rng = np.random.default_rng(0)
    rows = []
    for tag in ["teenagers", "memes"]:
        d = pd.read_csv(RESULTS / f"scored_posts_{tag}.csv")
        for item, g in list(d.groupby("item")) + [("ALL emoji", d[d["item"] != "none"])]:
            if item == "none" or len(g) < 20:
                continue
            diff = cost(g)
            lo, hi = interval(rng, diff)
            rows.append(dict(community=tag, item=item, n=len(g), cost=100 * diff.mean(),
                             ci_low=100 * lo, ci_high=100 * hi, significant=(lo > 0) or (hi < 0)))
    both = pd.concat([pd.read_csv(RESULTS / f"scored_posts_{t}.csv") for t in ["teenagers", "memes"]])
    for item in POOLED:
        diff = cost(both[both["item"] == item])
        lo, hi = interval(rng, diff)
        rows.append(dict(community="pooled", item=item, n=len(diff), cost=100 * diff.mean(),
                         ci_low=100 * lo, ci_high=100 * hi, significant=(lo > 0) or (hi < 0)))
    out = pd.DataFrame(rows).round(1)
    out.to_csv(RESULTS / "cost_confidence_intervals.csv", index=False, encoding="utf-8")
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
