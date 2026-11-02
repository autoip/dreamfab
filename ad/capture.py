"""A 1920x1080 screenshot of a web page as a visitor in another country sees it -> a picture for SHOTS (no credits).

usage: python ad/capture.py URL OUT.png [--lang ja] [--hide-corner]
  --lang         the browser's language and Accept-Language: a site that picks its language from the visitor's
                 browser shows that version (a /locale/xx link usually only sets a cookie the headless browser drops)
  --hide-corner  paint over the bottom-right corner (a reCAPTCHA badge) with the page's own background
Put a white page in the gold frame (move "frame" in SHOTS) so the subtitles below it stay readable.
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cards import shoot

if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 2:
        sys.exit(__doc__)
    url, out = a[0], a[1]
    lang = a[a.index("--lang") + 1] if "--lang" in a else None
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    if not shoot(url, out, lang=lang, wait=10000):
        sys.exit("no screenshot (is the address right?)")
    if "--hide-corner" in a:
        from PIL import Image, ImageDraw
        im = Image.open(out).convert("RGB")
        ImageDraw.Draw(im).rectangle((1840, 995, 1920, 1080), fill=im.getpixel((1800, 980)))
        im.save(out)
    print(out)
