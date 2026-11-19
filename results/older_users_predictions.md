# Older-user comparison: predictions written before collecting data

Written 2026-11-15, before any comments from the older subreddits were downloaded
beyond a 12-day probe used only to count emoji (no labels, no scores).

Question: in 2024-25, is the ironic use of emoji seen on r/teenagers mainly a
young-community pattern?

Older communities: r/AskWomenOver30, r/AskMenOver30, r/AskOldPeople (pooled).
Same seven emoji as the before/after comparison: 😭 💀 🙏 😩 🔥 ❤ 😂.
Same labelling rule (rule A) and the same scorers as for r/teenagers.

If the pattern is specific to young users, the older communities will show, compared
with r/teenagers 2024-25:

1. 😭 used literally (sad or upset) more often than on r/teenagers (12%).
2. 😂 posts more positive on average than on r/teenagers (+0.20).
3. All seven emoji pooled: a higher mean label and a higher literal share than
   r/teenagers (0.26 and 35%).
4. A smaller loss from VADER's emoji handling than on r/teenagers (-6.8 points
   on the same seven emoji).

The comparison counts as supporting the idea only if most of these hold with
confidence intervals that separate the groups. Otherwise it is reported as not
supported.

## Outcome (added after the comparison, 2026-11-15; predictions above unchanged)

302 older-subreddit posts labelled (rule A). Results in older_vs_teens.csv and
older_vs_teens_balanced.csv.

1. 😭 literal: 24% older vs 12% young (+12, CI -2 to +26). Right direction, not significant.
2. 😂 mean label: +0.18 older vs +0.20 young. Not supported.
3. Five shared emoji, equal weight: literal 51% vs 43% (+8, CI +3 to +14), supported;
   mean label 0.25 vs 0.18 (CI crosses zero), not supported.
4. VADER emoji cost: -0.2 vs -5.6 points (+5.4, CI -2.5 to +13.6). Right direction,
   not significant.

By the rule set above, the idea that ironic use is mainly a young-community pattern
is NOT supported. Older users use these emoji somewhat more literally, but their
😂 posts are just as un-positive, and 76% of their 😭 posts are not literal sadness.

## Second check: 45+ communities (written 2026-11-15, before this data was labelled)

The over-30 subreddits are mostly people in their 30s and 40s. Second older group:
r/GenX (roughly 45 to 60) and r/AskOldPeople (mostly 50+), pooled, 2024-25.
Same seven emoji, same rule, same four predictions and the same decision rule as above,
compared with r/teenagers 2024-25. r/BabyBoomers and r/over50 were checked and have
almost no comments, so they are not used.

## Outcome, 45+ check (added after the comparison, 2026-11-15)

332 posts labelled (rule A; 18 reused from the over-30 set). All seven emoji had at
least 20 posts. Results in older45_vs_teens.csv and older45_vs_teens_balanced.csv.

1. 😭 literal: 30% vs 12% (+18, CI +2 to +34). Supported.
2. 😂 mean label: +0.26 vs +0.20 (CI crosses zero). Not supported.
3. Seven emoji, equal weight: literal 58% vs 35% (+22, CI +17 to +28), supported;
   mean label 0.19 vs 0.25 (CI crosses zero), not supported.
4. VADER emoji cost: -0.5 vs -6.4 points (+5.9, CI -1.1 to +12.8). Right direction,
   not significant.

Partly supported: 45+ users use these emoji clearly more literally, and the gap is
larger than for the over-30 group. But 😂 is used the same mocking way at every age,
and the difference in VADER's loss is not significant. Topic differs too: r/AskOldPeople
has many condolence threads, which raises literal 🙏 (prayer, RIP).
