"""RTM-Wiki · 03-动画/更新器动画/01b-更新工具与自动变化 —— 本页专属样例

演示参数（文档「参数」表逐条）：
    always_redraw(func)                                        ✓ 配 ValueTracker(alpha.animate.set_value(PI))
    always(method, *args)            —— always(sq.next_to, dot2, DOWN)                     ✓
    f_always(method, *arg_generators) —— f_always(lbl.next_to, dot2.get_center, UP)        ✓
    always_shift(mobject, direction=UP, rate=0.9)                                        ✓
    always_rotate(mobject, rate=PI)                                                      ✓
    turn_animation_into_updater(animation, cycle=False, delay=0.3)                       ✓
    cycle_animation(animation)             —— cycle_animation(ApplyWave(...))             ✓
    TracedPath(traced_point_func, stroke_width=5, stroke_color=YELLOW,
               dissipating_time=0.6)                                                     ✓
    AnimatedBoundary(vmobject, colors=[RED, GREEN, BLUE], max_stroke_width=4, cycle_rate=3,
                     back_and_forth=True, draw_rate_func=smooth, fade_rate_func=smooth)  ✓
不演示：`override_animation`（类方法装饰器：要自定义 Mobject 子类才有意义，
        效果等同直接改写方法，无可视参数差异）；`always_rotate` 的 `**kwargs`
        （传给 `rotate` 的 `about_point` 等，样例用默认绕自身中心）。
注意：`turn_animation_into_updater` / `cycle_animation` 按 alpha 语义调用
      `animation.interpolate(alpha)`，而 RTM 自有的 `Write` / `ApplyWave` 是时间语义
      （`begin(t)`、`interpolate(t)`），两者不兼容；本页第 4 步因此用 manim 原生的
      `Write` / `ApplyWave`（RTM 的 render_hooks 已接线，可正常渲染）。
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
    PI,
    RED,
    YELLOW,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    AnimatedBoundary,
    ApplyWave,
    Circle,
    Dot,
    Scene,
    Square,
    Text,
    TracedPath,
    Triangle,
    ValueTracker,
    VGroup,
    Write,
    always,
    always_redraw,
    always_rotate,
    always_shift,
    cycle_animation,
    f_always,
    linear,
    smooth,
    turn_animation_into_updater,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeIn,
    FadeOut,
    Wait,
)
from real_time_manim.record import fast_record_scene  # noqa: F401  文件末尾 __main__ 使用


class Page_01b_更新工具与自动变化(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # 参数 w=1280 / h=720 / hidden=True
        win.scene = self                          # 参数 win.scene

        title = Text("Update utils 12.1 / TracedPath / AnimatedBoundary",
                     font_size=34, color=GREEN).to_edge(UP)   #标题只用 ASCII：两引擎字体回退才稳
        win.play(Write(title), run_time=0.8)

        # —— 步骤 1：always_redraw(func) —— 每帧按 func() 重新生成对象 ——
        s1a = Text("alpha = ValueTracker(0)", font_size=28, color=GREY_B)
        s1b = Text("dot = always_redraw(lambda: Dot([2cos t, 2sin t-1, 0], BLUE))",
                   font_size=26, color=GREY_B)
        s1c = Text("win.play(alpha.animate.set_value(PI), run_time=1.6, rate_func=linear)",
                   font_size=24, color=GREY_B)
        sig1 = VGroup(s1a, s1b, s1c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.35)
        alpha = ValueTracker(0)
        dot = always_redraw(lambda: Dot(                    # 参数 func：每帧重新生成 ✓
            [np.cos(alpha.get_value()) * 2,
             np.sin(alpha.get_value()) * 2 - 1.2, 0], color=BLUE))
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.4)
        self.add(dot)
        win.play(alpha.animate.set_value(PI), run_time=1.6, rate_func=linear)
        win.play(FadeOut(sig1), FadeOut(dot), run_time=0.4)

        # —— 步骤 2：always / f_always —— 每帧调用绑定方法 / 每帧重新求值参数 ——
        s2a = Text("always(sq.next_to, dot2, DOWN)", font_size=30, color=GREY_B)
        s2b = Text("f_always(lbl.next_to, dot2.get_center, direction=UP)", font_size=28, color=GREY_B)
        s2c = Text("win.play(dot2.animate.shift(RIGHT * 5), run_time=1.5, rate_func=linear)",
                   font_size=24, color=GREY_B)
        sig2 = VGroup(s2a, s2b, s2c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.35)
        dot2 = Dot(radius=0.1, color=RED).next_to(sig2, DOWN, buff=0.9).shift(LEFT * 2.5)
        sq = Square(side_length=0.9, color=ORANGE).set_fill(ORANGE, 0.7)
        lbl = Text("f_always", font_size=30, color=ORANGE)
        always(sq.next_to, dot2, DOWN)                      # 参数 method(*args)：固定参数每帧调用 ✓
        f_always(lbl.next_to, dot2.get_center, direction=UP)  # 参数 method(*生成函数)：每帧重新求值 ✓
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.4)
        self.add(dot2, sq, lbl)
        win.play(dot2.animate.shift(RIGHT * 5), run_time=1.5, rate_func=linear)
        sq.clear_updaters()
        lbl.clear_updaters()
        win.play(FadeOut(sig2), FadeOut(dot2), FadeOut(sq), FadeOut(lbl), run_time=0.4)

        # —— 步骤 3：always_shift / always_rotate —— 不 play，随时间自动变化 ——
        s3a = Text("always_shift(tri, direction=UP, rate=0.9)", font_size=30, color=GREY_B)
        s3b = Text("always_rotate(tri, rate=PI)", font_size=30, color=GREY_B)
        sig3 = VGroup(s3a, s3b).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.35)
        tri = Triangle().set_fill(GREEN, 0.7).set_stroke(GREEN, width=4)
        tri.next_to(sig3, DOWN, buff=0.8).shift(LEFT * 3 + DOWN * 0.8)
        always_shift(tri, direction=UP, rate=0.9)           # 参数 direction=UP / rate=0.9 ✓
        always_rotate(tri, rate=PI)                         # 参数 rate=PI ✓（默认 20*DEGREES）
        win.play(FadeIn(sig3, shift=DOWN), run_time=0.4)
        self.add(tri)
        win.play(Wait(1.5))
        tri.clear_updaters()
        win.play(FadeOut(sig3), FadeOut(tri), run_time=0.4)

        # —— 步骤 4：turn_animation_into_updater / cycle_animation ——
        s4a = Text("turn_animation_into_updater(Write(words), cycle=False, delay=0.3)",
                   font_size=24, color=GREY_B)
        s4b = Text("cycle_animation(ApplyWave(wave, amplitude=0.3, ripples=2))",
                   font_size=26, color=GREY_B)
        s4c = Text("win.play(Wait(2.0))", font_size=26, color=GREY_B)
        sig4 = VGroup(s4a, s4b, s4c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.35)
        words = Text("Welcome", font_size=46, color=YELLOW).next_to(sig4, DOWN, buff=0.9).shift(LEFT * 3)
        wave = Text("wave", font_size=46, color=BLUE).next_to(sig4, DOWN, buff=0.9).shift(RIGHT * 3)
        turn_animation_into_updater(                        # 参数 animation ✓
            Write(words, run_time=1.2), cycle=False, delay=0.3)   # 参数 cycle=False / delay=0.3 ✓
        cycle_animation(                                    # 参数 animation ✓（= turn_animation_into_updater(cycle=True)）
            ApplyWave(wave, amplitude=0.3, ripples=2, run_time=1.0))
        win.play(FadeIn(sig4, shift=DOWN), run_time=0.4)
        self.add(words, wave)
        win.play(Wait(2.0))                                 # 不 play 动画本身，updater 随时间推进
        wave.clear_updaters()
        win.play(FadeOut(sig4), FadeOut(words), FadeOut(wave), run_time=0.4)

        # —— 步骤 5：TracedPath(traced_point_func, stroke_width, stroke_color,
        #                      dissipating_time) —— 记录点轨迹画成线 ——
        s5a = Text("trace = TracedPath(circ.get_start, stroke_width=5,", font_size=26, color=GREY_B)
        s5b = Text("                     stroke_color=YELLOW, dissipating_time=0.6)", font_size=24, color=GREY_B)
        s5c = Text("group.add_updater(lambda m: m.rotate(-0.3))", font_size=28, color=GREY_B)
        s5d = Text("win.play(group.animate.shift(RIGHT * 6), run_time=2, rate_func=linear)",
                   font_size=24, color=GREY_B)
        sig5 = VGroup(s5a, s5b, s5c, s5d).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.35)
        circ = Circle(radius=0.7, color=RED, stroke_width=4).next_to(sig5, DOWN, buff=0.5)
        dot5 = Dot(radius=0.08, color=RED).move_to(circ.get_start())
        group = VGroup(circ, dot5)
        group.add_updater(lambda m: m.rotate(-0.3))
        trace = TracedPath(                                 # 参数 traced_point_func ✓
            circ.get_start,
            stroke_width=5,                                 # 参数 stroke_width=5 ✓（默认 2）
            stroke_color=YELLOW,                            # 参数 stroke_color=YELLOW ✓（默认 WHITE）
            dissipating_time=0.6,                           # 参数 dissipating_time=0.6 ✓（拖尾消散）
        )
        win.play(FadeIn(sig5, shift=DOWN), run_time=0.4)
        self.add(trace, group)
        win.play(group.animate.shift(RIGHT * 6), run_time=2.0, rate_func=linear)
        group.clear_updaters()
        win.play(FadeOut(sig5), FadeOut(trace), FadeOut(group), run_time=0.4)

        # —— 步骤 6：AnimatedBoundary(vmobject, colors, max_stroke_width, cycle_rate,
        #                             back_and_forth, draw/fade_rate_func) ——
        s6a = Text("AnimatedBoundary(txt, colors=[RED, GREEN, BLUE],", font_size=28, color=GREY_B)
        s6b = Text("    max_stroke_width=4, cycle_rate=3, back_and_forth=True,",
                   font_size=26, color=GREY_B)
        s6c = Text("    draw_rate_func=smooth, fade_rate_func=smooth)",
                   font_size=26, color=GREY_B)
        sig6 = VGroup(s6a, s6b, s6c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.35)
        txt = Text("So shiny!", font_size=46, color=GREEN).next_to(sig6, DOWN, buff=1.0)
        boundary = AnimatedBoundary(                        # 参数 vmobject ✓
            txt,
            colors=[RED, GREEN, BLUE],                      # 参数 colors ✓（默认 [BLUE_D, BLUE_B, BLUE_E, GREY_BROWN]）
            max_stroke_width=4,                             # 参数 max_stroke_width=4 ✓（默认 3）
            cycle_rate=3,                                   # 参数 cycle_rate=3 ✓（默认 0.5）
            back_and_forth=True,                            # 参数 back_and_forth=True ✓（来回描绘）
            draw_rate_func=smooth,                          # 参数 draw_rate_func=smooth ✓
            fade_rate_func=smooth,                          # 参数 fade_rate_func=smooth ✓
        )
        win.play(FadeIn(sig6, shift=DOWN), run_time=0.4)
        self.add(txt, boundary)
        win.play(Wait(1.5))
        win.play(FadeOut(sig6), FadeOut(txt), FadeOut(boundary), run_time=0.45)
        win.play(Wait(0.3))

        win.play(FadeOut(title), run_time=0.5)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_01b_更新工具与自动变化,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "01b-更新工具与自动变化.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
