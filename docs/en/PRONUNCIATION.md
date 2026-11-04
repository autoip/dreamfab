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

## What to read again
- **One or two sentences wrong**: read just those again and put them back into the narration. On the news line: `news/make.py redo DAY 4 9` → `submit DAY redo` → `splice DAY 4 9`. The re-read applies the table, and the splice cuts at the pauses before and after, leaving at least 0.3 s.
- **Many spots wrong**: reading the whole narration again is cleaner. Its timing changes, so any lip-synced anchor parts must be lip-synced again; pictures and cards are kept.
- **The new take misreads something else**: mix the takes within a sentence, each where it is right, joined at a pause.
- **Cost**: 50 credits a narration part, 50 a lip-sync; half off-peak (03:00-09:00 Taiwan time).

## Before you swap: other ways
- **Write numbers as words**: 一千一百四十三 is safer than 1,143. On the news line the spoken column has words and the subtitle column has digits.
- **Write English as English**: Dow Jones, Oracle, Apple in Latin letters are read in English. On the news line the subtitle column can still show Chinese names.
- **Rephrase**: with no same-sounding character to hand, say it another way (一路貶爵 → 一路降爵).

## The table (used in Dreamfab productions)
From this project's explainers, in-depth reports and daily news. Copy all of it or only what you need.

**Characters with two readings**
| Subtitle | Read as | Note |
|---|---|---|
| 供給 | 供擠 | 給 is jǐ |
| 重啟 | 崇啟 | 重 is chóng |
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

**Numbers**
| Subtitle | Read as | Note |
|---|---|---|
| 〇 | 零 | e.g. 二〇二八 → 二零二八; 〇 is often read "circle" |
| 二二〇 | 二二零 | a year |

See also: [Explainer overview](explain/OVERVIEW.md), [News overview](news/OVERVIEW.md)
