---
name: dreamfab-news
description: >
  Make a short daily vertical news brief with Dreamfab's news line (`news/`, a pilot): English sources first, every
  number checked against a second source, a script with numbers spelled out, an AI anchor who opens and closes on
  camera (lip-sync of her two parts only), cards for the numbers, subtitles, the show's theme, a cover and SEO copy that
  open on the same hook. Files only: nothing is uploaded or published.
  Use when the user wants a daily news brief / 新聞 / 每日美股 / 盤前快報 / 一分鐘新聞 / AI 主播, or mentions
  dreamfab-news, 造夢廠 新聞, 聞.
---

# Dreamfab · news (聞・新聞, pilot)

One folder per show (`projects/<show>/`, settings in `series.py`), one folder per day (`YYYY-MM-DD/`). Everything runs
through `news/make.py`; read `ROOT/docs/en/news/OVERVIEW.md` before the first day of a new show.

## 0. Locate the toolkit

1. `ROOT` = `$DREAMFAB_HOME`, else `~/.dreamfab`. If this skill's base directory is `<repo>/skills/dreamfab-news` and
   `<repo>/news/make.py` exists, you may use `<repo>` instead.
2. If `ROOT/news` is missing, install with `DREAMFAB_LINES=news` (and `DREAMFAB_AGENTS=none`):
   - macOS / Linux / Git Bash:
     `curl -fsSL https://raw.githubusercontent.com/autoip/dreamfab/main/install.sh | DREAMFAB_LINES=news DREAMFAB_AGENTS=none bash`
   - Windows PowerShell:
     `$env:DREAMFAB_LINES='news'; $env:DREAMFAB_AGENTS='none'; irm https://raw.githubusercontent.com/autoip/dreamfab/main/install.ps1 | iex`
3. `PY` = `ROOT/.venv/bin/python` (Windows: `ROOT/.venv/Scripts/python.exe`). `ffmpeg` with libass, and Edge or Chrome
   for the cards (`DREAMFAB_BROWSER`). `AUTOIP_API_KEY` is set by the user; never read keys from elsewhere, write them
   into files or echo them.

## Hard rules

- **Pilot: files only.** No upload, no publishing, no scheduled run unless the user sets one up and says so.
- **Credits are charged on submit and there is no cancel.** Before the first job of a day (and before any extra
  re-read) give the price now and off-peak (03:00-09:00 Taiwan time, half; `submit … --off-peak`) and wait for a yes,
  unless the user has approved a standing daily run. One job at a time.
- **English sources first, then two sources for every number.** CNBC's live blog, AP, Reuters, MarketWatch, company
  releases and SEC 8-Ks, official data (ISM, BLS, the Fed). Chinese-language media only for local numbers (for Taiwan:
  the TAIEX futures night session, the index). When two sources disagree, check a quote page's historical close. Never
  invent a number, a reason or a quote.
- **News, not advice.** No buy or sell calls, no price targets of your own. The end card always lists the sources and
  says the anchor and voice are AI-generated and that it is not investment advice.
- **No logos, no real people's pictures.** Companies appear as names and numbers. The anchor is a made-up person
  (text-to-image portrait, her voice from an image-to-video line); never clone a real person's face or voice.

## Every day

1. `PY ROOT/news/make.py new projects/<show> YYYY-MM-DD`: `day.py` is copied from the day before (date changed);
   `script.md` has the fixed first and last lines.
2. Research (send the searches together; it takes about a minute) and write `script.md`, one line per sentence:
   `spoken｜subtitle｜picture`.
   - About 11 lines and 280 characters make a minute.
   - Spoken: numbers as words; company and index names in English (Dow Jones, Oracle, Apple…); local companies in the
     local language; avoid words with two readings (in Chinese, 重啟 → 恢復).
   - Subtitle: digits, local names.
   - Picture: `anchor` for the first and last line, card ids in between.
3. `day.py`:
   - `SOURCES` and `CARDS`, built with `row()`, `bar()` and `box()`; red up and green down for Taiwan.
   - `COVER`: two hook lines (the biggest number, then a question) plus one line of the next stories.
   - `SEO`: titles A/B/C that open on the same hook, a lead, tags.
4. `cards`, `cover`, `seo` (no credits). Show the cards and the cover before spending anything.
5. `voice` → `submit voice` → `check`. Listen to every spot `check` lists. English names are often written otherwise
   by the recogniser, so do not re-read on the transcript alone.
6. `anchor` → `submit lipsync` (only her two parts, about 8 s) → `render`.
7. A line read wrong: `redo DAY FIRST LAST` → `submit redo` → `splice DAY FIRST LAST`. The lip-sync is kept when her
   lines did not change. If only a word of the new take is wrong, mix old and new by hand at the pauses.
8. Report:
   - the files: `out/<NAME>_<YYYYMMDD>.mp4`, `.zh-TW.srt`, `_cover.jpg`, `_SEO.txt`
   - the length and the credits spent
   - the spots to listen to
   - the minutes per step (`timing.tsv`)
