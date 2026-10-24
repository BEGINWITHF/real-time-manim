# -*- coding: utf-8 -*-
"""Full source of the three samples in 07-Polar-and-3D-Coordinates.md (identical to the code blocks in the page).

Usage: python 07-Polar-and-3D-Coordinates.py <scene name>...
With no arguments it renders every scene and concatenates the page's three videos.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
ASSETS = os.path.dirname(HERE)
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

from real_time_manim import (
    Scene, ThreeDScene, ThreeDAxes, PolarPlane, Dot, Text, np,
    YELLOW, TEAL, BLUE, ORANGE, RED, GREEN, GREY_B, UP, DOWN, UR, TAU,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: PolarPlane polar plane ===================================
class PolarDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("07-PolarPlane", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        plane = PolarPlane(size=5,   #parameter "size": plane diameter
                           azimuth_units="PI radians",   #parameter "azimuth_units": label azimuth angles in π fractions
                           background_line_style={"stroke_color": TEAL, "stroke_width": 2},   #style of the concentric circles and radial lines
                           ).add_coordinates()   #"add_coordinates": radius numbers + angle labels
        rose = plane.plot_polar_graph(lambda th: 2 * np.sin(th * 5),   #"plot_polar_graph": draw a polar curve for r=f(θ)
                                      theta_range=[0, TAU], color=ORANGE)   #five-petal rose
        lab = Text("plot_polar_graph(2*sin(5*theta))",
                   font_size=18, color=GREY_B).to_edge(DOWN, buff=0.3)   #parameter caption label
        win.play(Create(plane), FadeIn(lab), run_time=1.0)   #the polar plane (with labels) and the caption appear together
        win.play(Create(rose), run_time=1.2)   #draw the rose curve
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window


# ===== Sample 2: ThreeDAxes 3D coordinate system ==========================
class ThreeDAxesDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        self.play = win.play   #move_camera calls self.play internally, so wire it up first
        title = Text("07-ThreeDAxes", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        ax = ThreeDAxes(x_range=(-3, 3, 1), y_range=(-3, 3, 1), z_range=(-4, 4, 1),   #data range of the three axes
                        x_length=7, y_length=7, z_length=5)   #on-screen length of each axis
        ax.add_coordinates(range(-2, 3), None, range(-4, 5, 2))   #"add_coordinates": given ticks for x/z, default for y
        d1 = Dot(ax.c2p(1, 1, 2), color=RED)   #"c2p": 3D data coordinates -> scene point
        d2 = Dot(ax.c2p(-2, 2, -3), color=GREEN)
        lab = Text("ThreeDAxes + c2p(1,1,2) / c2p(-2,2,-3)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   #method caption label
        win.play(Create(ax), FadeIn(lab), run_time=0.8)   #the 3D axes and the caption appear together
        win.play(FadeIn(d1), FadeIn(d2), run_time=0.4)   #the two space points fade in
        self.move_camera(theta=-0.6, phi=1.1, run_time=1.0)   #"move_camera": rotate to a 3D view to show depth
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window


# ===== Sample 3: Axes.plot_surface parametric surface =====================
class SurfaceDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        self.play = win.play   #move_camera calls self.play internally, so wire it up first
        title = Text("07-plot_surface", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        ax = ThreeDAxes(x_range=(-3, 3, 1), y_range=(-3, 3, 1), z_range=(-2, 2, 1))   #data range of the three axes
        surf = ax.plot_surface(lambda u, v: np.sin(u) * np.cos(v),   #"plot_surface": parametric surface
                               u_range=(-3, 3), v_range=(-3, 3), resolution=(12, 12))   #u/v ranges and grid resolution
        lab = Text("plot_surface(sin(u)*cos(v))",
                   font_size=24, color=GREY_B).to_edge(DOWN)   #method caption label
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   #the axes and the caption appear together
        win.play(FadeIn(surf), run_time=0.6)   #the surface fades in
        self.move_camera(theta=-0.6, phi=1.1, run_time=1.0)   #rotate to a 3D view to show the surface's undulation
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window


SCENES = [
    ("07-Polar-and-3D-Coordinates-polar", PolarDemo),
    ("07-Polar-and-3D-Coordinates-threed", ThreeDAxesDemo),
    ("07-Polar-and-3D-Coordinates-surface", SurfaceDemo),
]

PAIRS = [
    ("07-Polar-and-3D-Coordinates-polar", ["07-Polar-and-3D-Coordinates-polar"]),
    ("07-Polar-and-3D-Coordinates-threed", ["07-Polar-and-3D-Coordinates-threed"]),
    ("07-Polar-and-3D-Coordinates-surface", ["07-Polar-and-3D-Coordinates-surface"]),
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
        for out_name, names in PAIRS:
            dst = os.path.join(ASSETS, "RTM output", out_name + ".mp4")
            concat(names, dst)
            print("concat ->", dst, os.path.getsize(dst), "bytes")
