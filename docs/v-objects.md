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

**Touched** means price is inside the region. The first time it happens
the box stops projecting to the right and freezes there, but the region
stays on the books and every later visit counts as a touch too — the
frozen box is a drawing, not a state the region has left.

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

**Lifetime.** Counted from the source candle, three days by default. An
untouched M object is removed when it expires. A touched one stays on the
books until it expires or is absorbed.

**Half sessions** produce no M object. They open a daily bar but trade a
fraction of the usual volume, so the winner means nothing.

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
