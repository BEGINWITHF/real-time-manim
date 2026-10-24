"""RTM-Wiki · 03-动画/通用/02-play与wait参数 —— 本页专属样例

演示参数（文档「参数」表逐条）：
    win.play(*anims)                                    ✓ 一次播多个动画对象
    win.play(..., run_time=1.6)                         ✓ play 级关键字逐个 setattr 到每个动画
    win.play(..., rate_func=linear)                     ✓ 同上（速率函数）
    win.play(*[FadeIn(m) for m in dots])                ✓ 列表/生成器展开成多个动画
    win.play(Wait(1.2))  ≡  Scene.wait(duration=1.2)    ✓ duration
不演示：subcaption / subcaption_duration / subcaption_offset —— 三形参已接线（见页尾
    「2026-10-16 更新」与 01-场景与相机/场景/04-分段字幕与声音），本页不演示；Scene.pause /
    Scene.wait_until 与 Wait 的 stop_condition / frozen_frame —— 均已支持，演示见 01-场景与相机/
    场景/03-播放与等待；play 级 lag_ratio —— RTM 的 win.play
    只覆盖 run_time / rate_func 两个关键字，错峰请写在动画构造器或 AnimationGroup 上。
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
    ORANGE,
    PURPLE,
    RED,
    RIGHT,
    UP,
    YELLOW,
    Circle,
    Dot,
    Scene,
    Square,
    Text,
    Triangle,
    VGroup,
    linear,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    Create,
    FadeIn,
    FadeOut,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_02_play与wait参数(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # 参数 w / h / hidden
        win.scene = self                          # 参数 win.scene

        title = Text("02-Scene.play / wait 参数（win.play 等价）", font_size=42, color=YELLOW).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        # —— 步骤 1：一次 play 多个动画 + play 级 run_time / rate_func ——
        l1 = Text("win.play(Create(sq), FadeIn(ci, scale=0.5),", font_size=30, color=GREY_B)
        l2 = Text("         run_time=1.6, rate_func=linear)   # 逐个 setattr", font_size=30, color=GREY_B)
        sig1 = VGroup(l1, l2).arrange(DOWN, buff=0.06).to_edge(UP).shift(DOWN * 1.05)
        sq = Square(side_length=1.3, color=BLUE).set_fill(BLUE, 0.5).shift(LEFT * 2.4 + DOWN * 2.0)
        ci = Circle(radius=0.68, color=GREEN).set_fill(GREEN, 0.5).shift(RIGHT * 2.4 + DOWN * 2.0)
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.4)
        win.play(
            Create(sq),                          # 参数 *anims 之 Create
            FadeIn(ci, scale=0.5),               # 参数 *anims 之 FadeIn(scale)
            run_time=1.6,                        # 参数 **kwargs: run_time（两个动画都被拉到 1.6s）
            rate_func=linear,                    # 参数 **kwargs: rate_func
        )
        win.play(FadeOut(VGroup(sig1, sq, ci)), run_time=0.4)

        # —— 步骤 2：列表展开：win.play(*[FadeIn(m) for m in dots]) ——
        l3 = Text("win.play(*[FadeIn(m, shift=DOWN) for m in dots])",
                  font_size=30, color=GREY_B).to_edge(UP).shift(DOWN * 1.05)
        cols = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]
        dots = VGroup(*[Dot(radius=0.16, color=c).shift(LEFT * 5 + RIGHT * 2 * i + DOWN * 1.9)
                        for i, c in enumerate(cols)])
        win.play(FadeIn(l3, shift=DOWN), run_time=0.4)
        win.play(*[FadeIn(m, shift=DOWN) for m in dots])          # 参数 *anims（列表/生成器展开）
        win.play(Wait(0.4))
        win.play(FadeOut(VGroup(l3, dots)), run_time=0.4)

        # —— 步骤 3：Wait(duration)：≈ Scene.wait(duration) ——
        l4 = Text("win.play(Wait(1.2))   #  ≡  self.wait(1.2)", font_size=30, color=GREY_B)
        l4.to_edge(UP).shift(DOWN * 1.05)
        tr = Triangle(color=ORANGE).scale(0.8).set_fill(ORANGE, 0.5).shift(DOWN * 1.9)
        txt = Text("静止 1.2 秒", font_size=30, color=GREY_B).next_to(tr, DOWN, buff=0.45)
        win.play(FadeIn(l4, shift=DOWN), FadeIn(tr), FadeIn(txt), run_time=0.4)
        win.play(Wait(1.2))                                        # 参数 duration=1.2
        win.play(Wait(0.4))

        win.play(FadeOut(VGroup(title, l4, tr, txt)), run_time=0.6)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_02_play与wait参数,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "02-play与wait参数.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
