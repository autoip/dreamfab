"""Style packs for the ad line: one look per market version. A pack is the project.py fields that make the look (the
renderer is explain/render.py) plus a theme for ad/cards.py, a narrator's manner and a Suno style for the music
(ad/new.py writes it into each version's suno.md). ad/new.py writes a pack into a new project.py, where it
can be changed freely; nothing reads the pack again after that except the cards.

usage: python ad/styles.py            list the packs
"""

PACKS = {
    "documentary": dict(
        label="紀錄片：深藍金色、底部柔光暗帶字幕、沉穩旁白",
        voice="calm, warm documentary narrator",
        music="instrumental, modern cinematic future bass meets city pop, soft piano, airy pads, hopeful, 108 BPM, "
              "steady energy, clean mix for voiceover",
        fields=dict(SUBS=dict(style="band", bold=True, size=60, size2=42)),
        theme="navy",
    ),
    "variety": dict(
        label="綜藝：亮色漸層、歪斜白框、黃字粗黑邊、貼紙字卡加音效、俏皮旁白",
        voice="bright, playful variety-show narrator who laughs as she talks",
        music="instrumental, variety show background music, playful funky pop, bouncy slap bass, brass stabs, "
              "handclaps, whistle and xylophone accents, cheerful and comedic, 120 BPM, light enough for voiceover",
        fields=dict(SUBS=dict(style="pop", bold=True, size=64, size2=40, fill2="&H00FFFFFF"),
                    CARD=dict(colors=("#ffe14d", "#ff7eb3", "#7ad7ff"), scale=0.74, tilt=-1.5, border=12, shadow=14, top=36),
                    LABELS=dict(chap=("&H00222222", "&H00FFFFFF"), title=("&H004DE1FF", "&H00222222"))),
        theme="variety",
    ),
    "keynote": dict(
        label="發表會：白底極簡、超大粗字、單一藍色、白框字幕、清爽專業旁白",
        voice="clear, confident product-launch presenter",
        music="instrumental, minimal modern electronic, clean plucks, soft sub bass, subtle claps, optimistic tech "
              "keynote mood, 112 BPM, spacious, sits under a voiceover",
        fields=dict(SUBS=dict(style="box", bold=True, size=52, size2=36, fill2="&H00666666"),
                    CARD=dict(colors=("#f4f6f9", "#eef2f8", "#f7f8fa"), scale=0.8, tilt=0, border=0, shadow=0, top=30),
                    LABELS=dict(chap=("&H00FF6631", "&H00FFFFFF"), title=("&H00111111", "&H00FFFFFF"))),
        theme="keynote",
    ),
    "cinematic": dict(
        label="電影感：寬銀幕黑邊、暖色調、暗角、細字幕、溫柔旁白",
        voice="soft, intimate film narrator",
        music="instrumental, emotional film score, felt piano, warm strings, slow build, tender and hopeful, 80 BPM, "
              "leaves room for a voiceover",
        fields=dict(SUBS=dict(style="outline", size=46, size2=32, margin=16),   # inside the bottom bar
                    FILM=dict(bars=130, warm=0.08, vignette=0.35),
                    LABELS=dict(chap=("&H00C3E3F3", "&H60000000"), title=("&H00C3E3F3", "&H60000000"))),
        theme="cinematic",
    ),
}

if __name__ == "__main__":
    for k, p in PACKS.items():
        print(f"{k:12s} {p['label']}")
