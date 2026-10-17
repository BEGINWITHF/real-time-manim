# -*- coding: utf-8 -*-
"""Where are the grid lines? Print runs of lit rows (or cols) in two clips.

For one frame and one column (or row), list every run of pixels brighter than
a threshold, with its centre and peak colour, for A and B separately.  This is
how a line-position / line-count difference is read off numerically.

    python tools/_probe_line_rows.py A.mp4 B.mp4 --frame 40 --x 0.55
    python tools/_probe_line_rows.py A.mp4 B.mp4 --frame 40 --row 0.55
"""
import argparse
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from tools.wiki_diff import decode  # noqa: E402


def runs(profile, thr):
    """profile: (N,3) int.  Return (start, end, centre, peak colour)."""
    lit = profile.max(axis=1) > thr
    out = []
    i = 0
    n = len(lit)
    while i < n:
        if lit[i]:
            j = i
            while j + 1 < n and lit[j + 1]:
                j += 1
            seg = profile[i:j + 1]
            k = int(seg.max(axis=1).argmax())
            out.append((i, j, (i + j) / 2.0, tuple(int(v) for v in seg[k])))
            i = j + 1
        else:
            i += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--frame", type=int, default=0)
    ap.add_argument("--scale", default="1920x1080")
    ap.add_argument("--x", type=float, default=None)
    ap.add_argument("--row", type=float, default=None)
    ap.add_argument("--thr", type=int, default=30)
    args = ap.parse_args()
    w, h = (int(v) for v in args.scale.lower().split("x"))
    a, b = decode(args.a, (w, h)), decode(args.b, (w, h))
    n = min(len(a), len(b))
    i = max(0, min(args.frame, n - 1))

    if args.row is not None:
        r = int(args.row * (h - 1))
        pa, pb = a[i, r], b[i, r]
        label = "col"
    else:
        c = int((args.x if args.x is not None else 0.55) * (w - 1))
        pa, pb = a[i, :, c], b[i, :, c]
        label = "row"
    print("f=%d  %s profile  thr=%d" % (i, label, args.thr))
    for name, p in (("A", pa), ("B", pb)):
        rs = runs(p.astype(int), args.thr)
        print("  %s: %d runs" % (name, len(rs)))
        for s, e, c, pk in rs:
            print("     %4d..%-4d centre %7.1f  peak %s" % (s, e, c, pk))
        if len(rs) > 1:
            centres = [r[2] for r in rs]
            print("     gaps: %s" % [round(centres[k + 1] - centres[k], 1)
                                     for k in range(len(centres) - 1)])


if __name__ == "__main__":
    main()
