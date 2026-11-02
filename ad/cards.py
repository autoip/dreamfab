"""Cards for an ad, drawn as HTML in the project's style pack and shot with a headless browser at 1920x1080 ->
images/<id>.png (no credits). The renderer uses them like any other picture (SHOTS).

usage: python ad/cards.py PROJECT_DIR [ID ...]       every card in CARDS, or just these

project.py:
  STYLE = "variety"                      a pack in ad/styles.py: its theme colours the cards
  CARD_FONTS = dict(head="Black Han Sans", body="Malgun Gothic", zh="Microsoft JhengHei", web=["Black+Han+Sans"])
                                         web: Google Fonts families loaded for the cards (the cards only; subtitles need
                                         the font installed)
  CARDS = [dict(id="hero", kind="hero", title="...", sub="...", image="images/product.png", tag="NEW"), ...]
kinds (each line may carry a translation as zh="..."; text stays above y 760, clear of the subtitles):
  hero      title, sub, image, tag         a big headline beside the product or a screenshot
  features  title, items=[(head, body, zh)] three or four boxes in a row
  steps     title, sub, steps=[(word, zh)], note    a row of numbered boxes with arrows (a process)
  prompt    lines=[(kind, text)], kind me | ok | q | zh    a terminal window: a request and the agent's replies
  wall      title, zh, files=[path or glob], cols=, ratio=16/9    a grid of covers or thumbnails
  quote     text, who, zh                  a testimonial
  offer     title, price, note, cta, zh    a price and a call to action
  end       brands=[(name, url, zh)], line    the closing card with names and addresses
Browser: Edge or Chrome (DREAMFAB_BROWSER to name one).
"""
import glob, html, os, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # run as a script: the repo root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dreamfab.util import load_project
from styles import PACKS

THEMES = {   # bg, ink, accent, box, box border, box shadow, heading extra
    "navy": dict(bg="radial-gradient(ellipse at 50% 35%,#1d2a3e 0%,#0c121c 70%)", ink="#f4efe2", accent="#e8c860",
                 muted="#cfd6e0", box="#16202f", border="2px solid #e8c860", shadow="none", head="", hcol="#f4efe2"),
    "variety": dict(bg="#fff8e8 radial-gradient(circle,#f3e6c8 2px,transparent 2.5px) 0 0/36px 36px", ink="#222",
                    accent="#ff4f8b", muted="#555", box="#fff", border="4px solid #222", shadow="6px 6px 0 #222",
                    head="-webkit-text-stroke:4px #222;paint-order:stroke fill;text-shadow:6px 6px 0 #222;", hcol="#ff4f8b"),
    "keynote": dict(bg="#f7f8fa", ink="#111", accent="#3166ff", muted="#5b6b8c", box="#fff", border="none",
                    shadow="0 18px 50px rgba(20,40,90,.12)", head="letter-spacing:-2px;", hcol="#111"),
    "cinematic": dict(bg="radial-gradient(ellipse at 50% 40%,#2a2118 0%,#0b0a09 75%)", ink="#f3e3c3", accent="#d9b77a",
                      muted="#bfae8e", box="rgba(255,255,255,.04)", border="1px solid #d9b77a55", shadow="none",
                      head="font-weight:600;letter-spacing:6px;", hcol="#f3e3c3"),
}


def browser():
    if os.environ.get("DREAMFAB_BROWSER"):
        return os.environ["DREAMFAB_BROWSER"]
    for p in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"):
        if os.path.exists(p):
            return p
    for n in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge"):
        if shutil.which(n):
            return shutil.which(n)
    sys.exit("no Edge or Chrome found: set DREAMFAB_BROWSER")


def shoot(html_path, png, lang=None, wait=8000):
    """A 1920x1080 screenshot of a page (a local file or a URL) in a headless browser."""
    cmd = [browser(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1920,1080",
           f"--virtual-time-budget={wait}", f"--screenshot={os.path.abspath(png)}"]
    if lang:
        cmd += [f"--lang={lang}", f"--accept-lang={lang}"]
    url = html_path if "://" in html_path else "file:///" + os.path.abspath(html_path).replace("\\", "/")
    subprocess.run(cmd + [url], capture_output=True)
    return os.path.exists(png)


def build(proj, card):
    t = THEMES[PACKS[getattr(proj, "STYLE", "documentary")]["theme"]]
    f = dict(dict(head="sans-serif", body="sans-serif", zh="Microsoft JhengHei", web=[]), **getattr(proj, "CARD_FONTS", {}))
    E = html.escape
    url = lambda p: "file:///" + os.path.abspath(os.path.join(proj.DIR, p)).replace("\\", "/")
    zh = lambda s: f"<span class='zh'>　{E(s)}</span>" if s else ""
    k = card["kind"]
    if k == "hero":
        img = f"<div class='pic'><img src='{url(card['image'])}'></div>" if card.get("image") else ""
        tag = f"<div class='tag'>{E(card['tag'])}</div>" if card.get("tag") else ""
        body = (f"{img}<div class='txt'>{tag}<div class='h'>{E(card['title']).replace(chr(10), '<br>')}</div>"
                f"<div class='s'>{E(card.get('sub', ''))}</div><div class='zh b'>{E(card.get('zh', ''))}</div></div>")
        css = (".pic{position:absolute;right:140px;top:110px;width:720px;height:620px;border-radius:28px;overflow:hidden;"
               "background:var(--box);border:var(--border);box-shadow:var(--shadow)}.pic img{width:100%;height:100%;object-fit:cover}"
               ".txt{position:absolute;left:150px;top:150px;width:"
               + ("880px" if img else "1620px") + "}.h{font-family:var(--head);font-size:104px;line-height:1.12;color:var(--hcol);"
               "font-weight:900;var(--hx)}.s{font-size:44px;margin-top:30px;color:var(--muted)}.b{display:block;font-size:32px;margin-top:16px}"
               ".tag{display:inline-block;background:var(--accent);color:#fff;font-size:30px;padding:6px 22px;border-radius:40px;margin-bottom:26px}")
    elif k == "features":
        items = "".join(f"<div class='it'><div class='n'>{n + 1:02d}</div><div class='ih'>{E(h)}</div><div class='ib'>{E(b)}</div>"
                        f"<div class='zh'>{E(z)}</div></div>" for n, (h, b, z) in enumerate(card["items"]))
        body = f"<div class='hd'>{E(card['title'])}{zh(card.get('zh'))}</div><div class='row'>{items}</div>"
        css = (".row{position:absolute;top:250px;left:0;right:0;display:flex;justify-content:center;gap:36px}"
               ".it{width:380px;min-height:360px;padding:36px 32px;box-sizing:border-box;background:var(--box);border:var(--border);"
               "box-shadow:var(--shadow);border-radius:26px}.n{color:var(--accent);font-size:40px;font-weight:900}"
               ".ih{font-family:var(--head);font-size:48px;margin:14px 0;color:var(--ink)}.ib{font-size:30px;line-height:1.45;color:var(--muted)}"
               ".it .zh{font-size:26px;margin-top:14px;display:block}")
    elif k == "steps":
        boxes = "".join(f"<div class='st'><div class='n'>{n + 1}</div><div class='w'>{E(w)}</div><div class='zh'>{E(z)}</div></div>"
                        + ("<div class='ar'>›</div>" if n + 1 < len(card["steps"]) else "") for n, (w, z) in enumerate(card["steps"]))
        body = (f"<div class='top'>{E(card['title'])}</div><div class='sub'>{E(card.get('sub', ''))}{zh(card.get('zh'))}</div>"
                f"<div class='row'>{boxes}</div><div class='note'>{card.get('note', '')}</div>")
        css = (".top{position:absolute;top:130px;width:100%;text-align:center;font-family:var(--head);font-size:120px;color:var(--accent);var(--hx)}"
               ".sub{position:absolute;top:300px;width:100%;text-align:center;font-size:44px}.sub .zh{font-size:32px}"
               ".row{position:absolute;top:420px;width:100%;display:flex;justify-content:center;align-items:center}"
               ".st{width:190px;height:200px;border:var(--border);border-radius:22px;background:var(--box);box-shadow:var(--shadow);"
               "display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px}.n{font-size:28px;color:var(--accent)}"
               ".w{font-family:var(--head);font-size:40px;white-space:nowrap}.st .zh{font-size:26px}.ar{font-size:50px;color:var(--accent);margin:0 4px}"
               ".note{position:absolute;top:680px;width:100%;text-align:center;font-size:36px;color:var(--muted);font-weight:400}"
               ".note b{color:var(--accent);font-weight:400}")
    elif k == "prompt":
        rows = "".join(f"<div class='l {c}'>{E(x)}</div>" for c, x in card["lines"])
        body = (f"<div class='win'><div class='bar'><i></i><i></i><i></i><span>{E(card.get('bar', 'dreamfab — AI agent'))}</span></div>"
                f"<div class='t'>{rows}</div></div>")
        css = (".win{position:absolute;left:260px;top:150px;width:1400px;height:600px;background:#0a0f16;border:2px solid #34445c;"
               "border-radius:20px;box-shadow:0 30px 80px #000a;overflow:hidden}.bar{height:56px;background:#1a2433;display:flex;"
               "align-items:center;padding-left:24px;gap:12px}.bar i{width:18px;height:18px;border-radius:50%;background:var(--accent)}"
               ".bar span{margin-left:20px;color:#9fb0c6;font-size:24px;font-weight:400}.t{padding:40px 56px;font-size:40px;line-height:1.7;color:#fff}"
               ".me:before{content:'› ';color:var(--accent)}.ok{color:#9fd8a8;font-weight:400;font-size:34px}.q{color:#ffe08a;font-size:38px}"
               ".t .zh{font-size:28px;color:#c9b56e;font-weight:400;margin-top:-6px}")
    elif k == "wall":
        files = [x for p in card["files"] for x in (sorted(glob.glob(os.path.join(proj.DIR, p))) if any(c in p for c in "*?[")
                                                     else [os.path.join(proj.DIR, p)])][:card.get("max", 24)]
        cols, ratio = card.get("cols", 5), card.get("ratio", 16 / 9)
        rows = -(-len(files) // cols)
        w = min((1720 - (cols - 1) * 16) // cols, int((600 - (rows - 1) * 16) / rows * ratio))
        cells = "".join(f"<img src='{url(x)}' style='width:{w}px;height:{int(w / ratio)}px'>" for x in files)
        body = (f"<div class='hd'>{E(card['title'])}{zh(card.get('zh'))}</div>"
                f"<div class='grid' style='grid-template-columns:repeat({cols},{w}px)'>{cells}</div>")
        css = (".grid{position:absolute;top:160px;left:0;right:0;margin:auto;width:fit-content;display:grid;gap:16px}"
               ".grid img{object-fit:cover;border-radius:12px;border:var(--border);box-shadow:var(--shadow)}")
    elif k == "quote":
        body = (f"<div class='q'>“{E(card['text'])}”</div><div class='who'>— {E(card.get('who', ''))}</div>"
                f"<div class='zh qz'>{E(card.get('zh', ''))}</div>")
        css = (".q{position:absolute;left:220px;right:220px;top:220px;font-family:var(--head);font-size:72px;line-height:1.3;color:var(--ink)}"
               ".who{position:absolute;left:220px;top:560px;font-size:38px;color:var(--accent)}.qz{position:absolute;left:220px;top:630px;font-size:32px}")
    elif k == "offer":
        body = (f"<div class='box'><div class='ot'>{E(card['title'])}</div><div class='pr'>{E(card.get('price', ''))}</div>"
                f"<div class='on'>{E(card.get('note', ''))}</div><div class='cta'>{E(card.get('cta', ''))}</div>"
                f"<div class='zh oz'>{E(card.get('zh', ''))}</div></div>")
        css = (".box{position:absolute;left:460px;top:90px;width:1000px;height:670px;box-sizing:border-box;padding:44px;text-align:center;"
               "background:var(--box);border:var(--border);box-shadow:var(--shadow);border-radius:36px}.ot{font-family:var(--head);font-size:64px}"
               ".pr{font-family:var(--head);font-size:150px;color:var(--accent);margin:20px 0;var(--hx)}.on{font-size:34px;color:var(--muted)}"
               ".cta{display:inline-block;margin-top:36px;background:var(--accent);color:#fff;font-size:42px;padding:14px 48px;border-radius:60px}"
               ".oz{display:block;font-size:28px;margin-top:22px}")
    elif k == "end":
        n = len(card["brands"])
        cols = "".join(f"<div class='c'><div class='nm'>{E(a)}</div><div class='u'>{E(u)}</div><div class='zh'>{E(z)}</div></div>"
                       + ("<div class='x'>×</div>" if i + 1 < n else "") for i, (a, u, z) in enumerate(card["brands"]))
        body = f"<div class='row'>{cols}</div><div class='line'>{E(card.get('line', ''))}</div>"
        css = (".row{position:absolute;top:300px;left:0;right:0;display:flex;justify-content:center;align-items:center;gap:40px}"
               ".c{text-align:center;max-width:720px}.nm{font-family:var(--head);font-size:118px;color:var(--accent);var(--hx)}"
               ".u{font-size:44px;margin-top:18px}.c .zh{font-size:32px;display:block;margin-top:14px}.x{font-size:80px;color:var(--muted)}"
               ".line{position:absolute;top:640px;width:100%;text-align:center;font-size:40px;color:var(--muted)}")
    else:
        sys.exit(f"card {card['id']}: unknown kind {k!r}")
    head = "".join(f"<link href='https://fonts.googleapis.com/css2?family={w}&display=swap' rel='stylesheet'>" for w in f["web"])
    root = (f":root{{--ink:{t['ink']};--accent:{t['accent']};--muted:{t['muted']};--box:{t['box']};--border:{t['border']};"
            f"--shadow:{t['shadow']};--hcol:{t['hcol']};--head:'{f['head']}',sans-serif}}")
    css = css.replace("var(--hx)", t["head"])
    return (f"<!doctype html><html><head><meta charset='utf-8'>{head}<style>{root}"
            f"html,body{{margin:0;width:1920px;height:1080px;overflow:hidden;background:{t['bg']};color:var(--ink);"
            f"font-family:'{f['body']}',sans-serif;font-weight:700}}"
            f".zh{{font-family:'{f['zh']}',sans-serif;color:var(--accent);font-weight:400}}"
            f".hd{{position:absolute;top:44px;width:100%;text-align:center;font-family:var(--head);font-size:64px}}.hd .zh{{font-size:34px}}"
            f"{css}</style></head><body>{body}</body></html>")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    proj = load_project(sys.argv[1])
    want = set(sys.argv[2:])
    os.makedirs(os.path.join(proj.DIR, "images"), exist_ok=True)
    for c in getattr(proj, "CARDS", []):
        if want and c["id"] not in want:
            continue
        h = os.path.join(proj.DIR, "images", f"_{c['id']}.html")
        open(h, "w", encoding="utf-8").write(build(proj, c))
        print(c["id"], "ok" if shoot(h, os.path.join(proj.DIR, "images", f"{c['id']}.png")) else "FAILED")
