"""RTM-Wiki · 03-Animations/Transforms/03-Saving-State-and-Style-Transform — page-specific sample

Demonstrated parameters (each row of the page's "Parameters" tables):
    Restore(mobject, **kwargs)
        ✓ prerequisite: call sq.save_state() first (otherwise it restores to the default state)
        ✓ sq.animate.set_color(PURPLE).scale(1.8) messes it up
        ✓ Restore(sq, run_time=1.1, rate_func=smooth) puts the saved state back
    ScaleInPlace(mobject, scale_factor, **kwargs)
        ✓ scale_factor=1.8 enlarges / scale_factor=0.6 shrinks (non-default values; plain semantics)
        ✓ run_time / rate_func forwarding

Not demonstrated: none — every visible parameter of the two classes on this page is shown explicitly.

Run: $env:PYTHONPATH="C:\\Users\\begin\\Desktop\\real-time-manim"; python "<this file>"
"""
import os

from real_time_manim import (
    BLUE,
    GREEN,
    GREY_B,
    ORANGE,
    PURPLE,
    DOWN,
    LEFT,
    UP,
    Scene,
    Square,
    Text,
    VGroup,
    smooth,
)
# Restore / ScaleInPlace are not in RTM's export list; import them from real_time_manim with the bundled ManimCE; tested and working
from real_time_manim import Restore, ScaleInPlace
from real_time_manim.vulkan_bind import (
    MLWindow,
    Create,
    FadeIn,
    FadeOut,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_03_Saving_State_and_Style_Transform(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # params w / h / hidden
        win.scene = self                          # param win.scene

        title = Text("Saving state / in-place style", font_size=44, color=ORANGE).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        # --- 1. save_state() + .animate to mess it up ---
        lab1 = VGroup(
            Text("sq.save_state()", font_size=30, color=GREY_B),
            Text("sq.animate.set_color(PURPLE).scale(1.8)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        sq = Square(side_length=1.4, color=BLUE).set_fill(BLUE, 0.6).move_to(LEFT * 3.2 + DOWN * 1.2)
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)
        win.play(Create(sq), run_time=0.5)
        sq.save_state()                            # param save_state() ✓ (the prerequisite for Restore)
        win.play(sq.animate.set_color(PURPLE).scale(1.8), run_time=1.1)   # param .animate ✓
        win.play(FadeOut(lab1), run_time=0.45)

        # --- 2. Restore: go back to the most recent save_state() ---
        lab2 = Text("Restore(sq, run_time=1.2, rate_func=smooth)",
                    font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)
        win.play(Restore(sq, run_time=1.2, rate_func=smooth), run_time=1.2)   # param Restore(mobject) ✓
        win.play(FadeOut(VGroup(lab2, sq)), run_time=0.5)

        # --- 3. ScaleInPlace: in-place scaling, the factor reads plainly ---
        lab3 = VGroup(
            Text("ScaleInPlace(txt, 1.8, run_time=1.0)", font_size=30, color=GREY_B),
            Text("ScaleInPlace(txt, 0.6, run_time=1.0)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        txt = Text("ScaleInPlace", font_size=40, color=GREEN).move_to(DOWN * 1.3)
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)
        win.play(Write(txt), run_time=0.6)
        win.play(ScaleInPlace(txt, 1.8, run_time=1.0, rate_func=smooth), run_time=1.0)   # param scale_factor=1.8 ✓
        win.play(ScaleInPlace(txt, 0.6, run_time=1.0, rate_func=smooth), run_time=1.0)   # param scale_factor=0.6 ✓

        win.play(Wait(0.5))
        win.play(FadeOut(VGroup(title, lab3, txt)), run_time=0.6)
        win.close()                                 # param win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(
        Page_03_Saving_State_and_Style_Transform,
        out_path=os.path.join(os.path.dirname(here), "RTM output", "03-Saving-State-and-Style-Transform.mp4"),
        fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True,
    )
