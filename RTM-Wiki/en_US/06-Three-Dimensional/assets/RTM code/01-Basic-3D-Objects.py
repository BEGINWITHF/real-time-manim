# -*- coding: utf-8 -*-
"""Full source for the three samples in 01-Basic-3D-Objects.md (identical to the code blocks in the page).

Usage: python 01-Basic-3D-Objects.py <clip names>...
With no arguments it renders every clip and concatenates the page's three sample videos (written to the parent assets/);
python 01-Basic-3D-Objects.py --concat-only concatenates without rendering.
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
    ThreeDScene, Cube, Prism, Dot3D, Text,
    BLUE, GREEN, GREY_B, RED, YELLOW,
    UP, DOWN, LEFT, RIGHT, UR, DEGREES,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: Cube's side length / color / opacity / stroke ==============
class CubeDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("01-cube", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen so it always faces the viewer
        a = Cube(side_length=2, fill_opacity=0.75, fill_color=BLUE)   # defaults: side length 2, translucent blue, no stroke
        b = Cube(side_length=1.2, fill_color=GREEN, fill_opacity=1.0, stroke_width=6)   # solid green, thicker stroke
        b.next_to(a, RIGHT, buff=1.2)   # place it to the right of the default cube
        tag1 = Text("default", font_size=26, color=GREY_B).next_to(a, DOWN)   # bottom-left label
        tag2 = Text("solid + stroke", font_size=26, color=GREY_B).next_to(b, DOWN)   # bottom-right label
        self.add(a, b, tag1, tag2)   # add the two cubes and labels to the scene
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the 3D effect
        self.move_camera(theta=-135 * DEGREES, run_time=1.4)   # animate a 90° orbit to see the other side
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window


# ===== Sample 2: Prism's dimensions (three side lengths) ===================
class PrismDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("01-prism", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        a = Prism(dimensions=[3, 2, 1])   # default side lengths [x, y, z] = [3, 2, 1]
        b = Prism(dimensions=[1, 1, 3], fill_color=RED, fill_opacity=0.6)   # tall thin red prism
        b.next_to(a, RIGHT, buff=1.2)   # place it to the right of the default prism
        tag1 = Text("[3, 2, 1]", font_size=26, color=GREY_B).next_to(a, DOWN)   # bottom-left label
        tag2 = Text("[1, 1, 3]", font_size=26, color=GREY_B).next_to(b, DOWN)   # bottom-right label
        self.add(a, b, tag1, tag2)   # add the two prisms and labels to the scene
        self.set_camera_orientation(phi=65 * DEGREES, theta=-60 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the side-length difference
        self.move_camera(theta=-150 * DEGREES, run_time=1.4)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window


# ===== Sample 3: Dot3D's radius / color / resolution =======================
class Dot3DDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("01-dot3d", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        big = Dot3D(2 * UR, radius=0.5, color=RED)   # large red sphere marking a 3D point
        rough = Dot3D(LEFT * 2.5 + DOWN, radius=0.4, color=GREEN, resolution=(4, 2))   # very low resolution: sharp facets
        smooth = Dot3D(RIGHT * 2.5 + DOWN, radius=0.4, color=GREEN)   # default (8, 8): a bit smoother
        tag1 = Text("res=(4,2)", font_size=26, color=GREY_B).next_to(rough, DOWN)   # bottom-left label
        tag2 = Text("default (8,8)", font_size=26, color=GREY_B).next_to(smooth, DOWN)   # bottom-right label
        self.add(big, rough, smooth, tag1, tag2)   # add the three spheres and labels to the scene
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to compare resolution
        self.move_camera(theta=-135 * DEGREES, run_time=1.4)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window


SCENES = [
    ("cube", CubeDemo),
    ("prism", PrismDemo),
    ("dot3d", Dot3DDemo),
]

PAIRS = [
    ("cube", ["cube"]),
    ("prism", ["prism"]),
    ("dot3d", ["dot3d"]),
]

PAGE = "01-Basic-3D-Objects"


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
