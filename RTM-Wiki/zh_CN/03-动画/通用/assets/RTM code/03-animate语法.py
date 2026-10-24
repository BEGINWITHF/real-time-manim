"""RTM-Wiki · 03-动画/通用/03-animate语法 —— 本页专属样例

演示参数（文档「参数」表逐条）：
    sq.animate.shift(...)                       ✓ 基本语法：改属性即动画
    sq.animate(run_time=1.3)                    ✓ kwargs 紧跟 .animate(...)，只能传一次
    .set_color(RED).rotate(PI/5)                ✓ 链式方法合成一个动画
    sq.animate(rate_func=there_and_back)        ✓ kwargs 里的速率函数
    ci.generate_target() + MoveToTarget(ci, run_time=1.2)  ✓ 显式目标状态
不演示：.animate(lag_ratio=...) —— 单个 .animate 没有子对象错峰可言（参数本身没被丢弃，
    无子对象时打 UserWarning 提示，见页尾）；@override_animate / @override_animation ——
    需要自定义 Mobject 子类，本页不出样例（机制已接线，见页尾）。
运行：python "<本文件>"（脚本会自行把仓库根目录加入 sys.path）
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    BLUE,
    DOWN,
    GREEN,
    GREY_B,
    LEFT,
    RED,
    RIGHT,
    UP,
    YELLOW,
    PI,
    Circle,
    Scene,
    Square,
    Text,
    VGroup,
    there_and_back,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeIn,
    FadeOut,
    MoveToTarget,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_03_animate语法(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # 参数 w / h / hidden
        win.scene = self                          # 参数 win.scene

        title = Text("03-.animate 语法与 MoveToTarget", font_size=44, color=YELLOW).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        sq = Square(side_length=1.4, color=BLUE).set_fill(BLUE, 0.5).shift(LEFT * 3.2 + DOWN * 1.9)
        ci = Circle(radius=0.7, color=GREEN).set_fill(GREEN, 0.5).shift(RIGHT * 3.2 + DOWN * 1.9)

        # —— 步骤 1：sq.animate.shift(...) ——
        l1 = Text("win.play(sq.animate.shift(RIGHT * 1.6))", font_size=30, color=GREY_B)
        l1.to_edge(UP).shift(DOWN * 1.05)
        win.play(FadeIn(l1, shift=DOWN), FadeIn(sq), FadeIn(ci), run_time=0.4)
        win.play(sq.animate.shift(RIGHT * 1.6))                  # 参数 .animate + 链式方法 shift
        win.play(Wait(0.2))

        # —— 步骤 2：kwargs 紧跟 .animate(...)，链式多个方法 ——
        win.play(FadeOut(l1), run_time=0.3)
        l2 = Text("win.play(sq.animate(run_time=1.3)", font_size=30, color=GREY_B)
        l3 = Text("              .set_color(RED).rotate(PI/5))", font_size=30, color=GREY_B)
        sig2 = VGroup(l2, l3).arrange(DOWN, buff=0.06).to_edge(UP).shift(DOWN * 1.05)
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.4)
        win.play(sq.animate(run_time=1.3)                         # 参数 .animate(run_time=…)（只能传一次）
                 .set_color(RED)                                  # 链式方法 1
                 .rotate(PI / 5))                                 # 链式方法 2（合成一个动画）
        win.play(Wait(0.2))

        # —— 步骤 3：rate_func 写进 .animate(...) ——
        win.play(FadeOut(sig2), run_time=0.3)
        l4 = Text("win.play(sq.animate(rate_func=there_and_back).scale(0.55))",
                  font_size=30, color=GREY_B).to_edge(UP).shift(DOWN * 1.05)
        win.play(FadeIn(l4, shift=DOWN), run_time=0.4)
        win.play(sq.animate(rate_func=there_and_back).scale(0.55))   # 参数 rate_func（出去又回来）
        win.play(Wait(0.2))

        # —— 步骤 4：显式 generate_target() + MoveToTarget ——
        win.play(FadeOut(l4), run_time=0.3)
        l5 = Text("ci.generate_target();  ci.target.set_fill(RED, 0.4)", font_size=28, color=GREY_B)
        l6 = Text("                 .shift(2 * RIGHT + UP).scale(0.5)", font_size=28, color=GREY_B)
        l7 = Text("win.play(MoveToTarget(ci, run_time=1.2))", font_size=28, color=GREY_B)
        sig4 = VGroup(l5, l6, l7).arrange(DOWN, buff=0.06).to_edge(UP).shift(DOWN * 1.05)
        win.play(FadeIn(sig4, shift=DOWN), run_time=0.4)
        ci.generate_target()                                      # 参数 generate_target()
        ci.target.set_fill(RED, 0.4).shift(2 * RIGHT + UP).scale(0.5)
        win.play(MoveToTarget(ci, run_time=1.2))                  # 参数 MoveToTarget(mobject, run_time)
        win.play(Wait(0.3))

        win.play(FadeOut(VGroup(title, sq, ci, sig4)), run_time=0.6)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_03_animate语法,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "03-animate语法.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
