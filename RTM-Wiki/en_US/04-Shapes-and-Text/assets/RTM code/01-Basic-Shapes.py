# -*- coding: utf-8 -*-
"""Full source for the three samples in 01-Basic-Shapes.md (identical to the code blocks in the page).

Usage: python 01-Basic-Shapes.py <clip names>...
With no arguments it renders every clip and concatenates the page's three sample videos (written to the parent assets/).
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
    Scene, Arc, ArcBetweenPoints, TangentialArc, CurvedArrow, CurvedDoubleArrow,
    Circle, Dot, Square, Text, DashedLine,
    BLUE, RED, GREEN, YELLOW, ORANGE, TEAL, GREY_B,
    UP, DOWN, LEFT, RIGHT, PI, TAU, DEGREES,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: the arc family Arc / ArcBetweenPoints / TangentialArc =====
class ArcDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-Arc family", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— Arc: radius / start_angle / angle / arc_center ——
        arc = Arc(radius=1.2, start_angle=0, angle=PI, color=BLUE, stroke_width=8,
                  arc_center=[-4.6, -1.0, 0])   # radius 1.2, sweeping 180° counter-clockwise from straight right
        cdot = Dot([-4.6, -1.0, 0], radius=0.06, color=YELLOW)   # centre dot = arc_center
        l1 = Text("Arc(angle=PI)", font_size=24, color=GREY_B)   # label for the arc
        l1.next_to(arc, DOWN, buff=0.3)   # place it right below the arc
        win.play(Create(arc), FadeIn(cdot), run_time=0.8)   # draw the arc and dot the centre
        win.play(FadeIn(l1), run_time=0.3)   # fade in the label

        # —— ArcBetweenPoints: angle controls the bend direction and size ——
        ab1 = ArcBetweenPoints([-1.7, -0.3, 0], [1.7, -0.3, 0], angle=PI / 2,
                               color=GREEN, stroke_width=8)   # positive angle (counter-clockwise): dips down into a valley
        ab2 = ArcBetweenPoints([-1.7, -2.1, 0], [1.7, -2.1, 0], angle=-PI / 2,
                               color=ORANGE, stroke_width=8)   # negative angle (clockwise): arches up into a hill
        lu = Text("angle=+PI/2", font_size=24, color=GREY_B).next_to(ab1, UP, buff=0.15)
        ld = Text("angle=-PI/2", font_size=24, color=GREY_B).next_to(ab2, DOWN, buff=0.15)
        win.play(Create(ab1), FadeIn(lu), run_time=0.7)   # positive-angle arc + top label
        win.play(Create(ab2), FadeIn(ld), run_time=0.7)   # negative-angle arc + bottom label

        # —— TangentialArc: corner arc for two intersecting lines (corner picks the quadrant) ——
        ln1 = DashedLine([3.1, -1.0, 0], [6.1, -1.0, 0], color=GREY_B)   # horizontal line that takes part in the intersection
        ln2 = DashedLine([4.6, -2.7, 0], [4.6, 0.7, 0], color=GREY_B)   # vertical line that takes part in the intersection
        ta = TangentialArc(ln1, ln2, radius=0.9, corner=(1, 1), color=TEAL)   # corner arc at the intersection
        lt = Text("TangentialArc(corner=(1,1))", font_size=22, color=GREY_B)
        lt.next_to(ln1, DOWN, buff=0.25)   # place it below the horizontal dashed line so it does not overlap the helper lines
        win.play(Create(ln1), Create(ln2), run_time=0.6)   # draw the two helper lines first
        win.play(Create(ta), FadeIn(lt), run_time=0.7)   # then the corner arc + label
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


# ===== Sample 2: the curved arrows CurvedArrow / CurvedDoubleArrow =========
class CurvedArrowDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-CurvedArrow / CurvedDoubleArrow", font_size=32, color=YELLOW)
        title.to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        ca1 = CurvedArrow([-3.2, 1.4, 0], [3.2, 1.4, 0], color=BLUE, stroke_width=6)   # default angle=TAU/4: dips down into a valley
        l1 = Text("CurvedArrow (default angle)", font_size=24, color=GREY_B)
        l1.next_to(ca1, UP, buff=0.1)   # put the label above the arrow
        win.play(Create(ca1), FadeIn(l1), run_time=0.8)   # draw the default-bend curved arrow

        ca2 = CurvedArrow([-3.2, -0.4, 0], [3.2, -0.4, 0], angle=-TAU / 4,
                          color=GREEN, stroke_width=6)   # negative angle: the bend flips (arches up into a hill)
        l2 = Text("CurvedArrow(angle=-TAU/4)", font_size=24, color=GREY_B)
        l2.next_to(ca2, DOWN, buff=0.15)   # put the label below (the curve is high in the middle, low at the ends)
        win.play(Create(ca2), FadeIn(l2), run_time=0.8)   # draw the reverse-bend curved arrow

        cda = CurvedDoubleArrow([-3.2, -2.3, 0], [3.2, -2.3, 0], color=RED, stroke_width=6)   # a tip at both ends
        l3 = Text("CurvedDoubleArrow", font_size=24, color=GREY_B)
        l3.next_to(cda, UP, buff=0.2)   # put the label inside the valley (the concave side, so it stays on screen)
        win.play(Create(cda), FadeIn(l3), run_time=0.8)   # draw the double-headed curved arrow
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


# ===== Sample 3: circles and dots Circle / Dot =============================
class CircleDotDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-Circle / Dot", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— Circle.surround(): scale a circle until it encloses any object ——
        sq = Square(side_length=1.3, color=GREEN, fill_opacity=0.4).shift(LEFT * 4.2)   # the square to be enclosed
        cir = Circle(radius=0.55, color=BLUE, stroke_width=7).shift(LEFT * 4.2 + UP * 1.7)   # the circle starts out not enclosing it
        l1 = Text("Circle.surround()", font_size=24, color=GREY_B)
        l1.next_to(sq, DOWN, buff=0.5)   # put the label below the square
        self.add(sq)   # add the square to the scene statically first
        win.play(FadeIn(cir), run_time=0.5)   # first see the small circle that encloses nothing
        win.play(cir.animate.surround(sq), run_time=0.8)   # the circle moves and scales until it just encloses the square (1.2x margin)
        win.play(FadeIn(l1), run_time=0.3)   # fade in the label
        pdot = Dot(cir.point_at_angle(45 * DEGREES), radius=0.07, color=YELLOW)   # take a point at 45° on the circle
        win.play(FadeIn(pdot), run_time=0.3)   # dot that point on the circle

        # —— Circle defaults: radius=None means 1, color=RED ——
        red_c = Circle().shift(RIGHT * 3.0)   # default: radius 1, red stroke
        l2 = Text("Circle() default: r=1, RED", font_size=24, color=GREY_B)
        l2.next_to(red_c, DOWN, buff=0.35)   # put the label below the red circle
        win.play(Create(red_c), FadeIn(l2), run_time=0.7)   # draw the default red circle

        # —— Dot: point / radius / color / fill_opacity ——
        d1 = Dot(point=[0.6, -2.5, 0])   # default: radius 0.08, filled white
        d2 = Dot(point=[2.2, -2.5, 0], radius=0.2, color=ORANGE)   # a bigger orange dot
        d3 = Dot(point=[3.8, -2.5, 0], radius=0.12, color=TEAL, fill_opacity=0.5)   # a semi-transparent teal dot
        l3 = Text("Dot(radius=...)", font_size=24, color=GREY_B)
        l3.next_to(d2, DOWN, buff=0.4)   # put the label below the middle dot (clear of the red circle's label)
        win.play(FadeIn(d1), FadeIn(d2), FadeIn(d3), run_time=0.5)   # fade in all three dots together
        win.play(FadeIn(l3), run_time=0.3)   # fade in the label
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


SCENES = [
    ("arc", ArcDemo),
    ("curved", CurvedArrowDemo),
    ("circle_dot", CircleDotDemo),
]

PAIRS = [
    ("arc", ["arc"]),
    ("curved", ["curved"]),
    ("circle_dot", ["circle_dot"]),
]

PAGE = "01-Basic-Shapes"


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
