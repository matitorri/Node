#!/usr/bin/env python3
"""Assemble the pasteable scripts from their parts.

Edit src/, run this, paste from dist/. See docs/architecture.md.

    python3 build.py
"""

from pathlib import Path

SRC  = Path("src")
DIST = Path("dist")

KINDS = ("indicator", "strategy")


SHARED = ("model.vobjects", "model.structure", "setup", "signal", "diagnostics")

# What each script adds on top of the shared layers. The indicator draws;
# the strategy trades, and only it has a book to manage.
OWN = {
    "indicator": ("indicator.tail",),
    "strategy":  ("strategy", "portfolio"),
}


def build(kind: str) -> Path:
    names = (f"{kind}.head", *SHARED, *OWN[kind])
    parts = [SRC / f"{name}.pine" for name in names]
    body = "\n\n".join(p.read_text().strip("\n") for p in parts) + "\n"
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
