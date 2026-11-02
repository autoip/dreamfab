# 廣 Ads `ad/`

Turn a product, a service or a brand into an ad, **in several markets at once**, each language in its own look
(documentary, variety show, keynote, cinematic). Every version gets:

- a main cut of 1–2 minutes
- 30 s and 15 s cuts
- 16:9, 9:16 and 1:1 sizes
- two caption files with each video: the market's language and Chinese

The result is delivered as files, not uploaded.

The ad line renders with the explain line's program ([explain/](../explain/OVERVIEW.md) `render.py`) and adds these
tools:
- starting a campaign: `ad/new.py`
- style packs: `ad/styles.py`
- cards: `ad/cards.py`
- website screenshots: `ad/capture.py`
- rendering a whole campaign with its delivery list: `ad/render.py`

[中文](../../zh-TW/ad/OVERVIEW.md) | English

## A campaign's folder

```
projects/<brand>/<campaign>/
  brief.md                    the brief: filled in with the user before any script; checked line by line before delivery
  voices/raw/ voices/NARR_JA.wav ...   one narrator per language (text-to-video, then the voice taken from it)
  fonts/                      subtitle fonts that are not installed
  ja_documentary/             one market version = one folder (language_pack)
    project.py  script.md  images/  voice/  jobs/
    out/<NAME>.mp4            the main cut (16:9) + .ja.srt, .zh-TW.srt
    out/<NAME>_30.mp4         a shorter cut (one per CUTS entry)
    out/<NAME>_15.mp4  out/<NAME>_15sq.mp4
  ko_variety/  en_keynote/ ...
  delivery.md                 every file with its size, length, loudness and caption files
```

Example: [examples/ad/demo](../../../examples/ad/demo/).

## Three kinds of ad

| Kind | For | Default cards (`ad/new.py --kind`) |
|---|---|---|
| `product` | something you can hold: a drink, skincare, an appliance | hero shot, three features, price and where to buy, end card |
| `service` | an app, a platform, a shop, a course | hero (a screenshot of the site), how it works, features, end card |
| `brand` | a feeling, a promise | the promise, a customer's words, a wall of moments, end card |

## Style packs

Every market gets its own look, not a copy of the last language's. `python ad/styles.py` lists them:

| Pack | Look | Narrator | Music to ask for |
|---|---|---|---|
| `documentary` | navy and gold, a soft dark strip under the subtitles | calm, warm | cinematic future bass, piano |
| `variety` | bright gradient, a tilted white card, yellow subtitles with a thick edge, stickers with sounds | bright, laughing | funky, brass, handclaps |
| `keynote` | white and spare, huge heavy type, one blue, subtitles on white boxes | clear, confident | minimal electronic |
| `cinematic` | black bars, a warm grade, a vignette, thin subtitles | soft | piano, strings |

A pack only fills `project.py` when the campaign is started; change anything afterwards.

## Steps

Before every batch that costs credits, give the price now and off-peak, and wait for a yes.

1. **Start and brief**:
   ```bash
   python ad/new.py projects/<brand>/<campaign> --kind product --langs ja:documentary,ko:variety,en:keynote
   ```
   This writes `brief.md` and a folder per market. Fill in `brief.md` with the user: who it is for, three points, the proof, what the viewer should do, the lengths, what must not be said.
2. **Look samples**: for each market, set one picture in two or three looks for the user to choose from (drawn locally, no credits). Write the pick into `STYLE` and its fields.
3. **Script** `script.md`: in that language, `> Chinese` under every line. One line is one subtitle (it fits on one row). Hook the viewer in the first three seconds. Every claim must trace back to the brief's proof: who made the music, the numbers, whether it is free.
4. **Narration**: for each language, use text-to-video to have a new narrator say one line, then cut 5–15 s of it as `VOICE`. Match the delivery to the pack (lively for variety, crisp for keynote). Then run:
   ```bash
   python explain/narration.py P jobs && python dreamfab/aip_runner.py P/jobs/voice_jobs.json
   python explain/narration.py P check
   ```
   Voice v3 (`voxcpm2`) reads the text in whatever language it is written in.
5. **Pictures** (the explain line's `SHOTS`):
   - **Existing work**: put video clips in `CLIPS` and write `"key:second"` in `SHOTS`.
   - **The product**: text-to-image v4 product shots, or image-to-video to make them move.
   - **The website**: `python ad/capture.py URL images/site_ja.png --lang ja --hide-corner`. Use move `frame` for a white page so the subtitles stay readable.
   - **Cards**: `python ad/cards.py P` draws `CARDS` as `images/<id>.png`.
6. **Music: Suno is recommended**. Suno has no API open to ordinary users, so the agent writes and the user pastes:
   - **The agent writes `suno.md`** (every version starts with a draft): a title, the Style of Music (the pack's suggestion rewritten for this ad's mood), Exclude styles and the length. A bed under the narration is Instrumental; for a jingle that sings the brand, write lyrics too (`[Intro]`, `[Hook]`, `[Outro]`, sung in the market's language, the brand, promise and address as in the brief).
   - **The user pastes it into Suno** (Custom mode), picks one, downloads it into `music/` and the file goes in `MUSIC`.
   - The ad must not say the music was made with AutoIP.
   - **All automatic, without Suno**: AutoIP's composer, `/voice/song` (30 credits); then the ad may say its music came from AutoIP. A long piece sometimes comes back a few seconds long (150 s asked, 2.6 s and 6.5 s returned): measure it first.
   - Without `CH_MUSIC` the music plays straight through. If a piece is too short, loop its middle sections on the beat.
7. **Render** (no credits):
   ```bash
   python ad/render.py projects/<brand>/<campaign>     # every market: the main cut, each CUTS entry, then delivery.md
   python explain/render.py P --cut 30                 # one cut only
   ```
   `CUTS = {"30": dict(clips=[("from these words", "up to these"), ...], aspect="16:9"), "15": dict(..., aspect="9:16", head=("head line",))}`:
   - `16:9` keeps the main cut's look.
   - `9:16` and `1:1` set the picture across the middle, with subtitles hanging below it.
8. **Check and deliver**: tick every line of the brief's checklist and give the user the narration's list of words to listen to. `delivery.md` lists every file with its size, length, loudness (−14 to −16 LUFS) and caption files. In the library (`python dreamfab/library.py serve projects`) the front page has the 廣 line, with a card per market.

## project.py (fields the ad line adds)

| Field | Meaning |
|---|---|
| `LINE = "ad"` | the library counts it on the ad line |
| `STYLE` | the style pack (`ad/styles.py`); the cards take their colours from it |
| `CARDS` | cards: `[dict(id=, kind=, ...)]`, see below |
| `CARD_FONTS` | the cards' fonts: `dict(head=, body=, zh=, web=["Google Fonts family"])` |
| `CUTS` | shorter cuts: clips, size, head line |
| `GAPS` | tighter than an explainer by default: 0.8 s lead, 0.6 s between chapters, 2.2 s title, 3.5 s end |
| `CHAPTER_LABELS = False` | no chapter names on screen (the default for a new campaign; a 30 s ad needs none) |
| `FILM` | cinema look: `dict(bars=130, warm=0.08, vignette=0.35)` black bars (16:9 only), a warm grade, a vignette |

Everything else as on the explain line: `SCRIPT`, `VOICE`, `NARRATION`, `SHOTS`, `CLIPS`, `SUBS`, `CARD`, `STICKERS`, `LABELS`, `MUSIC`, ... ([the explain line's project.py](../explain/OVERVIEW.md#projectpy)).

## Card kinds (`ad/cards.py`)

Text stays above y 760, clear of the subtitles. Each card can carry `zh="Chinese"`.

| `kind` | Fields | Draws |
|---|---|---|
| `hero` | `title`, `sub`, `image`, `tag` | a big headline beside the product or a screenshot |
| `features` | `title`, `items=[(head, line, zh)]` | three or four boxes in a row |
| `steps` | `title`, `sub`, `steps=[(word, zh)]`, `note` | numbered boxes with arrows |
| `prompt` | `lines=[(me/ok/q/zh, text)]` | a terminal: a request and the agent's replies |
| `wall` | `title`, `files=[path or glob]`, `cols`, `ratio` | a grid of covers or thumbnails |
| `quote` | `text`, `who` | a customer's words |
| `offer` | `title`, `price`, `note`, `cta` | a price and a call to action |
| `end` | `brands=[(name, address, zh)]`, `line` | the end card |

## Lessons

- **A new look for every language**: the same film with new subtitles does not feel made for its viewers. A different look and voice (the Korean version as a teasing variety show, say) does more than translation.
- **Claims must hold**: if the music came from Suno, the ad cannot say the music was made with AutoIP; only say what AutoIP's composer can do.
- **Music from Suno**: Suno has no API for ordinary users; the agent writes `suno.md` (style, lyrics) and the user pastes it in. AutoIP's composer is all automatic, but measure what comes back.
- **Screenshot the site in the right language**: a site's `/locale/ja` link usually only sets a cookie the headless browser drops; `--lang ja` makes the browser itself ask for Japanese. `--hide-corner` covers the reCAPTCHA badge.
- **White pages go in the frame**: white subtitles vanish on a white page across the whole picture; framed, they sit on the dark around it.
- **Fonts**: subtitle fonts must be installed (libass cannot use web fonts); cards are web pages and can use Google Fonts. Korean lines break at spaces, Japanese and Chinese at commas.
- **Two subtitles must not overlap**: by even a moment, and libass lifts the later one a whole line, so the subtitles jump around. The renderer ends each line before the next begins.
