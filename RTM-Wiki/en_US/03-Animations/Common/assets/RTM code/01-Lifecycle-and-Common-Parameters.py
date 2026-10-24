"""RTM-Wiki · 03-Animations/Common/01-Lifecycle-and-Common-Parameters — page-specific sample

Demonstrated parameters (each row of the page's "Parameters" tables):
    Animation(mobject=…)                      ✓ every animation acts on a mobject
    run_time=1.4 / 1.6 / 0.8                  ✓ non-default durations, passed explicitly each time
    lag_ratio=0.5 (Write staggered by glyph)  ✓ visible: characters are written one by one
    rate_func=linear                          ✓ non-default rate function
    reverse_rate_function=True                ✓ visible: Rotate rewinds (from the end state back)
    remover=True (FadeOut)                    ✓ visible: removed from the scene when done
    introducer=True (FadeIn)                  ✓ visible: added to the scene before playback
    Animation.set_default(run_time, rate_func)/set_default()  ✓ change defaults in bulk and restore
    set_rate_func() (the only chained method RTM's Animation implements)  ✓
Not demonstrated: name — only affects repr/logs, the image is unchanged; suspend_mobject_updating —
    with a mobject that has no updater, True/False give an identical image; use_override — the override
    mechanism is wired up (override_animation / animation_override_for), but it only has an effect with a
    custom Mobject subclass; set_run_time/set_name/get_run_time/get_rate_func/is_introducer/
    is_remover/copy — RTM's own Animation implements these chained methods (tests/test_gap_wait_timeline.py).
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
    RIGHT,
    UP,
    YELLOW,
    PI,
    Circle,
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
    Rotate,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_01_Lifecycle_and_Common_Parameters(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # params w / h / hidden
        win.scene = self                          # param win.scene

        title = Text("01-Animation lifecycle and common parameters", font_size=42, color=YELLOW).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        # —— signature on screen: the constructor parameters all animations share ——
        s1 = Text("Animation(mobject, lag_ratio=0.0, run_time=1.0, rate_func=smooth,", font_size=28, color=GREY_B)
        s2 = Text("           reverse_rate_function=False, name=None, remover=False,", font_size=28, color=GREY_B)
        s3 = Text("           introducer=False, use_override=True)", font_size=28, color=GREY_B)
        sig = VGroup(s1, s2, s3).arrange(DOWN, buff=0.06).to_edge(UP).shift(DOWN * 1.0)
        win.play(FadeIn(sig, shift=DOWN), run_time=0.5)

        # —— Step 1: run_time + rate_func ——
        l1 = Text("Create(sq, run_time=1.4, rate_func=linear)", font_size=30, color=GREY_B)
        l1.next_to(sig, DOWN, buff=0.35)
        sq = Square(side_length=1.2, color=BLUE).set_fill(BLUE, 0.5).shift(LEFT * 3.4 + DOWN * 2.4)
        ci = Circle(radius=0.62, color=GREEN).set_fill(GREEN, 0.5).shift(DOWN * 2.4)
        tri = Triangle(color=ORANGE).scale(0.75).set_fill(ORANGE, 0.5).shift(RIGHT * 3.4 + DOWN * 2.4)
        win.play(FadeIn(l1, shift=DOWN), run_time=0.4)
        win.play(Create(sq, run_time=1.4, rate_func=linear))    # params run_time / rate_func

        # —— Step 2: lag_ratio: Write staggered by glyph ——
        win.play(FadeOut(l1), run_time=0.3)
        l2 = Text("Write(txt, lag_ratio=0.5, run_time=1.6)", font_size=30, color=GREY_B)
        l2.next_to(sig, DOWN, buff=0.35)
        txt = Text("lag_ratio", font_size=40, color=YELLOW).shift(DOWN * 2.4)
        win.play(FadeIn(l2, shift=DOWN), run_time=0.4)
        win.play(Write(txt, lag_ratio=0.5, run_time=1.6))       # param lag_ratio (glyphs written one by one)
        win.play(FadeOut(VGroup(l2, txt)), run_time=0.3)

        # —— Step 3: introducer / remover: the two lifecycle hooks for entering/leaving the scene ——
        l3 = Text("FadeIn(sq2, introducer=True) / FadeOut(sq2, remover=True)",
                  font_size=30, color=GREY_B).next_to(sig, DOWN, buff=0.35)
        sq2 = Square(side_length=1.2, color=YELLOW).set_fill(YELLOW, 0.5).shift(DOWN * 2.4)
        win.play(FadeIn(l3, shift=DOWN), run_time=0.4)
        win.play(FadeIn(sq2, introducer=True, shift=UP, run_time=0.9))   # param introducer
        win.play(Wait(0.3))
        win.play(FadeOut(sq2, remover=True, run_time=0.9))               # param remover

        # —— Step 4: reverse_rate_function: rewind ——
        win.play(FadeOut(l3), run_time=0.3)
        l4 = Text("Rotate(tri, PI/2, reverse_rate_function=True)", font_size=30, color=GREY_B)
        l4.next_to(sig, DOWN, buff=0.35)
        win.play(FadeIn(l4, shift=DOWN), run_time=0.4)
        win.play(Rotate(tri, PI / 2, reverse_rate_function=True,
                        run_time=1.2, rate_func=linear))        # param reverse_rate_function (rewinds from PI/2 back to 0)
        win.play(FadeOut(l4), run_time=0.3)

        # —— Step 5: set_default bulk defaults + set_rate_func chained method ——
        l5 = Text("Rotate.set_default(run_time=1.2, rate_func=linear)", font_size=30, color=GREY_B)
        l6 = Text("  ->  win.play(Rotate(ci, PI/2))   # 1.2s linear from the defaults", font_size=28, color=GREY_B)
        l7 = Text("rot.set_rate_func(linear)  # chained method on RTM's Animation", font_size=28, color=GREY_B)
        sig5 = VGroup(l5, l6, l7).arrange(DOWN, buff=0.06).next_to(sig, DOWN, buff=0.35)
        win.play(FadeIn(sig5, shift=DOWN), run_time=0.4)
        Rotate.set_default(run_time=1.2, rate_func=linear)      # Animation.set_default(**kwargs)
        win.play(Rotate(ci, PI / 2))                            # params run_time=1.2 / rate_func=linear (from the defaults)
        Rotate.set_default()                                    # called with no arguments to restore the defaults
        rot = Rotate(ci, -PI / 2, run_time=0.8)
        rot.set_rate_func(linear)                               # method set_rate_func
        win.play(rot)

        win.play(FadeOut(VGroup(title, sig, sq, ci, tri, sig5)), run_time=0.6)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_01_Lifecycle_and_Common_Parameters,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "01-Lifecycle-and-Common-Parameters.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
