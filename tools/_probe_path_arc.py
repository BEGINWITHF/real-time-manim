# -*- coding: utf-8 -*-
"""Does the play-level ``path_arc`` reach the animation?  (numeric, no render)

``LinearTransformationScene.apply_transposed_matrix`` puts ``path_arc`` in the
kwargs it hands to ``play`` (vector_space_scene.py:1212-1217).  manim's
``Scene.compile_animations`` forwards every play kwarg to every animation with
``setattr``; ``Transform.path_arc`` is a property whose setter rebuilds
``path_func``.  This probe builds the same animation, optionally applies the
attribute the way each engine does, and prints the interpolated geometry of a
sheared ``NumberPlane`` so the two behaviours can be compared to the video.

    python tools/_probe_path_arc.py
"""
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from real_time_manim import NumberPlane  # noqa: E402
from real_time_manim.manim.animation.transform import (  # noqa: E402
    ApplyPointwiseFunction,
)
from real_time_manim.manim.utils.space_ops import angle_of_vector  # noqa: E402
from real_time_manim.manim.constants import RIGHT, UP  # noqa: E402

FG = {
    "x_range": np.array([-14.2222, 14.2222, 1.0]),
    "y_range": np.array([-14.2222, 14.2222, 1.0]),
    "faded_line_ratio": 1,
}
RUN = 1.2


def shear(p):
    m = np.array([[1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    return np.dot(p, m)


def net_rotation():
    return np.mean([angle_of_vector(shear(RIGHT)),
                    angle_of_vector(shear(UP)) - np.pi / 2])


def _all_points(mob):
    pts = [np.asarray(m.get_points(), dtype=float)
           for m in mob.family_members_with_points()]
    return np.vstack([p for p in pts if len(p)])


def probe(apply_play_kwarg):
    plane = NumberPlane(**FG)
    anim = ApplyPointwiseFunction(shear, plane, run_time=RUN)
    if apply_play_kwarg:
        setattr(anim, "path_arc", net_rotation())
    anim.begin()
    out = []
    for i in range(1, 72):
        alpha = i / 72.0
        anim.interpolate(alpha)
        pts = _all_points(plane)
        out.append((i, float(pts[:, 1].min()), float(pts[:, 1].max()),
                    float(pts[:, 0].min()), float(pts[:, 0].max())))
    return out


def main():
    nr = net_rotation()
    print("net_rotation = %.6f rad (%.3f deg)" % (nr, np.degrees(nr)))
    for label, flag in (("rtm (no kwarg forwarded)", False),
                        ("ce (setattr path_arc)", True)):
        rows = probe(flag)
        i, ymin, ymax, xmin, xmax = rows[39]
        print("%-26s frame40: y[%.4f .. %.4f]  x[%.4f .. %.4f]  y-max factor %.4f"
              % (label, ymin, ymax, xmin, xmax, ymax / rows[0][2]))
        # a couple more frames so the curve is visible
        for k in (1, 20, 40, 60, 71):
            i, ymin, ymax, xmin, xmax = rows[k - 1]
            print("     i=%2d  ymax=%.4f  xmin=%.4f" % (i, ymax, xmin))


if __name__ == "__main__":
    main()
