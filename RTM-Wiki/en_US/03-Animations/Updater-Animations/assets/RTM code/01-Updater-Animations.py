"""RTM-Wiki · 03-Animations/Updater-Animations/01-Updater-Animations — page-specific sample

Demonstrated parameters (each row of the page's "Parameters" tables):
    UpdateFromFunc(mobject, update_function, suspend_mobject_updating=False,
                   **kwargs(run_time=2.4))                                       ✓
    UpdateFromAlphaFunc(mobject, update_function, suspend_mobject_updating=False,
                        **kwargs(run_time=2.0))                                  ✓
    MaintainPositionRelativeTo(mobject, tracked_mobject, **kwargs(run_time=2.2)) ✓
Not demonstrated: `suspend_mobject_updating=True` — it suspends the object's own
        updater, the opposite of this page's "per-frame callback driving" purpose;
        the sample keeps it explicitly False as the page recommends;
        the remaining common Transform/Animation parameters in `**kwargs` have no visual effect.
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
    LEFT,
    RIGHT,
    UP,
    Dot,
    Scene,
    Square,
    Text,
    UpdateFromAlphaFunc,
    UpdateFromFunc,
    MaintainPositionRelativeTo,
    VGroup,
    linear,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeIn,
    FadeOut,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401  used by __main__ at the end of the file


class Page_01_Updater_Animations(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # params w=1280 / h=720 / hidden=True
        win.scene = self                          # param win.scene

        title = Text("UpdateFromFunc / UpdateFromAlphaFunc / MaintainPositionRelativeTo",
                     font_size=24, color=GREEN).to_edge(UP)   #title uses ASCII only: two-engine font fallback is more stable
        win.play(Write(title), run_time=0.85)

        # —— Step 1: UpdateFromFunc(mobject, update_function, suspend..., run_time) ——
        s1a = Text("UpdateFromFunc(label, lambda l: l.next_to(dot, UP),",
                   font_size=28, color=GREY_B)
        s1b = Text("    suspend_mobject_updating=False, run_time=2.4)",
                   font_size=28, color=GREY_B)
        sig1 = VGroup(s1a, s1b).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        dot = Dot(radius=0.12, color=RED).next_to(sig1, DOWN, buff=1.1).shift(LEFT * 3.5)
        label = Text("hi", font_size=40, color=RED).next_to(dot, UP, buff=0.3)
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.45)
        self.add(dot, label)
        win.play(                                    # params mobject=dot + drives label every frame
            dot.animate.shift(RIGHT * 7),
            UpdateFromFunc(
                label,                               # param mobject ✓
                lambda l: l.next_to(dot, UP),        # param update_function ✓ (called every frame)
                suspend_mobject_updating=False,      # param suspend_mobject_updating=False ✓
                run_time=2.4,                        # param **kwargs: run_time=2.4 ✓ (must be given explicitly)
            ),
            rate_func=linear,
        )
        win.play(FadeOut(sig1), FadeOut(dot), FadeOut(label), run_time=0.45)

        # —— Step 2: UpdateFromAlphaFunc(mobject, update_function, ...) ——
        s2a = Text("UpdateFromAlphaFunc(sq, lambda m, a: m.set_fill(RED, opacity=a),",
                   font_size=26, color=GREY_B)
        s2b = Text("    suspend_mobject_updating=False, run_time=2.0)",
                   font_size=26, color=GREY_B)
        sig2 = VGroup(s2a, s2b).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        sq = Square(side_length=2.0, color=GREEN).next_to(sig2, DOWN, buff=0.6)
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.45)
        self.add(sq)
        win.play(
            UpdateFromAlphaFunc(
                sq,                                   # param mobject ✓
                lambda m, a: m.set_fill(RED, opacity=a),   # param update_function ✓ (receives one extra progress argument)
                suspend_mobject_updating=False,       # param suspend_mobject_updating=False ✓
                run_time=2.0,                         # param **kwargs: run_time=2.0 ✓
            ),
        )
        win.play(FadeOut(sig2), FadeOut(sq), run_time=0.45)

        # —— Step 3: MaintainPositionRelativeTo(mobject, tracked_mobject, **kwargs) ——
        s3a = Text("MaintainPositionRelativeTo(b, a, run_time=2.2)",
                   font_size=30, color=GREY_B)
        sig3 = s3a.next_to(title, DOWN, buff=0.4)
        a = Dot(radius=0.14, color=GREEN).next_to(sig3, DOWN, buff=1.1).shift(LEFT * 2)
        b = Dot(radius=0.14, color=PURPLE).next_to(a, RIGHT, buff=1.2)
        win.play(FadeIn(sig3, shift=DOWN), run_time=0.45)
        self.add(a, b)
        win.play(                                    # params mobject=b / tracked_mobject=a
            a.animate.shift(RIGHT * 2.5 + DOWN * 0.9),
            MaintainPositionRelativeTo(
                b,                                   # param mobject (the follower) ✓
                a,                                   # param tracked_mobject (the one followed) ✓
                run_time=2.2,                        # param **kwargs: run_time=2.2 ✓
            ),
            rate_func=linear,
        )
        win.play(FadeOut(sig3), FadeOut(a), FadeOut(b), run_time=0.5)

        win.play(FadeOut(title), run_time=0.5)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_01_Updater_Animations,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "01-Updater-Animations.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
