# -*- coding: utf-8 -*-
"""Full source of the five samples in 08-Updaters.md (identical to the code blocks in the page).

Usage: python 08-Updaters.py <clip name>...
With no arguments it renders every clip and concatenates the page's five sample videos (output to the parent assets/).
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
    Scene, Square, Dot, Text, DecimalNumber,
    BLUE, RED, GREEN, YELLOW,
    UP, DOWN, LEFT, RIGHT, DEGREES, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: add_updater =============================================
class AddUpdaterDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.0, fill_opacity=0.6).shift(LEFT * 3.5)   #blue square
        self.add(sq)   #add to the scene (an object with an updater must be in the scene to be driven)
        spin = lambda m, dt: m.rotate(dt * 90 * DEGREES)   #time-based f(mob, dt): rotate 90° per second
        sq.add_updater(spin)   #attach the updater
        lbl = DecimalNumber(0, num_decimal_places=2, color=YELLOW).scale(0.7).shift(LEFT * 3.5 + DOWN * 1.6)   #readout label
        val = lambda d: d.set_value(round(float(sq.get_width()), 2))   #non-time-based f(mob): read the square's bounding-box width every frame
        pos = lambda d: d.next_to(sq, DOWN, buff=0.3)   #non-time-based: the label follows the square
        lbl.add_updater(val)   #appended to the end of the list by default
        lbl.add_updater(pos, index=0, call_updater=True)   #insert at the head and run once immediately on attach
        self.add(lbl)   #add the label to the scene
        win.play(Wait(1.0))   #hold for 1 second: the square keeps rotating and the number keeps refreshing
        win.play(sq.animate.shift(RIGHT * 2.0), run_time=0.5)   #updaters keep driving during the animation
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


# ===== Sample 2: remove_updater / clear_updaters ==========================
class RemoveClearDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=GREEN, side_length=1.0, fill_opacity=0.6).shift(LEFT * 3.0)   #green square
        spin = lambda m, dt: m.rotate(dt * 120 * DEGREES)   #keep it named: removal needs the same function object
        sq.add_updater(spin)   #attach
        self.add(sq)   #add to the scene
        print("updaters after attach =", len(sq.get_updaters()))   #1
        win.play(Wait(0.6))   #it starts rotating
        sq.remove_updater(spin)   #remove by the same function object
        print("updaters after remove =", len(sq.get_updaters()))   #0
        sq.add_updater(lambda m, dt: m.shift(DOWN * dt))   #attach another anonymous function: fall 1 per second
        win.play(Wait(0.5))   #it falls
        sq.clear_updaters()   #clear every updater (recursive)
        print("updaters after clear =", len(sq.get_updaters()))   #0
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


# ===== Sample 3: suspend_updating / resume_updating / update =============
class SuspendDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=RED, side_length=1.0, fill_opacity=0.6).shift(UP * 1.5)   #red square
        sq.add_updater(lambda m, dt: m.rotate(dt * 120 * DEGREES))   #rotate 120° per second
        self.add(sq)   #add to the scene
        win.play(Wait(0.5))   #it starts rotating
        sq.suspend_updating(recursive=True)   #pause: the function is still in the list, it just does not run
        win.play(Wait(0.5))   #it stops spinning
        sq.resume_updating(recursive=True)   #resume: run once immediately with dt=0
        win.play(Wait(0.3))   #it spins again
        sq.update(dt=0, recursive=True)   #trigger once by hand (only needed outside the render loop)
        win.play(Wait(0.3))   #wait 0.3s
        win.close()   #close the RTM window


# ===== Sample 4: always (property) =======================================
class AlwaysDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.2, fill_opacity=0.6).shift(LEFT * 3.0)   #blue square
        self.add(sq)   #add to the scene
        tag = Text("tag", font_size=28, color=YELLOW)   #the following label
        tag.always.next_to(sq, UP, buff=0.3)   #sugar: equivalent to add_updater(..., call_updater=True)
        self.add(tag)   #add to the scene
        win.play(sq.animate.shift(RIGHT * 2.5), run_time=0.8)   #the label follows the whole time
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


# ===== Sample 5: queries and match_updaters ==============================
class QueryMatchDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=GREEN, side_length=1.0, fill_opacity=0.6).shift(LEFT * 3.0)   #green square
        spin = lambda m, dt: m.rotate(dt * 90 * DEGREES)   #keep it named
        sq.add_updater(spin)   #attach
        self.add(sq)   #add to the scene
        print("get_updaters =", len(sq.get_updaters()))   #1
        print("get_time_based_updaters =", len(sq.get_time_based_updaters()))   #1
        print("has_time_based_updater =", sq.has_time_based_updater())   #True
        d2 = Dot(color=RED, radius=0.1).shift(RIGHT * 3.0)   #red dot
        d2.match_updaters(sq)   #copy sq's updater list (only sq's own)
        self.add(d2)   #add to the scene
        print("d2 updaters =", len(d2.get_updaters()))   #1
        win.play(Wait(0.8))   #both of them are spinning
        win.close()   #close the RTM window


SCENES = [
    ("add_updater", AddUpdaterDemo),
    ("remove_clear", RemoveClearDemo),
    ("suspend", SuspendDemo),
    ("always", AlwaysDemo),
    ("query_match", QueryMatchDemo),
]

PAIRS = [
    ("add_updater", ["add_updater"]),
    ("remove_clear", ["remove_clear"]),
    ("suspend", ["suspend"]),
    ("always", ["always"]),
    ("query_match", ["query_match"]),
]

PAGE = "08-Updaters"


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
