# -*- coding: utf-8 -*-
"""Full source of the three samples in 02-Reverse-Removal.md (word for word identical to the code blocks on the page).

Usage: python 02-Reverse-Removal.py <clip-name>...
With no arguments it renders every clip and concatenates the three sample videos shown on the page (written to the parent assets/).
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
    Scene, Text, Square, Rectangle, Circle, VGroup,
    BLUE, GREEN, RED, YELLOW, GREY_B,
    UP, DOWN, LEFT, RIGHT,
    linear, smooth,
    Create, FadeIn, Uncreate, Unwrite, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait, Succession, Add
from real_time_manim.record import fast_record_scene


# ===== Sample 1: Uncreate's reverse erasing =================================
class UncreateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02-Uncreate", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l1 = Text("Uncreate(mobject, reverse_rate_function=True, remover=True,",
                  font_size=30, color=GREY_B)
        l2 = Text("         lag_ratio=1.0, run_time=1.2, rate_func=smooth)",
                  font_size=30, color=GREY_B)
        lab1 = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # two-line "Uncreate" signature label
        sq = Square(side_length=1.6, color=BLUE).next_to(lab1, DOWN, buff=0.6)   # the blue square to draw first and erase later
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)   # label fades in from below
        win.play(Create(sq, run_time=1.0), run_time=1.0)   # draw the square first
        win.play(
            Uncreate(sq,                            # parameter "mobject"
                     reverse_rate_function=True,    # parameter "reverse_rate_function": play backwards
                     remover=True,                  # parameter "remover": removed from the scene once erased
                     lag_ratio=1.0,                 # parameter "lag_ratio"
                     run_time=1.2,                  # parameter "run_time"
                     rate_func=smooth),             # parameter "rate_func"
            run_time=1.2,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


# ===== Sample 2: Unwrite's reverse=False erasing from the start =============
class UnwriteDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02-Unwrite", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l3 = Text("Unwrite(vmobject, rate_func=linear, reverse=False,",
                  font_size=30, color=GREY_B)
        l4 = Text("        run_time=1.4, lag_ratio=0.2)",
                  font_size=30, color=GREY_B)
        lab2 = VGroup(l3, l4).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # two-line "Unwrite" signature label
        txt = Text("Goodbye Manim", font_size=44, color=GREEN).next_to(lab2, DOWN, buff=0.6)   # the text to write first and erase later
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)   # label fades in from below
        win.play(Write(txt, rate_func=linear, run_time=1.0), run_time=1.0)   # write the text first
        win.play(
            Unwrite(txt,                            # parameter "vmobject"
                    rate_func=linear,               # parameter "rate_func": constant-speed erasing by hand
                    reverse=False,                  # parameter "reverse": non-default, erase from the start
                    run_time=1.4,                   # parameter "run_time"
                    lag_ratio=0.2),                 # parameter "lag_ratio"
            run_time=1.4,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


# ===== Sample 3: Add sequenced on a Succession timeline =====================
class AddDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02-Add", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l5 = Text("Add(*mobjects, run_time=0.0 instant / 0.5 hold) in Succession",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   # signature label
        rect = (Rectangle(width=3.4, height=1.4, color=YELLOW)
                .next_to(l5, DOWN, buff=0.6))   # the yellow box holding the dots
        dot_a = Circle(radius=0.16, color=GREEN).move_to(rect.get_left() + RIGHT * 0.7)   # the first dot to be added
        dot_b = Circle(radius=0.16, color=RED).move_to(rect.get_center() + RIGHT * 0.7)   # the second dot to be added
        dot_c = Circle(radius=0.16, color=BLUE).move_to(rect.get_right() + LEFT * 0.7)   # added in the same group as "dot_b"
        win.play(FadeIn(l5, shift=DOWN), run_time=0.4)   # label fades in from below
        win.play(Create(rect, run_time=0.8), run_time=0.8)   # draw the yellow box
        win.play(
            Succession(
                Add(dot_a, run_time=0.0),           # parameter "run_time=0.0": added instantly
                Wait(0.4),                          # 0.4s gap
                Add(dot_b, dot_c, run_time=0.5),    # more than 1 is wrapped into a Group; run_time=0.5 holds for half a second
            ),
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


SCENES = [
    ("uncreate", UncreateDemo),
    ("unwrite", UnwriteDemo),
    ("add", AddDemo),
]

PAIRS = [
    ("uncreate", ["uncreate"]),
    ("unwrite", ["unwrite"]),
    ("add", ["add"]),
]

PAGE = "02-Reverse-Removal"


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
