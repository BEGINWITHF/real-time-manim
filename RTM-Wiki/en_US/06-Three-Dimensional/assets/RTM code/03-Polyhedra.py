# -*- coding: utf-8 -*-
"""Full source for the three samples in 03-Polyhedra.md (identical to the code blocks in the page).

Usage: python 03-Polyhedra.py <clip names>...
With no arguments it renders every clip and concatenates the page's three sample videos (written to the parent assets/);
python 03-Polyhedra.py --concat-only concatenates without rendering.
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
    ThreeDScene, Polyhedron, Tetrahedron, Octahedron, Icosahedron,
    Dodecahedron, ConvexHull3D, VGroup, Dot3D, Text,
    BLUE, GREEN, GREY_B, RED, YELLOW,
    UP, DOWN, LEFT, RIGHT, DEGREES,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: the four Platonic solids + graph/faces access =============
class PlatonicDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("03-platonic", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        solids = VGroup(
            Tetrahedron(edge_length=1),      # 4-face tetrahedron
            Octahedron(edge_length=1),       # 8-face octahedron
            Icosahedron(edge_length=0.9),    # 20-face icosahedron
            Dodecahedron(edge_length=0.7),   # 12-face dodecahedron
        ).arrange(RIGHT, buff=1.2)   # arrange left to right in a row
        solids.to_edge(DOWN, buff=1.4)   # lower it a bit to leave room for the title
        octa = solids[1]   # take the octahedron to demo attribute access
        octa.graph[0].set_color(RED)   # color one vertex (graph is the vertex Graph)
        octa.faces[2].set_color(YELLOW)   # color one face (faces is the face VGroup)
        tag = Text("tetra / octa / icosa / dodeca", font_size=24, color=GREY_B).next_to(solids, DOWN)
        self.add(solids, tag)   # add the four solids and the label to the scene
        self.set_camera_orientation(phi=65 * DEGREES, theta=-30 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the four solids
        self.move_camera(theta=-120 * DEGREES, run_time=1.4)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window


# ===== Sample 2: custom vertex/face tables + dragging a vertex to deform ===
class PolyhedronDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # safety wiring: animate is played directly by win.play (only scene methods like move_camera really call self.play)
        title = Text("03-polyhedron", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        pyramid = Polyhedron(
            vertex_coords=[[1, 1, 0], [1, -1, 0], [-1, -1, 0], [-1, 1, 0], [0, 0, 2]],   # 4 base vertices + 1 apex
            faces_list=[[0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4], [0, 1, 2, 3]],   # 4 side faces + 1 base
            faces_config={"fill_opacity": 0.6, "fill_color": BLUE},   # face config: translucent blue
        )
        pyramid.shift(LEFT * 2)   # shift left as a whole to leave room for the deformation
        pyramid.faces[2].set_color(YELLOW)   # recolor the 3rd face (a side face)
        pyramid.graph[4].set_color(RED)   # color the apex vertex
        print("faces:", len(pyramid.faces), "vertices:", len(pyramid.graph))   # confirm the structure on the console
        tag = Text("faces[2] / graph[4]", font_size=24, color=GREY_B).next_to(pyramid, DOWN)
        self.add(pyramid, tag)   # add the pyramid and the label to the scene
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the colored face and vertex
        win.play(pyramid.graph[4].animate.shift(DOWN + RIGHT * 0.5), run_time=1.0)   # drag the apex: the updater deforms the whole solid
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window


# ===== Sample 3: ConvexHull3D computes the hull automatically ==============
class HullDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("03-hull", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        pts = [[1.9, 0.4, -1.5], [-0.9, 1.2, 0.6], [0.4, 0.4, -1.8],   # 6 3D points
               [-1.5, -0.8, -0.5], [0.8, -1.4, 0.9], [-0.2, 0.1, 2.0]]
        hull = ConvexHull3D(*pts, faces_config={"fill_opacity": 0.4, "fill_color": GREEN})   # automatically compute the convex hull as a polyhedron
        dots = VGroup(*[Dot3D(p, radius=0.08, color=RED) for p in pts])   # mark the original points with small red spheres
        tag = Text("ConvexHull3D(*points)", font_size=24, color=GREY_B).to_edge(DOWN)
        self.add(hull, dots, tag)   # add the hull, points and label to the scene
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the hull envelope
        self.move_camera(theta=-135 * DEGREES, run_time=1.4)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window


SCENES = [
    ("platonic", PlatonicDemo),
    ("polyhedron", PolyhedronDemo),
    ("hull", HullDemo),
]

PAIRS = [
    ("platonic", ["platonic"]),
    ("polyhedron", ["polyhedron"]),
    ("hull", ["hull"]),
]

PAGE = "03-Polyhedra"


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
