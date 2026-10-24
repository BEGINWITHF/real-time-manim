# -*- coding: utf-8 -*-
"""Full source of the two samples in 08-BarChart.md (identical to the code blocks in the page).

Usage: python 08-BarChart.py <scene name>...
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

from real_time_manim import (  # noqa: E402
    BarChart, DOWN, FadeIn, GREY_B, Scene, Text, UP, WHITE, YELLOW,
    Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait  # noqa: E402
from real_time_manim.record import fast_record_scene  # noqa: E402


# ===== Sample 1: BarChart construction + get_bar_labels ===================
class BasicDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("08-BarChart", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        chart = BarChart(values=[-4, 6, -2, 3],   #parameter "values": may be negative; negative bars point down automatically
                         bar_names=["one", "two", "three", "four"],   #parameter "bar_names": x-axis labels
                         y_range=[-7, 9, 2],   #parameter "y_range": a 2-tuple fills in the step automatically
                         y_length=5.5, x_length=10,   #on-screen length of both axes
                         x_axis_config={"font_size": 24})   #forwarded to Axes: x-axis tick font size
        labels = chart.get_bar_labels(color=WHITE, font_size=24)   #"get_bar_labels": top-of-bar value labels (only returns; add them yourself)
        win.play(FadeIn(chart), run_time=0.8)   #the whole coordinate system and the bars fade in
        win.play(FadeIn(labels), run_time=0.4)   #the value labels fade in
        win.play(Wait(0.8))   #wait 0.8s
        win.close()   #close the RTM window


# ===== Sample 2: change_bar_values changes bar heights in place ===========
class ChangeValuesDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("08-change_bar_values", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        chart = BarChart(values=[3, 4, 2],   #starting bar heights
                         bar_names=["A", "B", "C"],
                         y_range=[0, 10, 2],
                         y_length=5, x_length=9,
                         x_axis_config={"font_size": 24})
        lab = Text("chart.animate.change_bar_values(...)", font_size=24,
                   color=GREY_B).to_edge(UP).shift(DOWN * 0.9)   #place the caption below the title
        win.play(FadeIn(chart), FadeIn(lab), run_time=0.8)   #the coordinate system and the caption appear together
        win.play(chart.animate.change_bar_values([7, 5, 3]),   #"change_bar_values": change bar heights in place
                 run_time=1.0)   #smooth transition through .animate
        win.play(chart.animate.change_bar_values([1, 2, 9]),
                 run_time=1.0)   #change them again
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window


SCENES = [
    ("08-BarChart-basic", BasicDemo),
    ("08-BarChart-changevalues", ChangeValuesDemo),
]

PAIRS = [
    ("08-BarChart-basic", ["08-BarChart-basic"]),
    ("08-BarChart-changevalues", ["08-BarChart-changevalues"]),
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
