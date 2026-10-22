# -*- coding: utf-8 -*-
"""Full source for the three samples in 03-ZoomedScene.md (identical to the code blocks in the page).

Usage: python 03-ZoomedScene.py <clip names>...
With no arguments it renders all 5 clips and concatenates the page's two comparison videos (zoom / activate).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
ASSETS = os.path.dirname(HERE)
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    GREEN, RED, YELLOW, UP, DOWN, LEFT, RIGHT, Dot, Text, VGroup,
    ZoomedScene,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


def make_target():   # a "small and dense" target: small text and dots, unreadable without zooming
    return VGroup(
        Text("RTM", font_size=22, color=YELLOW),   # very small title text
        Dot(radius=0.04, color=GREEN),              # two small dots
        Dot(radius=0.04, color=RED).shift(RIGHT * 0.18),
    ).arrange(DOWN, buff=0.1).shift(LEFT * 2 + DOWN * 0.8)   # place it lower-left of centre in the frame


# ===== Sample 1: ZoomedScene constructor parameters =========================
class ZoomBase(ZoomedScene):
    LABEL = ""   # subclasses fill in this clip's title text
    KW = {}      # subclasses fill in the constructor parameters to pass to ZoomedScene.__init__

    def __init__(self, **kwargs):
        super().__init__(**self.KW, **kwargs)   # pass the keys in "KW" to ZoomedScene.__init__

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        target = make_target()   # the small target to zoom in on
        self.add(target)   # add it to the scene (it is too small to read here)
        cap = Text(self.LABEL, font_size=28, color=YELLOW).to_edge(UP)   # top title shows the current constructor parameters
        self.add(cap)   # add it to the scene (in a 2D scene text is pinned to the screen by default)
        self.activate_zooming(animate=False)   # switch zooming on: the small window appears instantly, no animation
        self.zoomed_camera.frame.move_to(target)   # put the magnifier's view frame over the target
        win.play(Wait(0.8))   # pause 0.8s to see the zoomed result
        win.play(target.animate.shift(RIGHT * 1.2), run_time=1.2)   # move the target right, out of the view frame
        win.play(self.zoomed_camera.frame.animate.move_to(target), run_time=0.8)   # the view frame follows it
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window


class ZoomA(ZoomBase):
    LABEL = "zoom_factor=0.15 display 3x3 corner=UP+RIGHT"   # the default step: frame at 15%
    KW = {"zoom_factor": 0.15,
          "zoomed_display_height": 3, "zoomed_display_width": 3,
          "zoomed_display_corner": UP + RIGHT}


class ZoomB(ZoomBase):
    LABEL = "zoom_factor=0.08 display 4x2.5 corner=DOWN+LEFT"   # the harsher step: frame at 8% = about 12x zoom
    KW = {"zoom_factor": 0.08,
          "zoomed_display_height": 2.5, "zoomed_display_width": 4,
          "zoomed_display_corner": DOWN + LEFT, "zoomed_display_corner_buff": 0.3}


# ===== Sample 2: activate_zooming(animate) =================================
class ZoomActivateBase(ZoomedScene):
    ANIMATE = False   # subclasses change it to True to see the small window's entrance animation
    LABEL = ""        # subclasses fill in this clip's title text

    def __init__(self, **kwargs):
        super().__init__(zoom_factor=0.15, **kwargs)   # both classes share the same zoom_factor and compare only animate

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # with animate=True, activate_zooming calls self.play internally, so wire it to the window first
        target = make_target()   # the small target to zoom in on
        self.add(target)   # add it to the scene
        cap = Text(self.LABEL, font_size=28, color=YELLOW).to_edge(UP)   # top title shows the value of animate
        self.add(cap)   # add it to the scene
        self.activate_zooming(animate=self.ANIMATE)   # False = the small window appears instantly; True = push the camera in first, then pop the window out
        self.zoomed_camera.frame.move_to(target)   # put the magnifier's view frame over the target
        win.play(Wait(0.8))   # pause 0.8s to see the zoomed result
        win.close()   # close the RTM window


class ZoomNoAnim(ZoomActivateBase):
    ANIMATE = False   # the small window appears directly
    LABEL = "activate_zooming(animate=False)"


class ZoomAnim(ZoomActivateBase):
    ANIMATE = True   # play the entrance animations
    LABEL = "activate_zooming(animate=True)"


# ===== Sample 3: get_zoom_in_animation / pop_out / get_zoom_factor =========
class ManualZoomDemo(ZoomedScene):
    def __init__(self, **kwargs):
        super().__init__(zoom_factor=0.15, **kwargs)   # the default 0.15 step

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # all the animations sequenced by hand below go through win.play
        target = make_target()   # the small target to zoom in on
        self.add(target)   # add it to the scene

        # do the three steps of activate_zooming(animate=True) by hand, pacing them yourself:
        self.renderer.camera.add_image_mobject_from_camera(self.zoomed_display)   # (1) register the small window into the main camera
        win.play(self.get_zoom_in_animation(run_time=1.2))   # (2) "camera pushes in": the view frame shrinks from full screen to the zoom size
        win.play(self.get_zoomed_display_pop_out_animation(run_time=0.8))   # (3) "small window pops out": it unfolds from the window's position
        self.add_foreground_mobjects(self.zoomed_camera.frame, self.zoomed_display)   # put the view frame and the small window on top

        ratio = self.get_zoom_factor()   # zoom ratio = zoom view-frame height / small-window height
        print("get_zoom_factor() =", ratio)   # print the zoom ratio to the console
        cap = Text("get_zoom_factor() = %.2f" % ratio,   # show a copy at the top as well
                   font_size=28, color=YELLOW).to_edge(UP)
        self.add(cap)   # add it to the scene
        self.zoomed_camera.frame.move_to(target)   # put the magnifier's view frame over the target
        win.play(Wait(0.8))   # pause 0.8s to see the zoomed result
        win.close()   # close the RTM window


SCENES = [
    ("zoom_a", ZoomA),
    ("zoom_b", ZoomB),
    ("noanim", ZoomNoAnim),
    ("anim", ZoomAnim),
    ("manual", ManualZoomDemo),
]

PAIRS = [
    ("03-ZoomedScene-zoom", ["zoom_a", "zoom_b"]),
    ("03-ZoomedScene-activate", ["noanim", "anim"]),
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

    for out_name, names in PAIRS:
        dst = os.path.join(ASSETS, "RTM output", out_name + ".mp4")
        concat(names, dst)
        print("concat ->", dst, os.path.getsize(dst), "bytes")

    import shutil   # single clips are published as page videos too: <page name>-<clip name>.mp4
    PAGE = os.path.splitext(os.path.basename(__file__))[0]
    used = {n for _, names in PAIRS for n in names}
    for name, _ in SCENES:
        if name in used or (only and name not in only):
            continue
        src = os.path.join(OUT, name + ".mp4")
        if os.path.exists(src):
            shutil.copy(src, os.path.join(HERE, "..", PAGE + "-" + name + ".mp4"))
            print("publish ->", PAGE + "-" + name + ".mp4")
