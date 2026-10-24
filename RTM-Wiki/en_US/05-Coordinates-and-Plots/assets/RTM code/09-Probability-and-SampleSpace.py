# -*- coding: utf-8 -*-
"""Full source of the two samples in 09-Probability-and-SampleSpace.md (identical to the code blocks in the page).

Usage: python 09-Probability-and-SampleSpace.py <scene name>...
With no arguments it renders every scene and concatenates the page's two videos.
"""
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
ASSETS = os.path.dirname(HERE)
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

from real_time_manim import (  # noqa: E402
    BLACK, BLUE_E, Brace, Create, DOWN, FadeIn, GRAY, GREEN_E, GREY_B, LEFT,
    RIGHT, SampleSpace, Scene, Text, UP, WHITE, YELLOW,
    Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait  # noqa: E402
from real_time_manim.record import fast_record_scene  # noqa: E402


# ===== Sample 1: divide_vertically + brace labels ========================
class VerticalDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("09-SampleSpace", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        poly = SampleSpace(width=2, height=2, stroke_width=5, fill_opacity=0.1)   #the sample-space box
        poly.divide_vertically(   #"divide_vertically": split vertically by a probability list
            p_list=np.array([0.37, 0.13, 0.5]),   #parameter "p_list": share of each block (auto-fills the remainder when the sum is under 1)
            colors=[BLACK, WHITE, GRAY],   #parameter "colors": color scheme (a gradient is applied automatically)
            vect=RIGHT)   #parameter "vect": split direction
        poly.add_title("Sample space")   #"add_title": title above the box
        win.play(Create(poly), run_time=0.8)   #draw the box and the split blocks
        win.play(Wait(0.5))   #wait 0.5s

        b0 = Brace(poly.vertical_parts[0], LEFT)   #attach a brace on the left of block 0
        t0 = b0.get_text("0.37")   #"get_text": the label next to the brace
        b2 = Brace(poly.vertical_parts[2], RIGHT)   #attach one on the right of the rightmost block
        t2 = b2.get_text("0.50")
        win.play(FadeIn(b0), FadeIn(t0), run_time=0.4)   #the two labels fade in one after another
        win.play(FadeIn(b2), FadeIn(t2), run_time=0.4)
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window


# ===== Sample 2: divide_horizontally + auto-filling the shortfall ========
class HorizontalDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("09-divide_horizontally", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        grid = SampleSpace(height=2.5, width=3, fill_opacity=0.6)   #a flatter sample space
        grid.divide_horizontally(   #"divide_horizontally": split horizontally by a probability list
            p_list=[0.4, 0.25],   #only two blocks = 0.65; the remaining 0.35 is filled in as a third block by complete_p_list
            colors=[GREEN_E, BLUE_E],
            vect=DOWN)   #parameter "vect": split direction
        grid.add_title("horizontal division")   #the title states the split method (do not put `_` in the Tex)
        win.play(Create(grid), run_time=0.8)   #draw the three blocks
        win.play(Wait(0.5))   #wait 0.5s

        labels = ["0.40", "0.25", "0.35"]
        braces = [Brace(grid.horizontal_parts[i], LEFT) for i in range(3)]   #one brace on the left of each row
        texts = [braces[i].get_text(labels[i]) for i in range(3)]
        win.play(*[FadeIn(b) for b in braces], run_time=0.4)   #the three braces fade in together
        win.play(*[FadeIn(t) for t in texts], run_time=0.4)   #the three labels fade in together
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window


SCENES = [
    ("09-Probability-and-SampleSpace-basic", VerticalDemo),
    ("09-Probability-and-SampleSpace-horizontal", HorizontalDemo),
]

PAIRS = [
    ("09-Probability-and-SampleSpace-basic", ["09-Probability-and-SampleSpace-basic"]),
    ("09-Probability-and-SampleSpace-horizontal", ["09-Probability-and-SampleSpace-horizontal"]),
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
