# 廣・廣告 `ad/`

把實體商品、服務、品牌做成廣告，**一次出多個市場版本**，每個語言換一種包裝（紀錄片、綜藝、發表會、電影感）。每個版本都有主版和短版：

- 主版約 1–2 分鐘
- 30 秒、15 秒
- 16:9、9:16、1:1 三種尺寸
- 每支都附兩個字幕檔：當地語言和中文

成品只交檔案，不上架。

合成用解說線的程式（[explain/](../explain/OVERVIEW.md) 的 `render.py`），廣告線另外提供這些工具：
- 開案：`ad/new.py`
- 風格包：`ad/styles.py`
- 卡片：`ad/cards.py`
- 官網截圖：`ad/capture.py`
- 整個活動的合成和交件清單：`ad/render.py`

中文 | [English](../../en/ad/OVERVIEW.md)

## 一個廣告活動的資料夾

```
projects/<品牌>/<活動>/
  brief.md                    簡報：一起填完才寫文案；交件前逐條查核
  voices/raw/ voices/NARR_JA.wav ...   每個語言一位旁白（文生影片開口取聲音）
  fonts/                      沒有安裝的字幕字型放這裡
  ja_documentary/             一個市場版本＝一個資料夾（語言_風格包）
    project.py  script.md  images/  voice/  jobs/
    out/<NAME>.mp4            主版（16:9）＋ .ja.srt、.zh-TW.srt
    out/<NAME>_30.mp4         短版（CUTS 的每一項各一支）
    out/<NAME>_15.mp4  out/<NAME>_15sq.mp4
  ko_variety/  en_keynote/ ...
  delivery.md                 交件清單：每支的尺寸、長度、響度、字幕檔
```

範例：[examples/ad/demo](../../../examples/ad/demo/)。

## 三種廣告

| 類型 | 適合 | 預設卡片（`ad/new.py --kind`） |
|---|---|---|
| `product` 實體商品 | 拿得到的東西：飲料、保養品、家電 | 主視覺、三個特點、價格與購買、片尾 |
| `service` 服務 | App、平台、店家、課程 | 主視覺（官網截圖）、使用流程、特點、片尾 |
| `brand` 品牌 | 一種感覺、一個承諾 | 品牌承諾、顧客的一句話、生活片段牆、片尾 |

## 風格包

每個市場一種包裝，不照搬上一個語言的樣子。`python ad/styles.py` 列出全部：

| 風格包 | 樣子 | 旁白 | 配樂建議 |
|---|---|---|---|
| `documentary` 紀錄片 | 深藍金色、底部柔光暗帶字幕 | 沉穩溫暖 | 電影感 future bass、鋼琴 |
| `variety` 綜藝 | 亮色漸層、歪斜白框、黃字粗黑邊、貼紙字卡加音效 | 活潑、帶笑 | 輕快 funk、銅管、拍手 |
| `keynote` 發表會 | 白底極簡、超大粗字、藍色重點、白框字幕 | 清爽專業 | 極簡電子 |
| `cinematic` 電影感 | 寬銀幕黑邊、暖色調、暗角、細字幕 | 輕柔 | 鋼琴、弦樂 |

風格包只是 `project.py` 的起始值，開案時寫進去，之後可以自由改。

## 步驟

每一批要花點數的任務，送出前都先報「原價／離峰」兩種價，等使用者點頭。

1. **開案和簡報**：
   ```bash
   python ad/new.py projects/<品牌>/<活動> --kind product --langs ja:documentary,ko:variety,en:keynote
   ```
   會寫出 `brief.md` 和每個市場的資料夾。和使用者一起填 `brief.md`：給誰看、三個重點、證據、要對方做什麼、長度、不能說的話。
2. **風格樣張**：每個市場先拿同一張畫面做 2–3 種包裝給使用者挑（在本機畫，不花點數），選好的寫進 `STYLE` 和對應欄位。
3. **文案** `script.md`：用那個語言寫，每一行底下加 `> 中文`。一行＝一句字幕（一列放得下）。前 3 秒就要有鉤子。每一句都要對得回簡報的證據：配樂是誰做的、數字、免費與否，都不能說錯。
4. **旁白**：每個語言用文生影片做一位新的旁白開口說一句，切 5–15 秒當 `VOICE`。語氣照風格包，例如綜藝要活潑、發表會要清爽。接著跑：
   ```bash
   python explain/narration.py P jobs && python dreamfab/aip_runner.py P/jobs/voice_jobs.json
   python explain/narration.py P check
   ```
   語音 v3（`voxcpm2`）照文字的語言唸。
5. **畫面**（解說線的 `SHOTS`）：
   - **現有作品**：`CLIPS` 放影片片段，`SHOTS` 寫 `"代號:秒"`。
   - **產品畫面**：文生圖 v4 拍產品照，或用圖生影片讓它動起來。
   - **官網截圖**：`python ad/capture.py URL images/site_ja.png --lang ja --hide-corner`。白底網頁在 `SHOTS` 用 `frame`，字幕才看得清楚。
   - **卡片**：`python ad/cards.py P`，把 `CARDS` 畫成 `images/<id>.png`。
6. **配樂：建議用 Suno**。Suno 目前沒有開放一般使用者用 API，所以由 agent 寫、使用者貼：
   - **agent 寫 `suno.md`**（開案時每個版本都有一份草稿）：歌名、Style of Music（從風格包的建議改寫成這支廣告的情緒）、Exclude styles、長度。墊在旁白底下的配樂開 Instrumental；想唱出品牌名，就另外寫 jingle 歌詞（`[Intro]`、`[Hook]`、`[Outro]` 段落標記，用那個市場的語言唱，品牌名、口號、網址照簡報）。
   - **使用者貼進 Suno**（Custom 模式）生成，挑一首下載，放進 `music/`，檔名寫進 `MUSIC`。
   - 片中不能說這支的配樂是 AutoIP 做的。
   - **想全自動、不經 Suno**：用 AutoIP 作曲 `/voice/song`（30 點），片中就可以說「配樂也是 AutoIP 做的」。長曲子偶爾只回幾秒（遇過要 150 秒只回 2.6 秒、6.5 秒），回來先量長度。
   - 沒寫 `CH_MUSIC` 時，配樂從頭一路放到尾；曲子太短就在拍點上把中間段落重複接長。
7. **合成**（不花點數）：
   ```bash
   python ad/render.py projects/<品牌>/<活動>           # 每個市場：主版、CUTS 每一支，再寫 delivery.md
   python explain/render.py P --cut 30                   # 只出一支短版
   ```
   `CUTS = {"30": dict(clips=[("從哪幾個字", "到哪幾個字之前"), ...], aspect="16:9"), "15": dict(..., aspect="9:16", head=("上方標題",))}`：
   - `16:9`：跟主版同一個樣子。
   - `9:16`、`1:1`：畫面放在中間，字幕從畫面下方往下排。
8. **查核和交件**：照 `brief.md` 的查核逐條打勾，把旁白聽寫的疑點清單給使用者聽。`delivery.md` 列出每一支的尺寸、長度、響度（−14 到 −16 LUFS）和字幕檔。資源庫 `python dreamfab/library.py serve projects` 首頁有「廣」這條線，每個市場一張卡片。

## project.py（廣告線多出來的欄位）

| 欄位 | 意思 |
|---|---|
| `LINE = "ad"` | 資源庫把它算在廣告線 |
| `STYLE` | 風格包名稱（`ad/styles.py`）；卡片的配色跟著它 |
| `CARDS` | 卡片：`[dict(id=, kind=, ...)]`，見下面 |
| `CARD_FONTS` | 卡片的字型：`dict(head=, body=, zh=, web=["Google Fonts 家族"])` |
| `CUTS` | 短版：片段、尺寸、上方標題 |
| `GAPS` | 開案預設比解說緊湊：片頭 0.8、章節間 0.6、片名 2.2、片尾 3.5 秒 |
| `CHAPTER_LABELS = False` | 不在畫面上放章名（開案預設；30 秒的廣告不需要） |
| `FILM` | 電影感：`dict(bars=130, warm=0.08, vignette=0.35)` 寬銀幕黑邊（只在 16:9）、暖色、暗角 |

其餘照解說線：`SCRIPT`、`VOICE`、`NARRATION`、`SHOTS`、`CLIPS`、`SUBS`、`CARD`、`STICKERS`、`LABELS`、`MUSIC`……（[解說線的 project.py](../explain/OVERVIEW.md#projectpy)）。

## 卡片種類（`ad/cards.py`）

字都排在 y 760 以上，字幕不會壓到。每張都能帶 `zh="中文"`。

| `kind` | 欄位 | 畫成 |
|---|---|---|
| `hero` | `title`、`sub`、`image`、`tag` | 大標題和產品照或截圖 |
| `features` | `title`、`items=[(標題, 一句, 中文)]` | 三、四個並排的特點 |
| `steps` | `title`、`sub`、`steps=[(字, 中文)]`、`note` | 有編號和箭頭的流程 |
| `prompt` | `lines=[(me/ok/q/zh, 字)]` | 終端機視窗：一句要求和 agent 的回覆 |
| `wall` | `title`、`files=[路徑或萬用字元]`、`cols`、`ratio` | 封面、縮圖牆 |
| `quote` | `text`、`who` | 顧客的一句話 |
| `offer` | `title`、`price`、`note`、`cta` | 價格和行動呼籲 |
| `end` | `brands=[(名稱, 網址, 中文)]`、`line` | 片尾 |

## 學到的事

- **每個語言換一種風格**：同一支片翻成另一個語言，觀眾不會覺得是為他們做的。換包裝、換口吻（例如韓語版改成綜藝吐槽），比只換字幕有效。
- **說法要對得回事實**：配樂如果是 Suno 做的，就不能說「這支的配樂也是 AutoIP 做的」；只能講 AutoIP 作曲能做什麼。
- **配樂建議用 Suno**：Suno 沒有開放一般使用者用 API，agent 寫好 `suno.md`（曲風、歌詞），使用者貼進去生成。AutoIP 作曲可以全自動，但要先量回來的長度。
- **官網截圖要用對語言**：網站的 `/locale/ja` 連結通常只寫 cookie，無頭瀏覽器帶不過去；改用 `--lang ja` 讓瀏覽器自己說日文。右下角的 reCAPTCHA 標誌用 `--hide-corner` 蓋掉。
- **白底網頁放金框**：鋪滿畫面的白底網頁，白字幕會看不清楚，放進框裡讓字幕落在暗處。
- **字型**：字幕的字型要安裝在電腦上（libass 不能用網頁字型）；卡片是網頁，可以直接用 Google Fonts。韓文斷行要斷在空格，日文、中文斷在逗號。
- **錯開兩句字幕**：前後兩句只要重疊一點點，libass 就會把後一句往上推一整行，廣告的字幕位置會亂跳。合成程式已經讓每句在下一句開始前結束。
