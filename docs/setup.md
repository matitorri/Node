# Setup

The context. It holds or it does not, and it can hold for hours.

Source: `src/setup.pine`.

What it publishes is not a verdict but the V object in play — the region
the signal will be judged against — or nothing. That is what lets one
signal serve every setup: the setup chooses what to look at, the signal
only asks whether it fired.

Each setup declares what it needs from the model, so one that cannot run
says so in the diagnostics instead of quietly never firing.

## M touch

Price entering an M object puts that region in play. A later touch on a
different one takes its place: the most recent is the one being traded.

It lets go when the region stops existing — price absorbs it, or it
expires untouched — or when the session turns over. Everything downstream
goes with it: no region, no signal, no order.

That release is read on the **bar**, not on the grid. A slice is published
once every five minutes, so on an M1 chart a region would stay in play for
four more after price took the edge it lives off, and a change of
character inside that window traded something already gone.

And an absorbed region is never taken up again. Price on its way out of a
region is inside it, so the slice that kills one also reports a touch on
it; without that guard the setup re-armed on the corpse.

It does **not** let go when a target is reached. The setup sits above the
strategy and cannot see a position. Keeping a second trade from opening
while one is live belongs to the position manager.

Touches outside the trading hours are ignored. The filter is here and not
only in the portfolio because the arming moment matters: without it, a
touch at three in the morning would sit armed and fire on a change of
character at ten.

**Needs** M objects to be enabled.

## The touch is an event

The model latches it on the region itself. The setup asks whether a region
**has been** touched, not whether price is inside one now: without the
event there is no setup, and after it there is one whether price is in or
out.

Three readings were tried before this one, and the two that failed are
worth keeping:

**The first touch of a region's life**, raised on the transition that
freezes its box. A touch at three in the morning was rejected by the
trading hours and spent it, and the region went on living for days with no
way left to arm anything.

**Being inside the region right now**, published every five-minute slice
it held. An M object is as wide as the H4 candle it came from — four or
five hundred points is ordinary — so a region that contained price
overnight armed the setup at the open of every day, with price having done
nothing at all.

The latch has neither problem: the event is recorded whenever it happens,
and the trading hours decide when a region so marked may be taken up.

The most recent qualifying region wins. A newer one replaces whatever the
setup was holding.
