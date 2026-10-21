# -*- coding: utf-8 -*-
"""Full source for the three samples in 02-Surfaces.md (identical to the code blocks in the page).

Usage: python 02-Surfaces.py <clip names>...
With no arguments it renders every clip and concatenates the page's three sample videos (written to the parent assets/);
python 02-Surfaces.py --concat-only concatenates without rendering.
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
    ThreeDScene, Surface, Sphere, Torus, Text,
    GREEN, GREY_B, RED, YELLOW, PI, TAU,
    UP, DOWN, LEFT, RIGHT, DEGREES,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: Surface's parametric equation / resolution / checkerboard colors
class SurfaceDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("02-surface", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        surf = Surface(lambda u, v: [v * np.cos(u), v * np.sin(u), u * 0.5],   # parametric equation of a spiral ramp
                       u_range=(0, TAU), v_range=(0.3, 1.8),   # u makes a full turn, v spans the inner/outer radius
                       resolution=(16, 8))   # low resolution: keeps render time down while the faces stay readable
        self.add(surf)   # add the surface to the scene
        self.set_camera_orientation(phi=60 * DEGREES, theta=-60 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the default blue checkerboard
        surf.set_fill_by_checkerboard([GREEN, YELLOW], opacity=0.85)   # method: recolor the checkerboard in place
        win.play(Wait(0.6))   # pause 0.6s to see the new colors
        self.move_camera(theta=-150 * DEGREES, run_time=1.2)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window


# ===== Sample 2: Sphere's v_range cuts out a spherical cap =================
class SphereDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("02-sphere", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        full = Sphere(radius=1, resolution=(24, 12))   # full sphere: u a full turn, v from north to south pole
        full.shift(LEFT * 2.5)   # place it on the left
        half = Sphere(radius=1, resolution=(24, 12), v_range=(0, PI / 2))   # v_range cuts out the upper hemisphere
        half.set_color(RED)   # recolor: the "color=" parameter of a Surface subclass has no effect; call set_color after construction
        half.shift(RIGHT * 2.5)   # place it on the right
        tag1 = Text("v_range=(0,PI)", font_size=24, color=GREY_B).next_to(full, DOWN)   # bottom-left label
        tag2 = Text("v_range=(0,PI/2)", font_size=24, color=GREY_B).next_to(half, DOWN)   # bottom-right label
        self.add(full, half, tag1, tag2)   # add the two spheres and labels to the scene
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the spherical-cap shape
        self.move_camera(theta=-135 * DEGREES, run_time=1.2)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window


# ===== Sample 3: Torus's radii and v_range cutting half the tube ===========
class TorusDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("02-torus", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        full = Torus(major_radius=1.6, minor_radius=0.5)   # default full ring: ring radius 1.6, tube radius 0.5
        full.shift(LEFT * 2.5)   # place it on the left
        half = Torus(major_radius=1.6, minor_radius=0.5, v_range=(0, PI))   # v_range cuts out half the tube
        half.set_color(GREEN)   # recolor: the "color=" parameter of a Surface subclass has no effect; call set_color after construction
        half.shift(RIGHT * 2.5)   # place it on the right
        tag1 = Text("full ring", font_size=24, color=GREY_B).next_to(full, DOWN)   # bottom-left label
        tag2 = Text("v_range=(0,PI)", font_size=24, color=GREY_B).next_to(half, DOWN)   # bottom-right label
        self.add(full, half, tag1, tag2)   # add the two tori and labels to the scene
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the half-tube cross-section
        self.move_camera(theta=-135 * DEGREES, run_time=1.2)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window


SCENES = [
    ("surface", SurfaceDemo),
    ("sphere", SphereDemo),
    ("torus", TorusDemo),
]

PAIRS = [
    ("surface", ["surface"]),
    ("sphere", ["sphere"]),
    ("torus", ["torus"]),
]

PAGE = "02-Surfaces"


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
