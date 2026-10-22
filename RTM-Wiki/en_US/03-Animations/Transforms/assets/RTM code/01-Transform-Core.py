"""RTM-Wiki · 03-Animations/Transforms/01-Transform-Core — page-specific sample

Demonstrated parameters (each row of the page's "Parameters" tables):
    Transform(mobject, target_mobject, path_func, path_arc, path_arc_axis,
              path_arc_centers, replace_mobject_with_target_in_scene)
        ✓ step 1: square -> circle (shape / position / colour all change), path_arc=PI/2 follows a 90° arc
        ✓ step 2: path_func=arc_up switches to a custom path function (the points arc upward while interpolating)
        ✓ replace_mobject_with_target_in_scene=False: when done the source stays in the scene (already shaped like the target)
    ReplacementTransform(mobject, target_mobject)
        ✓ when done the source disappears and the target takes over the scene (internally fixes replace_mobject_with_target_in_scene=True)
    MoveToTarget(mobject) (call generate_target() first to set up mobject.target)
        ✓ position / colour / size all morph into the target

Not demonstrated: path_arc_centers — RTM's own Transform (real_time_manim/animations/transform.py)
        only stores it; the path is actually decided by path_func / path_arc, so passing a
        non-None value makes no visual difference;
        path_arc_axis — only affects the rotation axis of a 3D arc; in a 2D frame changing the
        axis swings the arc off screen, so there is nothing to compare (this clip passes OUT
        explicitly, matching the default).

Run: $env:PYTHONPATH="C:\\Users\\begin\\Desktop\\real-time-manim"; python "<this file>"
"""
import os

import numpy as np
from real_time_manim import (
    BLUE,
    GREEN,
    GREY_B,
    ORANGE,
    RED,
    YELLOW,
    DOWN,
    LEFT,
    OUT,
    RIGHT,
    UP,
    PI,
    Circle,
    Scene,
    Square,
    Text,
    Triangle,
    VGroup,
    smooth,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    Create,
    FadeIn,
    FadeOut,
    MoveToTarget,
    ReplacementTransform,
    Transform,
    Wait,  # noqa: F401
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


def arc_up(start_pts, end_pts, alpha):
    """Custom path_func: (start_pts, end_pts, alpha) -> pts; the points arc upward while interpolating."""
    pts = start_pts + (end_pts - start_pts) * alpha
    return pts + np.array([0.0, 1.1 * np.sin(np.pi * alpha), 0.0])


class Page_01_Transform_Core(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # params w / h / hidden
        win.scene = self                          # param win.scene

        title = Text("Transform core · turn A into B", font_size=44, color=ORANGE).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        # --- 1. Transform: every documented parameter passed explicitly; source and target differ in shape / position / colour ---
        lab1 = VGroup(
            Text("Transform(sq, circ, path_arc=PI / 2,", font_size=30, color=GREY_B),
            Text("  path_func=None, path_arc_axis=OUT,", font_size=30, color=GREY_B),
            Text("  replace_mobject_with_target_in_scene=False)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.3)
        sq = Square(side_length=1.5, color=BLUE).set_fill(BLUE, 0.6).move_to(LEFT * 3.6 + DOWN * 1.2)
        circ = Circle(radius=0.8, color=GREEN).set_fill(GREEN, 0.6).move_to(RIGHT * 2.8 + DOWN * 0.4)
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)
        win.play(Create(sq), run_time=0.5)
        win.play(                                                    # point-set interpolation plus an arc path
            Transform(sq, circ,                                     # params mobject / target_mobject ✓
                      path_func=None,                               # param path_func=None ✓ (the next step swaps in a custom function)
                      path_arc=PI / 2,                              # param path_arc ✓ (non-default 0: follows a 90° arc)
                      path_arc_axis=OUT,                            # param path_arc_axis ✓ (always the z-axis in 2D)
                      path_arc_centers=None,                        # param path_arc_centers ✓ (see "Not demonstrated")
                      replace_mobject_with_target_in_scene=False,   # param ✓ (default; when done the source stays in the scene)
                      run_time=1.5),                                # param run_time / **kwargs ✓
            run_time=1.5,
        )
        win.play(FadeOut(VGroup(lab1, sq)), run_time=0.5)

        # --- 2. Transform's path_func: a custom interpolation path ---
        lab2 = VGroup(
            Text("Transform(sq2, tri, path_func=arc_up,", font_size=30, color=GREY_B),
            Text("                      run_time=1.3)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        sq2 = Square(side_length=1.2, color=YELLOW).set_fill(YELLOW, 0.6).move_to(LEFT * 3.6 + DOWN * 1.2)
        tri = Triangle(color=RED).scale(0.8).set_fill(RED, 0.6).move_to(RIGHT * 3.2 + DOWN * 1.2)
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)
        win.play(Create(sq2), run_time=0.5)
        win.play(                                     # the interpolated points arc up along the custom path, then come back down
            Transform(sq2, tri, path_func=arc_up, run_time=1.3),
            run_time=1.3,
        )
        win.play(FadeOut(VGroup(lab2, sq2)), run_time=0.5)

        # --- 3. ReplacementTransform: when done the source disappears and the target takes over the scene ---
        lab3 = VGroup(
            Text("ReplacementTransform(left, right,", font_size=30, color=GREY_B),
            Text("                     run_time=1.2)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        left = Text("left", font_size=44, color=BLUE).move_to(LEFT * 3.2 + DOWN * 1.2)
        right = Text("right", font_size=44, color=GREEN).move_to(RIGHT * 3.2 + DOWN * 1.2)
        self.add(left)                              # put the source object into the scene first
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)
        win.play(ReplacementTransform(left, right, run_time=1.2), run_time=1.2)
        win.play(FadeOut(VGroup(lab3, right)), run_time=0.5)

        # --- 4. MoveToTarget: call generate_target() to set up .target first, then play ---
        lab4 = VGroup(
            Text("sq3.generate_target(); sq3.target.shift(", font_size=30, color=GREY_B),
            Text("  RIGHT * 3).scale(1.6).set_fill(GREEN, 0.6)", font_size=30, color=GREY_B),
            Text("MoveToTarget(sq3, run_time=1.3)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.3)
        sq3 = Square(side_length=0.9, color=YELLOW).set_fill(YELLOW, 0.6).move_to(LEFT * 3.4 + DOWN * 1.4)
        win.play(FadeIn(lab4, shift=DOWN), run_time=0.4)
        win.play(Create(sq3), run_time=0.5)
        sq3.generate_target()                       # param mobject.target ✓ (set up the target state first)
        sq3.target.shift(RIGHT * 3).scale(1.6).set_fill(GREEN, 0.6)
        win.play(MoveToTarget(sq3, run_time=1.3), run_time=1.3)

        win.play(FadeOut(VGroup(title, lab4, sq3)), run_time=0.6)
        win.close()                                 # param win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(
        Page_01_Transform_Core,
        out_path=os.path.join(os.path.dirname(here), "RTM output", "01-Transform-Core.mp4"),
        fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True,
    )
