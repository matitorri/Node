#!/usr/bin/env python3
"""Merge the TradingView exports into one record of the backtest.

TradingView will only deep-backtest fifteen days at a time, so a run comes
back as a pile of exports. Each one restarts its trade numbering and its
cumulative columns, which makes none of them comparable and all of them
wrong about the whole. This reads them, drops the trades two windows both
saw, orders what is left by entry, and recomputes the running figures once.

    python3 performance.py [--capital 50000]

Writes Performance/trades.xlsx, which is then the only place to read the
backtest from. Two sheets: the trades, and a page of figures that are
formulas over them. Nothing in the book is a number somebody typed, so
correcting a trade corrects everything that was said about it.
"""

import argparse
import csv
import glob
import os
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(HERE, "Performance")
OUT = os.path.join(DIR, "trades.xlsx")
HEAD = os.path.join(HERE, "src", "strategy.head.pine")


def built_version():
    """What src currently builds. An export carries the title the script had
    when it ran, which lags a version bump, so the build is the better
    default — and --label is there for a backtest of something older."""
    try:
        for line in open(HEAD, encoding="utf-8"):
            if line.startswith("strategy("):
                return line.split('"')[1]
    except OSError:
        pass
    return "unknown"

# What the exports said, and then what follows from it. The second group is
# formulas: the drawdown and the streak need a running value, and a sheet
# that shows how they are reached can be argued with.
GIVEN = ["n", "side", "entry time", "entry price", "exit time", "exit price",
         "qty", "net pnl", "commission", "favorable", "adverse", "bars",
         "source"]
DERIVED = ["cumulative pnl", "equity", "peak", "drawdown", "drawdown %",
           "losing streak"]

MONEY = "#,##0.00"
PCT   = "0.00%"
PCT1  = "0.0%"


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


def trades_sheet(ws, trades, capital_ref):
    """The exports, ordered, with the running figures written as formulas so
    the sheet shows how each one is reached."""
    head = GIVEN + DERIVED
    ws.append(head)
    for c in range(1, len(head) + 1):
        ws.cell(1, c).font = Font(bold=True)

    for i, t in enumerate(trades, 1):
        r = i + 1
        ws.append([
            i, t["side"], t["entry time"], t["entry price"],
            t["exit time"], t["exit price"], int(t["qty"]),
            round(t["net pnl"], 2), round(t["commission"], 2),
            round(t["favorable"], 2), round(t["adverse"], 2),
            int(t["bars"]), t["source"],
        ])
        prev = r - 1
        first = r == 2
        ws.cell(r, 14).value = f"=SUM($H$2:H{r})"
        ws.cell(r, 15).value = f"={capital_ref}+N{r}"
        # The peak carries forward; on the first row there is nothing behind
        # it but the account as it started.
        ws.cell(r, 16).value = (f"=MAX({capital_ref},O{r})" if first
                                else f"=MAX(P{prev},O{r})")
        ws.cell(r, 17).value = f"=P{r}-O{r}"
        ws.cell(r, 18).value = f"=IF(P{r}=0,0,Q{r}/P{r})"
        ws.cell(r, 19).value = (f"=IF(H{r}<0,1,0)" if first
                                else f"=IF(H{r}<0,S{prev}+1,0)")

        for c in (3, 5):
            ws.cell(r, c).number_format = "yyyy-mm-dd hh:mm"
        for c in (4, 6, 8, 9, 10, 11, 14, 15, 16, 17):
            ws.cell(r, c).number_format = MONEY
        ws.cell(r, 18).number_format = PCT

    for c, w in enumerate([5, 7, 17, 12, 17, 12, 6, 11, 12, 11, 11, 7, 46,
                           15, 12, 12, 11, 11, 14], start=1):
        ws.column_dimensions[get_column_letter(c)].width = w
    ws.freeze_panes = "A2"


def figures(ws, trades, capital, windows, label):
    """Every figure a formula over the trades sheet. A row is named once and
    referred to by name, so a line can be moved without breaking the rest."""
    last = len(trades) + 1
    pnl  = f"Trades!$H$2:$H${last}"
    side = f"Trades!$B$2:$B${last}"

    at = {}

    def ref(name):
        return f"$B${at[name]}"

    rows = []

    def put(name, value, fmt=None):
        rows.append((name, value, fmt))
        if name:
            at[name] = len(rows) + 1

    put("script", label)
    put("capital", capital, MONEY)
    put("windows", windows)
    put("trades", f"=COUNT({pnl})")
    put("from", f"=MIN(Trades!$C$2:$C${last})", "yyyy-mm-dd")
    put("to", f"=MAX(Trades!$E$2:$E${last})", "yyyy-mm-dd")
    put("", "")
    put("net", f"=SUM({pnl})", MONEY)
    put("net %", f"={ref('net')}/{ref('capital')}", PCT)
    put("gross win", f'=SUMIF({pnl},">0")', MONEY)
    put("gross loss", f'=-SUMIF({pnl},"<0")', MONEY)
    put("profit factor",
        f"=IF({ref('gross loss')}=0,\"\",{ref('gross win')}/{ref('gross loss')})",
        "0.00")
    put("", "")
    put("wins", f'=COUNTIF({pnl},">0")')
    put("losses", f'=COUNTIF({pnl},"<0")')
    put("win rate", f"={ref('wins')}/{ref('trades')}", PCT1)
    put("average win",
        f"=IF({ref('wins')}=0,\"\",{ref('gross win')}/{ref('wins')})", MONEY)
    put("average loss",
        f"=IF({ref('losses')}=0,\"\",-{ref('gross loss')}/{ref('losses')})", MONEY)
    put("expectancy", f"={ref('net')}/{ref('trades')}", MONEY)
    put("best", f"=MAX({pnl})", MONEY)
    put("worst", f"=MIN({pnl})", MONEY)
    put("", "")
    put("max drawdown", f"=MAX(Trades!$Q$2:$Q${last})", MONEY)
    put("max drawdown %", f"=MAX(Trades!$R$2:$R${last})", PCT)
    put("losing streak", f"=MAX(Trades!$S$2:$S${last})")
    put("commission", f"=SUM(Trades!$I$2:$I${last})", MONEY)
    put("", "")
    for s in ("long", "short"):
        put(f"{s} trades", f'=COUNTIF({side},"{s}")')
        put(f"{s} net", f'=SUMIF({side},"{s}",{pnl})', MONEY)
        put(f"{s} win rate",
            f'=IF({ref(f"{s} trades")}=0,\"\",'
            f'COUNTIFS({side},"{s}",{pnl},">0")/{ref(f"{s} trades")})', PCT1)

    ws.append(["metric", "value"])
    ws.cell(1, 1).font = ws.cell(1, 2).font = Font(bold=True)
    for name, value, fmt in rows:
        ws.append([name, value])
        r = ws.max_row
        if fmt:
            ws.cell(r, 2).number_format = fmt
        ws.cell(r, 2).alignment = Alignment(horizontal="right")
    ws.column_dimensions["A"].width = 18
    ws.column_dimensions["B"].width = 20
    return at


def show(trades, capital, windows, label, dupes):
    """The same figures, computed here, for the terminal. The book is the
    record; this is only so the run says something on its way past."""
    wins = [t for t in trades if t["net pnl"] > 0]
    losses = [t for t in trades if t["net pnl"] < 0]
    gw = sum(t["net pnl"] for t in wins)
    gl = -sum(t["net pnl"] for t in losses)
    net = sum(t["net pnl"] for t in trades)
    equity = [capital]
    for t in trades:
        equity.append(equity[-1] + t["net pnl"])
    dd, ddpct = drawdown(equity)
    streak = worst = 0
    for t in trades:
        streak = streak + 1 if t["net pnl"] < 0 else 0
        worst = max(worst, streak)

    def line(k, v):
        print(f"  {k:<16} {v}")

    print()
    line("script", label)
    line("trades", f"{len(trades)} over {windows} windows"
                   + (f", {dupes} duplicates dropped" if dupes else ""))
    line("from", f"{trades[0]['entry time']:%Y-%m-%d}"
                 f" to {trades[-1]['exit time']:%Y-%m-%d}")
    line("net", f"{net:+,.2f}   {net / capital * 100:+.2f}%")
    line("profit factor", f"{gw / gl:.2f}" if gl else "—")
    line("win rate", f"{len(wins) / len(trades) * 100:.1f}%"
                     f"   {len(wins)}W {len(losses)}L")
    line("expectancy", f"{net / len(trades):+,.2f} per trade")
    line("max drawdown", f"{dd:,.2f}   {ddpct:.2f}%")
    line("losing streak", worst)
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capital", type=float, default=50000)
    ap.add_argument("--label", default=None,
                    help="what produced these trades; defaults to what src builds")
    args = ap.parse_args()

    paths = [p for p in glob.glob(os.path.join(DIR, "*.csv"))]
    if not paths:
        raise SystemExit(f"no exports in {DIR}")

    trades, dupes = merge(paths)
    if not trades:
        raise SystemExit("the exports hold no completed trade")

    windows = len(set(t["source"] for t in trades))
    label = args.label or built_version()

    wb = Workbook()
    perf = wb.active
    perf.title = "Performance"
    trd = wb.create_sheet("Trades")

    at = figures(perf, trades, args.capital, windows, label)
    trades_sheet(trd, trades, f"Performance!$B${at['capital']}")
    wb.save(OUT)

    print(f"\n{os.path.relpath(OUT, HERE)}  {len(trades)} trades")
    show(trades, args.capital, windows, label, dupes)


if __name__ == "__main__":
    main()
