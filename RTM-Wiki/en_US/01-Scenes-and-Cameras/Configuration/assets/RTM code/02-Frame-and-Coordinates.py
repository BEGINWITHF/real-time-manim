# -*- coding: utf-8 -*-
"""Full source for the samples in 02-Frame-and-Coordinates.md (identical to the code blocks in the page).

Usage: python 02-Frame-and-Coordinates.py <clip names>...
With no arguments it renders every clip and concatenates the page's comparison videos.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
ASSETS = os.path.dirname(HERE)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    config,
    Scene, Square, Circle, Dot, Text, VGroup,
    WHITE, RED, GREEN, YELLOW,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, Create,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: default frame =============================================
class FrameLayoutDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        edge_x = 14.222222 / 2   # x of the picture's right edge: = "frame_width" / 2 = "frame_x_radius"
        edge_y = 8.0 / 2   # y of the picture's top edge: = "frame_height" / 2 = "frame_y_radius"
        label = Text("frame_width=14.222  frame_height=8.0", font_size=34,
                     color=WHITE).to_edge(UP, buff=0.3)   # label the frame size on screen
        corners = VGroup(*[
            Dot(color=RED, radius=0.1).move_to([sx * (edge_x - 0.25), sy * (edge_y - 0.25), 0])
            for sx in (-1, 1) for sy in (-1, 1)])   # a red dot at each corner: the frame's four corners
        sq = Square(side_length=1.6, color=YELLOW).set_stroke(width=4).shift(LEFT * 1.2)   # square: evidence the frame is undistorted
        circ = Circle(radius=0.8, color=GREEN).shift(RIGHT * 1.2)   # circle: same as above
        self.add(label)   # put the label into the scene
        win.play(FadeIn(corners), run_time=0.6)   # fade in the red dots at the four corners
        win.play(Create(sq), Create(circ), run_time=0.8)   # draw the square and the circle
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window


# ===== Sample 2: rewriting the frame (the two engines behave differently) ==
class FrameOverrideDemo(Scene):
    def __init__(self, **kwargs):
        self._saved = (config.frame_x_radius, config.frame_y_radius)   # remember the two default radii first
        config.frame_x_radius = 3.555   # rewrite "frame_x_radius": the picture width becomes 7.11
        config.frame_y_radius = 2.0     # rewrite "frame_y_radius": the picture height becomes 4.0
        super().__init__(**kwargs)   # the camera is constructed here, CE reads the changed frame

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        label = Text("frame_x_radius=3.555  frame_y_radius=2.0", font_size=34,
                     color=WHITE).to_edge(UP, buff=0.3)   # label the rewritten radii on screen
        corners = VGroup(*[
            Dot(color=RED, radius=0.1).move_to([sx * (3.555 - 0.25), sy * (2.0 - 0.25), 0])
            for sx in (-1, 1) for sy in (-1, 1)])   # the corner red dots placed for the rewritten frame
        sq = Square(side_length=1.6, color=YELLOW).set_stroke(width=4).shift(LEFT * 1.2)   # square: same as the previous sample
        circ = Circle(radius=0.8, color=GREEN).shift(RIGHT * 1.2)   # circle: same as the previous sample
        self.add(label)   # put the label into the scene
        win.play(FadeIn(corners), run_time=0.6)   # fade in the red dots at the four corners
        win.play(Create(sq), Create(circ), run_time=0.8)   # draw the square and the circle
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window
        config.frame_x_radius, config.frame_y_radius = self._saved   # restore the defaults so later samples are unaffected


# ===== Sample 3: edge midpoints ============================================
class EdgePointsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        edge_x = 14.222222 / 2   # x of the picture's right edge: the x coordinate of "right_side"
        edge_y = 8.0 / 2   # y of the picture's top edge: the y coordinate of "top"
        pts = VGroup(
            Dot(color=RED, radius=0.12).move_to([0, edge_y - 0.3, 0]),   # top: the midpoint of the top edge
            Dot(color=RED, radius=0.12).move_to([edge_x - 0.3, 0, 0]),   # right_side: the midpoint of the right edge
            Dot(color=RED, radius=0.12).move_to([0, -edge_y + 0.3, 0]),   # bottom: the midpoint of the bottom edge
            Dot(color=RED, radius=0.12).move_to([-edge_x + 0.3, 0, 0]),   # left_side: the midpoint of the left edge
        )
        names = VGroup(
            Text("top", font_size=28, color=YELLOW).next_to(pts[0], DOWN, buff=0.15),
            Text("right_side", font_size=28, color=YELLOW).next_to(pts[1], LEFT, buff=0.25),
            Text("bottom", font_size=28, color=YELLOW).next_to(pts[2], UP, buff=0.15),
            Text("left_side", font_size=28, color=YELLOW).next_to(pts[3], RIGHT, buff=0.25),
        )
        walker = Dot(color=WHITE, radius=0.18).move_to(pts[3])   # cursor: starts from "left_side"
        self.add(pts, names, walker)   # put the four edge points, the four name rows and the cursor into the scene
        win.play(FadeIn(pts), FadeIn(names), run_time=0.6)   # fade in the four edge points and names
        win.play(walker.animate.move_to(pts[0]), run_time=0.5)   # the cursor walks to "top"
        win.play(walker.animate.move_to(pts[1]), run_time=0.5)   # the cursor walks to "right_side"
        win.play(walker.animate.move_to(pts[2]), run_time=0.5)   # the cursor walks to "bottom"
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window


SCENES = [
    ("frame_layout", FrameLayoutDemo),
    ("frame_override", FrameOverrideDemo),
    ("edge_points", EdgePointsDemo),
]

OUTPUTS = [
    ("02-Frame-and-Coordinates-frame_layout", ["frame_layout"]),
    ("02-Frame-and-Coordinates-frame_override", ["frame_override"]),
    ("02-Frame-and-Coordinates-edge_points", ["edge_points"]),
]


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
        for out_name, names in OUTPUTS:
            dst = os.path.join(ASSETS, "RTM output", out_name + ".mp4")
            concat(names, dst)
            print("concat ->", dst, os.path.getsize(dst), "bytes")
