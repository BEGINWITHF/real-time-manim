# -*- coding: utf-8 -*-
"""Full source for the three samples in 10-Typst.md (identical to the code blocks in the page).

Usage: python 10-Typst.py <sample names>...
With no arguments it renders every sample and concatenates the page's three sample videos (written to assets/RTM output/).
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
    Scene, Typst, TypstMath, MathTex, Text,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


def cap(text, mob, buff=0.35, color=GREY_B, size=18):
    return Text(text, font_size=size, color=color).next_to(mob, DOWN, buff=buff)


# ===== Sample 1: Typst —— typesetting text / formulas with Typst ==========
class TypstDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("10-Typst", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— default: font_size=48, centred; Typst syntax ($...$ holds maths) ——
        t1 = Typst("The area is $pi r^2$", font_size=40).move_to([0, 1.4, 0])   # the "typst_code / font_size" parameters
        win.play(Write(t1), FadeIn(cap("Typst(...font_size=40)", t1)), run_time=0.7)

        # —— color / stroke_width: overall colour and stroke ——
        t2 = Typst("bold text #text(fill: red)[red]", font_size=40,
                   color=TEAL, stroke_width=1).move_to([0, -0.2, 0])   # the "color / stroke_width" parameters
        win.play(Write(t2), FadeIn(cap("color=TEAL, stroke_width=1", t2)), run_time=0.7)

        # —— typst_preamble: prepend definitions to the whole block (here defining a colour) ——
        t3 = Typst("#let hot = rgb(\"#ff6600\")\nA #text(fill: hot)[hot] word",
                   font_size=36, typst_preamble='#set text(size: 12pt)')   # the "typst_preamble" parameter
        t3.move_to([0, -1.8, 0])
        win.play(Write(t3), FadeIn(cap("typst_preamble definitions", t3)), run_time=0.7)

        # —— should_center / height: not centred, scaled by height ——
        t4 = Typst("H", font_size=72, should_center=False, height=1.2)   # the "should_center / height" parameters
        t4.move_to([4.6, 1.4, 0])
        win.play(Write(t4), FadeIn(cap("height=1.2", t4)), run_time=0.6)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: TypstMath —— writing just a maths expression =============
class TypstMathDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("10-TypstMath", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— default: write the expression directly (it is wrapped in $ ... $ automatically) ——
        m1 = TypstMath("sum_(i=1)^n i = (n(n+1))/2", font_size=44).move_to([0, 1.4, 0])   # the "math_expression" parameter
        win.play(Write(m1), FadeIn(cap("TypstMath(sum formula)", m1)), run_time=0.8)

        # —— the remaining parameters pass through to Typst: color / font_size ——
        m2 = TypstMath("integral_0^1 x^2 dif x = 1/3", font_size=44,
                       color=ORANGE).move_to([0, -0.4, 0])   # the "**kwargs (color)" parameter
        win.play(Write(m2), FadeIn(cap("color=ORANGE", m2)), run_time=0.8)

        # —— fractions / square roots / matrices ——
        m3 = TypstMath("mat(1, 2; 3, 4)", font_size=40).move_to([-3.4, -2.2, 0])
        m4 = TypstMath("sqrt(2) approx 1.414", font_size=40).move_to([2.6, -2.2, 0])
        win.play(Write(m3), FadeIn(cap("mat(1, 2; 3, 4)", m3)), run_time=0.7)
        win.play(Write(m4), FadeIn(cap("sqrt(2)", m4)), run_time=0.7)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: automatic routing —— MathTex goes through Typst under RTM =
class AutoRouteDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("10-Typst autoroute", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— MathTex writes LaTeX as usual; RTM converts it to Typst typesetting internally (no local LaTeX needed) ——
        mt = MathTex(r"\frac{a}{b} + \sqrt{x}").move_to([0, 1.0, 0])   # the "MathTex (automatic routing)" parameter
        win.play(Write(mt), FadeIn(cap("MathTex(\\frac{a}{b}+\\sqrt{x})", mt)), run_time=0.8)

        # —— the same formula written with TypstMath, same shape and position ——
        tm = TypstMath("a/b + sqrt(x)", font_size=48).move_to([0, -0.6, 0])
        win.play(Write(tm), FadeIn(cap("TypstMath(a/b + sqrt(x))", tm)), run_time=0.8)

        # —— MathTex's part-colouring and other interfaces still work as usual ——
        mt2 = MathTex(r"E = mc^2").move_to([0, -2.2, 0])
        mt2[0].set_color(YELLOW)
        win.play(Write(mt2), FadeIn(cap("MathTex part colouring as usual", mt2)), run_time=0.8)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


SCENES = [
    ("typst", TypstDemo),   # RTM-only
    ("typstmath", TypstMathDemo),   # RTM-only
    ("autoroute", AutoRouteDemo),   # RTM-only
]

PAIRS = [
    ("typst", ["typst"]),   # RTM-only
    ("typstmath", ["typstmath"]),   # RTM-only
    ("autoroute", ["autoroute"]),   # RTM-only
]

PAGE = "10-Typst"


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
