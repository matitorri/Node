# Architecture

## The layers

```
model > setup > signal > strategy > portfolio
```

**Model** describes the market and decides nothing. It publishes objects:
regions left by volume, and the structure price is drawing. It knows
nothing about trading.

**Setup** is the context. It holds or it does not, and it can hold for
hours. What it publishes is not a verdict but the object in play — the
region the signal will be judged against — or nothing. That is what lets
one signal serve every setup: the setup chooses what to look at, the
signal only asks whether it fired.

**Signal** is the trigger, inside a valid setup. Instantaneous, where the
setup is a standing condition. It is common to every setup, which is why
it sits beside them rather than inside one.

**Strategy** is the trade idea: which way, where in, where out. It
publishes an intention, not an order, and knows nothing about money.

**Portfolio** has the last word: how much, and whether at all. It reads
the intention and turns it into an order, or refuses it.

The order is not decorative. Each layer may read the ones above it and
none of the ones below. A setup cannot see a position; a strategy cannot
see the book.

## The two scripts

A Pine file can only be one script type, so a strategy has to be its own
script. Rather than keep two copies of the model, `build.py` assembles
both from the same parts:

| part | indicator | strategy |
|---|---|---|
| `model.vobjects` | ✓ | ✓ |
| `model.structure` | ✓ | ✓ |
| `setup` | ✓ | ✓ |
| `signal` | ✓ | ✓ |
| `diagnostics` | ✓ | ✓ |
| `output` | ✓ | ✓ |
| `indicator.tail` | ✓ | |
| `strategy` | | ✓ |
| `portfolio` | | ✓ |

Both scripts draw the model — a strategy that cannot show the structure it
trades is not worth watching. What the indicator keeps to itself is a
single line: `alertcondition` is not allowed in a strategy. What the
strategy keeps to itself is the book.

Everything shared is identical in both, byte for byte.

## Ordering constraints

Pine is sequential: a variable must be declared before it is used, and
there are no modules. Two consequences show up in the source.

The **settings dialog** lists groups in the order their first input is
declared, and Pine has no nested groups. The hierarchy is therefore
spelled out in the group names and held by where each block sits:

```
Common
Objects · V objects
Objects · Pattern objects
Setups
Portfolio · Position management
Portfolio · Risk management
```

The **trading hours** are read by both the setup and the position
manager, so they are declared once, above both. Since the portfolio is
built after the setup and only reaches the strategy, the declaration sits
in `setup.pine` — carrying the position manager's group, which is whose
policy it is. It sits there and not earlier only so that the Portfolio
section does not open above the model in the dialog.

## One account, not two

The model is the only source. Anything drawn is derived from it, in one
place, from state — never written alongside the logic that changed the
state. A chart that cannot say something the model does not is a chart
that shows a bug instead of hiding one.

See [the drawing pass](v-objects.md#drawing) for what that looks like.

## Conventions

Code and comments are written in English.

Versions follow semver and live in the script title, `Node - v0.16.0`.
Work in progress carries `-dev` until a batch is closed; closing one
tags the commit and publishes a GitHub release.

Changes are recorded in git, not in the files. There is no changelog
header in any source.
