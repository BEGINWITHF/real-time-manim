# -*- coding: utf-8 -*-
"""Full source of the three samples in 01-Camera.md (identical to the code blocks in the page).

Usage: python 01-Camera.py <clip name>...
With no arguments it renders all 3 scenes and concatenates the page's three videos.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FRAG = os.path.join(HERE, "final",
                       os.path.splitext(os.path.basename(__file__))[0])
ASSETS = os.path.dirname(HERE)
os.makedirs(FRAG, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    BLUE, RED, WHITE, YELLOW,
    DOWN, LEFT, RIGHT, UP,
    Circle, FadeIn, Scene, Square, Text,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: background_color / background_opacity =====================
class BackgroundDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=BLUE).set_fill(BLUE, 0.8)   #a blue square as a reference
        cap = Text("default background", font_size=32, color=YELLOW).to_edge(UP)   #caption at the top
        self.add(sq, cap)   #add the square and the caption to the scene
        win.play(FadeIn(sq), run_time=0.5)   #the square fades in: at this point still the default black background
        win.play(Wait(0.4))   #hold 0.4s
        self.camera.background_color = "#1E3A5F"   #change the background color: the assignment takes effect immediately
        cap.become(Text("background_color = '#1E3A5F'", font_size=32, color=YELLOW).to_edge(UP))   #swap the caption text for the background color
        win.play(Wait(0.8))   #hold 0.8s to see the navy background
        self.camera.background_opacity = 0.6   #change the background opacity: readable and writable
        info = Text("background_opacity = 0.6 (video unchanged)", font_size=26, color=WHITE).next_to(cap, DOWN)   #read the opacity back: the output is an opaque MP4
        self.add(info)   #add the reading to the scene
        win.play(Wait(0.8))   #hold 0.8s: the picture does not fade
        win.close()   #close the RTM window


# ===== Sample 2: is_in_frame =================================================
class IsInFrameDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        near = Square(color=BLUE).set_fill(BLUE, 0.8)   #the square in the middle of the screen: inside the viewfinder
        far = Circle(radius=0.8, color=RED).shift(RIGHT * 10)   #the distant circle: outside the viewfinder
        cap = Text("camera.is_in_frame(mobject) -> bool", font_size=30, color=YELLOW).to_edge(UP)   #caption at the top
        info = Text("square=%s  circle=%s" % (self.camera.is_in_frame(near), self.camera.is_in_frame(far)),
                    font_size=28, color=WHITE).next_to(cap, DOWN)   #first set of readings: square True, circle False
        self.add(near, far, cap, info)   #add the four objects to the scene
        win.play(FadeIn(near), run_time=0.5)   #the square fades in
        win.play(Wait(0.5))   #hold 0.5s
        win.play(near.animate.shift(RIGHT * 8.5), run_time=0.8)   #push the square out of the viewfinder
        info.become(Text("after move: square=%s" % self.camera.is_in_frame(near),
                    font_size=28, color=WHITE).next_to(cap, DOWN))   #second set of readings: the square becomes False
        win.play(Wait(0.8))   #hold 0.8s and wrap up
        win.close()   #close the RTM window


# ===== Sample 3: use_z_index =================================================
class UseZIndexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        a = Square(color=BLUE).set_fill(BLUE, 0.9).shift(LEFT * 0.4)   #the blue square: added to the scene first
        a.z_index = 1   #high z-order: drawn on top when use_z_index=True
        b = Square(color=RED).set_fill(RED, 0.9).shift(RIGHT * 0.4)   #the red square: added to the scene later
        b.z_index = 0   #low z-order: drawn on top only when drawing purely in add order
        cap = Text("use_z_index=True", font_size=32, color=YELLOW).to_edge(UP)   #caption at the top
        self.add(a, b, cap)   #add a then b to the scene
        win.play(Wait(1.0))   #hold 1.0s: blue on top (drawn sorted by z_index)
        self.camera.use_z_index = False   #turn z-order off: switch to drawing in add order
        cap.become(Text("use_z_index=False", font_size=32, color=YELLOW).to_edge(UP))   #swap the caption text accordingly
        win.play(Wait(1.0))   #hold 1.0s: red on top (later additions drawn on top)
        win.close()   #close the RTM window


SCENES = [
    ("01-Camera-background_1", BackgroundDemo),
    ("01-Camera-is_in_frame_1", IsInFrameDemo),
    ("01-Camera-use_z_index_1", UseZIndexDemo),
]

PAIRS = [
    ("01-Camera-background", ["01-Camera-background_1"]),
    ("01-Camera-is_in_frame", ["01-Camera-is_in_frame_1"]),
    ("01-Camera-use_z_index", ["01-Camera-use_z_index_1"]),
]


def concat(names, dst):
    lst = os.path.join(HERE, "concat-01-Camera.txt")
    with open(lst, "w", encoding="utf-8") as fh:
        for n in names:
            fh.write("file '%s'\n" % os.path.join(FRAG, n + ".mp4"))
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
            fast_record_scene(cls, out_path=os.path.join(FRAG, name + ".mp4"),
                              verbose=True)
        except Exception:
            import traceback
            traceback.print_exc()

    if not only:
        for out_name, names in PAIRS:
            dst = os.path.join(ASSETS, "RTM output", out_name + ".mp4")
            concat(names, dst)
            print("concat ->", dst, os.path.getsize(dst), "bytes")
