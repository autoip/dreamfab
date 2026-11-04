# 聞 · News `news/`

Two kinds of show on one channel, with one AI anchor:
- **The daily brief**: vertical (1080x1920), about a minute; the sections below.
- **In-depth reports**: 16:9, 3-6 minutes; [the last section](#in-depth-reports-3-6-minutes-169).

The daily brief:
- An AI anchor opens and closes on camera, lip-synced; cards carry the numbers in between.
- Subtitles and a theme tune run throughout.

The first show is a one-minute US-markets brief for Taiwan, out before the Taiwan market opens.

**Upload**:
- With no channel in the show's settings it makes files only.
- With a channel (`CHANNEL`), `upload` puts the brief on it; `PRIVACY` decides whether it goes public.
- A system scheduler can also run it unattended every day, from news to upload (see the last section).

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
  - Words the voice misreads go in `SAY` in `series.py`: a same-length, same-sounding swap that changes only what is read, never the subtitle, applied before the narration is sent. E.g. 光纖→光仙, 供給→供擠, 叢集→從集, 瓶頸→瓶錦, 重啟→崇啟. Add each new misreading `check` finds ([when the AI voice misreads a word](../PRONUNCIATION.md)).
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
  - The date leads, large on a yellow banner (`DATE` turned into 「11/3 週二」, or `COVER_DATE`): a daily show must show its day even in a phone's small tile.
  - The Shorts shelf and a channel's Shorts tab show the video's first frame, not the uploaded thumbnail, so use `COVER_FRAME`, and run `cover` before `render`.
  - Two big hook lines go above her: the day's biggest number first (red up, green down), then a question.
  - One line below her carries the next two stories.
- **SEO** (`SEO` in `day.py`):
  - Titles A, B and C all open on the hook: a number plus a twist or a question, e.g. "Palantir revenue up 96%, still down after hours?". The show's name and the date go at the end.
  - The description runs: the lead, one line per story (taken from the subtitles), sources, the AI and no-advice notes, the sponsor, hashtags.
  - The sections are laid out like the other lines' `YouTube_SEO.txt`. In the pilot nothing is published; it is a file.

### 5. Asking for the subscription
`CTA_LINE` in `series.py` is the anchor's last line, e.g. 「記得訂閱，每天開盤前看美股一分鐘，養成習慣，掌握財金動脈！」:
- `new` puts it last in every script.
- While she says it, the strap changes to `CTA`.
- The end card leads with a subscribe button and the `SUBSCRIBE` line, with the sponsor below.
- `SEO_FOOT` carries the same ask into the description.

### 6. Delivery and upload
The brief is `out/<NAME>_<YYYYMMDD>.mp4`, `.zh-TW.srt`, `_cover.jpg` and `_SEO.txt`.
```
python news/make.py upload DAY            # PRIVACY in series.py decides (private when unset); --public / --private override it
```
- It goes to `series.py`'s `CHANNEL` with that channel's own login (`YT_TOKEN`, see [SETUP](../SETUP.md)), so it cannot land on another channel.
- It uses title A, the description, tags, subtitles and the cover; `CATEGORY` defaults to 25 (News & Politics).
- The channel's daily cap (`youtube.daily_max`) still applies. `out/youtube.json` keeps the id, so a second run uploads nothing.
- **Cover**: the channel must be verified before it can use custom thumbnails; until then the cover is skipped with a note. The Shorts shelf picks its own frame, so `COVER_FRAME = 0.3` makes the first 0.3 s the cover, with no subtitle over it.

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
  - Any start after 05:15 works. 美股一分鐘 starts at 06:30 and is out about 16 minutes later, still off-peak, with time to redo before the Taiwan open.

## Unattended: made and uploaded every day
Give the time in `series.py`, put it in the system's scheduler once, and from then on each episode is made and uploaded with no one there:
```python
DAILY = dict(at="06:30", days="mon-fri", latest="08:30")   # when, which days (the computer's local time), and too late after
```
```
python news/make.py schedule SHOW --dry-run   # what it would schedule; changes nothing
python news/make.py schedule SHOW             # schedule it: Windows Task Scheduler; cron on macOS and Linux
python news/make.py schedule SHOW --remove    # take it away
python news/make.py daily SHOW --test         # only checks that Claude Code starts; no credits
python news/make.py daily SHOW                # what the scheduler runs each day; fine by hand too
```
What it does:
- **From the news to the upload in one go**: `daily` has Claude Code (`claude -p`) work through steps 1 to 6 above under the daily instructions: research, script, cards, cover, SEO, narration, the check, lip-sync, render, upload.
- **The daily instructions are one file**: [news/daily_prompt.md](../../../news/daily_prompt.md) by default, or the show's own (`DAILY` `prompt`); `{DATE}`, `{SHOW}` and `{PY}` are filled in.
  - It says what the user approved when they scheduled it: the day's credits, the upload at `PRIVACY`. And what is off limits: other projects, commits, keys.
  - The agent asks nothing.
- **Narrow permissions**: the shell, file reads and writes, search and the web only (`DAILY` `tools` to change it), one job at a time (`AIP_MAX=1`), every job off-peak (half price).
- **A misread word is fixed once**: when `check` lists a word read wrong, a common word that sounds the same goes into `SAY` and those lines are read again and spliced in.
  - Credits are no reason to skip it, but it is done once, never in a loop; what still sounds off goes in the log for a person to hear.
  - An English name the recogniser writes another way does not count. A narration cut off at the end gets its last line read again the same way.
- **A missed start runs late, a late one is skipped**: Windows starts a run the computer slept through once it is on; a start after `latest` is skipped with a line in the log, so stale news is not made at full price after the off-peak window.
- **No news, no episode**: weekends and market holidays get one line with the reason. Monday covers Friday's close.
- **No duplicates, the cap kept**: `out/youtube.json` keeps the video id, so a rerun does not upload twice; each channel's daily cap still holds.
- **It stops on an error**: a failed step is retried once; if it fails again the run stops and logs the step and the message. Never a half-made upload.
- **A record**: Claude's whole output in the show's `logs/DATE.log`; one entry a day in `daily_log.md`: link, length, credits, minutes per step, words swapped, spots to listen to.

## In-depth reports: 3-6 minutes, 16:9
The same channel and anchor take one story all the way, e.g. "Why Lumentum took off, and why AI runs on light" (3:47, 9 chapters).

- **Research**:
  - Primary sources first: SEC 8-Ks and 10-Ks, company releases, earnings calls. Then cross-check against English media, with every number agreed by two sources.
  - Leave out what sources disagree on, such as whether one company is a given customer's main supplier.
  - Local stocks appear only as "named by analysts", with the no-advice note.
- **Format**: the explainer line ([explain/](../explain/OVERVIEW.md)).
  - In `script.md`, one `###` per chapter under the narration heading. What is read is the subtitle, so numbers are written as words.
  - Misread words get a same-sounding swap in `SAY`, e.g. `("光纖", "光仙")`.
  - `explain/render.py` puts it together: chapter names, the title, source cards (`FACTS`) and the end card.
- **Anchor**:
  - Only the opening and closing parts of the narration go to lip-sync, 31 s at most each, with 0.6 s of silence at the end.
  - They are laid out 16:9, the title on the left and the anchor on the right, and played through `CLIPS`.
  - The opening one starts with a still held as long as the `GAPS` lead, so her lips meet the voice.
- **Pictures**:
  - v4 text-to-image in between (16:9, no text or logos).
  - HTML data cards carry the numbers (a revenue chart, the stock, deal terms, the supply chain), using only figures two sources agree on.
- **Music**: Suno gives two versions of a prompt. Join the two (crossfaded) and an episode has enough; the next episode starts with the other one.
- **Cover**: 16:9. The "in-depth" tag and the date, two or three hook lines, the anchor's face.
- **SEO**: titles open on the hook; the description carries the chapters (from 0:00, each 10 s or longer), the key numbers, sources, and the AI and no-advice notes.
- **Upload**: give the show a `series.py` (`CHANNEL`, `YT_TOKEN`, `PRIVACY`) and the episode folder a `day.py` with `FILE`, and `news/make.py upload` takes it.
  - In-depth reports are not urgent, so `PRIVACY = "private"` is suggested: upload privately, publish after a look.
  - The episode number goes first in the title: `TITLE_PREFIX = "EP{ep}｜"`, `{ep}` being the episode folder's number (`e05_…` gives `EP5｜`); a title in the SEO file that already has it is left alone.
- **Credits** (first episode, measured): narration in two parts 100, ten pictures 200, two lip-syncs 100: 400 submitted now, half off-peak.
