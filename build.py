#!/usr/bin/env python3
"""Assemble the pasteable scripts from their parts.

Edit src/, run this, paste from dist/. See docs/architecture.md.

    python3 build.py
"""

from pathlib import Path

SRC  = Path("src")
DIST = Path("dist")

KINDS = ("indicator", "strategy")


SHARED = ("model.vobjects", "model.structure", "setup", "signal", "diagnostics", "output")

# What each script adds on top of the shared layers. Both draw the model;
# only the indicator can raise an alert, and only the strategy has a book.
OWN = {
    "indicator": ("indicator.tail",),
    "strategy":  ("strategy", "portfolio"),
}


def build(kind: str) -> Path:
    names = (f"{kind}.head", *SHARED, *OWN[kind])
    parts = [SRC / f"{name}.pine" for name in names]
    body = "\n\n".join(p.read_text().strip("\n") for p in parts) + "\n"
    # The version pragma is a comment, so anything that sweeps comments can
    # take it with it and the artifact silently compiles as Pine v1.
    if not body.startswith("//@version=6\n"):
        raise SystemExit(f"{kind}: the artifact does not open with //@version=6")
    out = DIST / f"node_{kind}.pine"
    out.write_text(body)
    return out


def main() -> None:
    DIST.mkdir(exist_ok=True)
    for kind in KINDS:
        out = build(kind)
        print(f"{out}  {len(out.read_text().splitlines())} lines")


if __name__ == "__main__":
    main()
