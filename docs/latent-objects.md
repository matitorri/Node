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

      │  B  — candles it waits for the retest
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

**Latent** means broken and waiting. The object exists, it is drawn, and it
has `B` candles for the retest to arrive.

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

| | **Swi** | **Pos** | **Inv** |
|---|---|---|---|
| timeframe | D1 | D1 | D1 |
| `A` qualifies at | 3 | 7 | 21 |
| `C` waits for the break | 4 | 14 | 1000 |
| `B` latency, from the break | 1 | 1 | 21 |
| `n` zone, in points | 300 | 300 | 500 |

Candles throughout, of the one timeframe; `n` in index points.

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
declares its four numbers, whether it is drawn and in what colour, and
nothing else knows it by name. The machine below reads the classes as
rows and walks them in order, so a fourth class is a block and a row —
not a path through the logic, and not a line of diagnostics either.

So `A` is not an independent parameter. The three classes are one ordered
list of boundaries — 3, 7, 21, 1021 — and a level never belongs to two of
them: it is promoted, not duplicated.

`B` grows with the band for the same reason. A level that held three days
gets one day for its retest; one that held twenty-one gets twenty-one,
which is the whole chain below it. The deadline is proportional to what
the level proved.
