"""RTM-Wiki · 03-Animations/Transforms/02b-More-Function-Driven — page-specific sample

Demonstrated parameters (each row of the page's "Parameters" tables):
    ApplyPointwiseFunctionToCenter(function, mobject, **kwargs)
        ✓ function=lambda c: c + UP * 2.2 (centre -> new centre); the shape does not change, only the whole object is repositioned
        ✓ run_time=1.2 (explicitly overriding the default 3.0)
    ApplyComplexFunction(function, mobject, **kwargs)
        ✓ function=lambda z: np.exp(z) (a conformal map on the complex plane)
        ✓ run_time=1.5
    ApplyMatrix(matrix, mobject, about_point=ORIGIN, **kwargs)
        ✓ matrix=[[1, 1], [0, 2 / 3]] (a 2x2 shear + vertical compression)
        ✓ about_point=DOWN * 2.6 (a non-default transform origin: shear about the bottom anchor)
        ✓ run_time=1.4

Not demonstrated: none — every visible parameter of the three classes on this page is shown explicitly.

Run: python "<this file>"  (the script puts the repo root on sys.path itself)
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

import numpy as np
from real_time_manim import (
    BLUE,
    GREEN,
    GREY_B,
    ORANGE,
    YELLOW,
    DOWN,
    LEFT,
    ORIGIN,
    UP,
    Dot,
    Scene,
    Square,
    Text,
    VGroup,
    Write,
)
# The three classes below are not in RTM's export list; import them from real_time_manim with the bundled ManimCE; tested and working
# (ApplyPointwiseFunctionToCenter's __init__ is fixed up by real_time_manim.compat at import time)
from real_time_manim import ApplyComplexFunction, ApplyMatrix, ApplyPointwiseFunctionToCenter
from real_time_manim.vulkan_bind import (
    MLWindow,
    Create,
    FadeIn,
    FadeOut,
    Wait,  # noqa: F401
)
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_02b_More_Function_Driven(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # params w / h / hidden
        win.scene = self                          # param win.scene

        title = Text("More function-driven transforms: centre / complex / matrix", font_size=42, color=ORANGE).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        # --- 1. ApplyPointwiseFunctionToCenter: only the centre point changes, the shape stays put ---
        lab1 = VGroup(
            Text("ApplyPointwiseFunctionToCenter(", font_size=30, color=GREY_B),
            Text("  lambda c: c + UP * 2.2, d, run_time=1.2)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        d = Dot(radius=0.16, color=YELLOW).move_to(LEFT * 3.0 + DOWN * 1.5)
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)
        win.play(Create(d), run_time=0.4)
        win.play(                                   # the centre is repositioned by the given rule
            ApplyPointwiseFunctionToCenter(lambda c: c + UP * 2.2, d,
                                           run_time=1.2),   # param run_time ✓ (default 3.0)
            run_time=1.2,
        )
        win.play(FadeOut(VGroup(lab1, d)), run_time=0.5)

        # --- 2. ApplyComplexFunction: a conformal map by a complex function (relative to ORIGIN) ---
        lab2 = VGroup(
            Text("ApplyComplexFunction(lambda z: np.exp(z),", font_size=30, color=GREY_B),
            Text("                     sq, run_time=1.5)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        sq = Square(side_length=2.2, color=GREEN).set_fill(GREEN, 0.5).move_to(ORIGIN + DOWN * 0.6)
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)
        win.play(Create(sq), run_time=0.5)
        win.play(ApplyComplexFunction(lambda z: np.exp(z), sq,   # params function + mobject ✓
                                      run_time=1.5), run_time=1.5)
        win.play(FadeOut(VGroup(lab2, sq)), run_time=0.5)

        # --- 3. ApplyMatrix: a 2x2 linear transform about a custom anchor ---
        lab3 = VGroup(
            Text("ApplyMatrix([[1, 1], [0, 2 / 3]], txt,", font_size=30, color=GREY_B),
            Text("  about_point=DOWN * 2.6, run_time=1.4)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        txt = Text("Hello", font_size=48, color=BLUE).move_to(LEFT * 1.6 + DOWN * 1.0)
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)
        win.play(Write(txt), run_time=0.6)
        win.play(                                   # p' = (p - about_point) @ matrix.T + about_point
            ApplyMatrix([[1, 1], [0, 2 / 3]], txt,   # param matrix ✓ (2x2 is padded to 3x3 automatically)
                        about_point=DOWN * 2.6,      # param about_point ✓ (non-default ORIGIN)
                        run_time=1.4),               # param run_time ✓ (default 3.0)
            run_time=1.4,
        )

        win.play(FadeOut(VGroup(title, lab3, txt)), run_time=0.6)
        win.close()                                 # param win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(
        Page_02b_More_Function_Driven,
        out_path=os.path.join(os.path.dirname(here), "RTM output", "02b-More-Function-Driven.mp4"),
        fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True,
    )
