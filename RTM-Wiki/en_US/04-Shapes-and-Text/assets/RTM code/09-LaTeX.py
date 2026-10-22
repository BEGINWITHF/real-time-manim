# -*- coding: utf-8 -*-
"""Full source for the three samples in 09-LaTeX.md (identical to the code blocks in the page).

Usage: python 09-LaTeX.py <sample names>...
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
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    Scene, Tex, MathTex, SingleStringMathTex, Text,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


def cap(text, mob, buff=0.35, color=GREY_B, size=18):
    return Text(text, font_size=size, color=color).next_to(mob, DOWN, buff=buff)


# ===== Sample 1: Tex —— mixing body text and formulas =====================
class TexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("09-Tex", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— default: write formulas in $...$ inside body text; font_size controls the overall size ——
        t1 = Tex(r"The area is $A = \pi r^2$.", font_size=40).move_to([0, 1.5, 0])   # the "*tex_strings / font_size" parameters
        win.play(Write(t1), FadeIn(cap("Tex(...font_size=40)", t1)), run_time=0.7)

        # —— color: the overall colour (body text and formulas change together) ——
        t2 = Tex(r"$E = mc^2$", font_size=48, color=TEAL).move_to([0, 0.2, 0])   # the "color" parameter
        win.play(Write(t2), FadeIn(cap("color=TEAL", t2)), run_time=0.7)

        # —— tex_environment: switch to a maths environment (document by default) ——
        t3 = Tex(r"a + b = c", font_size=36,
                 tex_environment="align*").move_to([0, -1.4, 0])   # the "tex_environment" parameter
        win.play(Write(t3), FadeIn(cap('tex_environment="align*"', t3)), run_time=0.7)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: MathTex —— pure formulas with splittable parts ===========
class MathTexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("09-MathTex", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— default: each positional argument is one part; a single string may contain several $...$ ——
        m1 = MathTex(r"x^2 + y^2 = z^2", font_size=48).move_to([0, 1.4, 0])   # the "*tex_strings" parameter
        win.play(Write(m1), FadeIn(cap("MathTex(r\"x^2 + y^2 = z^2\")", m1)), run_time=0.8)

        # —— explicit parts: each part is its own unit, handy for colouring one later ——
        m2 = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2", font_size=48).move_to([0, 0.0, 0])   # the "{{ }}" part splitting
        m2[0].set_color(RED)
        m2[2].set_color(GREEN)
        m2[4].set_color(BLUE)
        win.play(Write(m2), FadeIn(cap("each part coloured separately", m2)), run_time=0.8)

        # —— color / font_size: the overall style ——
        m3 = MathTex(r"\int_0^1 x^2\,dx = \frac{1}{3}", font_size=44,
                     color=ORANGE).move_to([0, -1.6, 0])   # the "color / font_size" parameters
        win.play(Write(m3), FadeIn(cap("color=ORANGE, font_size=44", m3)), run_time=0.8)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: SingleStringMathTex —— a single formula string ===========
class SingleStringDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("09-SingleStringMathTex", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— takes a single string only: no part splitting, the lightest formula object ——
        s1 = SingleStringMathTex(r"\sum_{i=1}^{n} i = \frac{n(n+1)}{2}",
                                 font_size=44).move_to([0, 1.2, 0])   # the "tex_string" parameter
        win.play(Write(s1), FadeIn(cap("SingleStringMathTex(sum)", s1)), run_time=0.8)

        # —— difference from MathTex: it has a single part, so you cannot fetch by part ——
        s2 = SingleStringMathTex(r"[a, b] = [c, d]", font_size=44,
                                 color=TEAL).move_to([0, -0.4, 0])
        win.play(Write(s2), FadeIn(cap("one object for the whole string (color=TEAL)", s2)), run_time=0.8)

        # —— change font_size once more to see the scaling ——
        s3 = SingleStringMathTex(r"f(x) = e^{-x^2}", font_size=64).move_to([0, -2.2, 0])
        win.play(Write(s3), FadeIn(cap("font_size=64", s3)), run_time=0.8)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


SCENES = [
    ("tex", TexDemo),
    ("mathtex", MathTexDemo),
    ("singlestring", SingleStringDemo),
]

PAIRS = [
    ("tex", ["tex"]),
    ("mathtex", ["mathtex"]),
    ("singlestring", ["singlestring"]),
]

PAGE = "09-LaTeX"


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
