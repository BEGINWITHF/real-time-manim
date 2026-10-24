# -*- coding: utf-8 -*-
"""Full source for the eight samples in 02b-Positioning-Advanced.md (identical to the code blocks in the page).

Usage: python 02b-Positioning-Advanced.py <clip names>...
With no arguments it renders every clip and concatenates the page's eight sample videos (written to the parent assets/).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

from real_time_manim import (
    Scene, Square, Rectangle, Text, Line, Dot, VGroup,
    RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, TEAL,
    UP, DOWN, LEFT, RIGHT, UL, DR, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: align_on_border ==========================================
class BorderDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        a = Square(color=RED, side_length=0.9)   # the square on the top edge
        b = Square(color=BLUE, side_length=0.9)   # the square at the bottom-right corner
        a.align_on_border(UP, buff=0.4)   # the critical point snaps to the upper border, margin 0.4
        b.align_on_border(DR, buff=0.4)   # the critical point snaps to the bottom-right corner
        self.add(a, b)   # add them to the scene
        win.play(FadeIn(a), FadeIn(b), run_time=0.6)   # fade in both squares
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window


# ===== Sample 2: set_coord / set_x / set_y / set_z ========================
class CoordsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.2, fill_opacity=0.6)   # blue square
        self.add(sq)   # add it to the scene
        win.play(sq.animate.set_x(-3.0), run_time=0.5)   # set_x: x set to -3, y unmoved
        win.play(sq.animate.set_y(1.5), run_time=0.5)   # set_y: y set to 1.5, x unmoved
        win.play(sq.animate.set_coord(2.5, 0), run_time=0.5)   # set_coord: dim=0, i.e. x set to 2.5
        sq.set_x(0.0, direction=LEFT)   # direction=LEFT: set the left edge's x to 0 (the center stops at 0.6)
        sq.set_z(0.5)   # set_z: change the z coordinate, invisible in a 2D frame
        print("get_z =", sq.get_z())   # verify z really became 0.5
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window


# ===== Sample 3: arrange ==================================================
class ArrangeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        row = VGroup(*[Square(color=c, side_length=0.8) for c in (RED, BLUE, GREEN)])   # three squares
        row.arrange(RIGHT, buff=0.35)   # default center=True: center the whole thing
        self.add(row)   # add it to the scene
        win.play(FadeIn(row), run_time=0.5)   # fade in the row
        win.play(row.animate.arrange(DOWN, buff=0.6), run_time=0.6)   # change to a column, spacing 0.6
        win.play(row.animate.arrange(RIGHT, buff=1.0, center=False), run_time=0.6)   # center=False: don't recenter
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window


# ===== Sample 4: arrange_in_grid ==========================================
class GridDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        colors = (RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE)   # six colors = the fill order
        cells = VGroup(*[Square(color=c, side_length=0.7) for c in colors])   # six squares
        cells.arrange_in_grid(rows=2, cols=3, buff=(0.4, 0.8))   # 2 rows 3 cols, row spacing 0.4, column spacing 0.8
        self.add(cells)   # add them to the scene
        win.play(FadeIn(cells), run_time=0.6)   # fade in the grid: red, orange, yellow in the first row
        win.play(cells.animate.arrange_in_grid(rows=3, cols=2, flow_order="dr"), run_time=0.7)   # 3 rows 2 cols, fill by column
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window


# ===== Sample 5: surround / replace =======================================
class SurroundReplaceDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        txt = Text("target", font_size=36, color=YELLOW)   # the text being enclosed
        self.add(txt)   # add it to the scene
        frame = Rectangle(color=RED)   # an empty rectangle
        frame.surround(txt, buff=0.25)   # surround: enclose the text by width, margin 0.25
        self.add(frame)   # add it to the scene
        win.play(FadeIn(frame), run_time=0.5)   # fade in the frame
        panel = Rectangle(width=1.0, height=1.0, color=BLUE, fill_opacity=0.4)   # a small square
        panel.replace(txt, stretch=True)   # replace: same center, width and height stretched independently to match the text
        self.add(panel)   # add it to the scene
        win.play(FadeIn(panel), run_time=0.5)   # fade in the backing
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window


# ===== Sample 6: put_start_and_end_on =====================================
class PutEndsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        line = Line(LEFT * 2, RIGHT * 2, color=BLUE)   # initially: a horizontal line of length 4
        p1 = Dot(color=RED, radius=0.1).move_to(LEFT * 3 + DOWN * 1.5)   # target start
        p2 = Dot(color=RED, radius=0.1).move_to(RIGHT * 1 + UP * 2)   # target end
        self.add(line, p1, p2)   # add them to the scene
        win.play(line.animate.put_start_and_end_on(p1.get_center(), p2.get_center()), run_time=0.7)   # scale + rotate + translate to pin both ends to the two points
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window


# ===== Sample 7: shift_onto_screen / is_off_screen ========================
class OffScreenDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        sq = Square(color=RED, side_length=1.2)   # red square
        sq.shift(LEFT * 12)   # move it far off-frame
        print("is_off_screen =", sq.is_off_screen())   # True: fully off-frame
        self.add(sq)   # add it to the scene
        win.play(sq.animate.shift_onto_screen(buff=0.5), run_time=0.7)   # pull it back on screen, margin 0.5
        print("is_off_screen after pulling back =", sq.is_off_screen())   # False
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window


# ===== Sample 8: space_out_submobjects ====================================
class SpaceOutDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        g = VGroup(*[Square(color=BLUE, side_length=0.7) for _ in range(3)])   # three squares
        g.arrange(RIGHT, buff=0.05)   # almost touching
        self.add(g)   # add it to the scene
        win.play(g.animate.space_out_submobjects(1.8), run_time=0.6)   # factor>1: only the spacing spreads, the squares don't grow
        win.play(g.animate.space_out_submobjects(0.5), run_time=0.6)   # factor<1: tighten
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window


SCENES = [
    ("border", BorderDemo),
    ("coords", CoordsDemo),
    ("arrange", ArrangeDemo),
    ("grid", GridDemo),
    ("surround_replace", SurroundReplaceDemo),
    ("put_ends", PutEndsDemo),
    ("off_screen", OffScreenDemo),
    ("space_out", SpaceOutDemo),
]

PAIRS = [
    ("border", ["border"]),
    ("coords", ["coords"]),
    ("arrange", ["arrange"]),
    ("grid", ["grid"]),
    ("surround_replace", ["surround_replace"]),
    ("put_ends", ["put_ends"]),
    ("off_screen", ["off_screen"]),
    ("space_out", ["space_out"]),
]

PAGE = "02b-Positioning-Advanced"


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
