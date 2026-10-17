# -*- coding: utf-8 -*-
"""Inspect the stroke colour arrays of the NumberPlane lines a
LinearTransformationScene builds -- numeric, no rendering, no images.

Both the vendored manim (what RTM draws from) and the installed ManimCE can be
probed: the module is chosen by `--manim {rtm,ce}`.

    python tools/_probe_plane_strokes.py --manim rtm
    python tools/_probe_plane_strokes.py --manim ce
"""
import argparse
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manim", choices=("rtm", "ce"), default="rtm")
    args = ap.parse_args()

    if args.manim == "rtm":
        from real_time_manim.manim.mobject.graphing.coordinate_systems import (
            NumberPlane,
        )
    else:
        from manim.mobject.graphing.coordinate_systems import NumberPlane

    # the two planes LinearTransformationScene.setup() builds
    bg = NumberPlane(
        color="GREY",
        axis_config={"color": "GREY"},
        background_line_style={"stroke_color": "GREY", "stroke_width": 1},
    )
    fg = NumberPlane(
        x_range=np.array([-14.2222, 14.2222, 1.0]),
        y_range=np.array([-14.2222, 14.2222, 1.0]),
        faded_line_ratio=1,
    )

    for name, plane in (("background", bg), ("foreground", fg)):
        print("=" * 60)
        print(name, "num submobjects:", len(plane.submobjects))
        for grp_name in ("background_lines", "faded_lines"):
            grp = getattr(plane, grp_name, None)
            if grp is None:
                continue
            print("  %s: %d lines" % (grp_name, len(grp.submobjects)))
            shown = 0
            for ln in grp.submobjects:
                srgbas = np.asarray(ln.get_stroke_rgbas(), dtype=float)
                frgbas = np.asarray(ln.get_fill_rgbas(), dtype=float)
                pts = np.asarray(ln.get_points(), dtype=float)
                gpts = ln.get_gradient_start_and_end_points()
                print("    line pts=%d stroke_rows=%d fill_rows=%d "
                      "sw=%s so=%s" % (len(pts), len(srgbas), len(frgbas),
                                       ln.get_stroke_width(),
                                       getattr(ln, "stroke_opacity", None)))
                print("      stroke rgbas:")
                for r in srgbas:
                    print("        " + np.array2string(r, precision=4))
                print("      gradient pts: %s -> %s"
                      % (np.array2string(np.asarray(gpts[0]), precision=3),
                         np.array2string(np.asarray(gpts[1]), precision=3)))
                print("      p0=%s pN=%s"
                      % (np.array2string(pts[0], precision=3),
                         np.array2string(pts[-1], precision=3)))
                shown += 1
                if shown >= 2:
                    break


if __name__ == "__main__":
    main()
