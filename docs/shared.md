# Shared machinery

Constants, inputs, the evaluation grid and the clock every object reads.
Nothing here belongs to one of them alone.

Source: `src/model.vobjects.pine`, first half.

## The instrument

Node is for futures, CME in particular, and the day is the exchange
session rather than midnight. The session opens at 18:00 ET and closes at
17:00 ET; New York opens at 09:30 ET.

## The evaluation grid

Every judgement — the clock, a touch, an absorption, a New York candle —
is made on five-minute slices instead of on chart bars, so a session
produces the same objects whatever timeframe is on screen.

Charts coarser than the grid are split into their five-minute intrabars
through `request.security_lower_tf`. Finer ones are gathered into
five-minute buckets and read out whole when the bucket closes.

A chart timeframe that does not divide five minutes cannot line up with
the grid, and the script says so on the chart.

This buys timeframe independence for everything the model draws. It does
not buy it for execution: a strategy's fills are still resolved on chart
bars, so a backtest on H1 cannot know whether the stop or the target was
reached first inside a bar.

## The New York clock

Resolved per slice, into parallel arrays:

- `slOpen` marks the first slice at or past 09:30 ET. It closes an M
  object's trim window and gives birth to an ID object.
- `slNewSess` marks the first slice of a new exchange session, 18:00 ET.
  It reopens the trim window of an M object still untouched.
- `slInNy` covers the New York stretch, 09:00 to 17:00 ET.
- `slSkip` marks the sessions named in the skip list.
- `slEvt` is raised by whichever object price absorbs, and read by the NY
  ID object. A pulse per slice, not a latch held for the session.

The open detector is bounded at **both** ends. Without the upper bound, a
Sunday reopen at 18:00 ET counts as an opening: it is the first trade of
that New York day and sits well past 09:30. That produced an orphaned ID
box every Sunday.

## Session opening

`sessionOpened()` reads 18:00 ET off the clock.

It was once `timeframe.change("D")`, which around a holiday can run for
days without reporting a change. Every per-session reset hanging off it
froze silently: the volume winner never reset, the pre-New-York window
never cleared, and objects from the old session stayed on the chart. The
diagnostics table made it provable — the last turnover read four days
older than the bar being drawn.

Each call site keeps its own state, so the same function serves both
series it is used on.

## Skipped sessions

A hard calendar filter, not a statistical one. Holiday half sessions
still open a daily bar, so they would produce objects on a fraction of
the usual volume. They are named by date in an input, parsed once into
`YYYYMMDD` numbers; separators are stripped, so `2025-11-28` and
`20251128` both work.

A listed session is sat out **entirely**: no objects are created and no
setup arms, so nothing downstream can fire. Skipping only the objects
left the day trading regions built the day before.

The date is the session's **closing** day, and a session opens at 18:00
the evening before — so the filter compares session dates, not calendar
dates. Comparing calendar dates let the evening hours of a skipped
session through, which is half of it.

Full closures need no entry. There are no bars, so there is nothing to
draw.

The diagnostics say how many dates were read and whether the session on
screen is one of them, which is the only way to tell a typo from a rule.

## Trading hours

When the system is allowed to work. Declared once and read by two layers:
the setup will not arm a region outside them, so a touch at three in the
morning cannot sit waiting to fire at ten, and the position manager will
not open a position outside them either.

New York time, not the chart's timezone.

Declared in `src/setup.pine` for a reason that is only about the settings
dialog — see [architecture](architecture.md#ordering-constraints).
