"""RTM-Wiki · 03-Animations/Growth/01b-Arrows-and-Spin-In -- sample dedicated to this page

Demonstrated parameters (one by one from the page's Parameters table):
    GrowArrow(arrow, point_color=RED, run_time=1.7)  ✓
    SpinInFromNothing(mobject, angle=2*PI, point_color=BLUE, run_time=1.9)  ✓
    SpinInFromNothing(mobject, angle=PI/2, point_color=None, run_time=1.5)  ✓ default angle for comparison
Not demonstrated: point_color=None as a step of its own (the default = keeps the object's own colour, no different from not passing it);
    path_func in **kwargs is occupied by spiral_path(angle) and cannot be passed separately.
Run: python "<this file>"  (the script puts the repo root on sys.path itself)
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    BLUE,
    GOLD,
    GREY_B,
    PURPLE,
    RED,
    YELLOW,
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    PI,
    Arrow,
    Circle,
    Scene,
    Star,
    Text,
    VGroup,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeIn,
    FadeOut,
    GrowArrow,
    SpinInFromNothing,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_01b_Arrows_and_Spin_In(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # parameter w=1280 / h=720 / hidden=True
        win.scene = self

        title = Text("Grow: GrowArrow / SpinInFromNothing", font_size=42, color=YELLOW).to_edge(UP)
        win.play(Write(title, run_time=0.8), run_time=0.8)

        # --- 1. GrowArrow: the arrow grows from its start towards its tip ---
        l1 = Text("GrowArrow(arrow, point_color=RED, run_time=1.7)",
                  font_size=32, color=GREY_B).next_to(title, DOWN, buff=0.5)
        arr = Arrow(ORIGIN + LEFT * 3.2 + DOWN * 1.0, ORIGIN + RIGHT * 1.2 + DOWN * 1.0,
                    buff=0, color=GOLD, stroke_width=6).next_to(l1, DOWN, buff=0.9).shift(LEFT * 1.0)
        win.play(FadeIn(l1, shift=DOWN), run_time=0.4)
        win.play(
            GrowArrow(arr,                          # parameter arrow
                      point_color=RED,              # parameter point_color=RED (reddish at the start, back to gold as it grows)
                      run_time=1.7),                # parameter **kwargs(run_time)
            run_time=1.7,
        )
        win.play(FadeOut(VGroup(l1, arr)), run_time=0.5)

        # --- 2. SpinInFromNothing: grow while rotating (angle not the default: an extra full turn) ---
        l2 = Text("SpinInFromNothing(mobject, angle=2*PI, point_color=BLUE)",
                  font_size=32, color=GREY_B).next_to(title, DOWN, buff=0.5)
        star = Star(n=5, outer_radius=1.0, color=PURPLE).next_to(l2, DOWN, buff=0.8).shift(LEFT * 2.2)
        win.play(FadeIn(l2, shift=DOWN), run_time=0.4)
        win.play(
            SpinInFromNothing(                      # parameter mobject
                star,
                angle=2 * PI,                       # parameter angle=2*PI (an extra full turn while growing)
                point_color=BLUE,                   # parameter point_color=BLUE
                run_time=1.9),                      # parameter **kwargs(run_time)
            run_time=1.9,
        )
        # contrast: the small turn at the default angle PI/2
        l3 = Text("SpinInFromNothing(mobject, angle=PI/2)   # default angle for comparison",
                  font_size=32, color=GREY_B).next_to(l2, DOWN, buff=1.9).shift(RIGHT * 2.4)
        ci = Circle(radius=0.6, color=GREY_B).next_to(l3, DOWN, buff=0.6)
        win.play(FadeIn(VGroup(l3, ci), shift=DOWN), run_time=0.4)
        win.play(
            SpinInFromNothing(                      # parameter mobject
                ci,
                angle=PI / 2,                       # parameter angle=PI/2 (= the default, only 90°)
                run_time=1.5),                      # parameter **kwargs(run_time)
            run_time=1.5,
        )

        win.play(Wait(0.5))
        win.play(FadeOut(VGroup(title, star, l3, ci)), run_time=0.6)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(
        Page_01b_Arrows_and_Spin_In,
        out_path=os.path.join(os.path.dirname(here), "RTM output", "01b-Arrows-and-Spin-In.mp4"),
        fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
