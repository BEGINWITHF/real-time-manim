# -*- coding: utf-8 -*-
"""Full source for the five samples in 01b-Construction-and-Containers-Advanced.md (identical to the code blocks in the page).

Usage: python 01b-Construction-and-Containers-Advanced.py <clip names>...
With no arguments it renders every clip and concatenates the page's five sample videos (written to the parent assets/).
"""
import os
import subprocess
import sys
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    Scene, Group, VGroup,
    Square, Rectangle, Circle, Text,
    WHITE, RED, BLUE, YELLOW, GREEN, ORANGE, PURPLE,
    RIGHT, DOWN, UP, LEFT, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: get_family / family_members_with_points / split ==========
class FamilyDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        inner = VGroup(Square(color=RED, side_length=1.0), Square(color=BLUE, side_length=1.0))   # inner layer: two squares
        inner.arrange(RIGHT, buff=0.4)   # line up the inner layer
        empty = Group()   # empty container: not a single vertex
        solo = Square(color=GREEN, side_length=1.0)   # standalone square
        outer = Group(inner, empty, solo)   # outer layer: the inner group, the empty group, one square
        inner.shift(LEFT * 2.2)   # put the inner group on the left (don't use arrange: the empty group is zero wide and they would squeeze together)
        solo.shift(RIGHT * 2.2)   # put the standalone square on the right
        outer.shift(UP * 1.0)   # lift the whole tree a little
        self.add(outer)   # add the whole tree to the scene
        print("get_family =", len(outer.get_family()), [type(m).__name__ for m in outer.get_family()])   # self + all descendants
        print("family_members_with_points =", [type(m).__name__ for m in outer.family_members_with_points()])   # only those owning vertices
        print("split =", [type(m).__name__ for m in outer.split()])   # self (if it has points) + direct children
        for i, m in enumerate(outer.family_members_with_points()):   # the objects shift/scale actually act on
            m.set_color([ORANGE, YELLOW, PURPLE][i])   # color them one by one: only the three squares get colored
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


# ===== Sample 2: has_points / has_no_points / get_num_points ==============
class PointsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        g = Group()   # empty container
        sq = Square(color=BLUE, side_length=1.6)   # a square with vertices
        txt = Text("points", font_size=36, color=YELLOW)   # text: the points live in its glyph children
        sq.shift(LEFT * 3.2)   # put the square on the left
        txt.shift(RIGHT * 2.4)   # put the text on the right
        self.add(sq, txt)   # add both objects to the scene
        print("empty Group: has_points =", g.has_points(), "has_no_points =", g.has_no_points(), "get_num_points =", g.get_num_points())   # all "empty"
        print("Square: has_points =", sq.has_points(), "get_num_points =", sq.get_num_points())   # the square owns vertices
        print("Text itself get_num_points =", txt.get_num_points(), "| glyphs =", [m.get_num_points() for m in txt.submobjects])   # the points are in the glyphs
        win.play(FadeIn(sq), FadeIn(txt), run_time=0.5)   # fade in both objects
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window


# ===== Sample 3: set ======================================================
class SetDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        rect = Rectangle(width=3.0, height=1.4, color=BLUE, fill_opacity=0.6)   # a rectangle
        self.add(rect)   # add it to the scene
        win.play(rect.animate.set(width=5.0, color=ORANGE), run_time=0.7)   # "set" with animate: change several attributes at once
        rect.set(fill_opacity=1.0)   # without "animate" the change is instant
        print("rect.width =", rect.width, "| rect.color =", rect.color)   # verify by reading the attributes back
        with warnings.catch_warnings(record=True) as w:   # the legacy get_foo / set_foo emits a warning
            warnings.simplefilter("always")
            rect.set_width(4.0)   # legacy style: works but emits a DeprecationWarning
            print("legacy warning =", [str(x.message)[:24] for x in w])   # peek at the warning text
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window


# ===== Sample 4: set_default (classmethod) ================================
class SetDefaultDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        before = Square()   # default square: side length 2, white
        Square.set_default(side_length=1.0, color=YELLOW)   # change "Square"'s default side length to 1 and default color to yellow
        after = Square()   # the new object uses the new defaults
        Square.set_default()   # called with no arguments: restore the original defaults
        back = Square()   # build one more: back to the defaults
        trio = VGroup(before, after, back)   # the three squares as one group
        trio.arrange(RIGHT, buff=0.8)   # line them up so the size difference is plain
        self.add(trio)   # add them to the scene
        print("side length:", before.width, after.width, back.width)   # 2.0 1.0 2.0
        win.play(FadeIn(trio), run_time=0.6)   # fade in the whole group
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window


# ===== Sample 5: reset_points / generate_points / init_colors =============
class WideCircle(Circle):   # custom subclass: change the shape in a construction hook
    def generate_points(self):   # the constructor calls this to generate the shape
        super().generate_points()   # first generate "Circle"'s default shape
        self.stretch(1.6, 0)   # then stretch it horizontally into a "wide ellipse"


class HooksDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        wc = WideCircle(radius=0.9, color=GREEN)   # custom subclass: stretched after generation
        c = Circle(radius=0.9, color=BLUE)   # a plain circle for comparison
        duo = VGroup(wc, c)   # the two circles as one group
        duo.arrange(DOWN, buff=0.6)   # stack them vertically
        self.add(duo)   # add them to the scene
        win.play(FadeIn(duo), run_time=0.5)   # fade in: the wide ellipse is on top
        c.reset_points()   # clear all vertices: the circle disappears
        win.play(Wait(0.5))   # pause 0.5s to see it disappear
        c.generate_points()   # regenerate the shape: the default circle reappears at the origin
        c.init_colors()   # re-initialize the style from "color"
        win.play(Wait(0.5))   # pause 0.5s to see the result
        win.close()   # close the RTM window


SCENES = [
    ("family", FamilyDemo),
    ("points", PointsDemo),
    ("set", SetDemo),
    ("set_default", SetDefaultDemo),
    ("hooks", HooksDemo),
]

PAIRS = [
    ("family", ["family"]),
    ("points", ["points"]),
    ("set", ["set"]),
    ("set_default", ["set_default"]),
    ("hooks", ["hooks"]),
]

PAGE = "01b-Construction-and-Containers-Advanced"


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
