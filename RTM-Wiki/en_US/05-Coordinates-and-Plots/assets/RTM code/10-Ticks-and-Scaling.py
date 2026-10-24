# -*- coding: utf-8 -*-
"""Full source of the two samples in 10-Ticks-and-Scaling.md (identical to the code blocks in the page).

Usage: python 10-Ticks-and-Scaling.py <scene name>...
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
    Axes, BLUE, Create, DOWN, FadeIn, GREY_B, LEFT, LinearBase, LogBase,
    NumberLine, Scene, Text, UP, YELLOW,
    Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait  # noqa: E402
from real_time_manim.record import fast_record_scene  # noqa: E402


# ===== Sample 1: LogBase on the y axis of Axes (log scale + 10^k labels) =
class LogBaseDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("10-LogBase", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        ax = Axes(x_range=[0, 10, 1], y_range=[-2, 6, 1], tips=False,   #data range of both axes
                  axis_config={"include_numbers": True},   #both axes carry tick numbers
                  y_axis_config={"scaling": LogBase(custom_labels=True)})   #parameter "scaling": change the y axis to a log scale
        graph = ax.plot(lambda x: x**2,   #plot y=x^2: on a log y axis it is "squashed" into a rising curve
                        x_range=[0.001, 10],   #x_min must be > 0 (LogBase's inverse_function raises ValueError for ≤0)
                        use_smoothing=False)
        lab = Text("y_axis_config={'scaling': LogBase()}",
                   font_size=24, color=GREY_B).to_edge(UP).shift(DOWN * 0.9)   #place the caption below the title
        win.play(Create(ax), FadeIn(lab), run_time=0.8)   #the axes and the caption appear together
        win.play(Create(graph), run_time=0.8)   #draw the curve
        win.play(Wait(0.8))   #wait 0.8s
        win.close()   #close the RTM window


# ===== Sample 2: LinearBase multiplying all ticks by a factor ============
class LinearBaseDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("10-LinearBase", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        base = NumberLine(x_range=[0, 6, 1], length=9,   #default scale: LinearBase(scale_factor=1.0)
                          include_numbers=True).shift(UP * 0.9 + LEFT * 0.6)
        wide = NumberLine(x_range=[0, 6, 1], length=9,   #parameter "scale_factor": multiply all ticks by 1.5
                          scaling=LinearBase(scale_factor=1.5),
                          include_numbers=True).shift(DOWN * 0.9)
        la = Text("LinearBase(scale_factor=1.0)  # default", font_size=22,
                  color=GREY_B).next_to(base, UP, buff=0.25)
        lb = Text("LinearBase(scale_factor=1.5)", font_size=22,
                  color=GREY_B).next_to(wide, DOWN, buff=0.25)
        win.play(Create(base), Create(wide), FadeIn(la), FadeIn(lb), run_time=0.8)   #the two number lines appear together
        win.play(Wait(0.8))   #wait 0.8s
        win.close()   #close the RTM window


SCENES = [
    ("10-Ticks-and-Scaling-logbase", LogBaseDemo),
    ("10-Ticks-and-Scaling-linearbase", LinearBaseDemo),
]

PAIRS = [
    ("10-Ticks-and-Scaling-logbase", ["10-Ticks-and-Scaling-logbase"]),
    ("10-Ticks-and-Scaling-linearbase", ["10-Ticks-and-Scaling-linearbase"]),
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
