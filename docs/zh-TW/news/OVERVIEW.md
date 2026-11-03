# 聞・新聞 `news/`（試播）

每天一支直式短新聞（1080x1920，約 1 分鐘）：
- AI 主播開場、結尾露臉對嘴，中間用字卡講數字。
- 字幕和片頭主題曲從頭到尾都有。

第一個節目是「美股一分鐘」：台股開盤前，一分鐘看懂昨晚美股。

**目前是試播**：
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
- **不寫建議**：只報發生了什麼，不寫買賣建議。

### 2. 寫腳本
- `python news/make.py new projects/<節目> 2026-11-04`：開新的一天。
  - `day.py` 從前一天複製過來，日期自動換好。
  - `script.md` 已經放好固定的第一句和最後一句。
- **長度**：每行一句；約 11 句、280 字，就是 1 分鐘左右（實測每秒 5.2 字）。
- **唸的那欄**：
  - 數字寫國字，例如「百分之零點四」。
  - 美國指數和公司名直接唸英文：Dow Jones、Oracle、Intel、Apple、Palantir…
  - 台灣公司唸中文：台積電、聯電。
  - 避開多音字：「重啟」常被唸成 zhòng qǐ，改寫成「恢復」或「再度展開」。
- **字幕那欄**：數字用阿拉伯數字，名字寫中文（道瓊、甲骨文、英特爾…）。
- **畫面那欄**：寫 `anchor`（主播）或字卡 id。連續幾行用同一張卡，畫面就不換。
- **字卡**：在 `day.py` 用 `row()`（指數、股價）、`bar()`（跌幅長條）、`box()`（重點框）組。
  - 漲紅跌綠（台灣習慣）。
  - 公司只放文字和數字，不放 logo，也不放真人照片。
- **片尾**：一定要列資料來源，並標明「主播與聲音為 AI 生成」「僅供參考，不構成投資建議」。

### 3. 生成
```
python news/make.py cards  DAY
python news/make.py voice  DAY
python news/make.py submit DAY voice --off-peak      # 旁白
python news/make.py check  DAY                       # 逐字稿；列出聽起來不一樣的字
python news/make.py anchor DAY                       # 只取主播露臉的兩段
python news/make.py submit DAY lipsync --off-peak    # 對嘴
python news/make.py render DAY
```
- **對嘴只送主播露臉的兩段**（開場、結尾，合計約 8 秒）：比整段送快三倍，點數一樣。
  - 對嘴影片常少最後半秒，所以送出的音檔尾巴補 0.6 秒靜音。
  - 片尾在影片用完的地方接上全螢幕贊助卡。
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
  - Shorts 架上和頻道的 Shorts 分頁顯示的是影片的第一個畫面，不是上傳的縮圖，所以要搭配 `COVER_FRAME`，並且先做 `cover` 再 `render`。
  - 上方放兩行大字鉤子：第一行是最大的數字（漲紅跌綠），第二行是問句。
  - 下方一行放第二、第三則重點。
- **SEO**（`day.py` 的 `SEO`）：
  - 標題 A、B、C 都用鉤子開頭：數字加反差或問句，例如「Palantir 營收年增 96%，盤後還是跌？」。最後加上節目名和日期。
  - 說明欄依序是：導言、每則新聞一行（取自字幕）、資料來源、AI 與投資聲明、贊助、標籤。
  - 格式跟其他線的 `YouTube_SEO.txt` 一樣。試播期不發布，只出檔案。

### 5. 結尾催訂閱
`series.py` 的 `CTA_LINE` 是主播最後說的那句，例如「記得訂閱，每天開盤前看美股一分鐘，養成習慣，掌握財金動脈！」：
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
  - 05:15 開工，約 05:30 出片，離峰半價，台股開盤前還有時間重做。

## 無人值守：每天自動做完、上架
用系統排程（Windows 工作排程器、cron）每天叫 agent 跑一次，例如 `claude -p "<每日指示>" --allowedTools Bash,Read,Write,Edit,WebSearch,WebFetch`：
- **每日指示**：寫清楚使用者預先同意了什麼（每天離峰送任務的點數、直接公開），也寫清楚不能做什麼（不碰別的專案、不 commit）。
- **流程**：照上面第 1 到第 6 步，最後在節目資料夾的 log 寫下網址、點數、每步時間和出錯的地方。
- **排哪幾天**：週一到週五 05:15；週一做的是上週五的收盤，美國休市就不做。
- **太晚就跳過**：電腦睡著、錯過時間時，超過 08:30 才開始就跳過，避免離峰結束後原價做出過時的新聞。
