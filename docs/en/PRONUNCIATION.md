# When the AI voice misreads a word: the swap table

Cloned voices sound good but misread words: a character with two readings gets the wrong one, a rare character gets a guess, numbers and symbols come out odd. Dreamfab's fix is simple: **the subtitle keeps the word, the voice reads a common character that sounds the same**, written down once in a swap table (`SAY`) and applied to every episode after.

[中文](../zh-TW/PRONUNCIATION.md) | English

## Why words get misread
| Kind | Example | Read as |
|---|---|---|
| A character with two readings | 供給 (jǐ), 重啟 (chóng), 亭長 (zhǎng) | gěi, zhòng, cháng |
| A rare character | 宓妃, 曹叡, 磷化銦 | a guess, or a look-alike |
| Terms | 光纖, 叢集, 女媧 | 纖 as qiān, 叢 wrong |
| Numbers and symbols | 二〇二八, 1,143, 1.6T | 〇 as "circle", commas and points read oddly |
| English letters and names | ADR, Dow Jones | sometimes spelled out, sometimes guessed in Chinese |
| Traditional characters | 廣告, 下載, 學習 | 槓購, 下賊, 學士; right when the same text is in simplified (AutoIP converts it now) |

## Finding them
1. **The check**:
   - Run it when the narration comes back: `explain/narration.py <folder> check` on the explainer and ad lines, `news/make.py check DAY` on the news line.
   - It transcribes the narration, compares it with the script by pinyin, and lists the spots that sound different, with their times. Same-sounding words pass and are not listed.
2. **Always listen**: the recogniser makes mistakes too, above all with English names and numbers. Re-reading on the transcript alone often wastes credits.
3. **The user's ear decides**: some are habit, not right or wrong. If the user says 瓶頸 as 瓶錦, read it that way.

## The fix: `SAY`
```python
SAY = [("光纖", "光仙"), ("供給", "供擠"), ("叢集", "從集"), ("瓶頸", "瓶錦"), ("重啟", "崇啟"), ("銦", "因")]
```
- **Pairs**: (what the subtitle shows, what the voice reads).
- **The same length on both sides**: so the subtitles and the voice still line up character by character.
- **A common character with the same sound**: the tone too. The swap need not mean anything; it only has to be easy to read right.
- **Swap only the trouble spot**: for 大叢集, swap 叢集. A whole word is safer than a single character, which would change other words too.
- **Only what is read changes**: the subtitles, the caption file search reads, and the cover keep the original word.

| Line | Where the table lives | When it applies |
|---|---|---|
| 說 explainer, 廣 ads | `SAY` in each episode's `project.py` | when `narration.py jobs` writes the narration jobs, and when the render times the subtitles |
| 聞 news | `SAY` in the show's `series.py` (a day's `day.py` may add more) | `news/make.py voice`, `redo`, and timing |
| 戲 drama, 曲 MV | not supported: lines and singing are generated with the video | rewrite the line, or reshoot that shot |

**One table per show**: on the news line it lives in `series.py`, so every day uses it. Explainers and in-depth reports have one `project.py` per episode; copy the table from the last episode when starting the next.

**Shows read by the same voice share one table**: a word one show's voice gets wrong, the other's gets wrong too. Keep `SAY` in a shared file that each show reads, and add new words only there. `series.py` and `project.py` both know where they are (`__file__`), for example:

```python
import os
exec(open(os.path.join(os.path.dirname(__file__), "..", "錯音表.py"), encoding="utf-8").read())
SAY = SAY + [("範圍，最快", "範圍。最快")]   # a swap for one sentence of this episode stays here
```

**Dreamfab's own table is public in [`dreamfab/say_zh.py`](../../dreamfab/say_zh.py)**: the daily news and the in-depth reports both read it, and you can use it as it is. It was found with one voice (a Taiwanese-accented anchor on AutoIP's default engine); another voice may need fewer pairs, or others. AutoIP now turns traditional characters into simplified ones before reading (see "Trouble that is not a misread" below), so the table keeps only what the script does not explain; with a service that reads traditional as it is, the pairs marked "no longer needed" below may have to come back.

```python
from dreamfab.say_zh import SAY
SAY = SAY + [("範圍，最快", "範圍。最快")]
```

## What to read again
- **One or two sentences wrong**: read just those again and put them back into the narration. On the news line: `news/make.py redo DAY 4 9` → `submit DAY redo` → `splice DAY 4 9`. The re-read applies the table, and the splice cuts at the pauses before and after, leaving at least 0.3 s.
- **Many spots wrong**: reading the whole narration again is cleaner. Its timing changes, so any lip-synced anchor parts must be lip-synced again; pictures and cards are kept.
- **The new take misreads something else**: mix the takes within a sentence, each where it is right, joined at a pause. On the explainer line, `NARRATION` takes `dict(audio=old, job=..., stop_at="X")` followed by `dict(audio=new, job=..., start_at="X")`: the old take up to X, the new one from X, both cut at the pause before X.
- **One part a chapter** (explainer line, `VOICE_SPLIT = "chapter"`): a misread chapter is read again on its own.
- **Cost**: 50 credits a narration part, 50 a lip-sync; half off-peak (03:00-09:00 Taiwan time).

## Before you swap: other ways
- **Write numbers as words**: 一千一百四十三 is safer than 1,143. On the news line the spoken column has words and the subtitle column has digits.
- **Write English as English**: Dow Jones, Oracle, Apple in Latin letters are read in English. On the news line the subtitle column can still show Chinese names.
- **Rephrase**: with no same-sounding character to hand, say it another way (一路貶爵 → 一路降爵).

## Trouble that is not a misread
- **The last syllable is cut off**: the voice service cuts off the last moment of what it reads; measured, nearly every file ended in the middle of a sound. On the explainer line every part ends with a throwaway "謝謝收看", cut off at the pause before it (`TAIL` in `explain/common.py`). Ending in "……" did not help.
- **A word comes out as a noise**: the recogniser hears nothing there, and `check` marks it "nothing heard". Seen with an English name followed straight by a Chinese verb (the 買 of "AppLovin Ads 買廣告"); one more word between them ("Ads 平台買廣告") fixed it.
- **Misreads caused by traditional characters: AutoIP converts to simplified now**: the voice model was most likely trained on simplified Chinese and stumbles on traditional characters. 廣告 was read as 槓購 all through an episode; 廣誥 and 獷告 did not help, only simplified 广告 did. The whole of in-depth report EP7 (about 3,000 characters) was read twice in traditional and twice in simplified, with no table: both recognisers heard 94 misreads in traditional and 6 in simplified. All 94 sat on or next to a character written differently in the two scripts, and both takes went wrong in exactly the same places. Since 2026-11-06 AutoIP turns traditional characters into simplified ones, one by one, before its voice reads them: send traditional as it is, and the subtitles keep your own text. The same parts sent in traditional again went from 47 misreads to 3, and the audio was identical to the simplified takes. With another voice service, convert it yourself with OpenCC's `t2s` (character by character, so the length and subtitle timing stay the same).
- **Swap only what both recognisers hear wrong**: a word is not misread every time, and recognisers mishear too. One recogniser alone (medium or large-v3) is usually the recogniser; both of them, or your ears, mean a pair for the table.
- **Where chapters are cut**: the recogniser's word times run on over a pause, so a cut there takes off the end of the last syllable. The explainer line cuts at the pause found in the sound.

## The table (used in Dreamfab productions)
From this project's explainers, in-depth reports and daily news. Copy all of it or only what you need. The one the news channel reads now is `dreamfab/say_zh.py`.

**Characters with two readings**
| Subtitle | Read as | Note |
|---|---|---|
| 供給 | 供擠 | 給 is jǐ |
| 重啟 | 崇啟 | 重 is chóng |
| 金鑰 | 金要 | 鑰 is yào |
| 門檻 | 門砍 | 檻 is kǎn |
| 乾脆 | 甘脆 | 乾 is gān; the voice said qián |
| 亭長 | 亭掌 | 長 is zhǎng |
| 和之, 和了 | 賀之, 賀了 | 和 as in singing along is hè |
| 脈脈 | 末末 | mò mò |
| 文種 | 文腫 | a name, 種 is zhǒng |
| 夫差 | 夫釵 | 差 is chāi |
| 會稽 | 快雞 | 會 is kuài |
| 衣繡 | 意繡 | 衣 as a verb is yì |
| 被髮覆面 | 披髮覆面 | 被 is pī |
| 少翁 | 紹翁 | 少 is shào |
| 邪 | 耶 | at a sentence end, yé |
| 單于 | 蟬于 | 單 is chán |
| 閼氏 | 煙支 | yān zhī |
| 呼韓邪 | 呼韓爺 | 邪 is yé |
| 妹喜 | 末喜 | 妹 is mò |
| 孰制匠之 | 熟制匠之 | 孰 is shú |

**Rare characters**
| Subtitle | Read as | Subtitle | Read as | Subtitle | Read as |
|---|---|---|---|---|---|
| 宓妃, 甄宓 | 伏妃, 甄伏 | 曹叡 | 曹銳 | 丁廙 | 丁異 |
| 鄴城 | 業城 | 耳璫 | 耳噹 | 玉鏤 | 玉漏 |
| 垓下 | 該下 | 騅 | 追 | 玉玦 | 玉決 |
| 縢 | 藤 | 嵬 | 圍 | 鼙 | 皮 |
| 紉 | 任 | 嬙 | 牆 | 秭 | 子 |
| 鴟夷 | 吃夷 | 苧蘿 | 住蘿 | 顰 | 頻 |
| 沚戛 | 止夾 | 鉞 | 越 | | |
| 胡仔 | 胡子 | 顧藉 | 顧借 | 阮大鋮 | 阮大成 |
| 蔡邕 | 蔡雍 | 臨邛 | 臨窮 | 邛崍 | 窮來 |
| 當壚 | 當爐 | 皚如 | 挨如 | 許宣 | 許軒 |
| 缽 | 撥 | 冢 | 腫 | 擢素手 | 濁素手 |
| 機杼 | 機住 | 姮娥 | 恆娥 | 枚筮 | 枚是 |
| 晦芒 | 會芒 | 毋驚毋恐 | 無驚無恐 | 逢蒙 | 龐蒙 |
| 莒國 | 舉國 | 淄水 | 資水 | 杞梁 | 起梁 |
| 顓頊 | 專需 | 鼇 | 熬 | 盧仝 | 盧同 |
| 妲己 | 達己 | 銦 | 因 | | |

**Terms and habits**
| Subtitle | Read as | Note |
|---|---|---|
| 光纖 | 光仙 | 纖 is xiān; the voice often says qiān |
| 叢集 | 從集 | 叢 is cóng |
| 瓶頸 | 瓶錦 | the user's habit |
| 女媧 | 女娃 | 媧 is wā |
| 渦輪 | 窩輪 | 渦 is wō |
| autoip.ai | AutoIP點AI | the subtitle shows the address, the voice says it in words: both are 9 characters |
| 駭客 | 害客 | 駭 is hài |
| 反駁 | 反伯 | 駁 is bó |
| 帳上 | 丈上 | 帳 is zhàng |
| 黃仁勳 | 皇仁薰 | a name |
| 槓桿擴張 | 幹港闊章 | gàng gǎn, kuò: the characters the user's ear picked |
| 情報 | 晴報 | the default engine said something like 新房 |
| 攻擊 | 公擊 | heard as 中擊 |
| 釣魚 | 吊魚 | 釣 is diào |
| 企業 | 啟夜 | the characters the user's ear picked |
| 外洩 | 外謝 | 洩 is xiè |
| 併購 | 病夠 | 併 is bìng; the user's ear picked these |
| 飆漲 | 標漲 | 飆 is biāo |
| 布蘭特 | 步蘭特 | heard as 波蘭特 |

**Common words read wrong too** (both recognisers heard the misread)
| Subtitle | Read as | Subtitle | Read as | Subtitle | Read as |
|---|---|---|---|---|---|
| 資料 | 姿料 | 註冊 | 註策 | 機關 | 基關 |

**No longer needed: caused by traditional characters** (since 2026-11-06 AutoIP converts to simplified before reading, and these come out right unchanged; only a service that reads traditional as it is needs them)
| Subtitle | Read as | Subtitle | Read as | Subtitle | Read as |
|---|---|---|---|---|---|
| 廣告 | 广告 (simplified) | 報告 | 报告 (simplified) | 贊助 | 讚助 |
| 下載 | 下再 | 學習 | 學席 | 推薦 | 推見 |
| 獎勵 | 獎麗 | 蒐集 | 搜集 | 訴訟 | 訴送 |

**Numbers**
| Subtitle | Read as | Note |
|---|---|---|
| 〇 | 零 | e.g. 二〇二八 → 二零二八; 〇 is often read "circle" |
| 二二〇 | 二二零 | a year |

See also: [Explainer overview](explain/OVERVIEW.md), [News overview](news/OVERVIEW.md)
