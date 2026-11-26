"""Render the PyPI download history as a 3b1b-style SVG line chart.

Usage:
    python scripts/plot_downloads.py
    python scripts/plot_downloads.py --mirrors   # include mirror downloads

Data: https://pypistats.org/api/packages/<package>/overall
The SVG is committed so GitHub can render it without JavaScript.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import math
import os
import struct
import urllib.request
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join(ROOT, "assets", "pypi-downloads.svg")
RTM_LOGO = os.path.join(ROOT, "assets", "rtm-logo-white.png")
AX_LOGO = os.path.join(ROOT, "assets", "axioviva-mark-white.png")
API = "https://pypistats.org/api/packages/{package}/overall"

BG = "#000000"
CREAM = "#ffffff"
MUTED = "#8a8a8a"
FAINT = "#242424"
AXIS = "#ffffff"
BLUE = "#3f3f3f"
GOLD = "#ffffff"
TEAL = "#ffffff"

SERIF = '"CMU Serif", "Latin Modern Roman", Georgia, "Times New Roman", serif'


def fetch(package: str) -> list[dict]:
    req = urllib.request.Request(
        API.format(package=package),
        headers={"User-Agent": "rtm-downloads-chart/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)["data"]


def nice_max(value: int) -> int:
    if value <= 0:
        return 1
    exp = 10 ** math.floor(math.log10(value))
    for step in (1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if value <= step * exp:
            return int(step * exp)
    return int(10 * exp)


def fmt_date(day: dt.date) -> str:
    return f"{day.strftime('%b').upper()} {day.day}"


def png_size(path: str) -> tuple[int, int]:
    with open(path, "rb") as fh:
        fh.read(16)
        return struct.unpack(">II", fh.read(8))


def data_uri(path: str) -> str:
    with open(path, "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode("ascii")


def build_svg(rows: list[dict], package: str, mirrors: bool) -> str:
    wanted = "with_mirrors" if mirrors else "without_mirrors"
    by_day: dict[dt.date, int] = defaultdict(int)
    for row in rows:
        if row.get("category") == wanted:
            by_day[dt.date.fromisoformat(row["date"])] += int(row.get("downloads", 0))
    if not by_day:
        raise SystemExit("no %s rows in the pypistats response" % wanted)

    start, end = min(by_day), max(by_day)
    days = [start + dt.timedelta(days=i) for i in range((end - start).days + 1)]
    values = [by_day.get(day, 0) for day in days]

    def average(window: int) -> list[float]:
        out, total = [], 0
        for i, value in enumerate(values):
            total += value
            if i >= window:
                total -= values[i - window]
            out.append(total / min(i + 1, window))
        return out

    avg7 = average(7)

    width, height = 900, 450
    left, right, top, bottom = 84, 856, 112, 354
    plot_w, plot_h = right - left, bottom - top
    y_max = max(nice_max(max(values)), 10)
    y_max = int(math.ceil(y_max / 5.0) * 5)
    x_span = max(1, (end - start).days)

    def x_at(day: dt.date) -> float:
        return left + (day - start).days / x_span * plot_w

    def y_at(value: float) -> float:
        return bottom - value / y_max * plot_h

    daily_points = [(x_at(day), y_at(value)) for day, value in zip(days, values)]
    avg_points = [(x_at(day), y_at(value)) for day, value in zip(days, avg7)]
    daily_path = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in daily_points)
    avg_path = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in avg_points)

    grid = []
    for i in range(6):
        value = y_max * i / 5
        y = y_at(value)
        grid.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" '
                    f'stroke="{FAINT}" stroke-width="1" stroke-dasharray="2 6"/>')
        grid.append(f'<line x1="{left-5}" y1="{y:.1f}" x2="{left}" y2="{y:.1f}" '
                    f'stroke="{AXIS}" stroke-width="1.2"/>')
        grid.append(f'<text x="{left-14}" y="{y+4:.1f}" text-anchor="end" '
                    f'class="axis">{int(round(value))}</text>')

    ticks = [start, end]
    cursor = start.replace(day=1)
    while cursor <= end:
        if cursor > start:
            ticks.append(cursor)
        month = cursor.month + 1
        year = cursor.year + (month > 12)
        month = 1 if month > 12 else month
        cursor = dt.date(year, month, 1)
    xlabels = []
    last_x = -1000.0
    for day in sorted({d for d in ticks}):
        x = x_at(day)
        if x - last_x < 60 and day not in (start, end):
            continue
        xlabels.append(f'<line x1="{x:.1f}" y1="{bottom}" x2="{x:.1f}" '
                       f'y2="{bottom+5}" stroke="{AXIS}" stroke-width="1.2"/>')
        xlabels.append(f'<text x="{x:.1f}" y="{bottom+22}" text-anchor="middle" '
                       f'class="axis">{fmt_date(day)}</text>')
        last_x = x

    releases = [
        (dt.date(2026, 10, 23), "2.0.0"),
        (dt.date(2026, 11, 24), "2.0.12"),
    ]
    markers = []
    for day, label in releases:
        if start <= day <= end:
            x = x_at(day)
            anchor = "end" if x > right - 46 else "middle"
            markers.append(
                f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" '
                f'stroke="{GOLD}" stroke-opacity="0.30" stroke-width="1" '
                f'stroke-dasharray="3 6"/>'
                f'<text x="{x:.1f}" y="{top-12}" text-anchor="{anchor}" '
                f'class="release">{label}</text>')

    total = sum(values)
    last30 = sum(values[-30:])
    source = "including mirrors" if mirrors else "excluding mirrors"
    end_x, end_y = avg_points[-1]
    last_avg = avg7[-1]
    rtm_uri = data_uri(RTM_LOGO)
    rtm_w = round(30 * png_size(RTM_LOGO)[0] / png_size(RTM_LOGO)[1])
    ax_uri = data_uri(AX_LOGO)
    ax_h = 24
    ax_w = round(ax_h * png_size(AX_LOGO)[0] / png_size(AX_LOGO)[1])
    frame = 39
    org_x = 28 + frame + 13
    title_x = left + rtm_w + 14

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
     viewBox="0 0 {width} {height}" role="img"
     aria-labelledby="rtm-dl-title rtm-dl-desc">
  <title id="rtm-dl-title">PyPI downloads for {package}</title>
  <desc id="rtm-dl-desc">daily downloads, {source}, {total} total</desc>
  <style>
    .title {{ font: 500 34px "Helvetica Neue", Arial, sans-serif; fill: {CREAM}; letter-spacing: -0.02em; }}
    .sub {{ font: 500 10.5px ui-monospace, SFMono-Regular, Consolas, monospace; fill: {MUTED}; letter-spacing: 0.16em; }}
    .axis {{ font: 400 10px ui-monospace, SFMono-Regular, Consolas, monospace; fill: {MUTED}; }}
    .stat {{ font: 700 34px ui-monospace, SFMono-Regular, Consolas, monospace; fill: {CREAM}; }}
    .statlabel {{ font: 500 9.5px ui-monospace, SFMono-Regular, Consolas, monospace; fill: {MUTED}; letter-spacing: 0.14em; }}
    .release {{ font: 500 9.5px ui-monospace, SFMono-Regular, Consolas, monospace; fill: {CREAM}; letter-spacing: 0.08em; }}
    .legend {{ font: 400 10px ui-monospace, SFMono-Regular, Consolas, monospace; fill: {MUTED}; letter-spacing: 0.08em; }}
    .foot {{ font: 400 9.5px ui-monospace, SFMono-Regular, Consolas, monospace; fill: #5a5a5a; letter-spacing: 0.1em; }}
    .org {{ font: 600 14px "Helvetica Neue", Arial, sans-serif; fill: {CREAM}; letter-spacing: 0.04em; }}  </style>
  <rect width="{width}" height="{height}" fill="{BG}"/>
  <image x="{left}" y="24" width="{rtm_w}" height="30" href="{rtm_uri}"/>
  <text x="{title_x}" y="50" class="title">PYPI DOWNLOADS</text>
  <text x="{title_x}" y="76" class="sub">REAL-TIME-MANIM / DAILY / {source.upper()} / {total:,} TOTAL</text>
  <g text-anchor="end">
    <text x="{right}" y="50" class="stat">{last30:,}</text>
    <text x="{right}" y="69" class="statlabel">LAST 30 DAYS</text>
  </g>
  <g>{''.join(grid)}</g>
  <g>{''.join(markers)}</g>
  <path d="{daily_path}" fill="none" stroke="{BLUE}" stroke-width="1"
        stroke-linejoin="miter"/>
  <path d="{avg_path}" fill="none" stroke="{GOLD}" stroke-width="3"
        stroke-linejoin="miter" stroke-linecap="square"/>
  <rect x="{end_x-4:.1f}" y="{end_y-4:.1f}" width="8" height="8" fill="{GOLD}"/>
  <rect x="{end_x-7:.1f}" y="{end_y-7:.1f}" width="14" height="14"
        fill="none" stroke="{GOLD}" stroke-width="1"/>
  <text x="{end_x-12:.1f}" y="{end_y-13:.1f}" text-anchor="end"
        class="legend" fill="{CREAM}">7-DAY AVG {last_avg:.0f}</text>
  <g>{''.join(xlabels)}</g>
  <line x1="{left}" y1="{bottom}" x2="{right+10}" y2="{bottom}"
        stroke="{AXIS}" stroke-width="1.3"/>
  <polygon points="{right+18},{bottom} {right+9},{bottom-5} {right+9},{bottom+5}"
           fill="{AXIS}"/>
  <line x1="{left}" y1="{bottom}" x2="{left}" y2="{top-10}"
        stroke="{AXIS}" stroke-width="1.3"/>
  <polygon points="{left},{top-18} {left-5},{top-9} {left+5},{top-9}"
           fill="{AXIS}"/>
  <text x="26" y="{(top+bottom)/2:.1f}" text-anchor="middle" class="axis"
        transform="rotate(-90 26 {(top+bottom)/2:.1f})">DOWNLOADS / DAY</text>
  <g transform="translate({right-230},{height-47})">
    <line x1="0" y1="0" x2="20" y2="0" stroke="{GOLD}" stroke-width="2.6"/>
    <text x="27" y="4" class="legend">7-DAY AVERAGE</text>
    <line x1="132" y1="0" x2="152" y2="0" stroke="{BLUE}" stroke-width="1"
          stroke-opacity="0.55"/>
    <text x="159" y="4" class="legend">DAILY</text>
  </g>
  <g transform="translate(28,{height-66})">
    <rect x="0" y="0" width="{frame}" height="{frame}" fill="none"
          stroke="{CREAM}" stroke-width="1.6"/>
    <image x="{(frame-ax_w)/2:.1f}" y="{(frame-ax_h)/2:.1f}" width="{ax_w}"
           height="{ax_h}" href="{ax_uri}"/>
  </g>
  <text x="{org_x}" y="{height-42}" class="org">Team-Axioviva</text>
  <text x="{right}" y="{height-13}" text-anchor="end" class="foot">
    SOURCE: PYPISTATS.ORG / AUTO-REFRESH 00:00 GMT
  </text>
</svg>
'''


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--package", default="real-time-manim")
    ap.add_argument("--mirrors", action="store_true",
                    help="include mirror downloads (default: exclude)")
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()

    svg = build_svg(fetch(args.package), args.package, args.mirrors)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(svg)
    print("wrote", args.out, "(%d bytes)" % len(svg.encode("utf-8")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
