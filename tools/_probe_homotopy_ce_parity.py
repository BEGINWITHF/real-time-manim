# -*- coding: utf-8 -*-
"""RTM Homotopy vs manim CE Homotopy, point by point.

    python tools/_probe_homotopy_ce_parity.py
"""
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from manim import Rectangle, Square, Circle, YELLOW, DOWN, linear  # noqa: E402
import manim.animation.movement as movement  # noqa: E402
from real_time_manim.vulkan_bind import Homotopy as RtmHomotopy  # noqa: E402

RUN = 2.0


def wave(x, y, z, t):
    return (x, y + 0.45 * np.sin(2.2 * x + 2.0 * np.pi * t), z)


def rtm_points(mob, alpha):
    anim = RtmHomotopy(wave, mob, run_time=RUN, rate_func=linear)
    anim.begin(0.0)
    anim.interpolate(alpha * RUN)
    return np.asarray(mob.points, dtype=float).copy()


def ce_points(mob, alpha):
    anim = movement.Homotopy(wave, mob, run_time=RUN, rate_func=linear)
    anim.begin()
    anim.interpolate(alpha)
    return np.asarray(mob.points, dtype=float).copy()


def check(label, factory, alphas=(0.25, 0.5, 0.75)):
    worst = 0.0
    for alpha in alphas:
        a = rtm_points(factory(), alpha)
        b = ce_points(factory(), alpha)
        if a.shape != b.shape:
            print("  %-10s alpha=%.2f SHAPE %s vs %s"
                  % (label, alpha, a.shape, b.shape))
            return False
        d = float(np.abs(a - b).max())
        if d > 1e-9:
            print("  %-10s alpha=%.2f max|d|=%.6g" % (label, alpha, d))
            print("    RTM y:", np.round(a[:, 1], 4).tolist())
            print("    CE  y:", np.round(b[:, 1], 4).tolist())
        worst = max(worst, d)
    print("  %-10s max |RTM - CE| = %.6g" % (label, worst))
    return worst < 1e-9


def main():
    ok = True
    ok &= check("Rectangle", lambda: Rectangle(width=4.4, height=1.6)
                .set_fill(YELLOW, 0.35).shift(DOWN * 1.2))
    ok &= check("Square", lambda: Square(side_length=2).shift(DOWN))
    ok &= check("Circle", lambda: Circle(radius=1.2).shift(DOWN))
    print("PARITY OK" if ok else "PARITY MISMATCH")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
