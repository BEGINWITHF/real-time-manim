# -*- coding: utf-8 -*-
"""Does RTM's Homotopy deform EVERY point of the rectangle (anchors AND
bezier handles), the way manim CE's Homotopy does?

    python tools/_probe_homotopy_points.py
"""
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from real_time_manim import Rectangle, YELLOW, DOWN  # noqa: E402
from real_time_manim.animations.homotopy import Homotopy  # noqa: E402


def wave(x, y, z, t):
    return (x, y + 0.45 * np.sin(2.2 * x + 2.0 * np.pi * t), z)


def show(label, pts):
    p = np.asarray(pts, dtype=float)
    print("%s: n=%d" % (label, len(p)))
    print("   x:", np.round(p[:, 0], 3).tolist())
    print("   y:", np.round(p[:, 1], 3).tolist())


rect = Rectangle(width=4.4, height=1.6, color=YELLOW).set_fill(YELLOW, 0.35).shift(DOWN * 1.2)
orig = rect.points.copy()
show("orig", orig)

anim = Homotopy(wave, rect, run_time=2.0)
anim.begin(0.0)
for alpha, t in ((0.25, 0.5), (0.5, 1.0), (0.75, 1.5)):
    anim.interpolate(t)
    show("t=%.2f alpha=%.2f" % (t, alpha), rect.points)
    dev = rect.points[:, 1] - orig[:, 1]
    print("   dy:", np.round(dev, 3).tolist())
anim.finish()
show("after finish", rect.points)

# ---- what does manim CE's own Homotopy do to the same shape? -------------
print("\n--- manim CE Homotopy on an identical Rectangle ---")
import manim  # noqa: E402
from manim import Homotopy as CEHomotopy  # noqa: E402

r2 = manim.Rectangle(width=4.4, height=1.6).set_fill(YELLOW, 0.35).shift(DOWN * 1.2)
o2 = r2.points.copy()
ce = CEHomotopy(lambda x, y, z, t: (x, y + 0.45 * np.sin(2.2 * x + 2 * np.pi * t), z), r2)
ce.begin()
ce.interpolate_mobject(0.5)
print("CE n=%d" % len(r2.points))
print("CE dy:", np.round(r2.points[:, 1] - o2[:, 1], 3).tolist())
