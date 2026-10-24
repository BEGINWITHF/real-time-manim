"""RTM-Wiki · 03-动画/变换/04-位置互换与复制式变换 —— 本页专属样例

文档「参数」表逐条演示：
    Swap(*mobjects, path_arc=90 * DEGREES)
        ✓ Swap(a, b, path_arc=180 * DEGREES)：两对象绕弧线互换（非默认 90°）
    TransformFromCopy(mobject, target_mobject)
        ✓ 原件保留不动，目标从原件演化过去（MathTex 公式）
    ClockwiseTransform(mobject, target_mobject, path_arc=-np.pi)
        ✓ path_arc=-np.pi（文档默认值显式传入）：点沿顺时针半圆弧换位
    CounterclockwiseTransform(mobject, target_mobject, path_arc=np.pi)
        ✓ path_arc=np.pi（文档默认值显式传入）：点沿逆时针半圆弧换位
    CyclicReplace(*mobjects, path_arc=90 * DEGREES)
        ✓ 三个对象轮转占位，path_arc=90 * DEGREES

不演示：无 —— 本页五个类的全部可视参数均已显式演示
        （Clockwise/CounterclockwiseTransform 的 path_arc 用文档默认 ±π 显式传入，
        弧线肉眼可见；Swap 用非默认 180° 证明该参数可改）。

运行：python "<本文件>"（脚本会自行把仓库根目录加入 sys.path）
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

import numpy as np
from real_time_manim import (
    BLUE,
    GREEN,
    GREY_B,
    ORANGE,
    PURPLE,
    RED,
    YELLOW,
    DEGREES,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Dot,
    MathTex,
    Scene,
    Text,
    VGroup,
    smooth,
)
# 以下五类不在 RTM 导出清单，随自带 ManimCE 从 real_time_manim 导入，实测可跑
from real_time_manim import (
    ClockwiseTransform,
    CounterclockwiseTransform,
    CyclicReplace,
    Swap,
    TransformFromCopy,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeIn,
    FadeOut,
    Wait,  # noqa: F401
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_04_位置互换与复制式变换(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # 参数 w / h / hidden
        win.scene = self                          # 参数 win.scene

        title = Text("位置互换 / 复制式变换", font_size=42, color=ORANGE).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        # —— ① Swap：两个对象沿弧线互换位置 ——
        lab1 = VGroup(
            Text("Swap(a, b, path_arc=180 * DEGREES,", font_size=30, color=GREY_B),
            Text("     run_time=1.2)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        a = Text("A", font_size=52, color=BLUE).move_to(LEFT * 3.5 + DOWN * 1.3)
        b = Text("B", font_size=52, color=GREEN).move_to(RIGHT * 3.5 + DOWN * 1.3)
        self.add(a, b)
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)
        win.play(Swap(a, b, path_arc=180 * DEGREES, run_time=1.2), run_time=1.2)   # 参数 *mobjects / path_arc ✓
        # 注：RTM 中 self.add 进场景的对象要各自单独 FadeOut（VGroup 淡出只作用于
        #     由 win.play 动画加入的成员），所以这里逐个淡出。
        win.play(FadeOut(lab1), FadeOut(a), FadeOut(b), run_time=0.5)

        # —— ② TransformFromCopy：原件保留，目标演化出来 ——
        lab2 = Text("TransformFromCopy(eq1, eq2, run_time=1.2, rate_func=smooth)",
                    font_size=28, color=GREY_B).next_to(title, DOWN, buff=0.4)
        eq1 = MathTex("x = 1").move_to(LEFT * 3.2 + DOWN * 1.3)
        eq2 = MathTex("x^2 = 1").move_to(RIGHT * 3.2 + DOWN * 1.3)
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)
        win.play(Write(eq1), run_time=0.6)
        win.play(TransformFromCopy(eq1, eq2, run_time=1.2, rate_func=smooth), run_time=1.2)   # 参数 ✓（原件保留）
        win.play(FadeOut(lab2), FadeOut(eq1), FadeOut(eq2), run_time=0.5)

        # —— ③ ClockwiseTransform：点沿顺时针半圆弧换位 ——
        lab3 = Text("ClockwiseTransform(p, q.copy(), path_arc=-np.pi)",
                    font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)
        p = Dot(radius=0.16, color=YELLOW).move_to(LEFT * 3.2 + DOWN * 1.3)
        q = Dot(radius=0.16, color=ORANGE).move_to(RIGHT * 3.2 + DOWN * 1.3)
        self.add(p, q)
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)
        win.play(ClockwiseTransform(p, q.copy(), path_arc=-np.pi, run_time=1.2), run_time=1.2)   # 参数 path_arc ✓
        win.play(FadeOut(lab3), FadeOut(p), FadeOut(q), run_time=0.5)

        # —— ④ CounterclockwiseTransform：逆时针半圆弧换位（与③方向相反）——
        lab4 = VGroup(
            Text("CounterclockwiseTransform(p2, q2.copy(),", font_size=30, color=GREY_B),
            Text("                           path_arc=np.pi)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        p2 = Dot(radius=0.16, color=RED).move_to(LEFT * 3.2 + DOWN * 1.3)
        q2 = Dot(radius=0.16, color=PURPLE).move_to(RIGHT * 3.2 + DOWN * 1.3)
        self.add(p2, q2)
        win.play(FadeIn(lab4, shift=DOWN), run_time=0.4)
        win.play(CounterclockwiseTransform(p2, q2.copy(), path_arc=np.pi, run_time=1.2), run_time=1.2)   # 参数 ✓
        win.play(FadeOut(lab4), FadeOut(p2), FadeOut(q2), run_time=0.5)

        # —— ⑤ CyclicReplace：三个对象轮转占位 ——
        lab5 = VGroup(
            Text("CyclicReplace(c1, c2, c3,", font_size=30, color=GREY_B),
            Text("              path_arc=90 * DEGREES, run_time=1.4)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        c1 = Text("1", font_size=48, color=BLUE).move_to(LEFT * 3.5 + DOWN * 1.3)
        c2 = Text("2", font_size=48, color=GREEN).move_to(DOWN * 1.3)
        c3 = Text("3", font_size=48, color=ORANGE).move_to(RIGHT * 3.5 + DOWN * 1.3)
        self.add(c1, c2, c3)
        win.play(FadeIn(lab5, shift=DOWN), run_time=0.4)
        win.play(CyclicReplace(c1, c2, c3, path_arc=90 * DEGREES, run_time=1.4), run_time=1.4)   # 参数 ✓

        win.play(FadeOut(title), FadeOut(lab5),
                 FadeOut(c1), FadeOut(c2), FadeOut(c3), run_time=0.6)
        win.close()                                 # 参数 win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(
        Page_04_位置互换与复制式变换,
        out_path=os.path.join(os.path.dirname(here), "RTM output", "04-位置互换与复制式变换.mp4"),
        fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True,
    )
