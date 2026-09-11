#!/usr/bin/env python3
"""Assemble the pasteable scripts from their parts.

The model is written once, in src/model.pine, and both scripts are built
around it. Edit src/, run this, paste from dist/.

    python3 build.py
"""

from pathlib import Path

SRC  = Path("src")
DIST = Path("dist")

KINDS = ("indicator", "strategy")


def build(kind: str) -> Path:
    parts = [SRC / f"{kind}.head.pine", SRC / "model.pine", SRC / f"{kind}.tail.pine"]
    body = "\n".join(p.read_text().strip("\n") for p in parts) + "\n"
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
