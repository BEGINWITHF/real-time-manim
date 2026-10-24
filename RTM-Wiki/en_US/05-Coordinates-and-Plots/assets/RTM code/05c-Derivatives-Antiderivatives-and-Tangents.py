# -*- coding: utf-8 -*-
"""Full source of the three samples in 05c-Derivatives-Antiderivatives-and-Tangents.md (identical to the code blocks in the page).

Usage: python 05c-Derivatives-Antiderivatives-and-Tangents.py <clip name>...
With no arguments it renders every clip and concatenates the page's three sample videos.
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
    Scene, Axes, NumberPlane, Dot, Line, Text, PI,
    YELLOW, PURPLE_B, GREEN, ORANGE, GREY_B, UP, DOWN, UR, DL, DR,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: taking points on a curve, i2gp / i2gc ===================
class TakePointDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("05c-input_to_graph", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = NumberPlane(x_range=[-2, 5, 1], y_range=[-1, 7, 1],   # coordinate system with a grid
                         background_line_style={"stroke_opacity": 0.4})   # dim the grid lines so they do not steal the show
        curve = ax.plot(lambda x: x**2, color=PURPLE_B)   # the parabola y=x²
        lab = Text("i2gp(x) -> screen point   i2gc(x) -> data coords",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # method summary label
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   # the coordinate system and the label enter together
        win.play(Create(curve), run_time=0.8)   # draw the parabola

        pos = ax.input_to_graph_point(x=PI, graph=curve)   # "input_to_graph_point" (alias i2gp): the screen point at x
        dot = Dot(pos, color=YELLOW)   # once the screen point is in hand, place a Dot directly
        tag = Text("i2gp(PI)", font_size=24, color=YELLOW).next_to(dot, UR, buff=0.2)
        win.play(FadeIn(dot), FadeIn(tag), run_time=0.4)   # the yellow dot and the label fade in

        coords = ax.input_to_graph_coords(x=2.0, graph=curve)   # "input_to_graph_coords" (alias i2gc): the data coordinates at x
        tag2 = Text("i2gc(2.0)=(%.1f, %.1f)" % coords,   # show the data coordinates read back
                    font_size=24, color=GREEN).next_to(ax.c2p(2, 4), DR, buff=0.3)
        win.play(FadeIn(tag2), run_time=0.4)   # the read-back data coordinates fade in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


# ===== Sample 2: derivative and antiderivative curves ====================
class DerivativeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("05c-derivative_antiderivative", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[-1, 2.5, 1], y_range=[-2, 7, 1],
                  x_length=9, y_length=5.5)   # framing that encloses the three curves
        c1 = ax.plot(lambda x: x**2, color=PURPLE_B)   # the original curve y=x²
        lab = Text("f=x^2   f'=2x   F=x^3/3 (y_intercept=0)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # method summary label
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   # the coordinate system and the label enter together
        win.play(Create(c1), run_time=0.7)   # draw the original curve

        c2 = ax.plot_derivative_graph(c1, color=GREEN)   # "plot_derivative_graph": numerical differentiation, drawing 2x
        win.play(Create(c2), run_time=0.7)   # draw the derivative (a line through the origin)

        c3 = ax.plot_antiderivative_graph(c1, y_intercept=0,   # "plot_antiderivative_graph": the trapezoid rule integrating from 0 to x
                                           color=ORANGE)   # parameter "y_intercept": the constant of integration (the y-axis intercept)
        win.play(Create(c3), run_time=0.9)   # draw the antiderivative x³/3
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


# ===== Sample 3: slope_of_tangent / angle_of_tangent dynamic tangent =====
class TangentDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("05c-slope_of_tangent", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[-3, 3, 1], y_range=[-1, 7, 1],
                  x_length=9, y_length=5.5)   # gentle parabola framing
        f = lambda x: 0.25 * x**2 + 1   # a gentler parabola, so the tangents are not too steep
        curve = ax.plot(f, color=PURPLE_B)   # the original curve
        lab = Text("slope_of_tangent(x) + angle_of_tangent(x)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # method summary label
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   # the coordinate system and the label enter together
        win.play(Create(curve), run_time=0.8)   # draw the curve

        for x0, side in ((-2, DL), (0, UP), (2, DR)):   # draw a tangent at three positions
            s = ax.slope_of_tangent(x=x0, graph=curve)   # "slope_of_tangent": the tangent slope, numerically
            ang = ax.angle_of_tangent(x=x0, graph=curve)   # "angle_of_tangent": the angle between the tangent and the x axis (radians)
            p = ax.c2p(x0, f(x0))   # the tangent point
            half = 1.6   # half the tangent length (data units)
            pa = ax.c2p(x0 - half, f(x0) + s * (-half))   # extrapolate the two end points from the slope
            pb = ax.c2p(x0 + half, f(x0) + s * half)
            tline = Line(pa, pb, color=GREEN)   # the tangent segment
            tag = Text("x=%+d  slope=%.1f  ang=%.2frad" % (x0, s, ang),   # show the slope and the angle together
                       font_size=20, color=GREY_B).next_to(p, side, buff=0.25)
            win.play(Create(tline), FadeIn(tag), run_time=0.5)   # the tangent and the readout enter
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


SCENES = [
    ("05c-Derivatives-Antiderivatives-and-Tangents-takepoint", TakePointDemo),
    ("05c-Derivatives-Antiderivatives-and-Tangents-deriv", DerivativeDemo),
    ("05c-Derivatives-Antiderivatives-and-Tangents-tangent", TangentDemo),
]

PAIRS = [
    ("05c-Derivatives-Antiderivatives-and-Tangents-takepoint", ["05c-Derivatives-Antiderivatives-and-Tangents-takepoint"]),
    ("05c-Derivatives-Antiderivatives-and-Tangents-deriv", ["05c-Derivatives-Antiderivatives-and-Tangents-deriv"]),
    ("05c-Derivatives-Antiderivatives-and-Tangents-tangent", ["05c-Derivatives-Antiderivatives-and-Tangents-tangent"]),
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
