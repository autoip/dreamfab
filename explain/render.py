"""Render an explainer: still pictures with smooth pans and zooms and cross-fades, the narration, subtitles timed to
the voice (pinyin alignment), a music bed from the series' MV (one section per chapter, ducked under the voice),
an MV clip and other covers in a gold frame, a title after the opening, quick fact-check cards after the narration
and an AI-made end card. No credits.

usage: python explain/render.py PROJECT_DIR [--until TEXT] [--out out/NAME.mp4] [--full-only]
       python explain/render.py PROJECT_DIR --shorts [--layout band|square] [--out out/NAME_shorts.mp4]
       python explain/render.py PROJECT_DIR --cut NAME [--out out/NAME_<name>.mp4]
  --until TEXT   stop before this sentence (a short test cut); the title and a few seconds of music close it
  (a project with SHORTS gets both cuts from one command: the 16:9 episode, then its vertical Short; the
   workflow switch explain.shorts turns that off (dreamfab/workflow.py), --full-only skips it once)
  --shorts       a vertical 1080x1920 Short cut from the same narration, pictures and music (no credits):
                 SHORTS = dict(clips=[(from words, up to words or None), ...], head=("line", ...), music=second in
                 MUSIC (default: the bed meets the MV clip where the full cut's 結尾 section does), end="closing
                 line", layout="band"). Each clip plays the narration from its first words up to
                 (not including) the second (None: to the end of that part); keep the sum under 60 s (YouTube takes up
                 to 3 minutes, but a Short over 1 minute with any copyright claim is blocked everywhere). head stays at
                 the top, the pictures sit in the middle, subtitles below them, the end line over the last seconds.
  --cut NAME     a shorter cut from CUTS[NAME] = dict(clips=[...], aspect="16:9" | "9:16" | "1:1", head=(...), end="...")
                 (an ad's 30 s and 15 s versions): clips as for SHORTS; 16:9 keeps the full cut's look, 9:16 and 1:1
                 set the picture across the middle (1:1: band layout, head line smaller). The full render makes every
                 cut in CUTS after the Short (--full-only skips them).
  --layout       band: the whole 16:9 picture across the middle on a blurred copy of itself (default);
                 square: a 1:1 cut from the middle of each picture, larger on the phone (keep head to one line).
                 Render both (--layout ... --out ...) and let the user choose before setting SHORTS["layout"]
Needs images/<id>.png|jpg (voice/*.words.json are made on the first run, or by narration.py check), and in project.py:
  NAME, SCRIPT, SHOTS; optional SAY, NARRATION, TITLE, ENDCARD, FACTS, MUSIC, CH_MUSIC, MUSIC_DB, MV_CLIP, FONT, SUBS, GAPS
FACTS = [("heading", "line\\nline"), ...]: the script's fact check, one card each (FACTS_S seconds, default 2.4: quick,
pause to read) over the darkened last picture, between the narration and the end card. Full cut only.
SUBS = dict(style=outline | heavy | gold | band, font=a family in FONT's folder, size=58): the subtitle look the user
picked from explain/sub_styles.py (default: outline, FONT's family, 58).
Writes out/NAME.mp4 and out/NAME.<lang>.srt (YouTube indexes uploaded captions for search).
SHOTS = [(image, first words, move, focus)]: the picture comes in when the narration reaches those words (searched in
order). move: in / out (zoom towards / away from focus=(x, y) in 0..1), left / right (pan), frame (whole picture in a
gold frame: covers with lettering), scroll (a long handscroll on a white ground: cut out and panned right to left).
image "MV:12.5" plays MV_CLIP from 12.5 s in the gold frame. CLIPS = {"KEY": "path/to/video.mp4", ...}: image "KEY:3.0"
plays that video from 3.0 s across the whole picture (a vertical one stands in the middle on a blurred copy of itself;
move "frame": in the gold frame instead). Their own sound is not used: a line worth hearing goes in NARRATION as
dict(audio=..., sound=True) (common.narration).
Bilingual subtitles: "> " lines under the script's lines (common.translations) put each translation under its line,
in SUBS font2 / size2, and write a second .srt in RENDER["lang2"] (default zh-TW).
A variety-show look (all optional): CARD = dict(colors=("#ffe14d", "#ff7eb3", "#7ad7ff"), scale=0.74, tilt=-1.5, border=12,
shadow=14, top=36) sets every picture on a tilted white card over a gradient; STICKERS = [dict(at="phrase", text="...",
x=, y=, rot=, color="#rrggbb", ink="#rrggbb", size=64, dur=2.6, sfx="sfx/pop.wav", sfx_db=-6)] pop a word on a coloured
box (and play its sound) where the narration reaches the phrase, x and y on the 16:9 picture (STICKER_FONT: its font);
LABELS = dict(chap=(fill, edge), title=(fill, edge)) recolours the chapter labels and the title (ASS &HBBGGRR colours).
A film look: FILM = dict(bars=130, warm=0.08, vignette=0.35) adds black bars (wide cuts only), a warm grade and a vignette.
"""
import os, subprocess, sys
import numpy as np
from common import load_project, jload, venc, chapters, written, narration, words_path, transcribe, align, lines, \
    ass_time, sub_styles, sub_events, translations, asr_language
from dreamfab.workflow import get as workflow

W, H, FPS = 1920, 1080, 30
GOLD_BGR, GOLD_ASS = (96, 200, 232), "&H0060C8E8"


def srt_time(t):
    return f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(t % 1 * 1000):03d}"


def music_track(proj, chaps, total, work, start=None):
    """One section of the music per chapter (CH_MUSIC: chapter heading prefix -> second in the file), each levelled to
    MUSIC_DB (RMS, dBFS) and cross-faded into the next a second before the chapter starts. start: one section from
    that second for the whole video (a Short). Without CH_MUSIC the music plays straight through from the top."""
    src_file = os.path.join(proj.DIR, proj.MUSIC)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src_file, "-ac", "1", "-ar", "8000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    mono = np.frombuffer(raw, np.float32)
    starts, target = getattr(proj, "CH_MUSIC", {}), getattr(proj, "MUSIC_DB", -27)
    if start is None and not starts:   # a piece written for this video: no sections to pick, keep it whole
        start, chaps = 0.0, []
    segs = []
    for k, (t, name) in enumerate(chaps or [(0.0, "")]):
        a = 0.0 if k == 0 else t - 1.0
        b = total if k + 1 >= len(chaps) else chaps[k + 1][0] - 1.0
        src = start if start is not None else next((s for key, s in starts.items() if name.startswith(key)), 0.0)
        dur = b - a + 2.0
        x = mono[int(src * 8000): int((src + dur) * 8000)]
        rms = 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9) if len(x) else target
        segs.append((src, dur, float(np.clip(target - rms, -12, 10))))
    cmd, fl = ["ffmpeg", "-v", "error", "-y"], []
    for k, (src, dur, g) in enumerate(segs):
        cmd += ["-ss", f"{src:.3f}", "-t", f"{dur:.3f}", "-i", src_file]
        fl.append(f"[{k}:a]aresample=48000,volume={g:.1f}dB[s{k}]")
    cur = "[s0]"
    for k in range(1, len(segs)):
        fl.append(f"{cur}[s{k}]acrossfade=d=2.0:c1=tri:c2=tri[x{k}]"); cur = f"[x{k}]"
    fl.append(f"{cur}apad,atrim=0:{total:.3f},afade=t=in:d=1.2,afade=t=out:st={total - 3:.3f}:d=3[m]")
    out = os.path.join(work, "music.wav")
    subprocess.run(cmd + ["-filter_complex", ";".join(fl), "-map", "[m]", out], check=True)
    return out


def build():
    import cv2
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    proj = load_project(sys.argv[1])
    D, args = proj.DIR, sys.argv[2:]
    until = args[args.index("--until") + 1] if "--until" in args else None
    S = getattr(proj, "SHORTS", None) if "--shorts" in args else None
    if "--shorts" in args and not S:
        sys.exit("--shorts needs SHORTS = dict(clips=[...], ...) in project.py")
    cut = args[args.index("--cut") + 1] if "--cut" in args else None
    if cut:
        if cut not in getattr(proj, "CUTS", {}):
            sys.exit(f"--cut {cut}: no CUTS[{cut!r}] in project.py")
        S = proj.CUTS[cut]
    aspect = S.get("aspect", "9:16") if S else "16:9"
    vert = aspect != "16:9"   # the picture is set across the middle of a taller frame (a Short, a square cut)
    suffix = f"_{cut}" if cut else getattr(proj, "EDITS", {}).get("shorts", {}).get("suffix", "_shorts") if S else ""
    out = os.path.join(D, args[args.index("--out") + 1] if "--out" in args else f"out/{proj.NAME}{suffix}.mp4")
    work = os.path.join(D, "out", f"_work_{cut}" if cut else "_work_shorts" if S else "_work"); os.makedirs(work, exist_ok=True)
    gaps = dict(dict(lead=1.6, chapter=1.4, title=3.4, part=0.4, end=5.5, xfade=0.9), **getattr(proj, "GAPS", {}))
    if S:   # a Short starts on the first word, cuts tight and ends on its closing line
        gaps.update(lead=0.3, part=0.45, end=3.0, xfade=0.6)
    LEAD, XF = gaps["lead"], gaps["xfade"]
    title, endcard = getattr(proj, "TITLE", None), getattr(proj, "ENDCARD", "")
    font, fonts = getattr(proj, "FONT", ("Explainer Serif", "fonts"))
    fonts = next((p for p in (os.path.join(D, fonts), os.path.join(D, "..", fonts)) if os.path.isdir(p)), os.path.join(D, fonts))
    lang = getattr(proj, "RENDER", {}).get("lang", "zh-TW")
    sub = dict(dict(style="outline", font=font, size=58), **getattr(proj, "SUBS", {}))
    OW, OH = {"9:16": (1080, 1920), "1:1": (1080, 1080)}.get(aspect, (W, H))   # pictures are drawn 16:9 and set into it
    layout, pic_y, pic_h = "band", 0, H
    if vert:
        layout = args[args.index("--layout") + 1] if "--layout" in args else \
            S.get("layout") or workflow("explain.shorts_layout", D)
        if layout not in ("band", "square"):
            sys.exit("--layout is band or square")
        if aspect == "1:1":
            layout = "band"
        pic_h = OW if layout == "square" else OW * H // W        # the picture across the middle of the phone
        pic_y = 150 if aspect == "1:1" else 380 if layout == "square" else 520
        # subtitles under the picture (band) or over its lower edge (square), above the Shorts title and buttons that
        # cover the bottom fifth of the screen; heavy edges keep them readable on either
        sub = dict(sub, style="pop" if sub["style"] == "pop" else "heavy", size=S.get("sub_size", 68 if aspect == "9:16" else 54),
                   side=70, margin=max(40, OH - (1430 if layout == "square" else 1330)))

    # narration: each part's spoken text -> subtitle text and a time for every character; cut into one piece per
    # chapter and laid on the timeline with a breath between chapters (and the title after the first one)
    heads = [(h, t[:8]) for h, t in chapters(proj)]
    parts, items = [], narration(proj)
    missing = [it["audio"] for it in items if not it.get("sound") and not os.path.exists(words_path(it["audio"]))]
    if missing:   # a freshly cut or re-read file: time its words first
        transcribe(missing, language=asr_language(proj))
    for it in items:
        if it.get("sound"):
            d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                      it["audio"]], capture_output=True, text=True, check=True).stdout)
            parts.append(dict(path=it["audio"], text="", ct=[], dur=d, sound=True)); continue
        w = jload(words_path(it["audio"]))
        ct, _ = align(it["text"], w["words"])
        parts.append(dict(path=it["audio"], text=written(it["text"], proj), ct=ct, dur=w["duration"]))
    pieces = []   # (part, first char, end char, from s in the file, to s in the file, chapter heading or None)
    nh = 0        # chapters come in order: look only for the next heading, after the last one (an opening quote can recur)
    for pi, p in enumerate(parts):
        if p.get("sound"):
            pieces.append((pi, 0, 0, 0.0, p["dur"], None)); continue
        text, ct = p["text"], p["ct"]
        starts, at = [], 0
        while nh < len(heads) and heads[nh][1] in text[at:]:
            at = text.index(heads[nh][1], at)
            starts.append((at, heads[nh][0])); nh += 1; at += 1
        if not starts or starts[0][0] > 0:
            starts = [(0, None)] + starts
        stop = text.index(until) if until and until in text else len(text)
        for k, (a, name) in enumerate(starts):
            b = starts[k + 1][0] if k + 1 < len(starts) else len(text)
            if a >= stop:
                break
            b = min(b, stop)
            first = next(ct[i] for i in range(a, b) if ct[i])[0]
            last = next(ct[i] for i in range(b - 1, a - 1, -1) if ct[i])[1]
            fa = 0.0 if a == 0 else (first + next(ct[i] for i in range(a - 1, -1, -1) if ct[i])[1]) / 2
            fb = p["dur"] if b == len(text) else (last + next(ct[i] for i in range(b, len(text)) if ct[i])[0]) / 2
            pieces.append((pi, a, b, fa, fb, name))
        if stop < len(text):
            break
    if S:   # a Short plays the clips, not whole chapters
        pieces = []
        for frm, to in S["clips"]:
            pi = next((k for k, p in enumerate(parts) if frm in p["text"]), None)
            if pi is None:
                sys.exit(f"SHORTS clip {frm!r} is not in the narration")
            text, ct = parts[pi]["text"], parts[pi]["ct"]
            a = text.index(frm)
            if to and to not in text[a:]:
                sys.exit(f"SHORTS clip {frm!r}: {to!r} does not come after it in the same part")
            b = text.index(to, a) if to else len(text)
            first = next(ct[i] for i in range(a, b) if ct[i])[0]
            last = next(ct[i] for i in range(b - 1, a - 1, -1) if ct[i])[1]
            prev = next((ct[i][1] for i in range(a - 1, -1, -1) if ct[i]), None)
            nxt = next((ct[i][0] for i in range(b, len(text)) if ct[i]), None)
            fa = 0.0 if prev is None else (first + prev) / 2
            fb = parts[pi]["dur"] if nxt is None else (last + nxt) / 2
            pieces.append((pi, a, b, fa, fb, None))
    first_head = heads[0][0] if heads else None
    t, place, chaps = LEAD, [], []
    for k, (pi, a, b, fa, fb, name) in enumerate(pieces):
        if name:
            chaps.append((t + parts[pi]["ct"][next(i for i in range(a, b) if parts[pi]["ct"][i])][0] - fa, name))
        place.append(t - fa)
        t += fb - fa
        if k + 1 < len(pieces):
            nxt = pieces[k + 1][5]
            t += (gaps["title"] if title and name == first_head else gaps["chapter"]) if nxt else gaps["part"]
    narr_end = t
    total = narr_end + (3.2 if until else gaps["end"])
    facts, fact_s = ([] if S or until else list(getattr(proj, "FACTS", []))), getattr(proj, "FACTS_S", 2.4)
    facts_t0 = narr_end + 1.0
    if facts:   # the fact cards come before the end card, which keeps its place at the very end
        total += 1.0 + len(facts) * fact_s
    end_at = facts_t0 + len(facts) * fact_s + 0.3 if facts else narr_end + 1.3

    def when(pi, i):   # seconds into the video of character i of part pi
        k = next(k for k, pc in enumerate(pieces) if pc[0] == pi and pc[1] <= i < pc[2])
        return place[k] + parts[pi]["ct"][i][0], place[k] + parts[pi]["ct"][i][1]

    subs, tr = [], translations(proj)

    def units(text, a, b, width):
        """(first, end, shown, translation): one per script line when the script has translations, else lines()."""
        if not tr:
            return [(x + a, y + a, shown, None) for x, y, shown in lines(text[a:b], width=width)]
        out, i = [], a
        for ln in text[a:b].split("\n"):
            if ln.strip():
                x = i + len(ln) - len(ln.lstrip())
                t2 = tr.get(ln.strip())
                out.append((x, i + len(ln.rstrip()), ln.strip().rstrip("、。,."), t2 and t2.rstrip("，、。,.")))
            i += len(ln) + 1
        return out
    if S:   # each clip on its own, in lines narrow enough for a phone
        for pi, a, b, *_ in pieces:
            for x, y, shown, t2 in units(parts[pi]["text"], a, b, 12 if vert else 20):
                ts = [when(pi, i) for i in range(x, y) if parts[pi]["ct"][i]]
                subs.append((ts[0][0], ts[-1][1], shown, t2))
    for pi, p in enumerate(parts if not S else []):
        lim = max([pc[2] for pc in pieces if pc[0] == pi], default=0)
        for a, b, shown, t2 in units(p["text"], 0, lim, 20):
            ts = [when(pi, i) for i in range(a, b) if p["ct"][i]]
            subs.append((ts[0][0], ts[-1][1], shown, t2))
    for i, (a, b, s, t2) in enumerate(subs):   # hold each line a little, never into the next one
        nxt = subs[i + 1][0] if i + 1 < len(subs) else total
        # end before the next one starts (it starts 0.05 s early): two lines on screen at once and libass lifts the
        # second above the first for the whole of its time
        subs[i] = (a - 0.05, min(max(b + 0.35, a + 1.0), nxt - 0.07), s, t2)
    both = lambda s, t2: s + (f"\\N{{\\rTr}}{t2}" if t2 else "")   # the translation under its line

    # pictures: each comes in where the narration reaches its first words
    gtext = "".join(p["text"] + "\u0000" for p in parts)
    offs = np.cumsum([0] + [len(p["text"]) + 1 for p in parts])
    shots, starts, pos = [], [], 0
    for img, phrase, mv, focus in proj.SHOTS:
        if phrase is None:
            shots.append((img, mv, focus)); starts.append(0.0); continue
        g = gtext.find(phrase, pos)
        if g < 0:
            print(f"  shot {img}: {phrase!r} is not in the narration (or comes before the previous shot's words)"); continue
        pi = int(np.searchsorted(offs, g, side="right") - 1); i = g - offs[pi]
        if not any(pc[0] == pi and pc[1] <= i < pc[2] for pc in pieces):
            continue
        i = next(j for j in range(i, len(parts[pi]["text"])) if parts[pi]["ct"][j])
        shots.append((img, mv, focus)); starts.append(when(pi, i)[0] - 0.15); pos = g + len(phrase)
    if S:   # a clip can start in the middle of a shot: the picture that is up there comes in with the clip
        found, pos = [], 0
        for img, phrase, mv, focus in proj.SHOTS:
            g = 0 if phrase is None else gtext.find(phrase, pos)
            if g >= 0:
                found.append((g, img, mv, focus)); pos = g + len(phrase or "")
        shots, starts = [], []
        for k, (pi, a, b, fa, fb, _) in enumerate(pieces):
            ga, gb = offs[pi] + a, offs[pi] + b
            inside = [s for s in found if ga <= s[0] < gb]
            before = [s for s in found if s[0] < ga]
            if before and not (inside and inside[0][0] - ga < 4) and (not shots or shots[-1][0] != before[-1][1]):
                shots.append(before[-1][1:]); starts.append(place[k] + fa)
            for g, img, mv, focus in inside:
                i = next(j for j in range(g - offs[pi], b) if parts[pi]["ct"][j])
                shots.append((img, mv, focus)); starts.append(max(place[k] + fa, when(pi, i)[0] - 0.15))
        if shots:
            starts[0] = 0.0
    if not shots:
        sys.exit("no SHOTS")

    # stickers (STICKERS): a word on a coloured box that pops up where the narration reaches its phrase, with a sound
    stickers, pos = [], 0
    for st in getattr(proj, "STICKERS", []) if not until else []:
        g = gtext.find(st["at"], pos)
        if g < 0:
            print(f"  sticker {st['text']!r}: {st['at']!r} is not in the narration (or comes before the last sticker's)"); continue
        pos = g + len(st["at"])
        pi = int(np.searchsorted(offs, g, side="right") - 1); i = g - offs[pi]
        if not any(pc[0] == pi and pc[1] <= i < pc[2] for pc in pieces):
            continue
        i = next(j for j in range(i, len(parts[pi]["text"])) if parts[pi]["ct"][j])
        stickers.append((when(pi, i)[0] + st.get("delay", 0.0), st))

    # subtitles, chapter labels, title, end card
    (chap_fill, chap_edge), (title_fill, title_edge) = (lambda L: (L.get("chap", (GOLD_ASS, "&H60101010")),
                                                                   L.get("title", (GOLD_ASS, "&H40101010"))))(getattr(proj, "LABELS", {}))
    stk_font = getattr(proj, "STICKER_FONT", sub["font"])
    ass = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {OW}", f"PlayResY: {OH}", "WrapStyle: 2", "",
           "[V4+ Styles]",
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, "
           "StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
           *sub_styles(sub),
           f"Style: Chap,{font},36,{chap_fill},&H000000FF,{chap_edge},&H90000000,0,0,0,0,100,100,4,0,1,1.6,1.2,7,90,90,64,1",
           f"Style: Title,{font},120,{title_fill},&H000000FF,{title_edge},&HA0000000,0,0,0,0,100,100,12,0,1,3.2,2.5,5,0,0,0,1",
           f"Style: TitleSub,{font},46,&H00FFFFFF,&H000000FF,&H50101010,&H90000000,0,0,0,0,100,100,6,0,1,2,1.5,5,0,0,0,1",
           f"Style: Head,{font},84,{title_fill},&H000000FF,{title_edge},&H90000000,0,0,0,0,100,100,6,0,1,3.4,2.4,8,60,60,0,1",
           # a sticker: dark letters on an opaque box (BorderStyle 3: the outline colour fills the box), hard shadow
           f"Style: Stk,{stk_font},64,&H00222222,&H000000FF,&H004DE1FF,&H00222222,-1,0,0,0,100,100,1,0,3,16,7,5,0,0,0,1",
           "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    bgr = lambda c: f"&H{c[5:7]}{c[3:5]}{c[1:3]}&".upper()   # "#rrggbb" -> an ASS colour override
    for t0, st in stickers:   # coordinates are on the 16:9 picture; a Short maps them onto its picture
        x, y, size = st.get("x", 960), st.get("y", 200), st.get("size", 84)
        if vert:
            k = pic_h / H
            x = (x - (W - H) / 2) * OW / H if layout == "square" else x * OW / W
            y, size = pic_y + y * k, size * k * 1.25
        col = st.get("color", "#ffe14d")
        ink = st.get("ink", "#222222")
        pop = "\\fscx20\\fscy20\\t(0,140,\\fscx118\\fscy118)\\t(140,240,\\fscx100\\fscy100)\\fad(0,180)"
        at = f"{ass_time(t0)},{ass_time(t0 + st.get('dur', 2.6))},Stk,,0,0,0,,{{\\an5\\pos({x:.0f},{y:.0f})\\frz{st.get('rot', 0)}\\fs{size:.0f}"
        b = round(16 * size / 64)   # the box's padding grows with the letters; a dark box 5 px larger behind it is the outline
        ass.append(f"Dialogue: 3,{at}\\bord{b + 5}\\3c&H222222&\\1c&H222222&{pop}}}{st['text']}")
        ass.append(f"Dialogue: 4,{at}\\bord{b}\\shad0\\3c{bgr(col)}\\1c{bgr(ink)}{pop}}}{st['text']}")
    if vert:   # a line too wide for the phone breaks in two, at a comma near its middle if there is one
        def fit(s, n=13):
            """Latin letters and spaces count about half a character. Break after a comma, else at a space (Korean),
            else anywhere but inside a word in Latin letters."""
            wide = [0.55 if ord(c) < 128 else 1.0 for c in s]
            if sum(wide) <= n:
                return s
            half = sum(wide) / 2
            at = lambda k: abs(sum(wide[:k]) - half)
            word = lambda c: c.isascii() and c.isalnum()
            cut = min([k + 1 for k, c in enumerate(s) if c in "，、：," and 3 < k < len(s) - 3]
                      or [k for k, c in enumerate(s) if c == " " and 2 < k < len(s) - 2]
                      or [k for k in range(2, len(s) - 1) if not (word(s[k - 1]) and word(s[k]))], key=at)
            return s[:cut].rstrip() + "\\N" + s[cut:].lstrip()
        # bilingual lines run to three or four rows: hang them from just under the picture so they grow downwards
        hang = f"{{\\an8\\pos({OW // 2},{pic_y + pic_h + 36})}}" if tr or aspect == "1:1" else ""
        ass += sub_events(sub, [(a, b, hang + both(fit(s), t2 and fit(t2, 16))) for a, b, s, t2 in subs], OW, OH)
        head = "\\N".join(S.get("head", title or ()))
        if head:
            hy, hs = (24, "\\fs52") if aspect == "1:1" else (230 if layout == "square" else 250, "")
            ass.append(f"Dialogue: 1,{ass_time(0)},{ass_time(total)},Head,,0,0,0,,{{\\fad(300,600)\\an8{hs}\\pos({OW // 2},"
                       f"{hy})}}{head}")
    else:
        ass += sub_events(sub, [(a, b, both(s, t2)) for a, b, s, t2 in subs], W, H)
    for t0, name in chaps:
        st = 0.5 if t0 < LEAD + 1 else t0 - 0.2
        ass.append(f"Dialogue: 0,{ass_time(st)},{ass_time(st + 4.5)},Chap,,0,0,0,,{{\\fad(400,500)}}{name}")
    op = next((k for k, pc in enumerate(pieces) if pc[5] and pc[5] == first_head), None)
    if title and op is not None:   # the opening is over: the title comes up
        ts = place[op] + pieces[op][4] + 0.2
        te = (narr_end + 3.0) if op + 1 == len(pieces) else ts + gaps["title"] + 0.6
        ass.append(f"Dialogue: 1,{ass_time(ts)},{ass_time(te)},Title,,0,0,0,,{{\\fad(500,400)\\pos(960,500)}}{title[0]}")
        if len(title) > 1:
            ass.append(f"Dialogue: 1,{ass_time(ts + 0.3)},{ass_time(te)},TitleSub,,0,0,0,,{{\\fad(500,400)\\pos(960,620)}}{title[1]}")
    if S and S.get("end"):   # the closing line over the picture, then the AI note under it
        y = pic_y + pic_h // 2
        ass.append(f"Dialogue: 3,{ass_time(narr_end + 0.2)},{ass_time(total - 0.1)},Head,,0,0,0,,{{\\fad(400,300)\\an5"
                   f"\\fs74\\pos({OW // 2},{y})}}{S['end']}")
        if endcard:
            ass.append(f"Dialogue: 3,{ass_time(narr_end + 0.5)},{ass_time(total - 0.1)},TitleSub,,0,0,0,,{{\\fad(400,300)"
                       f"\\an5\\fs36\\pos({OW // 2},{y + 90})}}{endcard}")
    elif endcard and not until and not S:
        ass.append(f"Dialogue: 1,{ass_time(end_at)},{ass_time(total - 0.2)},TitleSub,,0,0,0,,{{\\fad(600,400)\\fs54\\pos(960,1000)}}{endcard}")
    if facts:   # 查證 above, then one card at a time: the heading in gold, the facts under it
        f_end = facts_t0 + len(facts) * fact_s
        ass.append(f"Dialogue: 1,{ass_time(facts_t0)},{ass_time(f_end)},TitleSub,,0,0,0,,{{\\fad(300,300)\\fs50\\pos(960,280)}}查證")
        for k, (head, body) in enumerate(facts):
            a = facts_t0 + k * fact_s
            ass.append(f"Dialogue: 2,{ass_time(a)},{ass_time(a + fact_s)},Title,,0,0,0,,{{\\fad(150,150)\\an2\\fs76\\pos(960,500)}}{head}")
            body = body.replace("\n", "\\N")
            ass.append(f"Dialogue: 2,{ass_time(a)},{ass_time(a + fact_s)},TitleSub,,0,0,0,,{{\\fad(150,150)\\an8\\fs48\\pos(960,560)}}{body}")
    subp = os.path.join(work, "subs.ass")
    open(subp, "w", encoding="utf-8-sig").write("\n".join(ass) + "\n")

    # sound: the narration pieces in place, the music ducked under them (sidechain)
    cmd, fl, labels = ["ffmpeg", "-v", "error", "-y"], [], []
    for k, (pi, a, b, fa, fb, name) in enumerate(pieces):
        cmd += ["-ss", f"{fa:.3f}", "-t", f"{fb - fa:.3f}", "-i", parts[pi]["path"]]
        fl.append(f"[{k}:a]aresample=48000,afade=t=in:d=0.03,afade=t=out:st={fb - fa - 0.06:.3f}:d=0.06,"
                  f"adelay={int((place[k] + fa) * 1000)}:all=1[n{k}]")
        labels.append(f"[n{k}]")
    n = len(pieces)
    fl.append(f"{''.join(labels)}amix=inputs={n}:normalize=0,apad=whole_dur={total:.3f},atrim=0:{total:.3f},"
              f"loudnorm=I=-16:TP=-2:LRA=9" + (",asplit[v][key]" if getattr(proj, "MUSIC", None) else "[v]"))
    sfx = [(t0, st["sfx"], st.get("sfx_db", -6)) for t0, st in stickers if st.get("sfx")]
    for k, (t0, path, db) in enumerate(sfx):   # each sticker's sound on top of the mix (not ducked, not levelled)
        cmd += ["-i", os.path.join(D, path)]
        fl.append(f"[{n + k}:a]aresample=48000,volume={db}dB,adelay={int(t0 * 1000)}:all=1,apad=whole_dur={total:.3f},"
                  f"atrim=0:{total:.3f}[x{k}]")
    fx = "".join(f"[x{k}]" for k in range(len(sfx)))
    n += len(sfx)
    if not getattr(proj, "MUSIC", None):
        fl.append(f"[v]{fx}amix=inputs={1 + len(sfx)}:normalize=0,alimiter=limit=0.93[a]")
    else:
        start = None
        if S:   # by default the bed reaches the MV clip where the full cut's 結尾 section does (in time with the MV)
            mv = next((k for k, s in enumerate(shots) if s[0].startswith("MV:")), None)
            end_src = next((s for key, s in getattr(proj, "CH_MUSIC", {}).items() if key == "結尾"), None)
            auto = end_src + 0.85 - starts[mv] if mv is not None and end_src is not None else 0.0
            start = S.get("music", max(0.0, auto))
        cmd += ["-i", music_track(proj, chaps, total, work, start=start)]
        fl.append(f"[{n}:a]anull[m]")
        fl.append("[m][key]sidechaincompress=threshold=0.03:ratio=5:attack=60:release=700:makeup=1[md]")
        fl.append(f"[v][md]{fx}amix=inputs={2 + len(sfx)}:normalize=0,alimiter=limit=0.93[a]")
    wav = os.path.join(work, "mix.wav")
    subprocess.run(cmd + ["-filter_complex", ";".join(fl), "-map", "[a]", "-ac", "2", wav], check=True)

    # pictures: sub-pixel pans and zooms (no jitter), cross-fades, fade in from and out to black
    ends = starts[1:] + [total]
    xf = [min(XF, 0.45 * (ends[i - 1] - starts[i - 1]), 0.45 * (ends[i] - starts[i])) if i else 0 for i in range(len(starts))]
    spans = [(max(0, starts[i] - xf[i] / 2), (starts[i + 1] + xf[i + 1] / 2) if i + 1 < len(starts) else total)
             for i in range(len(starts))]
    cache, clips, strips = {}, {}, {}
    yy, xx = np.mgrid[0:H, 0:W]
    vign = 1 - 0.55 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 2
    navy = (np.dstack([np.full((H, W), 40.0), np.full((H, W), 24.0), np.full((H, W), 14.0)]) * vign[..., None]).astype(np.uint8)

    def img(name):
        if name not in cache:
            p = next((os.path.join(D, "images", name + e) for e in (".png", ".jpg", ".jpeg", ".webp")
                      if os.path.exists(os.path.join(D, "images", name + e))), None)
            if not p:
                sys.exit(f"no images/{name}.png")
            cache[name] = cv2.imdecode(np.fromfile(p, np.uint8), cv2.IMREAD_COLOR)
        return cache[name]

    def framed(f):
        """A frame inside a gold border (room for subtitles below) on a blurred, darkened copy of itself. A Short sets
        every picture into its own frame (vertical below), so a cover or the MV fills it there."""
        if vert:
            return f
        bg = cv2.GaussianBlur(cv2.resize(f, (W // 8, H // 8)), (0, 0), 3)
        bg = (cv2.resize(bg, (W, H)).astype(np.float32) * 0.35).astype(np.uint8)
        s = 0.74; w, h = int(W * s), int(H * s); x, y = (W - w) // 2, int(H * 0.06)
        cv2.rectangle(bg, (x - 4, y - 4), (x + w + 3, y + h + 3), GOLD_BGR, 2, cv2.LINE_AA)
        bg[y:y + h, x:x + w] = cv2.resize(f, (w, h), interpolation=cv2.INTER_AREA)
        return bg

    videos = dict(getattr(proj, "CLIPS", {}), **({"MV": proj.MV_CLIP} if getattr(proj, "MV_CLIP", None) else {}))

    class Clip:
        """A video (MV_CLIP or one of CLIPS) decoded in order from a start second: scaled to the frame, or set in the
        middle of a blurred, darkened copy of itself when its shape is not 16:9 (in the gold frame: framed())."""
        def __init__(self, key, src, dur, gold):
            fill = (f"split[a][b];[a]scale={W // 4}:{H // 4}:force_original_aspect_ratio=increase,crop={W // 4}:{H // 4},"
                    f"gblur=sigma=6,eq=brightness=-0.18,scale={W}:{H}[bg];[b]scale={W}:{H}:force_original_aspect_ratio="
                    f"decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,fps={FPS}")
            self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{src:.3f}", "-t", f"{dur + 1:.3f}",
                                       "-i", os.path.join(D, videos[key]), "-an", "-filter_complex", fill,
                                       "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
            self.n, self.last, self.gold = -1, np.zeros((H, W, 3), np.uint8), gold

        def frame(self, k):
            while self.n < k:
                b = self.p.stdout.read(W * H * 3)
                if len(b) < W * H * 3:
                    break
                self.last = np.frombuffer(b, np.uint8).reshape(H, W, 3); self.n += 1
            return framed(self.last) if self.gold else self.last

    def strip(name):
        """A handscroll drawn as a thin strip on white: cut it out, 430 px high, for the scroll move."""
        if name not in strips:
            im = img(name); g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) < 200
            rows = np.where(g.mean(1) > 0.5)[0]; cols = np.where(g[rows[0]:rows[-1] + 1].mean(0) > 0.5)[0]
            cut = im[rows[0] + 3:rows[-1] - 2, cols[0] + 3:cols[-1] - 2]
            strips[name] = cv2.resize(cut, (int(cut.shape[1] * 430 / cut.shape[0]), 430), interpolation=cv2.INTER_LANCZOS4)
        return strips[name]

    def view(i, t):
        name, mv, focus = shots[i]
        a, b = spans[i]
        key, _, sec = name.rpartition(":")
        if key in videos:
            if i not in clips:
                clips[i] = Clip(key, float(sec), b - a, key == "MV" or mv == "frame")
            return clips[i].frame(int((t - a) * FPS))
        u = min(1, max(0, (t - a) / (b - a)))
        u = 0.75 * u + 0.25 * (0.5 - 0.5 * np.cos(np.pi * u))   # mostly linear: the camera never stops
        fx, fy = focus or (0.5, 0.5)
        if mv == "frame":
            return framed(cv2.resize(img(name), (W, H), interpolation=cv2.INTER_LANCZOS4))
        if mv == "scroll":   # read right to left, the way a Chinese handscroll unrolls
            st = strip(name); vw = int(W * 0.88)
            x0 = (1 - u) * max(0, st.shape[1] - vw)
            win = cv2.warpAffine(st, np.float32([[1, 0, -x0], [0, 1, 0]]), (vw, st.shape[0]), flags=cv2.INTER_LINEAR)
            fr = navy.copy(); y = (H - st.shape[0]) // 2 - 50; x = (W - vw) // 2
            cv2.rectangle(fr, (x - 3, y - 3), (x + vw + 2, y + st.shape[0] + 2), GOLD_BGR, 1, cv2.LINE_AA)
            fr[y:y + st.shape[0], x:x + vw] = win
            return fr
        if mv == "in":
            z = 1.0 + 0.16 * u; cx, cy = 0.5 + (fx - 0.5) * u, 0.5 + (fy - 0.5) * u
        elif mv == "out":
            z = 1.16 - 0.16 * u; cx, cy = fx + (0.5 - fx) * u, fy + (0.5 - fy) * u
        else:
            z = 1.14; d = (1 - 1 / z) / 2 * 0.9; sgn = 1 if mv == "right" else -1
            cx, cy = 0.5 + sgn * d * (2 * u - 1), 0.5
        h = 0.5 / z; cx = min(max(cx, h), 1 - h); cy = min(max(cy, h), 1 - h)
        im = img(name); sh, sw = im.shape[:2]
        sx = W / (sw / z); sy = H / (sh / z)
        M = np.float32([[sx, 0, W / 2 - sx * cx * sw], [0, sy, H / 2 - sy * cy * sh]])
        return cv2.warpAffine(im, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)

    def vertical(fr):
        """A Short's frame: the 16:9 picture (or its middle square) across the phone, gold rules above and below, on a
        blurred, darkened copy of itself that fills the rest."""
        bw = OH * W // H
        bg = cv2.GaussianBlur(cv2.resize(fr, (W // 12, H // 12), interpolation=cv2.INTER_AREA), (0, 0), 2.5)
        bg = cv2.resize(bg, (bw, OH))[:, (bw - OW) // 2:(bw - OW) // 2 + OW] * 0.38
        pic = fr[:, (W - H) // 2:(W + H) // 2] if layout == "square" else fr
        bg[pic_y:pic_y + pic_h] = cv2.resize(pic, (OW, pic_h), interpolation=cv2.INTER_AREA)
        bg[pic_y - 3:pic_y - 1] = GOLD_BGR
        bg[pic_y + pic_h + 1:pic_y + pic_h + 3] = GOLD_BGR
        return bg

    look = getattr(proj, "CARD", None)
    if look:   # CARD: every picture on a white card, tilted, with a hard shadow, on a three-colour diagonal gradient
        cols = [np.array([int(c[i:i + 2], 16) for i in (5, 3, 1)], np.float32) for c in look.get("colors", ("#ffe14d", "#ff7eb3", "#7ad7ff"))]
        u = ((xx / W + yy / H) / 2)[..., None]
        base = np.where(u < 0.5, cols[0] + (cols[1] - cols[0]) * u * 2, cols[1] + (cols[2] - cols[1]) * (u * 2 - 1))
        sc, bd = look.get("scale", 0.74), look.get("border", 12)
        cw, chh = int(W * sc), int(H * sc)
        M = cv2.getRotationMatrix2D((cw / 2 + bd, chh / 2 + bd), look.get("tilt", -1.5), 1.0)
        M[0, 2] += W / 2 - (cw / 2 + bd); M[1, 2] += look.get("top", 36)   # centred across, its top edge at `top`
        ones = np.ones((chh + 2 * bd, cw + 2 * bd), np.float32)
        mask = cv2.warpAffine(ones, M, (W, H))[..., None]
        Ms = M.copy(); Ms[:, 2] += look.get("shadow", 14)
        shade = cv2.warpAffine(ones, Ms, (W, H))[..., None]
        base = base * (1 - shade) + 34 * shade

        def on_card(fr):
            c = np.full((chh + 2 * bd, cw + 2 * bd, 3), 255, np.float32)
            c[bd:bd + chh, bd:bd + cw] = cv2.resize(fr, (cw, chh), interpolation=cv2.INTER_AREA)
            return base * (1 - mask) + cv2.warpAffine(c, M, (W, H), flags=cv2.INTER_LINEAR) * mask
    film = getattr(proj, "FILM", None)
    if film:   # FILM: a cinema look: black bars (2.35:1 at bars=130), a warm grade and a vignette
        bars, w = film.get("bars", 130), film.get("warm", 0.08)
        v = 1 - film.get("vignette", 0.35) * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 2
        grade = (v[..., None] * np.array([1 - w, 1, 1 + w * 0.6], np.float32)).astype(np.float32)   # BGR
    card = ((S.get("end") if S else endcard) or facts) and not until
    esc = lambda p: os.path.abspath(p).replace("\\", "/").replace(":", "\\:")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{OW}x{OH}", "-r", str(FPS),
                            "-i", "-", "-i", wav, "-vf", f"subtitles='{esc(subp)}':fontsdir='{esc(fonts)}'",
                            *venc("final"), "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", out],
                           stdin=subprocess.PIPE)
    for f in range(int(round(total * FPS))):
        t = f / FPS
        live = [i for i, (a, b) in enumerate(spans) if a <= t < b] or [len(spans) - 1]
        fr = view(live[0], t).astype(np.float32)
        if len(live) > 1:
            a = min(1, max(0, (t - spans[live[1]][0]) / max(xf[live[1]], 1e-3)))
            fr = fr * (1 - a) + view(live[1], t).astype(np.float32) * a
        if look and not vert:   # a Short keeps the picture as large as the phone allows
            fr = on_card(fr)
        if film:
            fr = fr * grade
            if bars and not vert:
                fr[:bars] = 0; fr[H - bars:] = 0
        if vert:
            fr = vertical(fr)
        g = min(1, t / 0.8, (total - t) / 1.2) if not S else min(1, t / 0.25, (total - t) / 0.8)
        if card:
            g *= 1 - 0.6 * min(1, max(0, (t - narr_end - (0.0 if S else 0.8)) / (0.5 if S else 1.0)))   # darken under the end card
            if facts:   # darker still under the fact cards, easing back for the end card
                g *= 1 - 0.65 * min(1, max(0, (t - narr_end - 0.8) / 1.0), max(0, (end_at - t) / 0.8))
        enc.stdin.write(np.clip(fr * g, 0, 255).astype(np.uint8).tobytes())
        if f % (FPS * 30) == 0:
            print(f"  {t:.0f}/{total:.0f} s", flush=True)
    enc.stdin.close(); enc.wait()
    for c in clips.values():
        c.p.kill()
    langs = [(lang, 2)] + ([(getattr(proj, "RENDER", {}).get("lang2", "zh-TW"), 3)] if tr else [])
    for code, k in langs:   # one .srt per language: YouTube takes each as its own caption track
        rows = [(e[0], e[1], e[k]) for e in subs if e[k]]
        open(os.path.splitext(out)[0] + f".{code}.srt", "w", encoding="utf-8").write(
            "".join(f"{n + 1}\n{srt_time(a)} --> {srt_time(b)}\n{s}\n\n" for n, (a, b, s) in enumerate(rows)))
    print(f"{os.path.relpath(out, D)}  {total:.1f} s, {len(subs)} subtitle lines, {len(shots)} pictures, chapters at "
          + ", ".join(f"{int(t0 // 60)}:{int(t0 % 60):02d}" if k else "0:00" for k, (t0, _) in enumerate(chaps)))   # YouTube wants 0:00 first


if __name__ == "__main__":
    build()
    a = sys.argv[2:]
    if not any(x in a for x in ("--shorts", "--cut", "--until", "--out", "--full-only")):
        proj = load_project(sys.argv[1])
        if getattr(proj, "SHORTS", None) and workflow("explain.shorts", sys.argv[1]):
            sys.argv.append("--shorts")
            build()
            sys.argv.pop()
        for name in getattr(proj, "CUTS", {}):   # an ad's shorter versions
            sys.argv += ["--cut", name]
            build()
            del sys.argv[-2:]
