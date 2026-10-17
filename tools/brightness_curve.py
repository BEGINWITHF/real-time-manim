"""Probe: mean frame brightness over time for a pair of wiki videos.

    python tools/brightness_curve.py A.mp4 B.mp4 --from 5.5 --to 8.0 [--fps 60]

Prints, per frame, the mean luma of each video and their difference, so a
timing offset between the two renders shows up as a shifted ramp -- no images
needed.
"""
import argparse
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np  # noqa: E402
from tools.wiki_diff import decode  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--from", dest="t0", type=float, default=0.0)
    ap.add_argument("--to", dest="t1", type=float, default=1e9)
    ap.add_argument("--fps", type=float, default=60.0)
    ap.add_argument("--scale", default="320x180")
    ap.add_argument("--step", type=int, default=1, help="print every Nth frame")
    args = ap.parse_args()
    w, h = args.scale.lower().split("x")
    scale = (int(w), int(h))
    a = decode(args.a, scale).mean(axis=(1, 2, 3))
    b = decode(args.b, scale).mean(axis=(1, 2, 3))
    n = min(len(a), len(b))
    print(f"frames rtm={len(a)} ce={len(b)}")
    lo, hi = int(args.t0 * args.fps), min(int(args.t1 * args.fps), n)
    print("  f    t      rtm     ce     diff")
    for i in range(lo, hi, args.step):
        print(f"{i:4d} {i/args.fps:5.2f} {a[i]:8.3f} {b[i]:8.3f} {a[i]-b[i]:+8.3f}")


if __name__ == "__main__":
    main()
