"""RTM-Wiki · 03-动画/变换/01-Transform核心 —— 本页专属样例

文档「参数」表逐条演示：
    Transform(mobject, target_mobject, path_func, path_arc, path_arc_axis,
              path_arc_centers, replace_mobject_with_target_in_scene)
        ✓ 第一步：方块 → 圆（形状 / 位置 / 颜色都变），path_arc=PI/2 走 90° 圆弧
        ✓ 第二步：path_func=arc_up 换成自定义路径函数（插值时向上拱起）
        ✓ replace_mobject_with_target_in_scene=False：播完源留在场景（已变成目标形状）
    ReplacementTransform(mobject, target_mobject)
        ✓ 播完源消失、目标接管场景（内部固定 replace_mobject_with_target_in_scene=True）
    MoveToTarget(mobject)（先 generate_target() 改好 mobject.target）
        ✓ 位置 / 颜色 / 大小一起变形成 target

不演示：path_arc_centers —— RTM 自带的 Transform（real_time_manim/animations/transform.py）
        只把它存下来，路径实际由 path_func / path_arc 决定，传非 None 没有视觉差异；
        path_arc_axis —— 只影响 3D 弧线的旋转轴，2D 画幅下换轴弧线会转出屏幕，
        无法对比（本片显式传 OUT，与默认一致）。

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
    RED,
    YELLOW,
    DOWN,
    LEFT,
    OUT,
    RIGHT,
    UP,
    PI,
    Circle,
    Scene,
    Square,
    Text,
    Triangle,
    VGroup,
    smooth,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    Create,
    FadeIn,
    FadeOut,
    MoveToTarget,
    ReplacementTransform,
    Transform,
    Wait,  # noqa: F401
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


def arc_up(start_pts, end_pts, alpha):
    """自定义 path_func：(start_pts, end_pts, alpha) -> pts，插值时向上拱一段。"""
    pts = start_pts + (end_pts - start_pts) * alpha
    return pts + np.array([0.0, 1.1 * np.sin(np.pi * alpha), 0.0])


class Page_01_Transform核心(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # 参数 w / h / hidden
        win.scene = self                          # 参数 win.scene

        title = Text("Transform 核心 · 把 A 变成 B", font_size=44, color=ORANGE).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        # —— ① Transform：全部文档参数显式传；源与目标形状 / 位置 / 颜色都不同 ——
        lab1 = VGroup(
            Text("Transform(sq, circ, path_arc=PI / 2,", font_size=30, color=GREY_B),
            Text("  path_func=None, path_arc_axis=OUT,", font_size=30, color=GREY_B),
            Text("  replace_mobject_with_target_in_scene=False)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.3)
        sq = Square(side_length=1.5, color=BLUE).set_fill(BLUE, 0.6).move_to(LEFT * 3.6 + DOWN * 1.2)
        circ = Circle(radius=0.8, color=GREEN).set_fill(GREEN, 0.6).move_to(RIGHT * 2.8 + DOWN * 0.4)
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)
        win.play(Create(sq), run_time=0.5)
        win.play(                                                    # 点集插值变形 + 圆弧路径
            Transform(sq, circ,                                     # 参数 mobject / target_mobject ✓
                      path_func=None,                               # 参数 path_func=None ✓（下一步换自定义函数）
                      path_arc=PI / 2,                              # 参数 path_arc ✓（非默认 0：走 90° 圆弧）
                      path_arc_axis=OUT,                            # 参数 path_arc_axis ✓（2D 下恒为 z 轴）
                      path_arc_centers=None,                        # 参数 path_arc_centers ✓（见「无法演示」）
                      replace_mobject_with_target_in_scene=False,   # 参数 ✓（默认；播完源留在场景）
                      run_time=1.5),                                # 参数 run_time / **kwargs ✓
            run_time=1.5,
        )
        win.play(FadeOut(VGroup(lab1, sq)), run_time=0.5)

        # —— ② Transform 的 path_func：自定义插值路径 ——
        lab2 = VGroup(
            Text("Transform(sq2, tri, path_func=arc_up,", font_size=30, color=GREY_B),
            Text("                      run_time=1.3)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        sq2 = Square(side_length=1.2, color=YELLOW).set_fill(YELLOW, 0.6).move_to(LEFT * 3.6 + DOWN * 1.2)
        tri = Triangle(color=RED).scale(0.8).set_fill(RED, 0.6).move_to(RIGHT * 3.2 + DOWN * 1.2)
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)
        win.play(Create(sq2), run_time=0.5)
        win.play(                                     # 插值点沿自定义路径向上拱起再落下
            Transform(sq2, tri, path_func=arc_up, run_time=1.3),
            run_time=1.3,
        )
        win.play(FadeOut(VGroup(lab2, sq2)), run_time=0.5)

        # —— ③ ReplacementTransform：播完源消失、目标接管场景 ——
        lab3 = VGroup(
            Text("ReplacementTransform(left, right,", font_size=30, color=GREY_B),
            Text("                     run_time=1.2)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        left = Text("left", font_size=44, color=BLUE).move_to(LEFT * 3.2 + DOWN * 1.2)
        right = Text("right", font_size=44, color=GREEN).move_to(RIGHT * 3.2 + DOWN * 1.2)
        self.add(left)                              # 源对象先放进场景
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)
        win.play(ReplacementTransform(left, right, run_time=1.2), run_time=1.2)
        win.play(FadeOut(VGroup(lab3, right)), run_time=0.5)

        # —— ④ MoveToTarget：先 generate_target() 改好 .target 再播 ——
        lab4 = VGroup(
            Text("sq3.generate_target(); sq3.target.shift(", font_size=30, color=GREY_B),
            Text("  RIGHT * 3).scale(1.6).set_fill(GREEN, 0.6)", font_size=30, color=GREY_B),
            Text("MoveToTarget(sq3, run_time=1.3)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.3)
        sq3 = Square(side_length=0.9, color=YELLOW).set_fill(YELLOW, 0.6).move_to(LEFT * 3.4 + DOWN * 1.4)
        win.play(FadeIn(lab4, shift=DOWN), run_time=0.4)
        win.play(Create(sq3), run_time=0.5)
        sq3.generate_target()                       # 参数 mobject.target ✓（先改好目标状态）
        sq3.target.shift(RIGHT * 3).scale(1.6).set_fill(GREEN, 0.6)
        win.play(MoveToTarget(sq3, run_time=1.3), run_time=1.3)

        win.play(FadeOut(VGroup(title, lab4, sq3)), run_time=0.6)
        win.close()                                 # 参数 win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(
        Page_01_Transform核心,
        out_path=os.path.join(os.path.dirname(here), "RTM output", "01-Transform核心.mp4"),
        fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True,
    )
