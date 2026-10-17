# -*- coding: utf-8 -*-
"""How far along edge (1,4) is drawn, frame by frame, RTM vs CE."""
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

V4 = np.array([348.5, 89.0])
V1 = np.array([307.5, 135.0])
D = V1 - V4


def ink(img, f, pt, half=3):
    x0, y0 = int(round(pt[0])), int(round(pt[1]))
    win = img[f, max(0, y0 - half):y0 + half + 1,
              max(0, x0 - half):x0 + half + 1].astype(float)
    return float(win.mean(axis=2).max())


def edge_map(img, f, lo=0.18, hi=0.80, n=40):
    """A 40-char bitmap of the edge's drawn samples, dot-free stretch.

    Sampled only where NEITHER LabeledDot covers the segment (radius ~9.6 px
    at 480x270 = ~0.155 of this 61.7 px segment), so the vertices' own ink
    cannot be mistaken for the edge.  s=0 is vertex 4, s=1 is vertex 1.
    """
    return "".join("#" if ink(img, f, V4 + D * s, half=2) > 40 else "."
                   for s in np.linspace(lo, hi, n))


def dot_ink(img, f):
    """Peak brightness at the dot's own centre."""
    return float(img[f, 86:93, 344:353].astype(float).mean(axis=2).max())


print("  f    edge RTM (s 0.18 -> 0.80)   / CE                       "
      "  dot peak")
for f in range(82, 140, 2):
    print("  %3d   %s / %s   %3.0f/%3.0f"
          % (f, edge_map(a, f), edge_map(b, f), dot_ink(a, f), dot_ink(b, f)))
