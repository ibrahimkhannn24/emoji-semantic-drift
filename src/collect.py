"""Sample Reddit comments from the Arctic Shift archive.

Each request returns up to 100 comments posted after a random timestamp in the
target year, so a year's sample is spread across many short windows.

Usage:
    python src/collect.py pilot
    python src/collect.py full <requests_per_sub_year> [subreddit ...]
    python src/collect.py more <n> <offset> <first_year> <last_year> <subreddit ...>
        (extra requests; offset keeps them from repeating earlier windows)
"""
import json
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import requests

API = "https://arctic-shift.photon-reddit.com/api/comments/search"
OUT = Path(__file__).resolve().parent.parent / "data" / "raw"
SUBS = ["teenagers"]
YEARS = list(range(2016, 2026))
WORKERS = 6


def fetch(sub, year, seed):
    rng = random.Random(seed)
    start = datetime(year, 1, 1, tzinfo=timezone.utc).timestamp()
    end = datetime(year + 1, 1, 1, tzinfo=timezone.utc).timestamp()
    after = int(rng.uniform(start, end - 86400))
    params = dict(subreddit=sub, after=after, before=after + 86400, limit=100,
                  fields="id,body,created_utc,score")
    for attempt in range(4):
        try:
            r = requests.get(API, params=params, timeout=60)
            d = r.json()
            if d.get("data"):
                return [c for c in d["data"] if c["body"] not in ("[deleted]", "[removed]")]
            if d.get("error"):
                time.sleep(3 * (attempt + 1))
                continue
            return []
        except Exception:
            time.sleep(3 * (attempt + 1))
    return []


def run(n_requests, tag, offset=0):
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [(s, y, f"{s}-{y}-{i}") for s in SUBS for y in YEARS
            for i in range(offset, offset + n_requests)]
    with ThreadPoolExecutor(WORKERS) as ex:
        results = ex.map(lambda j: (j, fetch(*j)), jobs)
        files = {}
        done = 0
        for (sub, year, _), comments in results:
            key = (sub, year)
            if key not in files:
                files[key] = open(OUT / f"{tag}_{sub}_{year}.jsonl", "a", encoding="utf-8")
            for c in comments:
                files[key].write(json.dumps(c, ensure_ascii=False) + "\n")
            done += 1
            if done % 50 == 0:
                print(f"{done}/{len(jobs)} requests", flush=True)
        for f in files.values():
            f.close()


if __name__ == "__main__":
    if sys.argv[1] == "pilot":
        run(5, "pilot")
    elif sys.argv[1] == "more":
        # more <n> <offset> <first_year> <last_year> <subreddit ...>
        n, offset, y0, y1 = map(int, sys.argv[2:6])
        YEARS = list(range(y0, y1 + 1))
        SUBS = sys.argv[6:]
        run(n, "full", offset)
    else:
        if len(sys.argv) > 3:
            SUBS = sys.argv[3:]
        run(int(sys.argv[2]), "full")
