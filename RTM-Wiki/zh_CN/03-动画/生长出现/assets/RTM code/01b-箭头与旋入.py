"""RTM-Wiki · 03-动画/生长出现/01b-箭头与旋入 —— 本页专属样例

演示参数（文档「参数」表逐条）：
    GrowArrow(arrow, point_color=RED, run_time=1.7)  ✓
    SpinInFromNothing(mobject, angle=2*PI, point_color=BLUE, run_time=1.9)  ✓
    SpinInFromNothing(mobject, angle=PI/2, point_color=None, run_time=1.5)  ✓ 默认角度对照
不演示：point_color=None 单独成步（默认=沿用对象自身颜色，与"不传"无差别）；
    **kwargs 的 path_func 被 spiral_path(angle) 占用、不可另传。
运行：$env:PYTHONPATH="C:\\Users\\begin\\Desktop\\real-time-manim"; python "<本文件>"
"""
import os

from real_time_manim import (
    BLUE,
    GOLD,
    GREY_B,
    PURPLE,
    RED,
    YELLOW,
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    PI,
    Arrow,
    Circle,
    Scene,
    Star,
    Text,
    VGroup,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeIn,
    FadeOut,
    GrowArrow,
    SpinInFromNothing,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_01b_箭头与旋入(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # 参数 w=1280 / h=720 / hidden=True
        win.scene = self

        title = Text("生长出现：GrowArrow / SpinInFromNothing", font_size=42, color=YELLOW).to_edge(UP)
        win.play(Write(title, run_time=0.8), run_time=0.8)

        # —— 一、GrowArrow：箭头从起点长向箭尖 ——
        l1 = Text("GrowArrow(arrow, point_color=RED, run_time=1.7)",
                  font_size=32, color=GREY_B).next_to(title, DOWN, buff=0.5)
        arr = Arrow(ORIGIN + LEFT * 3.2 + DOWN * 1.0, ORIGIN + RIGHT * 1.2 + DOWN * 1.0,
                    buff=0, color=GOLD, stroke_width=6).next_to(l1, DOWN, buff=0.9).shift(LEFT * 1.0)
        win.play(FadeIn(l1, shift=DOWN), run_time=0.4)
        win.play(
            GrowArrow(arr,                          # 参数 arrow
                      point_color=RED,              # 参数 point_color=RED（起点偏红，长出恢复金色）
                      run_time=1.7),                # 参数 **kwargs(run_time)
            run_time=1.7,
        )
        win.play(FadeOut(VGroup(l1, arr)), run_time=0.5)

        # —— 二、SpinInFromNothing：边旋转边长大（angle 非默认：多转一整圈）——
        l2 = Text("SpinInFromNothing(mobject, angle=2*PI, point_color=BLUE)",
                  font_size=32, color=GREY_B).next_to(title, DOWN, buff=0.5)
        star = Star(n=5, outer_radius=1.0, color=PURPLE).next_to(l2, DOWN, buff=0.8).shift(LEFT * 2.2)
        win.play(FadeIn(l2, shift=DOWN), run_time=0.4)
        win.play(
            SpinInFromNothing(                      # 参数 mobject
                star,
                angle=2 * PI,                       # 参数 angle=2*PI（长大时多转一整圈）
                point_color=BLUE,                   # 参数 point_color=BLUE
                run_time=1.9),                      # 参数 **kwargs(run_time)
            run_time=1.9,
        )
        # 对照：angle 取默认值 PI/2 的小转
        l3 = Text("SpinInFromNothing(mobject, angle=PI/2)   # 默认角度对照",
                  font_size=32, color=GREY_B).next_to(l2, DOWN, buff=1.9).shift(RIGHT * 2.4)
        ci = Circle(radius=0.6, color=GREY_B).next_to(l3, DOWN, buff=0.6)
        win.play(FadeIn(VGroup(l3, ci), shift=DOWN), run_time=0.4)
        win.play(
            SpinInFromNothing(                      # 参数 mobject
                ci,
                angle=PI / 2,                       # 参数 angle=PI/2（= 默认值，仅转 90°）
                run_time=1.5),                      # 参数 **kwargs(run_time)
            run_time=1.5,
        )

        win.play(Wait(0.5))
        win.play(FadeOut(VGroup(title, star, l3, ci)), run_time=0.6)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(
        Page_01b_箭头与旋入,
        out_path=os.path.join(os.path.dirname(here), "RTM output", "01b-箭头与旋入.mp4"),
        fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
