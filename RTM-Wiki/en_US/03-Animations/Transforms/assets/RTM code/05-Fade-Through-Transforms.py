"""RTM-Wiki · 03-Animations/Transforms/05-Fade-Through-Transforms — page-specific sample

Demonstrated parameters (each row of the page's "Parameters" tables):
    FadeTransform(mobject, target_mobject, stretch=True, dim_to_match=1)
        ✓ stretch=True: the target is first stretched / scaled to the source's size, then restored
        ✓ stretch=False + dim_to_match=0: match length along x only (a non-default combination)
    FadeTransformPieces(mobject, target_mobject, stretch=True, dim_to_match=1)
        ✓ submobjects are paired one by one and cross-faded (both groups have the same number of shapes)
        ✓ note: RTM's FadeTransformPieces is an AnimationGroup; since 2026-10-16 the constructor also
          accepts run_time (AnimationGroup gained that parameter), so run_time / rate_func can go in the
          constructor or at play level (this sample keeps the play-level form)
    TransformAnimations(start_anim, end_anim, rate_func=squish_rate_func(smooth))
        ✓ the two animations themselves are interpolated into each other; rate_func=squish_rate_func(smooth) (a non-default curve)
        ✓ run_time=1.5 (non-default)

Not demonstrated: none — every visible parameter of the three classes on this page is shown explicitly.

Run: $env:PYTHONPATH="C:\\Users\\begin\\Desktop\\real-time-manim"; python "<this file>"
"""
import os

from real_time_manim import (
    BLUE,
    GREEN,
    GREY_B,
    ORANGE,
    RED,
    YELLOW,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Circle,
    Rectangle,
    Scene,
    Square,
    Text,
    Triangle,
    VGroup,
    smooth,
    squish_rate_func,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    Create,
    FadeIn,
    FadeOut,
    FadeTransform,
    FadeTransformPieces,
    Wait,
    Write,
)
# TransformAnimations is a native ManimCE animation (RTM has not rewritten it; it is exported along with RTM);
# and it needs native sub-animations (it calls set_run_time / starting_mobject), so the sub-animations are imported under native aliases too
from real_time_manim import Create as MCreate, FadeOut as MFadeOut, TransformAnimations
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_05_Fade_Through_Transforms(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # params w / h / hidden
        win.scene = self                          # param win.scene

        title = Text("Fade-out / fade-in transforms", font_size=44, color=ORANGE).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        # --- 1. FadeTransform: the source fades out while the target fades in (and is stretched to the source's size) ---
        lab1 = VGroup(
            Text("FadeTransform(rect, circ, stretch=True,", font_size=30, color=GREY_B),
            Text("              dim_to_match=1, run_time=1.2)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        rect = Rectangle(width=4.0, height=1.0, color=BLUE).set_fill(BLUE, 0.5).move_to(LEFT * 2.4 + DOWN * 1.4)
        circ = Circle(radius=1.1, color=GREEN).set_fill(GREEN, 0.5).move_to(RIGHT * 3.0 + DOWN * 1.4)
        self.add(rect)                             # put the source object into the scene first
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)
        win.play(
            FadeTransform(rect, circ, stretch=True, dim_to_match=1,   # params stretch / dim_to_match ✓
                          run_time=1.2),                               # param run_time ✓
            run_time=1.2,
        )
        win.play(FadeOut(VGroup(lab1, circ)), run_time=0.5)

        # --- 2. FadeTransform: dim_to_match only takes effect when stretch=False (0 = match along x) ---
        lab2 = VGroup(
            Text("FadeTransform(rect2, tri, stretch=False,", font_size=30, color=GREY_B),
            Text("              dim_to_match=0, run_time=1.2)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        rect2 = Rectangle(width=4.5, height=0.8, color=RED).set_fill(RED, 0.5).move_to(LEFT * 2.4 + DOWN * 1.4)
        tri = Triangle(color=YELLOW).scale(1.1).set_fill(YELLOW, 0.5).move_to(RIGHT * 3.0 + DOWN * 1.4)
        self.add(rect2)
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)
        win.play(
            FadeTransform(rect2, tri, stretch=False, dim_to_match=0,  # params stretch=False / dim_to_match=0 ✓
                          run_time=1.2),
            run_time=1.2,
        )
        win.play(FadeOut(VGroup(lab2, tri)), run_time=0.5)

        # --- 3. FadeTransformPieces: submobjects are paired one by one and cross-faded ---
        lab3 = VGroup(
            Text("FadeTransformPieces(grp, grp2,", font_size=30, color=GREY_B),
            Text("  stretch=True, dim_to_match=1)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        grp = VGroup(Square(side_length=1.0, color=BLUE),
                     Circle(radius=0.5, color=GREEN).shift(RIGHT * 1.6)).move_to(LEFT * 2.6 + DOWN * 1.4)
        grp2 = VGroup(Circle(radius=0.5, color=RED),
                      Triangle(color=YELLOW).scale(0.55).shift(RIGHT * 1.6)).move_to(RIGHT * 3.0 + DOWN * 1.4)
        self.add(grp)
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)
        # note: the sample keeps the older form - RTM's FadeTransformPieces is an AnimationGroup,
        #     so run_time / rate_func go at play level (since 2026-10-16 the constructor also takes run_time; both work).
        win.play(FadeTransformPieces(grp, grp2, stretch=True, dim_to_match=1),   # params stretch / dim_to_match ✓
                 run_time=1.5,                                                    # param run_time ✓ (play level)
                 rate_func=smooth)                                               # param rate_func ✓
        win.play(FadeOut(VGroup(lab3, grp2)), run_time=0.5)

        # --- 4. TransformAnimations: the two animations themselves interpolate into each other ---
        lab4 = VGroup(
            Text("TransformAnimations(MCreate(sq),", font_size=30, color=GREY_B),
            Text("  MFadeOut(sq), run_time=1.5,", font_size=30, color=GREY_B),
            Text("  rate_func=squish_rate_func(smooth))", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.3)
        sq = Square(side_length=1.8, color=GREEN).set_fill(GREEN, 0.5).move_to(LEFT * 2.8 + DOWN * 1.4)
        win.play(FadeIn(lab4, shift=DOWN), run_time=0.4)
        win.play(Create(sq), run_time=0.6)
        win.play(                                   # the two animations themselves interpolate into each other
            TransformAnimations(MCreate(sq), MFadeOut(sq),          # params start_anim / end_anim ✓
                                rate_func=squish_rate_func(smooth), # param rate_func ✓ (non-default)
                                run_time=1.5),                      # param run_time ✓ (non-default)
            run_time=1.5,
        )

        win.play(Wait(0.4))
        win.play(FadeOut(VGroup(title, lab4)), run_time=0.6)
        win.close()                                 # param win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(
        Page_05_Fade_Through_Transforms,
        out_path=os.path.join(os.path.dirname(here), "RTM output", "05-Fade-Through-Transforms.mp4"),
        fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True,
    )
