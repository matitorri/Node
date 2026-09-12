# Signal

The trigger, inside a valid setup. Instantaneous, where the setup is a
standing condition.

Source: `src/signal.pine`.

It is the change of character the structure model publishes, and it is
the same for every setup — which is why it lives beside them rather than
inside one. Two things qualify it:

**There has to be a region in play.** A change of character with no setup
holding is a fact about the market, not a signal.

**Its direction has to agree with that region's side.** An M object that
came from a bullish candle is demand, and the setup is a reversion to it,
so only a turn upwards on it means anything.

Nothing expires. While the setup holds the region, a change of character
hours after the touch still counts.

The structure section already marks the raw change of character on the
chart. This is the qualified one.
