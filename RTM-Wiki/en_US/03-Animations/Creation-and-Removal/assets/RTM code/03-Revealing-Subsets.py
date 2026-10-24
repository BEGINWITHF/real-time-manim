# -*- coding: utf-8 -*-
"""Full source of the three samples in 03-Revealing-Subsets.md (word for word identical to the code blocks on the page).

Usage: python 03-Revealing-Subsets.py <clip-name>...
With no arguments it renders every clip and concatenates the three sample videos shown on the page (written to the parent assets/).
"""
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    Scene, Text, VGroup, Circle, Square, Triangle,
    BLUE, GREEN, GREY_B, ORANGE, RED, YELLOW,
    UP, DOWN, RIGHT,
    FadeIn, ShowIncreasingSubsets, ShowSubmobjectsOneByOne, SpiralIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: ShowIncreasingSubsets popping out one after another ========
class IncreasingSubsetsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("03-ShowIncreasingSubsets", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l1 = Text("ShowIncreasingSubsets(group, suspend_mobject_updating=False,",
                  font_size=30, color=GREY_B)
        l2 = Text("    int_func=np.floor, reverse_rate_function=False)",
                  font_size=30, color=GREY_B)
        lab1 = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # two-line signature label
        g1 = VGroup(Circle(radius=0.35, color=BLUE),
                    Square(side_length=0.9, color=GREEN),
                    Triangle(color=ORANGE).scale(0.6),
                    Circle(radius=0.35, color=RED),
                    ).arrange(RIGHT, buff=0.7).next_to(lab1, DOWN, buff=0.6)   # the four shapes revealed one by one
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)   # label fades in from below
        self.add(g1)   # the submobjects are set_opacity(0) at construction, so add to the scene first
        win.play(
            ShowIncreasingSubsets(                  # parameter "group"
                g1,
                suspend_mobject_updating=False,     # parameter "suspend_mobject_updating"
                int_func=np.floor,                  # parameter "int_func": round the number revealed
                reverse_rate_function=False,        # parameter "reverse_rate_function"
                run_time=2.0,                       # parameter "run_time"
            ),
            run_time=2.0,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


# ===== Sample 2: ShowSubmobjectsOneByOne lighting only one at a time ========
class OneByOneDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("03-ShowSubmobjectsOneByOne", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l3 = Text("ShowSubmobjectsOneByOne(group, int_func=np.ceil, run_time=2.0)",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   # signature label
        g2 = VGroup(Circle(radius=0.35, color=YELLOW),
                    Square(side_length=0.9, color=RED),
                    Triangle(color=BLUE).scale(0.6),
                    Circle(radius=0.35, color=GREEN),
                    ).arrange(RIGHT, buff=0.7).next_to(l3, DOWN, buff=0.6)   # the four shapes flashing in turn
        win.play(FadeIn(l3, shift=DOWN), run_time=0.4)   # label fades in from below
        self.add(g2)   # set to 0 at construction, so add to the scene first
        win.play(
            ShowSubmobjectsOneByOne(                # parameter "group"
                g2,
                int_func=np.ceil,                   # parameter "int_func": the rounding function
                run_time=2.0,                       # parameter "run_time"
            ),
            run_time=2.0,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


# ===== Sample 3: SpiralIn flying in along a spiral trajectory ===============
class SpiralInDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("03-SpiralIn", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l5 = Text("SpiralIn(shapes, scale_factor=6, fade_in_fraction=0.3,",
                  font_size=30, color=GREY_B)
        l6 = Text("        run_time=1.8)",
                  font_size=30, color=GREY_B)
        lab3 = VGroup(l5, l6).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # two-line signature label
        g3 = VGroup(Circle(radius=0.4, color=GREEN),
                    Square(side_length=1.0, color=BLUE),
                    Triangle(color=RED).scale(0.7),
                    Circle(radius=0.4, color=ORANGE),
                    ).arrange(RIGHT, buff=0.7).next_to(lab3, DOWN, buff=0.6)   # the four shapes flying in along a spiral
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)   # label fades in from below
        # do not add ahead of time: SpiralIn moves the submobjects to the spiral start at construction and enters the scene as an introducer
        win.play(
            SpiralIn(g3,                            # parameter "shapes"
                     scale_factor=6,                # parameter "scale_factor": non-default 8
                     fade_in_fraction=0.3,          # parameter "fade_in_fraction"
                     run_time=1.8),                 # parameter "run_time"
            run_time=1.8,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


SCENES = [
    ("increasing_subsets", IncreasingSubsetsDemo),
    ("one_by_one", OneByOneDemo),
    ("spiral_in", SpiralInDemo),
]

PAIRS = [
    ("increasing_subsets", ["increasing_subsets"]),
    ("one_by_one", ["one_by_one"]),
    ("spiral_in", ["spiral_in"]),
]

PAGE = "03-Revealing-Subsets"


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
