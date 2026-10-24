# -*- coding: utf-8 -*-
"""Full source of the six samples in 04b-Scaling-Rotation-and-Stretching-Advanced.md (identical to the code blocks in the page).

Usage: python 04b-Scaling-Rotation-and-Stretching-Advanced.py <clip name>...
With no arguments it renders every clip and concatenates the page's six sample videos (output to the parent assets/).
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
    Scene, Square, Rectangle, Circle, Triangle, Line, Dot, Arc, VGroup,
    BLUE, RED, GREEN, YELLOW, GREY, TEAL,
    UP, DOWN, LEFT, RIGHT, ORIGIN, TAU, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: rescale_to_fit ===========================================
class RescaleDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.0, fill_opacity=0.5)   #a 1×1 square
        self.add(sq)   #add to the scene
        win.play(sq.animate.rescale_to_fit(4.0, 0), run_time=0.6)   #set width to 4.0: stretch=False, proportional
        print("after proportional: width =", round(sq.width, 2), "height =", round(sq.height, 2))   #4.0 4.0
        win.play(sq.animate.rescale_to_fit(1.0, 1, stretch=True), run_time=0.6)   #force height to 1.0: squash only this dimension
        print("after stretch: width =", round(sq.width, 2), "height =", round(sq.height, 2))   #4.0 1.0
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


# ===== Sample 2: scale_to_fit_* / stretch_to_fit_* ========================
class FitDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        a = Rectangle(width=1.0, height=1.0, color=BLUE, fill_opacity=0.4)   #left: the pair that keeps the aspect ratio
        a.shift(LEFT * 4.0 + UP * 1.4)
        b = Rectangle(width=1.0, height=1.0, color=RED, fill_opacity=0.4)   #right: the pair that distorts
        b.shift(RIGHT * 4.0 + UP * 1.4)
        self.add(a, b)   #add to the scene
        win.play(a.animate.scale_to_fit_width(3.0), run_time=0.6)   #proportional: width 3 makes the height 3 too
        a.scale_to_fit_height(1.0)   #proportional: set height to 1, width comes back to 1 as well
        print("after scale_to_fit:", round(a.width, 2), round(a.height, 2))   #1.0 1.0
        win.play(b.animate.stretch_to_fit_width(3.0), run_time=0.6)   #stretch the width only, height unchanged
        b.stretch_to_fit_height(1.0)   #squash the height only
        print("after stretch_to_fit:", round(b.width, 2), round(b.height, 2))   #3.0 1.0
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


# ===== Sample 3: pose_at_angle ============================================
class PoseDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        tri = Triangle(color=YELLOW, fill_opacity=0.4).scale(1.2)   #the triangle being posed
        flat = Triangle(color=GREY, fill_opacity=0.3).shift(RIGHT * 3.2)   #the unposed reference
        self.add(tri, flat)   #add to the scene
        print("before pose: width =", round(tri.width, 2))   #width before posing
        win.play(tri.animate.pose_at_angle(), run_time=0.7)   #equivalent to rotate(TAU/14, RIGHT + UP)
        print("after pose: width =", round(tri.width, 2), "height =", round(tri.height, 2))   #smaller after the oblique projection
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


# ===== Sample 4: apply_function / apply_matrix / apply_complex_function ===
class ApplyDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        c1 = Circle(radius=0.8, color=BLUE, fill_opacity=0.4)   #first circle: deform at the origin first
        self.add(c1)   #add to the scene
        win.play(c1.animate.apply_function(
            lambda p: np.array([p[0], p[1] + 0.55 * p[0], p[2]])), run_time=0.6)   #per-point mapping: y rises with x = a shear
        win.play(c1.animate.move_to(LEFT * 4.2 + UP * 1.4), run_time=0.4)   #after deforming, move it to the upper left
        c2 = Circle(radius=0.8, color=RED, fill_opacity=0.4)   #second circle: also at the origin first
        self.add(c2)   #add to the scene
        win.play(c2.animate.apply_matrix(
            np.array([[1.0, 0.45, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])), run_time=0.6)   #linear transform: shear
        win.play(c2.animate.move_to(UP * 1.4), run_time=0.4)   #after deforming, move it to the top centre
        c3 = Circle(radius=0.8, color=GREEN, fill_opacity=0.4)   #third circle: also at the origin first
        self.add(c3)   #add to the scene
        win.play(c3.animate.apply_complex_function(
            lambda z: np.exp(z) * 0.5), run_time=0.6)   #complex mapping: the circle becomes a bean shape
        win.play(c3.animate.move_to(RIGHT * 4.2 + UP * 1.4), run_time=0.4)   #after deforming, move it to the upper right
        d1 = Dot(color=YELLOW, radius=0.13).shift(LEFT * 3.0 + DOWN * 1.6)   #a dot whose centre alone moves
        self.add(d1)   #add to the scene
        win.play(d1.animate.apply_function_to_position(lambda p: p + RIGHT * 1.6), run_time=0.5)   #move only its own centre
        pair = VGroup(Dot(color=TEAL, radius=0.13), Dot(color=TEAL, radius=0.13))   #two submobjects
        pair.arrange(RIGHT, buff=0.4).shift(RIGHT * 1.2 + DOWN * 1.6)
        self.add(pair)   #add to the scene
        win.play(pair.animate.apply_function_to_submobject_positions(lambda p: p + UP * 0.8), run_time=0.5)   #shift each submobject's centre by its own amount
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


# ===== Sample 5: apply_points_function_about_point ========================
class PointsFuncDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        ln = Line(LEFT * 1.5, RIGHT * 1.5, color=BLUE)   #a horizontal segment
        ln.shift(UP * 1.5)
        self.add(ln)   #add to the scene
        win.play(ln.animate.apply_points_function_about_point(
            lambda pts: pts * 1.6, about_point=ln.get_center()), run_time=0.6)   #process points in bulk: scale 1.6 about the centre
        win.play(ln.animate.apply_points_function_about_point(
            lambda pts: pts + np.array([0.0, -1.4, 0.0]), about_point=ORIGIN), run_time=0.6)   #bulk translate: shift the whole thing down
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


# ===== Sample 6: repeat / reverse_points ==================================
class RepeatRevDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        arc = Arc(radius=1.5, start_angle=0, angle=TAU * 0.7, color=YELLOW)   #an open arc: start and end clearly distinct
        mark = Dot(color=RED, radius=0.09).move_to(arc.point_from_proportion(0.25))   #a marker at 25% of the path
        self.add(arc, mark)   #add to the scene
        arc.reverse_points()   #reverse the path direction: start and end swap (the arc's appearance is unchanged)
        win.play(mark.animate.move_to(arc.point_from_proportion(0.25)), run_time=0.5)   #the 25% point jumps to the other end with the direction
        print("points before repeat =", len(arc.points))   #the point count after the reversal
        arc.repeat(2)   #repeat the vertex sequence twice: the appearance is unchanged
        print("points after repeat =", len(arc.points))   #doubled
        win.play(Wait(0.5))   #wait 0.5s
        win.close()   #close the RTM window


SCENES = [
    ("rescale", RescaleDemo),
    ("fit", FitDemo),
    ("pose", PoseDemo),
    ("apply", ApplyDemo),
    ("points_func", PointsFuncDemo),
    ("repeat_rev", RepeatRevDemo),
]

PAIRS = [
    ("rescale", ["rescale"]),
    ("fit", ["fit"]),
    ("pose", ["pose"]),
    ("apply", ["apply"]),
    ("points_func", ["points_func"]),
    ("repeat_rev", ["repeat_rev"]),
]

PAGE = "04b-Scaling-Rotation-and-Stretching-Advanced"


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
