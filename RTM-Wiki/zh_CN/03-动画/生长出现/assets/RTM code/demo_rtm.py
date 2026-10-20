"""RTM-Wiki · 03-动画/生长出现 视频样例（RTM 渲染）

一段场景覆盖本文件夹 2 个页面的可演示参数，用注释分隔：

    # ========== 01-Grow家族.md ==========
    # ========== 01b-箭头与旋入.md ==========

只使用 RTM 已导出的动画类（✅ 名单，见 99-功能状态总览），
本组 5 个类（GrowFromPoint / GrowFromCenter / GrowFromEdge / GrowArrow /
SpinInFromNothing）全部为 RTM 自有实现。

运行（cwd 必须是 real-time-manim 仓库）：
    $env:PYTHONPATH="C:\\Users\\begin\\Desktop\\real-time-manim"
    python demo_rtm.py      # -> assets\\sample.mp4
"""
import os

from real_time_manim import (
    BLUE,
    GOLD,
    GREEN,
    ORANGE,
    PURPLE,
    RED,
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    PI,
    Arrow,
    Circle,
    Rectangle,
    Scene,
    Square,
    Star,
    Text,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeOut,
    GrowArrow,
    GrowFromCenter,
    GrowFromEdge,
    GrowFromPoint,
    SpinInFromNothing,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401  文件末尾 __main__ 使用


class Demo_Grow(Scene):
    def construct(self):
        # 参数 MLWindow(w=1280, h=720, hidden=True) ✓ —— 全片共用一个窗口
        win = MLWindow(1280, 720, hidden=True)
        win.scene = self

        # ========== 01-Grow家族.md ==========
        # GrowFromPoint(mobject, point, point_color=None, **kwargs)
        # GrowFromCenter(mobject, point_color=None, **kwargs)
        # GrowFromEdge(mobject, edge, point_color=None, **kwargs)
        t01 = Text("Grow 家族：Point / Center / Edge", font_size=34).to_edge(UP)
        win.play(Write(t01, run_time=0.8), run_time=0.8)

        sq = Square(side_length=1.6, color=BLUE).shift(LEFT * 4.6 + DOWN * 1.0)
        win.play(                                                          # GrowFromPoint：从指定点长出来
            GrowFromPoint(
                sq,                                                        # 参数 mobject ✓
                ORIGIN,                                                    # 参数 point=ORIGIN ✓（从画面中心长到原位）
                point_color=RED,                                           # 参数 point_color=RED ✓（起始为红色）
                run_time=1.4,                                              # 参数 **kwargs(run_time) ✓
            ),
            run_time=1.4,
        )

        ci = Circle(radius=0.9, color=GREEN).shift(DOWN * 1.0)
        win.play(                                                          # GrowFromCenter：从自身中心长出来
            GrowFromCenter(
                ci,                                                        # 参数 mobject ✓
                point_color=BLUE,                                          # 参数 point_color=BLUE ✓
                run_time=1.4,                                              # 参数 **kwargs(run_time) ✓
            ),
            run_time=1.4,
        )

        rect = Rectangle(width=3, height=1, color=ORANGE).shift(RIGHT * 3.6 + DOWN * 1.0)
        win.play(                                                          # GrowFromEdge：从包围盒的某条边长出来
            GrowFromEdge(
                rect,                                                      # 参数 mobject ✓
                DOWN,                                                      # 参数 edge=DOWN ✓（从底边长出）
                point_color=RED,                                           # 参数 point_color=RED ✓
                run_time=1.4,                                              # 参数 **kwargs(run_time) ✓
            ),
            run_time=1.4,
        )
        win.play(FadeOut(sq, run_time=0.6), FadeOut(ci, run_time=0.6),
                  FadeOut(rect, run_time=0.6), FadeOut(t01, run_time=0.6), run_time=0.6)

        # ========== 01b-箭头与旋入.md ==========
        # GrowArrow(arrow, point_color=None, **kwargs)
        # SpinInFromNothing(mobject, angle=PI / 2, point_color=None, **kwargs)
        t01b = Text("生长出现：GrowArrow / SpinInFromNothing", font_size=34).to_edge(UP)
        win.play(Write(t01b, run_time=0.8), run_time=0.8)

        arr = Arrow(ORIGIN + LEFT * 3.6 + DOWN * 1.0, ORIGIN + RIGHT * 0.4 + DOWN * 1.0,
                    buff=0, color=GOLD, stroke_width=6)
        win.play(                                                          # GrowArrow：箭头从起点长向箭尖
            GrowArrow(
                arr,                                                       # 参数 arrow ✓
                point_color=RED,                                           # 参数 point_color=RED ✓
                run_time=1.6,                                              # 参数 **kwargs(run_time) ✓
            ),
            run_time=1.6,
        )

        star = Star(n=5, outer_radius=1.1, color=PURPLE).shift(RIGHT * 3.6 + DOWN * 1.0)
        win.play(                                                          # SpinInFromNothing：边旋转边长大
            SpinInFromNothing(
                star,                                                      # 参数 mobject ✓
                angle=2 * PI,                                              # 参数 angle=2*PI ✓（长大的同时多转一整圈）
                point_color=BLUE,                                          # 参数 point_color=BLUE ✓
                run_time=1.8,                                              # 参数 **kwargs(run_time) ✓
            ),
            run_time=1.8,
        )
        win.play(Wait(0.4))                                                # 参数 Wait ✓

        # 参数 win.close() ✓ —— 关闭窗口、结束渲染
        win.close()


if __name__ == "__main__":
    fast_record_scene(Demo_Grow, out_path=os.path.join(os.path.dirname(__file__), "sample.mp4"), fps=30, overwrite=True, cleanup=True)
