# 聞 · News `news/` (pilot)

A short vertical news brief every day (1080x1920, about a minute):
- An AI anchor opens and closes on camera, lip-synced; cards carry the numbers in between.
- Subtitles and a theme tune run throughout.

The first show is a one-minute US-markets brief for Taiwan, out before the Taiwan market opens.

**This is a pilot**:
- It makes files only. There is no news channel and no platform to publish on.
- The flow has no upload or publish step, and nothing runs on a daily schedule yet.

[中文](../../zh-TW/news/OVERVIEW.md) | English

## A show's folder

```
projects/<show>/
  series.py                   the show: file names, the top bar, anchor, voice, theme tune, fixed opening and closing
                              lines, the sponsor's end card
  cast/ANCHOR_A.png           the anchor's portrait (9:16, for lip-sync)
  voices/ANCHOR_A.wav         her voice sample
  music/                      the theme (Suno suggested, see below)
  timing.tsv                  minutes per step (every command writes its line)
  2026-11-03/                 one folder a day
    script.md                 one line per sentence: "spoken｜subtitle｜picture"
    day.py                    DATE, SOURCES, CARDS (each card's HTML)
    cards/ voice/ clips/ jobs/
    out/<NAME>_20261103.mp4   the brief + .zh-TW.srt
```

Example: [examples/news/demo](../../../examples/news/demo/).

## Starting a show (once)

1. **Anchor**: first make a v4 text-to-image portrait (`size` 540x960, waist-up at a news desk, no text or logos behind her). Then make a 480p, 8 s image-to-video of her saying an opening line, and take the voice from it as her sample.
   - Image-to-video sometimes reads the tone directions in the prompt out loud, so cut the clean part only.
   - In the 11/03 pilot she said "steady, moderate pace" first, so the sample starts at 3.1 s.
2. **Theme**: as in the ad line, the agent writes the Suno style (`music/suno.md`) and the user generates the track in Suno.
   - Measure the whole bars that may repeat and put them in `MUSIC_LOOP`; `render` stretches the tune to the brief's length.
3. **series.py**: fill it in like [the example](../../../examples/news/demo/series.py).

## Every day

### 1. The news: English sources first
English outlets have their closing story within 15 minutes of the US close. Chinese-language reports come an hour or two later and often miss after-hours earnings, oil settlements and economic data.

In the 11/03 pilot, English sources first turned up three stories no Chinese report carried:
- Palantir's after-hours results
- Brent and WTI settlement prices
- the ISM manufacturing index

| What | Look first at |
|---|---|
| Index closes | the closing post of CNBC's live blog; AP "How major US stock indexes fared"; Reuters |
| Biggest movers and why | CNBC, Reuters, MarketWatch, TheStreet |
| After-hours earnings | the company's release (BusinessWire, SEC 8-K), CNBC |
| Oil | the Reuters / AP settlement story |
| Economic data | the official release: ISM, BLS, the Fed |
| Taiwan's own numbers | the night session of TAIEX futures (TAIFEX or MoneyDJ's after-hours close), the index, TSMC ADR: only these from Chinese-language media |

- **Every number from two sources that agree.** When they don't, check a quote page's historical close. On 11/03 one English source had Intel at −5.19%; it closed −8.80%.
- **No advice.** Report what happened; never tell anyone to buy or sell.

### 2. The script
- `python news/make.py new projects/<show> 2026-11-04` starts the day.
  - `day.py` is copied from the day before, with the date already changed.
  - `script.md` already holds the fixed first and last lines.
- **Length**: one line per sentence. About 11 lines and 280 characters make a minute (5.2 characters a second, measured).
- **Spoken column**:
  - Numbers are written out as words.
  - US indexes and company names are said in English: Dow Jones, Oracle, Intel, Apple, Palantir…
  - Taiwanese companies stay in Chinese: 台積電, 聯電.
  - Avoid words with two readings: 重啟 is often read zhòng qǐ, so write 恢復 or 再度展開 instead.
- **Subtitle column**: numbers in digits, names in Chinese.
- **Picture column**: `anchor` or a card id. Consecutive lines with the same card keep it on screen.
- **Cards**: build them in `day.py` from `row()` (an index or a price), `bar()` (a bar for a move) and `box()` (a point).
  - Red is up and green is down, as in Taiwan.
  - Companies appear as names and numbers only: no logos, no photos of real people.
- **Credits at the end**: the sources must be listed, along with "anchor and voice are AI-generated" and "for information only, not investment advice".

### 3. Making it
```
python news/make.py cards  DAY
python news/make.py voice  DAY
python news/make.py submit DAY voice --off-peak      # narration
python news/make.py check  DAY                       # transcript; words heard differently
python news/make.py anchor DAY                       # only the anchor's two parts
python news/make.py submit DAY lipsync --off-peak    # lip-sync
python news/make.py render DAY
```
- **Lip-sync gets only the anchor's two parts** (opening and close, about 8 s together): three times faster than the whole narration, same credits.
  - Lip-sync clips usually come back half a second short, so the audio sent gets 0.6 s of silence at the end.
  - Where the clip runs out, the full-screen sponsor card takes over.
- **A few lines read wrong**: read just those lines again and put them back into the narration.
  ```
  python news/make.py redo   DAY 4 9               # read lines 4-9 again (the first line is 1)
  python news/make.py submit DAY redo
  python news/make.py splice DAY 4 9               # cut at the pauses, at least 0.3 s each
  ```
  - If the anchor's parts did not change, the lip-sync is kept.
  - The old narration stays in `voice/narr_prev.flac`.
  - When the new take gets only a word or two wrong, mix the two takes by hand.

### 4. Cover and SEO: one hook
```
python news/make.py cover DAY        # out/<NAME>_cover.jpg
python news/make.py seo   DAY        # out/<NAME>_SEO.txt
```
- **Cover** (`COVER` in `day.py`):
  - The anchor's picture moves down so her face stays in the middle, clear of the text.
  - Two big hook lines go above her: the day's biggest number first (red up, green down), then a question.
  - One line below her carries the next two stories.
- **SEO** (`SEO` in `day.py`):
  - Titles A, B and C all open on the hook: a number plus a twist or a question, e.g. "Palantir revenue up 96%, still down after hours?". The show's name and the date go at the end.
  - The description runs: the lead, one line per story (taken from the subtitles), sources, the AI and no-advice notes, the sponsor, hashtags.
  - The sections are laid out like the other lines' `YouTube_SEO.txt`. In the pilot nothing is published; it is a file.

### 5. Delivery
In the pilot it is files only: `out/<NAME>_<YYYYMMDD>.mp4`, `.zh-TW.srt`, `_cover.jpg`, `_SEO.txt`.

## Speed and credits (11/03 pilot, measured)

| Step | Minutes |
|---|---|
| The news (English sources, queries sent together) | 1 |
| Script and cards | about 10 |
| Narration (about 300 characters) | 2.3 |
| Lip-sync (about 8 s of anchor) | 0.9 |
| Cards and render | 1.8 |
| **Total** | **about 15** |

- **Credits**: narration 50 and lip-sync 50 a day; submitted off-peak (03:00-09:00 Taiwan time) they cost half, 50 in all.
  - Starting a show adds the anchor's portrait (v4, 20) and her voice test (image-to-video 480p 8 s, 48).
- **Timing**: the US market closes at 05:00 Taiwan time (04:00 in US summer time), and so does the TAIEX futures night session.
  - Starting at 05:15 gives a finished brief around 05:30, at the off-peak price, with time to redo before the Taiwan open.
