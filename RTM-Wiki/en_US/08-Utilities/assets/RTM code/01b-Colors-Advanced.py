# -*- coding: utf-8 -*-
"""Full source of the two samples in 01b-Colors-Advanced.md (identical to the code blocks in the page).

Usage: python 01b-Colors-Advanced.py <clip name>...
With no arguments it renders every clip and concatenates the page's two sample videos (output to the parent assets/).
"""
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

from real_time_manim import (
    Scene, Square, Rectangle, Text, VGroup,
    ManimColor, average_color, interpolate_color, random_bright_color, random_color,
    RED, BLUE, YELLOW, WHITE, GREY_B,
    UP, DOWN, LEFT, RIGHT, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: interpolate, two-color interpolation =======================
class ColorInterpolateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("01b-interpolate", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        cols = [RED.interpolate(BLUE, i / 8) for i in range(9)]   #alpha evenly divided into 9 steps from 0 to 1
        sq = VGroup(*[Square(side_length=0.85, stroke_width=1).set_fill(c, 1) for c in cols])   #9 color blocks
        sq.arrange(RIGHT, buff=0.12).move_to(UP * 0.55)   #arrange into an interpolation band, left to right
        sq[4].set_fill(interpolate_color(RED, BLUE, 0.5), 1)   #the middle block switches to the function form; the color is bit-identical to interpolate
        lab = Text("RED.interpolate(BLUE, i / 8)", font_size=18, color=GREY_B)
        lab.next_to(sq, UP, buff=0.3)   #label the call above the band
        l0 = Text("alpha=0  RED", font_size=16, color=GREY_B).next_to(sq[0], DOWN, buff=0.22)   #left end = self
        l1 = Text("alpha=1  BLUE", font_size=16, color=GREY_B).next_to(sq[-1], DOWN, buff=0.22)   #right end = target color
        lm = Text("interpolate_color(RED, BLUE, 0.5)", font_size=16, color=WHITE)
        lm.next_to(sq[4], DOWN, buff=0.55)   #the middle block = the same result as the function form
        self.add(lab, l0, l1, lm)   #add the labels to the scene first (the blocks fade in one by one later)
        for m in sq:   #fade in block by block in increasing alpha so the color change is visible
            win.play(FadeIn(m), run_time=0.12)
        win.play(FadeIn(lab), FadeIn(l0), FadeIn(l1), FadeIn(lm), run_time=0.5)   #the three labels fade in
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window


# ===== Sample 2: average / random with invert / opacity / contrasting =======
class ColorHelpersDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("01b-ColorHelpers", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        random.seed(7)   #pin the random seed so every run (on either engine) draws the same colors
        # —— row 1: three color-picking functions ——
        gen = [average_color(RED, BLUE), random_color(), random_bright_color()]   #average / random / bright random
        glab = ["average_color(RED, BLUE)", "random_color()", "random_bright_color()"]
        gsw = VGroup(*[Square(side_length=1.3, stroke_width=2).set_fill(c, 1) for c in gen])
        gsw.arrange(RIGHT, buff=1.2).move_to(UP * 1.7)   #three blocks in a row, spaced for the labels
        gt = VGroup(*[Text(s, font_size=15, color=GREY_B).next_to(m, DOWN, buff=0.18)
                      for s, m in zip(glab, gsw)])   #function name below each block
        gh = VGroup(*[Text(c.to_hex(), font_size=15, color=WHITE).next_to(m, UP, buff=0.18)
                      for c, m in zip(gen, gsw)])   #hex result above each block
        # —— row 2: three instance methods ——
        src = ManimColor("RED")
        meth = [src, src.invert(), src.opacity(0.35)]   #original / per-channel inversion / alpha-only swap
        mlab = ["'RED'", "invert()", "opacity(0.35)"]
        msw = VGroup(*[Square(side_length=1.3, stroke_width=2).set_fill(c, 1) for c in meth])
        msw.arrange(RIGHT, buff=1.2).move_to(DOWN * 0.35)   #three blocks in a row
        mt = VGroup(*[Text(s, font_size=15, color=GREY_B).next_to(m, DOWN, buff=0.18)
                      for s, m in zip(mlab, msw)])   #method name below each block
        # —— row 3: contrasting picks a readable text color ——
        dark = Rectangle(width=3.6, height=1.0, stroke_width=2).set_fill("#333333", 1)
        dark.set_stroke(GREY_B, 1).move_to(LEFT * 2.1 + DOWN * 2.5)   #dark backing panel
        dtx = Text("dark bg -> white text", font_size=20,
                   color=ManimColor("#333333").contrasting()).move_to(dark)   #picks white text on the dark panel
        lite = Rectangle(width=3.6, height=1.0, stroke_width=2).set_fill("#DDDDDD", 1)
        lite.set_stroke(GREY_B, 1).move_to(RIGHT * 2.1 + DOWN * 2.5)   #light backing panel
        ltx = Text("light bg -> black text", font_size=20,
                   color=ManimColor("#DDDDDD").contrasting()).move_to(lite)   #picks black text on the light panel
        self.add(gt, gh, mt)   #labels go in first
        win.play(FadeIn(gsw), FadeIn(gt), FadeIn(gh), run_time=0.6)   #row 1 blocks and labels
        win.play(FadeIn(msw), FadeIn(mt), run_time=0.6)   #row 2 blocks and labels
        win.play(FadeIn(VGroup(dark, dtx, lite, ltx)), run_time=0.6)   #row 3 contrast panels
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window


SCENES = [
    ("interpolate", ColorInterpolateDemo),
    ("helpers", ColorHelpersDemo),
]

PAIRS = [
    ("interpolate", ["interpolate"]),
    ("helpers", ["helpers"]),
]

PAGE = "01b-Colors-Advanced"


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
