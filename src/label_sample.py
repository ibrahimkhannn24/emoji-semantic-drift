"""Draw the posts to be labelled for RQ2.

Up to N posts per emoji, plus a baseline of posts with no emoji. A post is
filed under the first emoji it contains, so no post is labelled twice.

Three modes:
  (default) 2024-25 posts for every target and control emoji
  add       2024-25 posts for emoji added later, skipping the first sample
  early     2016-17 posts, for the before-and-after comparison

The saved sample files in data/labels are the reference. The default mode was
first run when TARGETS held ten emoji, so running it again now would draw a
different sample.

Usage: python src/label_sample.py <n_per_emoji> <subreddit> [subreddit ...]
       python src/label_sample.py add <n_per_emoji> <emoji,emoji,...> <subreddit ...>
       python src/label_sample.py early <n_per_emoji> <emoji,emoji,...> <subreddit ...>
"""
import random
import sys

import pandas as pd

from common import CONTROLS, ROOT, TARGETS, emoji_tokens, load

YEARS = [2024, 2025]
N_BASELINE = 100
MAX_CHARS = 400


def main(n, subs):
    rng = random.Random(7)
    pool = [(s, c) for s in subs for y in YEARS for c in load(s, y)
            if 3 <= len(c["body"]) <= MAX_CHARS]
    rng.shuffle(pool)

    picked, taken = [], set()
    for item in TARGETS + CONTROLS:
        hits = [(s, c) for s, c in pool if c["id"] not in taken and item in emoji_tokens(c["body"])]
        for s, c in hits[:n]:
            taken.add(c["id"])
            picked.append(dict(id=c["id"], sub=s, item=item, body=c["body"]))
    plain = [(s, c) for s, c in pool if c["id"] not in taken and not emoji_tokens(c["body"])]
    for s, c in plain[:N_BASELINE]:
        picked.append(dict(id=c["id"], sub=s, item="none", body=c["body"]))

    out = pd.DataFrame(picked)
    path = ROOT / "data" / "labels"
    path.mkdir(parents=True, exist_ok=True)
    out.to_csv(path / f"sample_{'_'.join(subs)}.csv", index=False, encoding="utf-8")
    print(out.groupby("item").size().to_string())


def add(n, items, subs):
    """Extra posts for emoji added after the first sample, leaving it untouched."""
    path = ROOT / "data" / "labels"
    taken = set(pd.read_csv(path / f"sample_{'_'.join(subs)}.csv").id)
    rng = random.Random(11)
    pool = [(s, c) for s in subs for y in YEARS for c in load(s, y)
            if 3 <= len(c["body"]) <= MAX_CHARS and c["id"] not in taken]
    rng.shuffle(pool)
    picked = []
    for item in items:
        hits = [(s, c) for s, c in pool if c["id"] not in taken and item in emoji_tokens(c["body"])]
        for s, c in hits[:n]:
            taken.add(c["id"])
            picked.append(dict(id=c["id"], sub=s, item=item, body=c["body"]))
    out = pd.DataFrame(picked)
    out.to_csv(path / f"sample_{'_'.join(subs)}_extra.csv", index=False, encoding="utf-8")
    print(out.groupby("item").size().to_string())


def early(n, items, subs, n_baseline=50):
    """2016-17 posts for the emoji that existed then, to compare lexicon error over time."""
    rng = random.Random(7)
    pool = [(s, c) for s in subs for y in (2016, 2017) for c in load(s, y)
            if 3 <= len(c["body"]) <= MAX_CHARS]
    rng.shuffle(pool)
    picked, taken = [], set()
    for item in items:
        hits = [(s, c) for s, c in pool if c["id"] not in taken and item in emoji_tokens(c["body"])]
        for s, c in hits[:n]:
            taken.add(c["id"])
            picked.append(dict(id=c["id"], sub=s, item=item, body=c["body"]))
    plain = [(s, c) for s, c in pool if c["id"] not in taken and not emoji_tokens(c["body"])]
    for s, c in plain[:n_baseline]:
        picked.append(dict(id=c["id"], sub=s, item="none", body=c["body"]))
    out = pd.DataFrame(picked)
    out.to_csv(ROOT / "data" / "labels" / f"sample_{'_'.join(subs)}_2016-17.csv",
               index=False, encoding="utf-8")
    print(out.groupby("item").size().to_string())


if __name__ == "__main__":
    if sys.argv[1] == "add":
        # add <n_per_emoji> <emoji,emoji,...> <subreddit ...>
        add(int(sys.argv[2]), sys.argv[3].split(","), sys.argv[4:])
    elif sys.argv[1] == "early":
        # early <n_per_emoji> <emoji,emoji,...> <subreddit ...>
        early(int(sys.argv[2]), sys.argv[3].split(","), sys.argv[4:])
    else:
        main(int(sys.argv[1]), sys.argv[2:])
