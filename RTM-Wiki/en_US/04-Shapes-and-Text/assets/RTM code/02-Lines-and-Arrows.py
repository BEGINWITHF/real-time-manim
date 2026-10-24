# -*- coding: utf-8 -*-
"""Full source for the two samples in 02-Lines-and-Arrows.md (identical to the code blocks in the page).

Usage: python 02-Lines-and-Arrows.py <clip names>...
With no arguments it renders every clip and concatenates the page's two sample videos (written to the parent assets/).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

from real_time_manim import (
    Scene, Line, DashedLine, TangentLine, Elbow, Arc, Arrow, Vector, DoubleArrow,
    Text, BLUE, RED, GREEN, YELLOW, ORANGE, TEAL, PURPLE, WHITE, GREY_B,
    UP, DOWN, LEFT, RIGHT, UR, PI, Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: the Line family Line / DashedLine / TangentLine / Elbow ===
class LinesDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02-Line / DashedLine / TangentLine / Elbow", font_size=28, color=YELLOW)
        title.to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— Line: start and end + path_arc bends the "straight line" ——
        ln = Line([-5.6, 2.2, 0], [0.4, 2.2, 0], stroke_width=6, color=YELLOW)   # default path_arc=0: straight
        c1 = Text("Line(start, end)", font_size=22, color=GREY_B).next_to(ln, DOWN, buff=0.15)
        win.play(Create(ln), FadeIn(c1), run_time=0.6)   # draw the straight line + caption

        ln2 = Line([-5.6, 0.9, 0], [0.4, 0.9, 0], path_arc=0.6, stroke_width=6, color=ORANGE)   # same endpoints, path_arc≠0 bends it into an arc
        c2 = Text("Line(path_arc=0.6)", font_size=22, color=GREY_B).next_to(ln2, DOWN, buff=0.15)
        win.play(Create(ln2), FadeIn(c2), run_time=0.6)   # draw the arc + caption

        # —— DashedLine: dash_length / dashed_ratio ——
        dl = DashedLine([-5.6, -0.7, 0], [0.4, -0.7, 0], dash_length=0.15,
                       dashed_ratio=0.55, color=TEAL, stroke_width=5)   # dash 0.15, solid fraction 0.55
        c3 = Text("DashedLine(dash_length=0.15)", font_size=22, color=GREY_B).next_to(dl, DOWN, buff=0.15)
        win.play(Create(dl), FadeIn(c3), run_time=0.6)   # draw the dashed line + caption

        # —— TangentLine: the tangent to the curve at alpha ——
        arc = Arc(radius=1.0, start_angle=-PI / 3, angle=2 * PI / 3, color=BLUE, stroke_width=6)
        arc.shift([4.6, 1.9, 0])   # put an arc in the top right
        tl = TangentLine(arc, 0.5, length=2.4, color=RED, stroke_width=6)   # the tangent at the arc's midpoint (alpha=0.5)
        c4 = Text("TangentLine(arc, 0.5)", font_size=22, color=GREY_B).move_to([4.6, 0.3, 0])   # below the tangent
        win.play(Create(arc), run_time=0.5)   # draw the arc first
        win.play(Create(tl), FadeIn(c4), run_time=0.6)   # then the tangent + caption

        # —— Elbow: a right-angle corner (angle turns the direction) ——
        e1 = Elbow(width=0.5, angle=0, color=GREEN, stroke_width=6).shift([3.8, -1.9, 0])   # original orientation
        e2 = Elbow(width=0.5, angle=PI / 2, color=GREEN, stroke_width=6).shift([5.4, -1.9, 0])   # rotated 90°
        c5 = Text("Elbow(angle=0 / PI/2)", font_size=22, color=GREY_B).move_to([4.6, -2.9, 0])
        win.play(FadeIn(e1), FadeIn(e2), run_time=0.5)   # both corners appear together
        win.play(FadeIn(c5), run_time=0.3)   # fade in the caption
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


# ===== Sample 2: the arrow family Arrow / Vector / DoubleArrow =============
class ArrowsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02-Arrow / Vector / DoubleArrow", font_size=30, color=YELLOW)
        title.to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— Arrow: the ratios are controlled automatically, a short line never looks top-heavy ——
        a1 = Arrow([-5.6, 2.0, 0], [0.6, 2.0, 0], color=BLUE, buff=0)   # regular length
        c1 = Text("Arrow(start, end, buff=0)", font_size=22, color=GREY_B).next_to(a1, DOWN, buff=0.15)
        win.play(Create(a1), FadeIn(c1), run_time=0.7)   # draw the regular arrow + caption

        a2 = Arrow([-5.6, 0.6, 0], [-2.4, 0.6, 0], color=RED, buff=0, stroke_width=14)   # short and thick: the tip ratio is capped automatically
        c2 = Text("short arrow + stroke_width=14", font_size=22, color=GREY_B).next_to(a2, DOWN, buff=0.15)
        win.play(Create(a2), FadeIn(c2), run_time=0.7)   # draw the short thick arrow + caption

        # —— DoubleArrow: a tip at both ends ——
        da = DoubleArrow([3.4, 2.0, 0], [6.6, 2.0, 0], color=PURPLE, buff=0)   # double-headed (a dimension line, moved right to make room for the coordinate label)
        c3 = Text("DoubleArrow", font_size=22, color=GREY_B).next_to(da, DOWN, buff=0.15)
        win.play(Create(da), FadeIn(c3), run_time=0.7)   # draw the double-headed arrow + caption

        # —— Vector: starts at the origin + coordinate_label labels the coordinates ——
        v = Vector([2.4, 1.4, 0], color=GREEN).shift([-4.8, -1.7, 0])   # direction vector (from the "origin" towards direction)
        c4 = Text("Vector([2.4, 1.4])", font_size=22, color=GREY_B).move_to([-4.4, -3.0, 0])
        win.play(Create(v), FadeIn(c4), run_time=0.7)   # draw the vector + caption

        v2 = Vector([2, 1, 0], color=TEAL)   # put it at the origin: coordinate_label rounds the endpoint's world coordinates
        lab = v2.coordinate_label(color=WHITE).next_to(v2.get_end(), UR, buff=0.2)   # label (2, 1) next to the endpoint
        c5 = Text("coordinate_label()", font_size=22, color=GREY_B).move_to([1.4, -0.9, 0])
        win.play(Create(v2), run_time=0.5)   # draw the vector
        win.play(FadeIn(lab), FadeIn(c5), run_time=0.5)   # the coordinate label + caption
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


SCENES = [
    ("lines", LinesDemo),
    ("arrows", ArrowsDemo),
]

PAIRS = [
    ("lines", ["lines"]),
    ("arrows", ["arrows"]),
]

PAGE = "02-Lines-and-Arrows"


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
