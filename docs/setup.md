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

## The touch channel

The touch is an event, and only the M object's lifecycle is in a position
to see it happen. It publishes `slTouch`, one entry per grid slice, holding
the region price entered on that slice or nothing. When price enters two at
once the newest claims the slot.

It is published **once**, on the same transition that ends the region's box.
A region that has been touched is done: it offers itself to no setup again,
and stays on the books only so price can still be caught absorbing it.

Publishing it every slice price held the region was tried, to keep a touch
outside the trading hours from spending a region. An M object is as wide as
the H4 candle it came from, and one wide enough to contain the whole day's
range then went on arming the setup for as long as it lived — with its box
finished days earlier. The chart said the region had ended; the model
carried on using it. One fact, drawn one way and read another.

The problem it was meant to solve is gone anyway: a region is not touchable
between 18:00 and the next New York open, so a touch at three in the
morning cannot happen at all.
