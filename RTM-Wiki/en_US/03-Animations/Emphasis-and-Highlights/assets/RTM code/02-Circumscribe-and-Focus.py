"""RTM-Wiki · 03-Animations/Emphasis-and-Highlights/02-Circumscribe-and-Focus — page-specific sample

Parameters demonstrated (one by one from the page's "Parameters" tables):
    Circumscribe(mobject, shape=Rectangle, fade_in=False, fade_out=True, time_width=0.3,
                 buff=SMALL_BUFF, color=PURE_YELLOW, run_time=1.6, stroke_width=6)      ✓
    Circumscribe(mobject, shape=Circle, fade_in=True, buff=0.18, color=TEAL,
                 stroke_width=6, run_time=1.6)                                           ✓
    FocusOn(focus_point, opacity=0.4, color=PURPLE, run_time=1.4)                        ✓
    Wiggle(mobject, scale_value=1.35, rotation_angle=0.03*TAU, n_wiggles=4,
           scale_about_point=None, rotate_about_point=None, run_time=1.6)                ✓
Not demonstrated: `Circumscribe`'s `time_width` beam branch — ✅ wired up (completed on 2026-10-16):
        when passed **explicitly** the non-fade branch switches to `ShowPassingFlash` beam
        semantics; **when not passed** it keeps the old `Create` progressive drawing;
        the `fade_in` / `fade_out=True` branch **ignores** this parameter, consistent with CE
        (both samples on this page take the fade branch), so there is no beam-branch video on this
        page; the remaining Transform common parameters in `FocusOn`'s `**kwargs` have no visual effect.
Run: $env:PYTHONPATH="C:\\Users\\begin\\Desktop\\real-time-manim"; python "<this file>"
"""
import os

from real_time_manim import (
    GREEN,
    GREY_B,
    PURE_YELLOW,
    PURPLE,
    SMALL_BUFF,
    TEAL,
    TAU,
    DOWN,
    UP,
    Circle,
    Dot,
    FocusOn,
    Rectangle,
    Scene,
    Text,
    VGroup,
    Wiggle,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    Circumscribe,
    FadeIn,
    FadeOut,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401  used by __main__ at the end of the file


class Page_02_Circumscribe_and_Focus(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # parameters w=1280 / h=720 / hidden=True
        win.scene = self                          # parameter win.scene

        title = Text("Circumscribe / FocusOn / Wiggle",
                     font_size=36, color=GREEN).to_edge(UP)   #title uses ASCII only: font fallback stays reliable in both engines
        win.play(Write(title), run_time=0.8)

        lbl = Text("Circumscribe", font_size=46, color=GREEN).shift(DOWN * 1.6)

        # —— step 1: Circumscribe(shape=Rectangle, fade_out=True) ——
        s1a = Text("Circumscribe(lbl, shape=Rectangle, fade_in=False,", font_size=28, color=GREY_B)
        s1b = Text("    fade_out=True, time_width=0.3, buff=SMALL_BUFF,", font_size=28, color=GREY_B)
        s1c = Text("    color=PURE_YELLOW, run_time=1.6, stroke_width=6)", font_size=28, color=GREY_B)
        sig1 = VGroup(s1a, s1b, s1c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.35)
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.45)
        cs1 = Circumscribe(
            lbl,                                     # parameter mobject ✓
            shape=Rectangle,                         # parameter shape=Rectangle (a class, not an instance) ✓
            fade_in=False,                           # parameter fade_in=False ✓
            fade_out=True,                           # parameter fade_out=True ✓ (default False: the frame fades out)
            time_width=0.3,                          # parameter time_width=0.3 (here fade_out=True: the fade branch ignores this parameter)
            buff=SMALL_BUFF,                         # parameter buff=SMALL_BUFF ✓
            color=PURE_YELLOW,                       # parameter color=PURE_YELLOW ✓
            run_time=1.6,                            # parameter run_time=1.6 ✓ (fade mode splits it evenly between the two halves)
            stroke_width=6,                          # parameter stroke_width=6 ✓ (default 4)
        )
        # add the label lbl to the scene by hand (Circumscribe's .mobject is None and carries no text);
        # since 2026-10-16 the frame _frame is also brought into the scene automatically by the play layer's "grouped sub-animation presentation",
        # so the self.add here becomes an idempotent fallback; clean_up_from_scene still removes _frame when it finishes.
        self.add(lbl, cs1._frame)
        win.play(cs1)
        win.play(FadeOut(sig1), run_time=0.4)

        # —— step 2: Circumscribe(shape=Circle, fade_in=True) ——
        s2a = Text("Circumscribe(lbl, shape=Circle, fade_in=True,", font_size=30, color=GREY_B)
        s2b = Text("    buff=0.18, color=TEAL, stroke_width=6, run_time=1.6)", font_size=30, color=GREY_B)
        sig2 = VGroup(s2a, s2b).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.35)
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.4)
        cs2 = Circumscribe(
            lbl,                                     # parameter mobject ✓
            shape=Circle,                            # parameter shape=Circle ✓ (default Rectangle)
            fade_in=True,                            # parameter fade_in=True ✓ (default False: the frame fades in)
            buff=0.18,                               # parameter buff=0.18 ✓ (default SMALL_BUFF)
            color=TEAL,                              # parameter color=TEAL ✓ (default PURE_YELLOW)
            stroke_width=6,                          # parameter stroke_width=6 ✓
            run_time=1.6,                            # parameter run_time=1.6 ✓
        )
        self.add(cs2._frame)
        win.play(cs2)
        win.play(FadeOut(sig2), FadeOut(lbl), run_time=0.4)

        # —— step 3: FocusOn(focus_point, opacity, color, run_time) ——
        s3a = Text("FocusOn(dot, opacity=0.4,", font_size=32, color=GREY_B)
        s3b = Text("         color=PURPLE, run_time=1.4)", font_size=32, color=GREY_B)
        sig3 = VGroup(s3a, s3b).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.35)
        dot = Dot(radius=0.1, color=PURPLE).next_to(sig3, DOWN, buff=1.2)
        win.play(FadeIn(sig3, shift=DOWN), run_time=0.4)
        self.add(dot)
        win.play(
            FocusOn(
                dot,                                   # parameter focus_point (passing a mobject → its centre) ✓
                opacity=0.4,                           # parameter opacity=0.4 ✓ (default 0.2)
                color=PURPLE,                          # parameter color=PURPLE ✓ (default GREY)
                run_time=1.4,                          # parameter run_time=1.4 ✓ (default 2)
            ),
        )
        win.play(FadeOut(sig3), FadeOut(dot), run_time=0.4)

        # —— step 4: Wiggle(mobject, scale_value, rotation_angle, n_wiggles,
        #                   scale_about_point, rotate_about_point, run_time) ——
        s4a = Text("Wiggle(wig, scale_value=1.35, rotation_angle=0.03*TAU,", font_size=28, color=GREY_B)
        s4b = Text("        n_wiggles=4, scale_about_point=None,", font_size=28, color=GREY_B)
        s4c = Text("        rotate_about_point=None, run_time=1.6)", font_size=28, color=GREY_B)
        sig4 = VGroup(s4a, s4b, s4c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.35)
        wig = Text("Wiggle", font_size=52, color=GREEN).next_to(sig4, DOWN, buff=0.9)
        win.play(FadeIn(sig4, shift=DOWN), run_time=0.4)
        self.add(wig)
        win.play(
            Wiggle(
                wig,                                   # parameter mobject ✓
                scale_value=1.35,                      # parameter scale_value=1.35 ✓ (default 1.1)
                rotation_angle=0.03 * TAU,             # parameter rotation_angle=0.03*TAU ✓ (default 0.01*TAU)
                n_wiggles=4,                           # parameter n_wiggles=4 ✓ (default 6)
                scale_about_point=None,                # parameter scale_about_point=None ✓ (uses the object's centre)
                rotate_about_point=None,               # parameter rotate_about_point=None ✓ (uses the object's centre)
                run_time=1.6,                          # parameter run_time=1.6 ✓ (default 2)
            ),
        )
        win.play(FadeOut(sig4), FadeOut(wig), run_time=0.45)
        win.play(Wait(0.3))

        win.play(FadeOut(title), run_time=0.5)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_02_Circumscribe_and_Focus,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "02-Circumscribe-and-Focus.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
