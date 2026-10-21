# -*- coding: utf-8 -*-
"""Full source of the three samples in 10-ValueTracker.md (identical to the code blocks in the page).

Usage: python 10-ValueTracker.py <clip name>...
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
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    Scene, Dot, DecimalNumber, ValueTracker, ComplexValueTracker,
    BLUE, YELLOW, UP, DOWN, LEFT, RIGHT, FadeIn, straight_path,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: construction and set_value / increment_value ============
class BasicDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        tracker = ValueTracker(0.0)   # initial value 0
        lbl = DecimalNumber(0, num_decimal_places=2, color=YELLOW).scale(0.8).to_edge(UP, buff=0.5)   # readout label
        lbl.add_updater(lambda d: d.set_value(round(float(tracker.get_value()), 2)))   # read the value every frame and display it
        self.add(lbl, tracker)   # tracker must be added to the scene to be driven
        win.play(tracker.animate.set_value(5.0), run_time=0.8)   # animated value change: 0 → 5
        win.play(tracker.animate.increment_value(-2.0), run_time=0.6)   # animated increment: -2
        tracker += 2.0   # change the value in place instantly (the += in-place version)
        print("after += :", tracker.get_value())   #5.0
        print("(tracker * 3).get_value() =", (tracker * 3).get_value())   #* → a new object, the original is unchanged
        print("- / / / // / % / ** =", (tracker - 1).get_value(), (tracker / 2).get_value(), (tracker // 2).get_value(), (tracker % 2).get_value(), (tracker ** 2).get_value())   #each arithmetic operator → a new ValueTracker
        print("bool(tracker) =", bool(tracker))   #bool is equivalent to bool(get_value())
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window


# ===== Sample 2: interpolate =============================================
class InterpolateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        tracker = ValueTracker(0.0)   # number tracker
        lbl = DecimalNumber(0, num_decimal_places=2, color=YELLOW).scale(0.8).to_edge(UP, buff=0.5)   # readout label
        lbl.add_updater(lambda d: d.set_value(round(float(tracker.get_value()), 2)))   # read the value every frame and display it
        self.add(lbl, tracker)   # add to the scene
        win.play(tracker.animate.set_value(4.0), run_time=0.6)   # animate to 4.0 first
        tracker.interpolate(ValueTracker(0.0), ValueTracker(2.0), 0.5, path_func=straight_path())   # take the interpolation of 0 and 2 at 0.5 directly (instant)
        print("after interpolate =", tracker.get_value())   #1.0
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window


# ===== Sample 3: ComplexValueTracker =====================================
class ComplexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        ct = ComplexValueTracker(-2 + 1j)   # complex tracker: the value is stored internally as [real, imaginary, 0]
        cdot = Dot(color=BLUE, radius=0.12)   # blue dot
        cdot.add_updater(lambda x: x.move_to(ct.points))   # the dot follows the internal coordinate directly
        self.add(cdot, ct)   # add to the scene
        win.play(ct.animate.set_value(3 + 2j), run_time=1.0)   # animated value change: the dot moves from (-2, 1) to (3, 2)
        cdot.clear_updaters()   # stop following
        print("ct.get_value() =", ct.get_value())   #3+2j
        #cannot be demonstrated: arithmetic like ct * 1j / ct + 1
        #    TypeError: float() argument must be a string or a real number, not 'complex'
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window


SCENES = [
    ("basic", BasicDemo),
    ("interpolate", InterpolateDemo),
    ("complex", ComplexDemo),
]

PAIRS = [
    ("basic", ["basic"]),
    ("interpolate", ["interpolate"]),
    ("complex", ["complex"]),
]

PAGE = "10-ValueTracker"


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
