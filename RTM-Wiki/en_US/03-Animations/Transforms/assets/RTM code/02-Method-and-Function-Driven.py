"""RTM-Wiki · 03-Animations/Transforms/02-Method-and-Function-Driven — page-specific sample

Demonstrated parameters (each row of the page's "Parameters" tables):
    ApplyMethod(method, *args, **kwargs)
        ✓ method=m.shift (a bound method) plus the positional argument RIGHT * 4.5
        ✓ a dict in the last position is treated as the method's keyword arguments: ApplyMethod(m.scale, 1.5, {'about_edge': UP})
        ✓ **kwargs forwarding: run_time / path_arc / rate_func
    ApplyFunction(function, mobject, **kwargs)
        ✓ function=lambda m: m.scale(0.6).set_color(RED) (copy -> new object)
    ApplyPointwiseFunction(function, mobject, run_time=3.0, **kwargs)
        ✓ function=lambda p: p + 0.5 * sin(p[1] * 2) * RIGHT (every point moves on its own; the square turns into a wave)
        ✓ run_time=1.5 (explicitly overriding the default 3.0)

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
    RED,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Scene,
    Square,
    Text,
    VGroup,
    smooth,
)
# ApplyMethod / ApplyFunction / ApplyPointwiseFunction are not in RTM's export list;
# import them from real_time_manim (= the bundled native ManimCE version); tested and win.play plays them fine
from real_time_manim import ApplyFunction, ApplyMethod, ApplyPointwiseFunction
from real_time_manim.vulkan_bind import (
    MLWindow,
    Create,
    FadeIn,
    FadeOut,
    Wait,  # noqa: F401
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_02_Method_and_Function_Driven(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # params w / h / hidden
        win.scene = self                          # param win.scene

        title = Text("Method / function-driven transforms", font_size=44, color=ORANGE).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        m = Square(side_length=1.6, color=BLUE).set_fill(BLUE, 0.6).move_to(LEFT * 4.0 + DOWN * 1.2)

        # --- 1. ApplyMethod: a bound method + a positional argument + **kwargs ---
        lab1 = VGroup(
            Text("ApplyMethod(m.shift, RIGHT * 4.5,", font_size=30, color=GREY_B),
            Text("            run_time=1.1, path_arc=0.6)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)
        win.play(Create(m), run_time=0.5)
        win.play(                                   # "calling a method" turned into an animation
            ApplyMethod(m.shift, RIGHT * 4.5,       # params method + *args ✓ (bound method + positional argument)
                        run_time=1.1,               # param run_time ✓
                        path_arc=0.6,               # param path_arc ✓ (**kwargs forwarded to Transform)
                        rate_func=smooth),          # param rate_func ✓
            run_time=1.1,
        )
        win.play(FadeOut(lab1), run_time=0.45)

        # --- 2. ApplyMethod: a dict in the last *args slot is treated as the method's keyword arguments ---
        lab2 = Text("ApplyMethod(m.scale, 1.5, {'about_edge': UP})",
                    font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)
        win.play(                                   # scale with the top edge fixed (about_edge=UP applies only to the copy)
            ApplyMethod(m.scale, 1.5, {'about_edge': UP}, run_time=1.0),
            run_time=1.0,
        )
        win.play(FadeOut(lab2), run_time=0.45)

        # --- 3. ApplyPointwiseFunction: every point goes its own way ---
        lab3 = VGroup(
            Text("ApplyPointwiseFunction(lambda p: p +", font_size=30, color=GREY_B),
            Text("  0.5 * np.sin(p[1] * 2) * RIGHT, m,", font_size=30, color=GREY_B),
            Text("  run_time=1.5)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.3)
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)
        win.play(                                   # each point shifts horizontally by its own y coordinate -> the square turns into a wave
            ApplyPointwiseFunction(lambda p: p + 0.5 * np.sin(p[1] * 2) * RIGHT, m,
                                   run_time=1.5),    # param run_time ✓ (default 3.0)
            run_time=1.5,
        )
        win.play(FadeOut(lab3), run_time=0.45)

        # --- 4. ApplyFunction: any pure function (copy -> new object) ---
        lab4 = VGroup(
            Text("ApplyFunction(lambda m: m.scale(0.6)", font_size=30, color=GREY_B),
            Text("  .set_color(GREEN), m, run_time=1.1)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        win.play(FadeIn(lab4, shift=DOWN), run_time=0.4)
        win.play(                                   # pure function: takes the copy and returns a new object
            ApplyFunction(lambda m: m.scale(0.6).set_color(GREEN), m, run_time=1.1),
            run_time=1.1,
        )

        win.play(FadeOut(VGroup(title, lab4, m)), run_time=0.6)
        win.close()                                 # param win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(
        Page_02_Method_and_Function_Driven,
        out_path=os.path.join(os.path.dirname(here), "RTM output", "02-Method-and-Function-Driven.mp4"),
        fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True,
    )
