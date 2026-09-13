# Performance

TradingView will only deep-backtest fifteen days at a time, so a run comes
back as a pile of exports in `Performance/`. Each one restarts its trade
numbering and its cumulative columns, which makes none of them comparable
and all of them wrong about the whole.

```
python3 performance.py [--capital 50000]
```

It reads every export, pairs the entry and exit rows into trades, drops the
ones two windows both saw, orders what is left by entry, and recomputes the
running figures once. The result is `Performance/trades.csv` — after that,
the only place to read the backtest from. The exports stay as the raw
material.

It then prints what it adds up to: net, profit factor, win rate, the two
averages, expectancy, the deepest fall from a peak, the longest losing
streak, and the two sides separately.

## What it can and cannot tell you

**Drawdown is on closed trades.** Nothing intrabar reaches the export, so
the real fall was deeper than the number here.

**Gaps are invisible.** An export carries trades, not the window it came
from, and a window that produced nothing produces no file. A missing
fortnight and a quiet one look the same.

**The windows each start at the declared capital.** With risk measured
against *Initial capital* the sizes are what a continuous run would have
used and the merge is faithful. Against *Current equity* they are not: each
window sized as though the account had never moved, and the merged sequence
is a run that never happened.

**The trades are the trades of the build that produced them.** The exports
carry the script's title, so check it against the version you mean to be
judging.
