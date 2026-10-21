# -*- coding: utf-8 -*-
"""Full source of the two samples in 02-MovingCamera.md (identical to the code blocks in the page).

Usage: python 02-MovingCamera.py <clip name>...
With no arguments it renders all 5 scenes and concatenates the page's two videos.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FRAG = os.path.join(HERE, "final",
                       os.path.splitext(os.path.basename(__file__))[0])
ASSETS = os.path.dirname(HERE)
os.makedirs(FRAG, exist_ok=True)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    BLUE, RED, WHITE, YELLOW,
    DOWN, LEFT, RIGHT, UP,
    Circle, Dot, FadeIn, MovingCameraScene, Square, Text, VGroup,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: frame_height / frame_width / frame_center ==================
class FrameScaleDemo(MovingCameraScene):
    HEIGHT = 4.0   #the picture height you want to see: change it to 2.0 and run again to zoom in 4×

    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        cam = self.camera   #MovingCameraScene's built-in movable camera
        a = Square(color=BLUE).set_stroke(width=4).shift(LEFT * 2.5)   #the target on the left
        b = Square(color=RED).set_stroke(width=4).shift(RIGHT * 2.5)   #the target on the right
        info = Text("frame: %.2f x %.2f" % (cam.frame_height, cam.frame_width),
                    font_size=28, color=WHITE).move_to(UP * 1.6)   #the viewfinder's height and width (placed inside the picture: after zooming in, an edge-hugging label goes off screen)
        self.add(a, b, info)   #add the two squares and the reading to the scene
        win.play(FadeIn(a, b), run_time=0.5)   #the two squares fade in: at this point still the default frame
        win.play(Wait(0.4))   #hold 0.4s
        cam.frame_height = self.HEIGHT   #change the height
        cam.frame_width = self.HEIGHT * 16 / 9   #change the width to match at 16:9: only a paired assignment gives a proportional zoom
        info.become(Text("frame: %.2f x %.2f" % (cam.frame_height, cam.frame_width),
                    font_size=28, color=WHITE).move_to(UP * 1.6))   #refresh the reading
        win.play(Wait(1.0))   #hold 1.0s to see the zoomed-in picture
        win.close()   #close the RTM window


class FrameCenterDemo(MovingCameraScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        cam = self.camera   #MovingCameraScene's built-in movable camera
        a = Square(color=BLUE).set_stroke(width=4).shift(LEFT * 4)   #the target on the left
        b = Square(color=RED).set_stroke(width=4).shift(RIGHT * 4)   #the target on the right
        info = Text("frame_center = ORIGIN", font_size=28, color=WHITE).to_edge(UP)   #viewfinder center
        self.add(a, b, info)   #add the two squares and the reading to the scene
        win.play(FadeIn(a, b), run_time=0.5)   #the two squares fade in
        win.play(Wait(0.4))   #hold 0.4s
        cam.frame_center = b   #move the viewfinder center onto the red square (a coordinate array is accepted too)
        info.become(Text("frame_center = red square", font_size=28, color=WHITE).to_edge(UP))   #refresh the reading
        win.play(Wait(1.0))   #hold 1.0s: the camera pans to the right
        win.close()   #close the RTM window


# ===== Sample 2: auto_zoom ==================================================
class AutoZoomAnimDemo(MovingCameraScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        cam = self.camera   #MovingCameraScene's built-in movable camera
        group = VGroup(
            Square(color=BLUE).set_stroke(width=4).shift(LEFT * 2.5),   #the square on the left
            Circle(color=RED).set_stroke(width=4).shift(RIGHT * 2.5),   #the circle on the right
            Dot(color=YELLOW).shift(DOWN * 2),   #the small dot below
        )   #the three objects as one group
        self.add(group)   #add the three objects to the scene
        win.play(cam.auto_zoom(group, margin=0.5), run_time=1.0)   #zoom in with an animation to exactly frame the three objects
        win.play(Wait(0.6))   #hold 0.6s
        win.close()   #close the RTM window


class AutoZoomNoAnimDemo(MovingCameraScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        cam = self.camera   #MovingCameraScene's built-in movable camera
        group = VGroup(
            Square(color=BLUE).set_stroke(width=4).shift(LEFT * 2.5),   #the square on the left
            Circle(color=RED).set_stroke(width=4).shift(RIGHT * 2.5),   #the circle on the right
            Dot(color=YELLOW).shift(DOWN * 2),   #the small dot below
        )   #the three objects as one group
        self.add(group)   #add the three objects to the scene
        cam.auto_zoom(group, margin=0.5, animate=False)   #animate=False: takes effect at once, the picture jumps straight there
        win.play(Wait(1.0))   #hold 1.0s
        win.close()   #close the RTM window


class AutoZoomOnlyDemo(MovingCameraScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        cam = self.camera   #MovingCameraScene's built-in movable camera
        sq = Square(color=BLUE).set_stroke(width=4).shift(LEFT * 5)   #a square far to the left
        circ = Circle(color=RED).set_stroke(width=4).shift(RIGHT * 2.5)   #the circle on the right
        self.add(sq, circ)   #add the square and the circle to the scene
        win.play(cam.auto_zoom(circ, margin=0.4), run_time=0.8)   #zoom in on the circle first: the square leaves the frame
        win.play(cam.auto_zoom([circ, sq], margin=0.4, only_mobjects_in_frame=True), run_time=0.8)   #the square is off screen and ignored: the camera does not move
        win.play(Wait(0.5))   #hold 0.5s
        win.play(cam.auto_zoom([circ, sq], margin=0.4), run_time=0.8)   #with no restriction: the square counts too, so the camera zooms out
        win.play(Wait(0.5))   #hold 0.5s and wrap up
        win.close()   #close the RTM window


SCENES = [
    ("02-MovingCamera-frame_scale_1", FrameScaleDemo),
    ("02-MovingCamera-frame_center_1", FrameCenterDemo),
    ("02-MovingCamera-auto_zoom_anim_1", AutoZoomAnimDemo),
    ("02-MovingCamera-auto_zoom_noanim_1", AutoZoomNoAnimDemo),
    ("02-MovingCamera-auto_zoom_only_1", AutoZoomOnlyDemo),
]

PAIRS = [
    ("02-MovingCamera-frame_props", ["02-MovingCamera-frame_scale_1", "02-MovingCamera-frame_center_1"]),
    ("02-MovingCamera-auto_zoom", ["02-MovingCamera-auto_zoom_anim_1", "02-MovingCamera-auto_zoom_noanim_1",
                                   "02-MovingCamera-auto_zoom_only_1"]),
]


def concat(names, dst):
    lst = os.path.join(HERE, "concat-02-MovingCamera.txt")
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
