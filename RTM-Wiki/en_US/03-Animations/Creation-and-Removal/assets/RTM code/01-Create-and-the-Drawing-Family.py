# -*- coding: utf-8 -*-
"""Full source of the four samples in 01-Create-and-the-Drawing-Family.md (word for word identical to the code blocks on the page).

Usage: python 01-Create-and-the-Drawing-Family.py <clip-name>...
With no arguments it renders every clip and concatenates the four sample videos shown on the page (written to the parent assets/).
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
    Scene, Text, Circle, Square, VGroup,
    BLUE, GREEN, ORANGE, YELLOW, GREY_B,
    UP, DOWN,
    double_smooth, linear, smooth,
    Create, DrawBorderThenFill, FadeIn, ShowPartial, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: Create's lag_ratio and the full set of common parameters ====
class CreateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-Create", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l1 = Text("Create(mobject, lag_ratio=0.3, introducer=True,",
                  font_size=30, color=GREY_B)
        l2 = Text("         run_time=1.3, rate_func=smooth, remover=False, ...)",
                  font_size=30, color=GREY_B)
        lab1 = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # two-line "Create" signature label
        obj1 = Text("Create", font_size=52, color=BLUE).next_to(lab1, DOWN, buff=0.7)   # the letters drawn stroke by stroke
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)   # label fades in from below
        win.play(
            Create(obj1,                               # parameter "mobject"
                   lag_ratio=0.3,                      # parameter "lag_ratio": letters are drawn one after another
                   introducer=True,                    # parameter "introducer"
                   run_time=1.3,                       # parameter "run_time"
                   rate_func=smooth,                   # parameter "rate_func"
                   remover=False,                      # parameter "remover": kept after drawing
                   name="Create(Text)",                # parameter "name"
                   suspend_mobject_updating=True,      # parameter "suspend_mobject_updating"
                   reverse_rate_function=False,        # parameter "reverse_rate_function"
                   use_override=True),                 # parameter "use_override"
            run_time=1.3,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


# ===== Sample 2: Write's linear and explicitly overriding the automatic run_time/lag_ratio ====
class WriteDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-Write", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l3 = Text("Write(vmobject, rate_func=linear, reverse=False,",
                  font_size=30, color=GREY_B)
        l4 = Text("        run_time=1.5, lag_ratio=0.2, stroke_width=2, ...)",
                  font_size=30, color=GREY_B)
        lab2 = VGroup(l3, l4).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # two-line "Write" signature label
        obj2 = Text("Hello Manim", font_size=48, color=GREEN).next_to(lab2, DOWN, buff=0.7)   # the text being written
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)   # label fades in from below
        win.play(
            Write(obj2,                                # parameter "vmobject"
                  rate_func=linear,                    # parameter "rate_func": constant-speed handwriting
                  reverse=False,                       # parameter "reverse": write in forward order
                  run_time=1.5,                        # parameter "run_time": overrides the automatic value
                  lag_ratio=0.2,                       # parameter "lag_ratio": overrides the automatic value
                  stroke_width=2,                      # parameter "stroke_width"
                  stroke_color=None),                  # parameter "stroke_color"
            run_time=1.5,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


# ===== Sample 3: DrawBorderThenFill strokes the outline first, then fills ====
class BorderFillDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-DrawBorderThenFill", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l5 = Text("DrawBorderThenFill(vmobject, run_time=1.8,",
                  font_size=30, color=GREY_B)
        l6 = Text("    rate_func=double_smooth, stroke_width=6,",
                  font_size=30, color=GREY_B)
        l7 = Text("    stroke_color=BLUE, introducer=True)",
                  font_size=30, color=GREY_B)
        lab3 = VGroup(l5, l6, l7).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # three-line signature label
        obj3 = (Square(side_length=1.8, color=ORANGE)
                .set_fill(ORANGE, 1.0).next_to(lab3, DOWN, buff=0.6))   # the filled orange square
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)   # label fades in from below
        win.play(
            DrawBorderThenFill(                        # parameter "vmobject"
                obj3,
                run_time=1.8,                          # parameter "run_time"
                rate_func=double_smooth,               # parameter "rate_func": one smoothing pass per stage
                stroke_width=6,                        # parameter "stroke_width": a thicker outline
                stroke_color=BLUE,                     # parameter "stroke_color": a blue outline
                introducer=True),                      # parameter "introducer"
            run_time=1.8,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


# ===== Sample 4: ShowPartial, the abstract base class, played straight in (measured to play under RTM) ====
class ShowPartialDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-ShowPartial", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l8 = Text("ShowPartial(mobject, run_time=1.3, introducer=True)",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   # signature label
        obj4 = Circle(radius=0.7, color=GREEN).next_to(l8, DOWN, buff=0.7)   # the circle drawn frame by frame
        win.play(FadeIn(l8, shift=DOWN), run_time=0.4)   # label fades in from below
        win.play(
            ShowPartial(obj4,                          # parameter "mobject"
                        run_time=1.3,                  # parameter "run_time"
                        introducer=True),              # parameter "introducer"
            run_time=1.3,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


SCENES = [
    ("create", CreateDemo),
    ("write", WriteDemo),
    ("border_fill", BorderFillDemo),
    ("showpartial", ShowPartialDemo),
]

PAIRS = [
    ("create", ["create"]),
    ("write", ["write"]),
    ("border_fill", ["border_fill"]),
    ("showpartial", ["showpartial"]),
]

PAGE = "01-Create-and-the-Drawing-Family"


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
