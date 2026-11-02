"""Render every market version of an ad campaign (each with its cuts) and write the delivery list (no credits).

usage: python ad/render.py CAMPAIGN_DIR [FOLDER ...] [--cards] [--list]
  FOLDER   only these language folders (default: every folder whose project.py says LINE = "ad")
  --cards  redraw the cards first (ad/cards.py)
  --list   only write the delivery list from what is already in out/
Each version renders with explain/render.py (the full cut, then every CUTS entry, and the Short if SHORTS is set).
CAMPAIGN_DIR/delivery.md lists every file: language, cut, size, length, loudness and its caption files.
"""
import glob, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


def versions(camp, only):
    out = []
    for d in sorted(glob.glob(os.path.join(camp, "*", "project.py"))):
        src = open(d, encoding="utf-8").read()
        if re.search(r"^LINE\s*=\s*[\"']ad", src, re.M) and (not only or os.path.basename(os.path.dirname(d)) in only):
            out.append(os.path.dirname(d))
    return out


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration",
                        "-of", "default=nw=1", path], capture_output=True, text=True).stdout
    v = dict(l.split("=") for l in r.split() if "=" in l)
    lufs = re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "ebur128=framelog=quiet",
                                                               "-f", "null", "-"], capture_output=True, text=True).stderr)
    return f"{v.get('width')}x{v.get('height')}", float(v.get("duration", 0)), lufs[-1] if lufs else "?"


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    camp, only = a[0], [x for x in a[1:] if not x.startswith("--")]
    todo = versions(camp, only)
    if not todo:
        sys.exit(f"no ad versions in {camp} (folders with a project.py that says LINE = \"ad\")")
    py = sys.executable
    for d in todo if "--list" not in a else []:
        print(f"== {os.path.basename(d)}")
        if "--cards" in a:
            subprocess.run([py, os.path.join(HERE, "cards.py"), d], check=True)
        subprocess.run([py, os.path.join(REPO, "explain", "render.py"), d], check=True)
    rows = ["# 交件清單", "", "| 版本 | 檔案 | 尺寸 | 長度 | 響度 | 字幕 |", "|---|---|---|---|---|---|"]
    for d in todo:
        for f in sorted(glob.glob(os.path.join(d, "out", "*.mp4"))):
            if os.path.basename(f).startswith("_"):
                continue
            size, dur, lufs = probe(f)
            subs = ", ".join(os.path.basename(s) for s in sorted(glob.glob(os.path.splitext(f)[0] + ".*.srt")))
            rows.append(f"| {os.path.basename(d)} | {os.path.relpath(f, camp)} | {size} | {dur:.1f} s | {lufs} LUFS | {subs} |")
    open(os.path.join(camp, "delivery.md"), "w", encoding="utf-8", newline="\n").write("\n".join(rows) + "\n")
    print("\n".join(rows))
