# -*- coding: utf-8 -*-
"""Full source of the three samples in 01-The-Fade-Family.md (word for word identical to the code blocks on the page).

Usage: python 01-The-Fade-Family.py <clip-name>...
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    Scene, Square, Circle, Triangle, Text, VGroup,
    BLUE, GREEN, RED, YELLOW, GREY_B,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    smooth, linear,
    AnimationGroup, Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: FadeIn's shift / scale / target_position ===================
class FadeInDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-FadeIn", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l1 = Text("FadeIn(mobject, shift=DOWN, scale=0.5, run_time=1.1,",
                  font_size=30, color=GREY_B)
        l2 = Text("        lag_ratio=0.0, name='FadeIn')   FadeIn(c, target_position=ORIGIN)",
                  font_size=30, color=GREY_B)
        lab1 = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # two-line "FadeIn" signature label
        sq = Square(side_length=1.3, color=BLUE).next_to(lab1, DOWN, buff=0.6).shift(LEFT * 2.2)   # demo object "sq"
        ci = Circle(radius=0.6, color=GREEN).next_to(lab1, DOWN, buff=0.6).shift(RIGHT * 2.2)   # demo object "ci"
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)   # label fades in from below
        win.play(
            FadeIn(sq,                               # one of "*mobjects"
                   shift=DOWN,                       # parameter "shift": enters from below
                   scale=0.5,                        # parameter "scale": grows back to full size from half size
                   run_time=1.1,                     # parameter "run_time"
                   lag_ratio=0.0,                    # parameter "lag_ratio"
                   name="FadeIn(Square)",            # parameter "name"
                   suspend_mobject_updating=True,    # parameter "suspend_mobject_updating"
                   reverse_rate_function=False,      # parameter "reverse_rate_function"
                   use_override=True),               # parameter "use_override"
            FadeIn(ci,                               # the second of "*mobjects" (another instance)
                   target_position=ORIGIN,           # parameter "target_position": drifts in from the center
                   run_time=1.1),                    # parameter "run_time"
            run_time=1.1, rate_func=smooth,          # play-level "rate_func"
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


# ===== Sample 2: FadeOut's shift / scale / target_position ==================
class FadeOutDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-FadeOut", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l1 = Text("FadeIn(mobject, shift=DOWN, scale=0.5, run_time=1.1,",
                  font_size=30, color=GREY_B)
        l2 = Text("        lag_ratio=0.0, name='FadeIn')   FadeIn(c, target_position=ORIGIN)",
                  font_size=30, color=GREY_B)
        lab1 = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # the signature label left behind by the previous segment
        sq = Square(side_length=1.3, color=BLUE).next_to(lab1, DOWN, buff=0.6).shift(LEFT * 2.2)   # the object "sq" to fade out
        ci = Circle(radius=0.6, color=GREEN).next_to(lab1, DOWN, buff=0.6).shift(RIGHT * 2.2)   # the object "ci" to fade out
        self.add(lab1, sq, ci)   # put the demo objects into the scene statically first (the star of this sample is "FadeOut")
        l3 = Text("FadeOut(sq, shift=UP, run_time=1.0)   FadeOut(ci, scale=0.3, ...)",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   # the swap label (in the same slot as lab1)
        win.play(FadeOut(lab1), FadeIn(l3, shift=DOWN), run_time=0.4)   # the old label fades out and the new one swaps in place
        win.play(
            FadeOut(sq,                              # one of "*mobjects"
                    shift=UP,                        # parameter "shift": drifts out upward
                    run_time=1.0,                    # parameter "run_time"
                    lag_ratio=0.0),                  # parameter "lag_ratio"
            FadeOut(ci,                              # the second of "*mobjects"
                    scale=0.3,                       # parameter "scale": shrinks to 0.3 times during the fade-out
                    target_position=ORIGIN,          # parameter "target_position": fades toward the center
                    run_time=1.0,                    # parameter "run_time"
                    name="FadeOut(Circle)"),         # parameter "name"
            run_time=1.0, rate_func=linear,          # play-level "rate_func"
        )
        win.play(FadeOut(l3), run_time=0.4)   # the label fades out too
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


# ===== Sample 3: the manual's "page-swap" AnimationGroup one-for-one ========
class SwapGroupDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-AnimationGroup swap", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l4 = Text("AnimationGroup(FadeOut(x, shift=UP), FadeIn(y1, y2, shift=UP))",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   # combination signature label
        x = (Square(side_length=1.2, color=RED).set_fill(RED, 0.6)
             .next_to(l4, DOWN, buff=0.7).shift(LEFT * 2.0))   # the red square "x" to be swapped out
        ya = Circle(radius=0.5, color=YELLOW).move_to(x)   # swap-in object one: stacked at "x"'s original position
        yb = (Triangle(color=GREEN).scale(0.9)
              .next_to(l4, DOWN, buff=0.7).shift(RIGHT * 2.0))   # swap-in object two
        win.play(FadeIn(l4, shift=DOWN), run_time=0.4)   # label fades in from below
        win.play(Create(x), run_time=0.7)   # draw the square to be swapped out first
        win.play(
            AnimationGroup(
                FadeOut(x, shift=UP),                # swap out: drifts out upward
                FadeIn(ya, yb, shift=UP),            # swap in: the new objects fade in from below
                lag_ratio=0.0,                       # parameter "lag_ratio": rise and fall together
            ),
            run_time=1.2,
        )
        win.play(Wait(0.8))   # pause 0.8s
        win.close()   # close the RTM window


SCENES = [
    ("fadein", FadeInDemo),
    ("fadeout", FadeOutDemo),
    ("swap", SwapGroupDemo),
]

PAIRS = [
    ("fadein", ["fadein"]),
    ("fadeout", ["fadeout"]),
    ("swap", ["swap"]),
]

PAGE = "01-The-Fade-Family"


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
