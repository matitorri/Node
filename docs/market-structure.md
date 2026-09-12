# Market structure

A pattern object, and a peer of the V objects rather than a part of them.
It holds the two levels the structure stands on, the direction they imply,
and the sequence of points that produced them.

Source: `src/model.structure.pine`.

Read on M1 whatever the chart is on, and unaware of the V objects:
crossing the two is the setup's job, not the model's.

## Candidates

Local extremes, one candle either side, no parameter. They are dense on
purpose.

## Reduction

What thins the candidates out is a **level**, never a size.

Going up, a candidate high is structural only if it exceeds the last
structural high. Everything that fails to is dropped, however large it
looked, and the structural low of the interval is simply the lowest
candidate low in it. A leg that makes no new high therefore leaves no
marks at all, which is why a clean advance reduces to a single line
between its two ends.

Going down, the mirror.

This is worth stating because every plausible alternative measures size —
a minimum retracement in points, a percentage of the leg, an ATR
multiple, a pivot lookback — and all of them read the structure wrong.
The rule measures levels.

## Change of character

Price taking a level out: the last structural low while going up, the
last structural high while going down. Reaching through it is enough — a
wick counts.

Requiring a close beyond the level was implemented and tried. It read the
structure noticeably worse and was reverted.

## Why request.security

The machine runs on the M1 series through `request.security` rather than
by splitting chart bars. Intrabar requests are capped at a few thousand
bars; a state machine running on a lower-timeframe series is not, so the
whole history is available.

## Output

A qualifying candidate brings in two points at once: itself, and the
extreme of the interval it just closed. Both are handed back in order, so
the drawing side can consume them as a path.

Published: the phase, the two levels, a count of points, the two point
slots, and the change of character — its count, direction and time.
Disabled, the model publishes nothing, and everything downstream reads
that as silence rather than as a false reading.

## lab/structure.pine

A scratch indicator outside the build, running the same reduction rule on
chart bars with candidate circles, a zigzag, HH/HL/LH/LL labels and CHoCH
triangles. Kept for fast iteration on the rule itself.
