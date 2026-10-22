# -*- coding: utf-8 -*-
"""Full source for the four samples in 01b-Basic-3D-Objects-Advanced.md (identical to the code blocks in the page).

Usage: python 01b-Basic-3D-Objects-Advanced.py <clip names>...
With no arguments it renders every clip and concatenates the page's four sample videos (written to the parent assets/);
python 01b-Basic-3D-Objects-Advanced.py --concat-only concatenates without rendering.
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
    ThreeDScene, Line3D, Arrow3D, Cone, Cylinder, Text,
    GREEN, GREY_B, RED, YELLOW, PI,
    UP, DOWN, LEFT, RIGHT, UR, DEGREES,
    Create,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: Line3D's thickness and parallel/perpendicular classmethods
class Line3DDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first (this sample's Create goes through win.play and needs no wiring)
        title = Text("01b-line3d", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        line = Line3D(start=[-2, -1, 0], end=[2, 1, 1.5], thickness=0.06, color=YELLOW)   # thicker yellow main segment
        para = Line3D.parallel_to(line, point=[-1, -2.5, 0], length=4)   # a segment through the given point, parallel to the main segment
        perp = Line3D.perpendicular_to(line, point=[2, -2, 0.75], length=3)   # a segment through the given point, perpendicular to the main segment
        self.add(para, perp)   # first add the two reference segments to the scene
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)   # set an oblique view
        win.play(Create(line), run_time=0.8)   # draw the main segment piece by piece
        win.play(Wait(0.5))   # pause 0.5s to see the parallel/perpendicular relation
        self.move_camera(theta=-135 * DEGREES, run_time=1.2)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window


# ===== Sample 2: Arrow3D's arrow sizes and get_end =========================
class Arrow3DDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("01b-arrow3d", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        a = Arrow3D(start=[-2, -1, 0], end=[1.5, 0.5, 1.5])   # default white 3D arrow
        b = Arrow3D(start=[0, -2.5, 0], end=[-1.5, -2.5, 2], color=RED,   # red arrow: larger cone
                    thickness=0.08, height=0.6, base_radius=0.18)
        tip = Text("tip=(%.1f, %.1f, %.1f)" % tuple(a.get_end()),   # format the arrow-tip coordinates into a label
                   font_size=24, color=GREY_B).next_to(a.get_end(), UR, buff=0.2)   # place it next to the arrow tip
        self.add_fixed_orientation_mobjects(tip)   # lock orientation only: the text faces the camera but stays in 3D space
        self.add(a, b, tip)   # add the two arrows and the label to the scene
        print("arrow tip:", a.get_end())   # also print a copy to the console
        self.set_camera_orientation(phi=65 * DEGREES, theta=-60 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the two arrows
        self.move_camera(theta=-150 * DEGREES, run_time=1.2)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window


# ===== Sample 3: Cone's show_base / u_min / v_range ========================
class ConeDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("01b-cone", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        a = Cone(base_radius=1, height=2, show_base=True)   # a standard cone with the base disk
        a.shift(LEFT * 2.5)   # place it on the left
        b = Cone(base_radius=1, height=2, u_min=0.5, v_range=(0, PI))   # truncated top + only half a turn
        b.set_color(GREEN)   # recolor: the "color=" parameter of a Surface subclass has no effect; call set_color after construction
        b.shift(RIGHT * 2.5)   # place it on the right
        tag1 = Text("show_base=True", font_size=24, color=GREY_B).next_to(a, DOWN)   # bottom-left label
        tag2 = Text("u_min=0.5 v_range=(0,PI)", font_size=24, color=GREY_B).next_to(b, DOWN)   # bottom-right label
        self.add(a, b, tag1, tag2)   # add the two cones and labels to the scene
        self.set_camera_orientation(phi=65 * DEGREES, theta=-30 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the shape difference
        self.move_camera(theta=-120 * DEGREES, run_time=1.2)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window


# ===== Sample 4: Cylinder's show_ends / v_range / direction ================
class CylinderDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("01b-cylinder", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        a = Cylinder(radius=0.8, height=2.5)   # a default cylinder with top and bottom caps
        a.shift(LEFT * 2.5)   # place it on the left
        b = Cylinder(radius=0.8, height=2.5, show_ends=False, v_range=(0, PI),   # no caps + half a turn of the wall
                     direction=RIGHT)   # make the central axis horizontal
        b.set_color(RED)   # recolor: the "color=" parameter of a Surface subclass has no effect; call set_color after construction
        b.shift(RIGHT * 2.5 + UP * 0.4)   # place it on the right, a bit higher
        tag1 = Text("show_ends=True", font_size=24, color=GREY_B).next_to(a, DOWN)   # bottom-left label
        tag2 = Text("half + no ends + direction", font_size=24, color=GREY_B).next_to(b, DOWN)   # bottom-right label
        self.add(a, b, tag1, tag2)   # add the two cylinders and labels to the scene
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the shape difference
        self.move_camera(theta=-135 * DEGREES, run_time=1.2)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window


SCENES = [
    ("line3d", Line3DDemo),
    ("arrow3d", Arrow3DDemo),
    ("cone", ConeDemo),
    ("cylinder", CylinderDemo),
]

PAIRS = [
    ("line3d", ["line3d"]),
    ("arrow3d", ["arrow3d"]),
    ("cone", ["cone"]),
    ("cylinder", ["cylinder"]),
]

PAGE = "01b-Basic-3D-Objects-Advanced"


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
    only = set(a for a in sys.argv[1:] if not a.startswith("--"))
    if "--concat-only" not in sys.argv:
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

    for out_name, names in PAIRS:
        if only and out_name not in only:
            continue
        dst = os.path.join(ASSETS, "RTM output", "%s-%s.mp4" % (PAGE, out_name))
        concat(names, dst)
        print("concat ->", dst, os.path.getsize(dst), "bytes")
