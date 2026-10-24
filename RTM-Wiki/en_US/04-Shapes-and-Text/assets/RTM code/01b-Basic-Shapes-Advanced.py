# -*- coding: utf-8 -*-
"""Full source for the two samples in 01b-Basic-Shapes-Advanced.md (identical to the code blocks in the page).

Usage: python 01b-Basic-Shapes-Advanced.py <clip names>...
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
    Scene, AnnotationDot, LabeledDot, Ellipse, AnnularSector, Sector, Annulus,
    CubicBezier, ArcPolygon, ArcPolygonFromArcs, ArcBetweenPoints, Dot, Text,
    ORANGE, RED, GREEN, BLUE, TEAL, PURPLE, YELLOW, GREY_B,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI, TAU,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: emphasis dots, label dots, and ellipses ===================
class DotsEllipseDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01b-AnnotationDot / LabeledDot / Ellipse", font_size=30, color=YELLOW)
        title.to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— AnnotationDot: an emphasis dot with a white stroke (against the default Dot) ——
        ad = AnnotationDot().move_to([-4.2, 0.6, 0])   # default: blue fill, white stroke 5, radius 0.104 (no positional argument, move it after building)
        d = Dot([-2.7, 0.6, 0])   # for comparison: the default small white dot (radius 0.08, no stroke)
        l1 = Text("AnnotationDot vs Dot", font_size=22, color=GREY_B)
        l1.move_to([-3.45, -0.15, 0])   # centre the label below the two dots
        win.play(FadeIn(ad), FadeIn(d), run_time=0.5)   # fade in both dots together
        win.play(FadeIn(l1), run_time=0.3)   # fade in the label

        # —— LabeledDot: a dot with a label at its centre (a string renders as MathTex automatically) ——
        ld1 = LabeledDot("x").shift([0, 0.7, 0])   # radius adapts to the label
        ld2 = LabeledDot("42", radius=0.55).shift(DOWN * 1.15)   # radius given by hand
        l2 = Text("LabeledDot(label, radius)", font_size=22, color=GREY_B)
        l2.move_to([0, -2.35, 0])   # put the label below the two label dots
        win.play(FadeIn(ld1), run_time=0.5)   # a label dot with an adaptive radius
        win.play(FadeIn(ld2), run_time=0.5)   # a label dot with a manual radius
        win.play(FadeIn(l2), run_time=0.3)   # fade in the label

        # —— Ellipse: width / height, the two axis lengths ——
        e1 = Ellipse(width=4.2, height=1.6, color=PURPLE).shift([4.3, 0.9, 0])   # flat ellipse
        e2 = Ellipse(width=1.6, height=3.0, color=TEAL).shift([4.3, -1.4, 0])   # tall ellipse
        l3 = Text("Ellipse(width=, height=)", font_size=22, color=GREY_B)
        l3.move_to([4.3, -3.4, 0])   # put the label below the two ellipses
        win.play(Create(e1), run_time=0.6)   # draw the flat ellipse
        win.play(Create(e2), run_time=0.6)   # draw the tall ellipse
        win.play(FadeIn(l3), run_time=0.3)   # fade in the label
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


# ===== Sample 2: the annular sector family, Bézier curves, and arc polygons =
class SectorsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01b-AnnularSector / Sector / Annulus / Bezier / ArcPolygon",
                     font_size=24, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— First row: three filled "annular sector / ring" blocks ——
        asec = AnnularSector(inner_radius=0.5, outer_radius=1.2, angle=2.0,
                             start_angle=PI / 2, color=ORANGE).shift(LEFT * 4.4 + UP * 0.9)   # annular sector
        cap1 = Text("AnnularSector", font_size=20, color=GREY_B).next_to(asec, DOWN, buff=0.3)
        win.play(Create(asec), FadeIn(cap1), run_time=0.6)   # draw the annular sector

        sec = Sector(radius=0.95, angle=TAU / 3, color=RED).shift(UP * 0.9)   # solid sector (one slice of a pie chart)
        cap2 = Text("Sector", font_size=20, color=GREY_B).next_to(sec, DOWN, buff=0.3)
        win.play(Create(sec), FadeIn(cap2), run_time=0.6)   # draw the solid sector

        ann = Annulus(inner_radius=0.4, outer_radius=1.0, color=GREEN).shift(RIGHT * 4.4 + UP * 0.9)   # ring (doughnut)
        cap3 = Text("Annulus", font_size=20, color=GREY_B).next_to(ann, DOWN, buff=0.3)
        win.play(Create(ann), FadeIn(cap3), run_time=0.6)   # draw the ring

        # —— Second row: a hand-drawn Bézier, and a polygon with arcs between its vertices ——
        cb = CubicBezier([-6.2, -2.6, 0], [-4.9, -0.9, 0], [-3.9, -3.5, 0], [-2.7, -1.8, 0],
                         color=PURPLE, stroke_width=6)   # two anchors + two control handles
        cap4 = Text("CubicBezier(4 pts)", font_size=20, color=GREY_B).move_to([-4.45, -3.7, 0])
        win.play(Create(cb), FadeIn(cap4), run_time=0.6)   # draw the S-shaped Bézier curve

        ap = ArcPolygon([-1.7, -2.9, 0], [0, -1.5, 0], [1.7, -2.9, 0],
                        angle=PI / 6, color=BLUE, stroke_width=6)   # three vertices, edges joined by arcs
        cap5 = Text("ArcPolygon(angle=PI/6)", font_size=20, color=GREY_B).move_to([0, -3.7, 0])
        win.play(Create(ap), FadeIn(cap5), run_time=0.6)   # draw the arc-edged triangle

        a1 = ArcBetweenPoints([2.7, -2.9, 0], [4.4, -1.6, 0], angle=-PI / 3, color=TEAL)   # the first arc, arching up
        a2 = ArcBetweenPoints([4.4, -1.6, 0], [6.1, -2.9, 0], angle=PI / 3, color=TEAL)   # the second arc, dipping down
        apa = ArcPolygonFromArcs(a1, a2)   # join the two arcs end to end into one object
        cap6 = Text("ArcPolygonFromArcs", font_size=20, color=GREY_B).move_to([4.4, -3.7, 0])
        win.play(Create(a1), run_time=0.4)   # draw the first arc
        win.play(Create(a2), run_time=0.4)   # then the second
        win.play(FadeIn(cap6), run_time=0.3)   # fade in the label
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


SCENES = [
    ("dots_ellipse", DotsEllipseDemo),
    ("sectors", SectorsDemo),
]

PAIRS = [
    ("dots_ellipse", ["dots_ellipse"]),
    ("sectors", ["sectors"]),
]

PAGE = "01b-Basic-Shapes-Advanced"


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
