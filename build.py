#!/usr/bin/env python3
"""Assemble the pasteable scripts from their parts.

Edit src/, run this, paste from dist/. See docs/architecture.md.

    python3 build.py
"""

from pathlib import Path

SRC  = Path("src")
DIST = Path("dist")

# What each script is made of, in order. The three share the model, so what
# one draws another cannot contradict.
#
#   indicator   the model, drawn, with the alert only it can raise
#   strategy    the model, drawn, plus the trade and the book
#   audit       the model, and every region it has ever held, kept
PARTS = {
    "indicator": ("indicator.head", "model.vobjects", "model.structure",
                  "setup", "signal", "diagnostics", "output", "indicator.tail"),
    "strategy":  ("strategy.head", "model.vobjects", "model.structure",
                  "setup", "signal", "diagnostics", "output",
                  "strategy", "portfolio"),
    "audit":     ("audit.head", "model.vobjects", "audit.tail"),
}


def build(kind: str) -> Path:
    parts = [SRC / f"{name}.pine" for name in PARTS[kind]]
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
    for kind in PARTS:
        out = build(kind)
        print(f"{out}  {len(out.read_text().splitlines())} lines")


if __name__ == "__main__":
    main()
