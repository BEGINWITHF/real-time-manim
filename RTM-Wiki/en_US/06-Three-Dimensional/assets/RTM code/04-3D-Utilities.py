# -*- coding: utf-8 -*-
"""Full source for the two samples in 04-3D-Utilities.md (identical to the code blocks in the page).

Usage: python 04-3D-Utilities.py <clip names>...
With no arguments it renders every clip and concatenates the page's two sample videos (written to the parent assets/);
python 04-3D-Utilities.py --concat-only concatenates without rendering.
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
    ThreeDScene, Cube, VGroup, Dot3D, Arrow3D, Text,
    GREEN, GREY_B, RED, YELLOW,
    UP, DOWN, DEGREES,
    get_3d_vmob_start_corner, get_3d_vmob_end_corner,
    get_3d_vmob_end_corner_index,
    get_3d_vmob_gradient_start_and_end_points,
    get_3d_vmob_start_corner_unit_normal, get_3d_vmob_end_corner_unit_normal,
    get_3d_vmob_unit_normal,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: start/end corners, gradient points and start/end normals ==
class CornersDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("04-corners", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        cube = Cube(side_length=2, fill_opacity=0.35, stroke_width=3)   # translucent cube
        face = cube[0]   # take one face (a single VMobject; these functions are only meaningful for it)
        p0 = get_3d_vmob_start_corner(face)   # start-corner coordinates (index is always 0)
        p1 = get_3d_vmob_end_corner(face)   # end-corner coordinates
        g0, g1 = get_3d_vmob_gradient_start_and_end_points(face)   # gradient start/end points = start/end corners
        n0 = get_3d_vmob_start_corner_unit_normal(face)   # unit normal at the start corner
        n1 = get_3d_vmob_end_corner_unit_normal(face)   # unit normal at the end corner
        print("start:", p0, " end idx:", get_3d_vmob_end_corner_index(face), "->", p1)   # print the query results to the console
        print("gradient:", g0, g1)   # the gradient start/end points are just the start/end corners
        print("normals:", n0, n1)   # unit normals at the start/end corners
        d0 = Dot3D(p0, radius=0.09, color=RED)   # red sphere marks the start corner
        d1 = Dot3D(p1, radius=0.09, color=YELLOW)   # yellow sphere marks the end corner
        a0 = Arrow3D(p0, p0 + 0.8 * n0, color=GREEN, thickness=0.05)   # normal arrow at the start corner
        a1 = Arrow3D(p1, p1 + 0.8 * n1, color=GREEN, thickness=0.05)   # normal arrow at the end corner
        tag = Text("corners(red/yellow) normals(green)", font_size=24, color=GREY_B).to_edge(DOWN)
        self.add(cube, d0, d1, a0, a1, tag)   # add the cube, corner markers and normal arrows to the scene
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the markers
        self.move_camera(theta=-135 * DEGREES, run_time=1.2)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window


# ===== Sample 2: look up the unit normal at any anchor index ===============
class FaceNormalsDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("04-face_normals", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        face = Cube(side_length=2)[1]   # use a different face (a side) to sample several anchors
        end_idx = get_3d_vmob_end_corner_index(face)   # index of the end corner in points
        idxs = [0, end_idx // 2, end_idx]   # the three anchors: start / middle / end
        arrows = VGroup()
        for i in idxs:   # draw a normal arrow at each anchor
            p = face.points[i]   # anchor coordinates
            n = get_3d_vmob_unit_normal(face, i)   # look up the unit normal by anchor index
            arrows.add(Arrow3D(p, p + 0.7 * n, color=GREEN, thickness=0.05))
        tag = Text("normals at idx 0 / %d / %d" % (end_idx // 2, end_idx),   # put the three indices into the label
                   font_size=24, color=GREY_B).to_edge(DOWN)
        self.add(face, arrows, tag)   # add this face and the three arrows to the scene (no need for the whole cube)
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the three normal arrows
        self.move_camera(theta=-120 * DEGREES, run_time=1.2)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window


SCENES = [
    ("corners", CornersDemo),
    ("face_normals", FaceNormalsDemo),
]

PAIRS = [
    ("corners", ["corners"]),
    ("face_normals", ["face_normals"]),
]

PAGE = "04-3D-Utilities"


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
