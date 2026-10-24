# -*- coding: utf-8 -*-
"""Full source for the three samples in 01-Rotation.md (identical to the code blocks in the page).

Usage: python 01-Rotation.py <clip name>...
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

from real_time_manim import (
    Scene, Text, VGroup, Square, Arrow, Dot, Triangle,
    BLUE, GOLD, GREY_B, TEAL, ORANGE, YELLOW,
    UP, DOWN, RIGHT, ORIGIN, PI, IN, DEGREES,
    FadeIn, Write, linear, rush_into, smooth,
)
from real_time_manim.vulkan_bind import MLWindow, Rotate, Rotating, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: Rotate 120° about a fixed point ===========================
class RotateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        title = Text("01-Rotate", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        l1 = Text("Rotate(sq, angle=2*PI/3, about_point=PIVOT,", font_size=30, color=GREY_B)
        l2 = Text("         run_time=1.6, rate_func=smooth)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # signature label
        pivot = Dot(point=ORIGIN + DOWN * 1.4, radius=0.09, color=ORANGE)   # rotation centre
        sq = Square(side_length=1.3, color=BLUE).set_fill(BLUE, 0.5).move_to(pivot.get_center() + RIGHT * 2.6)   # blue square
        win.play(FadeIn(sig, shift=DOWN), FadeIn(VGroup(pivot, sq)), run_time=0.4)   # fade in the label and the shapes
        win.play(Rotate(sq, angle=2 * PI / 3, about_point=pivot.get_center(),   # parameter "angle / about_point"
                        run_time=1.6, rate_func=smooth))                        # parameter "run_time / rate_func"
        win.play(Wait(0.6))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: Rotating turns the other way ==============================
class RotatingAxisDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        title = Text("01-RotatingAxis", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        l1 = Text("Rotating(arrow, angle=180*DEGREES, axis=IN,", font_size=30, color=GREY_B)
        l2 = Text("          run_time=1.4, rate_func=linear)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # signature label
        arrow = Arrow(ORIGIN, RIGHT * 2.0, buff=0, color=GOLD).shift(DOWN * 1.6)   # gold arrow
        win.play(FadeIn(sig, shift=DOWN), FadeIn(arrow), run_time=0.4)   # fade in the label and the arrow
        win.play(Rotating(arrow, angle=180 * DEGREES, axis=IN,   # parameter "angle / axis=IN" (reverse turn in the 2D frame)
                          run_time=1.4, rate_func=linear))       # parameter "run_time / rate_func"
        win.play(Wait(0.6))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: Rotating flips about the top edge =========================
class RotatingEdgeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        title = Text("01-RotatingEdge", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        l1 = Text("Rotating(tri, angle=90*DEGREES, about_edge=UP,", font_size=30, color=GREY_B)
        l2 = Text("           run_time=1.6, rate_func=rush_into)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # signature label
        tri = Triangle(color=TEAL).scale(1.1).set_fill(TEAL, 0.5).shift(DOWN * 2.0)   # teal triangle
        win.play(FadeIn(sig, shift=DOWN), FadeIn(tri), run_time=0.4)   # fade in the label and the triangle
        win.play(Rotating(tri, angle=90 * DEGREES, about_edge=UP,   # parameter "about_edge=UP" (the top edge as a hinge)
                          run_time=1.6, rate_func=rush_into))       # parameter "run_time / rate_func"
        win.play(Wait(0.6))   # hold to see the result
        win.close()   # close the RTM window


SCENES = [
    ("rotate", RotateDemo),
    ("rotating_axis", RotatingAxisDemo),
    ("rotating_edge", RotatingEdgeDemo),
]

PAIRS = [
    ("rotate", ["rotate"]),
    ("rotating_axis", ["rotating_axis"]),
    ("rotating_edge", ["rotating_edge"]),
]

PAGE = "01-Rotation"


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
