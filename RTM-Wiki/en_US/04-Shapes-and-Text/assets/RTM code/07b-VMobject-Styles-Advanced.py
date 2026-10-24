# -*- coding: utf-8 -*-
"""Full source for the nine samples in 07b-VMobject-Styles-Advanced.md (identical to the code blocks in the page).

Usage: python 07b-VMobject-Styles-Advanced.py <sample names>...
With no arguments it renders every sample and concatenates the page's nine sample videos (written to assets/RTM output/).
"""
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

from real_time_manim import (
    Scene, Square, Circle, Polygon, Line, Dot, Triangle, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: set_opacity —— whole-object transparency + the family switch ==
class OpacityDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("07b-set_opacity", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— three opacity levels: 0.25 / 0.6 / 1.0 (1.0 if you do not call it) ——
        for i, op in enumerate([0.25, 0.6, 1.0]):
            sq = Square(side_length=1.3, color=BLUE).set_fill(BLUE, 0.9)
            sq.move_to([-4.0 + i * 1.8, 1.3, 0])
            sq.set_opacity(op)   # the "opacity" parameter: fill and stroke change together
            cap = Text("opacity=%.2f" % op, font_size=18, color=GREY_B).next_to(sq, DOWN, buff=0.2)
            win.play(Create(sq), FadeIn(cap), run_time=0.45)   # draw one by one + caption

        # —— family: on the same VGroup, True changes the submobjects too, False changes only the container ——
        g1 = VGroup(Square(side_length=0.9, color=GREEN).set_fill(GREEN, 0.9),
                    Circle(radius=0.5, color=GREEN).set_fill(GREEN, 0.9))
        g1.arrange(RIGHT, buff=0.3).move_to([-2.6, -1.4, 0])
        g1.set_opacity(0.3, family=True)   # the "family=True" parameter: container and submobjects go down together
        cap1 = Text("family=True", font_size=18, color=GREY_B).next_to(g1, DOWN, buff=0.2)
        win.play(FadeIn(g1), FadeIn(cap1), run_time=0.5)   # both submobjects fade

        g2 = VGroup(Square(side_length=0.9, color=ORANGE).set_fill(ORANGE, 0.9),
                    Circle(radius=0.5, color=ORANGE).set_fill(ORANGE, 0.9))
        g2.arrange(RIGHT, buff=0.3).move_to([2.6, -1.4, 0])
        g2.set_opacity(0.3, family=False)   # the "family=False" parameter: only the container changes
        cap2 = Text("family=False", font_size=18, color=GREY_B).next_to(g2, DOWN, buff=0.2)
        win.play(FadeIn(g2), FadeIn(cap2), run_time=0.5)   # the submobjects keep their own 0.9
        win.play(Wait(0.5))   # hold to compare the two groups
        win.close()   # close the RTM window


# ===== Sample 2: set_sheen / set_sheen_direction —— the sheen gradient =======
class SheenDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("07b-set_sheen", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— three levels of factor ——
        for i, f in enumerate([0.0, 0.6, 1.5]):
            sq = Square(side_length=1.2, color=BLUE).set_fill(BLUE, 1.0)
            sq.move_to([-4.0 + i * 1.7, 1.3, 0])
            sq.set_sheen(f, direction=UP)   # the "factor / direction=UP" parameters
            cap = Text("factor=%.1f" % f, font_size=18, color=GREY_B).next_to(sq, DOWN, buff=0.2)
            win.play(Create(sq), FadeIn(cap), run_time=0.45)   # 0 turns it off / 0.6 / 1.5

        # —— direction switched to RIGHT, so the sheen goes from left to right ——
        sq2 = Square(side_length=1.2, color=TEAL).set_fill(TEAL, 1.0).move_to([1.4, -1.2, 0])
        sq2.set_sheen(1.0, direction=RIGHT)   # the "direction=RIGHT" parameter
        cap2 = Text("direction=RIGHT", font_size=18, color=GREY_B).next_to(sq2, DOWN, buff=0.2)
        win.play(Create(sq2), FadeIn(cap2), run_time=0.5)

        # —— set_sheen_direction: change only the direction, reusing the last factor for the strength ——
        sq3 = Square(side_length=1.2, color=PURPLE).set_fill(PURPLE, 1.0).move_to([4.4, -1.2, 0])
        sq3.set_sheen(1.0, direction=UP)   # use UP first
        sq3.set_sheen_direction(DOWN)   # then change only the direction (family defaults to True)
        cap3 = Text("set_sheen_direction(DOWN)", font_size=18, color=GREY_B).next_to(sq3, DOWN, buff=0.2)
        win.play(Create(sq3), FadeIn(cap3), run_time=0.5)
        win.play(Wait(0.5))   # hold to see the gradient direction
        win.close()   # close the RTM window


# ===== Sample 3: make_smooth —— turning a polyline into a smooth curve ======
class MakeSmoothDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("07b-make_smooth", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        verts = [[-3.2, 1.0, 0], [-1.6, -0.6, 0], [-0.2, 1.2, 0], [1.4, -0.4, 0]]   # the polyline's vertices
        raw = Polygon(*verts, color=GREY_B, stroke_width=5)   # untouched (with corners)
        smoothed = Polygon(*verts, color=GREEN, stroke_width=5)   # the copy to be smoothed
        smoothed.make_smooth()   # turn the corner points into smooth anchors: the polyline becomes a curve
        raw.shift(DOWN * 1.4)   # above: untouched
        smoothed.shift(DOWN * 1.4)
        cap1 = Text("jagged (raw)", font_size=20, color=GREY_B).next_to(raw, UP, buff=0.25)
        cap2 = Text("make_smooth()", font_size=20, color=GREEN).next_to(smoothed, UP, buff=0.25)
        win.play(Create(raw), FadeIn(cap1), run_time=0.6)   # look at the polyline first
        win.play(Create(smoothed), FadeIn(cap2), run_time=0.6)   # then the same path after smoothing
        win.play(Wait(0.5))   # hold to compare
        win.close()   # close the RTM window


# ===== Sample 4: make_jagged —— turning a smooth curve back into a polyline ===
class MakeJaggedDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("07b-make_jagged", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        circle = Circle(radius=1.2, color=BLUE).set_fill(BLUE, 0.3)   # a circle is smooth to begin with
        circle.move_to(LEFT * 2.2 + DOWN * 0.6)
        jagged = Circle(radius=1.2, color=ORANGE).set_fill(ORANGE, 0.3)
        jagged.make_jagged()   # turn the smooth anchors back into corners: the circle becomes a polygon
        jagged.move_to(RIGHT * 2.2 + DOWN * 0.6)
        cap1 = Text("Circle (smooth)", font_size=20, color=BLUE).next_to(circle, UP, buff=0.25)
        cap2 = Text("make_jagged()", font_size=20, color=ORANGE).next_to(jagged, UP, buff=0.25)
        win.play(Create(circle), FadeIn(cap1), run_time=0.6)   # look at the circle first
        win.play(Create(jagged), FadeIn(cap2), run_time=0.6)   # then the same-radius "polyline circle"
        win.play(Wait(0.5))   # hold to compare
        win.close()   # close the RTM window


# ===== Sample 5: pointwise_become_partial —— trimming a stretch along a path ===
class PartialDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("07b-pointwise_become_partial", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— the same circle, trimming one [a, b] stretch at a time, four times ——
        spans = [(0.0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.0)]   # the "a / b" parameters
        for i, (a, b) in enumerate(spans):
            src = Circle(radius=0.9, color=TEAL, stroke_width=6)   # the source object
            part = Circle(radius=0.9)   # the object that receives the trimmed result
            part.pointwise_become_partial(src, a, b)   # the "vmobject / a / b" parameters
            part.set_stroke(TEAL, 6)
            part.move_to([-4.0 + i * 2.2, 1.2, 0])
            cap = Text("[%.2f, %.2f]" % (a, b), font_size=18, color=GREY_B).next_to(part, DOWN, buff=0.25)
            win.play(Create(part), FadeIn(cap), run_time=0.45)   # four quarter arcs

        # —— [0, 1] is the whole path (the same length as the source object) ——
        src = Circle(radius=0.9, color=GOLD, stroke_width=6)
        whole = Circle(radius=0.9)
        whole.pointwise_become_partial(src, 0, 1)   # a=0, b=1: the whole path
        whole.set_stroke(GOLD, 6).move_to([-1.0, -1.4, 0])
        cap = Text("[0, 1] = whole path", font_size=18, color=GREY_B).next_to(whole, DOWN, buff=0.25)
        win.play(Create(whole), FadeIn(cap), run_time=0.5)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 6: get_stroke_width —— reading the current stroke width =======
class GetWidthDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("07b-get_stroke_width", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        ln = Line([-4.4, 1.0, 0], [-0.4, 1.0, 0], color=BLUE, stroke_width=4)   # the initial stroke width is 4
        info = Text("get_stroke_width() = %.1f" % ln.get_stroke_width(), font_size=24, color=WHITE)
        info.next_to(ln, DOWN, buff=0.4)
        win.play(Create(ln), FadeIn(info), run_time=0.5)   # the readout is 4.0

        ln.set_stroke(width=14)   # change the stroke width
        info.become(Text("after set_stroke(width=14) = %.1f" % ln.get_stroke_width(),
                         font_size=24, color=WHITE).next_to(ln, DOWN, buff=0.4))
        win.play(Create(ln), run_time=0.4)   # the line gets thicker
        win.play(FadeIn(info), run_time=0.3)   # the readout becomes 14.0

        # —— background=True: it reads the "background stroke width" (0 by default, and 0 if it has never been set) ——
        info2 = Text("get_stroke_width(background=True) = %.1f" % ln.get_stroke_width(background=True),
                     font_size=24, color=ORANGE).next_to(info, DOWN, buff=0.25)
        win.play(FadeIn(info2), run_time=0.4)   # the "background=True" parameter
        win.play(Wait(0.5))   # hold to see the readouts
        win.close()   # close the RTM window


# ===== Sample 7: set_cap_style —— the three line end-cap styles ============
class CapStyleDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("07b-set_cap_style", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        from manim import CapStyleType   # the enum of the three end-cap styles
        styles = [("ROUND", CapStyleType.ROUND), ("BUTT", CapStyleType.BUTT),
                  ("SQUARE", CapStyleType.SQUARE)]   # the "cap_style" parameter
        for i, (name, style) in enumerate(styles):
            ln = Line([-4.4, 1.4 - i * 1.5, 0], [-1.2, 1.4 - i * 1.5, 0],
                      color=TEAL, stroke_width=40)   # only a thick line makes the end caps visible
            ln.set_cap_style(style)   # the "cap_style=CapStyleType.%s" parameter % name
            cap = Text("CapStyleType.%s" % name, font_size=20, color=GREY_B).next_to(ln, RIGHT, buff=0.4)
            win.play(Create(ln), FadeIn(cap), run_time=0.5)   # the three end caps appear in turn
        win.play(Wait(0.5))   # hold to compare
        win.close()   # close the RTM window


# ===== Sample 8: change_anchor_mode —— the two modes, smooth / jagged ======
class AnchorModeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("07b-change_anchor_mode", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        verts = [[-3.0, 0.8, 0], [-1.4, -0.8, 0], [0.2, 1.0, 0], [1.8, -0.6, 0]]
        smooth = Polygon(*verts, color=GREEN, stroke_width=5)
        smooth.change_anchor_mode("smooth")   # the "mode="smooth"" parameter
        smooth.shift(UP * 0.9 + LEFT * 1.4)
        jagged = Polygon(*verts, color=ORANGE, stroke_width=5)
        jagged.change_anchor_mode("jagged")   # the "mode="jagged"" parameter
        jagged.shift(DOWN * 1.2 + LEFT * 1.4)
        cap1 = Text('mode="smooth"', font_size=20, color=GREEN).next_to(smooth, RIGHT, buff=0.4)
        cap2 = Text('mode="jagged"', font_size=20, color=ORANGE).next_to(jagged, RIGHT, buff=0.4)
        win.play(Create(smooth), FadeIn(cap1), run_time=0.6)   # the smooth mode
        win.play(Create(jagged), FadeIn(cap2), run_time=0.6)   # the corner mode
        win.play(Wait(0.5))   # hold to compare
        win.close()   # close the RTM window


# ===== Sample 9: apply_function —— custom deformation and the about point ===
class ApplyFunctionDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("07b-apply_function", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— per-point distortion: a sine wave changing x ——
        wave = lambda p: p + 0.35 * np.sin(p[1] * PI) * RIGHT   # the "function" parameter: change x point by point
        a = Square(side_length=1.6, color=BLUE).set_fill(BLUE, 0.6).move_to([-3.6, 1.2, 0])
        a.apply_function(wave)   # the "function" parameter
        cap1 = Text("apply_function(wave)", font_size=18, color=GREY_B).next_to(a, DOWN, buff=0.25)
        win.play(Create(a), FadeIn(cap1), run_time=0.5)   # the square is twisted into a wavy edge

        # —— scale everything up: p * 1.5 ——
        b = Square(side_length=1.2, color=GREEN).set_fill(GREEN, 0.6).move_to([1.2, 1.2, 0])
        b.apply_function(lambda p: p * 1.5)   # the "function" parameter: a uniform scale
        cap2 = Text("function = p * 1.5", font_size=18, color=GREY_B).next_to(b, DOWN, buff=0.25)
        win.play(Create(b), FadeIn(cap2), run_time=0.5)   # the whole square gets bigger

        # —— scale + translate: p * 0.8 + UP * 0.4 ——
        c = Square(side_length=1.2, color=RED).set_fill(RED, 0.6).move_to([1.2, -1.4, 0])
        c.apply_function(lambda p: p * 0.8 + UP * 0.4)   # the "function" parameter: scale and then shift the whole thing up
        cap3 = Text("function = p * 0.8 + UP * 0.4", font_size=18, color=GREY_B).next_to(c, DOWN, buff=0.25)
        win.play(Create(c), FadeIn(cap3), run_time=0.5)   # shrunk and moved up

        # —— change only one coordinate: squash y ——
        d = Square(side_length=1.2, color=PURPLE).set_fill(PURPLE, 0.6).move_to([4.2, -1.4, 0])
        d.apply_function(lambda p: p * [1.0, 0.5, 1.0])   # the "function" parameter: squash y only
        cap4 = Text("function = p * [1, 0.5, 1]", font_size=18, color=GREY_B).next_to(d, DOWN, buff=0.25)
        win.play(Create(d), FadeIn(cap4), run_time=0.5)   # the square is squashed
        win.play(Wait(0.5))   # hold to compare
        win.close()   # close the RTM window


SCENES = [
    ("opacity", OpacityDemo),
    ("sheen", SheenDemo),
    ("smooth", MakeSmoothDemo),
    ("jagged", MakeJaggedDemo),
    ("partial", PartialDemo),
    ("strokewidth", GetWidthDemo),
    ("capstyle", CapStyleDemo),
    ("anchor", AnchorModeDemo),
    ("applyfunc", ApplyFunctionDemo),
]

PAIRS = [
    ("opacity", ["opacity"]),
    ("sheen", ["sheen"]),
    ("smooth", ["smooth"]),
    ("jagged", ["jagged"]),
    ("partial", ["partial"]),
    ("strokewidth", ["strokewidth"]),
    ("capstyle", ["capstyle"]),
    ("anchor", ["anchor"]),
    ("applyfunc", ["applyfunc"]),
]

PAGE = "07b-VMobject-Styles-Advanced"


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
