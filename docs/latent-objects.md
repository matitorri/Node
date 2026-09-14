# Latent objects

A latent object is a broken level waiting to be retested. It is born when
price closes through a level that had held, it occupies a zone at that
level, and it lives only as long as the retest is still worth waiting for.

Latent objects are a family. The one built here is the **break and retest**
subfamily; the name leaves room for others.

## The life

A level does not become an object the moment a candle leaves it. It has to
earn the right, and the object that follows has a deadline.

```
a closed candle leaves its high (and its low)

      │  A  — candles the level must survive unbroken
      ▼
QUALIFIED LEVEL

      │  C  — candles it waits for its break
      ▼
LATENT OBJECT            zone = [high − n, high]

      │  candles it stays latent: what is left of its class,
      │  and never fewer than B
      ▼
  ACTIVE
```

Anywhere the clock runs out, the level or the object dies. A level that is
broken before it qualifies never becomes an object at all: it was not a
level yet, so nothing broke.

## Vocabulary

**Broken** means a candle closed beyond the level. Not a wick through it —
a close. The subfamily is break *and retest*, and price has to be on the
other side for a retest to be a retest.

**Qualified** means the level survived `A` candles unbroken. This is what
separates a level from any other high: not where it sits, but that it held.

While a level is still qualifying, a wick through it does not break it —
it **replaces** it. The wick's extreme becomes the level, the clock starts
again, and the old one is discarded. A level is the furthest price that
held, so when price goes further, that is the level now.

**Latent** means broken and waiting. The object exists, it is drawn, and
it waits until the level would have reached its class's end — never fewer
than `B` candles, so a level that breaks late still gets its minimum.

`B` is a floor on the life, not a deadline on the retest. Read the other
way the bands stop meaning anything the moment a level breaks: every
object would live the same one or two candles no matter which class it
came from, and the class would be decoration.

**Retest** means price touched the zone. A wick counts here, because the
operating timeframe is M1 and there is nothing inside a touch that could
tell one from another. The filtering is done by the thresholds, before the
object ever exists — not by the shape of the touch.

**Active** is not a state, it is the end. The retest activates the object
and the object is done, the way a touched V object is done. What the rest
of the system does with that event is a separate question from this one.

## The zone

The object occupies `n` points from the broken level inward, into the body
of the candle that left it — never outward, into where price has gone. The
level itself is the outer edge.

## The three classes

The same type, the same timeframe, three consecutive bands of maturity:

A level qualifies at `A` = **3**, which belongs to the family rather than
to any one class: below it a high is only a high.

| | **Swi** | **Pos** | **Inv** |
|---|---|---|---|
| timeframe | D1 | D1 | D1 |
| `C` dies at | 7 | 21 | 1021 |
| `B` latency, minimum | 1 | 1 | 21 |
| `n` zone, in points | 300 | 300 | 500 |

Candles throughout, of the one timeframe; `n` in index points.

`C` is stated as the age at which a class ends rather than as a width,
because a boundary is one fact and should be one number. Swi dying at 7
and Pos qualifying at 7 are the same event seen from either side, and
written twice they would eventually be written differently.

What tells the three apart is not where the level came from but **how long
it held**. That is the whole difference, and it is measured directly. An
earlier draft gave each class its own timeframe — monthly for Inv, daily
for the others — which said the same thing through a proxy and had the
classes sharing levels: a monthly high is also some daily high, so one
price could be two objects at once.

The bands are consecutive by construction. Each class qualifies exactly
where the one below it dies:

```
day 0    the candle closes and leaves the level
day 3    qualifies as Swi
day 7    dies as Swi   ·  qualifies as Pos
day 21   dies as Pos   ·  qualifies as Inv
day 1021 dies as Inv
```

Each class is a block of its own, in the code and in the settings: it
declares where it ends, its latency, its zone, whether it is drawn and in
what two colours — one for objects left by a high, one for objects left by
a low, so the hue reads as the class and the shade as the side — and nothing else knows it by name. Where a class begins is
not among them: it is where the one below it ended. The machine below reads the classes as
rows and walks them in order, so a fourth class is a block and a row —
not a path through the logic, and not a line of diagnostics either.

The three classes are one ordered list of boundaries — 3, 7, 21, 1021 —
and a level never belongs to two of them: it is promoted, not duplicated.
Only the last death is a death; the others are handovers.

`B` grows with the band for the same reason. A Swi that breaks on its
last day is owed one more candle; an Inv in the same position is owed
twenty-one, which is the whole chain below it. The floor is proportional
to what the level proved.
