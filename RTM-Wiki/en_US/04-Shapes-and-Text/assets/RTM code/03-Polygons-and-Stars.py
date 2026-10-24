# -*- coding: utf-8 -*-
"""Full source for the two samples in 03-Polygons-and-Stars.md (identical to the code blocks in the page).

Usage: python 03-Polygons-and-Stars.py <clip names>...
With no arguments it renders every clip and concatenates the page's two sample videos (written to the parent assets/).
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
    Scene, Polygram, Polygon, RegularPolygon, Triangle, Star, RegularPolygram,
    Dot, VGroup, Text,
    TEAL, GREEN, PURPLE, ORANGE, BLUE, GOLD, YELLOW, GREY_B,
    UP, DOWN, Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: Polygram / Polygon / RegularPolygon / Triangle ============
class PolygonsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("03-Polygram / Polygon / RegularPolygon / Triangle", font_size=26, color=YELLOW)
        title.to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— Polygram: one group of vertices = one positional argument, a scrambled order can self-intersect ——
        pb = Polygram([[-5.6, 2.0, 0], [-2.6, 0.8, 0], [-3.6, 2.0, 0], [-4.6, 0.8, 0]],
                      color=TEAL, stroke_width=5)   # vertices interleaved "top-left → bottom-right → top-right → bottom-left"
        cap1 = Text("Polygram (crossed order)", font_size=20, color=GREY_B).move_to([-4.6, 0.4, 0])
        win.play(Create(pb), FadeIn(cap1), run_time=0.7)   # draw the bow tie + caption

        # —— Polygon: joins in vertex order, closes, and can be filled ——
        pg = Polygon([-1.6, 2.0, 0], [1.6, 2.0, 0], [0.9, 0.7, 0], [-0.7, 0.7, 0],
                     color=GREEN, fill_opacity=0.55, stroke_width=5)   # an irregular quadrilateral with four vertices
        cap2 = Text("Polygon(*vertices)", font_size=20, color=GREY_B).move_to([0, 0.4, 0])
        win.play(Create(pg), FadeIn(cap2), run_time=0.7)   # draw the quadrilateral + caption

        # —— Triangle: an equilateral triangle (the n=3 specialization) ——
        tri = Triangle(radius=1.2, color=BLUE, fill_opacity=0.55).shift([4.6, 1.5, 0])   # equilateral triangle
        cap3 = Text("Triangle()", font_size=20, color=GREY_B).move_to([4.6, 0.4, 0])
        win.play(Create(tri), FadeIn(cap3), run_time=0.6)   # draw the triangle + caption

        # —— RegularPolygon: the shape changes as soon as n does ——
        r4 = RegularPolygon(n=4, radius=1.1, color=PURPLE, fill_opacity=0.55).shift([-4.6, -1.5, 0])   # n=4
        r6 = RegularPolygon(n=6, radius=1.1, color=ORANGE, fill_opacity=0.55).shift([0, -1.5, 0])   # n=6
        r8 = RegularPolygon(n=8, radius=1.1, color=BLUE, fill_opacity=0.55).shift([4.6, -1.5, 0])   # n=8
        cap4 = Text("RegularPolygon(n=4 / 6 / 8)", font_size=22, color=GREY_B).move_to([0, -2.8, 0])
        win.play(Create(r4), run_time=0.45)   # draw n=4
        win.play(Create(r6), run_time=0.45)   # draw n=6
        win.play(Create(r8), FadeIn(cap4), run_time=0.45)   # draw n=8 + caption
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


# ===== Sample 2: Star / RegularPolygram / round_corners / get_vertices =====
class StarsRoundDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("03-Star / RegularPolygram / round_corners / get_vertices",
                     font_size=24, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— First row: three stars ——
        s5 = Star(n=5, outer_radius=1.5, inner_radius=0.6, color=GOLD, fill_opacity=0.9)
        s5.shift([-4.7, 1.5, 0])   # a pentagram with a hand-given inner radius
        cap1 = Text("Star(inner_radius=0.6)", font_size=19, color=GREY_B).move_to([-4.7, 0.4, 0])
        win.play(Create(s5), FadeIn(cap1), run_time=0.6)   # draw the gold pentagram + caption

        rp = RegularPolygram(5, density=2, radius=1.4, color=TEAL, stroke_width=5)
        rp.shift([-0.6, 1.5, 0])   # the pentagram base class: join every other point (crossing lines built in)
        cap2 = Text("RegularPolygram(density=2)", font_size=19, color=GREY_B).move_to([-0.6, 0.4, 0])
        win.play(Create(rp), FadeIn(cap2), run_time=0.6)   # draw the pentagram wireframe + caption

        s7 = Star(n=7, outer_radius=1.4, density=3, color=BLUE, fill_opacity=0.6)
        s7.shift([4.6, 1.5, 0])   # seven-pointed star: inner_radius left to density to derive
        cap3 = Text("Star(n=7, density=3)", font_size=19, color=GREY_B).move_to([4.6, 0.4, 0])
        win.play(Create(s7), FadeIn(cap3), run_time=0.6)   # draw the seven-pointed star + caption

        # —— Second row: identical trapezoids, differing only in the corner radius ——
        t1 = Polygon([-5.9, -0.7, 0], [-3.3, -0.7, 0], [-3.7, -2.5, 0], [-5.5, -2.5, 0],
                     color=ORANGE, fill_opacity=0.55).round_corners(0.15)   # slight rounding
        cap4 = Text("round_corners(0.15)", font_size=19, color=GREY_B).move_to([-4.6, -2.85, 0])
        win.play(Create(t1), FadeIn(cap4), run_time=0.6)   # draw the slightly rounded trapezoid + caption

        t2 = Polygon([-2.7, -0.7, 0], [-0.1, -0.7, 0], [-0.5, -2.5, 0], [-2.3, -2.5, 0],
                     color=PURPLE, fill_opacity=0.55).round_corners(0.55)   # heavy rounding
        cap5 = Text("round_corners(0.55)", font_size=19, color=GREY_B).move_to([-1.4, -2.85, 0])
        win.play(Create(t2), FadeIn(cap5), run_time=0.6)   # draw the heavily rounded trapezoid + caption

        # —— get_vertices(): mark every vertex ——
        hexa = RegularPolygon(n=6, radius=1.1, color=BLUE, fill_opacity=0.3).shift([4.6, -1.6, 0])   # a blank hexagon
        dots = VGroup(*[Dot(p, radius=0.07, color=YELLOW) for p in hexa.get_vertices()])   # place yellow dots at the vertices
        cap6 = Text("get_vertices() -> dots", font_size=19, color=GREY_B).move_to([4.6, -2.85, 0])
        win.play(Create(hexa), run_time=0.5)   # draw the hexagon first
        win.play(FadeIn(dots), FadeIn(cap6), run_time=0.5)   # the yellow vertex dots + caption
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


SCENES = [
    ("polygons", PolygonsDemo),
    ("stars_round", StarsRoundDemo),
]

PAIRS = [
    ("polygons", ["polygons"]),
    ("stars_round", ["stars_round"]),
]

PAGE = "03-Polygons-and-Stars"


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
