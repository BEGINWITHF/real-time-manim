"""RTM-Wiki · 03-Animations/Emphasis-and-Highlights/01-Indicate-and-Flash — page-specific sample

Parameters demonstrated (one by one from the page's "Parameters" tables):
    Indicate(mobject, scale_factor=1.6, color=RED, rate_func=there_and_back, **kwargs)  ✓
    Flash(point, line_length=0.3, num_lines=30, flash_radius=0.18, line_stroke_width=5,
          color=RED, time_width=1.5, run_time=1.2, **kwargs(rate_func=rush_from))       ✓
    Blink(mobject, time_on=0.35, time_off=0.25, blinks=3, hide_at_end=True, **kwargs)   ✓
Not demonstrated: passing a coordinate point as `point` (when a mobject is passed only its centre is
        used, so the two look the same); the remaining Transform/Animation common parameters in
        `**kwargs` (no distinct visual effect).
Run: python "<this file>"  (the script puts the repo root on sys.path itself)
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    BLUE,
    DARK_GRAY,
    GREEN,
    GREY_B,
    RED,
    DOWN,
    UP,
    Dot,
    Flash,
    Scene,
    Square,
    Text,
    VGroup,
    rush_from,
    there_and_back,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    Blink,
    FadeIn,
    FadeOut,
    Indicate,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401  used by __main__ at the end of the file


class Page_01_Indicate_and_Flash(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # parameters w=1280 / h=720 / hidden=True
        win.scene = self                          # parameter win.scene

        title = Text("Indicate / Flash / Blink",
                     font_size=38, color=GREEN).to_edge(UP)   #title uses ASCII only: font fallback stays reliable in both engines
        win.play(Write(title), run_time=0.8)

        # —— step 1: Indicate(mobject, scale_factor, color, rate_func, **kwargs) ——
        s1a = Text("Indicate(sq, scale_factor=1.6,", font_size=32, color=GREY_B)
        s1b = Text("          color=RED, rate_func=there_and_back)", font_size=32, color=GREY_B)
        sig1 = VGroup(s1a, s1b).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        sq = Square(side_length=1.6, color=BLUE).set_fill(BLUE, 0.5).next_to(sig1, DOWN, buff=0.7)
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.45)
        win.play(
            Indicate(
                sq,                                      # parameter mobject ✓
                scale_factor=1.6,                        # parameter scale_factor=1.6 ✓ (default 1.2)
                color=RED,                               # parameter color=RED ✓ (default PURE_YELLOW)
                rate_func=there_and_back,                # parameter rate_func ✓ (explicit: goes there then comes back)
            ),
            run_time=1.4,                                # parameter **kwargs(run_time): overridden at the play level ✓
        )
        win.play(FadeOut(sig1), FadeOut(sq), run_time=0.45)

        # —— step 2: Flash(point, line_length, num_lines, flash_radius,
        #                   line_stroke_width, color, time_width, run_time, **kwargs) ——
        s2a = Text("Flash(dot, line_length=0.3, num_lines=30,", font_size=30, color=GREY_B)
        s2b = Text("        flash_radius=0.18, line_stroke_width=5,", font_size=30, color=GREY_B)
        s2c = Text("        color=RED, time_width=1.5, rate_func=rush_from)", font_size=30, color=GREY_B)
        sig2 = VGroup(s2a, s2b, s2c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        dot = Dot(radius=0.12, color=DARK_GRAY).next_to(sig2, DOWN, buff=1.0)
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.45)
        win.play(
            Flash(
                dot,                                     # parameter point (passing a mobject → its centre) ✓
                line_length=0.3,                         # parameter line_length=0.3 ✓ (default 0.2)
                num_lines=30,                            # parameter num_lines=30 ✓ (default 12)
                flash_radius=0.18,                       # parameter flash_radius=0.18 ✓ (default 0.1)
                line_stroke_width=5,                     # parameter line_stroke_width=5 ✓ (default 3)
                color=RED,                               # parameter color=RED ✓ (default PURE_YELLOW)
                time_width=1.5,                          # parameter time_width=1.5 ✓ (default 1)
                run_time=1.2,                            # parameter run_time=1.2 ✓ (default 1.0)
                rate_func=rush_from,                     # parameter **kwargs → passed through to each line's ShowPassingFlash ✓
            ),
            run_time=1.2,
        )
        win.play(FadeOut(sig2), FadeOut(dot), run_time=0.45)

        # —— step 3: Blink(mobject, time_on, time_off, blinks, hide_at_end, **kwargs) ——
        s3a = Text("Blink(txt, time_on=0.35, time_off=0.25,", font_size=32, color=GREY_B)
        s3b = Text("        blinks=3, hide_at_end=True)", font_size=32, color=GREY_B)
        sig3 = VGroup(s3a, s3b).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        txt = Text("Blinking", font_size=48, color=GREEN).next_to(sig3, DOWN, buff=0.9)
        win.play(FadeIn(sig3, shift=DOWN), run_time=0.45)
        self.add(txt)                                  #Blink does not introduce the object: add it to the scene first or it cannot blink
        win.play(
            Blink(
                txt,                                     # parameter mobject ✓
                time_on=0.35,                            # parameter time_on=0.35 ✓ (default 0.5)
                time_off=0.25,                           # parameter time_off=0.25 ✓ (default 0.5)
                blinks=3,                                # parameter blinks=3 ✓ (default 1)
                hide_at_end=True,                        # parameter hide_at_end=True ✓ (default False: stays hidden at the end)
            ),
        )
        win.play(FadeOut(sig3), run_time=0.45)

        win.play(FadeOut(title), run_time=0.5)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_01_Indicate_and_Flash,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "01-Indicate-and-Flash.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
