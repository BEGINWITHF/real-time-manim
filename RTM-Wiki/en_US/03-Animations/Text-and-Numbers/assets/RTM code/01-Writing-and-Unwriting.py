"""RTM-Wiki · 03-Animations/Text-and-Numbers/01-Writing-and-Unwriting — page-specific sample

Parameters demonstrated (one by one from the page's "Parameters" tables):
    AddTextLetterByLetter(text, suspend_mobject_updating=False, int_func=np.ceil,
                          rate_func=linear, time_per_char=0.25, run_time=2.4,
                          reverse_rate_function=False, introducer=True)                 ✓
    RemoveTextLetterByLetter(text, suspend_mobject_updating=False, int_func=np.ceil,
                             rate_func=linear, time_per_char=0.2, run_time=2.0,
                             reverse_rate_function=True, introducer=False, remover=True) ✓
Not demonstrated: `AddTextWordByWord` (`text_mobject` / `run_time` / `time_per_char`) —
        the upstream source is annotated `# TODO, this is broken...`: word-splitting a plain `Text`
        yields nothing, and ManimCE itself renders a static frame too (a faithful reproduction, not a
        gap in RTM); the page also says it is "not recommended in new scripts".
Run: $env:PYTHONPATH="C:\\Users\\begin\\Desktop\\real-time-manim"; python "<this file>"
"""
import os

import numpy as np
from real_time_manim import (
    BLUE,
    GREEN,
    GREY_B,
    RED,
    DOWN,
    UP,
    AddTextLetterByLetter,
    RemoveTextLetterByLetter,
    Scene,
    Text,
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


class Page_01_Writing_and_Unwriting(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # parameters w=1280 / h=720 / hidden=True
        win.scene = self                          # parameter win.scene

        title = Text("AddTextLetterByLetter / RemoveTextLetterByLetter",
                     font_size=34, color=GREEN).to_edge(UP)   #title uses ASCII only: font fallback stays reliable in both engines
        win.play(Write(title), run_time=0.85)

        # —— step 1: AddTextLetterByLetter(...) ——
        s1a = Text("AddTextLetterByLetter(txt, suspend_mobject_updating=False,",
                   font_size=28, color=GREY_B)
        s1b = Text("    int_func=np.ceil, rate_func=linear, time_per_char=0.25,",
                   font_size=28, color=GREY_B)
        s1c = Text("    run_time=2.4, reverse_rate_function=False, introducer=True)",
                   font_size=28, color=GREY_B)
        sig1 = VGroup(s1a, s1b, s1c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        a01 = Text("Typing...", font_size=50, color=BLUE).next_to(sig1, DOWN, buff=0.9)
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.45)
        win.play(
            AddTextLetterByLetter(
                a01,                                   # parameter text ✓ (only Text is supported)
                suspend_mobject_updating=False,        # parameter suspend_mobject_updating=False ✓
                int_func=np.ceil,                      # parameter int_func=np.ceil ✓ (shown as soon as reached)
                rate_func=linear,                      # parameter rate_func=linear ✓ (uniform typing speed)
                time_per_char=0.25,                    # parameter time_per_char=0.25 ✓ (default 0.1)
                run_time=2.4,                          # parameter run_time=2.4 ✓ (if not passed it is computed from the character count)
                reverse_rate_function=False,           # parameter reverse_rate_function=False ✓
                introducer=True,                       # parameter introducer=True ✓ (added to the scene before playing)
            ),
        )
        win.play(Wait(0.3))
        win.play(FadeOut(sig1), FadeOut(a01), run_time=0.45)

        # —— step 2: RemoveTextLetterByLetter(...) ——
        s2a = Text("RemoveTextLetterByLetter(txt, suspend_mobject_updating=False,",
                   font_size=28, color=GREY_B)
        s2b = Text("    int_func=np.ceil, rate_func=linear, time_per_char=0.2,",
                   font_size=28, color=GREY_B)
        s2c = Text("    run_time=2.0, reverse_rate_function=True, introducer=False,",
                   font_size=28, color=GREY_B)
        s2d = Text("    remover=True)", font_size=28, color=GREY_B)
        sig2 = VGroup(s2a, s2b, s2c, s2d).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        b01 = Text("Vanishing", font_size=50, color=RED).next_to(sig2, DOWN, buff=0.7)
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.45)
        self.add(b01)                                  # parameter introducer=False → added to the scene by hand first
        win.play(
            RemoveTextLetterByLetter(
                b01,                                   # parameter text ✓
                suspend_mobject_updating=False,        # parameter suspend_mobject_updating=False ✓
                int_func=np.ceil,                      # parameter int_func=np.ceil ✓
                rate_func=linear,                      # parameter rate_func=linear ✓
                time_per_char=0.2,                     # parameter time_per_char=0.2 ✓
                run_time=2.0,                          # parameter run_time=2.0 ✓
                reverse_rate_function=True,            # parameter reverse_rate_function=True ✓ (unlike the parent's False)
                introducer=False,                      # parameter introducer=False ✓ (unlike the parent's True)
                remover=True,                          # parameter remover=True ✓ (removed from the scene when done)
            ),
        )
        win.play(FadeOut(sig2), run_time=0.45)
        win.play(Wait(0.3))

        win.play(FadeOut(title), run_time=0.5)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_01_Writing_and_Unwriting,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "01-Writing-and-Unwriting.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
