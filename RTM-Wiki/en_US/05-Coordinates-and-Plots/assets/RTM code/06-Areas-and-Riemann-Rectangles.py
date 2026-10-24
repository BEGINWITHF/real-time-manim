# -*- coding: utf-8 -*-
"""Full source of the two samples in 06-Areas-and-Riemann-Rectangles.md (identical to the code blocks in the page).

Usage: python 06-Areas-and-Riemann-Rectangles.py <clip name>...
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
    Scene, Axes, Text,
    YELLOW, BLUE, BLUE_C, RED, GREEN, GREEN_B, GREEN_D, GREY_B, UP, DOWN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: get_area, the area under a curve ========================
class AreaDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("06-get_area", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[-3, 3, 1], y_range=[-2, 6, 1],
                  x_length=9, y_length=5.5).add_coordinates()   # coordinate system with tick numbers
        quad = ax.plot(lambda x: 0.5 * x**2 - 0.5, color=BLUE)   # the parabola
        lab = Text("get_area(x_range=(0,2)) + bounded_graph",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # parameter summary label
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   # the coordinate system and the label enter together
        win.play(Create(quad), run_time=0.7)   # draw the parabola

        area = ax.get_area(quad, x_range=(0, 2),   # "get_area": the area from under the curve to the x axis
                           color=(GREEN_B, GREEN_D), opacity=1)   # parameters "color"/"opacity": single colour, gradient list and opacity
        win.play(FadeIn(area), run_time=0.6)   # the green gradient area fades in
        win.play(FadeOut(area), run_time=0.3)   # remove it to make room for the between-two-curves demo

        bound = ax.plot(lambda x: 3, color=RED)   # the second curve y=3
        area2 = ax.get_area(quad, x_range=(-1.5, 1.5),   # "get_area" plus "bounded_graph": the area between the two curves
                            bounded_graph=bound, color=(BLUE_C, GREEN), opacity=0.6)
        win.play(Create(bound), run_time=0.4)   # draw the upper boundary line
        win.play(FadeIn(area2), run_time=0.6)   # the area between the two lines fades in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


# ===== Sample 2: get_riemann_rectangles ==================================
class RiemannDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("06-get_riemann_rectangles", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[-3, 3, 1], y_range=[-2, 6, 1],
                  x_length=9, y_length=5.5).add_coordinates()   # coordinate system with tick numbers
        quad = ax.plot(lambda x: 0.5 * x**2 - 0.5, color=BLUE)   # the parabola being approximated
        lab = Text("dx=0.25 left  ->  dx=0.5 center",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # parameter summary label
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   # the coordinate system and the label enter together
        win.play(Create(quad), run_time=0.7)   # draw the parabola

        rects = ax.get_riemann_rectangles(quad, x_range=[-2.5, 2.5],   # "get_riemann_rectangles": the Riemann-sum rectangle group
                                          dx=0.25,   # parameter "dx": rectangle width
                                          input_sample_type="left",   # parameter "input_sample_type": left-endpoint sampling
                                          color=YELLOW)   # parameter "color": single-colour fill (negative area colour-inverted automatically)
        win.play(FadeIn(rects), run_time=0.6)   # the left-endpoint rectangles fade in
        win.play(FadeOut(rects), run_time=0.3)   # remove them and switch to midpoint sampling

        rects2 = ax.get_riemann_rectangles(quad, x_range=[-2.5, 2.5],
                                           dx=0.5,   # wider, so there are fewer rectangles
                                           input_sample_type="center",   # midpoint sampling
                                           color=(BLUE, GREEN))   # multi-colour list: a gradient is made automatically
        win.play(FadeIn(rects2), run_time=0.6)   # the midpoint + gradient rectangles fade in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


SCENES = [
    ("06-Areas-and-Riemann-Rectangles-area", AreaDemo),
    ("06-Areas-and-Riemann-Rectangles-riemann", RiemannDemo),
]

PAIRS = [
    ("06-Areas-and-Riemann-Rectangles-area", ["06-Areas-and-Riemann-Rectangles-area"]),
    ("06-Areas-and-Riemann-Rectangles-riemann", ["06-Areas-and-Riemann-Rectangles-riemann"]),
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
