# -*- coding: utf-8 -*-
"""Vertical column profile of two clips (numeric, image-free).

Used to see how a horizontal grid line is drawn (position / width / peak) by
comparing a single column of pixels.  Run from the repo root:

    python _col.py <A.mp4> <B.mp4> --frame 0 --x 0.5 --y0 0.32 --y1 0.40
"""
import argparse
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
from tools.wiki_diff import decode  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("a")
ap.add_argument("b")
ap.add_argument("--frame", type=int, default=0)
ap.add_argument("--x", type=float, default=0.5)
ap.add_argument("--y0", type=float, default=0.0)
ap.add_argument("--y1", type=float, default=1.0)
ap.add_argument("--scale", default="1920x1080")
args = ap.parse_args()
w, h = (int(v) for v in args.scale.lower().split("x"))

fa = decode(args.a, scale=(w, h))
fb = decode(args.b, scale=(w, h))
n = min(len(fa), len(fb))
i = max(0, min(args.frame, n - 1))
col = int(args.x * (w - 1))
y0, y1 = int(args.y0 * (h - 1)), int(args.y1 * (h - 1))
print("frames A=%d B=%d f=%d col=%d  (scale %dx%d)" % (len(fa), len(fb), i, col, w, h))
print("   y      A               B            |d|")
for y in range(y0, y1 + 1):
    pa = fa[i, y, col].astype(int)
    pb = fb[i, y, col].astype(int)
    print("%5d  (%3d,%3d,%3d)  (%3d,%3d,%3d)  %5.1f"
          % (y, pa[0], pa[1], pa[2], pb[0], pb[1], pb[2],
             float(np.abs(pa - pb).max())))
A = fa[i, y0:y1 + 1, col].astype(int)
B = fb[i, y0:y1 + 1, col].astype(int)
d = np.abs(A - B)
print("band mean|d|=%.2f max=%.0f" % (d.mean(), d.max()))
