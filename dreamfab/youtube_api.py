"""YouTube Data API login and helpers shared by every uploader (drama/youtube_upload.py, mv/youtube_upload.py) and
dreamfab/youtube_playlists.py; analytics() for dreamfab/youtube_analytics.py (YouTube Analytics API, read only).

Credentials: YT_CLIENT_SECRET = an OAuth client of type "Desktop app" (default
~/.config/dreamfab/youtube_client_secret.json; ~/.config/dreamfab/ from before the merge is still read when the
new folder has none); the login is cached next to it as youtube_token.json. Keep both outside the repo.
YT_TOKEN (optional) = another file for the login, so a second channel keeps its own (e.g.
~/.config/dreamfab/youtube_token_news.json); the first channel's login is left alone.
YT_CHANNEL_ID (optional) = the only channel a script may act on.
"""
import os, sys, time

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]
ANALYTICS = "https://www.googleapis.com/auth/yt-analytics.readonly"   # only asked for by analytics(): uploads keep working
                                                                      # on a login made before it


def _secret():
    if os.environ.get("YT_CLIENT_SECRET"):
        return os.environ["YT_CLIENT_SECRET"]
    for d in ("dreamfab", "autoip-mv-maker"):   # the second: where the MV and drama tools kept it before the merge
        p = os.path.expanduser(f"~/.config/{d}/youtube_client_secret.json")
        if os.path.exists(p):
            return p
    return os.path.expanduser("~/.config/dreamfab/youtube_client_secret.json")


SECRET = _secret()
TOKEN = os.path.expanduser(os.environ.get("YT_TOKEN") or os.path.join(os.path.dirname(SECRET), "youtube_token.json"))


def _creds(scopes):
    """The saved login when it covers `scopes` (refreshed if needed), else a new one in the browser."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    if not os.path.exists(SECRET):
        sys.exit(f"no OAuth client at {SECRET} (docs/*/PUBLISHING.md: automatic upload)")
    creds = Credentials.from_authorized_user_file(TOKEN) if os.path.exists(TOKEN) else None
    if creds and not creds.has_scopes(scopes):
        print("  the saved login does not cover", ", ".join(s.rsplit("/", 1)[-1] for s in scopes if s not in (creds.scopes or [])))
        creds = None
    if creds and not creds.valid and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:   # revoked, or a consent screen left in Testing (logins expire after 7 days)
            print("  login expired:", e)
            creds = None
    if not creds or not creds.valid:
        print("  log in with the channel's Google account (if the account owns several channels, pick the right one);")
        print("  if no browser opens, open the URL below in a browser on this computer")
        creds = InstalledAppFlow.from_client_secrets_file(SECRET, scopes).run_local_server(port=0, prompt="consent")
        with open(TOKEN, "w") as f:
            f.write(creds.to_json())
    return creds


def youtube():
    from googleapiclient.discovery import build
    return build("youtube", "v3", credentials=_creds(SCOPES))


def analytics():
    """YouTube Analytics API v2 (views, watch time, retention, traffic sources...). The first call logs in again to
    add read-only analytics to the saved login; the Google Cloud project needs the YouTube Analytics API enabled."""
    from googleapiclient.discovery import build
    return build("youtubeAnalytics", "v2", credentials=_creds(SCOPES + [ANALYTICS]))


def channel(yt, lock=False, expect=None):
    """Print the logged-in channel; with lock=True exit unless it is `expect` (an upload plan's channel) or
    YT_CHANNEL_ID, whichever is set."""
    ch = yt.channels().list(part="snippet,contentDetails", mine=True).execute()["items"][0]
    print(f"  channel     {ch['snippet']['title']} ({ch['id']})")
    try:   # the library names the channel by it; never stop an upload over that
        from dreamfab.youtube_log import remember_channel
        remember_channel(ch)
    except Exception as e:
        print(f"  (channel name not kept: {e})")
    want = expect or os.environ.get("YT_CHANNEL_ID")
    if lock and want and ch["id"] != want:
        sys.exit(f"  !! logged in to channel {ch['id']}, expected {want}: delete {TOKEN} and log in again, "
                 "picking the right channel")
    return ch


def wait_until(check, what, timeout=45, step=3):
    """Reads lag a few seconds behind writes: poll check() until it is true. Returns False (and says so) on timeout."""
    end = time.time() + timeout
    while True:
        if check():
            return True
        if time.time() > end:
            print(f"  !! {what}: still not visible after {timeout} s; check in YouTube Studio")
            return False
        time.sleep(step)


def in_playlist(yt, pid, vid):
    return bool(yt.playlistItems().list(part="id", playlistId=pid, videoId=vid).execute()["items"])
