# -*- coding: utf-8 -*-
"""Row/column energy profile of the per-frame difference (numeric, image-free).

Answers "the diff is periodic bands -- along which axis, and at which spatial
period?" without ever looking at an image.

    python tools/_probe_rowcol.py A.mp4 B.mp4 --frame 30 [--scale 1920x1080]
    python tools/_probe_rowcol.py A.mp4 B.mp4 --frame 30 --profile row \
        --y0 0.44 --y1 0.52 --x 0.31     # dump A/B pixels down one column
"""
import argparse
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from tools.wiki_diff import decode  # noqa: E402


def peaks(profile, k=8):
    """Indices of the k strongest separated local maxima of `profile`."""
    order = np.argsort(profile)[::-1]
    picked = []
    for i in order:
        if all(abs(int(i) - p) > 3 for p in picked):
            picked.append(int(i))
        if len(picked) >= k:
            break
    return sorted(picked)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--frame", type=int, default=0)
    ap.add_argument("--scale", default="1920x1080")
    ap.add_argument("--y0", type=float, default=None)
    ap.add_argument("--y1", type=float, default=None)
    ap.add_argument("--x", type=float, default=0.31, help="column to dump")
    args = ap.parse_args()
    w, h = (int(v) for v in args.scale.lower().split("x"))

    fa = decode(args.a, scale=(w, h))
    fb = decode(args.b, scale=(w, h))
    n = min(len(fa), len(fb))
    i = max(0, min(args.frame, n - 1))
    d = np.abs(fa[i].astype(np.int16) - fb[i].astype(np.int16)).mean(axis=2)
    print("frames A=%d B=%d  f=%d  scale %dx%d  mean|diff|=%.3f"
          % (len(fa), len(fb), i, w, h, d.mean()))

    rows = d.mean(axis=1)
    cols = d.mean(axis=0)
    print("row profile: mean=%.2f max=%.2f  peaks=%s"
          % (rows.mean(), rows.max(), peaks(rows)))
    print("col profile: mean=%.2f max=%.2f  peaks=%s"
          % (cols.mean(), cols.max(), peaks(cols)))
    for name, prof in (("row", rows), ("col", cols)):
        top = np.argsort(prof)[::-1][:20]
        print("%s top: %s" % (name, ", ".join(
            "%d:%.1f" % (int(k), prof[k]) for k in sorted(top))))
    # strongest-row separation -> the spatial period of the bands
    rp = peaks(rows, 12)
    if len(rp) > 1:
        print("row peak gaps: %s" % np.diff(rp).tolist())
    cp = peaks(cols, 12)
    if len(cp) > 1:
        print("col peak gaps: %s" % np.diff(cp).tolist())

    if args.y0 is not None:
        y0 = int(args.y0 * (h - 1))
        y1 = int(args.y1 * (h - 1))
        col = int(args.x * (w - 1))
        print("column dump x=%d" % col)
        print("   y      A               B            |d|     rowmean")
        for y in range(y0, y1 + 1):
            pa = fa[i, y, col].astype(int)
            pb = fb[i, y, col].astype(int)
            print("%5d  (%3d,%3d,%3d)  (%3d,%3d,%3d)  %5.1f   %6.2f"
                  % (y, pa[0], pa[1], pa[2], pb[0], pb[1], pb[2],
                     float(np.abs(pa - pb).max()), rows[y]))


if __name__ == "__main__":
    main()
