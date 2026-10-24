"""RTM-Wiki · 03-Animations/Transforms/04-Swapping-and-Copy-Transforms — page-specific sample

Demonstrated parameters (each row of the page's "Parameters" tables):
    Swap(*mobjects, path_arc=90 * DEGREES)
        ✓ Swap(a, b, path_arc=180 * DEGREES): two objects swap along an arc (non-default 90 degrees)
    TransformFromCopy(mobject, target_mobject)
        ✓ the original stays put; the target evolves out of it (a MathTex formula)
    ClockwiseTransform(mobject, target_mobject, path_arc=-np.pi)
        ✓ path_arc=-np.pi (the documented default passed explicitly): the point swaps along a clockwise half-arc
    CounterclockwiseTransform(mobject, target_mobject, path_arc=np.pi)
        ✓ path_arc=np.pi (the documented default passed explicitly): the point swaps along a counterclockwise half-arc
    CyclicReplace(*mobjects, path_arc=90 * DEGREES)
        ✓ three objects rotate into each other's slots, path_arc=90 * DEGREES

Not demonstrated: none — every visible parameter of the five classes on this page is shown explicitly
        (Clockwise/CounterclockwiseTransform pass the documented default ±pi explicitly so that
        the arc is visible to the eye; Swap uses the non-default 180 degrees to prove the parameter can change).

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
    PURPLE,
    RED,
    YELLOW,
    DEGREES,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Dot,
    MathTex,
    Scene,
    Text,
    VGroup,
    smooth,
)
# The five classes below are not in RTM's export list; import them from real_time_manim with the bundled ManimCE; tested and working
from real_time_manim import (
    ClockwiseTransform,
    CounterclockwiseTransform,
    CyclicReplace,
    Swap,
    TransformFromCopy,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeIn,
    FadeOut,
    Wait,  # noqa: F401
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_04_Swapping_and_Copy_Transforms(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # params w / h / hidden
        win.scene = self                          # param win.scene

        title = Text("Swapping / copy transforms", font_size=42, color=ORANGE).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        # --- 1. Swap: two objects swap places along an arc ---
        lab1 = VGroup(
            Text("Swap(a, b, path_arc=180 * DEGREES,", font_size=30, color=GREY_B),
            Text("     run_time=1.2)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        a = Text("A", font_size=52, color=BLUE).move_to(LEFT * 3.5 + DOWN * 1.3)
        b = Text("B", font_size=52, color=GREEN).move_to(RIGHT * 3.5 + DOWN * 1.3)
        self.add(a, b)
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)
        win.play(Swap(a, b, path_arc=180 * DEGREES, run_time=1.2), run_time=1.2)   # params *mobjects / path_arc ✓
        # note: in RTM, objects added to the scene with self.add must each be FadeOut-ed
        #     separately (a VGroup fade only affects members added by a win.play animation), so here they are faded out one by one.
        win.play(FadeOut(lab1), FadeOut(a), FadeOut(b), run_time=0.5)

        # --- 2. TransformFromCopy: the original stays, the target evolves out ---
        lab2 = Text("TransformFromCopy(eq1, eq2, run_time=1.2, rate_func=smooth)",
                    font_size=28, color=GREY_B).next_to(title, DOWN, buff=0.4)
        eq1 = MathTex("x = 1").move_to(LEFT * 3.2 + DOWN * 1.3)
        eq2 = MathTex("x^2 = 1").move_to(RIGHT * 3.2 + DOWN * 1.3)
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)
        win.play(Write(eq1), run_time=0.6)
        win.play(TransformFromCopy(eq1, eq2, run_time=1.2, rate_func=smooth), run_time=1.2)   # param ✓ (the original stays)
        win.play(FadeOut(lab2), FadeOut(eq1), FadeOut(eq2), run_time=0.5)

        # --- 3. ClockwiseTransform: the point swaps along a clockwise half-arc ---
        lab3 = Text("ClockwiseTransform(p, q.copy(), path_arc=-np.pi)",
                    font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)
        p = Dot(radius=0.16, color=YELLOW).move_to(LEFT * 3.2 + DOWN * 1.3)
        q = Dot(radius=0.16, color=ORANGE).move_to(RIGHT * 3.2 + DOWN * 1.3)
        self.add(p, q)
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)
        win.play(ClockwiseTransform(p, q.copy(), path_arc=-np.pi, run_time=1.2), run_time=1.2)   # param path_arc ✓
        win.play(FadeOut(lab3), FadeOut(p), FadeOut(q), run_time=0.5)

        # --- 4. CounterclockwiseTransform: swap along a counterclockwise half-arc (opposite direction to (3)) ---
        lab4 = VGroup(
            Text("CounterclockwiseTransform(p2, q2.copy(),", font_size=30, color=GREY_B),
            Text("                           path_arc=np.pi)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        p2 = Dot(radius=0.16, color=RED).move_to(LEFT * 3.2 + DOWN * 1.3)
        q2 = Dot(radius=0.16, color=PURPLE).move_to(RIGHT * 3.2 + DOWN * 1.3)
        self.add(p2, q2)
        win.play(FadeIn(lab4, shift=DOWN), run_time=0.4)
        win.play(CounterclockwiseTransform(p2, q2.copy(), path_arc=np.pi, run_time=1.2), run_time=1.2)   # param ✓
        win.play(FadeOut(lab4), FadeOut(p2), FadeOut(q2), run_time=0.5)

        # --- 5. CyclicReplace: three objects rotate into each other's slots ---
        lab5 = VGroup(
            Text("CyclicReplace(c1, c2, c3,", font_size=30, color=GREY_B),
            Text("              path_arc=90 * DEGREES, run_time=1.4)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        c1 = Text("1", font_size=48, color=BLUE).move_to(LEFT * 3.5 + DOWN * 1.3)
        c2 = Text("2", font_size=48, color=GREEN).move_to(DOWN * 1.3)
        c3 = Text("3", font_size=48, color=ORANGE).move_to(RIGHT * 3.5 + DOWN * 1.3)
        self.add(c1, c2, c3)
        win.play(FadeIn(lab5, shift=DOWN), run_time=0.4)
        win.play(CyclicReplace(c1, c2, c3, path_arc=90 * DEGREES, run_time=1.4), run_time=1.4)   # param ✓

        win.play(FadeOut(title), FadeOut(lab5),
                 FadeOut(c1), FadeOut(c2), FadeOut(c3), run_time=0.6)
        win.close()                                 # param win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(
        Page_04_Swapping_and_Copy_Transforms,
        out_path=os.path.join(os.path.dirname(here), "RTM output", "04-Swapping-and-Copy-Transforms.mp4"),
        fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True,
    )
