# -*- coding: utf-8 -*-
"""Full source of the four samples in 08b-Updater-Utilities.md (identical to the code blocks in the page).

Usage: python 08b-Updater-Utilities.py <clip name>...
With no arguments it renders every clip and concatenates the page's four sample videos (output to the parent assets/).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    Scene, Square, Triangle, Line, Dot, Text, ValueTracker,
    BLUE, RED, GREEN, YELLOW, GREY, ORANGE,
    UP, DOWN, LEFT, RIGHT, PI, TAU, FadeIn, Rotate,
    always_redraw, always, f_always, always_shift, always_rotate,
    turn_animation_into_updater, cycle_animation, assert_is_mobject_method,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: always_redraw ===========================================
class AlwaysRedrawDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        alpha = ValueTracker(0.0)   #value tracker
        track = Line(LEFT * 3.0, RIGHT * 3.0, color=GREY)   #a piece of track
        self.add(track)   #add to the scene
        bead = always_redraw(lambda: Dot(color=RED, radius=0.12).move_to(LEFT * 3.0 + alpha.get_value() * RIGHT))   #redraw the dot from the current value every frame
        self.add(bead)   #add to the scene (the return value is the object with its updater attached)
        win.play(alpha.animate.set_value(6.0), run_time=1.0)   #drive the tracker: the dot travels steadily along the track
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


# ===== Sample 2: always / f_always (module-level functions) ==============
class AlwaysFnDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.2).shift(LEFT * 3.0)   #blue square
        self.add(sq)   #add to the scene
        tag = Text("always", font_size=24, color=YELLOW)   #the upper label
        always(tag.next_to, sq, UP, buff=0.3)   #always: parameters evaluated once at attach time (the reference keeps working)
        self.add(tag)   #add to the scene
        tag2 = Text("f_always", font_size=24, color=GREEN)   #the lower label
        f_always(tag2.next_to, lambda: sq, lambda: DOWN, buff=0.3)   #f_always: the argument generators are re-evaluated every frame
        self.add(tag2)   #add to the scene
        win.play(sq.animate.shift(RIGHT * 2.5), run_time=0.8)   #the two labels, one above and one below, follow the whole time
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


# ===== Sample 3: always_shift / always_rotate ============================
class AlwaysShiftRotateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        tri = Triangle(color=GREEN).set_fill(GREEN, opacity=1).scale(0.8).shift(DOWN * 1.5 + LEFT * 3.0)   #green triangle
        self.add(tri)   #add to the scene
        assert_is_mobject_method(tri.shift)   #argument-checking helper: confirm it is a bound method on a Mobject (returns None)
        print("assert_is_mobject_method -> None")
        always_shift(tri, direction=RIGHT, rate=1.0)   #steady translation right: 1.0 unit per second
        always_rotate(tri, rate=PI / 2)   #steady self-rotation: 90° per second
        win.play(Wait(1.2))   #moving and rotating at once
        tri.clear_updaters()   #stop both updaters together
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


# ===== Sample 4: turn_animation_into_updater / cycle_animation ===========
class AnimUpdaterDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.0).shift(LEFT * 3.5 + UP * 1.5)   #left: ends after one full turn
        self.add(sq)   #add to the scene
        turn_animation_into_updater(Rotate(sq, angle=TAU), cycle=False, delay=0)   #turn the animation into an updater: it advances with the scene time
        win.play(Wait(0.9))   #watch it complete a full turn on its own
        sq2 = Square(color=ORANGE, side_length=1.0).shift(RIGHT * 3.5 + UP * 1.5)   #right: loops forever
        self.add(sq2)   #add to the scene
        cycle_animation(Rotate(sq2, angle=TAU))   #shorthand for cycle=True: it keeps turning forever
        win.play(Wait(0.9))   #watch it keep turning
        sq2.clear_updaters()   #stop it
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


SCENES = [
    ("always_redraw", AlwaysRedrawDemo),
    ("always_fn", AlwaysFnDemo),
    ("always_shift_rotate", AlwaysShiftRotateDemo),
    ("anim_updater", AnimUpdaterDemo),
]

PAIRS = [
    ("always_redraw", ["always_redraw"]),
    ("always_fn", ["always_fn"]),
    ("always_shift_rotate", ["always_shift_rotate"]),
    ("anim_updater", ["anim_updater"]),
]

PAGE = "08b-Updater-Utilities"


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
