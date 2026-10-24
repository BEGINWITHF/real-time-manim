# -*- coding: utf-8 -*-
"""Full source of the three samples in 01-AnimationGroup-and-Lag-Ratios.md (identical to the code blocks in the page).

Usage: python 01-AnimationGroup-and-Lag-Ratios.py <clip name>...
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
    Scene, Text, VGroup, Square, Circle, Triangle, Dot,
    RED, BLUE, GREEN, PURPLE, GREY_B, YELLOW,
    UP, DOWN, LEFT, RIGHT,
    ApplyMethod, FadeIn, LaggedStart, LaggedStartMap, Write,
    linear, there_and_back,
)
from real_time_manim.vulkan_bind import MLWindow, AnimationGroup, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: AnimationGroup starts in turn ==============================
class AnimationGroupDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("01-AnimationGroup", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        l1 = Text("AnimationGroup(sq.animate.shift(UP),", font_size=30, color=GREY_B)
        l2 = Text("              ci.animate.shift(DOWN), tr.animate.shift(UP),", font_size=28, color=GREY_B)
        l3 = Text("              lag_ratio=0.5, rate_func=linear);  ag.run_time = 1.8", font_size=28, color=GREY_B)
        sig = VGroup(l1, l2, l3).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #signature labels
        sq = Square(side_length=1.2, color=RED).set_fill(RED, 0.5).shift(LEFT * 3.4 + DOWN * 2.1)   #red square
        ci = Circle(radius=0.65, color=BLUE).set_fill(BLUE, 0.5).shift(DOWN * 2.1)   #blue circle
        tr = Triangle(color=GREEN).scale(0.8).set_fill(GREEN, 0.5).shift(RIGHT * 3.4 + DOWN * 2.1)   #green triangle
        win.play(FadeIn(sig, shift=DOWN), FadeIn(VGroup(sq, ci, tr)), run_time=0.4)   #labels and shapes fade in
        ag = AnimationGroup(                                      #param "*animations" (3 .animate builders)
            sq.animate.shift(UP * 1.4),
            ci.animate.shift(DOWN * 1.4),
            tr.animate.shift(UP * 1.4),
            lag_ratio=0.5,                                        #param "lag_ratio" (red → blue → green start in turn)
            rate_func=linear,                                     #param "rate_func" (group-level)
        )
        ag.run_time = 1.8                                         #param "run_time" (attribute assignment stretches the whole axis to 1.8s)
        win.play(ag)   #the three actions start in turn
        win.play(Wait(0.6))   #hold to see the result
        win.close()   #close the RTM window


# ===== Sample 2: LaggedStart streaming stagger ==============================
class LaggedStartDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("01-LaggedStart", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        l1 = Text("LaggedStart(*[FadeIn(d, shift=DOWN) for d in dots],", font_size=30, color=GREY_B)
        l2 = Text("            lag_ratio=0.3, run_time=1.6)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #signature labels
        cols = [RED, YELLOW, GREEN, BLUE, PURPLE]   #colours of the 5 lanes
        dots = VGroup(*[Dot(radius=0.18, color=c).shift(LEFT * 4.4 + RIGHT * 2.2 * i + DOWN * 1.8)   #5 coloured dots
                        for i, c in enumerate(cols)])
        win.play(FadeIn(sig, shift=DOWN), run_time=0.4)   #labels fade in
        win.play(LaggedStart(                                    #param "*animations" (5 FadeIns in different colours)
            *[FadeIn(d, shift=DOWN) for d in dots],
            lag_ratio=0.3,                                       #param "lag_ratio" (streaming stagger)
            run_time=1.6,                                        #param "run_time"
        ))
        win.play(Wait(0.6))   #hold to see the result
        win.close()   #close the RTM window


# ===== Sample 3: LaggedStartMap bulk animation ==============================
class LaggedStartMapDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("01-LaggedStartMap", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        l1 = Text("LaggedStartMap(ApplyMethod, words,", font_size=30, color=GREY_B)
        l2 = Text("   lambda m: (m.set_color, YELLOW),", font_size=30, color=GREY_B)
        l3 = Text("   lag_ratio=0.15, run_time=2.0, rate_func=there_and_back)", font_size=28, color=GREY_B)
        sig = VGroup(l1, l2, l3).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #signature labels
        words = Text("manim", font_size=64, color=GREY_B).shift(DOWN * 1.9)   #the word tinted letter by letter
        win.play(FadeIn(sig, shift=DOWN), FadeIn(words), run_time=0.4)   #labels and word fade in
        win.play(LaggedStartMap(                                 #param "animation_class / mobject / arg_creator"
            ApplyMethod, words,
            lambda m: (m.set_color, YELLOW),                     #param "arg_creator" (submob -> argument tuple)
            lag_ratio=0.15,                                      #param "lag_ratio"
            run_time=2.0,                                        #param "run_time"
            rate_func=there_and_back,                            #param "**kwargs" (passed through to each child animation)
        ))
        win.play(Wait(0.6))   #hold to see the result
        win.close()   #close the RTM window


SCENES = [
    ("animationgroup", AnimationGroupDemo),
    ("laggedstart", LaggedStartDemo),
    ("laggedstartmap", LaggedStartMapDemo),
]

PAIRS = [
    ("animationgroup", ["animationgroup"]),
    ("laggedstart", ["laggedstart"]),
    ("laggedstartmap", ["laggedstartmap"]),
]

PAGE = "01-AnimationGroup-and-Lag-Ratios"


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
