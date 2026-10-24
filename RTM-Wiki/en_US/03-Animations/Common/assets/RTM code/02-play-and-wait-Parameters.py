"""RTM-Wiki · 03-Animations/Common/02-play-and-wait-Parameters — page-specific sample

Demonstrated parameters (each row of the page's "Parameters" tables):
    win.play(*anims)                                    ✓ several animation objects in one play
    win.play(..., run_time=1.6)                         ✓ play-level keyword setattr'd onto each animation
    win.play(..., rate_func=linear)                     ✓ same (rate function)
    win.play(*[FadeIn(m) for m in dots])                ✓ list/generator unpacked into several animations
    win.play(Wait(1.2))  ≡  Scene.wait(duration=1.2)    ✓ duration
Not demonstrated: subcaption / subcaption_duration / subcaption_offset — the three parameters are wired up
    (see the page's "2026-10-16 update" and 01-Scenes-and-Cameras/Scenes/04-Subcaptions-and-Sound), not
    demonstrated here; Scene.pause / Scene.wait_until and Wait's stop_condition / frozen_frame — all
    supported, demonstrated in 01-Scenes-and-Cameras/Scenes/03-Play-and-Wait; play-level lag_ratio — RTM's
    win.play only overrides the two keywords run_time / rate_func, so write staggering on the animation
    constructor or AnimationGroup.
Run: python "<this file>"  (the script puts the repo root on sys.path itself)
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    BLUE,
    DOWN,
    GREEN,
    GREY_B,
    LEFT,
    ORANGE,
    PURPLE,
    RED,
    RIGHT,
    UP,
    YELLOW,
    Circle,
    Dot,
    Scene,
    Square,
    Text,
    Triangle,
    VGroup,
    linear,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    Create,
    FadeIn,
    FadeOut,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_02_play_and_wait_Parameters(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # params w / h / hidden
        win.scene = self                          # param win.scene

        title = Text("02-Scene.play / wait parameters (win.play equivalent)", font_size=42, color=YELLOW).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        # —— Step 1: one play with several animations + play-level run_time / rate_func ——
        l1 = Text("win.play(Create(sq), FadeIn(ci, scale=0.5),", font_size=30, color=GREY_B)
        l2 = Text("         run_time=1.6, rate_func=linear)   # setattr on each", font_size=30, color=GREY_B)
        sig1 = VGroup(l1, l2).arrange(DOWN, buff=0.06).to_edge(UP).shift(DOWN * 1.05)
        sq = Square(side_length=1.3, color=BLUE).set_fill(BLUE, 0.5).shift(LEFT * 2.4 + DOWN * 2.0)
        ci = Circle(radius=0.68, color=GREEN).set_fill(GREEN, 0.5).shift(RIGHT * 2.4 + DOWN * 2.0)
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.4)
        win.play(
            Create(sq),                          # param *anims: Create
            FadeIn(ci, scale=0.5),               # param *anims: FadeIn(scale)
            run_time=1.6,                        # param **kwargs: run_time (both animations stretched to 1.6s)
            rate_func=linear,                    # param **kwargs: rate_func
        )
        win.play(FadeOut(VGroup(sig1, sq, ci)), run_time=0.4)

        # —— Step 2: unpacking a list: win.play(*[FadeIn(m) for m in dots]) ——
        l3 = Text("win.play(*[FadeIn(m, shift=DOWN) for m in dots])",
                  font_size=30, color=GREY_B).to_edge(UP).shift(DOWN * 1.05)
        cols = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]
        dots = VGroup(*[Dot(radius=0.16, color=c).shift(LEFT * 5 + RIGHT * 2 * i + DOWN * 1.9)
                        for i, c in enumerate(cols)])
        win.play(FadeIn(l3, shift=DOWN), run_time=0.4)
        win.play(*[FadeIn(m, shift=DOWN) for m in dots])          # param *anims (list/generator unpacked)
        win.play(Wait(0.4))
        win.play(FadeOut(VGroup(l3, dots)), run_time=0.4)

        # —— Step 3: Wait(duration): ≈ Scene.wait(duration) ——
        l4 = Text("win.play(Wait(1.2))   #  ≡  self.wait(1.2)", font_size=30, color=GREY_B)
        l4.to_edge(UP).shift(DOWN * 1.05)
        tr = Triangle(color=ORANGE).scale(0.8).set_fill(ORANGE, 0.5).shift(DOWN * 1.9)
        txt = Text("still for 1.2 seconds", font_size=30, color=GREY_B).next_to(tr, DOWN, buff=0.45)
        win.play(FadeIn(l4, shift=DOWN), FadeIn(tr), FadeIn(txt), run_time=0.4)
        win.play(Wait(1.2))                                        # param duration=1.2
        win.play(Wait(0.4))

        win.play(FadeOut(VGroup(title, l4, tr, txt)), run_time=0.6)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_02_play_and_wait_Parameters,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "02-play-and-wait-Parameters.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
