# -*- coding: utf-8 -*-
"""Event timeline of the `add` sample: when does each element appear?"""
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from tools.issues_baseline import entries, twin  # noqa: E402
from tools.wiki_diff import decode  # noqa: E402

rtm = [p for p, d in entries() if "add.mp4" in p][0]
ce = twin(rtm)
a = decode(rtm, (480, 270))
b = decode(ce, (480, 270))
n = min(len(a), len(b))

# 480x270: 33.75 px/unit, centre (240, 135)
WIN = {
    "title": (96, 300, 10, 45),        # page title band
    "label": (96, 380, 46, 62),        # signature label
    "v1": (296, 320, 124, 146),        # existing vertex 1  (2, 0)
    "v2": (195, 218, 66, 87),          # existing vertex 2  (-1, 1.732)
    "v4": (336, 360, 78, 100),         # NEW vertex 4       (3.2, 1.2)
    "v5": (336, 360, 172, 194),        # NEW vertex 5       (3.2, -1.4)
    "e45": (338, 356, 130, 168),       # edge (4,5) middle
}


def first_ink(img, box, thr=40):
    x0, x1, y0, y1 = box
    for f in range(n):
        if (img[f, y0:y1, x0:x1].astype(float).mean(axis=2) > thr).any():
            return f
    return None


def ink_count(img, box, f, thr=40):
    x0, x1, y0, y1 = box
    return int((img[f, y0:y1, x0:x1].astype(float).mean(axis=2) > thr).sum())


print("%-6s %8s %8s %6s" % ("where", "RTM", "CE", "delta"))
for name, box in WIN.items():
    fa, fb = first_ink(a, box), first_ink(b, box)
    d = "-" if fa is None or fb is None else str(fa - fb)
    print("%-6s %8s %8s %6s" % (name, fa, fb, d))

print()
print("ink count in the v4 window over time (RTM / CE):")
for f in range(80, 136, 4):
    print("  f%3d  %3d / %3d" % (f, ink_count(a, WIN["v4"], f),
                                 ink_count(b, WIN["v4"], f)))
