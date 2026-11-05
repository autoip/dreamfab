"""What a person decided about a piece, kept apart from where it stands on YouTube: 留下 (keep), 不留 (drop) or 待看
(look at it again). A mark is a row of the shared database (dreamfab/db.py, table marks) keyed by the episode's folder;
nothing is moved or renamed. The library's warehouse shows it on the piece's box next to ▶ / 待上架, and counts it on
its own: 不留 is left out of 待上架 and of the stock's 做好沒上傳, and a piece marked 不留 while still on a line leaves
the line (it was given up, not stuck).

usage: python dreamfab/marks.py keep|drop|review FOLDER [FOLDER ...] [--note "…"]   mark episode folders
       python dreamfab/marks.py clear FOLDER [FOLDER ...]                           take the mark off
       python dreamfab/marks.py list [ROOT]                                         the marks (under ROOT)
In the library a click on the chip at a box's top left goes — → 留下 → 不留 → 待看 → —.
"""
import os, sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # run as a script: the repo root
from dreamfab import db as shared

LABELS = {"keep": "留下", "drop": "不留", "review": "待看"}
CYCLE = ("", "keep", "drop", "review")   # what a click on the chip goes through
TABLE = "CREATE TABLE IF NOT EXISTS marks (path TEXT PRIMARY KEY, mark TEXT, note TEXT, at TEXT)"


def key(folder):
    """The folder as the marks table keys it."""
    return os.path.normcase(os.path.abspath(folder))


def _db():
    con = shared.connect()
    con.execute(TABLE)
    return con


def get_all():
    """{key: (mark, note)}"""
    con = _db()
    try:
        return {p: (m, n or "") for p, m, n in con.execute("SELECT path, mark, note FROM marks")}
    finally:
        con.close()


def put(folders, mark, note=""):
    """Mark the folders (mark "" clears it)."""
    if mark and mark not in LABELS:
        raise ValueError(f"mark is one of {', '.join(LABELS)}")
    con = _db()
    with con:
        for f in folders:
            if mark:
                con.execute("INSERT OR REPLACE INTO marks VALUES (?, ?, ?, ?)",
                            (key(f), mark, note, datetime.now().isoformat(timespec="seconds")))
            else:
                con.execute("DELETE FROM marks WHERE path = ?", (key(f),))
    con.close()


def main(args):
    if not args or args[0] not in (*LABELS, "clear", "list"):
        sys.exit(__doc__)
    cmd, rest = args[0], args[1:]
    if cmd == "list":
        under = key(rest[0]) if rest else ""
        for p, (m, n) in sorted(get_all().items()):
            if p.startswith(under):
                print(f"{LABELS.get(m, m)}  {p}" + (f"  ({n})" if n else ""))
        return
    note = rest[rest.index("--note") + 1] if "--note" in rest else ""
    folders = [f for i, f in enumerate(rest) if f != "--note" and (i == 0 or rest[i - 1] != "--note")]
    missing = [f for f in folders if not os.path.isdir(f)]
    if not folders or missing:
        sys.exit(f"no such folder: {', '.join(missing)}" if missing else __doc__)
    put(folders, "" if cmd == "clear" else cmd, note)
    print(f"{'cleared' if cmd == 'clear' else LABELS[cmd]}: {len(folders)} folder(s)")


if __name__ == "__main__":
    main(sys.argv[1:])
