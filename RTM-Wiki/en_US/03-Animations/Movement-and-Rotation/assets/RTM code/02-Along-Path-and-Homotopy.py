# -*- coding: utf-8 -*-
"""Full source for the two samples in 02-Along-Path-and-Homotopy.md (identical to the code blocks in the page).

Usage: python 02-Along-Path-and-Homotopy.py <clip name>...
With no arguments it renders every clip and concatenates the page's two sample videos (output to the parent assets/).
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
    Scene, Text, VGroup, Circle, Dot, Rectangle,
    GREY_B, ORANGE, YELLOW, UP, DOWN,
    Create, FadeIn, Write, linear,
)
from real_time_manim.vulkan_bind import MLWindow, MoveAlongPath, Homotopy, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: MoveAlongPath walks a full lap along a visible trajectory =
class MoveAlongPathDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        title = Text("02-MoveAlongPath", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        sig = Text("MoveAlongPath(dot, path, run_time=2.0, rate_func=linear)",
                   font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   # signature label
        path = Circle(radius=1.9, color=GREY_B).shift(DOWN * 0.9)   # grey circular path
        dot = Dot(radius=0.14, color=ORANGE).move_to(path.point_from_proportion(0.0))   # orange dot at the start point
        win.play(FadeIn(sig, shift=DOWN), FadeIn(dot), run_time=0.4)   # fade in the label and the dot
        win.play(Create(path, run_time=0.8, rate_func=linear))   # draw the path (so the trajectory is visible)
        win.play(MoveAlongPath(dot, path, run_time=2.0, rate_func=linear))   # parameter "path / run_time / rate_func"
        win.play(Wait(0.6))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: Homotopy remaps point by point into a wave ================
class HomotopyDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        title = Text("02-Homotopy", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        sig = Text("Homotopy(wave, rect, run_time=2.0, rate_func=linear)",
                   font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   # signature label
        rect = Rectangle(width=4.4, height=1.6, color=YELLOW).set_fill(YELLOW, 0.35).shift(DOWN * 1.2)   # yellow rectangle
        win.play(FadeIn(sig, shift=DOWN), FadeIn(rect), run_time=0.4)   # fade in the label and the rectangle

        def wave(x, y, z, t):   # parameter "homotopy": (x, y, z, t) -> (x', y', z')
            return (x, y + 0.45 * np.sin(2.2 * x + 2.0 * np.pi * t), z)

        win.play(Homotopy(wave, rect, run_time=2.0, rate_func=linear))   # parameter "homotopy / run_time / rate_func"
        win.play(Wait(0.6))   # hold to see the result
        win.close()   # close the RTM window


SCENES = [
    ("movealongpath", MoveAlongPathDemo),
    ("homotopy", HomotopyDemo),
]

PAIRS = [
    ("movealongpath", ["movealongpath"]),
    ("homotopy", ["homotopy"]),
]

PAGE = "02-Along-Path-and-Homotopy"


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
