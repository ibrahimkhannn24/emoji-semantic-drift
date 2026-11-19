"""Share of emoji uses, per period, that ESR and VADER have no entry for.

Usage: python src/coverage.py <tag> <subreddit> [subreddit ...]
"""
import sys
from collections import Counter

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from common import PERIODS, RESULTS, emoji_tokens, load, strip_modifiers
from lexicon_error import esr_lexicon


def main(tag, subs):
    esr = esr_lexicon()
    vader = {strip_modifiers(e) for e in SentimentIntensityAnalyzer().emojis}
    rows, missing_recent = [], Counter()
    for name, years in PERIODS.items():
        uses = Counter(e for s in subs for y in years for c in load(s, y) for e in emoji_tokens(c["body"]))
        total = sum(uses.values())
        if not total:
            continue
        no_esr = sum(n for e, n in uses.items() if e not in esr)
        no_vader = sum(n for e, n in uses.items() if e not in vader)
        rows.append(dict(period=name, emoji_uses=total, distinct=len(uses),
                         missing_esr=no_esr / total, missing_vader=no_vader / total))
        if name == "2024-25":
            missing_recent = Counter({e: n for e, n in uses.items() if e not in esr})

    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / f"coverage_{tag}.csv", index=False, encoding="utf-8")
    print(out.round(3).to_string())
    print("Most used 2024-25 emoji missing from ESR:", missing_recent.most_common(15))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
