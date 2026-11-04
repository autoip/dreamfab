# 美股一分鐘（試播）：每天台股開盤前，一分鐘看懂昨晚美股。news/make.py 讀這個檔
# A one-minute US-markets brief for Taiwan, before the Taiwan open (pilot). Read by news/make.py.
NAME = "us_stocks"                              # out/us_stocks_20261103.mp4
BRAND = ("美股", "1分鐘")                        # the bar at the top: a tag and a title
ANCHOR = "cast/ANCHOR_A.png"                    # v4 text-to-image 540x960 (see the overview: starting a show)
VOICE = "voices/ANCHOR_A.wav"                   # her line from an image-to-video, the clean part only
MUSIC = "music/theme.mp3"                       # generated in Suno from music/suno.md
MUSIC_LOOP = (4.04, 18.04)                      # whole bars that may repeat (120 bpm: 2 s a bar); before = intro
OPEN = ("台股開盤前 1 分鐘", "昨晚美股發生什麼事？")    # the strap over the anchor at the start
CLOSE = ("本新聞由以下平台獨家贊助", "autoip.ai")       # ... and at the end
SPONSOR = dict(kicker="本新聞由以下平台獨家贊助", name="autoip.ai", sub="美股一分鐘　每天台股開盤前")
FIRST_LINE = "早安，台股開盤前，一分鐘看懂昨晚美股。｜早安，台股開盤前，一分鐘看懂昨晚美股｜anchor"
LAST_LINE = "以上是一分鐘美股，本新聞由AutoIP點AI平台獨家贊助。｜以上是一分鐘美股，本新聞由 autoip.ai 平台獨家贊助｜anchor"
SEO_TAGS = ["美股", "台股", "美股新聞", "財經新聞", "台股開盤", "費半", "台積電ADR", "美股一分鐘"]
SEO_FOOT = "🔔 記得訂閱，每天台股開盤前看美股一分鐘，養成習慣，掌握財金動脈\n📈 美股一分鐘：每天台股開盤前，一分鐘看懂昨晚美股\n本新聞由 autoip.ai 平台獨家贊助"
# the call to subscribe, said last by the anchor, with its own strap; the end card leads with it
CTA_LINE = "記得訂閱，每天開盤前看美股一分鐘，養成習慣，掌握財金動脈！｜記得訂閱，每天開盤前看美股一分鐘，養成習慣，掌握財金動脈｜anchor"
CTA = ("🔔 記得訂閱", "養成習慣・掌握財金動脈")
SUBSCRIBE = dict(button="訂閱", line="每天台股開盤前看美股一分鐘<br>養成習慣，掌握財金動脈")
COVER_FRAME = 0.3                               # the first 0.3 s of the video is the cover
# upload: the channel and its own login (docs SETUP); PRIVACY "public" publishes at once, unset = private
# CHANNEL = "UC..."
# YT_TOKEN = a login file of this channel's own (docs SETUP: a second channel)
# PRIVACY = "public"
CATEGORY = "25"                                 # News & Politics
# every weekday with no one there (news/make.py schedule, then daily): skipped when it starts after `latest`
# DAILY = dict(at="06:30", days="mon-fri", latest="08:30")
# words the voice misreads: a same-length, same-sounding swap, read only (the subtitle keeps the word)
SAY = [("光纖", "光仙"), ("供給", "供擠"), ("叢集", "從集"), ("瓶頸", "瓶錦"), ("重啟", "崇啟"), ("銦", "因"), ("〇", "零")]
