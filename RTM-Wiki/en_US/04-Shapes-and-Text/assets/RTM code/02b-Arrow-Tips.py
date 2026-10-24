# -*- coding: utf-8 -*-
"""Full source for the two samples in 02b-Arrow-Tips.md (identical to the code blocks in the page).

Usage: python 02b-Arrow-Tips.py <clip names>...
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
    Scene, Line, Arc, Arrow, Text,
    StealthTip, ArrowTriangleTip, ArrowTriangleFilledTip,
    ArrowCircleTip, ArrowCircleFilledTip, ArrowSquareTip, ArrowSquareFilledTip,
    BLUE, RED, GREEN, TEAL, YELLOW, GREY_B,
    UP, DOWN, LEFT, RIGHT, PI, Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: the tip base-class methods add_tip / get_tip / tip_length =
class TipsBaseDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02b-add_tip / get_tip / tip_length", font_size=30, color=YELLOW)
        title.to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— lines have no tip by default, add_tip() installs one on the spot ——
        ln1 = Line([-5.5, 2.0, 0], [0.5, 2.0, 0], color=BLUE, stroke_width=7)   # Line has no tip by default
        c1 = Text("Line (no tip yet)", font_size=22, color=GREY_B).next_to(ln1, DOWN, buff=0.15)
        win.play(Create(ln1), FadeIn(c1), run_time=0.6)   # draw the bare line + caption

        # —— tip_length is given at construction; get_tip() fetches the tip object back ——
        ln2 = Line([-5.5, 0.75, 0], [0.5, 0.75, 0], color=RED, stroke_width=7, tip_length=0.6)   # give tip_length at construction
        c2 = Text("tip_length=0.6 + add_tip() + get_tip()", font_size=20, color=GREY_B)
        c2.next_to(ln2, DOWN, buff=0.15)   # the caption is below
        win.play(Create(ln2), run_time=0.5)   # draw the bare line first
        win.play(ln2.animate.add_tip(), run_time=0.5)   # install the tip with tip_length=0.6
        tip = ln2.get_tip()   # fetch back the tip just installed (get_tip takes no arguments)
        win.play(tip.animate.set_color(YELLOW), FadeIn(c2), run_time=0.4)   # colour the tip yellow to prove it was fetched

        # —— at_start: install the tip at the start end ——
        ln3 = Line([-5.5, -0.5, 0], [0.5, -0.5, 0], color=GREEN, stroke_width=7)   # the start is on the left
        c3 = Text("add_tip(at_start=True)", font_size=22, color=GREY_B).next_to(ln3, DOWN, buff=0.15)
        win.play(Create(ln3), run_time=0.4)   # draw the bare line first
        win.play(ln3.animate.add_tip(at_start=True), FadeIn(c3), run_time=0.5)   # install the tip at the left end

        # —— tip=: hand in a ready-made tip instance directly ——
        ln4 = Line([-5.5, -1.75, 0], [0.5, -1.75, 0], color=TEAL, stroke_width=7)   # about to install a square tip
        c4 = Text("add_tip(tip=ArrowSquareTip(...))", font_size=18, color=GREY_B)
        c4.next_to(ln4, DOWN, buff=0.15)   # the caption is below
        win.play(Create(ln4), run_time=0.4)   # draw the bare line first
        win.play(ln4.animate.add_tip(tip=ArrowSquareTip(length=0.42)), FadeIn(c4), run_time=0.5)   # install the ready-made square tip instance

        # —— any arc can take a tip too (an arrowhead at the arc's tail) ——
        arc = Arc(radius=1.1, start_angle=-PI / 4, angle=PI / 2, color=YELLOW, stroke_width=7)
        arc.shift([4.6, 1.0, 0])   # an arc in the top right
        c5 = Text("arc.add_tip(tip_length=0.3)", font_size=22, color=GREY_B).move_to([4.6, -0.6, 0])
        win.play(Create(arc), run_time=0.5)   # draw the arc first
        win.play(arc.animate.add_tip(tip_length=0.3), FadeIn(c5), run_time=0.5)   # install a tip at the arc's tail + caption
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


# ===== Sample 2: the seven tip shapes tip_shape=... ========================
class TipShapesDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02b-7 tip shapes (tip_shape=...)", font_size=30, color=YELLOW)
        title.to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        names = ["StealthTip", "ArrowTriangleTip", "ArrowTriangleFilledTip",
                 "ArrowCircleTip", "ArrowCircleFilledTip",
                 "ArrowSquareTip", "ArrowSquareFilledTip"]   # the seven tip class names
        shapes = [StealthTip, ArrowTriangleTip, ArrowTriangleFilledTip,
                  ArrowCircleTip, ArrowCircleFilledTip,
                  ArrowSquareTip, ArrowSquareFilledTip]   # the seven classes themselves (pass classes, not instances)
        ys = [2.6, 1.7, 0.8, -0.1, -1.0, -1.9, -2.8]   # y coordinates of the seven rows
        for name, shape, y in zip(names, shapes, ys):   # draw row by row: arrow + class name on the right
            a = Arrow([-5.2, y, 0], [2.2, y, 0], buff=0, stroke_width=6,
                      tip_shape=shape)   # tip_shape takes a "class", with no parentheses
            lab = Text(name, font_size=22, color=GREY_B).next_to(a, RIGHT, buff=0.3)
            win.play(Create(a), FadeIn(lab), run_time=0.45)   # draw the arrow + the class-name caption
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


SCENES = [
    ("tips_base", TipsBaseDemo),
    ("tip_shapes", TipShapesDemo),
]

PAIRS = [
    ("tips_base", ["tips_base"]),
    ("tip_shapes", ["tip_shapes"]),
]

PAGE = "02b-Arrow-Tips"


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
