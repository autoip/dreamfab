# 美股一分鐘 2026-11-03（二）：美東 11/2 收盤。數字與來源見 script.md 的資料來源
# row(name, value, pct, hot) / bar(name, pct, note, hot, top) / box(title, body, cls) come from news/make.py
DATE = "11/3（二）"
SOURCES = "資料來源：CNBC、Fortune、公司新聞稿、鉅亨網、中央社、MoneyDJ（美東 11/2 收盤）<br>主播與聲音為 AI 生成｜僅供參考，不構成投資建議"

COVER = dict(lines=[("費半重挫 3.4%", "down"), ("AI 股殺不停？", "gold")],
             sub="台指期夜盤 −917 點<br>Palantir 營收年增 96% 盤後仍下跌")
SEO = dict(
    titles=["費半重挫3.4%！AI股殺不停？台指夜盤跌917點｜美股一分鐘 11/3",
            "Palantir營收年增96%，盤後還是跌？昨晚美股開高走低｜美股一分鐘 11/3",
            "甲骨文股債募資200億美元、油價重挫7%：台股開盤前必看｜美股一分鐘 11/3"],
    lead="昨晚美股開高走低：道瓊小漲，那斯達克、標普收黑，費半重挫 3.4%，台指期夜盤跌 917 點。台股開盤前，一分鐘看懂。",
    tags=["Palantir", "甲骨文", "英特爾", "邁威爾", "蘋果財報", "油價", "期中選舉"])

CARDS = {
    "indices": '<div class="kick">昨晚美股收盤　美東 11/2</div><h1>開高走低</h1>'
               + row("道瓊工業", "51,983.98", 0.41) + row("那斯達克", "25,164.32", -1.07)
               + row("標普 500", "7,541.40", -0.51) + row("費城半導體", "10,328.33", -3.37, hot=True),
    "oracle": '<div class="kick">AI 支出疑慮再起</div><h1>甲骨文<br>股債各募 100 億美元</h1>'
              '<div class="big num down">▼8.76%</div><div class="sub">市場擔心 AI 投資燒錢、回報太慢</div>',
    "chips": '<div class="kick">晶片股全面走弱</div><h1>記憶體、處理器都跌</h1>'
             + bar("英特爾", -8.80, top=8.8) + bar("超微", -7.52, top=8.8) + bar("美光", -5.78, "鎧俠財測保守", top=8.8)
             + bar("台積電 ADR", -1.85, "398.63 美元", hot=True, top=8.8) + bar("聯電 ADR", -1.74, "16.39 美元", top=8.8),
    "deal": '<div class="kick">今年最大科技併購之一</div><h1>邁威爾收購<br>朗美通</h1>'
            '<div class="sub">企業價值約 1,150 億美元</div>'
            + bar("朗美通 Lumentum", -18.6, top=18.6) + bar("邁威爾 Marvell", -12.7, top=18.6),
    "apple": '<div class="kick">蘋果 第四財季財報</div><h1>優於預期<br>但展望保守</h1>'
             + box("✓ 營收、獲利都優於預期", "營收 1,144.8 億美元，年增 12%<br>每股盈餘 2.10 美元（預估 1.99）", "up")
             + box("▼ 毛利展望偏保守", "下一季毛利率 45–46%<br>市場原本預期 47%", "down")
             + '<div class="note">記憶體與零組件成本上升｜財報公布後盤後走低</div>',
    "palantir": '<div class="kick">帕蘭泰爾 Palantir 第三季財報</div><h1>營收年增 96%<br>盤後卻下跌</h1>'
                + box("✓ 營收 23.1 億美元", "首度突破 20 億美元<br>美國商業營收 9.84 億，年增 148%", "up")
                + box("▲ 調高全年財測", "全年營收約 85.3 億美元，年增 91%", "up")
                + '<div class="note">AI 類股賣壓之下，盤後股價先漲後跌</div>',
    "oil": '<div class="kick">國際油價　美伊可能重啟和談</div><h1>油價重挫<br>西德州跌破 100</h1>'
           + row("布蘭特原油", "104.77 美元", -7.63) + row("西德州原油", "96.46 美元", -7.36, hot=True),
    "futures": '<div class="kick">台指期夜盤　11/3 05:00 收</div><h1>開盤前壓力</h1>'
               '<div class="big num down">44,310</div><div class="sub num down" style="font-size:72px;font-weight:700">▼ 917 點</div>'
               '<div class="note">加權指數 11/2 收 44,920.14 點</div>',
    "election": '<div class="kick">今日關注　美東 11/3</div><h1>美國期中選舉</h1>'
                + box("眾議院", "民主黨被看好拿下") + box("參議院", "情勢未明")
                + box("市場關注", "AI 與資料中心的監管會不會變嚴"),
}
