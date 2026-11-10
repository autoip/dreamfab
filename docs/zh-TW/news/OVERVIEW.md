# 聞・新聞 `news/`

兩種節目，同一個頻道、同一位 AI 主播：
- **每日快報**：直式（1080x1920），約 1 分鐘，見下面各節。
- **深度報導**：16:9 長片，3–6 分鐘，見[最後一節](#深度報導36-分鐘-169-長片)。

每日快報：
- AI 主播開場、結尾露臉對嘴，中間用字卡講數字。
- 字幕和片頭主題曲從頭到尾都有。

第一個節目是「美股一分鐘」：台股開盤前，一分鐘看懂昨晚美股。

**上架**：
- 節目設定裡沒有頻道時只出檔案。
- 設了頻道（`CHANNEL`）就由 `upload` 上架；公不公開看 `PRIVACY`。
- 也可以交給系統排程，每天無人值守做完、上架（見最後一節）。

中文 | [English](../../en/news/OVERVIEW.md)

## 一個節目的資料夾

```
projects/<節目>/
  series.py                   節目設定：檔名、標題條、主播、聲音、主題曲、開場和結尾的固定台詞、片尾贊助卡
  cast/ANCHOR_A.png           主播定裝照（9:16，對嘴用）
  voices/ANCHOR_A.wav         主播的聲音樣本
  music/                      主題曲（建議 Suno，見下面）
  timing.tsv                  每一步花了幾分鐘（每個指令自己寫）
  2026-11-03/                 一天一個資料夾
    script.md                 每行「唸的｜字幕｜畫面」
    day.py                    DATE、SOURCES、CARDS（每張字卡的 HTML）
    cards/ voice/ clips/ jobs/
    out/<NAME>_20261103.mp4   成品＋ .zh-TW.srt
```

範例：[examples/news/demo](../../../examples/news/demo/)。

## 開一個節目（一次）

1. **主播**：先用 v4 文生圖做定裝照（`size` 540x960，半身、主播台、背景不要有字和 logo），再用圖生影片 480p 8 秒讓她說一句開場白，取出人聲當聲音樣本。
   - 圖生影片有時會把提示詞裡的語氣描述也唸出來，所以只截乾淨的那一段。
   - 11/03 試播：她先唸了「穩定、語速適中」，聲音樣本只取 3.1 秒之後。
2. **主題曲**：照廣告線的做法，agent 寫好 Suno 用的曲風（`music/suno.md`），使用者貼進 Suno 生成。
   - 量出可以重複的整小節，寫進 `MUSIC_LOOP`，`render` 會把它接到片長。
3. **series.py**：照 [範例](../../../examples/news/demo/series.py) 填。

## 每天的流程

### 1. 查新聞：先查英文媒體
美股收盤後 15 分鐘內，英文媒體就有收盤稿。中文報導要晚一到兩個小時，還常漏掉盤後財報、油價結算價和經濟數據。

11/03 試播實測：先查英文媒體，多找到三則中文報導都沒寫的消息：
- Palantir 盤後財報
- 布蘭特和西德州原油的結算價
- ISM 製造業指數

| 要什麼 | 先查 |
|---|---|
| 收盤指數 | CNBC 當天 live blog 的收盤那則；AP〈How major US stock indexes fared〉；Reuters |
| 漲跌最大的股票和原因 | CNBC、Reuters、MarketWatch、TheStreet |
| 盤後財報 | 公司新聞稿（BusinessWire、SEC 8-K）、CNBC |
| 油價 | Reuters／AP 的收盤稿（settle） |
| 經濟數據 | 官方發布：ISM、BLS、Fed |
| 台灣的資料 | 台指期夜盤（期交所或 MoneyDJ 的盤後收盤價）、加權指數、台積電 ADR，這些才查中文媒體 |

- **每個數字都要兩個來源對得上**：對不上就查報價頁的歷史收盤。11/03 有一個英文來源把英特爾寫成 −5.19%，實際是 −8.80%。
- **不寫建議**：只報發生了什麼，不寫買賣建議。法律紅線和出片前清單在 [COMPLIANCE.md](COMPLIANCE.md)：每一集研究寫完過一次、合成前再過一次。

### 2. 寫腳本
- `python news/make.py new projects/<節目> 2026-11-04`：開新的一天。
  - `day.py` 從前一天複製過來，日期自動換好。
  - `script.md` 已經放好固定的第一句和最後一句。
- **長度**：每行一句；約 11 句、280 字，就是 1 分鐘左右（實測每秒 5.2 字）。
- **唸的那欄**：
  - 數字寫國字，例如「百分之零點四」。
  - 美國指數和公司名直接唸英文：Dow Jones、Oracle、Intel、Apple、Palantir…
  - 台灣公司唸中文：台積電、聯電。
  - 唸錯的字放進 `series.py` 的 `SAY`：同樣長度的同音字，只改唸的、不改字幕，送旁白前自動換。例如光纖→光仙、供給→供擠、叢集→從集、瓶頸→瓶錦、重啟→崇啟。`check` 抓到新的唸錯字，就加進去（[AI 唸錯字怎麼辦：錯音表](../PRONUNCIATION.md)）。
- **字幕那欄**：數字用阿拉伯數字，名字寫中文（道瓊、甲骨文、英特爾…）。
- **畫面那欄**：寫 `anchor`（主播）或字卡 id。連續幾行用同一張卡，畫面就不換。
- **字卡**：在 `day.py` 用 `row()`（指數、股價）、`bar()`（跌幅長條）、`box()`（重點框）組。
  - 漲紅跌綠（台灣習慣）。
  - 公司只放文字和數字，不放 logo，也不放真人照片。
- **片尾**：一定要列資料來源，並標明「主播與聲音為 AI 生成｜本頻道非證券投資顧問事業，內容為新聞整理與公開資料，不構成投資建議」（11/06 起加非投顧警語，見 [COMPLIANCE.md](COMPLIANCE.md)）。

### 3. 生成
```
python news/make.py cards  DAY
python news/make.py hero   DAY                       # 選用：day.py 的 COVER_HERO → 封面主圖
python news/make.py submit DAY hero --off-peak       # v4 一張 20 點（離峰 10 點），約半分鐘
python news/make.py cover  DAY
python news/make.py voice  DAY
python news/make.py submit DAY voice --off-peak      # 旁白
python news/make.py check  DAY                       # 逐字稿；列出聽起來不一樣的字
python news/make.py anchor DAY                       # 只取主播露臉的兩段
python news/make.py submit DAY lipsync --off-peak    # 對嘴
python news/make.py render DAY
```
- **封面用當天的主圖**：`COVER_HERO` 把當天最大的那則新聞寫成一張圖（英文散文；漲用紅色光、跌用綠色光；不要字、logo、真人、旗子；主體放中間，上面三分之一留暗給標題）。有 `images/cover_hero.png` 時封面就用它，不再放主播；主體被下面的資訊框擋住，就在 `COVER` 加 `shift=40` 之類把圖往上移。
- **旁白最後多唸一句「謝謝收看」**：語音服務會把最後一點聲音截掉，最後一個字常常只剩一半。多唸的這句被截掉也沒關係：第一次 `check`（或對時）時在它前面的停頓切掉，原檔留成 `voice/narr_raw.flac`。重唸的 `redo.flac` 也一樣。
- **對嘴只送主播露臉的兩段**（開場、結尾，合計約 8 秒）：比整段送快三倍，點數一樣。
  - 對嘴影片常少最後半秒，所以送出的音檔尾巴補 0.6 秒靜音。
  - 片尾在影片用完的地方接上全螢幕贊助卡。
  - **合成前先看主播胸前有沒有字**：對嘴服務有時會在主播胸前、手的上面燒進一行亂碼字幕（不成字的英文或中文），任務照樣回報成功。重送對嘴多半還是有字，提示詞寫「不要字」也擋不住。這時改送去字幕（AutoIP 影片修復，每 8 秒 30 點，離峰半價），臉、嘴型、長度都不動：
    ```
    python news/make.py desub  DAY                   # 有字的那支改名 clips/anchor_ng.mp4，寫 jobs/desub.json
    python news/make.py submit DAY desub --off-peak  # 去好字的放回 clips/anchor.mp4，看過再 render
    ```
- **某幾句唸錯**：只重唸那幾句，接回原本的旁白。
  ```
  python news/make.py redo   DAY 4 9               # 重唸第 4–9 句（第一句是 1）
  python news/make.py submit DAY redo
  python news/make.py splice DAY 4 9               # 在停頓處接回，停頓至少 0.3 秒
  ```
  - 主播的兩段沒有變，就不用重做對嘴。
  - 舊的旁白留在 `voice/narr_prev.flac`。
  - 新的一段只有幾個字不好時，可以手動混用新舊兩段。

### 4. 封面和 SEO：同一個鉤子
```
python news/make.py cover DAY        # out/<NAME>_cover.jpg
python news/make.py seo   DAY        # out/<NAME>_SEO.txt
```
- **封面**（`day.py` 的 `COVER`）：
  - 主播照片往下移，臉保持在畫面正中間，不被字蓋到。
  - 最上面是黃底大字日期（`DATE` 轉成「11/3 週二」，或自己寫 `COVER_DATE`）：每天一集，縮到手機上的小圖也要看得到是哪一天。
  - 上傳的縮圖現在頻道的 Shorts 分頁也會顯示（2026-11 用 API 換過縮圖，分頁跟著換）。滑 Shorts 時看到的還是影片本身，所以仍要搭配 `COVER_FRAME`，讓第一個畫面就是封面，並且先做 `cover` 再 `render`。
  - 上方放兩行大字鉤子：第一行是最大的數字（漲紅跌綠），第二行是問句。
  - 下方一行放第二、第三則重點。
- **SEO**（`day.py` 的 `SEO`）：
  - 標題 A、B、C 都用鉤子開頭：數字加反差或問句，例如「Palantir 營收年增 96%，盤後還是跌？」。最後加上節目名和日期。
  - 說明欄依序是：導言、每則新聞一行（取自字幕）、資料來源、AI 與投資聲明、贊助、標籤。
  - 格式跟其他線的 `YouTube_SEO.txt` 一樣。試播期不發布，只出檔案。

### 5. 結尾催訂閱
`series.py` 的 `CTA_LINE` 是主播最後說的那句，例如「記得訂閱，每天開盤前看美股一分鐘，養成習慣！」：
- `new` 會自動把它放在最後一行。
- 說到這句時，標題條換成 `CTA`。
- 片尾卡先放訂閱按鈕和 `SUBSCRIBE` 的那句話，贊助放在下面。
- SEO 說明欄的訂閱那行寫在 `SEO_FOOT`。

### 6. 交件、上架
成品是 `out/<NAME>_<YYYYMMDD>.mp4`、`.zh-TW.srt`、`_cover.jpg`、`_SEO.txt`。
```
python news/make.py upload DAY            # 公不公開看 series.py 的 PRIVACY（沒寫就是私人）；--public / --private 可以蓋過
```
- 上傳到 `series.py` 的 `CHANNEL`，用它自己的登入（`YT_TOKEN`，見 [SETUP](../SETUP.md)），不會傳錯頻道。
- 用標題 A、說明欄、標籤、字幕和封面；`CATEGORY` 預設 25（新聞與政治）。
- 照樣遵守每個頻道每天的上限（`youtube.daily_max`）。`out/youtube.json` 記下影片 id，重跑不會傳兩次。
- **封面**：頻道要先完成驗證，才能用自訂縮圖；沒驗證時會跳過，並提示原因。Shorts 架上的縮圖由 YouTube 自己挑畫面，所以設 `COVER_FRAME = 0.3`，讓片頭前 0.3 秒就是封面，那段時間不放字幕。

## 速度和點數（11/03 試播實測）

| 步驟 | 分鐘 |
|---|---|
| 查新聞（英文媒體，查詢一起送） | 1 |
| 寫腳本、字卡 | 約 10 |
| 旁白（約 300 字） | 2.3 |
| 對嘴（主播露臉約 8 秒） | 0.9 |
| 畫字卡＋合成 | 1.8 |
| **合計** | **約 15** |

- **點數**：每天旁白 50、對嘴 50；離峰 03:00–09:00（台灣時間）送是半價，一共 50 點。
  - 第一次開節目另外要主播定裝照（v4 20 點）和試音（圖生影片 480p 8 秒，48 點）。
- **時間**：美股收盤是台灣 05:00（冬令時間；夏令時間 04:00），台指期夜盤也是 05:00 收。
  - 05:15 以後就能開工。美股一分鐘排 06:30，約 16 分鐘出片，還在離峰半價，台股開盤前也有時間重做。

## 無人值守：每天自動做完、上架
在 `series.py` 寫好時間，排進系統排程一次，之後每天沒人在旁邊也會做完、上架：
```python
DAILY = dict(at="06:30", days="mon-fri", latest="08:30")   # 幾點、哪幾天（電腦的本地時間）、幾點以後就不做
```
```
python news/make.py schedule SHOW --dry-run   # 先看會排什麼，不動系統
python news/make.py schedule SHOW             # 排進去：Windows 工作排程器；macOS、Linux 用 cron
python news/make.py schedule SHOW --remove    # 取消
python news/make.py daily SHOW --test         # 只確認 Claude Code 叫得起來，不花點數
python news/make.py daily SHOW                # 排程每天叫的就是這個；手動跑也可以
```
特色：
- **從查新聞到上架一次做完**：`daily` 叫 Claude Code（`claude -p`）照每日指示跑完上面第 1 到第 6 步：查新聞、寫稿、字卡、封面、SEO、旁白、檢查、對嘴、合成、上傳。
- **每日指示是一個檔案**：預設 [news/daily_prompt.md](../../../news/daily_prompt.md)，節目也可以用自己的（`DAILY` 的 `prompt`）；`{DATE}`、`{SHOW}`、`{PY}` 自動帶入。
  - 裡面寫清楚使用者排程時同意了什麼：每天的任務點數、照 `PRIVACY` 上架。也寫清楚不能做什麼：不碰別的專案、不 commit、不讀金鑰。
  - agent 不會停下來問問題。
- **權限收窄**：只開指令列、檔案讀寫、搜尋和網頁（`DAILY` 的 `tools` 可以改），一次只送一個任務（`AIP_MAX=1`），任務都在離峰送（半價）。
- **唸錯自己修一次**：`check` 抓到唸錯的字，就換成同音、常見的字加進 `SAY`，重唸那幾句再接回。
  - 不為省點數不修，但只修一次，不會一直循環；修完還不對的寫進 log 請人聽。
  - 英文名被辨識成別的字不算錯。旁白結尾被截掉（多唸的那句之前就沒了），也用同樣方法補唸最後一句。
- **錯過時間會補跑，太晚就跳過**：電腦睡著錯過時間，Windows 開機後會補跑；但超過 `latest` 才開始就跳過，並記一行，避免離峰結束後用原價做出過時的新聞。
- **換主播**：`series.py` 的 `ROTA` 依星期或日期換主播（例如 `{"fri": dict(ANCHOR=..., VOICE=...)}`，日期優先），排程照常跑。
- **沒新聞就不做**：休市日只記一行原因。`days` 排到哪一天，就看那天有沒有新聞：排 `mon-fri`，週一做的是上週五的收盤；排 `mon-sat`（美股一分鐘 2026-11 起），週六做美東週五的收盤，週一改做「週末消息整理」（開頭那句用 `ROTA` 的 `"mon"` 換掉，`new` 會寫進稿子），週日休息。
- **不重複、守上限**：`out/youtube.json` 記下影片 id，重跑不會傳兩次；照樣遵守每個頻道每天的上限。
- **出錯就停**：失敗的步驟重試一次，再失敗就停下來，寫下停在哪一步、錯誤訊息；不上傳半成品。
- **留紀錄**：Claude 的完整輸出在節目資料夾的 `logs/日期.log`；`daily_log.md` 每天一段：網址、片長、點數、每步分鐘數、換了哪些字、請人聽的地方。

## 深度報導：3–6 分鐘 16:9 長片
同一個頻道、同一位主播，把一則新聞講透，例如〈Lumentum 為什麼紅？光，為什麼是 AI 的命脈〉（3 分 47 秒、9 章）。

- **研究**：
  - 先查一手資料：SEC 8-K 和 10-K、公司新聞稿、財報電話會議。再用英文媒體交叉核對，每個數字都要兩個來源對得上。
  - 各家說法不一的事情不說，例如某家公司是不是某客戶的主要供應商。
  - 台股相關的公司只寫「法人點名」，並註明不構成投資建議。
  - 文案寫完先過 [COMPLIANCE.md](COMPLIANCE.md) 的清單：多空論點都引述、標出處；「後市」只列要看的訊號，不下看好看壞；估值不自己說貴或便宜；爭議寫「誰指控、公司怎麼回應、現在結果」。合成前再過一次。
- **格式**：用解說線（[explain/](../explain/OVERVIEW.md)）。
  - `script.md` 的 `## 旁白` 底下一章一個 `###`。唸的就是字幕，所以數字寫國字。
  - 唸錯的字用 `SAY` 換同音字，例如 `("光纖", "光仙")`。
  - `explain/render.py` 負責合成：章名、片名、資料來源卡（`FACTS`）、片尾。
- **主播**：
  - 只把開場和結尾那兩段旁白切出來送對嘴，每段 31 秒以內，尾巴補 0.6 秒靜音。
  - 再排成左邊標題、右邊主播的 16:9 畫面，放進 `CLIPS`。
  - 開場那支前面定格 `GAPS` 的 lead 那麼久，嘴型才對得上。
- **畫面**：
  - 中間用 v4 文生圖（16:9，不要有字和 logo）。
  - 數字用 HTML 畫的資料圖卡（營收長條圖、股價、收購條件、供應鏈），只放兩個來源對過的數字。
- **配樂**：Suno 一次會給兩個版本。兩首接在一起（交叉淡化）就夠一集用，下一集換成另一首在前。
- **封面**：16:9。「深度報導」標籤和日期、兩三行鉤子、主播露臉。
- **SEO**：標題用鉤子開頭；說明欄放章節時間（從 0:00 開始，每章 10 秒以上）、重點數字、資料來源、AI 與投資聲明。
- **上架**：節目資料夾寫 `series.py`（`CHANNEL`、`YT_TOKEN`、`PRIVACY`），單集資料夾的 `day.py` 寫 `FILE`，就能用 `news/make.py upload`。
  - 深度報導不趕時效，建議 `PRIVACY = "private"`：先私人上傳，看過再公開。
  - 集數放在標題最前面：`TITLE_PREFIX = "EP{ep}｜"`，`{ep}` 取單集資料夾的編號（`e05_…` 就是 `EP5｜`）；SEO 檔的標題已經有就不重複加。
  - 每日節目把日期放在標題最前面：`TITLE_PREFIX = "{date}｜"`，`{date}` 取當天資料夾的日期（`2026-11-05` 就是 `11/5｜`）；`seo` 寫 SEO 檔時就加上，標題結尾還寫著日期的會搬到最前面。
- **直式預告（Shorts）**：新聞頻道的流量幾乎都來自 Shorts 推薦，長片很少被推薦（2026-11 實測），所以每集長片配一支 60 秒內的預告，把人帶到長片。
  - `project.py` 寫 `SHORTS = dict(clips=[(從哪幾個字, 到哪幾個字之前)], head=(上方兩行), end="完整報導：點下方影片", layout="band")`，再跑 `explain/render.py 單集 --shorts`。只剪現成的旁白和畫面，不花點數。
  - 起訖字照 `script.md` 寫的字。開場、結尾有主播對嘴，要從那一段的第一句開始剪，嘴型才對得上。
  - 資料圖卡上有字，用 `band`（整張 16:9 放在中間），不要用 `square` 裁切。
  - 預告只放事件和數字。市場看好哪幾家、法人點名的台股、估值判斷都不放：剪短之後少了前後文，看起來會像在報明牌（見 [COMPLIANCE](COMPLIANCE.md)）。
  - SEO 檔加「Shorts 標題」「Shorts 說明欄」兩段：標題用鉤子開頭，不加 `EP` 前綴，結尾寫「｜深度報導EP8」；說明欄放長片網址。
  - 上傳用 `news/make.py upload 單集 --shorts`（id 記在 `out/youtube_shorts.json`）。「相關影片」API 不能設，要到 Studio 選長片。預告也算在每天的上限裡。
  - 一集要剪幾版預告：`project.py` 的 `CUTS = {"shorts_b": dict(clips=[...], aspect="9:16", head=..., end=..., layout="band")}`，跑 `explain/render.py 單集 --cut shorts_b` 出 `<NAME>_shorts_b.mp4`。SEO 檔再加「Shorts B 標題」「Shorts B 說明欄」，上傳用 `upload 單集 --shorts b`（id 記在 `out/youtube_shorts_b.json`）。說明欄寫 `{full}` 的地方，上傳時會換成長片網址，所以長片要先傳。
- **點數**（第一集實測）：旁白分兩段 100、10 張圖 200、主播對嘴兩段 100，現在送共 400，離峰半價。
