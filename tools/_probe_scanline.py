# -*- coding: utf-8 -*-
"""Print one scanline's RGB from two clips side by side (numeric, image-free).

Used to show WHAT a renderer does to a fill -- e.g. a gradient polygon painted
flat (item a) reads one constant colour along the line where its ManimCE twin
ramps.  Decodes at a reduced size (default 960x540), so it stays cheap.

    python tools/_probe_scanline.py A.mp4 B.mp4 --frame 90 --y 0.60 \
        --x0 0.35 --x1 0.65 --step 8
"""
import argparse
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from tools.wiki_diff import decode  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--frame", type=int, default=0)
    ap.add_argument("--y", type=float, default=0.5, help="row, fraction of height")
    ap.add_argument("--x0", type=float, default=0.3)
    ap.add_argument("--x1", type=float, default=0.7)
    ap.add_argument("--step", type=int, default=8)
    ap.add_argument("--scale", default="960x540")
    args = ap.parse_args()
    w, h = (int(v) for v in args.scale.lower().split("x"))

    fa = decode(args.a, scale=(w, h))
    fb = decode(args.b, scale=(w, h))
    n = min(len(fa), len(fb))
    i = max(0, min(args.frame, n - 1))
    row = int(args.y * (h - 1))
    x0 = int(args.x0 * (w - 1))
    x1 = int(args.x1 * (w - 1))
    print("frames: A=%d B=%d comparing f%d row=%d" % (len(fa), len(fb), i, row))
    print("   x      A               B            |d|")
    worst = (0.0, 0)
    for x in range(x0, x1 + 1, args.step):
        pa = fa[i, row, x].astype(int)
        pb = fb[i, row, x].astype(int)
        d = float(np.abs(pa - pb).max())
        if d > worst[0]:
            worst = (d, x)
        print("%5d  (%3d,%3d,%3d)  (%3d,%3d,%3d)  %5.1f"
              % (x, pa[0], pa[1], pa[2], pb[0], pb[1], pb[2], d))
    # whole-frame stats over the same band, so one line cannot cherry-pick
    A = fa[i, row, x0:x1 + 1].astype(int)
    B = fb[i, row, x0:x1 + 1].astype(int)
    diff = np.abs(A - B)
    d2 = diff.max(axis=1)
    print("band f%d row=%d x[%d..%d]: mean|d|=%.2f  max=%.0f at x=%d"
          % (i, row, x0, x1, diff.mean(), d2.max(), x0 + int(d2.argmax())))


if __name__ == "__main__":
    main()
