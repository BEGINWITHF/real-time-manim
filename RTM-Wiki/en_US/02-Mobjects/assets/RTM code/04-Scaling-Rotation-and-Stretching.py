# -*- coding: utf-8 -*-
"""Full source for the four samples in 04-Scaling-Rotation-and-Stretching.md (identical to the code blocks in the page).

Usage: python 04-Scaling-Rotation-and-Stretching.py <clip names>...
With no arguments it renders every clip and concatenates the page's four sample videos (written to the parent assets/).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    Scene, Square, Rectangle, Line, Arrow, Dot,
    BLUE, GREEN, YELLOW, PURPLE, RED,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    DEGREES, PI, FadeIn, Rotate,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: scale ====================================================
class ScaleDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.6, fill_opacity=0.5)   # blue square
        anchor = Dot(color=RED, radius=0.08).move_to(RIGHT * 2.5)   # marker for the scaling pivot
        self.add(sq, anchor)   # add them to the scene
        win.play(sq.animate.scale(1.6), run_time=0.6)   # by default scales up about its own center
        win.play(sq.animate.scale(0.6, about_point=RIGHT * 2.5), run_time=0.6)   # scale about the red dot: the dot's position is unchanged
        win.play(sq.animate.scale(1.8, about_edge=DOWN), run_time=0.6)   # scale about the bottom edge: the bottom edge stays fixed
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window


# ===== Sample 2: rotate / rotate_about_origin =============================
class RotateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        rect = Rectangle(width=2.4, height=1.0, color=GREEN, fill_opacity=0.5)   # a rectangle: easy to see when it turns
        self.add(rect)   # add it to the scene
        win.play(rect.animate.rotate(90 * DEGREES), run_time=0.6)   # turn 90° about its own center (radians = 90*DEGREES)
        win.play(rect.animate.rotate(60 * DEGREES, about_point=LEFT * 2), run_time=0.6)   # turn about a given point
        win.play(Rotate(rect, angle=180 * DEGREES), run_time=0.8)   # "animate.rotate" only interpolates; for a continuous turn use the Rotate animation
        win.play(rect.animate.rotate_about_origin(90 * DEGREES), run_time=0.6)   # rotate about the scene origin (0, 0, 0)
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window


# ===== Sample 3: flip =====================================================
class FlipDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        s = Line(LEFT * 2, RIGHT * 2 + UP * 1.2, color=YELLOW)   # a line high on the right and low on the left: a mirror is easy to see
        self.add(s)   # add it to the scene
        win.play(s.animate.flip(axis=UP), run_time=0.6)   # turn 180° about the vertical axis = a left-right mirror
        win.play(s.animate.flip(axis=RIGHT, about_point=RIGHT * 2), run_time=0.6)   # turn 180° about the horizontal axis = an up-down mirror, pivot on the right
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window


# ===== Sample 4: stretch / stretch_about_point ============================
class StretchDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        sq = Square(color=PURPLE, side_length=1.4, fill_opacity=0.5)   # purple square
        self.add(sq)   # add it to the scene
        win.play(sq.animate.stretch(2.2, 0), run_time=0.6)   # stretch horizontally only: dim=0
        win.play(sq.animate.stretch(0.5, 1, about_point=ORIGIN), run_time=0.6)   # dim=1 squash, about the origin
        win.play(sq.animate.stretch_about_point(1.8, 0, sq.get_left()), run_time=0.6)   # stretch right, left end fixed
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window


SCENES = [
    ("scale", ScaleDemo),
    ("rotate", RotateDemo),
    ("flip", FlipDemo),
    ("stretch", StretchDemo),
]

PAIRS = [
    ("scale", ["scale"]),
    ("rotate", ["rotate"]),
    ("flip", ["flip"]),
    ("stretch", ["stretch"]),
]

PAGE = "04-Scaling-Rotation-and-Stretching"


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
