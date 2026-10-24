# -*- coding: utf-8 -*-
"""Full source of the two samples in 04-Grids-and-Complex-Plane.md (identical to the code blocks in the page).

Usage: python 04-Grids-and-Complex-Plane.py <clip name>...
With no arguments it renders every clip and concatenates the page's two sample videos.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
ASSETS = os.path.dirname(HERE)
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

from real_time_manim import (
    Scene, NumberPlane, ComplexPlane, Dot, MathTex, Text,
    YELLOW, TEAL, BLUE_E, GREEN, GREY_B, UP, DOWN, UR,
    Create, FadeIn, GrowArrow, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: NumberPlane grid canvas ==================================
class NumberPlaneDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("04-NumberPlane", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        plane = NumberPlane(
            background_line_style={"stroke_color": TEAL, "stroke_width": 4, "stroke_opacity": 0.6},   # parameter "background_line_style": style of the main grid lines
            faded_line_ratio=2,   # parameter "faded_line_ratio": subdivide each cell into 2x2 faded lines
        )
        lab = Text("faded_line_ratio=2  (each cell -> 4)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # parameter summary label
        win.play(Create(plane), run_time=1.2)   # draw the main grid + faded subdivision lines
        win.play(FadeIn(lab), run_time=0.3)   # the summary label fades in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


# ===== Sample 2: ComplexPlane complex plane ===============================
class ComplexPlaneDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("04-ComplexPlane", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        cplane = ComplexPlane(
            x_range=[-3, 3, 1], y_range=[-3, 3, 1],   # range/step parameters are the same as for NumberPlane
            background_line_style={"stroke_color": BLUE_E, "stroke_width": 2},   # switch the grid lines to blues
        ).add_coordinates()   # the y-axis labels carry an i automatically (1i, 2i…)
        d1 = Dot(cplane.n2p(2 + 1j), color=YELLOW)   # "n2p": convert the complex number 2+i straight into a scene point
        label = MathTex("2+i").next_to(d1, UR, buff=0.2)   # complex-number label
        vec = cplane.get_vector([1, -2], color=GREEN)   # "get_vector": an arrow from the origin to (1,-2)
        lab = Text("n2p(2+1j) + get_vector([1,-2])",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # method summary label
        win.play(Create(cplane), run_time=1.0)   # draw the complex plane (including the i labels)
        win.play(FadeIn(lab), run_time=0.3)   # the summary label fades in
        win.play(FadeIn(d1), Write(label), run_time=0.6)   # the yellow dot and the "2+i" label enter
        win.play(GrowArrow(vec), run_time=0.6)   # the green arrow grows out of the origin
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


SCENES = [
    ("04-Grids-and-Complex-Plane-numberplane", NumberPlaneDemo),
    ("04-Grids-and-Complex-Plane-complexplane", ComplexPlaneDemo),
]

PAIRS = [
    ("04-Grids-and-Complex-Plane-numberplane", ["04-Grids-and-Complex-Plane-numberplane"]),
    ("04-Grids-and-Complex-Plane-complexplane", ["04-Grids-and-Complex-Plane-complexplane"]),
]


def concat(names, dst):
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    lst = os.path.join(HERE, "concat.txt")
    with open(lst, "w", encoding="utf-8") as fh:
        for n in names:
            fh.write("file '%s'\n" % os.path.join(OUT, n + ".mp4"))
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", lst, "-c", "copy", dst],
        check=True)
    return dst


if __name__ == "__main__":
    only = set(sys.argv[1:])
    for name, cls in SCENES:
        if only and name not in only:
            continue
        print("=" * 30, name)
        try:
            fast_record_scene(cls, out_path=os.path.join(OUT, name + ".mp4"),
                              verbose=True)
        except Exception:
            import traceback
            traceback.print_exc()

    if not only:
        for out_name, names in PAIRS:
            dst = os.path.join(ASSETS, "RTM output", out_name + ".mp4")
            concat(names, dst)
            print("concat ->", dst, os.path.getsize(dst), "bytes")
