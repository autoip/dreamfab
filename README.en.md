# Dreamfab 造夢廠

**An AI agent framework for making video: say one sentence and you are the director and producer, while an AI agent makes the film you dream of.**

[中文](README.md) | English

Dreamfab is a framework that lets AI agents (Claude Code, Codex, and tested with Grok Bot) make videos on their own. Tell the agent one sentence and it follows a production line's skill: writes the script, submits generation jobs, checks the review sheets, edits, subtitles, mixes and publishes. Every batch of jobs that costs credits is priced first and goes out only when you say so.

- **Production lines**: one line per kind of video, each with its own workflow, formats and skill. A new kind of video is a new line.
- **Generation engines**: pictures, video, voices and lip-sync come from the public [AutoIP](https://autoip.ai) API today (text-to-image, image-to-video, multi-reference video, lip-sync, voice cloning, AI songs); more engines will follow.
- **The shared core** `dreamfab/`: submitting jobs, credits, half-price off-peak runs, local editing and rendering, GPU super resolution and frame generation, the library page, YouTube publishing ([the shared core and the library](docs/en/CORE.md)).

## Lines: 戲・曲・說・廣・影・聞

| Line | Tell the agent | Status | Docs |
|---|---|---|---|
| **戲** short drama `drama/` | Use dreamfab-drama to turn script.md into a short drama | Ready | [Drama overview](docs/en/drama/OVERVIEW.md) |
| **曲** music video `mv/` | Use dreamfab-mv to turn song.mp3 into a music video | Ready | [MV overview](docs/en/mv/OVERVIEW.md) |
| **說** explainer `explain/` | Use dreamfab-explain to explain the history behind my MV in 5 minutes | Ready (static B-roll; moving B-roll planned) | [Explainer overview](docs/en/explain/OVERVIEW.md) |
| **廣** ads `ad/` | Use dreamfab-ad to make ads for my product in Japanese, Korean and English, a different look for each | Ready (products, services, brands; a main cut plus 30 s and 15 s in 16:9, 9:16 and 1:1) | [Ads overview](docs/en/ad/OVERVIEW.md) |
| **聞** news `news/` | Use dreamfab-news to make today's one-minute US-markets brief; make an in-depth report on why Lumentum took off | Ready (new): a daily one-minute vertical brief (an AI anchor opens and closes, cards, a cover and SEO copy, uploaded unattended every day) and 3-6 minute 16:9 in-depth reports | [News overview](docs/en/news/OVERVIEW.md) |
| **影** film | — | Later | — |

Each series is a world of its own (`projects/<series>/`); its actors and voices (`cast/`, `voices/`) are cast again across episodes and seasons with the same face and voice.

## Showcase

**Short drama 《我的室友是楊貴妃》** (My Roommate Is Yang Guifei), made with the drama line: Yang Guifei falls from Mawei into the flat of a talent agent three million in debt. Season one, 10 episodes of about 50 seconds, is all out. <!-- public-ok -->

- ▶ Episode 1: https://youtu.be/kA4J9kLOVVo <!-- public-ok -->
- ▶ The whole season: https://www.youtube.com/playlist?list=PLFDknh7mplug
- 🎵 The same character's MV 《馬嵬》: https://youtu.be/C6aGMU8mKdw (made with the MV line; the drama and the MV link to each other in their descriptions) <!-- public-ok -->

**Music videos**: one MV line, four genres and looks. Click a thumbnail to watch on YouTube.

| **Dark metal epic** | **Wong Kar-wai-style Cantopop ballad** | **Chinese-style duet** | **Cyberpunk female rap** |
|:---:|:---:|:---:|:---:|
| [![《黑日聖殿》](https://img.youtube.com/vi/ErQCd04OGA8/mqdefault.jpg)](https://youtu.be/ErQCd04OGA8) | [![《過期的那一分鐘》](https://img.youtube.com/vi/fMTLkI7qDq8/mqdefault.jpg)](https://youtu.be/fMTLkI7qDq8) | [![《洛川》](https://img.youtube.com/vi/OlIQYvfwZhA/mqdefault.jpg)](https://youtu.be/OlIQYvfwZhA) | [![《科技睪丸》](https://img.youtube.com/vi/fZ9SlclC9ng/mqdefault.jpg)](https://youtu.be/fZ9SlclC9ng) |

A whole season of MVs: the [《國風淒美對唱》 playlist](https://www.youtube.com/playlist?list=PLfoBI7oPycHg), 6 episodes with one look and packaging, a different genre each.

**AI-automated news**: market news from the news line, with one AI anchor; the daily one-minute brief is researched, written, voiced, carded and uploaded by a scheduled run with no one there.

- ▶ The channel, AutoIP財經新聞, one a day, all in Shorts: https://www.youtube.com/@AutoIP%E8%B2%A1%E7%B6%93%E6%96%B0%E8%81%9E/shorts
- ▶ A one-minute US-markets brief before the Taiwan open, made and uploaded unattended every day: https://youtu.be/NupJ10Z46xg
- ▶ An in-depth report, why Lumentum took off and why AI runs on light (3:47): https://youtu.be/SR1r42OAaXg

## Install

### On a computer: one line (Claude Code / Codex)

**macOS / Linux / Git Bash:**

```bash
curl -fsSL https://raw.githubusercontent.com/autoip/dreamfab/main/install.sh | bash
```

**Windows PowerShell:**

```powershell
irm https://raw.githubusercontent.com/autoip/dreamfab/main/install.ps1 | iex
```

Four lines are installed by default (drama, MV, explainer, ads); add `news` for the news line (e.g. `DREAMFAB_LINES=drama,mv,explain,ad,news`); for short dramas only, set `DREAMFAB_LINES=drama`. Plugin install, ffmpeg (with libass), fonts and `AUTOIP_API_KEY`: see [SETUP.md](docs/en/SETUP.md).

**Updating**: run the same line again. Your work and settings stay as they are, and an older version's databases come in by themselves; for plugin installs and your own clone, see [SETUP.md, Updating from an older version](docs/en/SETUP.md#7-updating-from-an-older-version).

### On a phone: Grok Bot (tested)

On your phone, tell Grok Bot `install https://github.com/autoip/dreamfab`. It reads the install script first, installs everything on its own machine, then asks for your AutoIP API key. No PC needed: the factory runs from your phone.

<img src="docs/images/grok_bot_install.jpg" width="300" alt="On a phone, Grok Bot is told to install github.com/autoip/dreamfab; it reads the install script and starts installing">

That machine has no GPU, and it doesn't matter: generation runs in the AutoIP cloud, editing, subtitles and mixing need only the CPU, and the GPU only speeds up optional steps. Publishing to YouTube needs a Google sign-in on that machine; that step hasn't been tested yet.

## The library page

`python dreamfab/library.py serve projects` opens a local web page with every episode, shot, character, credit and upload status of every series, and plays the videos. See [the shared core and the library](docs/en/CORE.md#the-local-library-page).

![Home: the flow on top, then the drama, MV and explainer lines, each episode at its station](docs/images/library_home_lines.jpg)

![Warehouse: a drama series, one shelf per season, ▶ uploaded or waiting](docs/images/library_home_store_drama.jpg)

![Warehouse: the MV and explainer series; a dashed slot is an episode still on a line](docs/images/library_home_store_mv.jpg)

## Docs

| Doc | Contents |
|---|---|
| [SETUP.md](docs/en/SETUP.md) | Install, GPU, API key, off-peak pricing, YouTube login, rights to your material, updating from an older version |
| [Drama](docs/en/drama/OVERVIEW.md)・[MV](docs/en/mv/OVERVIEW.md)・[Explainer](docs/en/explain/OVERVIEW.md)・[Ads](docs/en/ad/OVERVIEW.md)・[News](docs/en/news/OVERVIEW.md) overviews | Each line's workflow, format, editing, publishing, lessons |
| [The shared core and the library](docs/en/CORE.md) | Series folders, the library page, what each file in `dreamfab/` does |
| [WORKFLOW.md](docs/en/WORKFLOW.md) | Workflow switches: which steps happen on their own is your call |
| [GPU_ENHANCE.md](docs/en/GPU_ENHANCE.md) | Local super resolution + frame generation: tools, measured speed and results |
| [PRONUNCIATION.md](docs/en/PRONUNCIATION.md) | When the AI voice misreads a word: finding it, the swap table `SAY`, what to read again, the table we use |
| [CONTRIBUTING.en.md](CONTRIBUTING.en.md) | Contributing: what belongs in the repo, de-identification, the check before you send |

## Where it is going

More generation engines (one line switching engines to compare quality and price), more production lines (film 影) and more news shows, and fuller agent automation: from one sentence to publishing, with people stepping in only before spending credits and before going public.

## Licence

[MIT](LICENSE). What you make with Dreamfab is yours; use only material you have the rights to (see [SETUP.md, Rights to your material](docs/en/SETUP.md#6-rights-to-your-material)).
