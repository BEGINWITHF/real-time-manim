# -*- coding: utf-8 -*-
"""Full source for the six samples in 04-Angles-and-Callout-Boxes.md (identical to the code blocks in the page).

Usage: python 04-Angles-and-Callout-Boxes.py <sample names>...
With no arguments it renders every sample and concatenates the page's six sample videos (written to assets/RTM output/).
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
    Scene, Line, Arrow, Dot, Square, Circle, Triangle, Text, VGroup,
    Angle, RightAngle, SurroundingRectangle, BackgroundRectangle, Cross, Underline,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: Angle —— radius / quadrant / reflex angle / dot / elbow =====
class AngleDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("04-Angle", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— four quadrant values: the same angle, the marking arc drawn in a different quadrant ——
        quads = [(1, 1), (-1, 1), (1, -1), (-1, -1)]   # the "quadrant" parameter
        for i, q in enumerate(quads):
            l1 = Line(ORIGIN, RIGHT * 1.6)   # the "line1" parameter
            l2 = Line(ORIGIN, UP * 1.6)   # the "line2" parameter
            ang = Angle(l1, l2, radius=0.45, quadrant=q, color=ORANGE)   # the "radius / quadrant" parameters
            grp = VGroup(l1, l2, ang).move_to([-4.3 + i * 2.6, 1.5, 0])
            cap = Text("quadrant=%s" % (q,), font_size=18, color=GREY_B).next_to(grp, DOWN, buff=0.25)
            win.play(Create(grp), FadeIn(cap), run_time=0.5)   # draw the angles one by one + quadrant captions

        # —— other_angle (the reflex angle) + the dot family: add a dot inside the arc and change its radius/position/colour ——
        l1 = Line(ORIGIN, RIGHT * 1.6)
        l2 = Line(ORIGIN, UP * 1.6)
        big = Angle(l1, l2, radius=1.5, other_angle=True, color=RED)   # the "other_angle=True" parameter
        grp = VGroup(l1, l2, big).move_to([-1.4, -1.6, 0])
        cap = Text("other_angle=True", font_size=18, color=GREY_B).next_to(grp, DOWN, buff=0.25)
        win.play(Create(grp), FadeIn(cap), run_time=0.5)   # reflex angle + caption

        l1b = Line(ORIGIN, RIGHT * 1.6)   # another copy of the second side (one object can only mark one angle)
        l2b = Line(ORIGIN, UP * 1.6)
        marked = Angle(l1b, l2b, radius=1.0, dot=True, dot_radius=0.12,
                       dot_distance=0.75, dot_color=YELLOW, color=TEAL)   # the "dot / dot_radius / dot_distance / dot_color" parameters
        grp2 = VGroup(l1b, l2b, marked).move_to([1.6, -1.6, 0])
        cap2 = Text("dot=True dot_distance=0.75", font_size=18, color=GREY_B).next_to(grp2, DOWN, buff=0.25)
        win.play(Create(grp2), FadeIn(cap2), run_time=0.5)   # with a dot + caption

        # —— elbow=True: use a right-angle elbow instead of an arc; get_value() reads out the angle value ——
        l1c = Line(ORIGIN, RIGHT * 1.6)
        l2c = Line(ORIGIN, UP * 1.6)
        elbow = Angle(l1c, l2c, radius=0.6, elbow=True, color=PURPLE)   # the "elbow=True" parameter
        grp3 = VGroup(l1c, l2c, elbow).move_to([4.4, -1.6, 0])
        # get_value() is broken upstream in ManimCE 0.21 (Angle has no angle_value attribute,
        # both engines crash), so here we read the same value from the difference of the two sides' direction angles
        deg = (l2c.get_angle() - l1c.get_angle()) % (2 * PI)
        cap3 = Text("elbow=True (%.1f deg)" % (deg / PI * 180),
                    font_size=18, color=GREY_B).next_to(grp3, DOWN, buff=0.25)   # the difference of the two direction angles = 90.0
        win.play(Create(grp3), FadeIn(cap3), run_time=0.6)   # elbow + angle readout
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: Angle.from_three_points —— an angle from three points ======
class AngleThreePointsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("04-Angle.from_three_points", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        a = ORIGIN + LEFT * 2.2 + DOWN * 1.2   # the "A" parameter: start point
        b = ORIGIN + LEFT * 0.2 + DOWN * 1.2   # the "B" parameter: vertex
        c = ORIGIN + RIGHT * 0.6 + UP * 0.8   # the "C" parameter: end point
        dots = VGroup(Dot(a, radius=0.07, color=WHITE), Dot(b, radius=0.07, color=WHITE),
                      Dot(c, radius=0.07, color=WHITE))   # mark the three vertices with small dots
        ang = Angle.from_three_points(a, b, c, radius=0.7, color=GOLD)   # an angle from three points (B is the vertex)
        cap = Text("Angle.from_three_points(A, B, C)", font_size=20, color=GREY_B).to_edge(DOWN, buff=1.0)
        win.play(FadeIn(dots), run_time=0.4)   # show the dots first
        win.play(Create(ang), FadeIn(cap), run_time=0.7)   # then draw the angle
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: RightAngle —— length and colour of the right-angle mark =====
class RightAngleDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("04-RightAngle", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— length given explicitly as 0.25 / 0.6, with different colours ——
        l1 = Line(ORIGIN, RIGHT * 1.6)
        l2 = Line(ORIGIN, UP * 1.6)
        small = RightAngle(l1, l2, length=0.25, color=RED)   # the "length=0.25" parameter
        grp = VGroup(l1, l2, small).move_to([-2.6, 0.8, 0])
        cap = Text("length=0.25", font_size=18, color=GREY_B).next_to(grp, DOWN, buff=0.25)
        win.play(Create(grp), FadeIn(cap), run_time=0.5)   # small right-angle mark + caption

        l3 = Line(ORIGIN, RIGHT * 1.6)
        l4 = Line(ORIGIN, UP * 1.6)
        big = RightAngle(l3, l4, length=0.6, color=GREEN)   # the "length=0.6" parameter
        grp2 = VGroup(l3, l4, big).move_to([1.2, 0.8, 0])
        cap2 = Text("length=0.6", font_size=18, color=GREY_B).next_to(grp2, DOWN, buff=0.25)
        win.play(Create(grp2), FadeIn(cap2), run_time=0.5)   # large right-angle mark + caption

        # —— length omitted: derived from the two sides ——
        l5 = Line(ORIGIN, RIGHT * 1.6)
        l6 = Line(ORIGIN, UP * 1.6)
        auto = RightAngle(l5, l6, color=BLUE)   # do not pass length (default None)
        grp3 = VGroup(l5, l6, auto).move_to([4.6, 0.8, 0])
        cap3 = Text("length=None (auto)", font_size=18, color=GREY_B).next_to(grp3, DOWN, buff=0.25)
        win.play(Create(grp3), FadeIn(cap3), run_time=0.5)   # automatic length + caption
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 4: SurroundingRectangle —— colour / buff / corner radius ======
class SurroundingDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("04-SurroundingRectangle", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— a single object: default bright yellow, buff 0.1, no rounded corners ——
        sq = Square(side_length=1.4, color=BLUE, fill_opacity=0.5).move_to([-3.4, 1.2, 0])
        f1 = SurroundingRectangle(sq)   # the "*mobjects" parameter with only one object
        cap = Text("SurroundingRectangle(sq)", font_size=18, color=GREY_B).next_to(VGroup(sq, f1), DOWN, buff=0.25)
        win.play(Create(sq), run_time=0.4)   # draw the framed object first
        win.play(Create(f1), FadeIn(cap), run_time=0.5)   # then add the default frame + caption

        # —— a larger buff + rounded corners + a different colour ——
        ci = Circle(radius=0.7, color=GREEN, fill_opacity=0.5).move_to([0, 1.2, 0])
        f2 = SurroundingRectangle(ci, color=RED, buff=0.45, corner_radius=0.25)   # the "color / buff / corner_radius" parameters
        cap2 = Text("buff=0.45 corner_radius=0.25", font_size=18, color=GREY_B).next_to(VGroup(ci, f2), DOWN, buff=0.25)
        win.play(Create(ci), run_time=0.4)
        win.play(Create(f2), FadeIn(cap2), run_time=0.5)   # a wide, rounded frame + caption

        # —— several objects: take the overall bounding box ——
        tri = Triangle(color=PURPLE, fill_opacity=0.5).scale(0.6).move_to([3.0, 1.0, 0])
        dot = Dot(point=[4.6, 1.8, 0], radius=0.1, color=ORANGE)
        f3 = SurroundingRectangle(tri, dot, color=TEAL, buff=0.2)   # the "*mobjects" parameter with two objects: the overall bounding box
        cap3 = Text("SurroundingRectangle(tri, dot)", font_size=18, color=GREY_B).next_to(VGroup(tri, dot, f3), DOWN, buff=0.25)
        win.play(Create(tri), FadeIn(dot), run_time=0.4)
        win.play(Create(f3), FadeIn(cap3), run_time=0.5)   # overall bounding box + caption
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 5: BackgroundRectangle —— backdrop / stroke / opacity / buff ===
class BackgroundDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("04-BackgroundRectangle", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— default: a 75% opaque black backdrop under white text ——
        t1 = Text("readable", font_size=34, color=WHITE).move_to([-3.0, 1.2, 0])
        b1 = BackgroundRectangle(t1)   # default parameter values: color=None (treated as black), fill_opacity=0.75, buff=0
        win.play(FadeIn(b1), run_time=0.4)   # lay the backdrop first
        win.play(FadeIn(t1), run_time=0.4)   # then add the text

        # —— change the colour + add a stroke + tune the opacity ——
        t2 = Text("tinted", font_size=34, color=WHITE).move_to([1.4, 1.2, 0])
        b2 = BackgroundRectangle(t2, color=PURPLE, stroke_width=4, stroke_opacity=1,
                                 fill_opacity=0.5)   # the "color / stroke_width / stroke_opacity / fill_opacity" parameters
        win.play(FadeIn(b2), run_time=0.4)
        win.play(FadeIn(t2), run_time=0.4)

        # —— a larger buff: the backdrop is a ring bigger than the text ——
        t3 = Text("padded", font_size=34, color=WHITE).move_to([-1.0, -1.4, 0])
        b3 = BackgroundRectangle(t3, color=TEAL, fill_opacity=0.9, buff=0.35)   # the "buff=0.35" parameter
        cap = Text("buff=0.35", font_size=18, color=GREY_B).next_to(VGroup(t3, b3), DOWN, buff=0.25)
        win.play(FadeIn(b3), FadeIn(cap), run_time=0.4)
        win.play(FadeIn(t3), run_time=0.4)   # the backdrop is a ring bigger than the text
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 6: Cross / Underline —— two ways to negate ====================
class CrossUnderlineDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("04-Cross / Underline", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— Cross: position and size are decided by the crossed-out object ——
        sq = Square(side_length=1.2, color=BLUE, fill_opacity=0.5).move_to([-3.4, 0.6, 0])
        x1 = Cross(sq)   # the "mobject=sq" parameter: the cross sits on the square and its size follows the square
        cap1 = Text("Cross(sq)", font_size=18, color=GREY_B).next_to(VGroup(sq, x1), DOWN, buff=0.25)
        win.play(Create(sq), run_time=0.4)
        win.play(Create(x1), FadeIn(cap1), run_time=0.5)

        # —— a different colour / width / scale ——
        ci = Circle(radius=0.6, color=GREEN, fill_opacity=0.5).move_to([0, 0.6, 0])
        x2 = Cross(ci, stroke_color=YELLOW, stroke_width=14, scale_factor=1.4)   # the "stroke_color / stroke_width / scale_factor" parameters
        cap2 = Text("stroke_width=14 scale_factor=1.4", font_size=18, color=GREY_B).next_to(VGroup(ci, x2), DOWN, buff=0.25)
        win.play(Create(ci), run_time=0.4)
        win.play(Create(x2), FadeIn(cap2), run_time=0.5)

        # —— Underline: give only the width and buff (the length follows the object's width) ——
        t = Text("underlined", font_size=34, color=WHITE).move_to([3.4, 0.6, 0])
        u1 = Underline(t, buff=0.08, color=RED)   # the "buff=0.08" parameter
        cap3 = Text("Underline(t, buff=0.08)", font_size=18, color=GREY_B).next_to(VGroup(t, u1), DOWN, buff=0.35)
        win.play(FadeIn(t), run_time=0.4)
        win.play(Create(u1), FadeIn(cap3), run_time=0.5)

        t2 = Text("loose", font_size=34, color=WHITE).move_to([3.4, -1.6, 0])
        u2 = Underline(t2, buff=0.5, color=ORANGE)   # the "buff=0.5" parameter: farther from the text
        cap4 = Text("buff=0.5", font_size=18, color=GREY_B).next_to(VGroup(t2, u2), DOWN, buff=0.35)
        win.play(FadeIn(t2), run_time=0.4)
        win.play(Create(u2), FadeIn(cap4), run_time=0.5)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


SCENES = [
    ("angle", AngleDemo),
    ("angle3p", AngleThreePointsDemo),
    ("rightangle", RightAngleDemo),
    ("surrounding", SurroundingDemo),
    ("background", BackgroundDemo),
    ("cross", CrossUnderlineDemo),
]

PAIRS = [
    ("angle", ["angle"]),
    ("angle3p", ["angle3p"]),
    ("rightangle", ["rightangle"]),
    ("surrounding", ["surrounding"]),
    ("background", ["background"]),
    ("cross", ["cross"]),
]

PAGE = "04-Angles-and-Callout-Boxes"


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
