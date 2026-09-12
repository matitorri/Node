# Node

A trading system for CME futures, written in Pine Script v6 and run on
TradingView.

One model, two scripts. `dist/node_indicator.pine` draws the model on a
chart; `dist/node_strategy.pine` trades it. Both are assembled from the
same sources in `src/`, so the strategy cannot drift from what the
indicator shows.

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

## Documentation

The reasoning lives in [docs/](docs/), one page per layer. Start with
[docs/architecture.md](docs/architecture.md).
