# -*- coding: utf-8 -*-
"""Full source for the two samples in 02b-Lines-and-Plots.md (identical to the code blocks in the page).

Usage: python 02b-Lines-and-Plots.py <scene names>...
With no arguments it renders every scene and concatenates the page's two videos.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
ASSETS = os.path.dirname(HERE)
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    Scene, Axes, Dot, Line, Text, VGroup,
    YELLOW, RED, BLUE, GREEN, GREY, GREY_B, GOLD_E, UP, DOWN,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: the horizontal / vertical guide-line trio ================
class GuideLinesDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02b-guide-lines", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[-4, 4, 1], y_range=[-3, 3, 1],
                  x_length=9, y_length=5.5).add_coordinates()   # a coordinate system with tick numbers
        p = ax.c2p(2, 1.5)   # target point: data coordinates (2, 1.5)
        dot = Dot(p, color=RED)   # the target-point dot
        vline = ax.get_vertical_line(p, color=BLUE)   # "get_vertical_line": a vertical dashed line from the x axis to the point
        both = ax.get_lines_to_point(ax.c2p(-3, -1), color=GREY)   # "get_lines_to_point": both a horizontal and a vertical guide line
        solid = ax.get_line_from_axis_to_point(   # "get_line_from_axis_to_point": the general version, with a chosen line class
            1, ax.c2p(3, -2), line_func=Line, color=GREEN)   # pull a solid line from the y axis (index=1) to the point
        lab = Text("vertical / lines_to_point / from_axis(1, Line)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # method description label
        win.play(Create(ax), run_time=0.8)   # draw the coordinate system
        win.play(FadeIn(lab), run_time=0.3)   # the description label fades in
        win.play(FadeIn(dot), run_time=0.3)   # the target point fades in
        win.play(Create(vline), run_time=0.6)   # the blue vertical dashed line grows from the x axis to the point
        win.play(Create(both), run_time=0.6)   # the grey horizontal and vertical guide lines
        win.play(Create(solid), run_time=0.6)   # the green solid line connects the y axis to the point
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


# ===== Sample 2: a plot_line_graph discrete line graph ====================
class LineGraphDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02b-plot_line_graph", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[0, 5, 1], y_range=[0, 5, 1],
                  x_length=8, y_length=5).add_coordinates()   # a first-quadrant coordinate system
        lg = ax.plot_line_graph(x_values=[0, 1.5, 2.8, 4],   # "plot_line_graph": joins discrete data points (not function sampling)
                                y_values=[1, 3, 4, 2.5],
                                line_color=GOLD_E, stroke_width=4)   # parameters "line_color"/"stroke_width": polyline color and stroke width
        lab = Text("plot_line_graph(x=[0,1.5,2.8,4], y=[1,3,4,2.5])",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # parameter description label
        win.play(Create(ax), run_time=0.7)   # draw the coordinate system
        win.play(FadeIn(lab), run_time=0.3)   # the description label fades in
        win.play(Create(lg["line_graph"]), run_time=1.0)   # the polyline itself (the returned VDict's "line_graph" key)
        win.play(FadeIn(lg["vertex_dots"]), run_time=0.5)   # the vertex dots (the "vertex_dots" key)
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


SCENES = [
    ("02b-Lines-and-Plots-lines", GuideLinesDemo),
    ("02b-Lines-and-Plots-linegraph", LineGraphDemo),
]

PAIRS = [
    ("02b-Lines-and-Plots-lines", ["02b-Lines-and-Plots-lines"]),
    ("02b-Lines-and-Plots-linegraph", ["02b-Lines-and-Plots-linegraph"]),
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
