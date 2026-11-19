# Labelling guide (codebook)

How every post in `data/labels/` was labelled. The same rules were used for all sets: r/teenagers and the meme subreddits (2016-17 and 2024-25), and the over-30 and 45+ subreddits (2024-25).

**Who labelled:** one AI model (Claude), reading each post in full and applying the rules below. The model knew the study's hypothesis. A blind recheck by the same model of 40 random posts agreed with the original labels 80% of the time for sentiment (kappa 0.69) and 88% for literal use (kappa 0.75); see `results/label_recheck.csv`. Labelling by human annotators is left for future work.

Each post gets two labels.

## 1. Sentiment: `pos`, `neu` or `neg`

How the **writer** feels in the post as a whole, taking the emoji and the words together.

- **pos:** the writer is happy, amused, excited, approving, affectionate or thankful.
  - "U almost had me lol😭💀" (laughing)
  - "Thank you so much!! 🙏❤️"
- **neg:** the writer is sad, angry, annoyed, worried, disgusted, or mocking a real person or group (see the rule below).
  - "This economy is so bad im 29 at home still 😭"
  - "Trash advice 😂" (mocking another commenter)
- **neu:** no clear feeling: plain information, a question, a mixed post with no side winning, or a playful joke about oneself.
  - "October 16🙏"
  - "people think I'm smart but I'm just good at remembering Wikipedia articles 😭😭😭"

**The mockery rule (rule A).** Mocking a real person or group counts as **negative**, even when it's funny. A playful, self-aware joke counts as **neutral**. For 🤓: negative if someone else is cast as the nerd, neutral if the writer means themselves.

**Borderline cases.** When a post sits between neutral and positive or negative, judge by the overall tone the writer seems to intend. These borderline cases are where most disagreements happened in the recheck.

## 2. Literal use: `1` or `0`

`1` if the post uses the emoji (the one the post is filed under, in the `item` column) in its **dictionary sense**, otherwise `0`. Posts with no emoji get `0`.

| Emoji | Literal (`1`) means | Literal example | Non-literal example |
| --- | --- | --- | --- |
| 😭 | actually sad, upset or crying | "RIP D.L. 😭" | "U almost had me lol😭💀" (laughing) |
| 💀 | death, dying or skeletons | "doot doot 💀🎺🎺🎺"; "Step on this in the dark and next you dead 💀" | "Lmao 💀" ("I'm dead" from laughing) |
| 🙏 | praying, pleading, hoping or wishing someone well | "god bless 🙏"; "Praying for you 🙏🏻" | "Thank you 🙏" (thanks); "REAL 🗣️🙏🔥🔥" (hype) |
| 😩 | tired, weary, frustrated or upset | "No one reads 😩" | "That new 21 pilots shirt is sick 😩" (desire, hype) |
| 🔥 | actual fire or heat | "my AC literally still runs 75% of the day… 😭🔥🔥" | "this entire album was 🔥" (great) |
| ❤ | love or affection | "I love that man of mine. ❤️" | "I ❤️NY logo" |
| 😂 | laughing | always literal in our data | none |
| 🙂 | genuinely content or pleased | "happy birthday🙂" | "Well, i wear glasses but im not that smart🙂" (ironic) |
| 🤡 | an actual clown, or a clown reference | "...ICP 🤡💥🪓" | calling someone or something foolish |
| 🗿 | the Moai statue itself | "are you disguising as a moai rock🗿" | "im also 13 frfr 🗿" (deadpan) |
| 🧢 | an actual cap or hat | none found | "No cap 🚫🧢" ("no lie") |
| 🫠 | melting or crumbling | "Crumbling away🫠" | "15f 5'7… 47kg 🫠" (awkward, overwhelmed) |
| 🥲 | smiling through sadness, bittersweet | "I'm so sorry my blud 🥲 If you wanna talk, I am here for you" | "'Why do woman exist' WHAT!🥲" |
| 🥀 | wilting, loss or melancholy | "…because small feet looks girlish🥀" | "🥀💔🔥🙏☝️ Kowalski analysis" (meme) |
| 🗣 | shouting, speaking or announcing | "NO 🗣️🙏🏾🙏🏾🔥🔥🔥🔥🗣️" | "City of evil 🗣️🔥🔥" (hype) |
| 🤓 | sincere nerdy or pedantic correction | a genuine factual correction ending in 🤓 | "Nuh uh: Eleventeen 🤓☝️" (parodying the nerd meme) |
| 🫵 | pointing at or directly addressing "you" | "that is a decision only u can make 🫵🫵🫵" | "Object 🫵😹" |

For the newer emoji (🙂 to 🫵), what counts as "literal" is less settled, so their literal labels are less reliable than those for the seven core emoji. The study's literal-use results (slides 10 and 16) use only the core emoji.

## File format

`labels_<set>.csv` has three columns: `id` (the Reddit comment id), `label` (`pos`, `neu` or `neg`) and `literal` (`1` or `0`). Each labels file is merged with its `sample_<set>.csv` (the post text) into `labelled_<set>.csv`, which the analysis scripts read.
