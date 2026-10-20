"""RTM-Wiki · 03-动画/变换/03-状态保存与样式变换 —— 本页专属样例

文档「参数」表逐条演示：
    Restore(mobject, **kwargs)
        ✓ 前提：先 sq.save_state()（否则恢复到的是默认状态）
        ✓ sq.animate.set_color(PURPLE).scale(1.8) 折腾一下
        ✓ Restore(sq, run_time=1.1, rate_func=smooth) 变回保存的状态
    ScaleInPlace(mobject, scale_factor, **kwargs)
        ✓ scale_factor=1.8 放大 / scale_factor=0.6 缩小（非默认值，语义直白）
        ✓ run_time / rate_func 转发

不演示：无 —— 本页两个类的全部可视参数均已显式演示。

运行：$env:PYTHONPATH="C:\\Users\\begin\\Desktop\\real-time-manim"; python "<本文件>"
"""
import os

from real_time_manim import (
    BLUE,
    GREEN,
    GREY_B,
    ORANGE,
    PURPLE,
    DOWN,
    LEFT,
    UP,
    Scene,
    Square,
    Text,
    VGroup,
    smooth,
)
# Restore / ScaleInPlace 不在 RTM 导出清单，随自带 ManimCE 从 real_time_manim 导入，实测可跑
from real_time_manim import Restore, ScaleInPlace
from real_time_manim.vulkan_bind import (
    MLWindow,
    Create,
    FadeIn,
    FadeOut,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_03_状态保存与样式变换(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # 参数 w / h / hidden
        win.scene = self                          # 参数 win.scene

        title = Text("状态保存 / 就地改样式", font_size=44, color=ORANGE).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        # —— ① save_state() + .animate 折腾一下 ——
        lab1 = VGroup(
            Text("sq.save_state()", font_size=30, color=GREY_B),
            Text("sq.animate.set_color(PURPLE).scale(1.8)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        sq = Square(side_length=1.4, color=BLUE).set_fill(BLUE, 0.6).move_to(LEFT * 3.2 + DOWN * 1.2)
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)
        win.play(Create(sq), run_time=0.5)
        sq.save_state()                            # 参数 save_state() ✓（Restore 的前提）
        win.play(sq.animate.set_color(PURPLE).scale(1.8), run_time=1.1)   # 参数 .animate ✓
        win.play(FadeOut(lab1), run_time=0.45)

        # —— ② Restore：变回最近一次 save_state() 的状态 ——
        lab2 = Text("Restore(sq, run_time=1.2, rate_func=smooth)",
                    font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)
        win.play(Restore(sq, run_time=1.2, rate_func=smooth), run_time=1.2)   # 参数 Restore(mobject) ✓
        win.play(FadeOut(VGroup(lab2, sq)), run_time=0.5)

        # —— ③ ScaleInPlace：就地缩放，倍数直白 ——
        lab3 = VGroup(
            Text("ScaleInPlace(txt, 1.8, run_time=1.0)", font_size=30, color=GREY_B),
            Text("ScaleInPlace(txt, 0.6, run_time=1.0)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        txt = Text("ScaleInPlace", font_size=40, color=GREEN).move_to(DOWN * 1.3)
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)
        win.play(Write(txt), run_time=0.6)
        win.play(ScaleInPlace(txt, 1.8, run_time=1.0, rate_func=smooth), run_time=1.0)   # 参数 scale_factor=1.8 ✓
        win.play(ScaleInPlace(txt, 0.6, run_time=1.0, rate_func=smooth), run_time=1.0)   # 参数 scale_factor=0.6 ✓

        win.play(Wait(0.5))
        win.play(FadeOut(VGroup(title, lab3, txt)), run_time=0.6)
        win.close()                                 # 参数 win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(
        Page_03_状态保存与样式变换,
        out_path=os.path.join(os.path.dirname(here), "RTM output", "03-状态保存与样式变换.mp4"),
        fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True,
    )
