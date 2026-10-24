"""RTM-Wiki · 03-Animations/Text-and-Numbers/01b-Typing-with-a-Cursor — page-specific sample

Parameters demonstrated (one by one from the page's "Parameters" tables):
    TypeWithCursor(text, cursor, buff=0.12, keep_cursor_y=True, leave_cursor_on=True,
                   time_per_char=0.14, reverse_rate_function=False, introducer=True)   ✓
    UntypeWithCursor(text, cursor, buff=0.12, keep_cursor_y=True, leave_cursor_on=True,
                     time_per_char=0.14, reverse_rate_function=True,
                     introducer=False, remover=True)                                   ✓
    Blink(cursor, time_on=0.3, time_off=0.3, blinks=2)  ← the cursor-blink combo from the page example ✓
Not demonstrated: the `cursor`'s "colour parameter" is not in the animation signature — the cursor is
        just a mobject, and its colour is set when the Rectangle is created (the sample uses RED, the
        page example uses GREY_A); the remaining common upstream parameters in `**kwargs` have no
        visual effect.
Run: python "<this file>"  (the script puts the repo root on sys.path itself)
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    GREEN,
    GREY_B,
    PURPLE,
    RED,
    DOWN,
    UP,
    Rectangle,
    Scene,
    Text,
    VGroup,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    Blink,
    FadeIn,
    FadeOut,
    TypeWithCursor,
    UntypeWithCursor,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401  used by __main__ at the end of the file


class Page_01b_Typing_with_a_Cursor(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # parameters w=1280 / h=720 / hidden=True
        win.scene = self                          # parameter win.scene

        title = Text("TypeWithCursor / UntypeWithCursor",
                     font_size=34, color=GREEN).to_edge(UP)   #title uses ASCII only: font fallback stays reliable in both engines
        win.play(Write(title), run_time=0.85)

        # —— step 1: TypeWithCursor(text, cursor, buff, keep_cursor_y,
        #                           leave_cursor_on, time_per_char, ...) ——
        s1a = Text("TypeWithCursor(txt, cursor,", font_size=28, color=GREY_B)
        s1b = Text("    buff=0.12, keep_cursor_y=True, leave_cursor_on=True,",
                   font_size=28, color=GREY_B)
        s1c = Text("    time_per_char=0.14, reverse_rate_function=False,",
                   font_size=28, color=GREY_B)
        s1d = Text("    introducer=True)", font_size=28, color=GREY_B)
        sig1 = VGroup(s1a, s1b, s1c, s1d).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.3)
        txt01 = Text("Inserting", color=PURPLE, font_size=52).next_to(sig1, DOWN, buff=0.6)
        cur01 = Rectangle(color=RED, fill_color=RED, fill_opacity=1,   # cursor colour: set when the cursor is created
                          height=1.0, width=0.14).move_to(txt01[0])
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.45)
        win.play(
            TypeWithCursor(
                txt01,                                # parameter text ✓
                cur01,                                # parameter cursor ✓ (a thin rectangular cursor, RED)
                buff=0.12,                            # parameter buff=0.12 ✓ (default 0.1: the gap between the cursor and the last character)
                keep_cursor_y=True,                   # parameter keep_cursor_y=True ✓ (y locked to the centre of the whole text)
                leave_cursor_on=True,                 # parameter leave_cursor_on=True ✓ (the cursor stays when done)
                time_per_char=0.14,                   # parameter time_per_char=0.14 ✓ (default 0.1)
                reverse_rate_function=False,          # parameter reverse_rate_function=False ✓
                introducer=True,                      # parameter introducer=True ✓ (added to the scene before playing)
            ),
            Wait(1.6),                                # slightly longer than the automatic run_time (=0.14*9=1.26s) so the last frame reaches alpha 1
        )
        win.play(                                     # page example: blink the cursor twice after typing
            Blink(
                cur01,                                # parameter mobject ✓
                time_on=0.3,                          # parameter time_on=0.3 ✓
                time_off=0.3,                         # parameter time_off=0.3 ✓
                blinks=2,                             # parameter blinks=2 ✓
            ),
            run_time=1.2,
        )
        win.play(FadeOut(sig1), FadeOut(txt01), FadeOut(cur01), run_time=0.5)

        # —— step 2: UntypeWithCursor(text, cursor, ..., reverse_rate_function=True,
        #                             introducer=False, remover=True) ——
        s2a = Text("UntypeWithCursor(txt, cursor,", font_size=28, color=GREY_B)
        s2b = Text("    buff=0.12, keep_cursor_y=True, leave_cursor_on=True,",
                   font_size=28, color=GREY_B)
        s2c = Text("    time_per_char=0.14, reverse_rate_function=True,",
                   font_size=28, color=GREY_B)
        s2d = Text("    introducer=False, remover=True)", font_size=28, color=GREY_B)
        sig2 = VGroup(s2a, s2b, s2c, s2d).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.3)
        txt02 = Text("Deleting", color=PURPLE, font_size=52).next_to(sig2, DOWN, buff=0.6)
        cur02 = Rectangle(color=RED, fill_color=RED, fill_opacity=1,
                          height=1.0, width=0.14).move_to(txt02[0])
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.45)
        self.add(txt02, cur02)                        # parameter introducer=False → added to the scene by hand first
        win.play(
            UntypeWithCursor(
                txt02,                                # parameter text ✓
                cur02,                                # parameter cursor ✓
                buff=0.12,                            # parameter buff ✓ (inherited from TypeWithCursor)
                keep_cursor_y=True,                   # parameter keep_cursor_y ✓
                leave_cursor_on=True,                 # parameter leave_cursor_on ✓
                time_per_char=0.14,                   # parameter time_per_char=0.14 ✓
                reverse_rate_function=True,           # parameter reverse_rate_function=True ✓ (unlike the parent's False)
                introducer=False,                     # parameter introducer=False ✓ (unlike the parent's True)
                remover=True,                         # parameter remover=True ✓ (removed from the scene when done)
            ),
            Wait(1.6),                                # as above: stretch the duration so the last frame reaches alpha 1
        )
        win.play(FadeOut(sig2), run_time=0.5)
        win.play(Wait(0.3))

        win.play(FadeOut(title), run_time=0.5)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_01b_Typing_with_a_Cursor,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "01b-Typing-with-a-Cursor.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
