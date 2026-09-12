# Portfolio

The last word: how much, and whether at all. It reads the intention the
strategy published and turns it into an order, or refuses it.

Source: `src/portfolio.pine`. Strategy only — there are no positions to
manage in an indicator.

Two blocks, kept apart because they answer different questions and are
told different things. Neither reaches into the other: a change in how
risk is taken leaves the gates alone, and a new gate leaves the sizing
alone.

## Risk management

How much this position may lose, and therefore how large it may be. It is
shown one trade and nothing else — not what is already open, not how the
day has gone, not how many trades have been taken. None of that changes
what a single position may lose.

```
riskBudget      = equity × percent ÷ 100   or   a fixed amount
riskPerContract = |entry − stop| × syminfo.pointvalue
riskSize        = floor(riskBudget ÷ riskPerContract), capped
```

**The budget** is either a percentage of equity or a fixed amount of
account currency.

**The equity** is either the current equity, which compounds — the
position grows after a win and shrinks after a loss — or the initial
capital, which keeps the risk flat whatever the account has done since.
Idle under a fixed amount.

**The cost of a contract** comes from the instrument: a point of price is
worth `syminfo.pointvalue`, so nothing here is specific to one symbol.
MNQ happens to be two dollars a point.

**The rounding is always down.** Rounding up would quietly spend more
than the budget just declared, which is the one thing this block exists
to prevent. A budget that does not cover a single contract therefore
means no position rather than a smaller one: there is nothing smaller
than one contract.

**The ceiling** is a hard maximum applied after the budget has spoken. It
never raises a size, only caps one.

## Position management

Whether this one may be opened, read off the book and the day rather than
off the trade. It never sizes anything and never looks at where the stop
is: given the same book it answers the same, whatever the signal was.

Three gates.

**Room.** A signal arriving while the book is full is ignored — not
queued, not stacked on what is running. Nothing is taken later on its
behalf.

**The day.** A count of trades closed since the session opened, against a
limit on each side: two losses or one win end it by default. Only the
session opening brings it back. Counting trades rather than money bounds
the day at a known number of attempts regardless of what each one was
worth; with those defaults the longest possible day is two trades.

Profit is measured net of commission, so a trade scratched to the tick
lands on the losing side rather than in a third category that neither cut
would ever see.

**The clock.** The shared trading hours, so the setup and this block can
never disagree on when the system is at work. Read on the chart bar,
since that is where an order would be placed.

All three gate **opening**. The day ending or the book filling leaves a
position already running alone.

There is one rule about **holding**, and it is here for the same reason
the gates are: the strategy cannot see a position. Nothing is carried
past the trading hours. A target may never be reached, so the hours
closing is what ends a position that is still going — an exit by time,
always on.

## Reading the trade list

`pmWins` and `pmLosses` are cleared when the session turns over.
`pmRead`, the cursor into TradingView's closed-trade list, is not: it is
cumulative over the whole backtest, and resetting it would count old
trades again.

## Orders

Where the two blocks meet, and the only place that talks to TradingView.
Nothing is decided here: the intention comes from the strategy, the size
from risk management, the permission from position management.

An entry is placed when all three agree — a direction, a permitted book,
and a size of at least one contract.

The loss and the target are copied when the position opens and held for
as long as it lasts, so the exit does not start following levels a later
signal would have used. A target that is `na` leaves the stop alone to
work; the position then ends on the loss or on the hours.
