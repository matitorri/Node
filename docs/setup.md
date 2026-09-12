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
expires untouched — or when the session turns over.

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
to see it happen — it is the code walking the slices while price is in
the region. It publishes `slTouch`, one entry per grid slice, holding the
object price is inside on that slice or nothing.

It is published for as long as price holds the region, not once. Freezing
the box is a separate, one-time drawing matter, and while the two were
tied together an M object had exactly one chance to arm a setup — its
first touch ever. A touch at three in the morning, rejected by the
trading hours, spent it; so did a touch on a day the setup then let go of
at the session turnover. Either way the region went on living for days
without ever being tradable again.
