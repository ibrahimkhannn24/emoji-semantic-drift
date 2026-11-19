"""Figures for the presentation: white background, larger text.

Reads only saved results, so it runs in seconds.

Usage: python src/slide_figures.py
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import FIGURES, RESULTS

OUT = FIGURES / "slides"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#898781", "#e6e6e6", "#b5b5b5"
NEG, POS = "#e34948", "#2a78d6"

plt.rcParams.update({
    "font.family": ["Segoe UI", "Segoe UI Emoji"], "font.size": 14,
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "lines.linewidth": 3, "savefig.dpi": 220, "savefig.bbox": "tight",
})


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.png")
    plt.close(fig)


def drift():
    d = pd.read_csv(RESULTS / "drift_teenagers_1yr.csv")
    years = sorted(d.period.unique())
    fig, ax = plt.subplots(figsize=(9, 4.6))
    for e, c in zip(["💀", "😭", "🙏"], SERIES):
        s = d[d.emoji == e].set_index("period").emoji_percentile.reindex(years)
        ax.plot(years, s.values, color=c, marker="o", markersize=7, label=e)
    for e, ls in [("😂", "--"), ("❤", ":")]:
        s = d[d.emoji == e].set_index("period").emoji_percentile.reindex(years)
        ax.plot(years, s.values, color=MUTED, linestyle=ls, linewidth=2, label=f"{e} control")
    ax.set_ylabel("Distance from 2025 meaning\n(percentile among emoji)")
    ax.set_ylim(-3, 103)
    ax.set_xticks(years)
    ax.legend(frameon=False, ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.1), fontsize=15)
    save(fig, "drift")


def before_after():
    d = pd.read_csv(RESULTS / "over_time_comparison.csv")
    d = d[d.community == "Pooled"].set_index("item")
    order = ["ALL", "😂", "❤", "🔥", "😩", "🙏", "💀", "😭"]
    d = d.loc[order]
    fig, ax = plt.subplots(figsize=(8, 5))
    y = np.arange(len(d))
    for i, row in enumerate(d.itertuples()):
        ax.plot([row.cost_early, row.cost_late], [i, i], color=GRID, linewidth=6, zorder=1,
                solid_capstyle="round")
    ax.scatter(d.cost_early, y, s=130, color=MUTED, zorder=3, label="2016-17")
    ax.scatter(d.cost_late, y, s=130, color=SERIES[1], zorder=3, label="2024-25")
    ax.set_yticks(y, ["All 7" if i == "ALL" else i for i in d.index], fontsize=20)
    ax.get_yticklabels()[0].set_fontsize(14)
    ax.axvline(0, color=AXIS, linewidth=1.5)
    ax.set_xlabel("Accuracy change from reading the emoji (points)")
    ax.grid(axis="y", visible=False)
    ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=14)
    save(fig, "before_after")


def cost():
    d = pd.read_csv(RESULTS / "lexicon_error_teenagers.csv")
    d = d[(d["item"] != "none") & (d.n >= 20)].sort_values("emoji_cost")
    d["item"] = d["item"].replace("ALL emoji", "All")
    fig, ax = plt.subplots(figsize=(6.2, 6.4))
    ax.barh(d["item"], 100 * d.emoji_cost, color=[NEG if v < 0 else POS for v in d.emoji_cost],
            height=0.65)
    for y, v in enumerate(d.emoji_cost):
        ax.annotate(f"{100 * v:+.0f}", (100 * v, y), xytext=(5 if v >= 0 else -5, 0),
                    textcoords="offset points", va="center", ha="left" if v >= 0 else "right",
                    fontsize=12, color=INK2)
    ax.tick_params(axis="y", labelsize=18)
    for t in ax.get_yticklabels():
        if t.get_text() == "All":
            t.set_fontsize(13)
    ax.axvline(0, color=AXIS, linewidth=1.5)
    ax.set_xlim(-30, 30)
    ax.set_xlabel("Accuracy change from reading the emoji (points)")
    ax.grid(axis="y", visible=False)
    save(fig, "cost_teenagers")


def coverage():
    fig, ax = plt.subplots(figsize=(8, 4.4))
    for tag, name, ls in [("teenagers", "r/teenagers", "-"), ("memes", "meme subs", "--")]:
        d = pd.read_csv(RESULTS / f"coverage_{tag}.csv")
        for col, lex, c in [("missing_esr", "ESR", INK), ("missing_vader", "VADER", MUTED)]:
            ax.plot(d.period, 100 * d[col], color=c, linestyle=ls, marker="o", markersize=6)
            ax.annotate(f"{lex}, {name}: {100 * d[col].iloc[-1]:.0f}%",
                        (len(d) - 1, 100 * d[col].iloc[-1]), xytext=(10, 0),
                        textcoords="offset points", va="center", fontsize=12, color=c)
    ax.set_ylabel("Emoji uses with no score (%)")
    ax.set_ylim(0, 36)
    save(fig, "coverage")


def repair():
    """VADER accuracy on 2024-25 emoji posts: as shipped, emoji removed, emoji scores updated."""
    r = pd.read_csv(RESULTS / "repair_test.csv").set_index("scale").loc[2.0]
    labels = ["VADER as shipped", "Emoji removed", "Emoji scores\nupdated"]
    vals = [r.acc_vader, r.acc_text_only, r.acc_repaired]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    bars = ax.bar(labels, vals, color=[NEG, MUTED, POS], width=0.6)
    for b, v in zip(bars, vals):
        ax.annotate(f"{v:.1f}%", (b.get_x() + b.get_width() / 2, v), xytext=(0, 6),
                    textcoords="offset points", ha="center", fontsize=16, color=INK)
    ax.set_ylabel("Accuracy on 1,334 emoji posts (%)")
    ax.set_ylim(0, 62)
    ax.grid(axis="x", visible=False)
    save(fig, "repair")


NUDGE = {("memes", "🙏"): (-9, 0), ("teenagers", "❤"): (9, -4), ("memes", "🔥"): (-9, 0),
         ("teenagers", "🔥"): (9, -2)}  # label offsets where points crowd


def direction():
    """Change in the gap between use and VADER's score vs change in cost, 2016-17 to 2024-25."""
    d = pd.read_csv(RESULTS / "direction_test.csv")
    fig, ax = plt.subplots(figsize=(8, 4.4))
    ax.axhline(0, color=AXIS, linewidth=1.2)
    ax.axvline(0, color=AXIS, linewidth=1.2)
    for r in d.itertuples():
        c = NEG if r.gap_change > 0 else POS
        m = "o" if r.community == "teenagers" else "s"
        ax.scatter(r.gap_change, r.cost_change, s=110, color=c, marker=m, zorder=3, edgecolors="white", linewidths=1)
        dx, dy = NUDGE.get((r.community, r.emoji), (8, 0))
        ax.annotate(r.emoji, (r.gap_change, r.cost_change), xytext=(dx, dy), textcoords="offset points",
                    fontsize=15, va="center", ha="left" if dx > 0 else "right")
    ax.set_xlabel("Change in gap between use and VADER's score\n(right = moved away from VADER)")
    ax.set_ylabel("Change in VADER cost (points)")
    ax.scatter([], [], s=80, color=MUTED, marker="o", label="r/teenagers")
    ax.scatter([], [], s=80, color=MUTED, marker="s", label="meme subs")
    ax.legend(frameon=False, loc="lower left", fontsize=12)
    save(fig, "direction")


def direction_groups():
    """Average change in VADER cost, 2016-17 to 2024-25, for emoji that moved away from VADER's score vs the rest."""
    d = pd.read_csv(RESULTS / "direction_test.csv")
    away, rest = d[d.gap_change > 0], d[d.gap_change <= 0]
    labels = ["Moved away from\nVADER's score (e.g. 😭)", "Moved closer or stayed\n(e.g. 😩)"]
    vals = [away.cost_change.mean(), rest.cost_change.mean()]
    fig, ax = plt.subplots(figsize=(8, 4.4))
    bars = ax.bar(labels, vals, color=[NEG, POS], width=0.55)
    for b, v in zip(bars, vals):
        ax.annotate(f"{v:+.1f} pts", (b.get_x() + b.get_width() / 2, v), xytext=(0, -8),
                    textcoords="offset points", ha="center", va="top", fontsize=17, color=INK)
    ax.axhline(0, color=AXIS, linewidth=1.5)
    ax.set_ylabel("Change in VADER accuracy\n2016-17 to 2024-25 (points)")
    ax.set_ylim(-32, 4)
    ax.tick_params(axis="x", labelsize=15)
    ax.grid(axis="x", visible=False)
    save(fig, "direction_groups")


def ages():
    """Share of posts using each drifting emoji NON-literally, 2024-25, by community age."""
    emoji = ["😭", "💀", "🙏"]
    groups = [("r/teenagers", "scored_posts_teenagers", "#d9c9ee"),
              ("Over-30 subs", "scored_posts_older", "#9b72cf"),
              ("45+ subs", "scored_posts_older45", "#5a2d91")]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    x = np.arange(len(emoji))
    for k, (name, f, c) in enumerate(groups):
        d = pd.read_csv(RESULTS / f"{f}.csv")
        vals = [100 - 100 * d[d["item"] == e].literal.mean() for e in emoji]
        bars = ax.bar(x + (k - 1) * 0.26, vals, width=0.24, color=c, label=name)
        for b, v in zip(bars, vals):
            ax.annotate(f"{v:.0f}%", (b.get_x() + b.get_width() / 2, v), xytext=(0, 5),
                        textcoords="offset points", ha="center", fontsize=13, color=INK)
    ax.axhline(50, color=AXIS, linewidth=1.2, linestyle="--")
    ax.set_xticks(x, emoji, fontsize=20)
    ax.set_ylabel("Posts using the emoji non-literally (%)")
    ax.set_ylim(0, 112)
    ax.set_yticks(range(0, 101, 20))
    ax.grid(axis="x", visible=False)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.12), ncol=3, fontsize=13)
    save(fig, "ages")


if __name__ == "__main__":
    for make in (drift, before_after, cost, coverage, repair, direction, direction_groups, ages):
        make()
    print("written to", OUT)
