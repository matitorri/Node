# V objects

A V object is a price region left behind by a candle that carried the
volume, held until price takes the edge its side lives off.

Source: `src/model.vobjects.pine`.

Three kinds, differing in the candle they come from and in how long they
last:

| | source candle | trimmed | lives |
|---|---|---|---|
| **M object** | the session's H4 volume winner | yes | days |
| **ID object** | the pre-New-York H1 winner | no | one session |
| **NY ID object** | a New York H1 winner | no | until absorbed |

They share a vocabulary and a type. The trim window and the expiry belong
to M objects alone.

## Vocabulary

**Side** is the direction of the source candle. A bullish candle leaves a
demand region, a bearish one supply. Dojis have no side and are never
candidates: with no side there is no edge to lose.

**Touched** means price entered the region, and it happens once. The box
stops projecting to the right there because the region ends there: it is
offered to no setup again. It stays on the books only so price can still
be caught absorbing it, which is what a NY ID object waits on.

The box and the touch are the same fact. Anything that reads one and draws
the other will eventually disagree with itself, and did.

**Absorbed** means price took the edge the region lives off — a bullish
region dies on its low, a bearish one on its high. Strictly: by a tick,
and a wick counts. The region is gone.

The edge that matters is the far one, because the trim already leaves
price on the side the candle came from.

## M object

The region left by the winning H4 candle of a session.

**Which candle.** The highest-volume H4 candle of the session, found by a
state machine running on the H4 series so the answer does not change with
the chart timeframe. While the session runs the winner can still change
hands, so nothing is drawn: the region is only created once the session
closes and the winner is final.

**The trim.** The window opens at the close of the source candle and runs
to the New York open. What survives is the part of the region price never
visited, on the side the candle came from: a bullish M object keeps the
part below the window's low, a bearish one the part above its high. If
nothing survives, the region was fully absorbed before it could be used
and is dropped.

The window is made of five-minute slices, so the range a region ends up
with is the same on any chart. The **moment** the trim is applied is read
off the bar rather than off the grid: keyed to the slice starting at
09:30, it only landed when that slice was published — five minutes later
on an M1 chart, fifteen on an M15 — and until then the region carried the
night's shape and could not be touched at all.

It happens **again at every session open** the region reaches untouched.
The window reopens when the exchange session does, runs overnight, and
closes at the next New York open, so a region that survives a day comes
back smaller. Between those two moments the region is not touchable —
which is what keeps a visit at three in the morning from settling a box
the day has yet to shape. Trimmed once and left alone, an old region
would be traded at yesterday's edge.

Only a region that has not been touched keeps trimming. Once price has
entered it the box is settled and the range is what it is.

**Lifetime.** Counted from the source candle, three days by default. An
untouched M object is removed when it expires. A touched one stays on the
books until it expires or is absorbed.

**Half sessions** produce no M object. They open a daily bar but trade a
fraction of the usual volume, so the winner means nothing.

A region already alive is not judged on one either: it does not trim,
does not freeze, and cannot be absorbed there. It reaches the next real
session untouched by a day the system sat out.

## ID object

The region left by the highest-volume H1 candle of the window running
from the session open to the New York open. No trim.

**Survivorship.** Every H1 candle of the window is kept until price
absorbs it. The winner is the highest-volume candle *still standing*, so
being absorbed hands the place to the next one down. The winner therefore
reaches the open un-absorbed by construction.

**Lifetime.** Born at the New York open, removed when the session turns
over, touched or not. It does not outlive its day.

## NY ID object

Price absorbing an M object or an ID object during New York is an
**event**. Every event picks the region again: the highest-volume New
York H1 candle standing at that instant — the one still forming included,
read at whatever it has reached by then.

Between events nothing moves. A bigger candle closing in between does not
take the place on its own; it takes it at the next event.

It ends when price absorbs the region in turn, and the session gives no
more.

The candle in progress is accumulated from grid slices rather than
requested, because `request.security` cannot hand back an unclosed candle
on history — and an unclosed candle is exactly what may have to be
picked.

Absorption is measured against the region **as drawn**, not against what
its source candle went on to become.

## Drawing

A V object is painted from its own state, in one pass, on every bar. The
lifecycles change state and nothing else; they never touch a box.

```
left   the source candle
right  where the region stopped projecting, or now if it has not
top    the region's top
bottom the region's bottom
```

The right edge is state like everything else: `na` while the region is
still running, and set by whatever ended it — the touch for an M or ID
object, the absorption for a NY ID one.

Geometry used to be written wherever a lifecycle happened to be: at the
trim, at the touch, at an absorption, on an excluded session. Half a dozen
places that each had to remember to keep the drawing current, and the
chart and the model were two accounts of the same fact rather than one.
They disagreed, and working out which of the two was wrong took longer
than any bug in either.
