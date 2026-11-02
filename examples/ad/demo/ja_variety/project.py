# kumo_oolong：ja 版（variety：綜藝：亮色漸層、歪斜白框、黃字粗黑邊、貼紙字卡加音效、俏皮旁白）
# 廣告線 ad/：explain/render.py 合成、ad/cards.py 畫卡片；簡報在 ../brief.md
LINE = "ad"
NAME = "kumo_oolong_ja"
RENDER = {"lang": "ja", "lang2": "zh-TW"}
SCRIPT = "script.md"
STYLE = "variety"
# 旁白：文生影片做一位新的旁白開口（../voices/raw/），切 5-15 s 當樣本；語氣照風格包：bright, playful variety-show narrator who laughs as she talks
VOICE = "../voices/NARR_JA.wav"
VOICE_FIELDS = dict(voice_engine="voxcpm2")
SAY = []

TITLE = ("(title)", "(subtitle)")
ENDCARD = ""
FONT = ("Yu Gothic", "../fonts")   # titles and labels: an installed font (libass cannot use web fonts)
SUBS = {'style': 'pop', 'bold': True, 'size': 64, 'size2': 40, 'fill2': '&H00FFFFFF', 'font': 'Yu Gothic', 'font2': 'Microsoft JhengHei'}
CARD = {'colors': ('#ffe14d', '#ff7eb3', '#7ad7ff'), 'scale': 0.74, 'tilt': -1.5, 'border': 12, 'shadow': 14, 'top': 36}
LABELS = {'chap': ('&H00222222', '&H00FFFFFF'), 'title': ('&H004DE1FF', '&H00222222')}
CARD_FONTS = dict(head="Noto Sans JP", body="Yu Gothic", zh="Microsoft JhengHei", web=["Noto+Sans+JP:wght@700;900"])
STICKER_FONT = "Yu Gothic"

# 配樂：自己寫曲風給使用者去 Suno 生成（風格包建議：instrumental, variety show background music, playful funky pop, bouncy slap bass, brass stabs, handclaps, whistle and xylophone accents, cheerful and comedic, 120 BPM, light enough for voiceover），或用 AutoIP 作曲；沒寫 CH_MUSIC 就一路放
MUSIC = "../music/kumo_oolong_ja.mp3"   # 照 suno.md 在 Suno 生成
MUSIC_DB = -26

# 卡片（ad/cards.py）：每張一個 id，畫成 images/<id>.png，SHOTS 直接用 id
CARDS = [
    dict(id="hero", kind="hero", title="(headline)", sub="(one line)", image="images/product.png", tag="NEW", zh="(中文)"),
    dict(id="features", kind="features", title="(why it is good)", zh="(中文)",
         items=[("(feature)", "(one line)", "(中文)"), ("(feature)", "(one line)", "(中文)"), ("(feature)", "(one line)", "(中文)")]),
    dict(id="offer", kind="offer", title="(product name)", price="(price)", note="(where to buy)", cta="(call to action)", zh="(中文)"),
    dict(id="end", kind="end", brands=[("(brand)", "(address)", "(中文)")], line="(closing line)"),
]

# 影片片段（現有作品、產品影片）：SHOTS 寫 "代號:秒"
CLIPS = {}

# (圖, 從哪句開始, 運鏡, 焦點)；運鏡 in / out / left / right / frame
SHOTS = [
    ("hero", None, "in", None),
]

# 短版：同一份旁白剪的片段（從哪幾個字, 到哪幾個字之前 / None）；16:9、9:16、1:1
CUTS = {
    # "30": dict(clips=[("...", "..."), ("...", None)], aspect="16:9"),
    # "15": dict(clips=[("...", "..."), ("...", None)], aspect="9:16", head=("(head)",)),
    # "15sq": dict(clips=[("...", "..."), ("...", None)], aspect="1:1", head=("(head)",)),
}
