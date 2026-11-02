# 示範廣告：雲茶烏龍 Kumo Oolong / Demo ad

**中文**

廣告線的示範：一個虛構的無糖罐裝高山烏龍茶，兩個市場版本，各用一種風格包。
- `en_keynote/`：英語，發表會風格，每個欄位都填好了
- `ja_variety/`：日語，綜藝風格，只寫了文案，其他是 `ad/new.py` 開案時的樣子

本資料夾只有設定檔和文案，不附任何素材。要實際跑，先把整個 `demo/` 複製到 `projects/<品牌>/<活動>/`，再照 [docs/zh-TW/ad/OVERVIEW.md](../../../docs/zh-TW/ad/OVERVIEW.md) 做：
1. 旁白選角，`narration.py jobs`，送出
2. `make_images.py` 產品照，送出
3. 配樂：把各版本的 `suno.md` 貼進 Suno 生成（Suno 沒有開放一般使用者用 API），下載放進 `music/`
4. `ad/cards.py`
5. `ad/render.py`：出主版和 CUTS 的每一支

**English**

The ad line's example: a made-up unsweetened canned high-mountain oolong, two market versions, each in its own style pack.
- `en_keynote/`: English, keynote look, every field filled in
- `ja_variety/`: Japanese, variety-show look, only the script written; the rest is as `ad/new.py` started it

Settings and scripts only, no media. To run it, copy `demo/` to `projects/<brand>/<campaign>/` and follow [docs/en/ad/OVERVIEW.md](../../../docs/en/ad/OVERVIEW.md):
1. cast a narrator, `narration.py jobs`, submit
2. `make_images.py` for the product shots, submit
3. music: paste each version's `suno.md` into Suno (it has no API for ordinary users) and download into `music/`
4. `ad/cards.py`
5. `ad/render.py`: the main cut and every CUTS entry
