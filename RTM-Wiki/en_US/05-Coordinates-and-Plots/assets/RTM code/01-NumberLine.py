# -*- coding: utf-8 -*-
"""Full source for the two samples in 01-NumberLine.md (identical to the code blocks in the page).

Usage: python 01-NumberLine.py <scene names>...
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
    Scene, NumberLine, UnitInterval, Dot, Text, VGroup,
    YELLOW, RED, GREY_B, UP, DOWN,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: basic constructor parameters =============================
class NumberLineBasicDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-NumberLine", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        line = NumberLine(x_range=[-4, 4, 1], length=8,   # parameter "x_range": data range and step; "length": total length 8
                         include_numbers=True, include_tip=True)   # parameters "include_numbers"/"include_tip": number labels + end arrow
        dot = Dot(line.n2p(2), color=RED)   # use "n2p" to turn the value 2 into a scene point (see 01b)
        lab = Text("x_range=[-4,4,1]  length=8  tip+numbers",
                   font_size=26, color=GREY_B).next_to(line, DOWN, buff=0.6)   # parameter description label
        win.play(Create(line), run_time=0.8)   # draw the whole number line (ticks, numbers, arrow)
        win.play(FadeIn(dot), FadeIn(lab), run_time=0.4)   # the red dot and the label fade in
        win.play(dot.animate.move_to(line.n2p(-3)), run_time=1.0)   # move the red dot along the axis to the value -3
        win.play(dot.animate.move_to(line.n2p(3.5)), run_time=1.0)   # then to the value 3.5 (it can stop between ticks)
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


# ===== Sample 2: the UnitInterval subclass ================================
class UnitIntervalDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-UnitInterval", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        line = UnitInterval(unit_size=10)   # parameter "unit_size": 0~1 fills 10 Manim units
        line.add_numbers()   # a 0.1 step automatically gives one-decimal labels, and 0/1 ticks are elongated
        lab = Text("UnitInterval(unit_size=10)", font_size=28,
                   color=GREY_B).next_to(line, DOWN, buff=0.6)   # parameter description label
        win.play(Create(line), run_time=0.8)   # draw the number line for [0,1]
        win.play(FadeIn(lab), run_time=0.4)   # the label fades in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


SCENES = [
    ("01-NumberLine-basic", NumberLineBasicDemo),
    ("01-NumberLine-unitinterval", UnitIntervalDemo),
]

PAIRS = [
    ("01-NumberLine-basic", ["01-NumberLine-basic"]),
    ("01-NumberLine-unitinterval", ["01-NumberLine-unitinterval"]),
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
