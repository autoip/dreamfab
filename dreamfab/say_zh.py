"""錯音表: Chinese words a voice clone misreads, and what to send it instead. Free to copy.

Each pair is (written, said): the subtitles keep the written words and the voice reads the said ones. Both sides have
the same length, so subtitle timing still maps character to character, and sound the same in Mandarin: the said side
is only characters the voice gets right. A show reads it in its project.py (explainers, deep reports) or series.py
(news), and keeps fixes for one line of one episode to itself:

    from dreamfab.say_zh import SAY
    SAY = SAY + [("範圍，最快", "範圍。最快")]

Dreamfab's own news shows (the daily brief and the deep reports) read this table, so a new misread goes in here once
and both get it. Pairs come from narration.py / news/make.py check, kept when two recognisers heard the same misread
or the user heard it. Found with one voice (a Taiwanese-accented anchor on AutoIP's default engine): another voice may
need fewer or other pairs. AutoIP turns traditional characters into simplified ones before its voice reads them (since
2026-11-06), so the table keeps only what the script does not explain; a service that reads traditional as it is may
want the dropped pairs back, or the text sent in simplified. Why and how: docs/zh-TW/PRONUNCIATION.md
(docs/en/PRONUNCIATION.md).
"""
SAY = [
    # polyphones: the voice picks the other reading
    ("供給", "供擠"), ("重啟", "崇啟"), ("金鑰", "金要"), ("門檻", "門砍"), ("乾脆", "甘脆"),
    # rarer characters, read as a look-alike or a guess
    ("銦", "因"), ("渦輪", "窩輪"), ("駭客", "害客"), ("反駁", "反伯"), ("帳上", "丈上"), ("釣魚", "吊魚"),
    ("外洩", "外謝"), ("飆漲", "標漲"),
    # common words the voice still gets wrong (heard as: 情報 新房, 攻擊 中擊, 資料 私料, 布蘭特 波蘭特)
    ("光纖", "光仙"), ("叢集", "從集"), ("情報", "晴報"), ("攻擊", "公擊"), ("註冊", "註策"), ("機關", "基關"),
    ("資料", "姿料"), ("布蘭特", "步蘭特"),
    # gone since 2026-11-06, when AutoIP began reading Chinese as simplified (character by character): 廣告, 報告,
    # 下載, 學習, 推薦, 獎勵, 蒐集, 訴訟, 贊助 were misread because they were written in traditional characters
    # chosen by the user's ear
    ("瓶頸", "瓶錦"), ("企業", "啟夜"), ("併購", "病夠"), ("黃仁勳", "皇仁薰"), ("槓桿擴張", "幹港闊章"),
    # numbers and symbols: 〇 is read as 圈 or 老; a web address shown on screen is read out in words (9 characters each)
    ("〇", "零"), ("autoip.ai", "AutoIP點AI"),
]
