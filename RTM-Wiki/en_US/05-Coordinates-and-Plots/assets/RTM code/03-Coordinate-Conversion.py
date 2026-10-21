# -*- coding: utf-8 -*-
"""Full source for the single sample in 03-Coordinate-Conversion.md (identical to the code block in the page).

Usage: python 03-Coordinate-Conversion.py
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
    Scene, Axes, Dot, Text, VGroup, np,
    YELLOW, GREEN, BLUE, GREY_B, UP, DOWN, UR, DL,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample: c2p / p2c / @ / batch conversion ===========================
class C2PDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("03-c2p-p2c", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[-4, 4, 1], y_range=[-3, 3, 1],
                  x_length=8, y_length=5, tips=False)   # coordinate system without arrows
        ax.add_coordinates()   # tick numbers
        labels = ax.get_axis_labels("x", "y")   # axis names
        lab = Text("p = ax.c2p(2, 1.5)   coords = ax.p2c(p)",
                   font_size=26, color=GREY_B).to_edge(DOWN)   # method description label
        win.play(Create(ax), FadeIn(labels), FadeIn(lab), run_time=0.8)   # the coordinate system and the labels appear together

        p = ax.c2p(2, 1.5)   # "c2p": data coordinates -> screen coordinates, the only correct way to place elements
        dot = Dot(p, color=GREEN)   # a green dot at the c2p result
        coords = ax.p2c(p)   # "p2c": screen coordinates -> data coordinates (the inverse of c2p)
        readout = Text("p2c=(%.1f, %.1f)" % (coords[0], coords[1]),   # show the read-back result on screen
                       font_size=28, color=GREEN).next_to(dot, UR, buff=0.2)
        win.play(FadeIn(dot), FadeIn(readout), run_time=0.5)   # the green dot and the read-back text fade in
        win.play(Wait(0.6))   # pause 0.6s to see the read-back result

        q = ax @ (1, -2)   # the "@" form: equivalent to ax.c2p(1, -2)
        assert np.allclose(ax.p2c(q), [1, -2], atol=1e-6)   # round-trip self-check: p2c(c2p(x)) == x
        dot2 = Dot(q, color=YELLOW)   # a yellow dot at the @ result
        tag2 = Text("ax @ (1,-2)", font_size=26, color=YELLOW).next_to(dot2, DL, buff=0.2)
        win.play(FadeIn(dot2), FadeIn(tag2), run_time=0.5)   # the yellow dot and label fade in

        batch = ax.c2p([-3, 0, 3], [-2, 0, 2])   # batch conversion: pass two equal-length arrays to compute 3 points at once
        dots3 = VGroup(*[Dot(pt, color=BLUE) for pt in batch])   # three blue dots placed on the diagonal
        win.play(FadeIn(dots3), run_time=0.4)   # the three blue dots fade in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


SCENES = [
    ("03-Coordinate-Conversion-c2p_p2c", C2PDemo),
]

PAIRS = [
    ("03-Coordinate-Conversion-c2p_p2c", ["03-Coordinate-Conversion-c2p_p2c"]),
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
