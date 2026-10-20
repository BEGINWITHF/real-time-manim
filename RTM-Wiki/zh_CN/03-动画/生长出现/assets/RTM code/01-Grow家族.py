"""RTM-Wiki · 03-动画/生长出现/01-Grow家族 —— 本页专属样例

演示参数（文档「参数」表逐条）：
    GrowFromPoint(mobject, point=ORIGIN, point_color=RED, run_time=1.3)  ✓
    GrowFromPoint(mobject, point=Dot（mobject 也能当 point）, point_color=BLUE, …)  ✓
    GrowFromCenter(mobject, point_color=GREEN, run_time=1.3)  ✓
    GrowFromEdge(mobject, edge=RIGHT, point_color=ORANGE, run_time=1.3)  ✓
不演示：point_color=None（默认=沿用对象自身颜色，与"不传"无差别）；
    **kwargs 里的 path_arc / path_func（Transform 路径参数，在 Grow 中不可视）。
运行：$env:PYTHONPATH="C:\\Users\\begin\\Desktop\\real-time-manim"; python "<本文件>"
"""
import os

from real_time_manim import (
    BLUE,
    GREEN,
    GREY_B,
    ORANGE,
    RED,
    YELLOW,
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    Circle,
    Dot,
    Rectangle,
    Scene,
    Square,
    Text,
    Triangle,
    VGroup,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    GrowFromEdge,
    GrowFromPoint,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_01_Grow家族(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # 参数 w=1280 / h=720 / hidden=True
        win.scene = self

        title = Text("Grow 家族：Point / Center / Edge", font_size=44, color=YELLOW).to_edge(UP)
        win.play(Write(title, run_time=0.8), run_time=0.8)

        # —— 一、GrowFromPoint：从指定点长出来（point 可以是坐标，也可以是 mobject）——
        l1 = Text("GrowFromPoint(mobject, point, point_color, run_time=1.3)",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)
        sq = Square(side_length=1.4, color=BLUE).next_to(l1, DOWN, buff=0.7).shift(LEFT * 2.6)
        anchor = Dot(radius=0.1, color=GREY_B).next_to(l1, DOWN, buff=0.7).shift(RIGHT * 1.4)
        tri = Triangle(color=RED).scale(0.8).next_to(l1, DOWN, buff=0.7).shift(RIGHT * 3.4)
        win.play(FadeIn(VGroup(l1, anchor), shift=DOWN), run_time=0.4)
        win.play(
            GrowFromPoint(                          # 参数 mobject=sq
                sq,
                ORIGIN,                              # 参数 point=ORIGIN（坐标当起点）
                point_color=RED,                     # 参数 point_color=RED（起点是红色）
                run_time=1.3,                        # 参数 **kwargs(run_time)
            ),
            run_time=1.3,
        )
        win.play(
            GrowFromPoint(                          # 参数 mobject=tri
                tri,
                anchor,                              # 参数 point=另一个 mobject（取其中心）
                point_color=BLUE,                    # 参数 point_color=BLUE
                run_time=1.3,                        # 参数 **kwargs(run_time)
            ),
            run_time=1.3,
        )
        win.play(FadeOut(VGroup(l1, sq, anchor, tri)), run_time=0.5)

        # —— 二、GrowFromCenter：从自身中心长大 ——
        l2 = Text("GrowFromCenter(mobject, point_color=GREEN, run_time=1.3)",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)
        ci = Circle(radius=0.85, color=GREEN).next_to(l2, DOWN, buff=0.7)
        win.play(FadeIn(l2, shift=DOWN), run_time=0.4)
        win.play(
            GrowFromCenter(                         # 参数 mobject
                ci,                                 # （point 由自身中心自动给出）
                point_color=GREEN,                  # 参数 point_color=GREEN
                run_time=1.3,                       # 参数 **kwargs(run_time)
            ),
            run_time=1.3,
        )
        win.play(FadeOut(VGroup(l2, ci)), run_time=0.5)

        # —— 三、GrowFromEdge：从包围盒的某条边长出来 ——
        l3 = Text("GrowFromEdge(mobject, edge=RIGHT, point_color=ORANGE)",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)
        rect = (Rectangle(width=3.4, height=1.1, color=ORANGE)
                .next_to(l3, DOWN, buff=0.8))
        win.play(FadeIn(l3, shift=DOWN), run_time=0.4)
        win.play(
            GrowFromEdge(                           # 参数 mobject
                rect,
                RIGHT,                              # 参数 edge=RIGHT（从右边长出来）
                point_color=ORANGE,                 # 参数 point_color=ORANGE
                run_time=1.3,                       # 参数 **kwargs(run_time)
            ),
            run_time=1.3,
        )

        win.play(Wait(0.5))
        win.play(FadeOut(VGroup(l3, rect)), run_time=0.6)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(
        Page_01_Grow家族,
        out_path=os.path.join(os.path.dirname(here), "RTM output", "01-Grow家族.mp4"),
        fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
