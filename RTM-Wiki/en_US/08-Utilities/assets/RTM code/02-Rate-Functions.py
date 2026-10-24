# -*- coding: utf-8 -*-
"""Full source of the three samples in 02-Rate-Functions.md (identical to the code blocks in the page).

Usage: python 02-Rate-Functions.py <clip name>...
With no arguments it renders every clip and concatenates the page's three sample videos (output to the parent assets/).
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
    Scene, Text, VGroup, Line, Dot, Arrow, Rectangle, FunctionGraph,
    BLUE, GREEN, RED, YELLOW, TEAL, PURPLE, GREY_B,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, Write, Create,
)
from real_time_manim import rate_functions
from real_time_manim import (
    exponential_decay, linear, lingering, rush_from, rush_into,
    smooth, squish_rate_func, there_and_back, wiggle,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: curves of the common rate functions ========================
class RateCurveCommonDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("02-common rate_funcs", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        x0, x1, y0, y1 = -6.0, 2.6, -2.4, 1.8   #plot area: t left to right, f(t) bottom to top
        lo, hi = -0.05, 1.05   #vertical display range (5% margin at each end)

        def plot(f, color):   #draw a rate function as a curve: map screen x back to t, then map f(t) into the plot area
            def g(u):
                t = (u - x0) / (x1 - x0)   #screen x → progress t
                y = f(t)   #actual progress given by the rate function
                if y < lo:
                    y = lo   #clamp out-of-range values (wiggle in sample 2 overshoots 0-1)
                elif y > hi:
                    y = hi
                return y0 + (y - lo) / (hi - lo) * (y1 - y0)   #map to a scene y coordinate
            return FunctionGraph(g, x_range=[x0, x1, (x1 - x0) / 96], color=color, stroke_width=5)

        xax = Arrow([x0 - 0.3, y0, 0], [x1 + 0.4, y0, 0], color=GREY_B, stroke_width=4, buff=0)   #x-axis: progress t
        yax = Arrow([x0, y0 - 0.3, 0], [x0, y1 + 0.35, 0], color=GREY_B, stroke_width=4, buff=0)   #y-axis: actual progress f(t)
        lt = Text("t", font_size=22, color=GREY_B).next_to(xax, DOWN, buff=0.12)   #x-axis name
        lf = Text("f(t)", font_size=22, color=GREY_B).next_to(yax, UP, buff=0.12)   #y-axis name
        l0 = Text("0", font_size=18, color=GREY_B).next_to([x0, y0, 0], DOWN, buff=0.15)   #origin tick
        l1t = Text("1", font_size=18, color=GREY_B).next_to([x1, y0, 0], DOWN, buff=0.15)   #t=1 tick
        l1f = Text("1", font_size=18, color=GREY_B).next_to([x0, y1, 0], LEFT, buff=0.15)   #f(t)=1 tick
        win.play(FadeIn(VGroup(xax, yax, lt, lf, l0, l1t, l1f)), run_time=0.4)   #axes position first

        names = ["linear", "smooth", "rush_into", "rush_from"]   #four common rate functions
        funcs = [linear, smooth, rush_into, rush_from]
        cols = [GREY_B, BLUE, GREEN, RED]
        for i, (nm, f, c) in enumerate(zip(names, funcs, cols)):
            g = plot(f, c)   #the i-th curve
            lab = Text(nm, font_size=17, color=c).move_to([3.2, 1.2 - i * 0.8, 0])   #same-color legend on the right
            win.play(Create(g), run_time=0.6)   #draw each curve in turn
            win.play(FadeIn(lab), run_time=0.2)   #then add its name
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window


# ===== Sample 2: factory / back-and-forth / standard easing curves =========
class RateCurveFactoryDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("02-squish / wiggle / ease", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        x0, x1, y0, y1 = -6.0, 2.6, -2.4, 1.8   #plot area
        lo, hi = -1.1, 1.4   #this group overshoots 0-1 (wiggle oscillates, ease pulls back), so widen the range

        def ypos(v):   #convert an f value to a scene y coordinate (for tick labels)
            return y0 + (v - lo) / (hi - lo) * (y1 - y0)

        def plot(f, color):   #likewise draw a rate function as a curve
            def g(u):
                t = (u - x0) / (x1 - x0)   #screen x → progress t
                y = f(t)   #actual progress given by the rate function
                if y < lo:
                    y = lo   #clamp to the display bounds
                elif y > hi:
                    y = hi
                return ypos(y)
            return FunctionGraph(g, x_range=[x0, x1, (x1 - x0) / 96], color=color, stroke_width=5)

        xax = Arrow([x0 - 0.3, y0, 0], [x1 + 0.4, y0, 0], color=GREY_B, stroke_width=4, buff=0)   #x-axis: progress t
        yax = Arrow([x0, y0 - 0.3, 0], [x0, y1 + 0.35, 0], color=GREY_B, stroke_width=4, buff=0)   #y-axis: actual progress f(t)
        lt = Text("t", font_size=22, color=GREY_B).next_to(xax, DOWN, buff=0.12)   #x-axis name
        lf = Text("f(t)", font_size=22, color=GREY_B).next_to(yax, UP, buff=0.12)   #y-axis name
        ticks = VGroup(*[Text(v, font_size=17, color=GREY_B).next_to([x0, ypos(float(v)), 0], LEFT, buff=0.15)
                         for v in ("1", "0", "-1")])   #three y-axis ticks: 1 top, 0 middle, -1 bottom
        l1t = Text("1", font_size=18, color=GREY_B).next_to([x1, y0, 0], DOWN, buff=0.15)   #t=1 tick
        win.play(FadeIn(VGroup(xax, yax, lt, lf, ticks, l1t)), run_time=0.4)   #axes position first

        names = ["squish(smooth, .2, .8)", "wiggle(t, 3)", "lingering", "ease_out_bounce"]   #four "decorated" rate functions
        funcs = [squish_rate_func(smooth, 0.2, 0.8), lambda t: wiggle(t, 3),
                 lingering, rate_functions.ease_out_bounce]
        cols = [PURPLE, RED, YELLOW, TEAL]
        for i, (nm, f, c) in enumerate(zip(names, funcs, cols)):
            g = plot(f, c)   #the i-th curve
            lab = Text(nm, font_size=16, color=c).move_to([3.4, 1.2 - i * 0.8, 0])   #same-color legend on the right
            win.play(Create(g), run_time=0.6)   #draw each curve in turn
            win.play(FadeIn(lab), run_time=0.2)   #then add its name
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window


# ===== Sample 3: one movement × four rates ==================================
class RateMotionDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("02-rate_func on a shift", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        names = ["linear", "smooth", "rush_into", "there_and_back"]   #one rate per lane
        funcs = [linear, smooth, rush_into, there_and_back]
        cols = [GREY_B, BLUE, GREEN, RED]
        xs0, xs1 = -2.4, 6.0   #start and end of the movement track (identical for all four)
        mx0, mx1 = -5.0, -3.0   #horizontal extent of the small curve box on the left
        lanes, dots = [], []
        for i, (nm, f, c) in enumerate(zip(names, funcs, cols)):
            y = 1.9 - i * 1.2   #y coordinate of each lane
            box = Rectangle(width=mx1 - mx0, height=1.0, stroke_width=1)
            box.set_stroke(GREY_B, 1, opacity=0.5).set_fill(opacity=0)   #hollow little box as the plot area
            box.move_to([(mx0 + mx1) / 2, y, 0])
            lab = Text(nm, font_size=15, color=c).next_to(box, LEFT, buff=0.25)   #lane name to the left of the curve box

            def g(u, f=f):   #draw this lane's rate function into the box (x 0→1, y 0→1)
                t = (u - mx0) / (mx1 - mx0)
                v = f(t)
                v = 0.0 if v < 0.0 else (1.0 if v > 1.0 else v)   #clamp out-of-range values to the box edge
                return y + (v - 0.5) * 0.8   #f=0 → box bottom, f=1 → box top

            curve = FunctionGraph(g, x_range=[mx0, mx1, (mx1 - mx0) / 40],
                                  color=c, stroke_width=3)   #thumbnail of this lane's rate curve
            trk = Line([xs0, y, 0], [xs1, y, 0], color=GREY_B, stroke_width=2)
            trk.set_stroke(opacity=0.4)   #movement track (translucent grey line)
            dot = Dot([xs0, y, 0], radius=0.13, color=c)   #starting dot, same color as the curve
            lanes += [box, lab, curve, trk]
            dots.append((dot, y, f))
        note = Text("same shift, only rate_func differs", font_size=19, color=YELLOW).to_edge(DOWN)   #bottom note
        win.play(FadeIn(VGroup(*lanes)), FadeIn(note), run_time=0.5)   #the four lanes and the note settle into place
        self.add(*[d for d, _, _ in dots])   #add the four dots to the scene (all start at the left end of the track)
        win.play(*[d.animate(run_time=1.6, rate_func=f).move_to([xs1, y, 0])
                   for d, y, f in dots])   #the "rate_func" parameter: one movement × four rates starting together
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window


SCENES = [
    ("curves_common", RateCurveCommonDemo),
    ("curves_factory", RateCurveFactoryDemo),
    ("motion", RateMotionDemo),
]

PAIRS = [
    ("curves_common", ["curves_common"]),
    ("curves_factory", ["curves_factory"]),
    ("motion", ["motion"]),
]

PAGE = "02-Rate-Functions"


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
