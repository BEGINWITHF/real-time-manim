"""RTM-Wiki · 03-Animations/Emphasis-and-Highlights/01b-Sweeps-and-Waves — page-specific sample

Parameters demonstrated (one by one from the page's "Parameters" tables):
    ShowPassingFlash(mobject, time_width=0.5, **kwargs(run_time=1.6))                            ✓
    ShowPassingFlashWithThinningStrokeWidth(vmobject, n_segments=12, time_width=0.15,
                                            remover=True, **kwargs(run_time=1.8))                 ✓
    ApplyWave(mobject, direction=UP, amplitude=0.35, wave_func=smooth, time_width=1,
              ripples=3, run_time=2)                                                              ✓
Not demonstrated: `ShowPassingFlash`'s "restore the full stroke" (`remover=False`) behaviour after it
        finishes — ✅ wired up (the `remover` parameter was completed on 2026-10-16 and defaults to
        `True` for backward compatibility: with `True` `clean_up_from_scene` removes the object from
        the scene; with an explicit `False` the object stays in the scene and its full stroke is
        restored), the sample uses the default; the remaining common parameters in `**kwargs` have no
        visual effect.
Run: $env:PYTHONPATH="C:\\Users\\begin\\Desktop\\real-time-manim"; python "<this file>"
"""
import os

from real_time_manim import (
    BLUE,
    DARK_GRAY,
    GREEN,
    GREY_B,
    YELLOW,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Circle,
    RegularPolygon,
    Scene,
    ShowPassingFlashWithThinningStrokeWidth,
    Text,
    VGroup,
    smooth,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    ApplyWave,
    FadeIn,
    FadeOut,
    ShowPassingFlash,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401  used by __main__ at the end of the file


class Page_01b_Sweeps_and_Waves(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # parameters w=1280 / h=720 / hidden=True
        win.scene = self                          # parameter win.scene

        title = Text("ShowPassingFlash / ApplyWave",
                     font_size=36, color=GREEN).to_edge(UP)   #title uses ASCII only: font fallback stays reliable in both engines
        win.play(Write(title), run_time=0.8)

        # —— step 1: ShowPassingFlash(mobject, time_width, **kwargs) ——
        sig1 = Text("ShowPassingFlash(poly, time_width=0.5, run_time=1.6)",
                    font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)
        poly = RegularPolygon(5, color=DARK_GRAY).scale(1.6).next_to(sig1, DOWN, buff=0.7)
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.45)
        win.play(
            ShowPassingFlash(
                poly,                                    # parameter mobject ✓
                time_width=0.5,                          # parameter time_width=0.5 ✓ (default 0.1: the beam covers 50% of the whole stroke)
                run_time=1.6,                            # parameter **kwargs(run_time) ✓
            ),
            run_time=1.6,
        )
        # RTM's version defaults remover to True, removing the mobject from the scene when it finishes, so the pentagon is not FadeOut-ed again
        #(since 2026-10-16 remover can be passed False explicitly, leaving the object in the scene).
        win.play(FadeOut(sig1), run_time=0.45)

        # —— step 2: ShowPassingFlashWithThinningStrokeWidth(
        #                vmobject, n_segments, time_width, remover, **kwargs) ——
        s2a = Text("ShowPassingFlashWithThinningStrokeWidth(", font_size=28, color=GREY_B)
        s2b = Text("    ring, n_segments=12, time_width=0.15,", font_size=28, color=GREY_B)
        s2c = Text("    remover=True, run_time=1.8)", font_size=28, color=GREY_B)
        sig2 = VGroup(s2a, s2b, s2c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        ring = Circle(radius=1.2, stroke_width=10, color=BLUE).next_to(sig2, DOWN, buff=0.6)
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.45)
        win.play(
            ShowPassingFlashWithThinningStrokeWidth(
                ring,                                    # parameter vmobject ✓
                n_segments=12,                           # parameter n_segments=12 ✓ (default 10)
                time_width=0.15,                         # parameter time_width=0.15 ✓ (default 0.1)
                remover=True,                            # parameter remover=True ✓ (the default, passed explicitly)
                run_time=1.8,                            # parameter **kwargs(run_time) ✓
            ),
            run_time=1.8,
        )
        win.play(FadeOut(sig2), FadeOut(ring), run_time=0.45)

        # —— step 3: ApplyWave(mobject, direction, amplitude, wave_func,
        #                      time_width, ripples, run_time) ——
        s3a = Text("ApplyWave(txt, direction=UP, amplitude=0.35,", font_size=30, color=GREY_B)
        s3b = Text("           wave_func=smooth, time_width=1,", font_size=30, color=GREY_B)
        s3c = Text("           ripples=3, run_time=2)", font_size=30, color=GREY_B)
        sig3 = VGroup(s3a, s3b, s3c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        wtxt = Text("WaveWaveWave", font_size=46, color=YELLOW).next_to(sig3, DOWN, buff=0.9)
        win.play(FadeIn(sig3, shift=DOWN), run_time=0.45)
        win.play(
            ApplyWave(
                wtxt,                                    # parameter mobject ✓
                direction=UP,                            # parameter direction=UP ✓ (explicit: the direction the wave pushes)
                amplitude=0.35,                          # parameter amplitude=0.35 ✓ (default 0.2)
                wave_func=smooth,                        # parameter wave_func=smooth ✓ (the shape of a single crest)
                time_width=1,                            # parameter time_width=1 ✓ (the wave-length fraction)
                ripples=3,                               # parameter ripples=3 ✓ (default 1)
                run_time=2,                              # parameter run_time=2 ✓
            ),
        )
        win.play(FadeOut(sig3), FadeOut(wtxt), run_time=0.5)
        win.play(Wait(0.3))

        win.play(FadeOut(title), run_time=0.5)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_01b_Sweeps_and_Waves,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "01b-Sweeps-and-Waves.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
