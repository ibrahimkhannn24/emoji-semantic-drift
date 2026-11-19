"""Figures for one community.

Usage: python src/figures.py <tag> <subreddit> [subreddit ...]
  e.g. python src/figures.py teenagers teenagers
       python src/figures.py compare      (community comparison, after both tags)
"""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from common import CONTROLS, FIGURES, RESULTS, TARGETS, emoji_tokens, load

# Colour palette for a light background, checked for colour-blind contrast
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS, SURFACE = "#e1e0d9", "#c3c2b7", "#fcfcfb"
NEG, POS = "#e34948", "#2a78d6"

plt.rcParams.update({
    "font.family": ["Segoe UI", "Segoe UI Emoji"], "font.size": 10,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "lines.linewidth": 2, "savefig.dpi": 200, "savefig.bbox": "tight",
})

FOCUS = ["💀", "😭", "🙏"]


def save(fig, name, tag):
    fig.savefig(FIGURES / f"{name}_{tag}.png")
    plt.close(fig)


def emoji_share(tag, subs):
    """Comments per 1,000 containing each item, per year (random sample only)."""
    path = RESULTS / f"emoji_share_{tag}.csv"
    if path.exists():
        return pd.read_csv(path, index_col=0)
    rows = {}
    for y in range(2016, 2026):
        comments = [c for s in subs for c in load(s, y)]
        sets = [set(emoji_tokens(c["body"])) for c in comments]
        rows[y] = {i: 1000 * sum(i in s for s in sets) / len(sets) for i in TARGETS + CONTROLS}
    out = pd.DataFrame(rows).T
    out.to_csv(path, encoding="utf-8")
    return out


def fig_growth(tag, subs):
    share = emoji_share(tag, subs)
    fig, ax = plt.subplots(figsize=(7, 3.6))
    for e, c in zip(FOCUS + ["😂"], SERIES):
        ax.plot(share.index, share[e], color=c, marker="o", markersize=4, label=e)
    ax.set_ylabel("Comments containing emoji (per 1,000)")
    ax.set_title("How often each emoji is used, by year", loc="left", fontsize=11)
    ax.legend(frameon=False, ncol=4, loc="upper left")
    ax.set_xticks(share.index)
    save(fig, "growth", tag)


def fig_drift(tag):
    """Raw distance to the reference shrinks for every token as the period
    approaches it, so the comparable measure is the rank among emoji."""
    d = pd.read_csv(RESULTS / f"drift_{tag}_1yr.csv")
    years = sorted(d.period.unique())
    fig, ax = plt.subplots(figsize=(7, 3.6))
    for e, c in zip(FOCUS, SERIES):
        s = d[d.emoji == e].set_index("period").emoji_percentile.reindex(years)
        ax.plot(years, s.values, color=c, marker="o", markersize=5, label=e)
    for e, ls in [("😂", "--"), ("❤", ":")]:
        s = d[d.emoji == e].set_index("period").emoji_percentile.reindex(years)
        ax.plot(years, s.values, color=MUTED, linestyle=ls, linewidth=1.5, label=f"{e} (control)")
    ax.set_ylabel("Distance from 2025 meaning\n(percentile among emoji)")
    ax.set_ylim(-3, 103)
    ax.set_title("How far each emoji is from its 2025 meaning", loc="left", fontsize=11)
    ax.legend(frameon=False, ncol=5, loc="lower left", fontsize=9)
    save(fig, "drift", tag)


def fig_cost(tag):
    d = pd.read_csv(RESULTS / f"lexicon_error_{tag}.csv")
    d = d[(d["item"] != "none") & (d.n >= 20)].sort_values("emoji_cost")
    d["item"] = d["item"].replace("ALL emoji", "All emoji posts")
    fig, ax = plt.subplots(figsize=(6.5, 0.32 * len(d) + 1))
    colors = [NEG if v < 0 else POS for v in d.emoji_cost]
    ax.barh(d["item"], 100 * d.emoji_cost, color=colors, height=0.6)
    for y, (v, n) in enumerate(zip(d.emoji_cost, d.n)):
        ax.annotate(f"{100 * v:+.0f}  (n={n})", (100 * v, y), xytext=(4 if v >= 0 else -4, 0),
                    textcoords="offset points", va="center", ha="left" if v >= 0 else "right",
                    fontsize=8, color=INK2)
    ax.axvline(0, color=AXIS, linewidth=1)
    ax.set_xlabel("Accuracy change from VADER's emoji handling (percentage points)")
    ax.set_title("VADER's emoji handling: small gains on some emoji, large losses on others",
                 loc="left", fontsize=11)
    ax.tick_params(axis="y", labelsize=13)
    for t in ax.get_yticklabels():
        if t.get_text() == "All emoji posts":
            t.set_fontsize(9)
    ax.grid(axis="y", visible=False)
    lim = 100 * d.emoji_cost.abs().max() + 12
    ax.set_xlim(-lim, lim)
    save(fig, "lexicon_cost", tag)


def fig_valence(tag):
    d = pd.read_csv(RESULTS / f"lexicon_error_{tag}.csv")
    d = d[(d["item"] != "none") & (d["item"] != "ALL emoji") & (d.n >= 20)].sort_values("human_valence")
    fig, ax = plt.subplots(figsize=(6.5, 0.36 * len(d) + 1))
    y = np.arange(len(d))
    for col, label, c, m in [("human_valence", "Labelled posts, 2024-25", SERIES[0], "o"),
                             ("esr_score", "Emoji Sentiment Ranking (2015)", SERIES[1], "s"),
                             ("vader_alone", "VADER (emoji alone)", SERIES[2], "D")]:
        ax.scatter(d[col], y, color=c, marker=m, s=42, label=label, zorder=3,
                   edgecolors=SURFACE, linewidths=1)
    for i, row in enumerate(d.itertuples()):
        vals = [v for v in (row.human_valence, row.esr_score, row.vader_alone) if not np.isnan(v)]
        ax.plot([min(vals), max(vals)], [i, i], color=GRID, linewidth=2, zorder=1)
        if np.isnan(row.esr_score):
            ax.annotate("not in ESR", (1.02, i), va="center", fontsize=7, color=MUTED,
                        xycoords=("axes fraction", "data"))
    ax.set_yticks(y, d["item"], fontsize=13)
    ax.axvline(0, color=AXIS, linewidth=1)
    ax.set_xlim(-1, 1)
    ax.set_xlabel("Sentiment (-1 negative, +1 positive)")
    ax.set_title("What the lexicons say vs how the emoji is used now", loc="left", fontsize=11)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3, fontsize=8)
    ax.grid(axis="y", visible=False)
    save(fig, "valence", tag)


def fig_coverage(tag):
    d = pd.read_csv(RESULTS / f"coverage_{tag}.csv")
    fig, ax = plt.subplots(figsize=(6, 3.2))
    for col, label, c in [("missing_esr", "Emoji Sentiment Ranking", SERIES[1]),
                          ("missing_vader", "VADER", SERIES[0])]:
        ax.plot(d.period, 100 * d[col], color=c, marker="o", markersize=5, label=label)
        ax.annotate(f"{100 * d[col].iloc[-1]:.0f}%", (len(d) - 1, 100 * d[col].iloc[-1]),
                    xytext=(6, 0), textcoords="offset points", va="center", fontsize=9, color=INK2)
    ax.set_ylabel("Emoji uses with no lexicon entry (%)")
    ax.set_title("Share of emoji the lexicons cannot score", loc="left", fontsize=11)
    ax.legend(frameon=False, loc="upper left")
    ax.set_ylim(0, None)
    save(fig, "coverage", tag)


def fig_link(tag):
    drift = pd.read_csv(RESULTS / f"drift_{tag}_2yr.csv")
    early = drift.dropna(subset=["drift"]).sort_values("period").groupby("emoji").first()
    err = pd.read_csv(RESULTS / f"lexicon_error_{tag}.csv").set_index("item")
    d = early.join(err, how="inner")
    d = d[d.n >= 20]
    rho, p = spearmanr(d.emoji_percentile, d.emoji_cost)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(d.emoji_percentile, 100 * d.emoji_cost, s=60, color=SERIES[0],
               edgecolors=SURFACE, linewidths=1, zorder=3)
    for e, row in d.iterrows():
        ax.annotate(e, (row.emoji_percentile, 100 * row.emoji_cost),
                    xytext=(7, 0), textcoords="offset points", va="center", fontsize=12)
    ax.axhline(0, color=AXIS, linewidth=1)
    ax.set_xlabel("Drift since earliest period with data\n(percentile among emoji)")
    ax.set_ylabel("Accuracy change from VADER's\nemoji handling (points)")
    ax.set_title(f"Drift vs lexicon error (Spearman ρ = {rho:.2f}, p = {p:.2f}, n = {len(d)})",
                 loc="left", fontsize=11)
    save(fig, "link", tag)
    d[["period", "drift", "emoji_percentile", "emoji_cost", "acc_vader", "acc_vader_text", "n"]] \
        .to_csv(RESULTS / f"link_{tag}.csv", encoding="utf-8")


def fig_compare(tags=("teenagers", "memes"), names=("r/teenagers", "r/memes + r/dankmemes")):
    """Cost of VADER's emoji handling per emoji, side by side for the two communities."""
    d = pd.concat([pd.read_csv(RESULTS / f"lexicon_error_{t}.csv").assign(tag=t) for t in tags])
    d = d[(d["item"] != "none") & (d.n >= 20)]
    wide = d.pivot(index="item", columns="tag", values="emoji_cost").dropna()
    wide = wide.sort_values(tags[0])
    wide.index = wide.index.str.replace("ALL emoji", "All emoji posts")
    fig, ax = plt.subplots(figsize=(6.5, 0.36 * len(wide) + 1))
    y = np.arange(len(wide))
    for i, (_, row) in enumerate(wide.iterrows()):
        ax.plot(100 * row.values, [i, i], color=GRID, linewidth=2, zorder=1)
    for t, name, c, m in zip(tags, names, SERIES, ["o", "s"]):
        ax.scatter(100 * wide[t], y, color=c, marker=m, s=46, label=name, zorder=3,
                   edgecolors=SURFACE, linewidths=1)
    ax.set_yticks(y, wide.index, fontsize=13)
    for t in ax.get_yticklabels():
        if t.get_text() == "All emoji posts":
            t.set_fontsize(9)
    ax.axvline(0, color=AXIS, linewidth=1)
    ax.set_xlabel("Accuracy change from VADER's emoji handling (percentage points)")
    ax.set_title("Same emoji, two communities", loc="left", fontsize=11)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2, fontsize=9)
    ax.grid(axis="y", visible=False)
    fig.savefig(FIGURES / "compare_communities.png")
    plt.close(fig)
    wide.to_csv(RESULTS / "compare_communities.csv", encoding="utf-8")


def neighbour_table(tag):
    d = pd.read_csv(RESULTS / f"drift_{tag}_2yr.csv").dropna(subset=["drift"])
    t = d[d.emoji.isin(FOCUS + ["😂", "🔥"])].pivot(index="emoji", columns="period", values="neighbours")
    t.to_csv(RESULTS / f"neighbours_{tag}.csv", encoding="utf-8")


if __name__ == "__main__":
    if sys.argv[1] == "compare":
        fig_compare()
        sys.exit()
    tag, subs = sys.argv[1], sys.argv[2:]
    fig_growth(tag, subs)
    for make in (fig_drift, fig_cost, fig_valence, fig_coverage, fig_link, neighbour_table):
        make(tag)
    print("figures written to", FIGURES)
