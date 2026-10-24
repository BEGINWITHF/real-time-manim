# -*- coding: utf-8 -*-
"""Full source of the three samples in 03-Play-and-Wait.md (identical to the code blocks in the page).

Usage: python 03-Play-and-Wait.py <scene name>...
With no arguments it renders every clip and concatenates the page's three videos (RTM version).
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    Scene,
    Square, Circle, Text,
    BLUE, RED, GREEN, YELLOW,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, Write, linear,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: win.play *args / run_time / rate_func / .animate ===========
class PlayDemo(Scene):
    RUN_TIME = 0.6   #animation duration: change it to 1.2 to see a half-speed version

    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim scene named "self" to the RTM window named "win"
        a = Circle(color=RED).shift(LEFT * 2.5)   #the circle on the left
        b = Square(color=GREEN).shift(RIGHT * 2.5)   #the square on the right
        self.add(a, b)   #put both objects on screen
        win.play(FadeIn(a), FadeIn(b), run_time=self.RUN_TIME)   #several animations in one play = played in parallel
        win.play(a.animate.shift(RIGHT * 1.2), run_time=self.RUN_TIME, rate_func=linear)   #".animate" builder + linear rate
        win.play(a.animate.shift(LEFT * 1.2), run_time=self.RUN_TIME)   #default smooth rate: slow at both ends, fast in the middle
        win.play(Write(Text("win.play", font_size=42, color=YELLOW).to_edge(DOWN)), run_time=self.RUN_TIME)   #Write writing animation
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


# ===== Sample 2: four ways to wait =========================================
class WaitDemo(Scene):
    FLAVOR = "play_wait"   #wait form: four flavors, see the subclasses below

    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   #self.wait / self.pause / self.wait_until all call self.play internally, so wire it up first
        tag = Text(self.FLAVOR, font_size=40, color=YELLOW).to_edge(UP)   #show the current form at the top of the screen
        sq = Square(color=BLUE).shift(DOWN)   #a static square, to make it clear the picture really doesn't move during the wait
        self.add(tag, sq)   #add the label and the square to the scene
        win.play(FadeIn(sq), run_time=0.3)   #fade in for 0.3s first
        if self.FLAVOR == "play_wait":
            win.play(Wait(0.5))   #RTM form: win.play(Wait(seconds))
        elif self.FLAVOR == "self_wait":
            self.wait(0.5)   #manim form: forwarded through self.play, waits 0.5s
        elif self.FLAVOR == "self_pause":
            self.pause(0.3)   #a pause that freezes the picture, waits 0.3s
        else:
            self.wait_until(lambda: True, max_time=0.3)   #conditional wait; the condition is true after the first frame, so the wait ends immediately
        win.close()   #close the RTM window


class WaitSelf(WaitDemo):
    FLAVOR = "self_wait"   #switch to self.wait


class WaitPause(WaitDemo):
    FLAVOR = "self_pause"   #switch to self.pause


class WaitUntil(WaitDemo):
    FLAVOR = "wait_until"   #switch to self.wait_until


# ===== Sample 3: Scene.add_updater / Scene.remove_updater ==================
class UpdaterDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   #a scene method calls self.play internally, so wire it up first
        mob = Square(color=BLUE).shift(LEFT * 3 + DOWN * 2)   #a square driven by a mobject-level updater
        via_scene = Square(color=RED).shift(RIGHT * 3 + DOWN * 2)   #a square driven by a scene-level updater
        self.add(mob, via_scene)   #put both squares on screen
        self.add(Text("mobject.add_updater", font_size=24, color=BLUE).next_to(mob, UP))   #label on the left
        self.add(Text("scene.add_updater", font_size=24, color=RED).next_to(via_scene, UP))   #label on the right
        mob.add_updater(lambda m, dt: m.shift(UP * 0.03))   #mobject level: RTM drives it every frame, the square keeps moving up

        def scene_updater(dt):   #scene level: RTM drives it every frame
            via_scene.shift(UP * 0.03)

        self.add_updater(scene_updater)   #register the function on the scene
        win.play(Wait(0.5))   #wait 0.5s: the blue square moves up and the red square too
        self.remove_updater(scene_updater)   #remove the scene-level updater
        mob.clear_updaters()   #remove the mobject-level updater, the blue square stops
        win.play(Wait(0.5))   #wait another 0.5s: neither square moves
        win.close()   #close the RTM window


PAGE = "03-Play-and-Wait"

SCENES = [
    ("play", PlayDemo),
    ("wait_play", WaitDemo),
    ("wait_self", WaitSelf),
    ("wait_pause", WaitPause),
    ("wait_until", WaitUntil),
    ("updater", UpdaterDemo),
]

SAMPLES = [
    ("play", ["play"]),
    ("wait", ["wait_play", "wait_self", "wait_pause", "wait_until"]),
    ("updater", ["updater"]),
]


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
        for out_name, names in SAMPLES:
            dst = os.path.join(ASSETS, "RTM output", "%s-%s.mp4" % (PAGE, out_name))
            concat(names, dst)
            print("concat ->", dst, os.path.getsize(dst), "bytes")
            if len(names) > 1:
                #multi-clip sample: copy each clip into assets/ too, for segment-by-segment comparison
                for n in names:
                    shutil.copyfile(os.path.join(OUT, n + ".mp4"),
                                    os.path.join(ASSETS, "%s-%s.mp4" % (PAGE, n)))
