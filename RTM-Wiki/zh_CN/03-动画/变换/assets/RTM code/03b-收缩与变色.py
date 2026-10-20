"""RTM-Wiki · 03-动画/变换/03b-收缩与变色 —— 本页专属样例

文档「参数」表逐条演示：
    ShrinkToCenter(mobject, **kwargs)
        ✓ ShrinkToCenter(word, run_time=1.4, rate_func=smooth) 缩到中心消失
        ✓ 播完对象仍留在场景里（只是不可见）—— 需要真正移除得手动 self.remove(...)
    FadeToColor(mobject, color, **kwargs)
        ✓ color=RED -> color=YELLOW 两次渐变（非默认目标颜色）
        ✓ run_time / rate_func 转发

不演示：无 —— 本页两个类的全部可视参数均已显式演示。

运行：$env:PYTHONPATH="C:\\Users\\begin\\Desktop\\real-time-manim"; python "<本文件>"
"""
import os

from real_time_manim import (
    GREY_B,
    ORANGE,
    RED,
    WHITE,
    YELLOW,
    DOWN,
    LEFT,
    UP,
    Scene,
    Text,
    VGroup,
    smooth,
)
# ShrinkToCenter / FadeToColor 不在 RTM 导出清单，随自带 ManimCE 从 real_time_manim 导入，实测可跑
from real_time_manim import FadeToColor, ShrinkToCenter
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeIn,
    FadeOut,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_03b_收缩与变色(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # 参数 w / h / hidden
        win.scene = self                          # 参数 win.scene

        title = Text("ShrinkToCenter / FadeToColor", font_size=40, color=ORANGE).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        # —— ① ShrinkToCenter：缩到 0，收缩到中心消失 ——
        lab1 = Text("ShrinkToCenter(word, run_time=1.4, rate_func=smooth)",
                    font_size=28, color=GREY_B).next_to(title, DOWN, buff=0.4)
        word = Text("Bye", font_size=48, color=YELLOW).move_to(LEFT * 2.0 + DOWN * 1.4)
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)
        win.play(Write(word), run_time=0.8)
        win.play(ShrinkToCenter(word, run_time=1.4, rate_func=smooth), run_time=1.4)   # 参数 ShrinkToCenter ✓
        self.remove(word)      # 注意：ShrinkToCenter 不是 remover，播完仍在场景里（只是不可见）
        win.play(FadeOut(lab1), run_time=0.45)

        # —— ② FadeToColor：颜色渐变到指定色（演示两次不同目标色）——
        lab2 = VGroup(
            Text("FadeToColor(msg, RED, run_time=1.2)", font_size=30, color=GREY_B),
            Text("FadeToColor(msg, YELLOW, run_time=1.2)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        msg = Text("Hello World!", font_size=44, color=WHITE).move_to(DOWN * 1.6)
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)
        win.play(Write(msg), run_time=0.8)
        win.play(FadeToColor(msg, RED, run_time=1.2, rate_func=smooth), run_time=1.2)      # 参数 color=RED ✓
        win.play(FadeToColor(msg, YELLOW, run_time=1.2, rate_func=smooth), run_time=1.2)   # 参数 color=YELLOW ✓

        win.play(Wait(0.4))
        win.play(FadeOut(VGroup(title, lab2, msg)), run_time=0.6)
        win.close()                                 # 参数 win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(
        Page_03b_收缩与变色,
        out_path=os.path.join(os.path.dirname(here), "RTM output", "03b-收缩与变色.mp4"),
        fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True,
    )
