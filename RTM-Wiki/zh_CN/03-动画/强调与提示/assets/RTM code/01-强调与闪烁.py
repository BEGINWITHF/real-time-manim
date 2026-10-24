"""RTM-Wiki · 03-动画/强调与提示/01-强调与闪烁 —— 本页专属样例

演示参数（文档「参数」表逐条）：
    Indicate(mobject, scale_factor=1.6, color=RED, rate_func=there_and_back, **kwargs)  ✓
    Flash(point, line_length=0.3, num_lines=30, flash_radius=0.18, line_stroke_width=5,
          color=RED, time_width=1.5, run_time=1.2, **kwargs(rate_func=rush_from))       ✓
    Blink(mobject, time_on=0.35, time_off=0.25, blinks=3, hide_at_end=True, **kwargs)   ✓
不演示：`point` 传坐标点（传 mobject 时只取中心，两者画面等价）；
        `**kwargs` 里 Transform/Animation 的其余通用参数（无独立可视效果）。
运行：python "<本文件>"（脚本会自行把仓库根目录加入 sys.path）
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    BLUE,
    DARK_GRAY,
    GREEN,
    GREY_B,
    RED,
    DOWN,
    UP,
    Dot,
    Flash,
    Scene,
    Square,
    Text,
    VGroup,
    rush_from,
    there_and_back,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    Blink,
    FadeIn,
    FadeOut,
    Indicate,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401  文件末尾 __main__ 使用


class Page_01_强调与闪烁(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # 参数 w=1280 / h=720 / hidden=True
        win.scene = self                          # 参数 win.scene

        title = Text("Indicate / Flash / Blink",
                     font_size=38, color=GREEN).to_edge(UP)   #标题只用 ASCII：两引擎字体回退才稳
        win.play(Write(title), run_time=0.8)

        # —— 步骤 1：Indicate(mobject, scale_factor, color, rate_func, **kwargs) ——
        s1a = Text("Indicate(sq, scale_factor=1.6,", font_size=32, color=GREY_B)
        s1b = Text("          color=RED, rate_func=there_and_back)", font_size=32, color=GREY_B)
        sig1 = VGroup(s1a, s1b).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        sq = Square(side_length=1.6, color=BLUE).set_fill(BLUE, 0.5).next_to(sig1, DOWN, buff=0.7)
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.45)
        win.play(
            Indicate(
                sq,                                      # 参数 mobject ✓
                scale_factor=1.6,                        # 参数 scale_factor=1.6 ✓（默认 1.2）
                color=RED,                               # 参数 color=RED ✓（默认 PURE_YELLOW）
                rate_func=there_and_back,                # 参数 rate_func ✓（显式：去一趟再回来）
            ),
            run_time=1.4,                                # 参数 **kwargs(run_time)：play 级覆盖 ✓
        )
        win.play(FadeOut(sig1), FadeOut(sq), run_time=0.45)

        # —— 步骤 2：Flash(point, line_length, num_lines, flash_radius,
        #                   line_stroke_width, color, time_width, run_time, **kwargs) ——
        s2a = Text("Flash(dot, line_length=0.3, num_lines=30,", font_size=30, color=GREY_B)
        s2b = Text("        flash_radius=0.18, line_stroke_width=5,", font_size=30, color=GREY_B)
        s2c = Text("        color=RED, time_width=1.5, rate_func=rush_from)", font_size=30, color=GREY_B)
        sig2 = VGroup(s2a, s2b, s2c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        dot = Dot(radius=0.12, color=DARK_GRAY).next_to(sig2, DOWN, buff=1.0)
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.45)
        win.play(
            Flash(
                dot,                                     # 参数 point（传 mobject → 取中心）✓
                line_length=0.3,                         # 参数 line_length=0.3 ✓（默认 0.2）
                num_lines=30,                            # 参数 num_lines=30 ✓（默认 12）
                flash_radius=0.18,                       # 参数 flash_radius=0.18 ✓（默认 0.1）
                line_stroke_width=5,                     # 参数 line_stroke_width=5 ✓（默认 3）
                color=RED,                               # 参数 color=RED ✓（默认 PURE_YELLOW）
                time_width=1.5,                          # 参数 time_width=1.5 ✓（默认 1）
                run_time=1.2,                            # 参数 run_time=1.2 ✓（默认 1.0）
                rate_func=rush_from,                     # 参数 **kwargs → 透传给每条线的 ShowPassingFlash ✓
            ),
            run_time=1.2,
        )
        win.play(FadeOut(sig2), FadeOut(dot), run_time=0.45)

        # —— 步骤 3：Blink(mobject, time_on, time_off, blinks, hide_at_end, **kwargs) ——
        s3a = Text("Blink(txt, time_on=0.35, time_off=0.25,", font_size=32, color=GREY_B)
        s3b = Text("        blinks=3, hide_at_end=True)", font_size=32, color=GREY_B)
        sig3 = VGroup(s3a, s3b).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        txt = Text("Blinking", font_size=48, color=GREEN).next_to(sig3, DOWN, buff=0.9)
        win.play(FadeIn(sig3, shift=DOWN), run_time=0.45)
        self.add(txt)                                  #Blink 不负责引入对象：先放进场景才闪得起来
        win.play(
            Blink(
                txt,                                     # 参数 mobject ✓
                time_on=0.35,                            # 参数 time_on=0.35 ✓（默认 0.5）
                time_off=0.25,                           # 参数 time_off=0.25 ✓（默认 0.5）
                blinks=3,                                # 参数 blinks=3 ✓（默认 1）
                hide_at_end=True,                        # 参数 hide_at_end=True ✓（默认 False：结束时保持隐藏）
            ),
        )
        win.play(FadeOut(sig3), run_time=0.45)

        win.play(FadeOut(title), run_time=0.5)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_01_强调与闪烁,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "01-强调与闪烁.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
