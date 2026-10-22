# -*- coding: utf-8 -*-
"""Full source of the three samples in 04-Vector-and-Geometry-Utilities.md (identical to the code blocks in the page).
Usage: python 04-Vector-and-Geometry-Utilities.py <clip name>...
With no arguments it renders every clip and concatenates the page's three sample videos (output to the parent assets/).
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

import numpy as np
from real_time_manim import (
    Scene, Text, VGroup, Dot, Vector, Line, Arc, Polygon, Circle,
    BLUE, GREEN, RED, YELLOW, GREY_B, WHITE, PURPLE, GOLD, TEAL,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI, TAU,
    rotate_vector, angle_between_vectors, angle_of_vector,
    center_of_mass, midpoint, regular_vertices, shoelace, shoelace_direction,
    FadeIn, Write, Create,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: rotate_vector, rotating a vector about an axis =============
class RotateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("04-rotate_vector", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        o = Dot(ORIGIN, radius=0.06, color=WHITE)   #coordinate origin
        v0 = Vector(2.4 * RIGHT, color=GREY_B)   #base vector: RIGHT itself
        l0 = Text("RIGHT", font_size=18, color=GREY_B).next_to(v0.get_end(), DOWN, buff=0.2)
        win.play(FadeIn(o), Create(v0), FadeIn(l0), run_time=0.7)   #draw the base arrow first

        v45 = Vector(2.4 * rotate_vector(RIGHT, PI / 4), color=YELLOW)   #rotate 45° CCW about the default axis OUT
        a45 = Arc(radius=1.2, start_angle=0, angle=PI / 4, arc_center=ORIGIN,
                  color=YELLOW, stroke_width=5)   #arc from 0 → 45°
        l45 = Text("rotate(PI/4)", font_size=17, color=YELLOW).move_to([1.3, 1.9, 0])   #45° label (placed outside the arc)
        win.play(Create(a45), Create(v45), FadeIn(l45), run_time=0.7)   #the result of rotating 45°

        v90 = Vector(2.4 * rotate_vector(RIGHT, PI / 2), color=GREEN)   #rotate 90°: RIGHT becomes exactly UP
        a90 = Arc(radius=1.7, start_angle=0, angle=PI / 2, arc_center=ORIGIN,
                  color=GREEN, stroke_width=4)   #arc from 0 → 90° (a bigger sweep)
        l90 = Text("rotate(PI/2)", font_size=17, color=GREEN).move_to([2.1, 0.8, 0])   #90° label
        win.play(Create(a90), Create(v90), FadeIn(l90), run_time=0.7)   #the result of rotating 90°
        note = Text("rotate_vector(v, angle, axis=OUT) returns a new vector",
                    font_size=18, color=YELLOW).to_edge(DOWN)   #bottom note: the original vector is unchanged
        win.play(FadeIn(note), run_time=0.35)   #note fades in
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window


# ===== Sample 2: angle and centroid ========================================
class AngleCentroidDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("04-angle_centroid", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        a = Vector([2.6, 0.9, 0], color=RED)   #vector 1
        b = Vector([1.1, 2.4, 0], color=BLUE)   #vector 2
        la = Text("v1", font_size=18, color=RED).next_to(a.get_end(), RIGHT, buff=0.15)
        lb = Text("v2", font_size=18, color=BLUE).next_to(b.get_end(), UP, buff=0.15)
        ang = angle_between_vectors(a.get_end(), b.get_end())   #angle between the two vectors, always in [0, PI]
        aa, ab = angle_of_vector(a.get_end()), angle_of_vector(b.get_end())   #their polar angles, used to place the arc
        arc = Arc(radius=1.15, start_angle=aa, angle=ab - aa, arc_center=ORIGIN,
                  color=YELLOW, stroke_width=6)   #arc between the two arrows
        lt = Text("%.3f rad" % ang, font_size=17, color=YELLOW).move_to([1.05, 0.45, 0])   #angle value
        win.play(Create(a), FadeIn(la), run_time=0.5)   #draw v1 first
        win.play(Create(b), FadeIn(lb), run_time=0.5)   #then draw v2
        win.play(Create(arc), FadeIn(lt), run_time=0.5)   #measure the angle

        pts = [np.array([-3.1, -1.0, 0]), np.array([-1.2, -2.0, 0]),   #four lower-left points (an irregular quadrilateral)
               np.array([-0.7, 0.5, 0]), np.array([-2.9, 1.3, 0])]
        quad = Polygon(*pts, color=GREY_B, stroke_width=3)   #join the points in order into a quadrilateral
        pdots = VGroup(*[Dot(p, radius=0.09, color=RED) for p in pts])   #four vertices
        com = center_of_mass(pts)   #centroid = arithmetic mean of the points
        star = Dot(com, radius=0.12, color=GOLD)   #centroid dot
        lc = Text("center_of_mass", font_size=16, color=GOLD).next_to(star, DOWN, buff=0.18)
        mid = midpoint(pts[0], pts[1])   #midpoint of the bottom edge
        mdot = Dot(mid, radius=0.09, color=GREEN)
        lm = Text("midpoint", font_size=15, color=GREEN).next_to(mdot, DOWN, buff=0.15)
        win.play(Create(quad), FadeIn(pdots), run_time=0.7)   #the irregular quadrilateral
        win.play(FadeIn(star), FadeIn(lc), run_time=0.4)   #centroid marker
        win.play(FadeIn(mdot), FadeIn(lm), run_time=0.4)   #midpoint marker
        note = Text("angle_between_vectors -> [0, PI]", font_size=18, color=YELLOW).to_edge(DOWN)
        win.play(FadeIn(note), run_time=0.35)   #bottom note fades in
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window


# ===== Sample 3: shoelace area and regular_vertices regular-polygon vertices =
class PolygonDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("04-shoelace_regular_vertices", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        verts, sa = regular_vertices(5, radius=1.4, start_angle=PI / 2)   #vertices of a radius-1.4 regular pentagon + start angle
        poly = Polygon(*verts, color=PURPLE, fill_opacity=0.3, stroke_width=5).shift([-2.3, -0.4, 0])   #left half: regular pentagon
        vdots = VGroup(*[Dot(v + np.array([-2.3, -0.4, 0]), radius=0.08, color=GOLD)
                         for v in verts])   #dots on the five vertices
        lv = Text("regular_vertices(n=5, radius=1.4)", font_size=15, color=GREY_B)
        lv.move_to([-2.3, 2.4, 0])   #left figure title
        area = shoelace(np.array(list(verts) + [verts[0]]))   #shoelace formula: signed area (feed np.array, append the first point to close)
        dire = shoelace_direction(np.array(verts))   #winding direction: "CW" or "CCW"
        la = Text("shoelace = %.3f" % area, font_size=16, color=PURPLE).move_to([-2.3, -2.75, 0])   #area value
        ld = Text("shoelace_direction = " + dire, font_size=16, color=YELLOW).move_to([-2.3, -3.2, 0])   #direction
        win.play(FadeIn(lv), Create(poly), FadeIn(vdots), run_time=0.9)   #the whole pentagon appears
        win.play(FadeIn(la), FadeIn(ld), run_time=0.5)   #the area and direction lines

        sq = [np.array([1.0, -1.0, 0]), np.array([1.0, 1.0, 0]),   #right half: a clockwise-ordered square
              np.array([3.0, 1.0, 0]), np.array([3.0, -1.0, 0])]   #(lower-left → upper-left → upper-right → lower-right)
        sqp = Polygon(*sq, color=TEAL, fill_opacity=0.3, stroke_width=5)
        sqdots = VGroup(*[Dot(p, radius=0.08, color=GREEN) for p in sq])
        ls = Text("clockwise order (4 pts)", font_size=15, color=GREY_B).move_to([2.0, 2.4, 0])   #right figure title
        sarea = shoelace(np.array(sq + [sq[0]]))   #clockwise order + closed first point → signed area is positive
        sdir = shoelace_direction(np.array(sq))
        lsa = Text("shoelace = %.1f" % sarea, font_size=16, color=TEAL).move_to([2.0, -1.6, 0])
        lsd = Text("shoelace_direction = " + sdir, font_size=16, color=YELLOW).move_to([2.0, -2.05, 0])
        win.play(Create(sqp), FadeIn(sqdots), FadeIn(ls), run_time=0.7)   #the clockwise square
        win.play(FadeIn(lsa), FadeIn(lsd), run_time=0.5)   #its area and direction
        note = Text("shoelace(np.array) + close the loop", font_size=18, color=YELLOW).to_edge(DOWN)   #bottom note: must be closed, must be np.array
        win.play(FadeIn(note), run_time=0.35)   #bottom note: must be closed, must be np.array
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window


SCENES = [
    ("rotate", RotateDemo),
    ("angle_centroid", AngleCentroidDemo),
    ("polygon", PolygonDemo),
]

PAIRS = [
    ("rotate", ["rotate"]),
    ("angle_centroid", ["angle_centroid"]),
    ("polygon", ["polygon"]),
]

PAGE = "04-Vector-and-Geometry-Utilities"


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
