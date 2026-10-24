# -*- coding: utf-8 -*-
"""临时实测：RTM 自带（vulkan_bind）AnimationGroup 在 win.play 下，
FadeIn 新对象（黄圆绿三角）组合期间是否登记出现。
渲完看 f140/f165（组合中段/末段）有无 ya/yb，用完即删。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    Scene, Square, Circle, Triangle, Text,
    RED, GREEN, YELLOW, GREY_B,
    UP, DOWN, LEFT, RIGHT,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait, AnimationGroup
from real_time_manim.record import fast_record_scene


class SwapVTKTest(Scene):
    def construct(self):
        win = MLWindow(960, 540)
        win.scene = self
        title = Text("01-AnimationGroup swap", font_size=34, color=YELLOW).to_edge(UP)
        win.play(Write(title), run_time=0.5)

        l4 = Text("AnimationGroup(FadeOut(x, shift=UP), FadeIn(y1, y2, shift=UP))",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)
        x = (Square(side_length=1.2, color=RED).set_fill(RED, 0.6)
             .next_to(l4, DOWN, buff=0.7).shift(LEFT * 2.0))
        ya = Circle(radius=0.5, color=YELLOW).move_to(x)
        yb = (Triangle(color=GREEN).scale(0.9)
              .next_to(l4, DOWN, buff=0.7).shift(RIGHT * 2.0))
        win.play(FadeIn(l4, shift=DOWN), run_time=0.4)
        win.play(Create(x), run_time=0.7)
        win.play(
            AnimationGroup(
                FadeOut(x, shift=UP),
                FadeIn(ya, yb, shift=UP),
                lag_ratio=0.0,
            ),
            run_time=1.2,
        )
        win.play(Wait(0.8))
        win.close()


if __name__ == "__main__":
    fast_record_scene(SwapVTKTest,
                      out_path=os.path.join(HERE, "final", "swap_vtk.mp4"),
                      verbose=True)
