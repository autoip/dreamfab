# kumo_oolong：en 版（keynote：發表會：白底極簡、超大粗字、單一藍色、白框字幕、清爽專業旁白）
# 廣告線 ad/：explain/render.py 合成、ad/cards.py 畫卡片；簡報在 ../brief.md。示範用的虛構商品。
# An ad line example (a made-up product): ad/new.py wrote this file, then every "(...)" was filled in.
LINE = "ad"
NAME = "kumo_oolong_en"
RENDER = {"lang": "en", "lang2": "zh-TW"}   # English narration and captions, Chinese under each line
SCRIPT = "script.md"
STYLE = "keynote"                          # ad/styles.py; the Japanese version is "variety"
# 旁白：文生影片做一位新的旁白開口（../voices/raw/NARR_EN.mp4），切 5-15 s 當樣本 ../voices/NARR_EN.wav
VOICE = "../voices/NARR_EN.wav"
VOICE_FIELDS = dict(voice_engine="voxcpm2", style="clear, confident product-launch presenter")
SAY = []

TITLE = ("Kumo Oolong", "Cold tea. Warm mountains.")
ENDCARD = ""
FONT = ("Arial", "../fonts")   # titles and labels: an installed font (libass cannot use web fonts)
SUBS = {'style': 'box', 'bold': True, 'size': 52, 'size2': 36, 'fill2': '&H00666666', 'font': 'Arial', 'font2': 'Microsoft JhengHei'}
CARD = {'colors': ('#f4f6f9', '#eef2f8', '#f7f8fa'), 'scale': 0.8, 'tilt': 0, 'border': 0, 'shadow': 0, 'top': 30}
LABELS = {'chap': ('&H00FF6631', '&H00FFFFFF'), 'title': ('&H00111111', '&H00FFFFFF')}
CARD_FONTS = dict(head="Montserrat", body="Arial", zh="Microsoft JhengHei", web=["Montserrat:wght@700;900"])
STICKER_FONT = "Arial"

# 配樂：給使用者去 Suno 生成的曲風（放 ../music/kumo_keynote.mp3）
# instrumental, minimal modern electronic, clean plucks, soft sub bass, subtle claps, optimistic, 112 BPM, spacious
MUSIC = "../music/kumo_keynote.mp3"
MUSIC_DB = -26

# 產品照：文生圖 v4（MOSS-Image：一段英文散文；罐子上要出現的字用引號寫出來）。explain/make_images.py 送出
LOOKS = {"P": "Clean studio product photography, soft daylight from the left, gentle reflections, a pale grey seamless "
              "background, sharp focus, in a wide 16:9 frame."}
NEG = "extra text, misspelled letters, logos of real brands, watermark, people, hands"
IMAGES = [
    ("product", "Points", "罐子特寫", "A slim matte silver drink can standing on a wet slate stone, the word \"KUMO OOLONG\" "
     "printed vertically in deep green, cold droplets on the can, a wisp of mountain mist curling around its base.", "P"),
    ("leaves", "Points", "茶園", "Rows of tea bushes on a steep green mountainside above a sea of clouds at sunrise, "
     "two thousand meters high, dew on the leaves in the foreground.", "P"),
]

# 卡片（ad/cards.py）：畫成 images/<id>.png，SHOTS 直接用 id
CARDS = [
    dict(id="hero", kind="hero", title="Cold tea.\nWarm mountains.", sub="Kumo Oolong, from Taiwan's high mountains",
         image="images/product.png", tag="NEW", zh="冰的茶，暖的山"),
    dict(id="features", kind="features", title="Why Kumo", zh="為什麼是雲茶",
         items=[("2,000 m", "Leaves from Taiwan's high mountains", "兩千公尺高山茶葉"),
                ("12 hours", "Roasted slowly, by hand", "慢焙十二小時"),
                ("0 sugar", "Nothing added. Just tea.", "完全無糖")]),
    dict(id="end", kind="end", brands=[("Kumo Oolong", "kumo-tea.example", "雲茶烏龍")], line="Cold tea. Warm mountains."),
]

CLIPS = {}   # the brand's own footage, if any: "key:second" in SHOTS

# (圖, 從哪句開始, 運鏡, 焦點)；運鏡 in / out / left / right / frame
SHOTS = [
    ("hero", None, "in", None),
    ("leaves", "Kumo Oolong grows", "right", None),
    ("features", "We roast it slowly", "in", (0.5, 0.45)),
    ("product", "Open a can", "in", (0.5, 0.55)),
    ("end", "Kumo Oolong. Find it", "in", None),
]

# 短版：同一份旁白剪的片段（從哪幾個字, 到哪幾個字之前 / None）
CUTS = {
    "15": dict(clips=[("Cold tea.", "Kumo Oolong grows"), ("And add no sugar", "Open a can"), ("Kumo Oolong. Find it", None)],
               aspect="9:16", head=("Kumo Oolong",)),
    "15sq": dict(clips=[("Cold tea.", "Kumo Oolong grows"), ("And add no sugar", "Open a can"), ("Kumo Oolong. Find it", None)],
                 aspect="1:1", head=("Kumo Oolong",)),
}
