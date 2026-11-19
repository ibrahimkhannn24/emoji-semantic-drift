# Emoji Semantic Drift and the Cost to Lexicon-Based Sentiment Analysis

DSC3013 Social Media Analytics, Group 3 (City University of Hong Kong).

This repository holds the code, labels and results for our study of how emoji meanings on Reddit changed between 2016 and 2025, and how much that change costs two lexicon-based sentiment tools, VADER and the Emoji Sentiment Ranking (ESR).

## What is in the repository

| Folder | Contents |
| --- | --- |
| `src/` | All analysis scripts (Python) |
| `data/labels/` | The labelled posts, the labelling guide (`labelling_guide.md`) and the post samples |
| `results/` | Every number reported in the report and slides, as CSV files |
| `figures/` | Figures; `figures/slides/` holds the presentation versions |

The raw Reddit comments (about 3 million, roughly 520 MB) and the trained embedding models are not included because of their size. `src/collect.py` downloads the comments again from the Arctic Shift archive, and `src/drift.py` retrains the models.

## Scripts, in the order they run

| Script | What it does | Main output |
| --- | --- | --- |
| `common.py` | Shared settings: emoji list, periods, cleaning rules | used by all scripts |
| `collect.py` | Downloads comments from Arctic Shift using random one-day windows | `data/raw/` |
| `drift.py` | RQ1: trains a word2vec model per period, aligns them, measures each emoji's distance from its 2025 position | `results/drift_*.csv` |
| `label_sample.py` | Draws the posts to be labelled | `data/labels/sample_*.csv` |
| `lexicon_error.py` | RQ2: scores labelled posts with VADER (with and without emoji) and ESR | `results/lexicon_error_*.csv`, `results/scored_posts_*.csv` |
| `intervals.py` | Bootstrap 95% confidence intervals for the costs | `results/cost_confidence_intervals.csv` |
| `over_time.py` | 2016-17 versus 2024-25 comparison | `results/over_time_comparison.csv` |
| `coverage.py` | Share of emoji uses with no lexicon entry | `results/coverage_*.csv` |
| `why_error.py` | Direction test and repair test | `results/direction_test.csv`, `results/repair_test.csv` |
| `older_users.py` | Comparison with over-30 and 45+ subreddits | `results/older*_vs_teens*.csv` |
| `figures.py`, `slide_figures.py` | Figures | `figures/` |

## Reproducing the results

```bash
pip install -r requirements.txt
python src/collect.py full <requests_per_year> teenagers       # download (slow)
python src/collect.py full <requests_per_year> memes dankmemes
python src/drift.py teenagers 1yr teenagers
python src/drift.py teenagers 2yr teenagers
python src/drift.py memes 1yr memes dankmemes
python src/drift.py memes 2yr memes dankmemes
python src/lexicon_error.py data/labels/labelled_teenagers.csv
python src/lexicon_error.py data/labels/labelled_memes.csv
python src/lexicon_error.py data/labels/labelled_teenagers_2016-17.csv
python src/lexicon_error.py data/labels/labelled_memes_2016-17.csv
python src/intervals.py
python src/over_time.py
python src/why_error.py
```

Everything after the download uses a fixed random seed (42 for the embeddings, 0 for the bootstraps), so the same data gives the same numbers.
