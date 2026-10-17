# -*- coding: utf-8 -*-
"""Numeric look at the deformed top edge RTM now submits."""
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from manim import Rectangle, YELLOW, DOWN, linear  # noqa: E402
from real_time_manim.vulkan_bind import Homotopy  # noqa: E402

RUN = 2.0


def wave(x, y, z, t):
    return (x, y + 0.45 * np.sin(2.2 * x + 2.0 * np.pi * t), z)


def cubic(p0, p1, p2, p3, ts):
    ts = ts[:, None]
    return ((1 - ts) ** 3 * p0 + 3 * (1 - ts) ** 2 * ts * p1
            + 3 * (1 - ts) * ts ** 2 * p2 + ts ** 3 * p3)


for alpha in (0.0, 0.25, 0.5, 0.75):
    rect = Rectangle(width=4.4, height=1.6, color=YELLOW).set_fill(YELLOW, 0.35).shift(DOWN * 1.2)
    anim = Homotopy(wave, rect, run_time=RUN, rate_func=linear)
    anim.begin(0.0)
    anim.interpolate(alpha * RUN)
    pts = np.asarray(rect.points, dtype=float)
    top = pts[0:4]                      # anchor, h1, h2, anchor
    ts = np.linspace(0, 1, 201)
    curve = cubic(top[0], top[1], top[2], top[3], ts)
    chord = top[0] + ts[:, None] * (top[3] - top[0])
    dev = np.abs(curve[:, 1] - chord[:, 1]).max()
    # centre of the frame is manim x = 0; find the curve y there
    yc = curve[np.argmin(np.abs(curve[:, 0]))]
    print("alpha=%.2f  anchors y=%s" % (alpha, np.round(top[[0, 3], 1], 3).tolist()))
    print("          handles y=%s" % np.round(top[[1, 2], 1], 3).tolist())
    print("          curve y-range=%.3f..%.3f  max dev from chord=%.3f  y@x=0: %.3f (x=%.3f)"
          % (curve[:, 1].min(), curve[:, 1].max(), dev, yc[1], yc[0]))
    print("          true wave y@x=0: %.3f" % (-0.4 + 0.45 * np.sin(2 * np.pi * alpha)))
