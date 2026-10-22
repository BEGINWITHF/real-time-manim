# -*- coding: utf-8 -*-
"""Full source of the five samples in 01-Wait-Rate-and-Speed.md (word for word identical to the code blocks on the page).

Usage: python 01-Wait-Rate-and-Speed.py <clip-name>...
With no arguments it renders every clip and concatenates the five sample videos shown on the page (written to the parent assets/).
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
    Scene, Text, VGroup, Square, Dot, Line,
    BLUE, GREEN, GREY_B, ORANGE, RED, YELLOW,
    UP, DOWN, LEFT, RIGHT,
    Animation, AnimationGroup, ChangeSpeed, FadeIn, FadeOut, Write,
)
from real_time_manim import (
    exponential_decay, linear, rush_from, rush_into, smooth,
    squish_rate_func, there_and_back, wiggle,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: Wait's pure wait ===========================================
class WaitDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-Wait", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        lab = Text("win.play(Wait(1.0))   # run_time=1.0s",
                   font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   # signature label
        sq = Square(side_length=1.1, color=BLUE).set_fill(BLUE, 0.5).next_to(lab, DOWN, buff=0.6)   # the blue square during the wait
        txt = Text("waiting...", font_size=30, color=GREY_B).next_to(sq, DOWN, buff=0.4)   # the waiting hint text
        win.play(FadeIn(lab, shift=DOWN), FadeIn(sq), FadeIn(txt), run_time=0.4)   # the label and square fade in
        win.play(Wait(1.0))   # parameter "run_time": wait 1 second doing nothing
        win.play(FadeOut(VGroup(lab, sq, txt)), run_time=0.4)   # the whole group fades out to close
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


# ===== Sample 2: ChangeSpeed paced by percentage ============================
class ChangeSpeedDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-ChangeSpeed", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        lab3 = Text("ChangeSpeed(AnimationGroup(a.shift, b.shift),",
                    font_size=30, color=GREY_B)
        lab4 = Text("  speedinfo={0.3:1, 0.5:0.25, 1:2}, rate_func=linear)",
                    font_size=30, color=GREY_B)
        lab = VGroup(lab3, lab4).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # two-line signature label
        a = Dot(radius=0.14, color=RED).move_to(LEFT * 3.2 + DOWN * 1.2)
        b = Dot(radius=0.14, color=BLUE).move_to(RIGHT * 3.2 + DOWN * 1.2)
        trk = Line(LEFT * 3.2 + DOWN * 1.2, RIGHT * 3.2 + DOWN * 1.2, stroke_width=2, color=GREY_B)
        trk.set_stroke(opacity=0.4)
        win.play(FadeIn(lab, shift=DOWN), FadeIn(VGroup(a, b, trk)), run_time=0.4)   # the label and the two colliding dots fade in
        win.play(ChangeSpeed(
            AnimationGroup(a.animate(run_time=1).shift(RIGHT * 6.4),
                           b.animate(run_time=1).shift(LEFT * 6.4)),
            speedinfo={0.3: 1, 0.5: 0.25, 1: 2},   # parameter "speedinfo": normal speed for the first 30%, 0.25x in the middle, 2x at the end
            rate_func=linear,                      # parameter "rate_func"
            affects_speed_updaters=True))          # parameter "affects_speed_updaters"
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


# ===== Sample 3: an updater attached with add_updater follows the speed change =====
class ChangeSpeedUpdaterDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-ChangeSpeed-updater", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        lab5 = Text("ChangeSpeed.add_updater(m, fn)  +  ChangeSpeed(",
                    font_size=30, color=GREY_B)
        lab6 = Text("    Wait(1.6), speedinfo={0.3:1, 0.55:0.15, 1:1})",
                    font_size=30, color=GREY_B)
        lab = VGroup(lab5, lab6).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # two-line signature label
        m = Dot(radius=0.14, color=YELLOW).move_to(LEFT * 3.2 + DOWN * 1.2)
        trk = Line(LEFT * 3.2 + DOWN * 1.2, RIGHT * 3.2 + DOWN * 1.2, stroke_width=2, color=GREY_B)
        trk.set_stroke(opacity=0.4)
        win.play(FadeIn(lab, shift=DOWN), FadeIn(VGroup(m, trk)), run_time=0.4)   # the label and track fade in
        ChangeSpeed.add_updater(m, lambda mob, dt: mob.shift(RIGHT * 3.4 * dt))   # parameter "ChangeSpeed.add_updater": attach a speed-changing updater
        win.play(ChangeSpeed(Wait(1.6), speedinfo={0.3: 1, 0.55: 0.15, 1: 1},   # parameter "speedinfo": 0.15x slow motion in the middle
                             affects_speed_updaters=True))
        m.clear_updaters()   # detach the updater
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


# ===== Sample 4: Animation base-class placeholder ===========================
class AnimationDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-Animation", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        lab = Text("Animation(sq, run_time=1.2, rate_func=linear)  # placeholder",
                   font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   # signature label
        sq = Square(side_length=1.3, color=GREEN).set_fill(GREEN, 0.5).next_to(lab, DOWN, buff=0.6)   # the green square that stays put as a placeholder
        win.play(FadeIn(lab, shift=DOWN), FadeIn(sq), run_time=0.4)   # the label and square fade in
        win.play(Animation(sq, run_time=1.2, rate_func=linear))   # parameter "mobject" / "run_time" / "rate_func": takes up 1.2 seconds
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


# ===== Sample 5: 8 rate functions compared in the same scene ================
class RateFuncDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-rate_func", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        cols = [RED, BLUE, GREEN, ORANGE]
        names1 = ["linear", "smooth", "rush_into", "rush_from"]
        funcs1 = [linear, smooth, rush_into, rush_from]
        lab1 = Text("dot.animate(run_time=1.8, rate_func=F).shift(RIGHT*6.4)",
                    font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   # signature label
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)   # label fades in from below
        tracks = VGroup()
        labels1 = VGroup()
        dots1 = []
        for i, nm in enumerate(names1):
            y = 0.55 - i * 1.15
            labels1.add(Text(nm, font_size=26, color=cols[i]).move_to(LEFT * 5.6 + UP * y))
            trk = Line(LEFT * 3.2 + UP * y, RIGHT * 3.2 + UP * y, stroke_width=2, color=GREY_B)
            trk.set_stroke(opacity=0.4)
            tracks.add(trk)
            dots1.append(Dot(radius=0.12, color=cols[i]).move_to(trk.get_start()))
        win.play(FadeIn(labels1), FadeIn(tracks), FadeIn(VGroup(*dots1)), run_time=0.4)   # the four tracks get in place
        win.play(*[d.animate(run_time=1.8, rate_func=f).shift(RIGHT * 6.4)
                   for d, f in zip(dots1, funcs1)])   # parameter "rate_func" x4: running together to pull the positions apart
        win.play(Wait(0.4))   # pause to see the result
        win.play(FadeOut(lab1), FadeOut(labels1), run_time=0.3)   # swap the label
        for d in dots1:   # put them back at the start with no animation: change the attributes directly
            d.move_to(LEFT * 3.2 + UP * d.get_center()[1])
        names2 = ["there_and_back", "exponential_decay", "squish(.35,.65)", "wiggle"]
        funcs2 = [there_and_back, exponential_decay, squish_rate_func(linear, 0.35, 0.65), wiggle]
        labels2 = VGroup()
        for i, nm in enumerate(names2):
            labels2.add(Text(nm, font_size=26, color=cols[i]).move_to(LEFT * 5.6 + UP * (0.55 - i * 1.15)))
        lab2 = Text("reset: 4 more rate_funcs (round-trip / overshoot)",
                    font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   # second batch signature label
        win.play(FadeIn(lab2, shift=DOWN), FadeIn(labels2), run_time=0.3)   # the second batch's label fades in
        win.play(*[d.animate(run_time=1.8, rate_func=f).shift(RIGHT * 6.4)
                   for d, f in zip(dots1, funcs2)])   # parameter "rate_func" x4: round-trip / decay / squish / wobble
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


SCENES = [
    ("wait", WaitDemo),
    ("changespeed", ChangeSpeedDemo),
    ("changespeed_updater", ChangeSpeedUpdaterDemo),
    ("animation", AnimationDemo),
    ("ratefunc", RateFuncDemo),
]

PAIRS = [
    ("wait", ["wait"]),
    ("changespeed", ["changespeed"]),
    ("changespeed_updater", ["changespeed_updater"]),
    ("animation", ["animation"]),
    ("ratefunc", ["ratefunc"]),
]

PAGE = "01-Wait-Rate-and-Speed"


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
