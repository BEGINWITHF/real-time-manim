# -*- coding: utf-8 -*-
"""Full source of the three samples in 01-Scene-Basics.md (identical to the code blocks in the page).

Usage: python 01-Scene-Basics.py <scene name>...
With no arguments it renders every clip and concatenates the page's three videos (RTM version).
"""
import os
import random
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
    Square, Text, VGroup,
    BLUE, RED, GREEN, YELLOW, WHITE,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, Create, linear,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: the Scene.__init__ constructor parameters ==================
class CtorDemo(Scene):
    SEED = 1   #random seed: change it to 7 and run again; the color order of the five squares changes

    def __init__(self, **kwargs):
        super().__init__(random_seed=self.SEED, **kwargs)   #pass "random_seed" to Scene.__init__

    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim scene named "self" to the RTM window named "win"
        info = VGroup(
            Text("random_seed=%d" % self.SEED, font_size=36, color=YELLOW),
            Text("camera_class=%s" % type(self.camera).__name__, font_size=28, color=WHITE),
            Text("always_update_mobjects=%s  skip_animations=%s" % (
                self.always_update_mobjects, self.skip_animations), font_size=22, color=GREEN),
        ).arrange(DOWN, buff=0.15).to_edge(UP)   #three label lines: print the current constructor parameter values on screen
        order = [0, 1, 2, 3, 4]   #prepare an index list 0..4
        random.shuffle(order)   #shuffle; the result is determined only by "random_seed"
        colors = [BLUE, RED, GREEN, YELLOW, WHITE]   #five colors
        row = VGroup(*[Square(color=colors[i], side_length=0.9) for i in order])   #create squares in the shuffled index order
        row.arrange(RIGHT, buff=0.3).to_edge(DOWN)   #arrange left to right in a row; color order = shuffle order
        self.add(info, row)   #add the labels and this row of squares to the scene
        win.play(FadeIn(row), run_time=0.5)   #fade in the whole row
        win.play(Wait(0.5))   #wait 0.5s
        win.close()   #close the RTM window


class CtorDemo7(CtorDemo):
    SEED = 7   #same scene, only "random_seed" changed to 7


# ===== Sample 2: scene lifecycle setup / construct / tear_down ==============
class LifeDemo(Scene):
    def setup(self):
        self.square = Square(color=BLUE)   #setup runs before construct; use it to prepare shared objects

    def tear_down(self):
        print("tear_down ran")   #(RTM calls this too since 2026-10-16: the record lifecycle's try/finally guarantees one run)

    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim scene named "self" to the RTM window named "win"
        title = Text("setup -> construct", font_size=40, color=YELLOW).to_edge(UP)   #on-screen title
        self.add(title)   #add the title to the scene
        win.play(Create(self.square), run_time=0.8)   #draw the square prepared in setup()
        win.play(Wait(0.5))   #wait 0.5s
        win.close()   #close the RTM window


# ===== Sample 3: Scene.camera / Scene.time =================================
class TimeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim scene named "self" to the RTM window named "win"
        sq = Square(color=GREEN).shift(DOWN)   #a square that moves, proving time really passes
        label = Text("scene.time = 0.00", font_size=40, color=YELLOW).to_edge(UP)   #label showing self.time

        def show_time(m):   #refresh "self.time" into the label every frame
            m.become(Text("scene.time = %.2f" % self.time, font_size=40, color=YELLOW).to_edge(UP))

        label.add_updater(show_time)   #mobject-level updater: RTM drives it every frame
        self.add(sq, label)   #add the square and the label to the scene
        win.play(sq.animate.shift(RIGHT * 4), run_time=0.8, rate_func=linear)   #the square moves right at constant speed
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


PAGE = "01-Scene-Basics"

SCENES = [
    ("ctor_seed1", CtorDemo),
    ("ctor_seed7", CtorDemo7),
    ("life", LifeDemo),
    ("time", TimeDemo),
]

SAMPLES = [
    ("ctor", ["ctor_seed1", "ctor_seed7"]),
    ("life", ["life"]),
    ("time", ["time"]),
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
