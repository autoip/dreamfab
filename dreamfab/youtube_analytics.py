"""Read the channel's YouTube Analytics by line, so the next batch is made from what viewers did (read only).

usage: python dreamfab/youtube_analytics.py pull [--since 2025-01-01] [--until DATE] [--curves 20]
       python dreamfab/youtube_analytics.py report [FILE] [--group NAME=REGEX ...] [--md OUT.md]
pull    every upload on the logged-in channel (Data API: title, length) and its Analytics from --since to --until:
        views, minutes, average view percentage, likes, subscribers per video; Shorts or long (YouTube's own split);
        traffic sources, search terms, suggested-by videos, outside sites, countries, age and gender, devices,
        subscribed or not; the retention curve of the --curves most-watched videos
        -> ~/.config/dreamfab/analytics/<channel>_<since>_<until>.json (next to the shared database; every pull kept)
report  the newest pull (or FILE), in lines: Shorts and long by default; --group puts the videos whose title matches
        REGEX in line NAME, first match wins, the rest stay Shorts / long
        (e.g. --group "短劇=^S\\dE\\d" --group "合集=完全版" --group "解說=解說")
        --md also writes the report to a file
To see what a change did (a new opening, a new title), pull again with --since the day of the change: YouTube's numbers
are about two days behind, so give it a week. Small channels have small samples: read the medians, not one video.
The first pull logs in again to add read-only analytics to the saved login (dreamfab/youtube_api.py: uploads keep
working on the old one); the OAuth client's Google Cloud project needs the YouTube Analytics API enabled (the error
says where if it is not).
"""
import glob, json, os, re, statistics, sys
from collections import defaultdict
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # run as a script: the repo root
from dreamfab import db as shared

DIR = os.path.join(os.path.dirname(shared.PATH), "analytics")
BASIC = "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,likes,shares,comments,subscribersGained"
QUERIES = {   # name: (metrics, dimensions, extra)
    "total": (BASIC, None, {}),
    "video": (BASIC, "video", dict(sort="-views", maxResults=200)),
    "shorts": ("views", "video", dict(filters="creatorContentType==shorts", sort="-views", maxResults=200)),
    "format": (BASIC, "creatorContentType", {}),
    "day": ("views,estimatedMinutesWatched,subscribersGained", "day", dict(sort="day")),
    "traffic": ("views,estimatedMinutesWatched", "insightTrafficSourceType", dict(sort="-views")),
    "traffic_shorts": ("views", "insightTrafficSourceType", dict(filters="creatorContentType==shorts", sort="-views")),
    "search": ("views", "insightTrafficSourceDetail", dict(filters="insightTrafficSourceType==YT_SEARCH", sort="-views",
                                                           maxResults=25)),
    "suggested": ("views", "insightTrafficSourceDetail", dict(filters="insightTrafficSourceType==RELATED_VIDEO",
                                                              sort="-views", maxResults=25)),
    "outside": ("views", "insightTrafficSourceDetail", dict(filters="insightTrafficSourceType==EXT_URL", sort="-views",
                                                            maxResults=25)),
    "country": ("views,estimatedMinutesWatched", "country", dict(sort="-views", maxResults=25)),
    "audience": ("viewerPercentage", "ageGroup,gender", {}),
    "device": ("views,estimatedMinutesWatched", "deviceType", dict(sort="-views")),
    "subscribed": ("views,estimatedMinutesWatched", "subscribedStatus", {}),
}
TRAFFIC = {"SHORTS": "Shorts 動態", "SUBSCRIBER": "首頁與訂閱內容（瀏覽功能）", "RELATED_VIDEO": "推薦影片",
           "YT_SEARCH": "YouTube 搜尋", "YT_CHANNEL": "頻道頁", "PLAYLIST": "播放清單", "EXT_URL": "外部網站",
           "NO_LINK_OTHER": "直接或不明", "YT_OTHER_PAGE": "YouTube 其他頁面", "END_SCREEN": "片尾畫面",
           "SHORTS_CONTENT_LINKS": "Shorts 相關影片連結", "NOTIFICATION": "通知", "HASHTAGS": "主題標籤",
           "ANNOTATION": "資訊卡", "SOUND_PAGE": "音訊頁面", "PLAYLIST_PAGE": "播放清單頁"}


def secs(iso):
    m = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    return sum(int(x or 0) * k for x, k in zip(m.groups(), (86400, 3600, 60, 1))) if m else 0


def pull(since="2025-01-01", until=None, curves=20):
    from dreamfab.youtube_api import youtube, analytics
    until = until or date.today().isoformat()
    yt, ya = youtube(), analytics()
    ch = yt.channels().list(part="snippet,contentDetails,statistics", mine=True).execute()["items"][0]
    ids, tok = [], None
    while True:
        r = yt.playlistItems().list(part="contentDetails", playlistId=ch["contentDetails"]["relatedPlaylists"]["uploads"],
                                    maxResults=50, pageToken=tok).execute()
        ids += [i["contentDetails"]["videoId"] for i in r["items"]]
        tok = r.get("nextPageToken")
        if not tok:
            break
    videos = {}
    for k in range(0, len(ids), 50):
        for v in yt.videos().list(part="snippet,contentDetails,status", id=",".join(ids[k:k + 50])).execute()["items"]:
            videos[v["id"]] = dict(title=v["snippet"]["title"], at=v["snippet"]["publishedAt"],
                                   secs=secs(v["contentDetails"]["duration"]), privacy=v["status"]["privacyStatus"])
    out = dict(channel=ch["id"], title=ch["snippet"]["title"], subscribers=ch["statistics"].get("subscriberCount"),
               since=since, until=until, pulled=date.today().isoformat(), videos=videos, tables={}, curves={})

    def query(**kw):
        return ya.reports().query(ids="channel==MINE", startDate=since, endDate=until, **kw).execute()
    for name, (metrics, dims, extra) in QUERIES.items():
        try:
            r = query(metrics=metrics, **({"dimensions": dims} if dims else {}), **extra)
            out["tables"][name] = dict(cols=[c["name"] for c in r["columnHeaders"]], rows=r.get("rows", []))
            print(f"  {name:15} {len(out['tables'][name]['rows'])} rows", flush=True)
        except Exception as e:   # one table YouTube will not give (too little data, not enabled) does not stop the rest
            print(f"  {name:15} !! {str(e)[:300]}", flush=True)
    for vid in [r[0] for r in out["tables"].get("video", {}).get("rows", [])][:curves]:
        try:
            r = query(metrics="audienceWatchRatio,relativeRetentionPerformance", dimensions="elapsedVideoTimeRatio",
                      filters=f"video=={vid}")
            if r.get("rows"):
                out["curves"][vid] = r["rows"]
        except Exception as e:
            print(f"  curve {vid} !! {str(e)[:120]}", flush=True)
    print(f"  {len(out['curves'])} retention curves", flush=True)
    os.makedirs(DIR, exist_ok=True)
    path = os.path.join(DIR, f"{ch['id']}_{since}_{until}.json")
    json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return path


def rows(d, name):
    t = d["tables"].get(name)
    return [dict(zip(t["cols"], r)) for r in t["rows"]] if t else []


def report(path, groups=()):
    d = json.load(open(path, encoding="utf-8"))
    V, out = d["videos"], []
    say = out.append
    shorts = {r["video"] for r in rows(d, "shorts")}
    pat = [(n, re.compile(rx)) for n, rx in groups]

    def line(vid):
        t = V.get(vid, {}).get("title", "")
        fmt = "Shorts" if vid in shorts else "長片"
        return next((n for n, rx in pat if rx.search(t)), fmt), fmt
    per = rows(d, "video")
    tot = (rows(d, "total") or [{}])[0]
    say(f"# {d['title']}：{d['since']} 到 {d['until']}（{d['pulled']} 抓，數據大約晚兩天）\n")
    say(f"觀看 {tot.get('views', 0):,}、觀看時間 {tot.get('estimatedMinutesWatched', 0):,} 分鐘、新訂閱 "
        f"{tot.get('subscribersGained', 0)}（目前訂閱 {d['subscribers']}）\n")

    say("## Shorts 和長片\n")
    fm = {r["creatorContentType"]: r for r in rows(d, "format")}
    tv, tm = max(1, tot.get("views", 1)), max(1, tot.get("estimatedMinutesWatched", 1))
    say("| | 觀看 | 佔觀看 | 佔觀看時間 | 平均看完 | 新訂閱 |\n|---|---|---|---|---|---|")
    for k, name in (("shorts", "Shorts"), ("videoOnDemand", "長片")):
        r = fm.get(k)
        if r:
            say(f"| {name} | {r['views']:,} | {100 * r['views'] / tv:.0f}% | {100 * r['estimatedMinutesWatched'] / tm:.0f}% "
                f"| {r['averageViewPercentage']:.0f}% | {r['subscribersGained']} |")
    say("\nShorts 帶觀看，長片帶觀看時間和訂閱：兩邊都要，各自看各自的數字。\n")

    say("## 各條線（看中位數：一支爆紅會把總數拉歪）\n")
    g = defaultdict(list)
    for r in per:
        g[line(r["video"])[0]].append(r)
    say("| 線 | 支數 | 觀看 | 每支中位數 | 平均看完 | 觀看分鐘 | 新訂閱 | 每千次觀看的讚 |\n|---|---|---|---|---|---|---|---|")
    for name, lst in sorted(g.items(), key=lambda kv: -sum(r["views"] for r in kv[1])):
        vs = sum(r["views"] for r in lst)
        pct = sum(r["averageViewPercentage"] * r["views"] for r in lst) / max(1, vs)
        say(f"| {name} | {len(lst)} | {vs:,} | {statistics.median(r['views'] for r in lst):.0f} | {pct:.0f}% | "
            f"{sum(r['estimatedMinutesWatched'] for r in lst):,} | {sum(r['subscribersGained'] for r in lst)} | "
            f"{1000 * sum(r['likes'] for r in lst) / max(1, vs):.0f} |")

    say("\n## 開頭留不留得住人\n")
    say("還在看的比例：1.0 = 全部的人；Shorts 會重播，所以開頭常超過 1。相對留存：跟同長度的影片比，0.5 是中位數。\n")
    say("| 影片 | 長度 | 5% | 25% | 50% | 相對留存 | |\n|---|---|---|---|---|---|---|")
    early = []
    for vid, rr in d["curves"].items():
        v, (_, fmt) = V.get(vid, {}), line(vid)
        at = lambda x: min(rr, key=lambda r: abs(r[0] - x))[1]
        rel = sum(r[2] for r in rr) / len(rr)
        flag = ""
        if fmt == "長片" and at(0.05) < 0.8:
            flag = "開頭就走掉兩成以上"; early.append(vid)
        elif fmt == "Shorts" and at(0.25) < 0.5:
            flag = "四分之一前走掉一半"
        say(f"| {v.get('title', vid)[:36]} | {v.get('secs', 0)} 秒 | {at(0.05):.2f} | {at(0.25):.2f} | {at(0.5):.2f} | {rel:.2f} | {flag} |")
    if early:
        say(f"\n{len(early)} 支長片開頭就掉人：先看第一秒是什麼（片頭卡、空景、慢慢淡入），換成最強的畫面。\n")

    say("## 觀眾從哪裡來\n")
    sh = {r["insightTrafficSourceType"]: r["views"] for r in rows(d, "traffic_shorts")}
    say("| 來源 | 觀看 | 其中 Shorts | 觀看分鐘 |\n|---|---|---|---|")
    for r in rows(d, "traffic"):
        k = r["insightTrafficSourceType"]
        say(f"| {TRAFFIC.get(k, k)} | {r['views']:,} | {sh.get(k, 0):,} | {r['estimatedMinutesWatched']:,} |")
    titles = " ".join(v["title"] for v in V.values())
    terms = rows(d, "search")
    if terms:
        say("\n**搜尋字**（標題裡還沒有的字，就是可以補進標題的字）：\n")
        for r in terms:
            w = r["insightTrafficSourceDetail"]
            say(f"- {w}：{r['views']}" + ("" if w.replace(" ", "") in titles.replace(" ", "") else "（標題裡沒有）"))
    sites = rows(d, "outside")
    if sites:
        say("\n**外部網站**：" + "、".join(f"{r['insightTrafficSourceDetail']} {r['views']}" for r in sites[:10]) + "\n")

    say("## 觀眾是誰\n")
    say("| 國家 | 觀看 | 每次觀看分鐘 |\n|---|---|---|")
    thin = []
    for r in rows(d, "country")[:15]:
        mpv = r["estimatedMinutesWatched"] / max(1, r["views"])
        say(f"| {r['country']} | {r['views']:,} | {mpv:.2f} |")
        if r["views"] >= 50 and mpv < 0.1:
            thin.append(r["country"])
    if thin:
        say(f"\n{'、'.join(thin)}：觀看不少但每次不到 6 秒，多半是 Shorts 動態推給看不懂這個語言的人，會拉低完播率。\n")
    aud = defaultdict(float)
    for r in rows(d, "audience"):
        aud[r["ageGroup"].replace("age", "")] += r["viewerPercentage"]
    if aud:
        say("年齡：" + "、".join(f"{k} {v:.0f}%" for k, v in sorted(aud.items())) + "\n")
    dev = rows(d, "device")
    if dev:
        dv = sum(r["views"] for r in dev)
        say("裝置：" + "、".join(f"{r['deviceType'].lower()} {100 * r['views'] / max(1, dv):.0f}%" for r in dev) + "\n")
    sub = {r["subscribedStatus"]: r["views"] for r in rows(d, "subscribed")}
    if sub:
        say(f"已訂閱的人看的：{100 * sub.get('SUBSCRIBED', 0) / max(1, sum(sub.values())):.1f}%\n")

    say("## 每支影片\n")
    say("| 觀看 | 平均看完 | 平均秒數 | 新訂閱 | 線 | 標題 |\n|---|---|---|---|---|---|")
    for r in per:
        v = V.get(r["video"], {})
        say(f"| {r['views']:,} | {r['averageViewPercentage']:.0f}% | {r['averageViewDuration']}/{v.get('secs', 0)} | "
            f"{r['subscribersGained']} | {line(r['video'])[0]} | {v.get('title', r['video'])[:50]} |")
    return "\n".join(out) + "\n"


def main():
    a = sys.argv[1:]
    if not a or a[0] not in ("pull", "report"):
        sys.exit(__doc__)

    def opt(name, default=None):
        return a[a.index(name) + 1] if name in a else default
    if a[0] == "pull":
        print(pull(opt("--since", "2025-01-01"), opt("--until"), int(opt("--curves", 20))))
        return
    files = [x for i, x in enumerate(a[1:], 1) if x.endswith(".json") and a[i - 1] not in ("--md",)]
    path = files[0] if files else max(glob.glob(os.path.join(DIR, "*.json")), key=os.path.getmtime, default=None)
    if not path:
        sys.exit("no pull yet: python dreamfab/youtube_analytics.py pull")
    groups = [a[i + 1].split("=", 1) for i, x in enumerate(a) if x == "--group"]
    text = report(path, groups)
    print(text)
    if opt("--md"):
        open(opt("--md"), "w", encoding="utf-8").write(text)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
