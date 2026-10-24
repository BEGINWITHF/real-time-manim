# -*- coding: utf-8 -*-
"""Full source for the three samples in 02-Vector-Fields-and-Streamlines.md (character-for-character identical to the code blocks in the page).

Usage: python 02-Vector-Fields-and-Streamlines.py <clip-name>...
With no arguments it renders every clip and concatenates the three sample videos shown in the page (written to the parent assets/).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

import numpy as np
from real_time_manim import (
    Scene, Text, VGroup, Dot, Line, ArrowVectorField,
    RED, ORANGE, GREEN, YELLOW, GREY_B, UP, DOWN, LEFT, RIGHT,
    Write, FadeIn, Create,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: ArrowVectorField constructor parameters ===================
class ArrowVectorFieldDemo(Scene):
    TUNED = False   # False uses the default coloring and length func; True switches to a single color + linear length

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02-ArrowVectorField", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = Text(
            "color=RED, length_func=lambda x: x/3, vector_config={stroke_width:2}"
            if self.TUNED else "default: color=norm gradient, length_func=0.45*sigmoid",
            font_size=24, color=GREY_B,
        ).next_to(title, DOWN, buff=0.3)   # show the current constructor parameters
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        func = lambda pos: np.sin(pos[1] / 2) * RIGHT + np.cos(pos[0] / 2) * UP   # field function: position -> vector
        if self.TUNED:
            vf = ArrowVectorField(
                func,                                   # parameter "func"
                x_range=[-4, 4, 1], y_range=[-2.5, 2.5, 1],   # sampling grid
                color=RED,                              # parameter "color": whole field single-colored
                length_func=lambda x: x / 3,            # parameter "length_func": constant linear length
                vector_config={"stroke_width": 2},      # parameter "vector_config"
            )
        else:
            vf = ArrowVectorField(
                func,                                   # parameter "func"
                x_range=[-4, 4, 1], y_range=[-2.5, 2.5, 1],   # sampling grid
            )
        win.play(FadeIn(vf), run_time=0.8)   # the whole arrow field fades in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


class ArrowVectorFieldTuned(ArrowVectorFieldDemo):
    TUNED = True   # same field: single color + linear length func + thin shafts


# ===== Sample 2: nudge one-step and continuous updater =====================
class NudgeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02-VectorField-nudge", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = VGroup(
            Text("vf.nudge(dot, dt=1, substeps=20)   # one RK4 step",
                 font_size=26, color=GREY_B),
            Text("dot.add_updater(vf.get_nudge_updater(speed=1))",
                 font_size=26, color=GREY_B),
        ).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.3)   # two-line signature label
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        func = lambda pos: np.sin(pos[1] / 2) * RIGHT + np.cos(pos[0] / 2) * UP   # field function
        vf = ArrowVectorField(func, x_range=[-4, 4, 1], y_range=[-2.5, 2.5, 1],
                              opacity=0.4)   # a semi-transparent field as the background
        dot = Dot(radius=0.12, color=RED).move_to([-3.5, -1.4, 0])   # starting point
        win.play(FadeIn(vf), FadeIn(dot), run_time=0.5)   # the field and the red dot fade in
        start = dot.get_center().copy()   # remember the start point
        vf.nudge(dot, dt=1, substeps=20)   # parameters "dt" / "substeps": one big RK4 step (instant, no animation)
        step = Line(start, dot.get_center(), stroke_width=4, color=ORANGE)   # draw this step's displacement
        win.play(Create(step), run_time=0.4)   # the orange segment marks the one-step displacement
        win.play(Wait(0.3))   # wait for 0.3 s
        dot.add_updater(vf.get_nudge_updater(speed=1))   # parameter "speed": switch to continuous flow along the field
        win.play(Wait(2.0))   # the red dot flows along the field for 2 seconds
        dot.clear_updaters()   # detach the updater; the dot stops
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


# ===== Sample 3: submobject group drift ====================================
class SubmobjectMoveDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02-VectorField-submobjects", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = Text("vf.start_submobject_movement(speed=1.5) ... stop_...()",
                   font_size=26, color=GREY_B).next_to(title, DOWN, buff=0.3)   # signature label
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        func = lambda pos: np.sin(pos[1] / 2) * RIGHT + np.cos(pos[0] / 2) * UP   # field function
        vf = ArrowVectorField(func, x_range=[-4, 4, 1.5], y_range=[-2.25, 2.25, 1.5],
                              color=GREEN)   # a slightly sparser green arrow grid
        win.play(FadeIn(vf), run_time=0.5)   # the whole arrow field fades in
        vf.start_submobject_movement(speed=1.5)   # parameter "speed": all arrows drift along the field together
        win.play(Wait(2.0))   # drift for 2 seconds
        vf.stop_submobject_movement()   # stop at the current position
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


SCENES = [
    ("field_default", ArrowVectorFieldDemo),
    ("field_tuned", ArrowVectorFieldTuned),
    ("nudge", NudgeDemo),
    ("submobject", SubmobjectMoveDemo),
]

PAIRS = [
    ("field", ["field_default", "field_tuned"]),
    ("nudge", ["nudge"]),
    ("submobject", ["submobject"]),
]

PAGE = "02-Vector-Fields-and-Streamlines"


def concat(names, dst):
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    lst = os.path.join(HERE, "concat.txt")
    with open(lst, "w", encoding="utf-8") as fh:
        for n in names:
            fh.write("file '%s'\n" % os.path.join(OUT, n + ".mp4"))
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", lst, "-c", "copy", dst],
        check=True)
    return dst


if __name__ == "__main__":
    only = set(sys.argv[1:])
    for name, cls in SCENES:
        if only and name not in only:
            continue
        print("=" * 30, name)
        try:
            fast_record_scene(cls, out_path=os.path.join(OUT, name + ".mp4"),
                              verbose=True)
        except Exception:
            import traceback
            traceback.print_exc()

    if not only:
        for out_name, names in PAIRS:
            dst = os.path.join(ASSETS, "RTM output", "%s-%s.mp4" % (PAGE, out_name))
            concat(names, dst)
            print("concat ->", dst, os.path.getsize(dst), "bytes")
