# -*- coding: utf-8 -*-
"""Full source of the three samples in 05-Function-Graphs.md (identical to the code blocks in the page).

Usage: python 05-Function-Graphs.py <clip name>...
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
    Scene, Axes, NumberPlane, FunctionGraph, Text, np,
    YELLOW, RED, GREEN, BLUE, ORANGE, GREY_B, UP, DOWN, TAU,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: plot and discontinuities ================================
class PlotDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("05-plot", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = NumberPlane(x_range=[-3, 3, 1], y_range=[-4, 4, 1])   # coordinate system with a grid
        f = lambda x: max(-60, min(60, (x**2 - 2) / (x**2 - 4)))   # vertical asymptotes at -2 and 2; clamp y to ±60 first: near the poles floating point produces huge values of 1e14 that cannot be drawn
        lab = Text("plot(discontinuities=[-2,2], dt=0.1)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # parameter summary label
        win.play(Create(ax), run_time=0.7)   # draw the coordinate grid
        win.play(FadeIn(lab), run_time=0.3)   # the summary label fades in

        bad = ax.plot(f, color=RED)   # no discontinuity points declared: at -2 and 2 a vertical line "joins them up"
        win.play(Create(bad), run_time=1.0)   # look at the wrong way first
        win.play(FadeOut(bad), run_time=0.4)   # remove the wrong way

        good = ax.plot(f, discontinuities=[-2, 2], dt=0.1,   # parameters "discontinuities"/"dt": declare the discontinuity points and the tolerance
                       color=GREEN, use_smoothing=False)   # parameter "use_smoothing": turning smoothing off on steep stretches is more truthful
        win.play(Create(good), run_time=1.2)   # now look at the right way
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


# ===== Sample 2: FunctionGraph without a coordinate system ===============
class FunctionGraphDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("05-FunctionGraph", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        g1 = FunctionGraph(lambda t: np.cos(3 * t), x_range=[-4, 4], color=BLUE)   # cosine curve
        g2 = FunctionGraph(lambda t: np.sin(3 * t), x_range=[-4, 4], color=GREEN)   # sine curve
        lab = Text("FunctionGraph(cos 3t) vs FunctionGraph(sin 3t)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # method summary label
        win.play(Create(g1), run_time=0.9)   # draw the cosine curve
        win.play(Create(g2), run_time=0.9)   # draw the sine curve (half a grid cell out of phase)
        win.play(FadeIn(lab), run_time=0.4)   # the summary label fades in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


# ===== Sample 3: plot_parametric_curve ===================================
class ParametricCurveDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("05-parametric_curve", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[-2, 2, 1], y_range=[-2, 2, 1],
                  x_length=6, y_length=6)   # square framing, so the Lissajous figure is not distorted
        curve = ax.plot_parametric_curve(   # "plot_parametric_curve": draw a curve from a parametric equation
            lambda t: np.array([np.sin(3 * t), np.sin(4 * t), 0]),   # x=sin(3t), y=sin(4t)
            t_range=[0, TAU], color=ORANGE)   # the parameter "t_range" is passed through **kwargs
        lab = Text("plot_parametric_curve(sin(3t), sin(4t))",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # parameter summary label
        win.play(Create(ax), run_time=0.6)   # draw the coordinate system
        win.play(Create(curve), run_time=1.4)   # draw the Lissajous curve
        win.play(FadeIn(lab), run_time=0.4)   # the summary label fades in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


SCENES = [
    ("05-Function-Graphs-plot", PlotDemo),
    ("05-Function-Graphs-functiongraph", FunctionGraphDemo),
    ("05-Function-Graphs-parametric", ParametricCurveDemo),
]

PAIRS = [
    ("05-Function-Graphs-plot", ["05-Function-Graphs-plot"]),
    ("05-Function-Graphs-functiongraph", ["05-Function-Graphs-functiongraph"]),
    ("05-Function-Graphs-parametric", ["05-Function-Graphs-parametric"]),
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
