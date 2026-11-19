"""Shared settings, data loading and tokenisation."""
import json
import re
from pathlib import Path

import emoji

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

# The last four targets are post-2020 slang emoji, none of them in ESR.
TARGETS = ["💀", "😭", "🙏", "🙂", "🤡", "🗿", "😩", "🧢", "🫠", "🥲",
           "🥀", "🗣", "🤓", "🫵"]
CONTROLS = ["❤", "😂", "🔥"]  # ❤ is stored without its variation selector
PERIODS = {"2016-17": (2016, 2017), "2018-19": (2018, 2019), "2020-21": (2020, 2021),
           "2022-23": (2022, 2023), "2024-25": (2024, 2025)}
YEARLY = {str(y): (y,) for y in range(2016, 2026)}

# Comments with more emoji than this are copypasta, such as the 2016
# "👌👀 good shit" text repeated dozens of times in r/dankmemes.
MAX_EMOJI = 20

# Variation selectors and skin tones are dropped so that 🙏🏽 and 🙏 count as the
# same token. Zero-width joiners are kept, because 🙂‍↕️ (nodding) and ❤️‍🔥 are
# emoji in their own right.
MODIFIERS = re.compile("[︎️\U0001F3FB-\U0001F3FF]")
WORD = re.compile(r"[a-z0-9']+")


def strip_modifiers(text):
    return MODIFIERS.sub("", text)


def collapse(tokens):
    """Count a run of one repeated token (💀💀💀) as a single use."""
    return [t for i, t in enumerate(tokens) if i == 0 or t != tokens[i - 1]]


def emoji_tokens(text):
    return collapse([e["emoji"] for e in emoji.emoji_list(strip_modifiers(text))])


def tokenize(text):
    """Lower-cased words plus each emoji as its own token, repeats collapsed."""
    text = strip_modifiers(text.lower())
    text = re.sub(r"https?://\S+", " ", text)
    tokens, pos = [], 0
    for e in emoji.emoji_list(text):
        tokens += WORD.findall(text[pos:e["match_start"]])
        tokens.append(e["emoji"])
        pos = e["match_end"]
    tokens += WORD.findall(text[pos:])
    return collapse(tokens)


def load(sub, year):
    """The sampled comments for one subreddit and year, without duplicates or copypasta."""
    path = RAW / f"full_{sub}_{year}.jsonl"
    if not path.exists():
        return []
    seen, rows = set(), []
    for line in open(path, encoding="utf-8"):
        try:
            c = json.loads(line)
        except json.JSONDecodeError:
            continue  # a line cut off when a download was interrupted
        if c["id"] not in seen:
            seen.add(c["id"])
            if len(emoji_tokens(c["body"])) <= MAX_EMOJI:
                rows.append(c)
    return rows
