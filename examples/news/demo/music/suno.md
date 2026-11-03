# 美股一分鐘：新聞主題曲（貼進 Suno）

每天沿用同一首：片頭 3 秒的提示音，接著墊旁白的配樂，片尾收一個短音。

**Title**
Morning Market Brief

**Style of Music**
instrumental financial news theme, modern broadcast, 120 bpm, ticking clock pulse, tight synth bass, bright piano stabs, clean electronic drums, confident and urgent but not dramatic, short punchy intro sting, steady low-key bed for voice-over, crisp ending hit

**Exclude styles**
vocals, singing, choir, lyrics, spoken word, rap, heavy guitar, epic orchestra, lo-fi

**Lyrics**（選 Instrumental，或貼下面這段段落標記）
```
[Intro]
[Instrumental]
[Break]
[Outro]
```

**長度**：Suno 生出來的長度都可以。量出可以重複的整小節寫進 series.py 的 `MUSIC_LOOP`，`news/make.py render` 會接到片長：前奏、重複的小節、收尾。

生好之後把檔案放到 `music/`，檔名寫進 series.py 的 `MUSIC`。
