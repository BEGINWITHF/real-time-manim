# -*- coding: utf-8 -*-
"""Full source of the three samples in 05b-Plot-Labels-and-Helper-Lines.md (identical to the code blocks in the page).

Usage: python 05b-Plot-Labels-and-Helper-Lines.py <clip name>...
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
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    Scene, Axes, Text,
    YELLOW, TEAL, PURPLE_B, GREEN, GREY, GREY_B, UP, DOWN, DL,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: plot_implicit_curve implicit curve ======================
class ImplicitDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("05b-plot_implicit_curve", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[-3, 3, 1], y_range=[-2, 2, 1],
                  x_length=8, y_length=5)   # range matches radius 2
        circle = ax.plot_implicit_curve(lambda x, y: x**2 + y**2 - 4,   # "plot_implicit_curve": the level curve of f(x,y)=0
                                        color=TEAL)   # x²+y²=4, i.e. the circle of radius 2
        lab = Text("plot_implicit_curve(x^2+y^2-4=0)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # parameter summary label
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   # the coordinate system and the label enter together
        win.play(Create(circle), run_time=1.2)   # draw the implicit circle
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


# ===== Sample 2: get_graph_label + get_T_label curve labels ==============
class LabelsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("05b-graph_label_T_label", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[-4, 4, 1], y_range=[-1, 7, 1],
                  x_length=9, y_length=5.5)   # parabola framing
        curve = ax.plot(lambda x: x**2, color=PURPLE_B)   # the parabola y=x²
        lab = Text("get_graph_label(x_val=-2) + get_T_label(x_val=4)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # parameter summary label
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   # the coordinate system and the label enter together
        win.play(Create(curve), run_time=0.8)   # draw the parabola

        label = ax.get_graph_label(curve, "x^2", x_val=-2,   # "get_graph_label": put a label at x=-2 on the curve
                                   direction=DL, dot=True)   # parameter "dot": also add a dot on the curve
        win.play(FadeIn(label), run_time=0.5)   # the label and the dot fade in

        t_label = ax.get_T_label(x_val=4, graph=curve,   # "get_T_label": the marker group at x=4
                                 label="x-value")   # triangle + vertical line + text label
        win.play(FadeIn(t_label), run_time=0.5)   # the T marker group fades in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


# ===== Sample 3: get_vertical_lines_to_graph + secant group ==============
class SecantDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("05b-secant_slope_group", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[-1, 5, 1], y_range=[-1, 7, 1],
                  x_length=9, y_length=5.5)   # parabola framing
        curve = ax.plot(lambda x: x**2, color=PURPLE_B)   # the parabola y=x²
        lab = Text("get_vertical_lines_to_graph(9) + secant(dx=1)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # parameter summary label
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   # the coordinate system and the label enter together
        win.play(Create(curve), run_time=0.8)   # draw the parabola

        vlines = ax.get_vertical_lines_to_graph(curve, x_range=[0, 4],   # "get_vertical_lines_to_graph": pull vertical dashed lines evenly up to the curve
                                                num_lines=9, color=GREY)   # parameter "num_lines": number of dashed lines
        win.play(Create(vlines), run_time=0.6)   # draw the vertical dashed line group
        win.play(FadeOut(vlines), run_time=0.3)   # remove the dashed lines to make room for the secant group

        group = ax.get_secant_slope_group(x=2.0, graph=curve, dx=1.0,   # "get_secant_slope_group": Δx horizontal line + Δy vertical line + secant line as one group
                                          dx_label="dx", dy_label="dy",   # parameters "dx_label"/"dy_label": labels beside the lines
                                          secant_line_color=GREEN, secant_line_length=4)   # parameters "secant_line_color"/"secant_line_length": secant line style
        win.play(FadeIn(group), run_time=0.8)   # the secant group fades in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


SCENES = [
    ("05b-Plot-Labels-and-Helper-Lines-implicit", ImplicitDemo),
    ("05b-Plot-Labels-and-Helper-Lines-labels", LabelsDemo),
    ("05b-Plot-Labels-and-Helper-Lines-secant", SecantDemo),
]

PAIRS = [
    ("05b-Plot-Labels-and-Helper-Lines-implicit", ["05b-Plot-Labels-and-Helper-Lines-implicit"]),
    ("05b-Plot-Labels-and-Helper-Lines-labels", ["05b-Plot-Labels-and-Helper-Lines-labels"]),
    ("05b-Plot-Labels-and-Helper-Lines-secant", ["05b-Plot-Labels-and-Helper-Lines-secant"]),
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
