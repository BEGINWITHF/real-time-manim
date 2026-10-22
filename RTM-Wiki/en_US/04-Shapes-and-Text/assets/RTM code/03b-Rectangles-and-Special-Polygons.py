# -*- coding: utf-8 -*-
"""Full source for the five samples in 03b-Rectangles-and-Special-Polygons.md (identical to the code blocks in the page).

Usage: python 03b-Rectangles-and-Special-Polygons.py <sample names>...
With no arguments it renders every sample and concatenates the page's five sample videos (written to assets/RTM output/).
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
    Scene, Rectangle, Square, RoundedRectangle, Cutout, ConvexHull, Circle,
    Triangle, Dot, VGroup, Text,
    BLUE, GREEN, TEAL, PURPLE, ORANGE, YELLOW, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: Rectangle —— width, height, grid lines ====================
class RectangleDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("03b-Rectangle", font_size=28, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— default 4x2 ——
        r1 = Rectangle(color=BLUE)   # the color parameter: WHITE by default
        r1.move_to([-4.4, 1.4, 0])   # default width=4.0 / height=2.0
        cap1 = Text("Rectangle()  4x2", font_size=19, color=GREY_B).move_to([-4.4, 0.1, 0])
        win.play(Create(r1), FadeIn(cap1), run_time=0.6)   # draw the default rectangle + caption

        # —— width / height given explicitly ——
        r2 = Rectangle(width=2.4, height=1.6, color=GREEN)   # the "width / height" parameters
        r2.move_to([0, 1.4, 0])   # narrow and short
        cap2 = Text("width=2.4 height=1.6", font_size=19, color=GREY_B).move_to([0, 0.1, 0])
        win.play(Create(r2), FadeIn(cap2), run_time=0.6)   # draw the custom size + caption

        # —— grid_xstep / grid_ystep: draw a grid inside the rectangle ——
        r3 = Rectangle(width=3.2, height=1.8, color=ORANGE,
                       grid_xstep=0.8, grid_ystep=0.6)   # the "grid_xstep / grid_ystep" parameters
        r3.move_to([4.4, 1.4, 0])   # the interior is cut into small cells
        cap3 = Text("grid_xstep=0.8 grid_ystep=0.6", font_size=19, color=GREY_B).move_to([4.4, 0.1, 0])
        win.play(Create(r3), FadeIn(cap3), run_time=0.6)   # draw the gridded rectangle + caption
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: Square —— side_length is readable and writable ============
class SquareDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("03b-Square", font_size=28, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        sq1 = Square(color=BLUE, fill_opacity=0.5)   # default side_length=2.0
        sq1.move_to([-3.6, 0.4, 0])
        cap1 = Text("Square()  2.0", font_size=19, color=GREY_B).move_to([-3.6, -1.5, 0])
        win.play(Create(sq1), FadeIn(cap1), run_time=0.6)   # draw the default square + caption

        sq2 = Square(side_length=1.2, color=TEAL, fill_opacity=0.5)   # the "side_length" parameter
        sq2.move_to([0, 0.4, 0])
        cap2 = Text("side_length=1.2", font_size=19, color=GREY_B).move_to([0, -1.5, 0])
        win.play(Create(sq2), FadeIn(cap2), run_time=0.6)   # draw the small square + caption

        # —— side_length is a readable and writable attribute: assigning it changes the shape on the spot ——
        sq3 = Square(color=PURPLE, fill_opacity=0.5)
        sq3.move_to([4.0, 0.4, 0])
        cap3 = Text("sq.side_length = 2.6", font_size=19, color=GREY_B).move_to([4.0, -1.5, 0])
        win.play(Create(sq3), FadeIn(cap3), run_time=0.6)   # draw it at the default size first
        sq3.side_length = 2.6   # default 2.0; assigning changes the shape immediately (no rebuild)
        win.play(Wait(0.5))   # hold after assigning so the change is visible
        win.close()   # close the RTM window


# ===== Sample 3: RoundedRectangle —— corner radius (single / four different) ==
class RoundedDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("03b-RoundedRectangle", font_size=28, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        rr1 = RoundedRectangle(corner_radius=0.5, width=3.4, height=1.6,
                               color=TEAL, fill_opacity=0.5)   # the "corner_radius=0.5" parameter
        rr1.move_to([0, 1.3, 0])
        cap1 = Text("RoundedRectangle(corner_radius=0.5)", font_size=19, color=GREY_B).move_to([0, 0.2, 0])
        win.play(Create(rr1), FadeIn(cap1), run_time=0.6)   # all four corners the same radius + caption

        rr2 = RoundedRectangle(corner_radius=[0.05, 0.35, 0.65, 1.0],
                               width=3.4, height=1.6,
                               color=PURPLE, fill_opacity=0.5)   # the "corner_radius=[four values]" parameter
        rr2.move_to([0, -1.6, 0])
        cap2 = Text("corner_radius=[0.05, 0.35, 0.65, 1.0]", font_size=19, color=GREY_B).move_to([0, -2.7, 0])
        win.play(Create(rr2), FadeIn(cap2), run_time=0.6)   # a different radius at each corner + caption
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 4: Cutout —— punching holes out of a main shape ==============
class CutoutDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("03b-Cutout", font_size=28, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        main = Rectangle(width=5.0, height=2.6, color=TEAL,
                         fill_opacity=0.9).move_to([-2.4, -0.4, 0])   # the main shape (with fill)
        # the "main_shape / *mobjects" parameters: every shape after this is cut out of the main shape
        cut = Cutout(main,
                     Circle(radius=0.55, color=WHITE).move_to([-4.0, -0.4, 0]),   # cut a round hole
                     Triangle(color=WHITE).scale(0.7).move_to([-1.2, -0.4, 0]))   # and cut a triangular hole
        cap = Text("Cutout(main, Circle, Triangle)", font_size=19, color=GREY_B).move_to([-2.4, -2.1, 0])
        win.play(Create(main), run_time=0.5)   # draw the main shape first
        win.play(Create(cut), FadeIn(cap), run_time=0.8)   # swap in the holed shape + caption
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 5: ConvexHull —— the convex hull of a family of points =======
class ConvexHullDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("03b-ConvexHull", font_size=28, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        pts = [[-4.6, -1.2, 0], [-3.2, 1.4, 0], [-1.6, 0.2, 0], [-2.2, -1.6, 0],
               [-0.6, 1.0, 0], [0.4, -0.8, 0], [-1.0, 1.8, 0]]   # seven irregular points
        dots = VGroup(*[Dot(p, radius=0.07, color=YELLOW) for p in pts])   # draw the points first
        hull = ConvexHull(*pts, color=GREEN, fill_opacity=0.4)   # the "*points / tolerance" parameters
        cap = Text("ConvexHull(*points, tolerance=1e-05)", font_size=19, color=GREY_B).move_to([-2.2, -2.7, 0])
        win.play(FadeIn(dots), run_time=0.5)   # the scattered points
        win.play(FadeIn(hull), FadeIn(cap), run_time=0.8)   # the convex hull + caption
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


SCENES = [
    ("rectangle", RectangleDemo),
    ("square", SquareDemo),
    ("rounded", RoundedDemo),
    ("cutout", CutoutDemo),
    ("convexhull", ConvexHullDemo),
]

PAIRS = [
    ("rectangle", ["rectangle"]),
    ("square", ["square"]),
    ("rounded", ["rounded"]),
    ("cutout", ["cutout"]),
    ("convexhull", ["convexhull"]),
]

PAGE = "03b-Rectangles-and-Special-Polygons"


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
