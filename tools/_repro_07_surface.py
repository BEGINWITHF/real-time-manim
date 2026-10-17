# -*- coding: utf-8 -*-
"""Reconstruction of the archived 07 `plot_surface` sample (RTM side).

The page script no longer contains the surface scene, so this file rebuilds the
exact source that produced `07-极坐标与三维坐标系-surface.mp4` and its CE twin
(198 frames = 3.30 s).  Every parameter was recovered from the archived twin
itself:

* title text / size  -> title bbox x[737..1182] == Text("07-plot_surface", 34)
* bottom label       -> label bbox width 541 px == Text(
                        "plot_surface(sin(u)*cos(v))", 24)
* surface            -> top-down shading pattern matches sin(u)*cos(v) at
                        resolution=(12, 12) exactly (f98 diff 3.2 -> 0.0);
                        amplitude 1.0 (silhouette IoU vs CE 0.999)
* run_times          -> Write .5 + Create .6 + FadeIn .6 + move_camera 1.0 +
                        Wait .6 reproduces the CE twin frame-for-frame.

    python tools/_repro_07_surface.py [out.mp4]
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import numpy as np

from real_time_manim import (
    Create, FadeIn, GREY_B, Text, ThreeDAxes, ThreeDScene, UP, DOWN, Write,
    YELLOW,
)
from real_time_manim.record import fast_record_scene
from real_time_manim.vulkan_bind import MLWindow, Wait


class SurfaceDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # 创建一个 RTM 窗口
        win.scene = self           # 把 manim scene 绑到 RTM 窗口
        self.play = win.play       # move_camera 内部会调 self.play
        title = Text("07-plot_surface", font_size=34, color=YELLOW).to_edge(UP)
        win.play(Write(title), run_time=0.5)
        ax = ThreeDAxes(x_range=(-3, 3, 1), y_range=(-3, 3, 1),
                        z_range=(-2, 2, 1))
        surf = ax.plot_surface(
            lambda u, v: np.sin(u) * np.cos(v),
            u_range=(-3, 3), v_range=(-3, 3), resolution=(12, 12))
        lab = Text("plot_surface(sin(u)*cos(v))",
                   font_size=24, color=GREY_B).to_edge(DOWN)
        win.play(Create(ax), FadeIn(lab), run_time=0.6)
        win.play(FadeIn(surf), run_time=0.6)
        self.move_camera(theta=-0.6, phi=1.1, run_time=1.0)
        win.play(Wait(0.6))
        win.close()


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.environ.get("TEMP", "."), "repro_07_surface.mp4")
    fast_record_scene(SurfaceDemo, out_path=out, verbose=True)
