"""RTM-Wiki · 03-动画/更新器动画/01-更新器动画与自动变化 —— 本页专属样例

演示参数（文档「参数」表逐条）：
    UpdateFromFunc(mobject, update_function, suspend_mobject_updating=False,
                   **kwargs(run_time=2.4))                                       ✓
    UpdateFromAlphaFunc(mobject, update_function, suspend_mobject_updating=False,
                        **kwargs(run_time=2.0))                                  ✓
    MaintainPositionRelativeTo(mobject, tracked_mobject, **kwargs(run_time=2.2)) ✓
不演示：`suspend_mobject_updating=True` —— 会把对象自带 updater 挂起，与本页
        "每帧回调驱动"的演示目的相反，样例按文档建议显式保持 False；
        `**kwargs` 里 Transform/Animation 的其余通用参数无可视效果。
运行：python "<本文件>"（脚本会自行把仓库根目录加入 sys.path）
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    GREEN,
    GREY_B,
    PURPLE,
    RED,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Dot,
    Scene,
    Square,
    Text,
    UpdateFromAlphaFunc,
    UpdateFromFunc,
    MaintainPositionRelativeTo,
    VGroup,
    linear,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeIn,
    FadeOut,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401  文件末尾 __main__ 使用


class Page_01_更新器动画与自动变化(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # 参数 w=1280 / h=720 / hidden=True
        win.scene = self                          # 参数 win.scene

        title = Text("UpdateFromFunc / UpdateFromAlphaFunc / MaintainPositionRelativeTo",
                     font_size=24, color=GREEN).to_edge(UP)   #标题只用 ASCII：两引擎字体回退才稳
        win.play(Write(title), run_time=0.85)

        # —— 步骤 1：UpdateFromFunc(mobject, update_function, suspend..., run_time) ——
        s1a = Text("UpdateFromFunc(label, lambda l: l.next_to(dot, UP),",
                   font_size=28, color=GREY_B)
        s1b = Text("    suspend_mobject_updating=False, run_time=2.4)",
                   font_size=28, color=GREY_B)
        sig1 = VGroup(s1a, s1b).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        dot = Dot(radius=0.12, color=RED).next_to(sig1, DOWN, buff=1.1).shift(LEFT * 3.5)
        label = Text("hi", font_size=40, color=RED).next_to(dot, UP, buff=0.3)
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.45)
        self.add(dot, label)
        win.play(                                    # 参数 mobject=dot + 每帧驱动 label
            dot.animate.shift(RIGHT * 7),
            UpdateFromFunc(
                label,                               # 参数 mobject ✓
                lambda l: l.next_to(dot, UP),        # 参数 update_function ✓（每帧调用）
                suspend_mobject_updating=False,      # 参数 suspend_mobject_updating=False ✓
                run_time=2.4,                        # 参数 **kwargs：run_time=2.4 ✓（必须显式给）
            ),
            rate_func=linear,
        )
        win.play(FadeOut(sig1), FadeOut(dot), FadeOut(label), run_time=0.45)

        # —— 步骤 2：UpdateFromAlphaFunc(mobject, update_function, ...) ——
        s2a = Text("UpdateFromAlphaFunc(sq, lambda m, a: m.set_fill(RED, opacity=a),",
                   font_size=26, color=GREY_B)
        s2b = Text("    suspend_mobject_updating=False, run_time=2.0)",
                   font_size=26, color=GREY_B)
        sig2 = VGroup(s2a, s2b).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        sq = Square(side_length=2.0, color=GREEN).next_to(sig2, DOWN, buff=0.6)
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.45)
        self.add(sq)
        win.play(
            UpdateFromAlphaFunc(
                sq,                                   # 参数 mobject ✓
                lambda m, a: m.set_fill(RED, opacity=a),   # 参数 update_function ✓（多收一个进度参数）
                suspend_mobject_updating=False,       # 参数 suspend_mobject_updating=False ✓
                run_time=2.0,                         # 参数 **kwargs：run_time=2.0 ✓
            ),
        )
        win.play(FadeOut(sig2), FadeOut(sq), run_time=0.45)

        # —— 步骤 3：MaintainPositionRelativeTo(mobject, tracked_mobject, **kwargs) ——
        s3a = Text("MaintainPositionRelativeTo(b, a, run_time=2.2)",
                   font_size=30, color=GREY_B)
        sig3 = s3a.next_to(title, DOWN, buff=0.4)
        a = Dot(radius=0.14, color=GREEN).next_to(sig3, DOWN, buff=1.1).shift(LEFT * 2)
        b = Dot(radius=0.14, color=PURPLE).next_to(a, RIGHT, buff=1.2)
        win.play(FadeIn(sig3, shift=DOWN), run_time=0.45)
        self.add(a, b)
        win.play(                                    # 参数 mobject=b / tracked_mobject=a
            a.animate.shift(RIGHT * 2.5 + DOWN * 0.9),
            MaintainPositionRelativeTo(
                b,                                   # 参数 mobject（跟随者）✓
                a,                                   # 参数 tracked_mobject（被跟随者）✓
                run_time=2.2,                        # 参数 **kwargs：run_time=2.2 ✓
            ),
            rate_func=linear,
        )
        win.play(FadeOut(sig3), FadeOut(a), FadeOut(b), run_time=0.5)

        win.play(FadeOut(title), run_time=0.5)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_01_更新器动画与自动变化,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "01-更新器动画与自动变化.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
