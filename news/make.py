"""The news line (聞): a short daily news brief in 9:16 (1080x1920). An AI anchor opens and closes on camera (lip-synced),
cards carry the numbers in between, subtitles and a theme tune run throughout. PILOT: it makes files; nothing is
uploaded or published.

usage: python news/make.py new SERIES [YYYY-MM-DD]       a day folder: day.py from the last day (DATE updated),
                                                        script.md with the series' fixed first and last lines
       python news/make.py cards DAY                    draw the cards (HTML in Edge/Chrome, no credits)
       python news/make.py cover DAY                    out/<NAME>_cover.jpg: the hook over the anchor, her face kept clear
       python news/make.py seo DAY                      out/<NAME>_SEO.txt: hook titles, description, tags (not published)
       python news/make.py voice DAY                    jobs/voice.json: the whole narration in one job, ending with a
                                                        throwaway line that is cut off at the pause before it
       python news/make.py submit DAY voice|lipsync|redo [--off-peak]   run that job file (dreamfab/aip_runner.py)
       python news/make.py check DAY                    transcribe voice/narr.flac; list words heard differently
       python news/make.py anchor DAY                   only the anchor's lines -> voice/anchor_in.wav (+0.6 s of
                                                        silence: lip-sync clips come back about 0.5 s short),
                                                        clips/anchor_map.json, jobs/lipsync.json (31 s at most)
       python news/make.py redo DAY FIRST [LAST]        jobs/redo.json: read lines FIRST..LAST again (1 = first line)
       python news/make.py splice DAY FIRST [LAST]      put voice/redo.flac in place of those lines, cut at the pauses
                                                        (gaps of 0.3 s at least); the anchor clip is kept
       python news/make.py render DAY                   out/<NAME>_<YYYYMMDD>.mp4 + .zh-TW.srt
       python news/make.py upload DAY [--public|--private]   to series.py's CHANNEL (its own login, YT_TOKEN) with the
                                                        SEO file's title A, description, tags, the subtitles and the
                                                        cover; PRIVACY in series.py, else private; daily cap kept
       python news/make.py daily SERIES [--test]        today's episode with no one there: Claude Code (claude -p)
                                                        works through the show's daily instructions end to end;
                                                        SERIES/logs/DATE.log; --test only checks that Claude starts
       python news/make.py schedule SERIES [--remove] [--dry-run]   run `daily` at DAILY's time on DAILY's days
                                                        (local time): Windows Task Scheduler, cron elsewhere
Every step adds a line to SERIES/timing.tsv (day, step, start, end, minutes): what a daily slot has to fit.

SERIES/series.py (the show; see examples/news/demo):
  NAME = "us_stocks"                 file names: <NAME>_<YYYYMMDD>
  BRAND = ("美股", "1分鐘")           the bar at the top (a tag and a title), with DATE and AI_LABEL
  ANCHOR = "cast/ANCHOR_A.png"       the anchor's picture for lip-sync (9:16)
  VOICE = "voices/ANCHOR_A.wav"      her voice sample (VOICE_FIELDS: more /voice/clone fields)
  MUSIC = "music/theme.mp3"          the theme; MUSIC_LOOP = (start, end) of whole bars that may repeat, MUSIC_BAR = 2.0
  OPEN = (kicker, title)             the strap over the anchor at the start; CLOSE the one at the end
  FIRST_LINE / LAST_LINE             fixed script lines (spoken｜subtitle｜anchor)
  CTA_LINE, CTA = (kicker, title)    the call to subscribe said last, with its own strap
  SAY = [("光纖", "光仙"), ...]        same-length, same-sounding swaps for words the voice misreads (read only)
  SUBSCRIBE = dict(button=, line=)   the end card asks for the subscription first, the sponsor under it
  SPONSOR = dict(kicker=, name=, sub=)   the end card, shown once the anchor clip runs out (or END_CARD = a card id)
  DAILY = dict(at="06:30", days="mon-fri", latest="08:30")   the unattended run (`daily`, `schedule`): its time,
                                     skipped when it starts after `latest`; prompt= the instructions (default
                                     news/daily_prompt.md), task= the scheduler's name for it
  ROTA = {"fri": dict(ANCHOR="cast/ANCHOR_D.png", VOICE="voices/ANCHOR_D.wav"), "2026-11-05": dict(...)}
                                     another anchor (or any setting) on a weekday or a date; a date wins
  TITLE_PREFIX = "EP{ep}｜"           put before the titles (SEO file, upload); {ep} = the episode folder's number
                                     (e05_… -> 5), {date} = the day folder's date as M/D ("{date}｜" -> 11/5｜)
DAY/day.py: DATE, SOURCES, CARDS = {id: html}; row(), bar() and box() are there to build them.
  COVER = dict(lines=[("費半重挫 3.4%", "down"), ("AI 股殺不停？", "gold")], sub="...")   the cover's hook
  SEO = dict(titles=["…", "…"], lead="…", tags=[…])                                 titles open on the same hook
DAY/script.md: one line per sentence, "spoken｜subtitle｜picture" (picture = anchor or a card id; the same card on
consecutive lines stays on screen). Spoken: numbers in words. Subtitle: digits.
"""
import glob, json, os, re, shutil, subprocess, sys, time
from datetime import date, datetime

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
for p in (REPO, os.path.join(REPO, "ad"), os.path.join(REPO, "explain")):
    sys.path.insert(0, p)
from cards import browser  # noqa: E402  (ad/cards.py)

W, H, FPS = 1080, 1920, 30
SUB_Y = 1480          # subtitle centre: below the cards, above the phone's own buttons
GAP = 0.3             # shortest pause left at a splice
WEEK = "一二三四五六日"

CSS = """
@font-face { font-family: Num; src: local("Bahnschrift"); }
* { margin: 0; box-sizing: border-box; }
body { width: 1080px; height: 1920px; font-family: "Microsoft JhengHei", "PingFang TC", "Noto Sans TC", sans-serif;
  color: #eef3ff; overflow: hidden; }
.bg { position: absolute; inset: 0; background: radial-gradient(120% 70% at 50% 18%, #1b2f57 0%, #0b1426 62%, #070d1a 100%); }
.grid { position: absolute; inset: 0; opacity: .10;
  background-image: linear-gradient(#8fb3ff 1px, transparent 1px), linear-gradient(90deg, #8fb3ff 1px, transparent 1px);
  background-size: 90px 90px; }
.wrap { position: absolute; left: 70px; right: 70px; top: 220px; bottom: 560px; display: flex; flex-direction: column;
  justify-content: center; }
.kick { font-size: 40px; color: #f5c542; font-weight: 700; letter-spacing: 4px; }
h1 { font-size: 92px; line-height: 1.15; font-weight: 900; margin-top: 14px; }
.sub { font-size: 44px; color: #b9c7e6; margin-top: 18px; }
.num { font-family: Num, sans-serif; font-variant-numeric: tabular-nums; }
.up { color: #ff4d4f; } .down { color: #27d17f; }
.row { display: flex; align-items: baseline; justify-content: space-between; padding: 30px 34px; margin-top: 22px;
  background: rgba(19, 33, 61, .88); border: 2px solid #26406f; border-radius: 26px; }
.row.hot { border-color: #27d17f; box-shadow: 0 0 40px rgba(39, 209, 127, .25); }
.row.hot.upx { border-color: #ff4d4f; box-shadow: 0 0 40px rgba(255, 77, 79, .25); }
.row .n { font-size: 52px; font-weight: 700; }
.row .v { font-size: 50px; color: #dfe7fb; }
.row .c { font-size: 64px; font-weight: 700; min-width: 250px; text-align: right; }
.bar { height: 22px; border-radius: 11px; background: #27d17f; margin-top: 12px; }
.bar.up { background: #ff4d4f; }
.box { margin-top: 30px; padding: 36px 40px; border-radius: 28px; background: rgba(19, 33, 61, .9); border: 2px solid #26406f; }
.box .t { font-size: 46px; font-weight: 900; }
.box .d { font-size: 42px; color: #c8d4ee; margin-top: 12px; line-height: 1.45; }
.big { font-size: 200px; font-weight: 700; line-height: 1; margin-top: 40px; }
.note { font-size: 36px; color: #8fa3c8; margin-top: 30px; }
.top { position: absolute; left: 0; right: 0; top: 0; height: 190px; padding: 56px 60px 0;
  background: linear-gradient(#050a14ee, #050a1400); display: flex; justify-content: space-between; align-items: center; }
.brand { font-size: 50px; font-weight: 900; letter-spacing: 2px; }
.brand b { background: #f5c542; color: #0b1426; padding: 4px 16px; border-radius: 12px; margin-right: 14px; }
.date { font-size: 38px; color: #d6e0f5; }
.ai { font-size: 30px; color: #0b1426; background: #cfe0ff; padding: 6px 16px; border-radius: 10px; margin-left: 18px; }
.lower { position: absolute; left: 50px; right: 50px; top: 1150px; padding: 34px 44px; border-radius: 28px;
  background: rgba(8, 16, 34, .86); border-left: 14px solid #f5c542; }
.lower .k { font-size: 38px; color: #f5c542; font-weight: 700; }
.lower .t { font-size: 70px; font-weight: 900; margin-top: 8px; }
.foot { position: absolute; left: 50px; right: 50px; bottom: 120px; font-size: 30px; color: #c3cfe8; line-height: 1.5;
  background: rgba(5, 10, 20, .8); padding: 22px 30px; border-radius: 18px; }
"""


# ---- card helpers for day.py (red up, green down: the Taiwan convention)
def row(name, value, pct, hot=False):
    cls, arrow = ("up", "▲") if pct > 0 else ("down", "▼")
    return (f'<div class="row{" hot" if hot else ""}{" upx" if hot and pct > 0 else ""}"><div><div class="n">{name}</div>'
            f'<div class="v num">{value}</div></div><div class="c num {cls}">{arrow}{abs(pct):.2f}%</div></div>')


def bar(name, pct, note="", hot=False, top=10.0):
    cls, arrow = ("up", "▲") if pct > 0 else ("down", "▼")
    return (f'<div class="row{" hot" if hot else ""}" style="display:block"><div style="display:flex;justify-content:space-between">'
            f'<div class="n">{name}<span class="v" style="font-size:36px;margin-left:16px">{note}</span></div>'
            f'<div class="c num {cls}">{arrow}{abs(pct):.2f}%</div></div>'
            f'<div class="bar {cls}" style="width:{min(100, int(abs(pct) / top * 100))}%"></div></div>')


def imread(path, flags=cv2.IMREAD_COLOR):
    """cv2.imread that also opens paths with CJK characters (Windows)."""
    return cv2.imdecode(np.fromfile(path, np.uint8), flags)


def read_frames(path):
    """(frames, fps) of a video through ffmpeg (cv2.VideoCapture cannot open CJK paths on Windows)."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                        "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip().split(",")
    w, h, (n, dn) = int(r[0]), int(r[1]), r[2].split("/")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
    return list(np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)), float(n) / float(dn)


def box(title, body, cls=""):
    return f'<div class="box"><div class="t {cls}">{title}</div><div class="d">{body}</div></div>'


# ---- loading
def series_of(day):
    return os.path.dirname(os.path.abspath(day))


def settings(f, ns=None):
    """Run series.py or day.py into ns. __file__ is set, so it can read a file next to it, e.g. a SAY table that two
    shows read by the same voice keep together."""
    ns = {} if ns is None else ns
    ns["__file__"] = os.path.abspath(f)
    exec(open(f, encoding="utf-8").read(), ns)
    return ns


def load(day):
    """(settings, script rows): series.py, then ROTA for the day's weekday and date, then day.py over it;
    rows = [spoken, subtitle, picture]."""
    ns = dict(row=row, bar=bar, box=box)
    for f in (os.path.join(series_of(day), "series.py"), os.path.join(day, "day.py")):
        if f.endswith("day.py"):
            when = os.path.basename(os.path.abspath(day))
            weekday = DAYS[datetime.strptime(when, "%Y-%m-%d").weekday()] if re.fullmatch(r"\d{4}-\d\d-\d\d", when) else None
            for k in (weekday, when):   # a guest anchor on a weekday, then on a date
                ns.update(ns.get("ROTA", {}).get(k, {}))
        if os.path.exists(f):
            settings(f, ns)
    rows = [[c.strip() for c in l.split("｜")] for l in open(os.path.join(day, "script.md"), encoding="utf-8").read().splitlines()
            if l.count("｜") == 2 and not l.lstrip().startswith(("#", ">", "每一行"))]
    for r in rows:
        r[0] = say(r[0], ns)
    return ns, rows


def say(text, d):
    """SAY = [(written, said)] in series.py or day.py: a same-length, same-sounding swap for a word the voice misreads
    (光纖 -> 光仙). It changes only what is read; the subtitle column keeps the written word."""
    for written, said in d.get("SAY", []):
        assert len(written) == len(said), f"SAY {written}->{said}: both sides must be the same length"
        text = text.replace(written, said)
    return text


def name_of(day, d):
    stamp = re.sub(r"\D", "", os.path.basename(os.path.abspath(day)))
    return d.get("FILE") or f"{d.get('NAME', 'news')}_{stamp}"


def titled(title, day, d):
    """The title with series.py's TITLE_PREFIX in front: {ep} = the episode folder's number (e05_… -> 5), {date} = the
    day folder's date as M/D (2026-11-05 -> 11/5). Left alone when it is there already; a date still at the end
    (「…｜美股一分鐘 11/5」) moves to the front."""
    pre, base = d.get("TITLE_PREFIX"), os.path.basename(os.path.normpath(day))
    if not pre:
        return title
    ep, iso = re.match(r"e(\d+)_", base), re.fullmatch(r"\d{4}-(\d\d)-(\d\d)", base)
    if "{ep}" in pre and not ep:
        sys.exit("TITLE_PREFIX has {ep}: name the episode folder eNN_…")
    if "{date}" in pre and not iso:
        sys.exit("TITLE_PREFIX has {date}: name the day folder YYYY-MM-DD")
    md = f"{int(iso.group(1))}/{int(iso.group(2))}" if iso else ""
    pre = pre.format(ep=int(ep.group(1)) if ep else "", date=md)
    if title.startswith(pre):
        return title
    if "{date}" in d["TITLE_PREFIX"]:
        title = re.sub(rf"\s*{re.escape(md)}$", "", title)
    return pre + title


def sp(day, *parts):
    return os.path.join(series_of(day), *parts)


def log_time(day, step, t0):
    t1 = time.time()
    line = (f"{os.path.basename(os.path.abspath(day))}\t{step}\t{time.strftime('%H:%M:%S', time.localtime(t0))}\t"
            f"{time.strftime('%H:%M:%S', time.localtime(t1))}\t{(t1 - t0) / 60:.1f}\n")
    path = sp(day, "timing.tsv")
    new = not os.path.exists(path)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(("day\tstep\tstart\tend\tminutes\n" if new else "") + line)
    print(f"[time] {step} {(t1 - t0) / 60:.1f} min")


# ---- new day
def new_day(series, when=None):
    when = when or date.today().isoformat()
    day = os.path.join(series, when)
    if os.path.exists(os.path.join(day, "script.md")):
        sys.exit(f"{day} already has a script.md")
    os.makedirs(os.path.join(day, "jobs"), exist_ok=True)
    days = sorted(d for d in glob.glob(os.path.join(series, "????-??-??")) if os.path.exists(os.path.join(d, "day.py")) and d != day)
    dt = datetime.strptime(when, "%Y-%m-%d")
    label = f"{dt.month}/{dt.day}（{WEEK[dt.weekday()]}）"
    if days:
        src = open(os.path.join(days[-1], "day.py"), encoding="utf-8").read()
        src = re.sub(r'^DATE\s*=.*$', f'DATE = "{label}"', src, flags=re.M)
        print(f"day.py from {os.path.basename(days[-1])}: rewrite SOURCES and CARDS for today")
    else:
        src = f'DATE = "{label}"\nSOURCES = "資料來源：…<br>主播與聲音為 AI 生成｜僅供參考，不構成投資建議"\nCARDS = {{}}\n'
    open(os.path.join(day, "day.py"), "w", encoding="utf-8", newline="\n").write(src)
    ns = settings(os.path.join(series, "series.py"))
    lines = [f"# {when}", "", "每一行三欄，用全形直線隔開：唸的（數字寫國字）、字幕（阿拉伯數字）、畫面（anchor 或 CARDS 的 id）", "",
             ns.get("FIRST_LINE", "早安。｜早安｜anchor"), "", ns.get("LAST_LINE", "以上是今天的新聞。｜以上是今天的新聞｜anchor"),
             *([ns["CTA_LINE"]] if ns.get("CTA_LINE") else []),
             "", "## 資料來源", "- "]
    open(os.path.join(day, "script.md"), "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print(f"{day}: write the news lines between the first and the last line of script.md")


# ---- every day, unattended
DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def daily_settings(series):
    ns = settings(os.path.join(series, "series.py"))
    return dict(dict(at="06:30", days="mon-fri", latest=None, prompt="daily_prompt.md",
                     task="Dreamfab " + os.path.basename(os.path.abspath(series))), **ns.get("DAILY", {}))


def daily(series, test=False):
    """Make today's episode with no one there. Claude Code (`claude -p`) gets the show's daily instructions (DAILY
    prompt in the show folder, else news/daily_prompt.md; {DATE}, {SHOW} and {PY} filled in) and works through them,
    the approvals written there standing in for questions. A start after DAILY latest is skipped: the computer slept
    through its time, the news would be stale and off-peak over. Claude's output goes to SERIES/logs/DATE.log.
    --test only checks that Claude starts (no credits)."""
    cfg, now = daily_settings(series), datetime.now()
    today = now.date().isoformat()
    os.makedirs(os.path.join(series, "logs"), exist_ok=True)
    if not test and cfg["latest"] and now.strftime("%H:%M") > cfg["latest"]:
        with open(os.path.join(series, "daily_log.md"), "a", encoding="utf-8", newline="\n") as f:
            f.write(f"\n== {today}: skipped, started {now:%H:%M} (after {cfg['latest']})\n")
        sys.exit(f"started after {cfg['latest']}: skipped")
    claude = (os.environ.get("DREAMFAB_CLAUDE") or shutil.which("claude")   # the scheduler's PATH may be shorter
              or next((p for p in (os.path.expanduser("~/.local/bin/claude" + x) for x in (".exe", ""))
                       if os.path.isfile(p)), None))
    if not claude:
        sys.exit("claude (Claude Code) not found: install it, or set DREAMFAB_CLAUDE to its path")
    if test:
        prompt = (f"This is a schedule test. Answer only: today's date, the working directory, and whether "
                  f"{sys.executable} exists. Do nothing else.")
    else:
        p = os.path.join(series, cfg["prompt"])
        prompt = open(p if os.path.exists(p) else os.path.join(HERE, "daily_prompt.md"), encoding="utf-8").read()
        for k, v in dict(DATE=today, SHOW=os.path.relpath(os.path.abspath(series), REPO), PY=sys.executable).items():
            prompt = prompt.replace("{" + k + "}", v.replace(os.sep, "/"))
    log = os.path.join(series, "logs", today + ("_test" if test else "") + ".log")
    tools = cfg.get("tools", "Bash,PowerShell,Read,Write,Edit,Glob,Grep,WebSearch,WebFetch")
    with open(log, "a", encoding="utf-8", newline="\n") as f:
        f.write(f"== start {now.isoformat(timespec='seconds')}\n")
        f.flush()
        r = subprocess.run([claude, "-p", prompt, "--allowedTools", tools], cwd=REPO, stdin=subprocess.DEVNULL,
                           stdout=f, stderr=subprocess.STDOUT, env=dict(os.environ, PYTHONIOENCODING="utf-8", AIP_MAX="1"))
        f.write(f"== end {datetime.now().isoformat(timespec='seconds')} exit {r.returncode}\n")
    print(f"{log} (exit {r.returncode})")
    return r.returncode


def schedule(series, remove=False, dry=False):
    """Run `daily` at DAILY at (the computer's local time) on DAILY days ("mon-fri", "mon,wed,fri", "daily").
    Windows: a Task Scheduler task that also starts a missed run once the computer is on (DAILY latest then decides),
    2 hours at most. Elsewhere: a line in the crontab. --remove takes it away; --dry-run prints it, changes nothing."""
    cfg = daily_settings(series)
    d = cfg["days"].lower().replace(" ", "")
    if d in ("daily", "all"):
        days = DAYS
    elif "-" in d and d.count("-") == 1 and set(d.split("-")) <= set(DAYS):
        a, b = d.split("-")
        days = DAYS[DAYS.index(a):DAYS.index(b) + 1]
    else:
        days = d.split(",")
    if not days or not set(days) <= set(DAYS) or not re.fullmatch(r"\d{1,2}:\d{2}", cfg["at"]):
        sys.exit(f'DAILY: at "HH:MM" and days like "mon-fri" (got {cfg["at"]!r}, {cfg["days"]!r})')
    show, me, task = os.path.abspath(series), os.path.abspath(__file__), cfg["task"]
    if os.name == "nt":
        q = lambda x: "'" + x.replace("'", "''") + "'"
        arg = f'-X utf8 "{me}" daily "{show}"'
        names = ",".join(("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")[DAYS.index(x)]
                         for x in days)
        ps = (f"Unregister-ScheduledTask -TaskName {q(task)} -Confirm:$false" if remove else
              f"$a = New-ScheduledTaskAction -Execute {q(sys.executable)} -Argument {q(arg)} -WorkingDirectory {q(REPO)}; "
              f"$t = New-ScheduledTaskTrigger -Weekly -DaysOfWeek {names} -At {cfg['at']}; "
              f"$s = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries "
              f"-DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Hours 2); "
              f"Register-ScheduledTask -TaskName {q(task)} -Action $a -Trigger $t -Settings $s -Force | Out-Null")
        if dry:
            print(ps)
            return
        subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
    else:
        hh, mm = cfg["at"].split(":")
        mark = f"# {task}"
        line = (f"{int(mm)} {int(hh)} * * {','.join(str((DAYS.index(x) + 1) % 7) for x in days)} "
                f'cd "{REPO}" && "{sys.executable}" "{me}" daily "{show}" >/dev/null 2>&1 {mark}')
        old = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout.splitlines()
        new = [l for l in old if not l.endswith(mark)] + ([] if remove else [line])
        if dry:
            print("\n".join(new))
            return
        subprocess.run(["crontab", "-"], input="\n".join(new) + "\n", text=True, check=True)
    print(f"{task}: " + ("removed" if remove else f"{cfg['days']} {cfg['at']} -> news/make.py daily {series}"))


# ---- cards
def page(body, transparent=False):
    bg = "" if transparent else '<div class="bg"></div><div class="grid"></div>'
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{bg}{body}</body></html>'


def shoot(htm, png, transparent=False):
    src = png[:-4] + ".html"
    open(src, "w", encoding="utf-8").write(htm)
    cmd = [browser(), "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={W},{H}",
           "--virtual-time-budget=3000", f"--screenshot={os.path.abspath(png)}"]
    if transparent:
        cmd.append("--default-background-color=00000000")
    subprocess.run(cmd + ["file:///" + os.path.abspath(src).replace("\\", "/")], check=True, capture_output=True)
    os.remove(src)


def cards(day):
    d, _ = load(day)
    out = os.path.join(day, "cards")
    os.makedirs(out, exist_ok=True)
    b1, b2 = d.get("BRAND", ("新聞", ""))
    top = (f'<div class="top"><div class="brand"><b>{b1}</b>{b2}</div><div class="date">{d.get("DATE", "")}'
           f'<span class="ai">{d.get("AI_LABEL", "AI 主播")}</span></div></div>')
    shoot(page(top, True), os.path.join(out, "_top.png"), True)
    for cid, body in d.get("CARDS", {}).items():
        shoot(page(f'<div class="wrap">{body}</div>'), os.path.join(out, f"{cid}.png"))
    for cid, key in (("_open", "OPEN"), ("_close", "CLOSE"), ("_cta", "CTA")):
        if key in d:
            k, t = d[key]
            foot = f'<div class="foot">{d.get("SOURCES", "")}</div>' if cid in ("_close", "_cta") else ""
            shoot(page(f'<div class="lower"><div class="k">{k}</div><div class="t">{t}</div></div>{foot}', True),
                  os.path.join(out, f"{cid}.png"), True)
    if ("SPONSOR" in d or "SUBSCRIBE" in d) and not d.get("END_CARD"):
        s, sub = d.get("SPONSOR", {}), d.get("SUBSCRIBE")
        ask = (f'<div style="display:inline-block;background:#e62117;color:#fff;font-size:84px;font-weight:900;padding:22px 70px;'
               f'border-radius:60px">{sub.get("button", "訂閱")}</div>'
               f'<div class="sub" style="margin-top:44px;font-size:56px;color:#eef3ff;font-weight:700;line-height:1.4">{sub.get("line", "")}</div>'
               if sub else "")
        spons = (f'<div class="kick" style="margin-top:{90 if sub else 0}px">{s.get("kicker", "")}</div>'
                 f'<div class="big" style="font-size:{110 if sub else 150}px;margin-top:30px;color:#f5c542">{s.get("name", "")}</div>'
                 + ("" if sub else f'<div class="sub" style="margin-top:50px">{s.get("sub", "")}</div>') if s else "")
        shoot(page(f'<div class="wrap"><div style="text-align:center">{ask}{spons}'
                   f'<div class="note" style="margin-top:90px;line-height:1.6">{d.get("SOURCES", "")}</div></div></div>'),
              os.path.join(out, "_end.png"))
    print("cards ->", out)


def cover(day):
    """out/<NAME>_cover.jpg (1080x1920): the anchor's face kept clear in the middle, the hook above her, one line below.
    day.py: COVER = dict(lines=[(text, colour), ...], sub="...", shift=420)  colour: up | down | gold | white"""
    import pathlib
    d, _ = load(day)
    c = d.get("COVER")
    if not c:
        sys.exit("day.py has no COVER = dict(lines=[(text, colour)], sub=...)")
    colours = dict(up="#ff4d4f", down="#27d17f", gold="#f5c542", white="#ffffff")
    pic = pathlib.Path(os.path.abspath(sp(day, d.get("COVER_IMAGE", d["ANCHOR"])))).as_uri()
    shift = c.get("shift", 560)   # the picture moves down so the face sits below the date and the hook
    b1, b2 = d.get("BRAND", ("新聞", ""))
    # a daily show: the date is the first thing read, big enough for a phone's small tile ("11/3（二）" -> "11/3 週二")
    when = d.get("COVER_DATE") or re.sub(r"（(.)）", r" 週\1", d.get("DATE", ""))
    lines = "".join(f'<div style="font-size:{140 if k == 0 else 108}px;color:{colours.get(col, col)};font-weight:900;line-height:1.1;'
                    f'-webkit-text-stroke:{8 if k == 0 else 6}px #050a14;paint-order:stroke fill">{t}</div>'
                    for k, (t, col) in enumerate(c["lines"]))
    body = (f'<img src="{pic}" style="position:absolute;left:0;top:{shift}px;width:1080px;height:1920px;object-fit:cover">'
            f'<div style="position:absolute;left:0;right:0;top:0;height:{shift + 260}px;'
            f'background:linear-gradient(#070d1a 0%,#070d1a {int(shift / (shift + 260) * 100)}%,#070d1a00 100%)"></div>'
            f'<div style="position:absolute;left:0;right:0;bottom:0;height:620px;background:linear-gradient(#070d1a00,#070d1aee 55%)"></div>'
            f'<div style="position:absolute;left:60px;right:60px;top:60px">'
            f'<div style="display:flex;justify-content:space-between;align-items:center">'
            f'<div style="background:#f5c542;color:#0b1426;font-size:124px;font-weight:900;line-height:1;padding:16px 34px 20px;'
            f'border-radius:26px">{when}</div>'
            f'<div style="text-align:right;font-size:58px;font-weight:900;line-height:1.15">{b1}<br>{b2}</div></div>'
            f'<div style="margin-top:36px">{lines}</div></div>'
            f'<div style="position:absolute;left:50px;right:50px;bottom:200px;padding:30px 40px;border-radius:26px;'
            f'background:rgba(8,16,34,.88);border-left:14px solid #f5c542;font-size:52px;font-weight:700;line-height:1.35">{c.get("sub", "")}</div>')
    os.makedirs(os.path.join(day, "out"), exist_ok=True)
    png = os.path.join(day, "out", "_cover.png")
    shoot(f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body style="background:#070d1a">{body}</body></html>', png)
    out = os.path.join(day, "out", f"{name_of(day, d)}_cover.jpg")
    cv2.imencode(".jpg", imread(png), [cv2.IMWRITE_JPEG_QUALITY, 92])[1].tofile(out)
    os.remove(png)
    print(out)


def seo(day):
    """out/<NAME>_SEO.txt: titles that open on the hook, a description (the lead, every subtitle line, sources,
    disclaimer, sponsor), tags. Sections as in the other lines' YouTube_SEO.txt; nothing is published.
    day.py: SEO = dict(titles=["A …", "B …"], lead="…", tags=[…]); series.py: SEO_TAGS = […], SEO_FOOT = "…" """
    d, rows = load(day)
    s = d.get("SEO")
    if not s:
        sys.exit("day.py has no SEO = dict(titles=[...], lead=..., tags=[...])")
    strip = lambda t: re.sub(r"<[^>]+>", "", re.sub(r"<br\s*/?>", "\n", t)).strip()
    body = [s.get("lead", ""), ""] + [f"・{r[1]}" for r in rows if r[2] != "anchor"] + [
        "", strip(d.get("SOURCES", "")), d.get("SEO_FOOT", "")]
    tags = list(dict.fromkeys(list(s.get("tags", [])) + list(d.get("SEO_TAGS", []))))
    titles = [titled(t, day, d) for t in s["titles"]]
    txt = ("==================== 標題（擇一，建議 A） ====================\n"
           + "\n".join(f"{chr(65 + k)}. {t}" for k, t in enumerate(titles))
           + "\n\n==================== 說明欄 ====================\n" + "\n".join(body).strip() + "\n"
           + " ".join("#" + t.replace(" ", "") for t in list(s.get("tags", []))[:4] + list(d.get("SEO_TAGS", []))[:4])
           + "\n\n==================== 標籤 ====================\n" + ", ".join(tags) + "\n")
    out = os.path.join(day, "out", f"{name_of(day, d)}_SEO.txt")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8", newline="\n").write(txt)
    long = [t for t in titles if len(t) > 60]
    print(out + ("" if not long else f"  !! {len(long)} title(s) over 60 characters: the hook may be cut off"))


def upload(day, privacy=None):
    """Upload out/<NAME>.mp4 with title A, the description and tags of out/<NAME>_SEO.txt, the subtitles and the cover,
    to series.py's CHANNEL with its own login (YT_TOKEN), at PRIVACY (default private). Stops at the channel's daily cap
    (youtube.daily_max); out/youtube.json keeps the id, so a second run does nothing."""
    d, _ = load(day)
    if not d.get("CHANNEL"):
        sys.exit("series.py has no CHANNEL (the channel id) to upload to")
    if d.get("YT_TOKEN"):
        os.environ["YT_TOKEN"] = os.path.expanduser(d["YT_TOKEN"])
    os.environ["YT_CHANNEL_ID"] = d["CHANNEL"]
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
    from dreamfab.youtube_api import youtube, channel
    from dreamfab.youtube_log import record, quota
    name, od = name_of(day, d), os.path.join(day, "out")
    state_p = os.path.join(od, "youtube.json")
    if os.path.exists(state_p):
        print("already uploaded: https://youtu.be/" + json.load(open(state_p, encoding="utf-8"))["id"]); return
    seo_txt = open(os.path.join(od, f"{name}_SEO.txt"), encoding="utf-8").read()
    sec = dict(re.findall(r"=+ (.+?) =+\n(.*?)(?=\n=+ |\Z)", seo_txt, flags=re.S))
    title = re.search(r"^A\. (.+)$", next(v for k, v in sec.items() if k.startswith("標題")), flags=re.M).group(1).strip()
    desc = next(v for k, v in sec.items() if k.startswith("說明欄")).strip()
    tags = [t.strip() for t in next(v for k, v in sec.items() if k.startswith("標籤")).split(",") if t.strip()]
    title = titled(title, day, d)
    if len(title) > 100 or len(desc.encode()) > 5000:
        sys.exit(f"title {len(title)} characters (100 at most) or description {len(desc.encode())} bytes (5,000 at most)")
    privacy = privacy or d.get("PRIVACY", "private")
    yt = youtube()
    cid = channel(yt, lock=True, expect=d["CHANNEL"])["id"]
    if quota(cid, day) == 0:
        sys.exit("the channel has put out its videos for today (youtube.daily_max): upload tomorrow")
    body = dict(snippet=dict(title=title, description=desc, tags=tags, categoryId=d.get("CATEGORY", "25"),
                             defaultLanguage="zh-TW", defaultAudioLanguage="zh-TW"),
                status=dict(privacyStatus=privacy, selfDeclaredMadeForKids=False, containsSyntheticMedia=True,
                            embeddable=True, license="youtube"))
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(os.path.join(od, f"{name}.mp4"), mimetype="video/mp4",
                                                        chunksize=16 * 1024 * 1024, resumable=True))
    resp, tries = None, 0
    while resp is None:
        try:
            st, resp = req.next_chunk()
            if st:
                print(f"  {st.progress() * 100:.0f}%", flush=True)
        except (HttpError, OSError) as e:
            if (isinstance(e, HttpError) and e.resp.status not in (500, 502, 503, 504)) or tries >= 8:
                raise
            tries += 1
            time.sleep(2 ** tries)
    vid = resp["id"]
    json.dump(dict(id=vid, channel=cid, title=title, privacy=privacy, at=datetime.now().isoformat(timespec="seconds")),
              open(state_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    record(vid, "upload", title, day, "news")
    if privacy == "public":
        record(vid, "publish", "uploaded public (news)", day, "news")
    print(f"  uploaded https://youtu.be/{vid} ({privacy})")
    srt = os.path.join(od, f"{name}.zh-TW.srt")
    if os.path.exists(srt):
        yt.captions().insert(part="snippet", body=dict(snippet=dict(videoId=vid, language="zh-TW", name="", isDraft=False)),
                             media_body=MediaFileUpload(srt, mimetype="application/octet-stream")).execute()
        record(vid, "captions", os.path.basename(srt), day, "news")
        print("  captions", os.path.basename(srt))
    cov = os.path.join(od, f"{name}_cover.jpg")
    if os.path.exists(cov):
        for wait in (0, 15, 30, 60):   # a fresh upload can be "not found" for a moment
            time.sleep(wait)
            try:   # the Shorts shelf picks its own frame; search and the watch page use this one
                yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(cov, mimetype="image/jpeg")).execute()
                record(vid, "thumbnail", os.path.basename(cov), day, "news")
                print("  thumbnail", os.path.basename(cov))
                break
            except HttpError as e:
                if e.resp.status != 404 or wait == 60:
                    print("  !! thumbnail not set:", getattr(e, "reason", e))
                    break
    if d.get("PLAYLIST"):
        yt.playlistItems().insert(part="snippet", body=dict(snippet=dict(
            playlistId=d["PLAYLIST"], resourceId=dict(kind="youtube#video", videoId=vid)))).execute()
        record(vid, "playlist", d["PLAYLIST"], day, "news")
        print("  playlist", d["PLAYLIST"])


# ---- jobs
def write_jobs(day, name, jobs):
    os.makedirs(os.path.join(day, "jobs"), exist_ok=True)
    path = os.path.join(day, "jobs", f"{name}.json")
    st = path + ".state"
    if os.path.exists(st):
        os.replace(st, st + ".prev")   # a new job file under the same name: start fresh
    open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(jobs, ensure_ascii=False, indent=1) + "\n")
    return path


def clone_job(day, d, jid, text, out):
    """A narration job. It ends with a throwaway line after a paragraph break (explain/common.py TAIL): the voice
    service cuts off the last moment of what it reads, and cut_tail ends the file at the pause before that line."""
    from common import TAIL
    tail = TAIL["zh"]
    return dict(id=jid, endpoint="/voice/clone", fields=dict(text=text + "\n\n" + tail, **d.get("VOICE_FIELDS", {})),
                files=dict(reference_audio=os.path.abspath(sp(day, d["VOICE"])).replace("\\", "/")),
                out=os.path.abspath(out).replace("\\", "/"), tail=tail)


def voice(day):
    d, rows = load(day)
    text = "\n".join(r[0] for r in rows)
    p = write_jobs(day, "voice", [clone_job(day, d, "narr", text, os.path.join(day, "voice", "narr.flac"))])
    chars = len(re.sub(r"[^\w]|[A-Za-z]", "", text)) + 2 * len(re.findall(r"[A-Za-z]+", text))   # an English word ~ 2
    print(f"{p}: {len(rows)} lines, {chars} characters (about {chars / 5.2:.0f} s; 5.2 a second was measured)")


def redo(day, first, last):
    d, rows = load(day)
    text = "\n".join(r[0] for r in rows[first - 1:last])
    p = write_jobs(day, "redo", [clone_job(day, d, "redo", text, os.path.join(day, "voice", "redo.flac"))])
    print(f"{p}: lines {first}-{last}")


def submit(day, which, off_peak):
    path = os.path.join(day, "jobs", f"{which}.json")
    if not os.path.exists(path):
        sys.exit(f"no {path}")
    subprocess.run([sys.executable, os.path.join(REPO, "dreamfab", "aip_runner.py"), path,
                    "--off-peak" if off_peak else "--now"], check=True)


# ---- timing in the narration
def cut_tail(day, f):
    """voice/F as it came back ends with the job's throwaway line (clone_job): keep it as F_raw.flac and make F end at
    the pause before that line, with its word times. Done once per submitted job (voice/F.cut.json keeps the task id),
    so a splice into F later is left alone. Jobs without a throwaway line (before 11/05) are not touched."""
    import soundfile as sf
    from common import align, pause_after, transcribe, words_path, PUNCT
    path = os.path.join(day, "voice", f)
    job = next((j for jf in sorted(glob.glob(os.path.join(day, "jobs", "*.json")))
                for j in json.load(open(jf, encoding="utf-8")) if os.path.basename(j.get("out", "")) == f and j.get("tail")), None)
    if not job or not os.path.exists(path):
        return
    st = os.path.join(day, "jobs", ("redo" if job["id"] == "redo" else "voice") + ".json.state")
    task = json.load(open(st)).get(job["id"], {}).get("uuid") if os.path.exists(st) else None
    side = os.path.splitext(path)[0] + ".cut.json"
    if os.path.exists(side) and json.load(open(side)).get("task") == task:
        return
    raw = os.path.splitext(path)[0] + "_raw.flac"
    if os.path.exists(raw):   # an earlier take
        os.replace(raw, os.path.splitext(raw)[0] + "_prev.flac")
    os.replace(path, raw)
    for p in (words_path(raw), words_path(path)):   # timings of an earlier take
        if os.path.exists(p):
            os.remove(p)
    transcribe([raw], language="zh")
    w = json.load(open(words_path(raw), encoding="utf-8"))
    full = job["fields"]["text"]
    text = full[:-len(job["tail"])].rstrip()
    ct, _ = align(full, w["words"])
    last = ct[max(i for i, c in enumerate(text) if c not in PUNCT)]
    gap = pause_after(raw, last[0] - 0.05)
    if gap:
        cut = min(gap[0] + 0.06, (gap[0] + gap[1]) / 2)
    else:
        cut = min(w["duration"], last[1] + 0.12)
        print(f"  !! {f}: no pause before the throwaway line; cut at {cut:.2f} s: listen to the ending")
    x, sr = sf.read(raw)
    x = x[:int(cut * sr)].copy()
    fade = min(len(x), int(0.015 * sr))
    x[len(x) - fade:] *= np.linspace(1, 0, fade) if x.ndim == 1 else np.linspace(1, 0, fade)[:, None]
    sf.write(path, x, sr)
    words = [[t, a, min(b, cut)] for t, a, b in w["words"] if a < cut]
    json.dump(dict(duration=cut, words=words), open(words_path(path), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(dict(task=task, cut=round(cut, 3), raw=os.path.basename(raw)), open(side, "w"))
    print(f"  {f}: ends at {cut:.2f} s, before the throwaway line ({w['duration'] - cut:.2f} s cut; as it came: {os.path.basename(raw)})")


def transcribe_narr(day, f="narr.flac"):
    from common import transcribe, words_path
    cut_tail(day, f)
    path = os.path.join(day, "voice", f)
    if not os.path.exists(words_path(path)):
        transcribe([path], language="zh")
    return json.load(open(words_path(path), encoding="utf-8"))


def seg_starts(day, rows):
    """Where every comma part of every line starts in voice/narr.flac (pinyin alignment: homophones still match)."""
    from common import align
    w = transcribe_narr(day)["words"]
    text = "\n".join(r[0] for r in rows)
    ct, _ = align(text, w)
    out, pos = [], 0
    for r in rows:
        segs = []
        for m in re.finditer(r"[^，。]+[，。]?", r[0]):
            i = next(k for k in range(pos + m.start(), pos + m.end()) if ct[k])
            segs.append(ct[i][0])
        out.append(segs)
        pos += len(r[0]) + 1
    return out, w[-1][2]


def anchor_spans(day, rows):
    segs, end = seg_starts(day, rows)
    starts = [g[0] for g in segs] + [end + 0.25]
    spans = []
    for k, r in enumerate(rows):
        if r[2] == "anchor":
            if spans and abs(spans[-1][1] - starts[k]) < 1e-6:
                spans[-1][1] = starts[k + 1]
            else:
                spans.append([starts[k], starts[k + 1]])
    return spans


def anchor(day):
    d, rows = load(day)
    spans = anchor_spans(day, rows)
    total = sum(b - a for a, b in spans) + 0.6
    if total > 31:
        sys.exit(f"the anchor speaks {total:.1f} s: lip-sync takes 31 s at most (give her fewer lines)")
    src = os.path.join(day, "voice", "narr.flac")
    inp = "".join(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS[p{k}];" for k, (a, b) in enumerate(spans))
    cat = "".join(f"[p{k}]" for k in range(len(spans))) + f"concat=n={len(spans)}:v=0:a=1,apad=pad_dur=0.6[a]"
    wav = os.path.join(day, "voice", "anchor_in.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", inp + cat, "-map", "[a]", "-ar", "44100",
                    "-ac", "1", wav], check=True)
    os.makedirs(os.path.join(day, "clips"), exist_ok=True)
    off, amap = 0.0, []
    for a, b in spans:
        amap.append([a, b, off]); off += b - a
    json.dump(amap, open(os.path.join(day, "clips", "anchor_map.json"), "w"))
    job = dict(id="anchor", endpoint="/videos/lip-sync",
               fields=dict(engine="ltx2", aspect_ratio="9:16", audio_start_time="0", audio_duration=f"{total:.1f}",
                           prompt=d.get("ANCHOR_PROMPT", "新聞主播坐在主播台後面，看著鏡頭穩定播報，頭部和肩膀有自然的小動作，雙手交疊放在桌上，背景維持模糊")),
               files=dict(image=os.path.abspath(sp(day, d["ANCHOR"])).replace("\\", "/"), audio=os.path.abspath(wav).replace("\\", "/")),
               out=os.path.abspath(os.path.join(day, "clips", "anchor.mp4")).replace("\\", "/"))
    p = write_jobs(day, "lipsync", [job])
    print(f"{p}: {total:.1f} s from {len(spans)} parts (" + ", ".join(f"{a:.1f}-{b:.1f}" for a, b in spans) + ")")


def check(day):
    """The transcript, and the spoken words it heard differently (pinyin compared: same-sounding words pass)."""
    from common import align
    from pypinyin import pinyin, Style
    _, rows = load(day)
    w = transcribe_narr(day)
    text = "\n".join(r[0] for r in rows)
    ct, info = align(text, w["words"])
    print(f"{w['duration']:.1f} s: " + "".join(x[0] for x in w["words"]))
    reads = lambda c: set(pinyin(c, style=Style.NORMAL, heteronym=True)[0])
    prev = (0, 0)
    for a, b, k in info["blocks"]:
        ta, tb = prev
        if 1 <= a - ta <= 8 and b - tb >= 1:
            said = "".join(text[info["idx"][i]] for i in range(ta, a))
            heard = "".join(info["asr"][tb:b])
            numeric = set("零〇一二兩三四五六七八九十百千萬億點分之%.")
            if set(said) <= numeric and set(heard) <= numeric:
                pass   # a number read out in words, written in digits by the recogniser
            elif not (len(said) == len(heard) and all(reads(x) & reads(y) for x, y in zip(said, heard))):
                t = ct[info["idx"][ta]][0]
                print(f"  listen at {int(t // 60)}:{t % 60:04.1f}: 「{said}」 heard as 「{heard}」")
        prev = (a + k, b + k)
    print("English names are often written another way by the recogniser: listen before re-reading anything.")


# ---- splice a re-read
def _mono(x):
    return x if x.ndim == 1 else x.mean(1)


def _env(x, sr):
    hop = sr // 100
    m = _mono(x)
    return np.array([np.sqrt(np.mean(m[i * hop:(i + 1) * hop] ** 2)) for i in range(len(m) // hop)])


def _quiet(ev, center, span=0.7, win=8):
    a, b = max(0, int((center - span) * 100)), min(len(ev) - win, int((center + span) * 100))
    i = min(range(a, b), key=lambda j: ev[j:j + win].mean())
    return (i + win / 2) / 100


def splice(day, first, last):
    import soundfile as sf
    _, rows = load(day)
    if any(r[2] == "anchor" for r in rows[first - 1:last]):
        print("!! these lines include the anchor's: run anchor and submit lipsync again after the splice")
    segs, end = seg_starts(day, rows)
    starts = [g[0] for g in segs]
    vd = os.path.join(day, "voice")
    cut_tail(day, "redo.flac")
    cur, sr = sf.read(os.path.join(vd, "narr.flac"))
    new, sr2 = sf.read(os.path.join(vd, "redo.flac"))
    if sr != sr2:
        sys.exit(f"sample rates differ ({sr} vs {sr2})")
    ev, en = _env(cur, sr), _env(new, sr)
    cut_a = 0.0 if first == 1 else _quiet(ev, starts[first - 1])
    cut_b = len(cur) / sr if last >= len(rows) else _quiet(ev, starts[last])
    loud = np.where(en > en.max() * 0.03)[0]
    piece = new[max(0, loud[0] - 3) * sr // 100:min(len(new), (loud[-1] + 6) * sr // 100)].copy()
    left, right = cur[:int(cut_a * sr)].copy(), cur[int(cut_b * sr):].copy()

    def silent_run(sig, from_end):
        e = _env(sig, sr) if len(sig) > sr // 50 else np.array([])
        e = e[::-1] if from_end else e
        n = next((i for i, v in enumerate(e) if v > 0.005), len(e))
        return n / 100
    fade = int(0.008 * sr)
    for p in (piece, right):
        if len(p) > fade:
            p[:fade] *= np.linspace(0, 1, fade) if p.ndim == 1 else np.linspace(0, 1, fade)[:, None]
    for p in (left, piece):
        if len(p) > fade:
            p[-fade:] *= np.linspace(1, 0, fade) if p.ndim == 1 else np.linspace(1, 0, fade)[:, None]
    zero = lambda s: np.zeros((max(0, int(s * sr)),) + cur.shape[1:])
    pad_a = 0 if first == 1 else GAP - silent_run(left, True) - silent_run(piece, False)
    pad_b = 0 if last >= len(rows) else GAP - silent_run(piece, True) - silent_run(right, False)
    out = np.concatenate([left, zero(pad_a), piece, zero(pad_b), right])
    for f in ("narr.flac", "narr.words.json"):
        if os.path.exists(os.path.join(vd, f)):
            shutil.copy2(os.path.join(vd, f), os.path.join(vd, f.replace("narr", "narr_prev")))
    sf.write(os.path.join(vd, "narr.flac"), out, sr)
    os.remove(os.path.join(vd, "narr.words.json"))
    print(f"lines {first}-{last}: {cut_b - cut_a:.2f} s -> {len(piece) / sr:.2f} s; narration {len(cur) / sr:.2f} -> {len(out) / sr:.2f} s"
          " (the old take is voice/narr_prev.flac)")
    mp = os.path.join(day, "clips", "anchor_map.json")
    if os.path.exists(mp):   # the anchor's audio did not change: same clip, new times
        old = json.load(open(mp))
        spans = anchor_spans(day, rows)
        if len(spans) == len(old):
            json.dump([[a, b, o[2]] for (a, b), o in zip(spans, old)], open(mp, "w"))


# ---- render
def music_bed(day, d, length):
    out = os.path.join(day, "voice", "music_bed.wav")
    if not d.get("MUSIC"):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{length}", out], check=True)
        return out
    src = sp(day, d["MUSIC"])
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                               capture_output=True, text=True).stdout)
    a, b = d.get("MUSIC_LOOP", (0.0, dur))
    bar_s = d.get("MUSIC_BAR", 2.0)
    body = length - a - (dur - b)
    parts, t = [(0, a)] if a > 0 else [], 0.0
    while body - t > 0.01:   # whole bars of the loop until the ending fits
        n = min(b - a, max(bar_s, round((body - t) / bar_s) * bar_s))
        parts.append((a, a + n)); t += n
    parts.append((b, dur))
    inp = "".join(f"[0:a]atrim={x}:{y},asetpts=PTS-STARTPTS[p{k}];" for k, (x, y) in enumerate(parts))
    chain, prev = "", "p0"
    for k in range(1, len(parts)):
        chain += f"[{prev}][p{k}]acrossfade=d=0.02:c1=tri:c2=tri[x{k}];"; prev = f"x{k}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", inp + chain.rstrip(";"),
                    "-map", f"[{prev}]", "-ar", "48000", out], check=True)
    return out


def ass_time(t):
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def render(day):
    d, rows = load(day)
    segs, narr_end = seg_starts(day, rows)
    starts = [g[0] for g in segs]
    length = max(round((narr_end + 1.7) / 2) * 2.0, narr_end + 1.5)
    bed = music_bed(day, d, length)
    lines = [(a, b, r[2]) for a, b, r in zip(starts, starts[1:] + [length], rows)]
    shots = []
    for a, b, s in lines:   # the same card on consecutive lines stays on screen
        if shots and shots[-1][2] == s:
            shots[-1] = (shots[-1][0], b, s)
        else:
            shots.append((a, b, s))
    ev = []
    for k, ((a, b, _), r) in enumerate(zip(lines, rows)):
        b = min(b, narr_end + 0.3)
        parts = re.findall(r"[^，。]+[，。]?", r[1])
        times = segs[k] if len(segs[k]) == len(parts) else [a + (b - a) * j / len(parts) for j in range(len(parts))]
        groups = []   # comma parts joined while a subtitle stays within about 14 characters (one row at 1080 wide)
        for t0, p in zip(times, parts):
            if groups and len(re.sub(r"[\s，。]", "", groups[-1][1] + p)) <= 14:
                groups[-1] = (groups[-1][0], groups[-1][1] + p)
            else:
                groups.append((t0, p))
        for j, (t0, txt) in enumerate(groups):
            t1 = groups[j + 1][0] if j + 1 < len(groups) else b
            ev.append((t0, t1 - 0.05, txt.rstrip("，。")))
    cf = d.get("COVER_FRAME", 0)   # no subtitle over the cover frames
    ev = [(max(a, cf), b, t) for a, b, t in ev if b > cf]
    font = d.get("SUB_FONT", "Microsoft JhengHei")
    ass = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, "
           "PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, "
           "Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
           f"Style: S,{font},62,&H00FFFFFF,&H00FFFFFF,&H00141414,&HB4000000,-1,0,0,0,100,100,0,0,3,14,0,5,60,60,0,1\n\n"
           "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    ass += "".join(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},S,,0,0,0,,{{\\pos(540,{SUB_Y})}}{t}\n" for a, b, t in ev)
    od = os.path.join(day, "out")
    os.makedirs(od, exist_ok=True)
    ass_p = os.path.join(od, "subs.ass")
    open(ass_p, "w", encoding="utf-8").write(ass)
    name = name_of(day, d)
    srt_t = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{t % 60:06.3f}".replace(".", ",")
    srt = "".join(f"{k + 1}\n{srt_t(a)} --> {srt_t(b)}\n{t}\n\n" for k, (a, b, t) in enumerate(ev))
    open(os.path.join(od, f"{name}.zh-TW.srt"), "w", encoding="utf-8").write(srt)

    def rgba(p):
        im = imread(p, cv2.IMREAD_UNCHANGED)
        return im[..., :3].astype(np.float32), im[..., 3:4].astype(np.float32) / 255
    cd = os.path.join(day, "cards")
    top, top_a = rgba(os.path.join(cd, "_top.png"))
    straps = {k: rgba(os.path.join(cd, f"_{k}.png")) for k in ("open", "close", "cta") if os.path.exists(os.path.join(cd, f"_{k}.png"))}
    cta_at = starts[-1] if d.get("CTA_LINE") and rows[-1][0] == say(d["CTA_LINE"].split("｜")[0].strip(), d) else None
    imgs = {s: imread(os.path.join(cd, f"{s}.png")) for _, _, s in shots if s != "anchor"}
    end_id = d.get("END_CARD") or ("_end" if os.path.exists(os.path.join(cd, "_end.png")) else None)
    if end_id:
        imgs[end_id] = imread(os.path.join(cd, f"{end_id}.png"))
    frames, afps = read_frames(os.path.join(day, "clips", "anchor.mp4"))
    mp = os.path.join(day, "clips", "anchor_map.json")
    amap = json.load(open(mp)) if os.path.exists(mp) else None

    def clip_t(t):   # narration time -> time in the lip-sync clip
        if not amap:
            return t
        for a, b, off in amap:
            if t < b:
                return off + max(0.0, t - a)
        a, b, off = amap[-1]
        return off + (b - a)
    silent = os.path.join(od, "_video.mp4")
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", silent],
                           stdin=subprocess.PIPE)
    end_at = None
    cv_p = os.path.join(od, f"{name}_cover.jpg")
    cover_img = imread(cv_p).astype(np.float32) if d.get("COVER_FRAME") and os.path.exists(cv_p) else None
    for i in range(int(length * FPS)):
        t = i / FPS
        k = max(j for j, (a, _, _) in enumerate(shots) if a <= t + 1e-6)
        a, b, s = shots[k]
        if s == "anchor" and end_id and (end_at is not None or clip_t(t) * afps >= len(frames) - 1):
            end_at = t if end_at is None else end_at   # the clip ran out: the end card
            fr = imgs[end_id].astype(np.float32) * min(1.0, 0.35 + (t - end_at) / 0.25)
        elif s == "anchor":
            fr = cv2.resize(frames[min(int(clip_t(t) * afps), len(frames) - 1)], (W, H), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
            key = "open" if k == 0 else "cta" if cta_at is not None and t >= cta_at and "cta" in straps else "close"
            strap = straps.get(key)
            if strap:
                show = min(1.0, (t - (cta_at if key == "cta" else a)) / 0.3)
                fr = fr * (1 - strap[1] * show) + strap[0] * strap[1] * show
        else:
            u = (t - a) / max(0.01, b - a)
            M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, 1.04 - 0.04 * u)   # a slow pull back
            fr = cv2.warpAffine(imgs[s], M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
            if t - a < 0.18:   # slides in from the right
                fr = np.roll(fr, int((1 - (t - a) / 0.18) ** 2 * 140), axis=1) * (0.6 + 0.4 * (t - a) / 0.18)
        fr = fr * (1 - top_a) + top * top_a
        if cover_img is not None and t < d.get("COVER_FRAME", 0):   # the cover as the first frames
            fr = cover_img
        enc.stdin.write(np.clip(fr, 0, 255).astype(np.uint8).tobytes())
    enc.stdin.close(); enc.wait()
    out = os.path.join(od, f"{name}.mp4")
    ass_f = ass_p.replace("\\", "/").replace(":", "\\:")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", silent, "-i", os.path.join(day, "voice", "narr.flac"), "-i", bed,
                    "-filter_complex",
                    f"[0:v]ass='{ass_f}'[v];[1:a]aresample=48000,apad=whole_dur={length},asplit[n][key];"
                    f"[2:a]volume={d.get('MUSIC_GAIN', 0.55)}[m];[m][key]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[duck];"
                    "[n][duck]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=9[a]",
                    "-map", "[v]", "-map", "[a]", "-t", f"{length}", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
    os.remove(silent)
    print(f"{out}  {length:.1f} s")


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 2:
        sys.exit(__doc__)
    cmd, target, rest = a[0], a[1], a[2:]
    t0 = time.time()
    nums = [int(x) for x in rest if x.isdigit()]
    if cmd == "new":
        new_day(target, rest[0] if rest else None)
        sys.exit()
    if cmd == "daily":
        sys.exit(daily(target, "--test" in rest))
    if cmd == "schedule":
        sys.exit(schedule(target, "--remove" in rest, "--dry-run" in rest))
    steps = dict(cards=lambda: cards(target), cover=lambda: cover(target), seo=lambda: seo(target),
                 upload=lambda: upload(target, "private" if "--private" in rest else "public" if "--public" in rest else None), voice=lambda: voice(target), check=lambda: check(target),
                 anchor=lambda: anchor(target), render=lambda: render(target),
                 redo=lambda: redo(target, nums[0], nums[-1]), splice=lambda: splice(target, nums[0], nums[-1]),
                 submit=lambda: submit(target, rest[0], "--off-peak" in rest))
    if cmd not in steps or (cmd in ("redo", "splice") and not nums) or (cmd == "submit" and not rest):
        sys.exit(__doc__)
    steps[cmd]()
    log_time(target, cmd if cmd != "submit" else f"submit {rest[0]}", t0)
