# -*- coding: utf-8 -*-
"""Full source for the five samples in 02-Positioning.md (identical to the code blocks in the page).

Usage: python 02-Positioning.py <clip names>...
With no arguments it renders every clip and concatenates the page's five sample videos (written to the parent assets/).
"""
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

from real_time_manim import (
    Scene, Square, Dot, VGroup, ScreenRectangle,
    BLUE, RED, GREEN, YELLOW, PURPLE, ORANGE, TEAL, WHITE, GREY,
    UP, DOWN, LEFT, RIGHT, UR, DL, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: shift ====================================================
class ShiftDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.4, fill_opacity=0.6)   # blue square
        self.add(sq)   # add it to the scene
        win.play(sq.animate.shift(RIGHT * 2.0), run_time=0.5)   # translate along one vector: right 2
        win.play(sq.animate.shift(UP * 1.2, LEFT * 4.0), run_time=0.6)   # several vectors: summed internally, moving left 4 and up 1.2
        sq.shift(DOWN * 2.4, RIGHT * 1.2)   # without "animate" the move is instant: down 2.4 + right 1.2
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window


# ===== Sample 2: move_to ==================================================
class MoveToDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        dot = Dot(color=YELLOW, radius=0.12)   # target point
        dot.move_to(LEFT * 3.0 + UP * 1.6)   # put the target point in the upper left
        sq = Square(color=RED, side_length=1.2, fill_opacity=0.6)   # the square to move
        self.add(dot, sq)   # add both to the scene
        win.play(sq.animate.move_to(dot), run_time=0.6)   # default center-to-center
        win.play(sq.animate.move_to(RIGHT * 3.0 + UP * 1.6, aligned_edge=UR), run_time=0.6)   # align its own top-right corner to the target point
        win.play(sq.animate.move_to(RIGHT * 3.0 + DOWN * 1.8, coor_mask=np.array([1, 0, 0])), run_time=0.6)   # align x only, y stays put
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window


# ===== Sample 3: next_to ==================================================
class NextToDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        box = Square(color=BLUE, side_length=1.6, fill_opacity=0.6)   # the reference
        self.add(box)   # add it to the scene
        right = Square(color=RED, side_length=0.8).next_to(box, RIGHT, buff=0.3)   # direction / buff: vertically centered on the right
        up = Square(color=GREEN, side_length=0.8).next_to(box, UP, buff=0.2)   # direction=UP: horizontally centered above
        low = Square(color=ORANGE, side_length=0.8).next_to(box, RIGHT, buff=1.2, aligned_edge=DOWN)   # aligned_edge=DOWN: bottom edges aligned, not vertically centered
        duo = VGroup(Square(color=PURPLE, side_length=0.5), Square(color=TEAL, side_length=0.5))   # two small squares as one group
        duo.arrange(DOWN, buff=0.2)   # stack them vertically
        duo.next_to(box, LEFT, buff=0.3, submobject_to_align=duo[1])   # attach by its own second child
        self.add(right, up, low, duo)   # add the four neighbors to the scene
        win.play(FadeIn(right), FadeIn(up), run_time=0.5)   # fade in the right and top neighbors
        win.play(FadeIn(low), FadeIn(duo), run_time=0.5)   # fade in the bottom-aligned one and the left group
        ref = VGroup(Square(color=TEAL, side_length=0.6), Square(color=TEAL, side_length=0.6))   # reference group: two children
        ref.arrange(RIGHT, buff=0.2).shift(DOWN * 2.3)   # put it at the bottom
        self.add(ref)   # add it to the scene
        tag = VGroup(Square(color=YELLOW, side_length=0.3), Square(color=WHITE, side_length=0.3))   # two-part marker
        tag.arrange(RIGHT, buff=0.1)   # line them up in a row
        tag.next_to(ref, UP, buff=0.25, index_of_submobject_to_align=1)   # both self and the reference align by their 2nd child
        self.add(tag)   # add it to the scene
        win.play(FadeIn(ref), FadeIn(tag), run_time=0.5)   # fade in the reference group and the marker
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window


# ===== Sample 4: to_edge / to_corner ======================================
class EdgeCornerDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        frame = ScreenRectangle(height=6.8, color=GREY)   # a hint at the frame border
        self.add(frame)   # add it to the scene
        top = Square(color=RED, side_length=0.9)   # the square on the top edge
        bottom = Square(color=BLUE, side_length=0.9)   # the square on the bottom edge
        side = Square(color=GREEN, side_length=0.9)   # the square on the left edge
        corner = Square(color=YELLOW, side_length=0.9)   # the square at the top-right corner
        top.to_edge(UP, buff=0.3)   # snap to the top edge, margin 0.3
        bottom.to_edge(DOWN, buff=0.3)   # snap to the bottom edge
        side.shift(UP * 1.2)   # raise it a little first
        side.to_edge(LEFT, buff=0.3)   # snap to the left edge: the y coordinate is unaffected
        corner.to_corner(UR, buff=0.5)   # snap to the top-right corner, margin 0.5
        self.add(top, bottom, side, corner)   # add them all to the scene
        win.play(FadeIn(top), FadeIn(bottom), FadeIn(side), FadeIn(corner), run_time=0.6)   # fade in the four squares
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window


# ===== Sample 5: center / align_to ========================================
class CenterAlignDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.2, fill_opacity=0.6)   # blue square
        sq.shift(LEFT * 3.2 + UP * 1.4)   # move it to the upper left first
        self.add(sq)   # add it to the scene
        win.play(sq.animate.center(), run_time=0.6)   # center: back to the origin (0, 0, 0)
        big = Square(color=RED, side_length=2.0, fill_opacity=0.4)   # the big reference square
        big.shift(RIGHT * 3.2)   # put it on the right
        small = Square(color=YELLOW, side_length=1.0)   # the small square to align
        small.shift(RIGHT * 3.2 + UP * 1.8)   # place it a little higher first
        self.add(big, small)   # add them to the scene
        win.play(small.animate.align_to(big, UP), run_time=0.6)   # align_to: top edges flush, x unmoved
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window


SCENES = [
    ("shift", ShiftDemo),
    ("move_to", MoveToDemo),
    ("next_to", NextToDemo),
    ("edge_corner", EdgeCornerDemo),
    ("center_align", CenterAlignDemo),
]

PAIRS = [
    ("shift", ["shift"]),
    ("move_to", ["move_to"]),
    ("next_to", ["next_to"]),
    ("edge_corner", ["edge_corner"]),
    ("center_align", ["center_align"]),
]

PAGE = "02-Positioning"


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
