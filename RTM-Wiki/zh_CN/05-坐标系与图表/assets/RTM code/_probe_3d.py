# -*- coding: utf-8 -*-
"""07 页三维能力最小探针：ThreeDAxes + move_camera、plot_surface 各一段。"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

from real_time_manim import (
    ThreeDScene, ThreeDAxes, Dot, MathTex, Text,
    RED, YELLOW, UP, ORIGIN,
    Create, FadeIn, VGroup,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


class ProbeAxes(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 内部会调 self.play，必须先接上
        ax = ThreeDAxes(x_range=(-3, 3, 1), y_range=(-3, 3, 1), z_range=(-3, 3, 1))
        d = Dot(ax.c2p(1, 1, 2), color=RED)
        win.play(Create(ax), run_time=0.8)
        win.play(FadeIn(d), run_time=0.3)
        self.move_camera(theta=-0.6, phi=1.1, run_time=1.0)
        win.play(Wait(0.3))
        win.close()


class ProbeSurface(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 内部会调 self.play，必须先接上
        ax = ThreeDAxes(x_range=(-3, 3, 1), y_range=(-3, 3, 1), z_range=(-2, 2, 1))
        surf = ax.plot_surface(lambda u, v: 0.6 * (np.sin(u) * np.cos(v)),
                               u_range=(-3, 3), v_range=(-3, 3),
                               resolution=(8, 8))
        win.play(Create(ax), run_time=0.5)
        win.play(FadeIn(surf), run_time=0.5)
        self.move_camera(theta=-0.6, phi=1.1, run_time=1.0)
        win.play(Wait(0.3))
        win.close()


import numpy as np  # noqa: E402

SCENES = [
    ("probe_axes", ProbeAxes),
    ("probe_surface", ProbeSurface),
]

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
