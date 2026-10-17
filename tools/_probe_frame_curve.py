# -*- coding: utf-8 -*-
"""Per-frame |diff| curve as text: which frames are bad, and in what runs.

    python tools/_probe_frame_curve.py A.mp4 B.mp4 [--threshold 4.0] [--scale 480x270]
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
    ap.add_argument("--threshold", type=float, default=4.0)
    ap.add_argument("--scale", default="480x270")
    args = ap.parse_args()
    w, h = (int(v) for v in args.scale.lower().split("x"))
    a, b = decode(args.a, (w, h)), decode(args.b, (w, h))
    n = min(len(a), len(b))
    diff = np.abs(a[:n].astype(np.int16) - b[:n].astype(np.int16)).mean(axis=(1, 2, 3))
    print("frames=%d mean=%.4f max=%.4f@f%d  >%.1f: %d"
          % (n, diff.mean(), diff.max(), int(diff.argmax()), args.threshold,
             int((diff > args.threshold).sum())))
    # runs of consecutive bad frames
    bad = diff > args.threshold
    runs = []
    i = 0
    while i < n:
        if bad[i]:
            j = i
            while j + 1 < n and bad[j + 1]:
                j += 1
            runs.append((i, j, float(diff[i:j + 1].mean())))
            i = j + 1
        else:
            i += 1
    for s, e, m in runs:
        print("  run f%d..f%d  (%d frames, mean %.2f)" % (s, e, e - s + 1, m))
    # sparkline every 6 frames
    step = max(1, n // 64)
    ramp = " .:-=+*#%@"
    mx = max(diff.max(), 1e-9)
    line = "".join(ramp[min(9, int(diff[i] / mx * 9.999))] for i in range(0, n, step))
    print("  curve (max=%.1f, step=%d):" % (mx, step))
    print("    " + line)


if __name__ == "__main__":
    main()
