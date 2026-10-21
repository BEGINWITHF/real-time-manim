"""RTM-Wiki · 03-Animations/Transforms/03b-Shrink-and-Recolor — page-specific sample

Demonstrated parameters (each row of the page's "Parameters" tables):
    ShrinkToCenter(mobject, **kwargs)
        ✓ ShrinkToCenter(word, run_time=1.4, rate_func=smooth) shrinks into the centre
        ✓ when done the object is still in the scene (just invisible) - to truly remove it, call self.remove(...) by hand
    FadeToColor(mobject, color, **kwargs)
        ✓ color=RED -> color=YELLOW, two fades (non-default target colours)
        ✓ run_time / rate_func forwarding

Not demonstrated: none — every visible parameter of the two classes on this page is shown explicitly.

Run: $env:PYTHONPATH="C:\\Users\\begin\\Desktop\\real-time-manim"; python "<this file>"
"""
import os

from real_time_manim import (
    GREY_B,
    ORANGE,
    RED,
    WHITE,
    YELLOW,
    DOWN,
    LEFT,
    UP,
    Scene,
    Text,
    VGroup,
    smooth,
)
# ShrinkToCenter / FadeToColor are not in RTM's export list; import them from real_time_manim with the bundled ManimCE; tested and working
from real_time_manim import FadeToColor, ShrinkToCenter
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeIn,
    FadeOut,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_03b_Shrink_and_Recolor(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # params w / h / hidden
        win.scene = self                          # param win.scene

        title = Text("ShrinkToCenter / FadeToColor", font_size=40, color=ORANGE).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        # --- 1. ShrinkToCenter: shrink to 0, collapsing into the centre ---
        lab1 = Text("ShrinkToCenter(word, run_time=1.4, rate_func=smooth)",
                    font_size=28, color=GREY_B).next_to(title, DOWN, buff=0.4)
        word = Text("Bye", font_size=48, color=YELLOW).move_to(LEFT * 2.0 + DOWN * 1.4)
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)
        win.play(Write(word), run_time=0.8)
        win.play(ShrinkToCenter(word, run_time=1.4, rate_func=smooth), run_time=1.4)   # param ShrinkToCenter ✓
        self.remove(word)      # note: ShrinkToCenter is not a remover; when done the object is still in the scene (just invisible)
        win.play(FadeOut(lab1), run_time=0.45)

        # --- 2. FadeToColor: fade the colour to a given colour (showing two different target colours) ---
        lab2 = VGroup(
            Text("FadeToColor(msg, RED, run_time=1.2)", font_size=30, color=GREY_B),
            Text("FadeToColor(msg, YELLOW, run_time=1.2)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        msg = Text("Hello World!", font_size=44, color=WHITE).move_to(DOWN * 1.6)
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)
        win.play(Write(msg), run_time=0.8)
        win.play(FadeToColor(msg, RED, run_time=1.2, rate_func=smooth), run_time=1.2)      # param color=RED ✓
        win.play(FadeToColor(msg, YELLOW, run_time=1.2, rate_func=smooth), run_time=1.2)   # param color=YELLOW ✓

        win.play(Wait(0.4))
        win.play(FadeOut(VGroup(title, lab2, msg)), run_time=0.6)
        win.close()                                 # param win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(
        Page_03b_Shrink_and_Recolor,
        out_path=os.path.join(os.path.dirname(here), "RTM output", "03b-Shrink-and-Recolor.mp4"),
        fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True,
    )
