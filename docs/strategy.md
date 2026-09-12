# Strategy

What to do about it: which way, where in, where out. One trade idea, and
nothing about money — how large the position may be is decided by the
portfolio, where the rest of the book is visible.

Source: `src/strategy.pine`.

It publishes an intention, not an order:

| | |
|---|---|
| `tradeDir` | `+1` long, `-1` short, `0` nothing to do on this bar |
| `tradeExec` | the price it wants in at |
| `tradeLoss` | where the idea is wrong |
| `tradeTarget` | where it is done |

Several strategies could sit on the same setup and the same signal and
differ only in those four, which is why the boundary is kept.

## Structure

A strategy is three components, one code block each, in the order they
decide: **execution**, **loss**, **target**. Each block owns what it
publishes, reads only what the blocks above it published, and may veto
them — a loss with no distance withdraws the execution. Nothing reaches
back up.

The day's extremes are measured before all three, since two of them read
it. That is a measurement, not a component.

## M reversion

The only one so far. It runs on the setup and the signal as they stand: a
region in play, touched inside the trading hours, and a change of
character agreeing with its side.

Meant to be run on an **M1 chart**. See [fills](#fills) below for why the
timeframe is part of the specification rather than a preference.

### Execution

At market, on the change of character.

### The day's extremes

Both the loss and the object target are the session's extreme quotes, so
they are worth stating once.

The day is the exchange session, the one that opens at 18:00 ET, and the
extremes are read straight off the chart against a clock of their own.

They are **not** reset on `isNewSession`. That comes from the H4 feed,
which reports a turnover at the close of the candle that opened the
session — four hours late. The extremes then belonged to a day running
22:00 to 22:00, which is nobody's day, and the loss was placed against
it.

They are not accumulated off the five-minute grid either. A slice is only
published when its bucket closes, so on an M1 chart the extremes would
trail the signal by up to four minutes and miss a low price just made.

The session is turned into a plain calendar date by pushing 18:00 ET to
midnight, which handles daylight saving without a special case.

### Loss

The extreme the trade is exposed to: a long is wrong at the cheapest
quote of the day, a short at the dearest.

Fixing the level at execution rather than trailing the session costs
nothing: for a long, the day's low cannot extend without price passing
through the loss first.

If that extreme *is* the execution — price is making the low as the
signal fires — there is no distance, and no position is taken.

### Target

Two rules, chosen by input.

**Object** exits at the day's other extreme: a long at the dearest quote
of the session, a short at the cheapest. The two levels therefore bound
the trade on both sides.

**R multiple** exits at a fixed multiple of the distance from the
execution to the loss.

An object target that is not ahead of the execution — price making the
day's high as a long fires — leaves the target empty, and the position
ends on the loss or on the hours.

### Time exit

Always on, and it lives in the [portfolio](portfolio.md#position-management)
rather than here: the strategy cannot see a position, and closing one is
the book's business. Nothing is carried past the trading hours.

## Fills

TradingView resolves orders on chart bars. When the loss and the target
both fall inside one bar, the engine cannot know which was reached first
and assumes the worse. On M1 that window is a minute; on H1 it can decide
the backtest.

A market order also fills at the **open of the next bar** by default, not
at the close of the bar that produced the signal. On M1 that is a minute
of slippage against the price the sizing was computed from. Turning it
off — `process_orders_on_close` — fills at the signal bar's close
instead, which flatters the result rather than improving it.
