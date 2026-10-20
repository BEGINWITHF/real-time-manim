"""RTM-Wiki · 03-动画/通用/01-生命周期与公共参数 —— 本页专属样例

演示参数（文档「参数」表逐条）：
    Animation(mobject=…)                      ✓ 所有动画都作用在 mobject 上
    run_time=1.4 / 1.6 / 0.8                  ✓ 非默认时长，逐处显式传
    lag_ratio=0.5（Write 按字形错峰）          ✓ 可视：字一个一个写出来
    rate_func=linear                          ✓ 非默认速率函数
    reverse_rate_function=True                ✓ 可视：Rotate 倒放（从终态转回）
    remover=True（FadeOut）                    ✓ 可视：播完从场景移除
    introducer=True（FadeIn）                  ✓ 可视：播放前加入场景
    Animation.set_default(run_time, rate_func)/set_default()  ✓ 批量改默认并恢复
    set_rate_func()（RTM 动画唯一实现的链式方法）              ✓
不演示：name —— 只影响 repr/日志，画面无变化；suspend_mobject_updating ——
    mobject 没有 updater 时传 True/False 画面完全一致；use_override —— 重写机制
    已接线（override_animation / animation_override_for），但要自定义 Mobject 子类
    才有效果；set_run_time/set_name/get_run_time/get_rate_func/is_introducer/
    is_remover/copy —— RTM 自有 Animation 已实现这些链式方法（tests/test_gap_wait_timeline.py）。
运行：$env:PYTHONPATH="C:\\Users\\begin\\Desktop\\real-time-manim"; python "<本文件>"
"""
import os

from real_time_manim import (
    BLUE,
    DOWN,
    GREEN,
    GREY_B,
    LEFT,
    ORANGE,
    RIGHT,
    UP,
    YELLOW,
    PI,
    Circle,
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
    Rotate,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_01_生命周期与公共参数(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # 参数 w / h / hidden
        win.scene = self                          # 参数 win.scene

        title = Text("01-动画的生命周期与公共构造参数", font_size=42, color=YELLOW).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        # —— 签名上屏：所有动画共享的构造参数 ——
        s1 = Text("Animation(mobject, lag_ratio=0.0, run_time=1.0, rate_func=smooth,", font_size=28, color=GREY_B)
        s2 = Text("           reverse_rate_function=False, name=None, remover=False,", font_size=28, color=GREY_B)
        s3 = Text("           introducer=False, use_override=True)", font_size=28, color=GREY_B)
        sig = VGroup(s1, s2, s3).arrange(DOWN, buff=0.06).to_edge(UP).shift(DOWN * 1.0)
        win.play(FadeIn(sig, shift=DOWN), run_time=0.5)

        # —— 步骤 1：run_time + rate_func ——
        l1 = Text("Create(sq, run_time=1.4, rate_func=linear)", font_size=30, color=GREY_B)
        l1.next_to(sig, DOWN, buff=0.35)
        sq = Square(side_length=1.2, color=BLUE).set_fill(BLUE, 0.5).shift(LEFT * 3.4 + DOWN * 2.4)
        ci = Circle(radius=0.62, color=GREEN).set_fill(GREEN, 0.5).shift(DOWN * 2.4)
        tri = Triangle(color=ORANGE).scale(0.75).set_fill(ORANGE, 0.5).shift(RIGHT * 3.4 + DOWN * 2.4)
        win.play(FadeIn(l1, shift=DOWN), run_time=0.4)
        win.play(Create(sq, run_time=1.4, rate_func=linear))    # 参数 run_time / rate_func

        # —— 步骤 2：lag_ratio：Write 按字形错峰 ——
        win.play(FadeOut(l1), run_time=0.3)
        l2 = Text("Write(txt, lag_ratio=0.5, run_time=1.6)", font_size=30, color=GREY_B)
        l2.next_to(sig, DOWN, buff=0.35)
        txt = Text("lag_ratio", font_size=40, color=YELLOW).shift(DOWN * 2.4)
        win.play(FadeIn(l2, shift=DOWN), run_time=0.4)
        win.play(Write(txt, lag_ratio=0.5, run_time=1.6))       # 参数 lag_ratio（字形逐个写）
        win.play(FadeOut(VGroup(l2, txt)), run_time=0.3)

        # —— 步骤 3：introducer / remover：生命周期的进出场景两个钩子 ——
        l3 = Text("FadeIn(sq2, introducer=True) / FadeOut(sq2, remover=True)",
                  font_size=30, color=GREY_B).next_to(sig, DOWN, buff=0.35)
        sq2 = Square(side_length=1.2, color=YELLOW).set_fill(YELLOW, 0.5).shift(DOWN * 2.4)
        win.play(FadeIn(l3, shift=DOWN), run_time=0.4)
        win.play(FadeIn(sq2, introducer=True, shift=UP, run_time=0.9))   # 参数 introducer
        win.play(Wait(0.3))
        win.play(FadeOut(sq2, remover=True, run_time=0.9))               # 参数 remover

        # —— 步骤 4：reverse_rate_function：倒放 ——
        win.play(FadeOut(l3), run_time=0.3)
        l4 = Text("Rotate(tri, PI/2, reverse_rate_function=True)", font_size=30, color=GREY_B)
        l4.next_to(sig, DOWN, buff=0.35)
        win.play(FadeIn(l4, shift=DOWN), run_time=0.4)
        win.play(Rotate(tri, PI / 2, reverse_rate_function=True,
                        run_time=1.2, rate_func=linear))        # 参数 reverse_rate_function（从 PI/2 倒回 0）
        win.play(FadeOut(l4), run_time=0.3)

        # —— 步骤 5：set_default 批量默认值 + set_rate_func 链式方法 ——
        l5 = Text("Rotate.set_default(run_time=1.2, rate_func=linear)", font_size=30, color=GREY_B)
        l6 = Text("  ->  win.play(Rotate(ci, PI/2))   # 1.2s 线性由默认值提供", font_size=28, color=GREY_B)
        l7 = Text("rot.set_rate_func(linear)  # RTM 动画实现的链式方法", font_size=28, color=GREY_B)
        sig5 = VGroup(l5, l6, l7).arrange(DOWN, buff=0.06).next_to(sig, DOWN, buff=0.35)
        win.play(FadeIn(sig5, shift=DOWN), run_time=0.4)
        Rotate.set_default(run_time=1.2, rate_func=linear)      # Animation.set_default(**kwargs)
        win.play(Rotate(ci, PI / 2))                            # 参数 run_time=1.2 / rate_func=linear（来自默认值）
        Rotate.set_default()                                    # 传空参恢复默认
        rot = Rotate(ci, -PI / 2, run_time=0.8)
        rot.set_rate_func(linear)                               # 方法 set_rate_func
        win.play(rot)

        win.play(FadeOut(VGroup(title, sig, sq, ci, tri, sig5)), run_time=0.6)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_01_生命周期与公共参数,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "01-生命周期与公共参数.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
