"""The news line (聞): a short daily news brief in 9:16 (1080x1920). An AI anchor opens and closes on camera (lip-synced),
cards carry the numbers in between, subtitles and a theme tune run throughout. PILOT: it makes files; nothing is
uploaded or published.

usage: python news/make.py new SERIES [YYYY-MM-DD]       a day folder: day.py from the last day (DATE updated),
                                                        script.md with the series' fixed first and last lines
       python news/make.py cards DAY                    draw the cards (HTML in Edge/Chrome, no credits)
       python news/make.py cover DAY                    out/<NAME>_cover.jpg: the hook over the anchor, her face kept clear
       python news/make.py seo DAY                      out/<NAME>_SEO.txt: hook titles, description, tags (not published)
       python news/make.py voice DAY                    jobs/voice.json: the whole narration in one job
       python news/make.py submit DAY voice|lipsync|redo [--off-peak]   run that job file (dreamfab/aip_runner.py)
       python news/make.py check DAY                    transcribe voice/narr.flac; list words heard differently
       python news/make.py anchor DAY                   only the anchor's lines -> voice/anchor_in.wav (+0.6 s of
                                                        silence: lip-sync clips come back about 0.5 s short),
                                                        clips/anchor_map.json, jobs/lipsync.json (31 s at most)
       python news/make.py redo DAY FIRST [LAST]        jobs/redo.json: read lines FIRST..LAST again (1 = first line)
       python news/make.py splice DAY FIRST [LAST]      put voice/redo.flac in place of those lines, cut at the pauses
                                                        (gaps of 0.3 s at least); the anchor clip is kept
       python news/make.py render DAY                   out/<NAME>_<YYYYMMDD>.mp4 + .zh-TW.srt
Every step adds a line to SERIES/timing.tsv (day, step, start, end, minutes): what a daily slot has to fit.

SERIES/series.py (the show; see examples/news/demo):
  NAME = "us_stocks"                 file names: <NAME>_<YYYYMMDD>
  BRAND = ("美股", "1分鐘")           the bar at the top (a tag and a title), with DATE and AI_LABEL
  ANCHOR = "cast/ANCHOR_A.png"       the anchor's picture for lip-sync (9:16)
  VOICE = "voices/ANCHOR_A.wav"      her voice sample (VOICE_FIELDS: more /voice/clone fields)
  MUSIC = "music/theme.mp3"          the theme; MUSIC_LOOP = (start, end) of whole bars that may repeat, MUSIC_BAR = 2.0
  OPEN = (kicker, title)             the strap over the anchor at the start; CLOSE the one at the end
  FIRST_LINE / LAST_LINE             fixed script lines (spoken｜subtitle｜anchor)
  SPONSOR = dict(kicker=, name=, sub=)   the end card, shown once the anchor clip runs out (or END_CARD = a card id)
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


def load(day):
    """(settings, script rows): series.py, then day.py over it; rows = [spoken, subtitle, picture]."""
    ns = dict(row=row, bar=bar, box=box)
    for f in (os.path.join(series_of(day), "series.py"), os.path.join(day, "day.py")):
        if os.path.exists(f):
            exec(open(f, encoding="utf-8").read(), ns)
    rows = [[c.strip() for c in l.split("｜")] for l in open(os.path.join(day, "script.md"), encoding="utf-8").read().splitlines()
            if l.count("｜") == 2 and not l.lstrip().startswith(("#", ">", "每一行"))]
    return ns, rows


def name_of(day, d):
    stamp = re.sub(r"\D", "", os.path.basename(os.path.abspath(day)))
    return d.get("FILE") or f"{d.get('NAME', 'news')}_{stamp}"


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
    ns = {}
    exec(open(os.path.join(series, "series.py"), encoding="utf-8").read(), ns)
    lines = [f"# {when}", "", "每一行三欄，用全形直線隔開：唸的（數字寫國字）、字幕（阿拉伯數字）、畫面（anchor 或 CARDS 的 id）", "",
             ns.get("FIRST_LINE", "早安。｜早安｜anchor"), "", ns.get("LAST_LINE", "以上是今天的新聞。｜以上是今天的新聞｜anchor"),
             "", "## 資料來源", "- "]
    open(os.path.join(day, "script.md"), "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print(f"{day}: write the news lines between the first and the last line of script.md")


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
    for cid, key in (("_open", "OPEN"), ("_close", "CLOSE")):
        if key in d:
            k, t = d[key]
            foot = f'<div class="foot">{d.get("SOURCES", "")}</div>' if cid == "_close" else ""
            shoot(page(f'<div class="lower"><div class="k">{k}</div><div class="t">{t}</div></div>{foot}', True),
                  os.path.join(out, f"{cid}.png"), True)
    if "SPONSOR" in d and not d.get("END_CARD"):
        s = d["SPONSOR"]
        shoot(page(f'<div class="wrap"><div style="text-align:center"><div class="kick">{s.get("kicker", "")}</div>'
                   f'<div class="big" style="font-size:150px;margin-top:60px;color:#f5c542">{s.get("name", "")}</div>'
                   f'<div class="sub" style="margin-top:50px">{s.get("sub", "")}</div>'
                   f'<div class="note" style="margin-top:120px;line-height:1.6">{d.get("SOURCES", "")}</div></div></div>'),
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
    shift = c.get("shift", 420)   # the picture moves down so the face sits below the hook
    b1, b2 = d.get("BRAND", ("新聞", ""))
    lines = "".join(f'<div style="font-size:{140 if k == 0 else 108}px;color:{colours.get(col, col)};font-weight:900;line-height:1.1;'
                    f'-webkit-text-stroke:{8 if k == 0 else 6}px #050a14;paint-order:stroke fill">{t}</div>'
                    for k, (t, col) in enumerate(c["lines"]))
    body = (f'<img src="{pic}" style="position:absolute;left:0;top:{shift}px;width:1080px;height:1920px;object-fit:cover">'
            f'<div style="position:absolute;left:0;right:0;top:0;height:{shift + 260}px;'
            f'background:linear-gradient(#070d1a 0%,#070d1a {int(shift / (shift + 260) * 100)}%,#070d1a00 100%)"></div>'
            f'<div style="position:absolute;left:0;right:0;bottom:0;height:620px;background:linear-gradient(#070d1a00,#070d1aee 55%)"></div>'
            f'<div style="position:absolute;left:60px;right:60px;top:70px">'
            f'<div class="brand" style="font-size:46px"><b>{b1}</b>{b2}<span class="date" style="margin-left:24px">{d.get("DATE", "")}</span></div>'
            f'<div style="margin-top:34px">{lines}</div></div>'
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
    txt = ("==================== 標題（擇一，建議 A） ====================\n"
           + "\n".join(f"{chr(65 + k)}. {t}" for k, t in enumerate(s["titles"]))
           + "\n\n==================== 說明欄 ====================\n" + "\n".join(body).strip() + "\n"
           + " ".join("#" + t.replace(" ", "") for t in list(s.get("tags", []))[:4] + list(d.get("SEO_TAGS", []))[:4])
           + "\n\n==================== 標籤 ====================\n" + ", ".join(tags) + "\n")
    out = os.path.join(day, "out", f"{name_of(day, d)}_SEO.txt")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8", newline="\n").write(txt)
    long = [t for t in s["titles"] if len(t) > 60]
    print(out + ("" if not long else f"  !! {len(long)} title(s) over 60 characters: the hook may be cut off"))


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
    return dict(id=jid, endpoint="/voice/clone", fields=dict(text=text, **d.get("VOICE_FIELDS", {})),
                files=dict(reference_audio=os.path.abspath(sp(day, d["VOICE"])).replace("\\", "/")),
                out=os.path.abspath(out).replace("\\", "/"))


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
def transcribe_narr(day, f="narr.flac"):
    from common import transcribe, words_path
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
    srt = "".join(f"{k + 1}\n{ass_time(a).replace('.', ',')}0 --> {ass_time(b).replace('.', ',')}0\n{t}\n\n" for k, (a, b, t) in enumerate(ev))
    open(os.path.join(od, f"{name}.zh-TW.srt"), "w", encoding="utf-8").write(srt)

    def rgba(p):
        im = imread(p, cv2.IMREAD_UNCHANGED)
        return im[..., :3].astype(np.float32), im[..., 3:4].astype(np.float32) / 255
    cd = os.path.join(day, "cards")
    top, top_a = rgba(os.path.join(cd, "_top.png"))
    straps = {k: rgba(os.path.join(cd, f"_{k}.png")) for k in ("open", "close") if os.path.exists(os.path.join(cd, f"_{k}.png"))}
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
    for i in range(int(length * FPS)):
        t = i / FPS
        k = max(j for j, (a, _, _) in enumerate(shots) if a <= t + 1e-6)
        a, b, s = shots[k]
        if s == "anchor" and end_id and (end_at is not None or clip_t(t) * afps >= len(frames) - 1):
            end_at = t if end_at is None else end_at   # the clip ran out: the end card
            fr = imgs[end_id].astype(np.float32) * min(1.0, 0.35 + (t - end_at) / 0.25)
        elif s == "anchor":
            fr = cv2.resize(frames[min(int(clip_t(t) * afps), len(frames) - 1)], (W, H), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
            strap = straps.get("open" if k == 0 else "close")
            if strap:
                show = min(1.0, (t - a) / 0.3)
                fr = fr * (1 - strap[1] * show) + strap[0] * strap[1] * show
        else:
            u = (t - a) / max(0.01, b - a)
            M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, 1.04 - 0.04 * u)   # a slow pull back
            fr = cv2.warpAffine(imgs[s], M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
            if t - a < 0.18:   # slides in from the right
                fr = np.roll(fr, int((1 - (t - a) / 0.18) ** 2 * 140), axis=1) * (0.6 + 0.4 * (t - a) / 0.18)
        fr = fr * (1 - top_a) + top * top_a
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
    steps = dict(cards=lambda: cards(target), cover=lambda: cover(target), seo=lambda: seo(target), voice=lambda: voice(target), check=lambda: check(target),
                 anchor=lambda: anchor(target), render=lambda: render(target),
                 redo=lambda: redo(target, nums[0], nums[-1]), splice=lambda: splice(target, nums[0], nums[-1]),
                 submit=lambda: submit(target, rest[0], "--off-peak" in rest))
    if cmd not in steps or (cmd in ("redo", "splice") and not nums) or (cmd == "submit" and not rest):
        sys.exit(__doc__)
    steps[cmd]()
    log_time(target, cmd if cmd != "submit" else f"submit {rest[0]}", t0)
