# -*- coding: utf-8 -*-
"""Full source of the three samples in 07-animate-Syntax.md (identical to the code blocks in the page).

Usage: python 07-animate-Syntax.py <clip name>...
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
    Scene, Square, Rectangle,
    PURPLE, TEAL, RED, ORANGE,
    UP, DOWN, LEFT, RIGHT, PI, FadeIn, FadeOut, Transform,
    there_and_back, override_animate,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: .animate basics ==========================================
class AnimateBasicDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        s = Square(color=RED, side_length=1.2, fill_opacity=0.6).shift(LEFT * 3.5)   #red square
        self.add(s)   #add to the scene
        win.play(s.animate.shift(RIGHT * 1.6), run_time=0.5)   #the plainest ".animate": a shift
        win.play(s.animate.scale(1.5).rotate(PI / 6), run_time=0.6)   #chained: one animation in two steps
        win.play(s.animate(run_time=0.8, rate_func=there_and_back).shift(DOWN), run_time=0.8)   #play parameters right after ".animate"
        rect = Rectangle(width=2.0, height=1.0, color=ORANGE, fill_opacity=0.6).shift(RIGHT * 3.5)   #orange rectangle
        self.add(rect)   #add to the scene
        win.play(rect.animate.set(width=5.0), run_time=0.5)   #set with animate: size to the target dimensions
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


# ===== Sample 2: override_animate ========================================
class PulseSquare(Square):   #a custom subclass: pair a plain method with a dedicated animation
    def pulse(self, scale_factor):   #plain call: scale directly (instantly)
        self.scale(scale_factor)

    @override_animate(pulse)   #tell "pulse" which animation to play on an ".animate" call
    def _pulse_animation(self, scale_factor, anim_args=None):   #parameters match the original method, plus anim_args
        if anim_args is None:
            anim_args = {}
        target = self.copy().scale(scale_factor)   #target shape
        return Transform(self, target, **anim_args)   #return the animation: morph over smoothly


class OverrideDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        ds = PulseSquare(color=PURPLE, side_length=1.2, fill_opacity=0.6).shift(LEFT * 3.5)   #left: called directly
        ds2 = PulseSquare(color=PURPLE, side_length=1.2, fill_opacity=0.6).shift(RIGHT * 3.5)   #right: called through animate
        self.add(ds, ds2)   #add to the scene
        ds.pulse(1.4)   #a direct call → goes through the plain method (grows instantly)
        win.play(Wait(0.5))   #see the instant change
        win.play(ds2.animate.pulse(1.4), run_time=0.6)   #an ".animate" call → replaced by the returned animation (smooth)
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


# ===== Sample 3: add_animation_override / animation_override_for =========
class FlashSquare(Square):   #just a carrier class for the registry
    pass


class AddOverrideDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        FlashSquare.add_animation_override(FadeIn, lambda mobject, **kwargs: FadeOut(mobject))   #register: FadeIn becomes FadeOut
        print("override_for(FadeIn) =", FlashSquare.animation_override_for(FadeIn))   #lookup: fetch the registered function
        print("override_for(Transform) =", FlashSquare.animation_override_for(Transform))   #never registered: None
        sq = FlashSquare(color=TEAL, side_length=1.4, fill_opacity=0.7)   #teal square
        self.add(sq)   #add to the scene
        win.play(FadeIn(sq), run_time=0.6)   #the code says FadeIn; the registry swaps in FadeOut (the visible object fades out on the spot)
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


SCENES = [
    ("animate", AnimateBasicDemo),
    ("override", OverrideDemo),
    ("add_override", AddOverrideDemo),
]

PAIRS = [
    ("animate", ["animate"]),
    ("override", ["override"]),
    ("add_override", ["add_override"]),
]

PAGE = "07-animate-Syntax"


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
