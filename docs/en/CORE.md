# The shared core and the library

[中文](../zh-TW/CORE.md) | English

The code every production line shares is in `dreamfab/`; every series lives in `projects/`.

## Series folders: parallel universes and a virtual troupe

- **Parallel universes**: each series is a world of its own in `projects/<series>/`, one folder and one `project.py` per episode or song.
- **A virtual troupe**: `projects/<series>/cast/` and `voices/` are that world's actors and voices, cast again across episodes and seasons with the same face and voice.
- **The library**: one local web page for every episode, shot, character, credit and upload of every world; see the next section.

## The local library page

After a while your material is spread over dozens of folders: every episode's `project.py`, shots, voices, job records, cuts, covers and upload records. The library turns every series under `projects/` into one local web page where you browse, play and search them, without digging through folders.

```bash
python dreamfab/library.py serve projects     # opens http://127.0.0.1:8765
python dreamfab/library.py list projects      # just lists the series it finds and their line
```

**Home is the factory floor.** The top row is the flow: one sentence → AI agent → production lines ⇄ generation engines → warehouse → YouTube, each with its numbers (in the making, finished, uploaded).

**Production lines**: one conveyor each for drama (戲), MV (曲) and explainer (說), with that line's stations (drama: script → storyboard → generation → cut → cover; explainer: script → narration → pictures → cut → cover). Every episode still being made sits at the first station it has not passed and links to its page; a line with work on it runs, its rollers turning and parcels riding into the warehouse. Film (影) and news (聞) are lines still to come.

![Home: the flow on top, then the drama, MV and explainer lines, each episode at its station](../images/library_home_lines.jpg)

**Warehouse**: a rack per series and a shelf per season, each episode standing on it by its cover, marked ▶ uploaded or waiting (待上架); one still on a line keeps a dashed slot that names its station. A rack's name opens that series' library. Folders that are not a series yet are under "loose items" (散件區).

**Stock and shipping**: per line, how many videos are made but not uploaded, uploaded but not public, and public (long videos and Shorts apart), and how many the channel put out each day of the last week and can still put out today (the cap is the workflow switch `youtube.daily_max`; 6 a day or fewer is wise, so the channel is not throttled). Publishing done by hand in Studio shows up after `python dreamfab/youtube_log.py sync`.

![Warehouse: a drama series, one shelf per season, ▶ uploaded or waiting](../images/library_home_store_drama.jpg)

![Warehouse: the MV and explainer series; a dashed slot is an episode still on a line](../images/library_home_store_mv.jpg)

- **Drama series**: every episode's cover, length, shot count, credits and YouTube status; an episode page has the cut, every shot's lines with the speech-recognition match and clip thumbnails; cast, sets and job credits are all there. See [Drama overview, Library page](drama/OVERVIEW.md#library-page).
- **MV series**: every episode's cut, stills, clips (old takes and candidates too), characters, lyrics, edit list, credits and uploads. See [MV overview, Library page](mv/OVERVIEW.md#library-page).
- **Explainer series**: one card per episode showing how far it is along script → narration → pictures → cut → covers → upload. An episode page has the cut with its chapters (click one to jump there), covers A/B/C, every picture with its note, the narration, the full script and the YouTube title and description; the series page also lists the shared narrator voice and each MV's instrumental.
- **Other folders**: open `/files/<path>` and a folder becomes a page, with players for audio, video and images and Markdown shown inline. Add `?raw` to an explainer page for the plain file listing.
- Video and audio can be scrubbed, so you can review a cut or a narration right in the browser.
- It listens on `127.0.0.1` only. Drama and MV indexes live in the shared database `~/.config/dreamfab/dreamfab.db` (outside the repo) and re-index while the page is open; explainer pages read the folders every time, so new files show up at once.
- Paste addresses straight into the conversation: when the agent finishes an episode it answers with a library link for you to review, and you can paste an episode's or a shot's link back to say what to change.

## Reading the numbers: YouTube Analytics

`python dreamfab/youtube_analytics.py pull` fetches the channel's YouTube Analytics (read only); `report` lays it out by line. The first `pull` logs in once more to add read-only analytics to the same saved login (uploads keep working on the old one); the Google Cloud project of the OAuth client needs the YouTube Analytics API enabled (the error gives the page when it is not). YouTube's numbers are about two days behind.

```
python dreamfab/youtube_analytics.py pull
python dreamfab/youtube_analytics.py report --group "短劇=^S\dE\d" --group "合集=完全版" --group "解說=解說" --md report.md
python dreamfab/youtube_analytics.py pull --since 2026-11-03     # after changing openings or titles: only the days since
```

How to read it. In brackets: what our channel showed the first time we looked, three weeks in, and what we changed that day:

1. **Shorts and long videos apart.** Shorts bring views; long videos bring watch time and subscribers (Shorts: 63% of the views but 22% of the watch time; most new subscribers came from long videos).
2. **Each line's median per video, not its total.** One video that takes off skews the total (one Short at 1,245 views; its line's median was 35).
3. **How many are still there at 5%.** A long video that has lost a fifth by 5% has a first-second problem (every MV opened on a 4-second brand card and lost 16–45% by 5%). For videos already out, cut the start in the Studio editor: the link, views and comments stay; uploaded captions move with it; chapters in the description you move yourself. New MVs: `open_s=0`, brand on the end card only ([mv/PROJECT_FORMAT.md](mv/PROJECT_FORMAT.md)).
4. **Episodes that lose viewers season after season are losing strangers.** A serial's episodes are found in the Shorts feed by people who do not know the show (season 1: 903 views, season 2: 174, season 3: 44), and a title like "three exes team up" only makes sense to regulars. Title: who plus the conflict; a premise banner across the top of the picture (`TYPO["banner"]`, [drama/PROJECT_FORMAT.md](drama/PROJECT_FORMAT.md)); one or two episodes a day, not five at once.
5. **Search terms.** The report marks the search terms no title has yet; put them in titles (our viewers searched for the poems, legends and idioms behind the songs, and for the genre, "time-travel drama"). Change the copy generators too (`make_seo.py`, `YouTube_SEO.txt`), or the next `--refresh` puts the old title back. A video in a title "Test & compare" cannot have its title changed by the API until the test ends.
6. **Countries.** A country with many views but under 6 seconds each is the Shorts feed showing you to people who do not understand the language; they pull the completion rate down.
7. **Drop what does nothing.** End screens, cards and Shorts "Related video" links brought views in single digits. Still set Related video right (11 MV Shorts had none and one pointed to a different song).
8. **Outside sites.** GitHub's README brought 93 views, more than many videos did; keep the best-performing videos in it.
9. **Look again a week after a change.** `pull --since the day of the change` shows only what came after it. While samples are small, conclusions are hypotheses.

## The files in `dreamfab/`

| File | What it does |
|---|---|
| `aip_runner.py` | Submits AutoIP jobs, polls, downloads; resumable, one at a time, `--off-peak` submits only in the half-price window |
| `util.py` | Project loading, ffmpeg, the NVIDIA encoder (used whenever available), credit estimates |
| `enhance.py` | The engine for local NVIDIA 2x super resolution + 60 fps frame generation (each line's `enhance.py` calls it): [GPU_ENHANCE.md](GPU_ENHANCE.md) |
| `library.py` | The local library page for every series (see the section above) |
| `youtube_api.py`, `youtube_playlists.py` | YouTube login (with a channel lock; read-only analytics is asked for only by `analytics()`), playlist tidying |
| `youtube_analytics.py` | YouTube Analytics (read only): `pull` fetches the numbers per video and for the channel, `report` lays them out by line (see the section above) |
| `db.py` | The shared database: every line's and every series' library index and the publishing log in one SQLite file, `~/.config/dreamfab/dreamfab.db` (`show` lists it; an older version's per-series `library.db` files and `youtube_log.db` come in by themselves, `merge` brings them all in at once; see [SETUP.md, Updating from an older version](SETUP.md#7-updating-from-an-older-version)) |
| `youtube_log.py` | The publishing log (table `youtube_log` of the shared database): upload, update, publish, comment, pin, end screen, card, links between episodes, each with its time (the uploaders record their own steps; what is done by hand in Studio is added with `add`); `sync` checks with YouTube (read only: what went public, and uploads made by hand in Studio), `stats` lists each day's output and the stock; the library's home page (stock and shipping, the log) and explainer pages read it |
| `workflow.py` | Workflow switches: off-peak only, tasks at once, the explainer's Short, GPU enhance, upload privacy, the publishing log, each on or off; one file for you, another per series if it differs ([WORKFLOW.md](WORKFLOW.md)) |
| `credits.py` | Audit: what each job folder actually cost |
| `check_public.py` | The de-identification check before you send: keys, personal data, the words of your own work |
| `gpu_check.py`, `make_static_font.py` | What this machine's GPU can take over; static font weights for libass |
