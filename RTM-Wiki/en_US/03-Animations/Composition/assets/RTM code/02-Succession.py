# -*- coding: utf-8 -*-
"""Full source of the two samples in 02-Succession.md (identical to the code blocks in the page).

Usage: python 02-Succession.py <clip name>...
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
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    Scene, Text, VGroup, Square, Circle,
    RED, BLUE, GREEN, GREY_B, YELLOW,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, Write, smooth,
)
from real_time_manim.vulkan_bind import MLWindow, Succession, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: four serial segments scheduled in one play =================
class SuccessionDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("02-Succession", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        l1 = Text("Succession(sq1.animate.move_to(sq2),", font_size=30, color=GREY_B)
        l2 = Text("           sq2.animate.move_to(sq3), Wait(0.6),", font_size=30, color=GREY_B)
        l3 = Text("           sq3.animate(run_time=0.8).set_color(RED))", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2, l3).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #signature labels
        sq1 = Square(side_length=1.1, color=BLUE).set_fill(BLUE, 0.5).shift(LEFT * 3.6 + DOWN * 2.1)   #blue square
        sq2 = Square(side_length=1.1, color=GREEN).set_fill(GREEN, 0.5).shift(DOWN * 2.1)   #green square
        sq3 = Square(side_length=1.1, color=GREY_B).shift(RIGHT * 3.6 + DOWN * 2.1)   #grey square
        win.play(FadeIn(sig, shift=DOWN), FadeIn(VGroup(sq1, sq2, sq3)), run_time=0.4)   #labels and squares fade in
        win.play(Succession(                                      #param "*animations" (4 child animations)
            sq1.animate(run_time=1.0).move_to(sq2.get_center()),
            sq2.animate(run_time=1.0).move_to(sq3.get_center()),
            Wait(0.6),                                            #param "*animations" (Wait used directly as an empty segment)
            sq3.animate(run_time=0.8).set_color(RED),
        ))
        win.play(Wait(0.6))   #hold to see the result
        win.close()   #close the RTM window


# ===== Sample 2: rate_func applied to the whole serial axis =================
class SuccessionRateFuncDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("02-SuccessionRateFunc", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        l1 = Text("Succession(a.animate.shift(UP), b.animate.shift(UP),", font_size=30, color=GREY_B)
        l2 = Text("           rate_func=smooth)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #signature labels
        a = Circle(radius=0.55, color=RED).set_fill(RED, 0.5).shift(LEFT * 2.2 + DOWN * 2.3)   #red circle
        b = Circle(radius=0.55, color=BLUE).set_fill(BLUE, 0.5).shift(RIGHT * 2.2 + DOWN * 2.3)   #blue circle
        win.play(FadeIn(sig, shift=DOWN), FadeIn(VGroup(a, b)), run_time=0.4)   #labels and circles fade in
        win.play(Succession(                                      #param "rate_func" (applied to the whole serial timeline)
            a.animate(run_time=1.0).shift(UP * 1.6),
            b.animate(run_time=1.0).shift(UP * 1.6),
            rate_func=smooth,
        ))
        win.play(Wait(0.6))   #hold to see the result
        win.close()   #close the RTM window


SCENES = [
    ("succession", SuccessionDemo),
    ("ratefunc", SuccessionRateFuncDemo),
]

PAIRS = [
    ("succession", ["succession"]),
    ("ratefunc", ["ratefunc"]),
]

PAGE = "02-Succession"


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
