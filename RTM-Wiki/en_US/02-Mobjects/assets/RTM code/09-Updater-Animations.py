# -*- coding: utf-8 -*-
"""Full source of the three samples in 09-Updater-Animations.md (identical to the code blocks in the page).

Usage: python 09-Updater-Animations.py <clip name>...
With no arguments it renders every clip and concatenates the page's three sample videos (output to the parent assets/).
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

from real_time_manim import (
    Scene, Square, Circle, Dot, DecimalNumber,
    BLUE, RED, GREEN, YELLOW, PURPLE, WHITE,
    UP, DOWN, LEFT, RIGHT, FadeIn, interpolate_color,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene
from real_time_manim import UpdateFromFunc, UpdateFromAlphaFunc, MaintainPositionRelativeTo


# ===== Sample 1: UpdateFromFunc ==========================================
class UpdateFromFuncDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        dot = Dot(color=YELLOW, radius=0.12).shift(LEFT * 4.0)   # yellow dot
        lab = DecimalNumber(0, num_decimal_places=2, color=WHITE).scale(0.7)   # readout label
        lab.to_edge(UP, buff=0.5)   # put it at the top first
        self.add(dot, lab)   # add to the scene

        def follow(m):   # called every frame during the animation: pin the label above the dot and show the dot's x coordinate
            m.move_to(dot.get_center() + UP * 1.2)
            m.set_value(round(float(dot.get_x()), 2))

        win.play(dot.animate.shift(RIGHT * 8.0), run_time=1.2)   # the dot crosses the screen (label not attached yet)
        win.play(UpdateFromFunc(lab, follow), dot.animate.shift(LEFT * 8.0), run_time=1.2)   # drive the label every frame for the whole animation
        win.play(Wait(0.3))   # pause 0.3s
        win.close()   # close the RTM window


# ===== Sample 2: UpdateFromAlphaFunc =====================================
class UpdateAlphaDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.2, fill_opacity=0.7)   # blue square
        self.add(sq)   # add to the scene
        start = sq.get_center().copy()   # remember the start point

        def morph(m, alpha):   # interpolate by progress: colour blue→red, move right
            m.set_color(interpolate_color(BLUE, RED, alpha))
            m.move_to(start + alpha * RIGHT * 3.0)

        win.play(UpdateFromAlphaFunc(sq, morph, suspend_mobject_updating=False), run_time=1.0)   # alpha goes 0→1 after rate_func
        win.play(Wait(0.3))   # pause 0.3s
        win.close()   # close the RTM window


# ===== Sample 3: MaintainPositionRelativeTo ==============================
class MaintainDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        ref = Square(color=GREEN, side_length=1.0, fill_opacity=0.6).shift(LEFT * 3.5)   # reference square
        sat = Circle(color=PURPLE, radius=0.35)   # satellite
        sat.next_to(ref, UP, buff=0.25)   # snap it above the reference first: this is the relative position to keep
        self.add(ref, sat)   # add to the scene
        win.play(MaintainPositionRelativeTo(sat, ref), ref.animate.shift(RIGHT * 7.0), run_time=1.2)   # the relative position stays: they move together
        win.play(Wait(0.3))   # pause 0.3s
        win.close()   # close the RTM window


SCENES = [
    ("update_func", UpdateFromFuncDemo),
    ("update_alpha", UpdateAlphaDemo),
    ("maintain", MaintainDemo),
]

PAIRS = [
    ("update_func", ["update_func"]),
    ("update_alpha", ["update_alpha"]),
    ("maintain", ["maintain"]),
]

PAGE = "09-Updater-Animations"


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
