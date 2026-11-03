# Dreamfab 造夢廠

**AI Agent 影音製作框架：一句話，你就是導演和製作人，AI Agent 幫你把心中夢想的影視作品做出來。**

中文 | [English](README.en.md)

Dreamfab 是讓 AI Agent（Claude Code、Codex，也實測過 Grok Bot）自動做影片的框架。你跟 agent 說一句話，它就照產線的 skill 寫劇本、送生成任務、看審核圖、剪輯、上字幕、混音、上架。每一批要花點數的任務都先報價，你點頭才送。

- **產線**：一種影片一條產線，各有自己的流程、格式和 skill。新的影片類型，就是一條新產線。
- **生成引擎**：畫面、影片、聲音、對嘴目前接 [AutoIP](https://autoip.ai) 公開 API（文生圖、圖生影片、多參考影片、對嘴、語音克隆、AI 作曲），之後接更多引擎。
- **共用核心** `dreamfab/`：送任務、算點數、離峰半價、本機剪輯合成、GPU 超分補幀、資源庫網頁、YouTube 上架（[共用核心與資源庫](docs/zh-TW/CORE.md)）。

## 產線：戲・曲・說・廣・影・聞

| 線 | 跟 agent 說一句話 | 狀態 | 文件 |
|---|---|---|---|
| **戲**：短劇 `drama/` | 用 dreamfab-drama 把 劇本.md 做成短劇 | 可用 | [短劇總覽](docs/zh-TW/drama/OVERVIEW.md) |
| **曲**：MV `mv/` | 用 dreamfab-mv 把 song.mp3 做成 MV | 可用 | [MV 總覽](docs/zh-TW/mv/OVERVIEW.md) |
| **說**：解說影片 `explain/` | 用 dreamfab-explain 把 MV《洛川》背後的歷史做成 5 分鐘解說 | 可用（靜態 B-roll；動態規劃中） | [解說總覽](docs/zh-TW/explain/OVERVIEW.md) |
| **廣**：廣告 `ad/` | 用 dreamfab-ad 把我的產品做成日、韓、英三國廣告，每國一種風格 | 可用（實體商品、服務、品牌；主版＋30／15 秒，16:9、9:16、1:1） | [廣告總覽](docs/zh-TW/ad/OVERVIEW.md) |
| **聞**：新聞 `news/` | 用 dreamfab-news 做今天的美股一分鐘 | 試播（每日 1 分鐘直式新聞：AI 主播開場收尾、字卡、封面和 SEO、結尾催訂閱；可上架到 YouTube、每天無人值守） | [新聞總覽](docs/zh-TW/news/OVERVIEW.md) |
| **影**：電影 | — | 之後 | — |

每個系列是一個世界（`projects/<系列>/`），演員和聲音（`cast/`、`voices/`）跨集、跨季重複演出，臉和聲音不會跑掉。

## 示範作品

**短劇《我的室友是楊貴妃》**：用短劇線做的穿越短劇。楊貴妃從馬嵬坡掉進負債三百萬的經紀人家裡，篇章一 10 集已全部上架，每集約 50 秒。 <!-- public-ok -->

- ▶ 第 1 集：https://youtu.be/kA4J9kLOVVo <!-- public-ok -->
- ▶ 全集播放清單：https://www.youtube.com/playlist?list=PLFDknh7mplug
- 🎵 同一個角色的 MV《馬嵬》：https://youtu.be/C6aGMU8mKdw（MV 線做的；短劇和 MV 的說明欄互相連結） <!-- public-ok -->

**MV**：同一條 MV 線，四種曲風與畫面風格。點縮圖到 YouTube 觀看。

| **暗黑金屬史詩** | **王家衛風港式抒情** | **國風古風對唱** | **賽博龐克女聲 Rap** |
|:---:|:---:|:---:|:---:|
| [![《黑日聖殿》](https://img.youtube.com/vi/ErQCd04OGA8/mqdefault.jpg)](https://youtu.be/ErQCd04OGA8) | [![《過期的那一分鐘》](https://img.youtube.com/vi/fMTLkI7qDq8/mqdefault.jpg)](https://youtu.be/fMTLkI7qDq8) | [![《洛川》](https://img.youtube.com/vi/OlIQYvfwZhA/mqdefault.jpg)](https://youtu.be/OlIQYvfwZhA) | [![《科技睪丸》](https://img.youtube.com/vi/fZ9SlclC9ng/mqdefault.jpg)](https://youtu.be/fZ9SlclC9ng) |

一整季的 MV 系列：[《國風淒美對唱》播放清單](https://www.youtube.com/playlist?list=PLfoBI7oPycHg)，6 集，同一套畫面和包裝，每集換一種曲風。

## 安裝

### 電腦：一行安裝（Claude Code / Codex）

**macOS / Linux / Git Bash：**

```bash
curl -fsSL https://raw.githubusercontent.com/autoip/dreamfab/main/install.sh | bash
```

**Windows PowerShell：**

```powershell
irm https://raw.githubusercontent.com/autoip/dreamfab/main/install.ps1 | iex
```

預設裝短劇、MV、解說三條線；只做短劇就設 `DREAMFAB_LINES=drama`。plugin 安裝、ffmpeg（要有 libass）、字型、`AUTOIP_API_KEY` 見 [SETUP.md](docs/zh-TW/SETUP.md)。

**更新**：再跑一次同一行。作品和設定都不會動，舊版的資料庫會自己併進來；plugin、自己 clone 的更新方式見 [SETUP.md〈從舊版更新〉](docs/zh-TW/SETUP.md#7-從舊版更新)。

### 手機：Grok Bot（已實測）

在手機上跟 Grok Bot 說 `安裝 https://github.com/autoip/dreamfab`，它會先看過安裝腳本，在它自己的機器上裝好，再跟你要 AutoIP API 金鑰。不需要 PC，手機就能開工廠。

<img src="docs/images/grok_bot_install.jpg" width="300" alt="在手機上跟 Grok Bot 說「安裝 github.com/autoip/dreamfab」，它看過安裝腳本後開始安裝">

那台機器沒有 GPU 也不影響：生成都在 AutoIP 雲端，剪輯、字幕、混音用 CPU 就夠，GPU 只加速選用的步驟。上架 YouTube 要在那台機器登入 Google，這一步還沒實測。

## 資源庫網頁

`python dreamfab/library.py serve projects` 開一個本機網頁，所有系列的每一集、每顆鏡頭、角色、點數、上架狀態都在裡面，影片直接播。說明見 [共用核心與資源庫](docs/zh-TW/CORE.md#本機資源庫網頁)。

![首頁：上面是流程，下面是戲・曲・說三條產線，每一集停在它目前的站](docs/images/library_home_lines.jpg)

![倉庫：短劇系列一季一層，▶ 已上架、待上架](docs/images/library_home_store_drama.jpg)

![倉庫：MV 和解說系列，虛線空位是還在產線上的那一集](docs/images/library_home_store_mv.jpg)

## 文件

| 文件 | 內容 |
|---|---|
| [SETUP.md](docs/zh-TW/SETUP.md) | 安裝、顯卡、API key、離峰半價、YouTube 登入、素材權利、從舊版更新 |
| [短劇總覽](docs/zh-TW/drama/OVERVIEW.md)・[MV 總覽](docs/zh-TW/mv/OVERVIEW.md)・[解說總覽](docs/zh-TW/explain/OVERVIEW.md) | 每條線的流程、格式、剪輯、上架、踩坑紀錄 |
| [共用核心與資源庫](docs/zh-TW/CORE.md) | 系列資料夾、資源庫網頁、`dreamfab/` 每個檔案做什麼 |
| [WORKFLOW.md](docs/zh-TW/WORKFLOW.md) | 工作流程開關：哪些步驟自動做，你自己決定 |
| [GPU_ENHANCE.md](docs/zh-TW/GPU_ENHANCE.md) | 本機超分＋補幀：工具、實測速度與效果 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 貢獻原始碼：什麼可以進 repo、去識別化、送出前的檢查 |

## 未來方向

更多生成引擎（同一條產線換引擎、比畫質和價錢）、更多產線（影・電影；聞・新聞從試播到正式上線），以及更完整的 agent 自動化：從一句話到上架，人只在花錢和公開之前點頭。

## 授權

[MIT](LICENSE)。用 Dreamfab 做的作品歸你；請只用你有權使用的素材（見 [SETUP.md〈素材的權利〉](docs/zh-TW/SETUP.md#6-素材的權利)）。
