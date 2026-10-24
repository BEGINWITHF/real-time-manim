# -*- coding: utf-8 -*-
"""最小探针：隔离 02b plot_line_graph 在 RTM 下的渲染问题。"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

from real_time_manim import (
    Scene, Axes, VGroup, VDict, Dot, Line, Text,
    GOLD_E, RED, YELLOW, UP, DOWN, LEFT, RIGHT,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


class ProbeCorners(Scene):
    """P1：VGroup.set_points_as_corners + Create（无 VDict）。"""
    def construct(self):
        win = MLWindow(960, 540)
        win.scene = self
        v = VGroup(color=GOLD_E, stroke_width=4)
        v.set_points_as_corners([LEFT * 3 + DOWN, LEFT * 1 + UP,
                                 RIGHT * 1 + DOWN, RIGHT * 3 + UP])
        ref = VGroup(*[Dot(p) for p in [LEFT * 3 + DOWN, LEFT * 1 + UP,
                                        RIGHT * 1 + DOWN, RIGHT * 3 + UP]])
        win.play(Create(v), run_time=0.8)
        win.play(FadeIn(ref), run_time=0.3)
        win.play(Wait(0.4))
        win.close()


class ProbeVDict(Scene):
    """P2：VDict + __setitem__ + 索引取出再动画。"""
    def construct(self):
        win = MLWindow(960, 540)
        win.scene = self
        vd = VDict()
        g = VGroup(color=GOLD_E, stroke_width=4)
        g.set_points_as_corners([LEFT * 3 + DOWN, LEFT * 1 + UP,
                                 RIGHT * 1 + DOWN, RIGHT * 3 + UP])
        vd["line_graph"] = g
        vd["vertex_dots"] = VGroup(*[Dot(p) for p in [LEFT * 3 + DOWN, LEFT * 1 + UP,
                                                      RIGHT * 1 + DOWN, RIGHT * 3 + UP]])
        win.play(Create(vd["line_graph"]), run_time=0.8)
        win.play(FadeIn(vd["vertex_dots"]), run_time=0.3)
        win.play(Wait(0.4))
        win.close()


SCENES = [
    ("probe_corners", ProbeCorners),
    ("probe_vdict", ProbeVDict),
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
