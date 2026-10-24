# -*- coding: utf-8 -*-
"""Full source of the three samples in 11b-Misc-APIs.md (identical to the code blocks in the page).

get_image / show / save_image and the three mobject.utils factory functions cannot be rendered (see the page),
so there are no corresponding sample classes.

Usage: python 11b-Misc-APIs.py <clip name>...
With no arguments it renders every clip and concatenates the page's three sample videos (output to the parent assets/).
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
    Scene, Group, VGroup, Square, Circle, Line, Dot,
    BLUE, RED, GREEN, YELLOW, PURPLE, ORANGE, GREY,
    UP, DOWN, LEFT, RIGHT, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: sort / shuffle / invert =================================
class SortShuffleInvertDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        colors = (RED, BLUE, GREEN, YELLOW, PURPLE)   # five colours
        spots = (LEFT * 3.5 + UP * 1.4, RIGHT * 2.0 + UP * 0.6, LEFT * 1.0 + DOWN * 1.2, RIGHT * 3.2 + DOWN * 1.6, LEFT * 2.4)   # five distinct scattered positions
        v = VGroup(*[Square(color=c, side_length=0.8).shift(p) for c, p in zip(colors, spots)])   # scatter them first
        self.add(v)   # add to the scene
        win.play(Wait(0.4))   # pause to see the initial scattered positions
        v.sort()   #sort: reorder the list left-to-right by current centre x
        win.play(v.animate.arrange(RIGHT, buff=0.3), run_time=0.5)   # line them up in list order: colours ordered by position
        v.invert(recursive=False)   #invert: reverse the list order
        win.play(v.animate.arrange(RIGHT, buff=0.3), run_time=0.5)   # the order is entirely reversed
        random.seed(7)   # fix the random seed for reproducibility
        v.shuffle(recursive=False)   #shuffle: randomise
        win.play(v.animate.arrange(RIGHT, buff=0.3), run_time=0.5)   # random order
        v.sort(submob_func=lambda m: str(m.color))   #submob_func takes priority: sort by colour name
        win.play(v.animate.arrange(RIGHT, buff=0.3), run_time=0.5)   # colour names A to Z
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window


# ===== Sample 2: apply_to_family =========================================
class ApplyFamilyDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        v = VGroup(*[Square(color=BLUE, side_length=0.9) for _ in range(3)])   # three squares
        v.arrange(RIGHT, buff=0.3).shift(UP * 1.5)
        self.add(v)   # add to the scene
        v.apply_to_family(lambda m: m.set_stroke(width=6))   # called once for every member with points
        win.play(FadeIn(v), run_time=0.4)   # squares with thick strokes fade in
        g = Group(Circle(radius=0.45), Circle(radius=0.45)).arrange(RIGHT, buff=0.4).shift(DOWN * 1.5)   # two circles
        self.add(g)   # add to the scene
        g.apply_to_family(lambda m: m.set_stroke(color=RED, width=6))   # works for the circles too
        win.play(FadeIn(g), run_time=0.4)   # circles with red thick strokes fade in
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window


# ===== Sample 3: the point-along-path family =============================
class PathDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        line = Line(LEFT * 3.5, RIGHT * 0.5, color=YELLOW).shift(UP * 1.5)   # a line segment
        self.add(line)   # add to the scene
        print("get_start =", line.get_start().round(2))   # first vertex
        print("get_end =", line.get_end().round(2))   # last vertex
        p = line.point_from_proportion(0.25)   # 25% along the path
        self.add(Dot(color=RED, radius=0.09).move_to(p))   # mark it with a dot
        print("point_from_proportion(0.25) =", p.round(2))
        pieces = line.get_pieces(4)   # cut into 4 segments
        pieces.set_color_by_gradient(RED, BLUE)
        self.add(pieces)   # add to the scene
        win.play(FadeIn(pieces), run_time=0.5)   # the four gradient segments appear
        c = Circle(radius=0.9, color=ORANGE).shift(RIGHT * 3.0 + DOWN * 1.2)   # circle: taking a point on a curve is more intuitive
        self.add(c)   # add to the scene
        q = c.point_from_proportion(0.25)
        print("circle 25% =", q.round(2))
        print("proportion_from_point =", round(c.proportion_from_point(q), 4))   # invert back to a proportion
        win.play(FadeIn(c), run_time=0.4)   # the circle fades in
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window


SCENES = [
    ("sort_shuffle_invert", SortShuffleInvertDemo),
    ("apply_family", ApplyFamilyDemo),
    ("path", PathDemo),
]

PAIRS = [
    ("sort_shuffle_invert", ["sort_shuffle_invert"]),
    ("apply_family", ["apply_family"]),
    ("path", ["path"]),
]

PAGE = "11b-Misc-APIs"


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
