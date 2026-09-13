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
running figures once.

The result is `Performance/trades.csv`: what the run adds up to at the top,
every trade below it. After that it is the only place to read the backtest
from — the exports stay as raw material, and nothing derived lives anywhere
else. The same computation feeds the file and what is printed, so the two
cannot disagree.

`script` names the build. It is read from `src/strategy.head.pine` rather
than from the exports, whose title is whatever the script was called when
it ran and lags a version bump; `--label` is there for a backtest of
something older.

## What it can and cannot tell you

**Drawdown is on closed trades.** Nothing intrabar reaches the export, so
the real fall was deeper than the number here.

**Gaps are invisible.** An export carries trades, not the window it came
from, and a window that produced nothing produces no file. A missing
fortnight and a quiet one look the same, and `windows` counts the exports
that held a trade, not the windows that were run.

**The windows each start at the declared capital.** With risk measured
against *Initial capital* the sizes are what a continuous run would have
used and the merge is faithful. Against *Current equity* they are not: each
window sized as though the account had never moved, and the merged sequence
is a run that never happened.

**The trades are the trades of the build that produced them.** The exports
carry the script's title, so check it against the version you mean to be
judging.
