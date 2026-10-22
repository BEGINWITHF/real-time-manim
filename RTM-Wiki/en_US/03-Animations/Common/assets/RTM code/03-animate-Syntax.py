"""RTM-Wiki · 03-Animations/Common/03-animate-Syntax — page-specific sample

Demonstrated parameters (each row of the page's "Parameters" tables):
    sq.animate.shift(...)                       ✓ basic syntax: change a property and it animates
    sq.animate(run_time=1.3)                    ✓ kwargs right after .animate(...), passed only once
    .set_color(RED).rotate(PI/5)                ✓ chained methods composed into one animation
    sq.animate(rate_func=there_and_back)        ✓ the rate function inside kwargs
    ci.generate_target() + MoveToTarget(ci, run_time=1.2)  ✓ explicit target state
Not demonstrated: .animate(lag_ratio=...) — a single .animate has no submobject staggering to speak of
    (the parameter itself is not dropped; with no children it raises a UserWarning, see the page end);
    @override_animate / @override_animation — they need a custom Mobject subclass, so no sample on this
    page (the mechanism is wired up, see the page end).
Run: $env:PYTHONPATH="C:\\Users\\begin\\Desktop\\real-time-manim"; python "<this file>"
"""
import os

from real_time_manim import (
    BLUE,
    DOWN,
    GREEN,
    GREY_B,
    LEFT,
    RED,
    RIGHT,
    UP,
    YELLOW,
    PI,
    Circle,
    Scene,
    Square,
    Text,
    VGroup,
    there_and_back,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeIn,
    FadeOut,
    MoveToTarget,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_03_animate_Syntax(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # params w / h / hidden
        win.scene = self                          # param win.scene

        title = Text("03-.animate syntax and MoveToTarget", font_size=44, color=YELLOW).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        sq = Square(side_length=1.4, color=BLUE).set_fill(BLUE, 0.5).shift(LEFT * 3.2 + DOWN * 1.9)
        ci = Circle(radius=0.7, color=GREEN).set_fill(GREEN, 0.5).shift(RIGHT * 3.2 + DOWN * 1.9)

        # —— Step 1: sq.animate.shift(...) ——
        l1 = Text("win.play(sq.animate.shift(RIGHT * 1.6))", font_size=30, color=GREY_B)
        l1.to_edge(UP).shift(DOWN * 1.05)
        win.play(FadeIn(l1, shift=DOWN), FadeIn(sq), FadeIn(ci), run_time=0.4)
        win.play(sq.animate.shift(RIGHT * 1.6))                  # param .animate + chained method shift
        win.play(Wait(0.2))

        # —— Step 2: kwargs right after .animate(...), several chained methods ——
        win.play(FadeOut(l1), run_time=0.3)
        l2 = Text("win.play(sq.animate(run_time=1.3)", font_size=30, color=GREY_B)
        l3 = Text("              .set_color(RED).rotate(PI/5))", font_size=30, color=GREY_B)
        sig2 = VGroup(l2, l3).arrange(DOWN, buff=0.06).to_edge(UP).shift(DOWN * 1.05)
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.4)
        win.play(sq.animate(run_time=1.3)                         # param .animate(run_time=…) (can only be passed once)
                 .set_color(RED)                                  # chained method 1
                 .rotate(PI / 5))                                 # chained method 2 (composed into one animation)
        win.play(Wait(0.2))

        # —— Step 3: rate_func written into .animate(...) ——
        win.play(FadeOut(sig2), run_time=0.3)
        l4 = Text("win.play(sq.animate(rate_func=there_and_back).scale(0.55))",
                  font_size=30, color=GREY_B).to_edge(UP).shift(DOWN * 1.05)
        win.play(FadeIn(l4, shift=DOWN), run_time=0.4)
        win.play(sq.animate(rate_func=there_and_back).scale(0.55))   # param rate_func (goes out and comes back)
        win.play(Wait(0.2))

        # —— Step 4: explicit generate_target() + MoveToTarget ——
        win.play(FadeOut(l4), run_time=0.3)
        l5 = Text("ci.generate_target();  ci.target.set_fill(RED, 0.4)", font_size=28, color=GREY_B)
        l6 = Text("                 .shift(2 * RIGHT + UP).scale(0.5)", font_size=28, color=GREY_B)
        l7 = Text("win.play(MoveToTarget(ci, run_time=1.2))", font_size=28, color=GREY_B)
        sig4 = VGroup(l5, l6, l7).arrange(DOWN, buff=0.06).to_edge(UP).shift(DOWN * 1.05)
        win.play(FadeIn(sig4, shift=DOWN), run_time=0.4)
        ci.generate_target()                                      # param generate_target()
        ci.target.set_fill(RED, 0.4).shift(2 * RIGHT + UP).scale(0.5)
        win.play(MoveToTarget(ci, run_time=1.2))                  # param MoveToTarget(mobject, run_time)
        win.play(Wait(0.3))

        win.play(FadeOut(VGroup(title, sq, ci, sig4)), run_time=0.6)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_03_animate_Syntax,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "03-animate-Syntax.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
