# -*- coding: utf-8 -*-
"""Full source for the three samples in 02b-More-Homotopy-Classes.md (identical to the code blocks in the page).

Usage: python 02b-More-Homotopy-Classes.py <clip name>...
With no arguments it renders every clip and concatenates the page's three sample videos (output to the parent assets/).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

import numpy as np

from real_time_manim import (
    Scene, Text, VGroup, Circle, Square, Dot,
    BLUE, RED, GREY_B, YELLOW, LEFT, UP, DOWN,
    ComplexHomotopy, FadeIn, PhaseFlow, SmoothedVectorizedHomotopy, Write, linear,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: SmoothedVectorizedHomotopy smooth squash and stretch ======
class SmoothedHomotopyDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        title = Text("02b-SmoothedVectorizedHomotopy", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        l1 = Text("SmoothedVectorizedHomotopy(squash, c, run_time=1.8,", font_size=30, color=GREY_B)
        l2 = Text("                            rate_func=linear)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # signature label
        c = Circle(radius=1.0, color=BLUE).set_fill(BLUE, 0.4).shift(DOWN * 1.5)   # blue circle
        win.play(FadeIn(sig, shift=DOWN), FadeIn(c), run_time=0.4)   # fade in the label and the circle

        def squash(x, y, z, t):   # parameter "homotopy": stretch x, squash y
            return (x * (1.0 + 0.9 * t), y * (1.0 - 0.45 * t), z)

        win.play(SmoothedVectorizedHomotopy(squash, c, run_time=1.8, rate_func=linear))
        win.play(Wait(0.6))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: ComplexHomotopy rotates 90° in the complex plane ==========
class ComplexHomotopyDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        title = Text("02b-ComplexHomotopy", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        l1 = Text("ComplexHomotopy(lambda z, t: z*e^(i*t*PI/2), sq,", font_size=30, color=GREY_B)
        l2 = Text("                run_time=1.8)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # signature label
        sq = Square(side_length=1.6, color=RED).set_fill(RED, 0.4).shift(DOWN * 1.5)   # red square
        win.play(FadeIn(sig, shift=DOWN), FadeIn(sq), run_time=0.4)   # fade in the label and the square
        win.play(ComplexHomotopy(lambda z, t: z * np.exp(1j * t * np.pi / 2), sq,   # parameter "complex_homotopy" (rotation in the complex plane)
                                 run_time=1.8))
        win.play(Wait(0.6))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: PhaseFlow accumulates displacement from a vector field ====
class PhaseFlowDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        title = Text("02b-PhaseFlow", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        l1 = Text("PhaseFlow(lambda p: [-p[1]-1.3, p[0], 0], dot,", font_size=30, color=GREY_B)
        l2 = Text("          virtual_time=1.2, run_time=2.0, rate_func=linear)", font_size=28, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # signature label
        dot = Dot(radius=0.13, color=GREY_B).shift(LEFT * 1.9 + DOWN * 1.3)   # the dot pushed by the vector field
        center = Dot(radius=0.06, color=GREY_B).shift(DOWN * 1.3)   # the centre of rotation of the vector field
        win.play(FadeIn(sig, shift=DOWN), FadeIn(VGroup(dot, center)), run_time=0.4)   # fade in the label and the dots
        win.play(PhaseFlow(lambda p: np.array([-p[1] - 1.3, p[0], 0.0]), dot,   # parameter "function" (the vector field)
                           virtual_time=1.2, run_time=2.0, rate_func=linear))   # parameter "virtual_time / run_time / rate_func"
        win.play(Wait(0.6))   # hold to see the result
        win.close()   # close the RTM window


SCENES = [
    ("smoothed", SmoothedHomotopyDemo),
    ("complex", ComplexHomotopyDemo),
    ("phaseflow", PhaseFlowDemo),
]

PAIRS = [
    ("smoothed", ["smoothed"]),
    ("complex", ["complex"]),
    ("phaseflow", ["phaseflow"]),
]

PAGE = "02b-More-Homotopy-Classes"


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
            dst = os.path.join(ASSETS, "RTM output", "%s-%s.mp4" % (PAGE, out_name))
            concat(names, dst)
            print("concat ->", dst, os.path.getsize(dst), "bytes")
