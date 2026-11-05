Today is {DATE} (local time). The system scheduler started you and no one is watching: ask nothing, finish, then stop.

Task: make today's episode of the show in {SHOW} with Dreamfab's news line, and upload it as that show's series.py says.
- The user approved this standing run when they scheduled it: today's jobs (narration, lip-sync, one re-read, and the
  cover's picture when the show's days have one) and the upload at series.py's PRIVACY. Nothing beyond that: no other
  channel, no other privacy, no extra jobs.
- Work only in {SHOW}. No commit, no push; leave every other project alone.
- Never read, print or write API keys or login files.

## Setting up
- Run commands from the repo root. Python: `{PY} -X utf8` (add `< /dev/null`). PYTHONIOENCODING=utf-8 and AIP_MAX=1
  are set.
- Read skills/dreamfab-news/SKILL.md and docs/en/news/OVERVIEW.md first; copy the format of the last day's day.py and
  script.md.

## Steps
0. Is there news today? If the market the show covers did not open (weekend, holiday), make nothing: write one line
   with the reason in {SHOW}/daily_log.md and stop.
1. `news/make.py new {SHOW} {DATE}`
2. Research: primary and English sources first, the searches sent together; every number from two sources that agree
   (when they do not, a quote page's historical close decides). A number with no second source stays out.
3. script.md and day.py (SOURCES, CARDS, COVER, SEO) as the skill says; then `cards`, `cover`, `seo`, and look at the
   cards and the cover: no text running out of its box.
   - When the last day's day.py has COVER_HERO, the show's covers have their own picture: write today's (the day's
     biggest story as one image in English prose, rising in red light and falling in green for a Taiwanese audience;
     no text, logos, real people or flags; the subject in the middle), then `hero` → `submit DAY hero --off-peak`
     before `cover`. A subject hidden by the box at the bottom: COVER shift=40 or so moves the picture up.
4. `voice` → `submit DAY voice --off-peak` → `check`.
   - A word read wrong (`check` lists it; an English name the recogniser writes another way does not count): put a
     same-length swap in common characters that sound the same into series.py's SAY, then `redo DAY FIRST LAST` →
     `submit DAY redo --off-peak` → `splice DAY FIRST LAST` for those lines. Do it without holding back on credits,
     but once only: no second round. Whatever still sounds off goes in the log for the user to listen to.
   - The narration cut off at the end (the last words missing in `check`; every job ends with a throwaway line that
     `check` cuts off by itself, so this is rare): re-read the last line the same way.
5. `anchor` → `submit DAY lipsync --off-peak` → `render`; look at a few frames (the cover, the anchor, cards, the end).
6. `upload DAY`.
7. Append to {SHOW}/daily_log.md: the date, the link, the length, the credits spent, minutes per step (timing.tsv),
   the words changed in SAY, the spots to listen to, and anything that went wrong.

## When something fails
- Retry a failed step once. If it fails again, stop and write in daily_log.md the step and the error message.
- Never upload a half-made video.
