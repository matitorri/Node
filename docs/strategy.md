# Strategy

What to do about it: which way, where in, where out. One trade idea, and
nothing about money — how large the position may be is decided by the
portfolio, where the rest of the book is visible.

Source: `src/strategy.pine`.

It publishes an intention, not an order:

| | |
|---|---|
| `tradeDir` | `+1` long, `-1` short, `0` nothing to do on this bar |
| `tradeEntry` | the price it wants in at |
| `tradeStop` | where the idea is wrong |
| `tradeTarget` | where it is done |

Several strategies could sit on the same setup and the same signal and
differ only in those four, which is why the boundary is kept.

## Status

Empty. The contract is declared and nothing fills it, so
`riskPerContract` is `na` and the portfolio sizes every position at zero.
The strategy script compiles, draws the model and takes no trades.

Still to be specified: whether entry is at market on the change of
character or on a limit somewhere in the region, where the stop goes, and
where the target goes.
