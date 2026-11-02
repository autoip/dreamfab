"""Start an ad campaign: a brief to fill in, then one folder per market language, each with its own style pack.

usage: python ad/new.py CAMPAIGN_DIR --kind product|service|brand --langs ja:documentary,ko:variety,en:keynote [--name NAME]
  CAMPAIGN_DIR   projects/<brand>/<campaign>
  --kind         product (a thing you can hold: hero shot, features, price), service (an app or a business: how it
                 works, features), brand (a feeling: story, testimonial, moments)
  --langs        LANG:PACK pairs (packs: python ad/styles.py); every market gets its own look, as a rule
Writes CAMPAIGN_DIR/brief.md (once) and CAMPAIGN_DIR/<lang>_<pack>/project.py + script.md + suno.md (the music to
paste into Suno), skipping files that exist.
Then: fill in brief.md with the user -> write each script.md (in that language, a translation under every line) ->
cast a narrator per language -> ad/cards.py -> explain/render.py (see docs/en/ad/OVERVIEW.md).
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from styles import PACKS

# subtitle fonts must be installed (these ship with Windows; on macOS use Hiragino Sans, Apple SD Gothic Neo, PingFang TC);
# card headings are web fonts from Google Fonts
FONTS = {
    "ja": dict(sub="Yu Gothic", body="Yu Gothic", head="Noto Sans JP", serif="Noto Serif JP"),
    "ko": dict(sub="Malgun Gothic", body="Malgun Gothic", head="Noto Sans KR", serif="Noto Serif KR", pop="Black Han Sans"),
    "en": dict(sub="Arial", body="Arial", head="Montserrat", serif="Playfair Display"),
    "zh-TW": dict(sub="Microsoft JhengHei", body="Microsoft JhengHei", head="Noto Sans TC", serif="Noto Serif TC"),
    "th": dict(sub="Leelawadee UI", body="Leelawadee UI", head="Noto Sans Thai", serif="Noto Serif Thai"),
    "vi": dict(sub="Arial", body="Arial", head="Be Vietnam Pro", serif="Noto Serif"),
}
SINGLE = {"Black Han Sans": "Black+Han+Sans"}   # web fonts with one weight (asking for 700;900 fails)
CARDS = {
    "product": '''[
    dict(id="hero", kind="hero", title="(headline)", sub="(one line)", image="images/product.png", tag="NEW", zh="(中文)"),
    dict(id="features", kind="features", title="(why it is good)", zh="(中文)",
         items=[("(feature)", "(one line)", "(中文)"), ("(feature)", "(one line)", "(中文)"), ("(feature)", "(one line)", "(中文)")]),
    dict(id="offer", kind="offer", title="(product name)", price="(price)", note="(where to buy)", cta="(call to action)", zh="(中文)"),
    dict(id="end", kind="end", brands=[("(brand)", "(address)", "(中文)")], line="(closing line)"),
]''',
    "service": '''[
    dict(id="hero", kind="hero", title="(headline)", sub="(one line)", image="images/site.png", zh="(中文)"),
    dict(id="steps", kind="steps", title="(service)", sub="(how it works)", zh="(中文)",
         steps=[("(step)", "(中文)"), ("(step)", "(中文)"), ("(step)", "(中文)"), ("(step)", "(中文)")]),
    dict(id="features", kind="features", title="(what you get)", zh="(中文)",
         items=[("(feature)", "(one line)", "(中文)"), ("(feature)", "(one line)", "(中文)"), ("(feature)", "(one line)", "(中文)")]),
    dict(id="end", kind="end", brands=[("(service)", "(address)", "(中文)")], line="(closing line)"),
]''',
    "brand": '''[
    dict(id="hero", kind="hero", title="(the brand's promise)", sub="(one line)", zh="(中文)"),
    dict(id="quote", kind="quote", text="(a customer's words)", who="(who)", zh="(中文)"),
    dict(id="moments", kind="wall", title="(moments)", zh="(中文)", files=["images/moment_*.png"], cols=3),
    dict(id="end", kind="end", brands=[("(brand)", "(address)", "(中文)")], line="(closing line)"),
]''',
}
BRIEF = """# {name}：廣告簡報

> 和使用者一起填完再寫文案。每一句文案都要能對回這裡的事實。

- 類型：{kind}（product 實體商品／service 服務／brand 品牌）
- 名稱、一句話說明：
- 給誰看（市場、年紀、他們在意什麼）：
- 三個重點（好處，不是規格）：
- 證據（實際作品、數字、評價、截圖；每一個都要查得到）：
- 要對方做什麼（行動呼籲）、網址：
- 長度：主版 __ 秒；短版 30 秒、15 秒（CUTS）
- 尺寸：16:9／9:16／1:1
- 市場版本：{langs}
- 不能說的話（誇大、比較、醫療療效、價格會變的……）：
- 配樂：建議 Suno（agent 寫 suno.md 的曲風和歌詞，使用者貼進 Suno 生成）；全自動就用 AutoIP 作曲；片中不能說錯配樂是誰做的

## 查核（交件前逐條打勾）

- [ ] 數字和事實都對得上簡報的證據
- [ ] 網址、品牌名拼對；每個語言的片尾卡都看過
- [ ] 沒有冒用真實人物、品牌、商標
- [ ] 旁白聽寫比對的疑點都聽過
"""
SUNO = """# {name}（{lang}，{pack}）：Suno 配樂

> 建議用 Suno 做配樂。Suno 目前沒有開放一般使用者用 API，所以由 agent 依簡報和風格包寫好，使用者貼進 Suno
> （Custom 模式）生成，挑一首下載，放進 `../music/{name}_{lang}.mp3`。片中不能說配樂是 AutoIP 做的。

- Title：{name} {lang}
- Instrumental：開（墊在旁白底下的配樂）
- Style of Music（照這支廣告的情緒改寫）：

```
{music}
```

- Exclude styles：`vocals, vocal chops, choir, heavy drop`
- 長度：比主版多 10 秒以上；太短就在拍點上把中間段落重複接長

## 選用：唱出品牌名的 jingle（Instrumental 關掉）

品牌名、口號、網址照簡報寫，用 {lang} 唱；段落標記照 Suno 的寫法。

```
[Intro]

[Hook]
(brand name, one line of promise)

[Outro]
(brand name)
```
"""
SCRIPT = """# {name}（{lang}，{pack}）

> 每一行＝一句字幕（一列放得下）；下一行「> 」是中文翻譯（雙語字幕，`>` 開頭不會唸出來）。

## 旁白

### 開場

(hook: the first three seconds)
> （開場鉤子）

### 重點

(benefit)
> （好處）

### 結尾

(call to action)
> （行動呼籲）
"""
PROJECT = '''# {name}：{lang} 版（{pack}：{label}）
# 廣告線 ad/：explain/render.py 合成、ad/cards.py 畫卡片；簡報在 ../brief.md
LINE = "ad"
NAME = "{name}_{lang}"
RENDER = {{"lang": "{lang}", "lang2": "zh-TW"}}
SCRIPT = "script.md"
STYLE = "{pack}"
# 旁白：文生影片做一位新的旁白開口（../voices/raw/），切 5-15 s 當樣本；語氣照風格包：{voice}
VOICE = "../voices/NARR_{LANG}.wav"
VOICE_FIELDS = dict(voice_engine="voxcpm2")
SAY = []
GAPS = dict(lead=0.8, chapter=0.6, title=2.2, part=0.4, end=3.5, xfade=0.6)   # an ad is tighter than an explainer
CHAPTER_LABELS = False   # no chapter names on screen

TITLE = ("(title)", "(subtitle)")
ENDCARD = ""
FONT = ("{sub}", "../fonts")   # titles and labels: an installed font (libass cannot use web fonts)
{fields}
CARD_FONTS = dict(head="{head_font}", body="{body}", zh="Microsoft JhengHei", web=["{web}"])
STICKER_FONT = "{sub}"

# 配樂：建議 Suno。照 suno.md 貼進 Suno 生成（Suno 沒有開放一般使用者用 API），下載放進 ../music/；
# 全自動就用 AutoIP 作曲（/voice/song）。沒寫 CH_MUSIC 就一路放
MUSIC = "../music/{name}_{lang}.mp3"
MUSIC_DB = -26

# 卡片（ad/cards.py）：每張一個 id，畫成 images/<id>.png，SHOTS 直接用 id
CARDS = {cards}

# 影片片段（現有作品、產品影片）：SHOTS 寫 "代號:秒"
CLIPS = {{}}

# (圖, 從哪句開始, 運鏡, 焦點)；運鏡 in / out / left / right / frame
SHOTS = [
    ("hero", None, "in", None),
]

# 短版：同一份旁白剪的片段（從哪幾個字, 到哪幾個字之前 / None）；16:9、9:16、1:1
CUTS = {{
    # "30": dict(clips=[("...", "..."), ("...", None)], aspect="16:9"),
    # "15": dict(clips=[("...", "..."), ("...", None)], aspect="9:16", head=("(head)",)),
    # "15sq": dict(clips=[("...", "..."), ("...", None)], aspect="1:1", head=("(head)",)),
}}
'''

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or "--kind" not in a or "--langs" not in a:
        sys.exit(__doc__)
    camp, kind = a[0], a[a.index("--kind") + 1]
    if kind not in CARDS:
        sys.exit("--kind is product, service or brand")
    pairs = [x.split(":") for x in a[a.index("--langs") + 1].split(",")]
    name = a[a.index("--name") + 1] if "--name" in a else os.path.basename(os.path.normpath(camp))
    os.makedirs(camp, exist_ok=True)

    def write(path, text):
        if os.path.exists(path):
            print("  kept   ", path); return
        open(path, "w", encoding="utf-8", newline="\n").write(text)
        print("  wrote  ", path)
    write(os.path.join(camp, "brief.md"), BRIEF.format(name=name, kind=kind, langs=", ".join(f"{l}:{p}" for l, p in pairs)))
    for lang, pack in pairs:
        if pack not in PACKS:
            sys.exit(f"no style pack {pack!r}: python ad/styles.py")
        P, F = PACKS[pack], FONTS.get(lang, FONTS["en"])
        head = F.get("pop") if pack == "variety" and F.get("pop") else F["serif"] if pack == "cinematic" else F["head"]
        fields = dict(P["fields"])
        fields["SUBS"] = dict(fields["SUBS"], font=F["sub"], font2="Microsoft JhengHei")
        d = os.path.join(camp, f"{lang}_{pack}")
        os.makedirs(os.path.join(d, "images"), exist_ok=True)
        write(os.path.join(d, "project.py"), PROJECT.format(
            name=name, lang=lang, LANG=lang.upper().replace("-", "_"), pack=pack, label=P["label"], voice=P["voice"],
            music=P["music"], head_font=head, body=F["body"], sub=F["sub"], web=SINGLE.get(head, head.replace(" ", "+") + ":wght@700;900"),
            fields="\n".join(f"{k} = {v!r}" for k, v in fields.items()), cards=CARDS[kind]))
        write(os.path.join(d, "script.md"), SCRIPT.format(name=name, lang=lang, pack=pack))
        write(os.path.join(d, "suno.md"), SUNO.format(name=name, lang=lang, pack=pack, music=P["music"]))
    os.makedirs(os.path.join(camp, "voices", "raw"), exist_ok=True)
    os.makedirs(os.path.join(camp, "fonts"), exist_ok=True)   # subtitle fonts that are not installed go here
