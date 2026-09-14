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

## The three scripts

A Pine file can only be one script type, so a strategy has to be its own
script. Rather than keep copies of the model, `build.py` assembles each
one from the same parts:

| part | indicator | strategy | audit |
|---|---|---|---|
| `model.vobjects` | ✓ | ✓ | ✓ |
| `model.structure` | ✓ | ✓ | |
| `setup` | ✓ | ✓ | |
| `signal` | ✓ | ✓ | |
| `diagnostics` | ✓ | ✓ | |
| `output` | ✓ | ✓ | |
| `indicator.tail` | ✓ | | |
| `strategy` + `portfolio` | | ✓ | |
| `audit.tail` | | | ✓ |

**Indicator** draws the model. What it keeps to itself is a single line:
`alertcondition` is not allowed in a strategy.

**Strategy** draws the same model and trades it. What it keeps to itself
is the book.

**Audit** carries the V objects and nothing else — no structure, no setup,
no signal — and keeps every region the model has held, after the model has
let go. The other two show what is in play; this one shows where things
were, so a day can be found before it is checked.

Everything shared is identical in all of them, byte for byte.

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

Versions follow semver and live in the script title, `Node - v1.0.0`.
Work in progress carries `-dev` until a batch is closed; closing one
tags the commit and publishes a GitHub release.

**1.0.0 is about the implementation, not the edge.** It says this is the
finished TradingView build of Node: the model, one setup, one signal, one
strategy and the book, documented, with a record of what it did. It does
not say the edge is proven, and the sample it rests on could not prove it
— see [performance](performance.md#the-size-of-the-sample).

Changes are recorded in git, not in the files. There is no changelog
header in any source.

## Branches and layouts

A major version is developed whole, not assembled feature by feature.

`main` is what runs. Every commit on it is a commit that can be pasted
into TradingView, and it is tagged at each version. The next major
version is developed on a branch of its own — `v2` — which merges into
`main` once, when it is finished, and is deleted at the merge. The tag is
what survives.

Each branch has a TradingView layout to match: **production** carries the
script built from `main`, **development** the one built from the branch.
Nothing else is loaded on production. The script title, which carries the
version and the `-dev` suffix, is the only thing on the chart that says
which one is open.

Bugs found in production are fixed on `main`, released as a PATCH, pasted
into the production layout, and then merged from `main` into the branch
the same day. That direction only. A fix that is not carried across is a
fix that the next major version silently ships without, and the merge
at the end will ask about it in a conflict, long after anyone remembers
the answer.

Promoting a version is a procedure, not a merge: paste the new script
into the production layout, recreate the alerts against it, and only then
remove the old ones. Alerts belong to the script they were created from;
replacing the script does not move them.
