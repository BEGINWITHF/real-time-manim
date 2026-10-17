# -*- coding: utf-8 -*-
"""Numeric probe for 02-沿路径与同态变换-homotopy (no images involved).

Decodes the RTM and ManimCE renders of the Homotopy demo and measures the
YELLOW rectangle band frame by frame: bbox, per-column top/bottom edge and the
vertical ink profile of the centre column.  Everything is printed as numbers /
ASCII so it never touches an image viewer.

    python tools/_probe_homotopy_shape.py
"""
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from tools.wiki_diff import decode  # noqa: E402

WIKI = "C:/Users/begin/Desktop/RTM-Wiki/03-动画/移动与旋转"
RTM = os.path.join(WIKI, "assets", "RTM output", "02-沿路径与同态变换-homotopy.mp4")
CE = os.path.join(WIKI, "assets", "ManimCE output", "02-沿路径与同态变换-homotopy-manimce.mp4")
SCALE = (480, 270)


def yellow_mask(frame, y0=60):
    """Pixels of the yellow rectangle: R,G high, B low, below the title."""
    f = frame[y0:].astype(np.int16)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    return (r > 60) & (g > 60) & (b < 0.6 * np.minimum(r, g))


def stats(video, label, y0=60, step=6):
    a = decode(video, SCALE)
    print("== %s  frames=%d" % (label, len(a)))
    print("  f   ink   x0  x1  y0  y1   top@x=120,180,240,300,360   bot@x=240")
    rows = []
    for i in range(0, len(a), step):
        m = yellow_mask(a[i], y0)
        ys, xs = np.nonzero(m)
        if not len(xs):
            print("%3d  --" % i)
            continue
        prof_top, prof_bot = [], []
        for x in (120, 180, 240, 300, 360):
            col = np.nonzero(m[:, x])[0]
            prof_top.append(int(col.min()) + y0 if len(col) else -1)
            prof_bot.append(int(col.max()) + y0 if len(col) else -1)
        print("%3d %5d %4d %4d %4d %4d   %s   %4d" % (
            i, int(m.sum()), int(xs.min()), int(xs.max()),
            int(ys.min()) + y0, int(ys.max()) + y0,
            ",".join("%3d" % v for v in prof_top), prof_bot[2]))
        rows.append((i, prof_top))
    return rows


def main():
    r = stats(RTM, "RTM")
    c = stats(CE, "CE")
    print("\n== centre-column top edge swing (RTM vs CE) ==")
    d_r = [p[2] for _, p in r]
    d_c = [p[2] for _, p in c]
    print("RTM top@x=240:", d_r)
    print("CE  top@x=240:", d_c)


if __name__ == "__main__":
    main()
