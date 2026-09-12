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

## M reversion

The only one so far. It runs on the setup and the signal as they stand: a
region in play, touched inside the trading hours, and a change of
character agreeing with its side.

Meant to be run on an **M1 chart**. See [fills](#fills) below for why the
timeframe is part of the specification rather than a preference.

### Execution

At market, on the change of character.

### Loss

The day's extreme on the side the trade is exposed to: a long is wrong
below the day's low, a short above the day's high.

The day is the exchange session, the one that opens at 18:00 ET, and its
extremes are accumulated off the five-minute grid rather than read from a
daily feed — the same day the rest of the model means, and not subject to
the daily series freezing around a holiday.

Fixing the level at execution rather than trailing the session costs
nothing: for a long, the day's low cannot extend without price passing
through the loss first.

If the day's extreme *is* the execution — price is making the low as the
signal fires — there is no distance, and no position is taken.

### Target

Two rules, chosen by input.

**Object** exits at the nearest thing in the way:

- an M object **facing** the trade — opposite side, still alive, beyond
  the execution — at its near edge, the one price reaches first;
- the day's extreme on the other side, if it is still ahead of the
  execution. This leg can be switched off, leaving only the M objects.

Whichever is nearer wins. If neither exists the target is empty and the
position ends on the loss or on the hours.

**R multiple** exits at a fixed multiple of the distance from the
execution to the loss.

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
