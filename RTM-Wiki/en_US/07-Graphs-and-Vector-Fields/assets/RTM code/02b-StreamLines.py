# -*- coding: utf-8 -*-
"""Full source for the two samples in 02b-StreamLines.md (character-for-character identical to the code blocks in the page).

Usage: python 02b-StreamLines.py <clip-name>...
With no arguments it renders every clip and concatenates the two sample videos shown in the page (written to the parent assets/).
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

import numpy as np
from real_time_manim import (
    Scene, Text, StreamLines,
    YELLOW, GREY_B, BLUE, UP, DOWN, LEFT,
    Write, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: create draws the lines one by one in random order =========
class StreamLinesCreateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02b-StreamLines-create", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = Text("sl.create(run_time=..., lag_ratio=...)",
                   font_size=26, color=GREY_B).next_to(title, DOWN, buff=0.3)   # signature label
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        func = lambda pos: np.sin(pos[0] / 2) * UP + np.cos(pos[1] / 2) * LEFT   # field function
        sl = StreamLines(
            func,                                   # parameter "func"
            x_range=[-4, 4, 1], y_range=[-2.5, 2.5, 1],   # spawn grid
            color=BLUE,                             # parameter "color": whole field blue
            stroke_width=3,                         # parameter "stroke_width"
            max_anchors_per_line=15,                # decimate anchors: faster construction, smoother lines
            virtual_time=1,                         # parameter "virtual_time": simulated trace duration
        )
        win.play(sl.create(run_time=1.4), run_time=1.4)   # draw the lines one by one in random order
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


# ===== Sample 2: start_animation / end_animation continuous flow ===========
class StreamLinesFlowDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02b-StreamLines-flow", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = Text("start_animation(flow_speed=1.5, time_width=0.5) ... end_animation()",
                   font_size=24, color=GREY_B).next_to(title, DOWN, buff=0.3)   # signature label
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        func = lambda pos: np.sin(pos[0] / 2) * UP + np.cos(pos[1] / 2) * LEFT   # field function
        sl = StreamLines(
            func,                                   # parameter "func"
            x_range=[-4, 4, 1], y_range=[-2.5, 2.5, 1],   # spawn grid
            color=BLUE,                             # parameter "color": whole field blue
            stroke_width=3,                         # parameter "stroke_width"
            max_anchors_per_line=15,                # decimate anchors
            virtual_time=1,                         # parameter "virtual_time"
        )
        win.play(sl.create(run_time=0.8), run_time=0.8)   # draw the stream lines first
        self.add(sl)   # put "sl" itself into the scene: the updater lives on it, and without add the whole field is black
        sl.start_animation(warm_up=False, flow_speed=1.5, time_width=0.5)   # parameters "flow_speed" / "time_width"
        win.play(Wait(2.0))   # the light point keeps flowing along the lines for 2 seconds
        win.play(sl.end_animation(), run_time=0.6)   # smoothly wind down the continuous animation
        win.close()   # close the RTM window


SCENES = [
    ("create", StreamLinesCreateDemo),
    ("flow", StreamLinesFlowDemo),
]

PAIRS = [
    ("create", ["create"]),
    ("flow", ["flow"]),
]

PAGE = "02b-StreamLines"


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
