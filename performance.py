#!/usr/bin/env python3
"""Merge the TradingView exports into one record of the backtest.

TradingView will only deep-backtest fifteen days at a time, so a run comes
back as a pile of exports. Each one restarts its trade numbering and its
cumulative columns, which makes none of them comparable and all of them
wrong about the whole. This reads them, drops the trades two windows both
saw, orders what is left by entry, and recomputes the running figures once.

    python3 performance.py [--capital 50000]

Writes Performance/trades.csv, which is then the only place to read the
backtest from, and prints what it adds up to.
"""

import argparse
import csv
import glob
import os
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(HERE, "Performance")
OUT = os.path.join(DIR, "trades.csv")

FIELDS = [
    "n", "side", "entry time", "entry price", "exit time", "exit price",
    "qty", "net pnl", "commission", "favorable", "adverse", "bars",
    "cumulative pnl", "equity", "source",
]


def num(s):
    """TradingView leaves a cell empty rather than writing a zero."""
    s = (s or "").strip().replace(",", "")
    return 0.0 if s == "" else float(s)


def when(s):
    return datetime.strptime(s.strip(), "%Y-%m-%d %H:%M")


def read(path):
    """One export, as trades. Each trade is two rows sharing a number."""
    trades = {}
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            kind = row["Type"].strip().lower()
            n = row["Trade number"].strip()
            t = trades.setdefault(n, {})
            if kind.startswith("entry"):
                t["side"] = "long" if kind.endswith("long") else "short"
                t["entry time"] = when(row["Date and time"])
                t["entry price"] = num(row["Price USD"])
                t["qty"] = num(row["Size (qty)"])
                t["net pnl"] = num(row["Net PnL USD"])
                t["commission"] = num(row["Commission USD"])
                t["favorable"] = num(row["Favorable excursion USD"])
                t["adverse"] = num(row["Adverse excursion USD"])
                t["bars"] = num(row["Duration (bars)"])
            else:
                t["exit time"] = when(row["Date and time"])
                t["exit price"] = num(row["Price USD"])
    # A window can end mid-trade: an entry whose exit the next window holds.
    return [t | {"source": os.path.basename(path)}
            for t in trades.values() if "entry time" in t and "exit time" in t]


def merge(paths):
    seen, trades, dupes = {}, [], 0
    for path in sorted(paths):
        for t in read(path):
            key = (t["entry time"], t["exit time"], t["side"],
                   t["entry price"], t["exit price"], t["qty"])
            if key in seen:
                dupes += 1
                continue
            seen[key] = True
            trades.append(t)
    trades.sort(key=lambda t: (t["entry time"], t["exit time"]))
    return trades, dupes


def drawdown(equity):
    """Deepest fall from a peak, on closed trades. Nothing intrabar is here."""
    peak, worst, pct = equity[0], 0.0, 0.0
    for e in equity:
        peak = max(peak, e)
        if peak - e > worst:
            worst, pct = peak - e, (peak - e) / peak * 100
    return worst, pct


def report(trades, capital, dupes):
    wins = [t for t in trades if t["net pnl"] > 0]
    losses = [t for t in trades if t["net pnl"] < 0]
    gross_win = sum(t["net pnl"] for t in wins)
    gross_loss = -sum(t["net pnl"] for t in losses)
    net = sum(t["net pnl"] for t in trades)
    equity = [capital]
    for t in trades:
        equity.append(equity[-1] + t["net pnl"])
    dd, ddpct = drawdown(equity)

    streak = worst_streak = 0
    for t in trades:
        streak = streak + 1 if t["net pnl"] < 0 else 0
        worst_streak = max(worst_streak, streak)

    def line(k, v):
        print(f"  {k:<22} {v}")

    print()
    print(f"  {len(trades)} trades from {len(set(t['source'] for t in trades))} windows"
          + (f", {dupes} duplicates dropped" if dupes else ""))
    print(f"  {trades[0]['entry time']:%Y-%m-%d}"
          f" to {trades[-1]['exit time']:%Y-%m-%d}")
    print()
    line("net", f"{net:+,.2f}   {net / capital * 100:+.2f}% of {capital:,.0f}")
    line("gross win / loss", f"{gross_win:,.2f} / {gross_loss:,.2f}")
    line("profit factor", f"{gross_win / gross_loss:.2f}" if gross_loss else "—")
    line("win rate", f"{len(wins) / len(trades) * 100:.1f}%"
                     f"   {len(wins)}W {len(losses)}L")
    line("average win", f"{gross_win / len(wins):,.2f}" if wins else "—")
    line("average loss", f"{-gross_loss / len(losses):,.2f}" if losses else "—")
    line("expectancy", f"{net / len(trades):+,.2f} per trade")
    line("best / worst", f"{max(t['net pnl'] for t in trades):+,.2f}"
                        f" / {min(t['net pnl'] for t in trades):+,.2f}")
    line("max drawdown", f"{dd:,.2f}   {ddpct:.2f}%")
    line("losing streak", f"{worst_streak}")
    line("commission", f"{sum(t['commission'] for t in trades):,.2f}")
    print()
    for side in ("long", "short"):
        s = [t for t in trades if t["side"] == side]
        if s:
            w = sum(1 for t in s if t["net pnl"] > 0)
            line(side, f"{len(s)} trades   {sum(t['net pnl'] for t in s):+,.2f}"
                       f"   {w / len(s) * 100:.0f}% won")
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capital", type=float, default=50000)
    args = ap.parse_args()

    paths = [p for p in glob.glob(os.path.join(DIR, "*.csv"))
             if os.path.abspath(p) != OUT]
    if not paths:
        raise SystemExit(f"no exports in {DIR}")

    trades, dupes = merge(paths)
    if not trades:
        raise SystemExit("the exports hold no completed trade")

    running = 0.0
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for i, t in enumerate(trades, 1):
            running += t["net pnl"]
            w.writerow({
                "n": i,
                "side": t["side"],
                "entry time": f"{t['entry time']:%Y-%m-%d %H:%M}",
                "entry price": t["entry price"],
                "exit time": f"{t['exit time']:%Y-%m-%d %H:%M}",
                "exit price": t["exit price"],
                "qty": int(t["qty"]),
                "net pnl": round(t["net pnl"], 2),
                "commission": round(t["commission"], 2),
                "favorable": round(t["favorable"], 2),
                "adverse": round(t["adverse"], 2),
                "bars": int(t["bars"]),
                "cumulative pnl": round(running, 2),
                "equity": round(args.capital + running, 2),
                "source": t["source"],
            })

    print(f"\n{os.path.relpath(OUT, HERE)}  {len(trades)} trades")
    report(trades, args.capital, dupes)


if __name__ == "__main__":
    main()
