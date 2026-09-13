# Node

A trading system for CME futures, written in Pine Script v6 and run on
TradingView.

One model, three scripts. `dist/node_indicator.pine` draws the model on a
chart, `dist/node_strategy.pine` trades it, and `dist/node_audit.pine`
keeps every region the model has ever held so past days can be found
without walking back through them. All three are assembled from the same
sources in `src/`, so none can drift from the others.

## Using it

```
python3 build.py
```

Then paste the artifact you want from `dist/` into the TradingView Pine
editor. Edit `src/`, never `dist/` — the artifacts are generated, and are
committed only so the repository holds exactly what ran on a chart.

## Layers

```
model > setup > signal > strategy > portfolio
```

Each is a section of the code and a file of its own. The model describes
the market; the setup decides what is worth watching; the signal fires;
the strategy says what to do about it; the portfolio decides how much, and
whether at all.

## Backtesting

TradingView deep-backtests fifteen days at a time, so a run arrives as a
pile of exports in `Performance/`. `python3 performance.py` merges them
into `Performance/trades.csv` and reports what they add up to. See
[docs/performance.md](docs/performance.md).

## Documentation

The reasoning lives in [docs/](docs/), one page per layer. Start with
[docs/architecture.md](docs/architecture.md).
