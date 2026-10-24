"""RTM-Wiki · 03-Animations/Text-and-Numbers/02-Number-Animations — page-specific sample

Parameters demonstrated (one by one from the page's "Parameters" tables):
    ChangingDecimal(decimal_mob, number_update_func=lambda a: 5*a,
                    suspend_mobject_updating=False, **kwargs(run_time, rate_func))  ✓
    ChangeDecimalToValue(decimal_mob, target_number=10,
                         **kwargs(run_time, rate_func, suspend_mobject_updating))    ✓
    ValueTracker + add_updater long-term following (the page's "tip" entry)          ✓
Not demonstrated: `TextDecimalNumber` — another class RTM exports; the manual does not document its
        signature and the page states it "does not go into it".
Run: python "<this file>"  (the script puts the repo root on sys.path itself)
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    BLUE,
    GREEN,
    GREY_B,
    RED,
    DOWN,
    UP,
    ChangeDecimalToValue,
    ChangingDecimal,
    DecimalNumber,
    Scene,
    Text,
    ValueTracker,
    VGroup,
    linear,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeIn,
    FadeOut,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401  used by __main__ at the end of the file


class Page_02_Number_Animations(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # parameters w=1280 / h=720 / hidden=True
        win.scene = self                          # parameter win.scene

        title = Text("ChangingDecimal / ChangeDecimalToValue",
                     font_size=34, color=GREEN).to_edge(UP)   #title uses ASCII only: font fallback stays reliable in both engines
        win.play(Write(title), run_time=0.85)

        # —— step 1: ChangingDecimal(decimal_mob, number_update_func, ...) ——
        s1a = Text("ChangingDecimal(num, lambda a: 5 * a,", font_size=30, color=GREY_B)
        s1b = Text("    suspend_mobject_updating=False, run_time=2.4,", font_size=30, color=GREY_B)
        s1c = Text("    rate_func=linear)", font_size=30, color=GREY_B)
        sig1 = VGroup(s1a, s1b, s1c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        n01 = DecimalNumber(0, num_decimal_places=2, color=BLUE).next_to(sig1, DOWN, buff=0.9)
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.45)
        self.add(n01)
        win.play(
            ChangingDecimal(
                n01,                                  # parameter decimal_mob ✓ (must be a DecimalNumber)
                lambda a: 5 * a,                      # parameter number_update_func ✓: f(alpha) -> value
                suspend_mobject_updating=False,       # parameter suspend_mobject_updating=False ✓ (can coexist with a ValueTracker)
                run_time=2.4,                         # parameter **kwargs: run_time=2.4 ✓
                rate_func=linear,                     # parameter **kwargs: rate_func=linear ✓
            ),
        )
        win.play(Wait(0.4))
        win.play(FadeOut(sig1), FadeOut(n01), run_time=0.45)

        # —— step 2: ChangeDecimalToValue(decimal_mob, target_number, ...) ——
        s2a = Text("ChangeDecimalToValue(num, target_number=10,",
                   font_size=30, color=GREY_B)
        s2b = Text("    run_time=2.4, rate_func=linear,", font_size=30, color=GREY_B)
        s2c = Text("    suspend_mobject_updating=False)", font_size=30, color=GREY_B)
        sig2 = VGroup(s2a, s2b, s2c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        n02 = DecimalNumber(0, num_decimal_places=2, color=RED).next_to(sig2, DOWN, buff=0.9)
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.45)
        self.add(n02)
        win.play(
            ChangeDecimalToValue(
                n02,                                  # parameter decimal_mob ✓
                10,                                   # parameter target_number=10 ✓ (the source annotates int; a float works just as well)
                run_time=2.4,                         # parameter **kwargs: run_time=2.4 ✓
                rate_func=linear,                     # parameter **kwargs: rate_func=linear ✓
                suspend_mobject_updating=False,       # parameter **kwargs: inherited from ChangingDecimal ✓
            ),
        )
        win.play(Wait(0.3))
        win.play(FadeOut(sig2), FadeOut(n02), run_time=0.45)

        # —— step 3: the page's "tip" — use ValueTracker + updater for long-term following ——
        s3a = Text("tracker = ValueTracker(0)", font_size=30, color=GREY_B)
        s3b = Text("num.add_updater(lambda n: n.set_value(tracker.get_value()))",
                   font_size=30, color=GREY_B)
        s3c = Text("win.play(tracker.animate.set_value(7.5), run_time=2)",
                   font_size=30, color=GREY_B)
        sig3 = VGroup(s3a, s3b, s3c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        tracker = ValueTracker(0)
        n03 = DecimalNumber(0, num_decimal_places=1, color=GREEN).next_to(sig3, DOWN, buff=0.9)
        n03.add_updater(lambda n: n.set_value(tracker.get_value()))
        win.play(FadeIn(sig3, shift=DOWN), run_time=0.45)
        self.add(n03)
        win.play(tracker.animate.set_value(7.5), run_time=2, rate_func=linear)
        n03.clear_updaters()
        win.play(FadeOut(sig3), FadeOut(n03), run_time=0.5)
        win.play(Wait(0.3))

        win.play(FadeOut(title), run_time=0.5)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_02_Number_Animations,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "02-Number-Animations.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
