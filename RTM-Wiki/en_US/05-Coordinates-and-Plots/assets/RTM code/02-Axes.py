# -*- coding: utf-8 -*-
"""Full source for the two samples in 02-Axes.md (identical to the code blocks in the page).

Usage: python 02-Axes.py <scene names>...
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

from real_time_manim import (
    Scene, Axes, Text,
    YELLOW, BLUE, GREY_B, UP, DOWN,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: Axes constructor parameters ==============================
class AxesCtorDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02-Axes", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[-4, 4, 1], y_range=[-3, 3, 1],   # parameters "x_range"/"y_range": data range and tick step
                  x_length=8, y_length=5,                   # parameters "x_length"/"y_length": on-screen physical length
                  tips=False, axis_config={"font_size": 24})   # parameter "tips": axis-end arrows; "axis_config": common parameters for both axes
        ax.add_coordinates()   # attach tick numbers to both axes
        labels = ax.get_axis_labels("x", "y")   # the two axis names x/y (you have to add them to the scene yourself)
        curve = ax.plot(lambda x: 0.5 * x**2, color=BLUE)   # draw a parabola along the way (see page 05 for the parameters)
        lab = Text("x_range=[-4,4,1]  y_range=[-3,3,1]  tips=False",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # parameter description label
        win.play(Create(ax), run_time=1.0)   # draw the coordinate system (including tick numbers)
        win.play(FadeIn(labels), FadeIn(lab), run_time=0.4)   # the axis names and the description label fade in
        win.play(Create(curve), run_time=1.0)   # draw the parabola
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


# ===== Sample 2: the list / dict forms of add_coordinates =================
class AxesAddCoordDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02-add_coordinates", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[-3, 3, 1], y_range=[-2, 2, 1], x_length=9, y_length=5)   # default tips=True (arrows at the axis ends)
        ax.add_coordinates({1: "Mon", 2: "Tue"}, [-2, 0, 2])   # "add_coordinates": x axis dict value->label, y axis list shows only the given values
        labels = ax.get_axis_labels("x", "y")   # axis names
        lab = Text("add_coordinates({1:Mon,2:Tue}, [-2,0,2])",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # parameter description label
        win.play(Create(ax), run_time=0.9)   # draw the coordinate system (including arrows and custom labels)
        win.play(FadeIn(labels), FadeIn(lab), run_time=0.4)   # the axis names and the description label fade in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


SCENES = [
    ("02-Axes-ctor", AxesCtorDemo),
    ("02-Axes-addcoordinates", AxesAddCoordDemo),
]

PAIRS = [
    ("02-Axes-ctor", ["02-Axes-ctor"]),
    ("02-Axes-addcoordinates", ["02-Axes-addcoordinates"]),
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
