# Diagnostics

A reading of the state behind the drawings, so a disagreement between the
chart and the code can be settled by looking rather than by inference.

Source: `src/diagnostics.pine`, plus the rows the portfolio appends.

Off by default. Turn it on under **Common → Diagnostics table**. It is
drawn on the last bar only, so in the replay it reports the bar you are
standing on.

## Rows

| rows | what they report |
|---|---|
| 0–2 | the chart, how the grid is being fed, the bar |
| 3–5 | what the H4 feed thinks the session is |
| 6–10 | the objects |
| 11–13 | the structure and its last change of character |
| 14–15 | the setup and the signal |
| 16–23 | the portfolio — strategy only |

The `signal` row speaks only on the bar it fires, so in live trading it
reads as empty almost always. Use the replay: stand on a bar where
`setup` is holding a region and step forward until a change of character
arrives.

The `allows` row says why when it says no: outside hours, day is over, or
book is full.

## Why it exists

It was built after two rounds of failed screenshot archaeology and
settled two bugs on sight. The holiday freeze was visible as a last
turnover four days older than the bar; the touch that seemed not to be
registering turned out to be registering all along.

Row numbers are fixed rather than running, so a section can add rows
without knowing what any other section did. The table is created with
room for every section that could write into it; a row nobody fills is
never drawn.
