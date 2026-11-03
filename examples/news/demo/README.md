# 示範新聞：美股一分鐘 / Demo news brief（試播 / pilot）

**中文**

新聞線的示範：「美股一分鐘」11/3 那一集。
- 內容：美東 11/2 收盤、台股開盤前。
- 結構：AI 主播開場、結尾露臉，中間 9 張字卡，約 1 分鐘。
- 試播：只出檔案，沒有發布。

這個資料夾只有設定檔和文案，不附任何素材（主播照、聲音、主題曲都要自己做）：
- `series.py`：節目設定
- `music/suno.md`：主題曲的 Suno 曲風
- `2026-11-03/`：那一天的 `script.md`（含資料來源）和 `day.py`（字卡、封面、SEO）

要實際跑，先把整個 `demo/` 複製到 `projects/<節目>/`，再照 [docs/zh-TW/news/OVERVIEW.md](../../../docs/zh-TW/news/OVERVIEW.md) 做：
1. 主播定裝照和聲音樣本，放進 `cast/`、`voices/`
2. 主題曲：把 `music/suno.md` 貼進 Suno 生成，放進 `music/`
3. `news/make.py cards`、`cover`、`seo`
4. `news/make.py voice`、`submit voice`、`check`
5. `news/make.py anchor`、`submit lipsync`、`render`

這一集的數字都核對過兩個來源，但只是當天的示範，不是即時行情。

**English**

The news line's example: the 11/3 episode of a one-minute US-markets brief.
- What it covers: the US close of 11/2, before the Taiwan open.
- How it is built: an AI anchor opens and closes on camera, with nine cards in between, about a minute long.
- Pilot: files only, nothing published.

Settings and scripts only, no media (make your own anchor portrait, voice and theme):
- `series.py`: the show
- `music/suno.md`: the theme's Suno style
- `2026-11-03/`: that day's `script.md` (with its sources) and `day.py` (cards, cover, SEO)

To run it, copy `demo/` to `projects/<show>/` and follow [docs/en/news/OVERVIEW.md](../../../docs/en/news/OVERVIEW.md):
1. the anchor's portrait and voice sample into `cast/` and `voices/`
2. the theme: paste `music/suno.md` into Suno, put the track in `music/`
3. `news/make.py cards`, `cover`, `seo`
4. `news/make.py voice`, `submit voice`, `check`
5. `news/make.py anchor`, `submit lipsync`, `render`

Every number in this episode was checked against two sources, but it is a dated example, not live market data.
