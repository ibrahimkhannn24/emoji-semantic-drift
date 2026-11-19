"""RQ1: how far has each emoji moved? (Hamilton et al. 2016 method)

One skip-gram model per period (two-year or single-year), each aligned to the
latest period with orthogonal Procrustes. Drift is the cosine distance between
an emoji's vector in an earlier period and in the latest one. The overlap of
nearest neighbours needs no alignment and serves as a check.

Rare tokens look unstable from sampling noise alone, so each drift score is
also given as a percentile among words of similar frequency and, the measure
used in the findings, among all emoji with enough uses.

Usage: python src/drift.py <tag> <2yr|1yr> <subreddit> [subreddit ...] [--saved]
  --saved re-scores the models saved by an earlier run instead of retraining.
"""
import sys

import numpy as np
import pandas as pd
from emoji import is_emoji
from gensim.models import KeyedVectors, Word2Vec
from scipy.linalg import orthogonal_procrustes

from common import CONTROLS, PERIODS, RESULTS, TARGETS, YEARLY, load, tokenize

MIN_COUNT = 10       # vocabulary cut-off for training
MIN_REPORT = 30      # occurrences needed in both periods to report a drift score
K = 10               # neighbours for the overlap score
ITEMS = TARGETS + CONTROLS
MODELS = RESULTS / "models"
MODELS.mkdir(exist_ok=True)


def corpus(subs, years):
    return [t for s in subs for y in years for c in load(s, y)
            if len(t := tokenize(c["body"])) > 1]


def train(sentences):
    return Word2Vec(sentences, sg=1, vector_size=100, window=5, min_count=MIN_COUNT,
                    negative=5, epochs=10, seed=42, workers=1)


def unit(m):
    return m / np.linalg.norm(m, axis=1, keepdims=True)


def neighbours(mat, vocab, idx, word, k=K):
    sims = mat @ mat[idx[word]]
    order = np.argsort(-sims)
    return [vocab[i] for i in order if vocab[i] != word][:k]


def main(tag, periods, subs, saved=False):
    """saved=True re-scores the models saved by an earlier run instead of training."""
    last = list(periods)[-1]
    models, counts = {}, {}
    for name, years in periods.items():
        if saved:
            wv = KeyedVectors.load(str(MODELS / f"{tag}_{name}.kv"))
        else:
            sents = corpus(subs, years)
            wv = train(sents).wv
            wv.save(str(MODELS / f"{tag}_{name}.kv"))
            print(f"{name}: {len(sents):,} comments, vocab {len(wv):,}", flush=True)
        models[name] = wv
        counts[name] = {w: wv.get_vecattr(w, "count") for w in wv.index_to_key}

    ref = models[last]
    rows = []
    for name in periods:
        if name == last:
            continue  # drift of the reference against itself is zero by definition
        wv = models[name]
        shared = [w for w in wv.index_to_key if w in ref.key_to_index]
        A, B = unit(wv[shared]), unit(ref[shared])
        anchors = [i for i, w in enumerate(shared) if w not in ITEMS]
        R, _ = orthogonal_procrustes(A[anchors], B[anchors])
        A = A @ R
        drift = 1 - np.sum(A * B, axis=1)
        idx = {w: i for i, w in enumerate(shared)}
        freq = np.array([min(counts[name][w], counts[last][w]) for w in shared])
        # Emoji neighbour other emoji, and the emoji inventory itself changed a
        # lot over the decade, so emoji are also ranked against other emoji.
        emoji_peers = [i for i, w in enumerate(shared) if is_emoji(w) and freq[i] >= MIN_REPORT]

        for item in ITEMS:
            n_p, n_r = counts[name].get(item, 0), counts[last].get(item, 0)
            row = dict(emoji=item, period=name, count=n_p, count_ref=n_r)
            if item in idx and min(n_p, n_r) >= MIN_REPORT:
                i = idx[item]
                f = freq[i]
                peers = [j for j in anchors if 0.5 * f <= freq[j] <= 2 * f]
                nb_p = neighbours(A, shared, idx, item)
                nb_r = neighbours(B, shared, idx, item)
                row.update(drift=drift[i],
                           percentile=100 * np.mean(drift[peers] < drift[i]) if peers else np.nan,
                           n_peers=len(peers),
                           emoji_percentile=100 * np.mean(drift[[j for j in emoji_peers if j != i]] < drift[i]),
                           n_emoji_peers=len(emoji_peers) - 1,
                           nn_overlap=len(set(nb_p) & set(nb_r)) / len(set(nb_p) | set(nb_r)),
                           neighbours=" ".join(neighbours(unit(wv[shared]), shared, idx, item, 8)))
            rows.append(row)

    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / f"drift_{tag}.csv", index=False, encoding="utf-8")
    print(out.to_string())


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--saved"]
    main(args[0], PERIODS if args[1] == "2yr" else YEARLY, args[2:], saved="--saved" in sys.argv)
