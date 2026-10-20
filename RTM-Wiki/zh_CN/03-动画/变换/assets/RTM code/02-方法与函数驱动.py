"""RTM-Wiki · 03-动画/变换/02-方法与函数驱动 —— 本页专属样例

文档「参数」表逐条演示：
    ApplyMethod(method, *args, **kwargs)
        ✓ method=m.shift（绑定方法）+ 位置参数 RIGHT * 4.5
        ✓ 末位放 dict 会被当作方法的关键字参数：ApplyMethod(m.scale, 1.5, {'about_edge': UP})
        ✓ **kwargs 转发：run_time / path_arc / rate_func
    ApplyFunction(function, mobject, **kwargs)
        ✓ function=lambda m: m.scale(0.6).set_color(RED)（副本 -> 新对象）
    ApplyPointwiseFunction(function, mobject, run_time=3.0, **kwargs)
        ✓ function=lambda p: p + 0.5 * sin(p[1] * 2) * RIGHT（每个点各走各的，方块变波浪）
        ✓ run_time=1.5（显式覆盖默认 3.0）

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
    RED,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Scene,
    Square,
    Text,
    VGroup,
    smooth,
)
# ApplyMethod / ApplyFunction / ApplyPointwiseFunction 不在 RTM 导出清单，
# 从 real_time_manim 导入（= 自带 ManimCE 原生版）并实测 win.play 可正常播放
from real_time_manim import ApplyFunction, ApplyMethod, ApplyPointwiseFunction
from real_time_manim.vulkan_bind import (
    MLWindow,
    Create,
    FadeIn,
    FadeOut,
    Wait,  # noqa: F401
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_02_方法与函数驱动(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # 参数 w / h / hidden
        win.scene = self                          # 参数 win.scene

        title = Text("方法 / 函数驱动的变换", font_size=44, color=ORANGE).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        m = Square(side_length=1.6, color=BLUE).set_fill(BLUE, 0.6).move_to(LEFT * 4.0 + DOWN * 1.2)

        # —— ① ApplyMethod：绑定方法 + 位置参数 + **kwargs ——
        lab1 = VGroup(
            Text("ApplyMethod(m.shift, RIGHT * 4.5,", font_size=30, color=GREY_B),
            Text("            run_time=1.1, path_arc=0.6)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)
        win.play(Create(m), run_time=0.5)
        win.play(                                   # 「调用某个方法」变成动画
            ApplyMethod(m.shift, RIGHT * 4.5,       # 参数 method + *args ✓（绑定方法 + 位置参数）
                        run_time=1.1,               # 参数 run_time ✓
                        path_arc=0.6,               # 参数 path_arc ✓（**kwargs 转发给 Transform）
                        rate_func=smooth),          # 参数 rate_func ✓
            run_time=1.1,
        )
        win.play(FadeOut(lab1), run_time=0.45)

        # —— ② ApplyMethod：*args 末位的 dict 会被当作方法的关键字参数 ——
        lab2 = Text("ApplyMethod(m.scale, 1.5, {'about_edge': UP})",
                    font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)
        win.play(                                   # 顶边不动地放大（about_edge=UP 只在副本上生效）
            ApplyMethod(m.scale, 1.5, {'about_edge': UP}, run_time=1.0),
            run_time=1.0,
        )
        win.play(FadeOut(lab2), run_time=0.45)

        # —— ③ ApplyPointwiseFunction：每个点各走各的 ——
        lab3 = VGroup(
            Text("ApplyPointwiseFunction(lambda p: p +", font_size=30, color=GREY_B),
            Text("  0.5 * np.sin(p[1] * 2) * RIGHT, m,", font_size=30, color=GREY_B),
            Text("  run_time=1.5)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.3)
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)
        win.play(                                   # 每个点按自己的 y 坐标横向偏移 -> 方块变波浪
            ApplyPointwiseFunction(lambda p: p + 0.5 * np.sin(p[1] * 2) * RIGHT, m,
                                   run_time=1.5),    # 参数 run_time ✓（默认 3.0）
            run_time=1.5,
        )
        win.play(FadeOut(lab3), run_time=0.45)

        # —— ④ ApplyFunction：任意纯函数（副本 -> 新对象）——
        lab4 = VGroup(
            Text("ApplyFunction(lambda m: m.scale(0.6)", font_size=30, color=GREY_B),
            Text("  .set_color(GREEN), m, run_time=1.1)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        win.play(FadeIn(lab4, shift=DOWN), run_time=0.4)
        win.play(                                   # 纯函数：接收副本并返回新对象
            ApplyFunction(lambda m: m.scale(0.6).set_color(GREEN), m, run_time=1.1),
            run_time=1.1,
        )

        win.play(FadeOut(VGroup(title, lab4, m)), run_time=0.6)
        win.close()                                 # 参数 win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(
        Page_02_方法与函数驱动,
        out_path=os.path.join(os.path.dirname(here), "RTM output", "02-方法与函数驱动.mp4"),
        fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True,
    )
