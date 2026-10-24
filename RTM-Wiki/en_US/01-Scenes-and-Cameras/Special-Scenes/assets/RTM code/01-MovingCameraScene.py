# -*- coding: utf-8 -*-
"""Full source for the three samples in 01-MovingCameraScene.md (identical to the code blocks in the page).

Usage: python 01-MovingCameraScene.py <clip names>...
With no arguments it renders all 7 clips and concatenates the page's three comparison videos.
"""
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
ASSETS = os.path.dirname(HERE)
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    MovingCameraScene, MovingCamera, Camera,
    Square, Text, VGroup,
    BLUE, RED, GREEN, YELLOW, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    FadeIn, Restore,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: camera_class =============================================
class CameraClassDemo(MovingCameraScene):
    CAM = MovingCamera   # camera class: change it to "Camera" and rerun, the view frame disappears

    def __init__(self, **kwargs):
        super().__init__(camera_class=self.CAM, **kwargs)   # pass "camera_class" to Scene.__init__

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        left = Square(color=BLUE, side_length=2).shift(LEFT * 4)   # blue square on the left of the frame
        right = Square(color=RED, side_length=2).shift(RIGHT * 4)   # red square on the right of the frame
        head = VGroup(
            Text(type(self.camera).__name__, font_size=28, color=YELLOW),   # line 1: the current camera class name
            Text("frame=%s" % hasattr(self.camera, "frame"), font_size=22, color=GREEN),   # line 2: is there a view frame
        ).arrange(DOWN, buff=0.1)   # stack the two lines vertically
        head.move_to(left)   # put the two lines inside the left square; they scale up too when the camera zooms in
        self.add(left, right, head)   # add the three objects to the scene
        win.play(FadeIn(left), run_time=0.4)   # fade in the left square
        if hasattr(self.camera, "frame"):   # only "MovingCamera" has "frame"; a plain "Camera" never enters this branch
            win.play(self.camera.frame.animate.set(width=4.0).move_to(left), run_time=0.8)   # shrink the frame to 4 and move it left = zoom in
            win.play(self.camera.frame.animate.set(width=14.0).move_to(ORIGIN), run_time=0.8)   # grow the frame to 14 and recentre = zoom back out
        win.play(Wait(0.5))   # wait 0.5s
        win.close()   # close the RTM window


class CameraClassPlain(CameraClassDemo):
    CAM = Camera   # just swap "MovingCamera" for "Camera"


# ===== Sample 2: **kwargs -> random_seed ==================================
class RandomSeedDemo(MovingCameraScene):
    SEED = 1   # random seed: change it to 7 and rerun, the color order of the row of squares changes

    def __init__(self, **kwargs):
        super().__init__(random_seed=self.SEED, **kwargs)   # forward "random_seed" to Scene.__init__

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        tag = Text("random_seed=%d" % self.SEED, font_size=40, color=YELLOW).to_edge(UP)   # show the current seed at the top of the screen
        order = [0, 1, 2, 3, 4]   # prepare an index list 0~4
        random.shuffle(order)   # shuffle; the result is decided by the constructor parameter "random_seed"
        colors = [BLUE, RED, GREEN, YELLOW, WHITE]   # five colors
        g = VGroup(*[Square(color=colors[i], side_length=0.9) for i in order])   # build squares from the shuffled indices
        g.arrange(RIGHT, buff=0.3).to_edge(DOWN)   # one row from left to right; color order = shuffle order
        self.add(tag, g)   # add the label and the row of squares to the scene
        print("random_seed=%d shuffled order =" % self.SEED, order)   # print the order to the console for comparison
        win.play(FadeIn(g), run_time=0.5)   # fade in the whole row
        win.play(Wait(0.5))   # wait 0.5s
        win.close()   # close the RTM window


class RandomSeedDemo7(RandomSeedDemo):
    SEED = 7   # the same scene with only "random_seed" changed to 7


# ===== Sample 3: self.camera.frame ========================================
class FrameDemo(MovingCameraScene):
    WIDTH = 4.0   # view-frame width: set it to 2.0 for a closer step, 14.0 for the full view

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        a = Square(color=BLUE, side_length=1.5).shift(LEFT * 1.5)   # the left target
        b = Square(color=RED, side_length=1.5).shift(RIGHT * 1.5)   # the right target
        t = Text("width=%.1f" % self.WIDTH, font_size=32, color=WHITE)   # show the current view-frame width

        def pin(m):   # keep the label at the bottom of the view frame and scale it with the frame width, so its on-screen size never changes
            m.width = self.camera.frame.width * 0.28
            m.move_to(self.camera.frame.get_bottom() + UP * (
                m.height * 0.5 + self.camera.frame.height * 0.08))

        t.add_updater(pin)   # pin the width label to the bottom of the view frame
        self.add(a, b, t)   # add the three objects to the scene
        print("initial frame: height=%.3f width=%.3f" % (
            self.camera.frame.height, self.camera.frame.width))   # default height 8.0, width 14.222
        self.camera.frame.save_state()   # remember the current (full-view) state so Restore can bring it back later
        win.play(self.camera.frame.animate.set(width=self.WIDTH), run_time=0.8)   # change only the width = zoom only, the frame centre does not move
        win.play(self.camera.frame.animate.move_to(a), run_time=0.8)   # change only the centre = pan only, the zoom does not change
        print("after frame: height=%.3f width=%.3f" % (
            self.camera.frame.height, self.camera.frame.width))   # the width is still the value set above, the centre has moved to a
        win.play(Restore(self.camera.frame), run_time=0.8)   # back to the full view from save_state
        win.play(Wait(0.5))   # wait 0.5s
        win.close()   # close the RTM window


class FrameDemo2(FrameDemo):
    WIDTH = 2.0   # one step closer


class FrameDemo14(FrameDemo):
    WIDTH = 14.0   # the full view


SCENES = [
    ("camera_class_moving", CameraClassDemo),
    ("camera_class_plain", CameraClassPlain),
    ("random_seed_1", RandomSeedDemo),
    ("random_seed_7", RandomSeedDemo7),
    ("frame_width_4", FrameDemo),
    ("frame_width_2", FrameDemo2),
    ("frame_width_14", FrameDemo14),
]

PAIRS = [
    ("camera_class", ["camera_class_moving", "camera_class_plain"]),
    ("random_seed", ["random_seed_1", "random_seed_7"]),
    ("camera_frame", ["frame_width_14", "frame_width_4", "frame_width_2"]),
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
        for out_name, names in PAIRS:
            dst = os.path.join(ASSETS, "RTM output", out_name + ".mp4")
            concat(names, dst)
            print("concat ->", dst, os.path.getsize(dst), "bytes")
