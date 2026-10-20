"""RTM-Wiki · 03-动画/变换/02b-更多函数驱动 —— 本页专属样例

文档「参数」表逐条演示：
    ApplyPointwiseFunctionToCenter(function, mobject, **kwargs)
        ✓ function=lambda c: c + UP * 2.2（中心 -> 新中心），形状不变只整体重定位
        ✓ run_time=1.2（显式覆盖默认 3.0）
    ApplyComplexFunction(function, mobject, **kwargs)
        ✓ function=lambda z: np.exp(z)（复平面共形变换）
        ✓ run_time=1.5
    ApplyMatrix(matrix, mobject, about_point=ORIGIN, **kwargs)
        ✓ matrix=[[1, 1], [0, 2 / 3]]（2×2 剪切 + 纵向压缩）
        ✓ about_point=DOWN * 2.6（非默认变换原点：绕底部锚点剪切）
        ✓ run_time=1.4

不演示：无 —— 本页三个类的全部可视参数均已显式演示。

运行：$env:PYTHONPATH="C:\\Users\\begin\\Desktop\\real-time-manim"; python "<本文件>"
"""
import os

import numpy as np
from real_time_manim import (
    BLUE,
    GREEN,
    GREY_B,
    ORANGE,
    YELLOW,
    DOWN,
    LEFT,
    ORIGIN,
    UP,
    Dot,
    Scene,
    Square,
    Text,
    VGroup,
    Write,
)
# 以下三类不在 RTM 导出清单，随自带 ManimCE 从 real_time_manim 导入，实测可跑
# （ApplyPointwiseFunctionToCenter 由 real_time_manim.compat 在导入时修好 __init__）
from real_time_manim import ApplyComplexFunction, ApplyMatrix, ApplyPointwiseFunctionToCenter
from real_time_manim.vulkan_bind import (
    MLWindow,
    Create,
    FadeIn,
    FadeOut,
    Wait,  # noqa: F401
)
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_02b_更多函数驱动(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # 参数 w / h / hidden
        win.scene = self                          # 参数 win.scene

        title = Text("更多函数驱动：中心 / 复变 / 矩阵", font_size=42, color=ORANGE).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        # —— ① ApplyPointwiseFunctionToCenter：只改中心点，形状不动 ——
        lab1 = VGroup(
            Text("ApplyPointwiseFunctionToCenter(", font_size=30, color=GREY_B),
            Text("  lambda c: c + UP * 2.2, d, run_time=1.2)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        d = Dot(radius=0.16, color=YELLOW).move_to(LEFT * 3.0 + DOWN * 1.5)
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)
        win.play(Create(d), run_time=0.4)
        win.play(                                   # 中心沿给定规则重定位
            ApplyPointwiseFunctionToCenter(lambda c: c + UP * 2.2, d,
                                           run_time=1.2),   # 参数 run_time ✓（默认 3.0）
            run_time=1.2,
        )
        win.play(FadeOut(VGroup(lab1, d)), run_time=0.5)

        # —— ② ApplyComplexFunction：复变函数共形变换（以 ORIGIN 为基准）——
        lab2 = VGroup(
            Text("ApplyComplexFunction(lambda z: np.exp(z),", font_size=30, color=GREY_B),
            Text("                     sq, run_time=1.5)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        sq = Square(side_length=2.2, color=GREEN).set_fill(GREEN, 0.5).move_to(ORIGIN + DOWN * 0.6)
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)
        win.play(Create(sq), run_time=0.5)
        win.play(ApplyComplexFunction(lambda z: np.exp(z), sq,   # 参数 function + mobject ✓
                                      run_time=1.5), run_time=1.5)
        win.play(FadeOut(VGroup(lab2, sq)), run_time=0.5)

        # —— ③ ApplyMatrix：2×2 线性变换，绕自定义锚点 ——
        lab3 = VGroup(
            Text("ApplyMatrix([[1, 1], [0, 2 / 3]], txt,", font_size=30, color=GREY_B),
            Text("  about_point=DOWN * 2.6, run_time=1.4)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        txt = Text("Hello", font_size=48, color=BLUE).move_to(LEFT * 1.6 + DOWN * 1.0)
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)
        win.play(Write(txt), run_time=0.6)
        win.play(                                   # p' = (p - about_point) @ matrix.T + about_point
            ApplyMatrix([[1, 1], [0, 2 / 3]], txt,   # 参数 matrix ✓（2×2 自动补成 3×3）
                        about_point=DOWN * 2.6,      # 参数 about_point ✓（非默认 ORIGIN）
                        run_time=1.4),               # 参数 run_time ✓（默认 3.0）
            run_time=1.4,
        )

        win.play(FadeOut(VGroup(title, lab3, txt)), run_time=0.6)
        win.close()                                 # 参数 win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(
        Page_02b_更多函数驱动,
        out_path=os.path.join(os.path.dirname(here), "RTM output", "02b-更多函数驱动.mp4"),
        fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True,
    )
