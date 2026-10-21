# -*- coding: utf-8 -*-
"""Full source for the five samples in 03-Measurement.md (identical to the code blocks in the page).

Usage: python 03-Measurement.py <clip names>...
With no arguments it renders every clip and concatenates the page's five sample videos (written to the parent assets/).
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
    Scene, VGroup, Square, Rectangle, Circle, Dot,
    BLUE, GREEN, YELLOW, RED, UR, DOWN, LEFT, RIGHT, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: width / height / depth ===================================
class SizeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        rect = Rectangle(width=4.0, height=2.0, color=BLUE, fill_opacity=0.4)   # a 4×2 rectangle
        self.add(rect)   # add it to the scene
        print("initial: width =", rect.width, "height =", rect.height, "depth =", rect.depth)   # 4.0 2.0 0.0
        win.play(rect.animate.set(width=2.0), run_time=0.6)   # assigning "width" = a uniform scale
        print("after width=2.0: width =", rect.width, "height =", rect.height)   # 2.0 1.0: the height scales uniformly too
        win.play(rect.animate.set(height=3.0), run_time=0.6)   # assigning "height": uniform scale up
        print("after height=3.0: width =", rect.width, "height =", rect.height)   # 6.0 3.0
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window


# ===== Sample 2: get_center / get_top / get_bottom / get_left / get_right ==
class EdgesDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=2.4, fill_opacity=0.4)   # a 2.4-by-2.4 square
        self.add(sq)   # add it to the scene
        marks = VGroup()   # critical-point markers
        for name, p in (
            ("center", sq.get_center()),
            ("top", sq.get_top()),
            ("bottom", sq.get_bottom()),
            ("left", sq.get_left()),
            ("right", sq.get_right()),
        ):   # the center and the four edge midpoints
            marks.add(Dot(color=RED, radius=0.08).move_to(p))   # drop a red dot on the critical point
            print(name, "=", p.round(2))   # print the coordinate to verify
        self.add(marks)   # add the markers to the scene
        win.play(FadeIn(marks), run_time=0.5)   # fade in the five red dots
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window


# ===== Sample 3: get_x / get_y / get_z / get_coord / get_corner ===========
class CoordsGetDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        sq = Square(color=GREEN, side_length=2.0).shift(RIGHT * 1.5)   # a square moved right by 1.5
        self.add(sq)   # add it to the scene
        print("get_x =", sq.get_x(), "| get_x(LEFT) =", sq.get_x(direction=LEFT))   # 1.5 0.5
        print("get_y =", sq.get_y(), "| get_z =", sq.get_z())   # 0.0 0.0
        print("get_coord(0, UR) =", sq.get_coord(0, UR))   # the x of the UR corner
        marks = VGroup()   # critical-point markers
        for name, p in (
            ("corner(UR)", sq.get_corner(UR)),
            ("edge_center(DOWN)", sq.get_edge_center(DOWN)),
            ("critical_point(LEFT)", sq.get_critical_point(LEFT)),
        ):   # corner / edge midpoint / general critical point
            marks.add(Dot(color=RED, radius=0.08).move_to(p))   # drop a red dot on the critical point
            print(name, "=", p.round(2))   # print the coordinate to verify
        self.add(marks)   # add the markers to the scene
        win.play(FadeIn(marks), run_time=0.5)   # fade in the red dots
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window


# ===== Sample 4: length_over_dim / get_all_points =========================
class MeasurePointsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        circ = Circle(radius=1.2, color=YELLOW)   # a circle of radius 1.2
        self.add(circ)   # add it to the scene
        print("length_over_dim(0/1/2) =", [float(circ.length_over_dim(i)) for i in range(3)])   # 2.4 2.4 0.0
        pts = circ.get_all_points()   # all vertices of self and every descendant
        print("get_all_points =", pts.shape)   # (32, 3)
        cloud = VGroup(*[Dot(color=RED, radius=0.03).move_to(p) for p in pts])   # a small red dot on each vertex
        self.add(cloud)   # add the point cloud to the scene
        win.play(FadeIn(cloud), run_time=0.6)   # fade in the point cloud: the Bézier control points
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window


# ===== Sample 5: center of mass, boundary points and low-level stats ======
class StatsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        c = Circle(radius=1.4, color=BLUE)   # a circle of radius 1.4
        self.add(c)   # add it to the scene
        marks = VGroup()   # critical-point markers
        for name, p in (
            ("center_of_mass", c.get_center_of_mass()),
            ("midpoint", c.get_midpoint()),
            ("boundary_point(UR)", c.get_boundary_point(UR)),
            ("zenith", c.get_zenith()),
            ("z_index_ref", c.get_z_index_reference_point()),
        ):   # center of mass and the boundary-point family (the zenith of a flat object falls on the center)
            marks.add(Dot(color=RED, radius=0.07).move_to(p))   # drop a red dot on the critical point
            print(name, "=", p.round(2))   # print the coordinate to verify
        self.add(marks)   # add the markers to the scene
        print("get_extremum_along_dim(key=1/-1) =", c.get_extremum_along_dim(dim=0, key=1), c.get_extremum_along_dim(dim=0, key=-1))   # rightmost / leftmost x
        print("reduce_across_dimension(max, 0) =", c.reduce_across_dimension(max, 0))   # reduce max over x
        print("get_merged_array('points') =", c.get_merged_array("points").shape)   # concatenation of the family's vertices
        print("get_points_defining_boundary =", c.get_points_defining_boundary().shape)   # contour sample points
        win.play(FadeIn(marks), run_time=0.5)   # fade in the red dots
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window


SCENES = [
    ("size", SizeDemo),
    ("edges", EdgesDemo),
    ("coords", CoordsGetDemo),
    ("points", MeasurePointsDemo),
    ("stats", StatsDemo),
]

PAIRS = [
    ("size", ["size"]),
    ("edges", ["edges"]),
    ("coords", ["coords"]),
    ("points", ["points"]),
    ("stats", ["stats"]),
]

PAGE = "03-Measurement"


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
