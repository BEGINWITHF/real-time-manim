# -*- coding: utf-8 -*-
"""03-测量.md 五个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 03-测量.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的五条样例视频（输出到上一级 assets/）。
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    Scene, VGroup, Square, Rectangle, Circle, Dot,
    BLUE, GREEN, YELLOW, RED, UR, DOWN, LEFT, RIGHT, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：width / height / depth =====================================
class SizeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        rect = Rectangle(width=4.0, height=2.0, color=BLUE, fill_opacity=0.4)   #4×2 的矩形
        self.add(rect)   #进场景
        print("初始：width =", rect.width, "height =", rect.height, "depth =", rect.depth)   #4.0 2.0 0.0
        win.play(rect.animate.set(width=2.0), run_time=0.6)   #给 “width” 赋值 = 等比缩放
        print("width=2.0 后：width =", rect.width, "height =", rect.height)   #2.0 1.0：高度等比跟着变
        win.play(rect.animate.set(height=3.0), run_time=0.6)   #给 “height” 赋值：等比放大
        print("height=3.0 后：width =", rect.width, "height =", rect.height)   #6.0 3.0
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：get_center / get_top / get_bottom / get_left / get_right ====
class EdgesDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=BLUE, side_length=2.4, fill_opacity=0.4)   #2.4 见方的方块
        self.add(sq)   #进场景
        marks = VGroup()   #关键点标记
        for name, p in (
            ("center", sq.get_center()),
            ("top", sq.get_top()),
            ("bottom", sq.get_bottom()),
            ("left", sq.get_left()),
            ("right", sq.get_right()),
        ):   #中心与四边中点
            marks.add(Dot(color=RED, radius=0.08).move_to(p))   #在关键点上打一个红点
            print(name, "=", p.round(2))   #打印坐标验证
        self.add(marks)   #标记进场景
        win.play(FadeIn(marks), run_time=0.5)   #五个红点淡入
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：get_x / get_y / get_z / get_coord / get_corner =============
class CoordsGetDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=GREEN, side_length=2.0).shift(RIGHT * 1.5)   #右移 1.5 的方块
        self.add(sq)   #进场景
        print("get_x =", sq.get_x(), "| get_x(LEFT) =", sq.get_x(direction=LEFT))   #1.5 0.5
        print("get_y =", sq.get_y(), "| get_z =", sq.get_z())   #0.0 0.0
        print("get_coord(0, UR) =", sq.get_coord(0, UR))   #UR 角点的 x
        marks = VGroup()   #关键点标记
        for name, p in (
            ("corner(UR)", sq.get_corner(UR)),
            ("edge_center(DOWN)", sq.get_edge_center(DOWN)),
            ("critical_point(LEFT)", sq.get_critical_point(LEFT)),
        ):   #角点 / 边中点 / 通用关键点
            marks.add(Dot(color=RED, radius=0.08).move_to(p))   #在关键点上打一个红点
            print(name, "=", p.round(2))   #打印坐标验证
        self.add(marks)   #标记进场景
        win.play(FadeIn(marks), run_time=0.5)   #红点淡入
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：length_over_dim / get_all_points ===========================
class MeasurePointsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        circ = Circle(radius=1.2, color=YELLOW)   #半径 1.2 的圆
        self.add(circ)   #进场景
        print("length_over_dim(0/1/2) =", [float(circ.length_over_dim(i)) for i in range(3)])   #2.4 2.4 0.0
        pts = circ.get_all_points()   #自身及全部后代的所有顶点
        print("get_all_points =", pts.shape)   #(32, 3)
        cloud = VGroup(*[Dot(color=RED, radius=0.03).move_to(p) for p in pts])   #每个顶点打一个小红点
        self.add(cloud)   #顶点云进场景
        win.play(FadeIn(cloud), run_time=0.6)   #顶点云淡入：贝塞尔控制点
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 5：重心与边界点族 + 底层统计 =================================
class StatsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        c = Circle(radius=1.4, color=BLUE)   #半径 1.4 的圆
        self.add(c)   #进场景
        marks = VGroup()   #关键点标记
        for name, p in (
            ("center_of_mass", c.get_center_of_mass()),
            ("midpoint", c.get_midpoint()),
            ("boundary_point(UR)", c.get_boundary_point(UR)),
            ("zenith", c.get_zenith()),
            ("z_index_ref", c.get_z_index_reference_point()),
        ):   #重心与边界点族（平面对象的 zenith 落在中心）
            marks.add(Dot(color=RED, radius=0.07).move_to(p))   #在关键点上打一个红点
            print(name, "=", p.round(2))   #打印坐标验证
        self.add(marks)   #标记进场景
        print("get_extremum_along_dim(key=1/-1) =", c.get_extremum_along_dim(dim=0, key=1), c.get_extremum_along_dim(dim=0, key=-1))   #最右 / 最左 x
        print("reduce_across_dimension(max, 0) =", c.reduce_across_dimension(max, 0))   #按 x 归约最大
        print("get_merged_array('points') =", c.get_merged_array("points").shape)   #家族顶点拼接
        print("get_points_defining_boundary =", c.get_points_defining_boundary().shape)   #轮廓采样点
        win.play(FadeIn(marks), run_time=0.5)   #红点淡入
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("size", SizeDemo),
    ("edges", EdgesDemo),
    ("coords", CoordsGetDemo),
    ("points", MeasurePointsDemo),
    ("stats", StatsDemo),
]

PAIRS = [
    ("size", ["size"]),
    ("edges", ["edges"]),
    ("coords", ["coords"]),
    ("points", ["points"]),
    ("stats", ["stats"]),
]

PAGE = "03-测量"


def concat(names, dst):
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    lst = os.path.join(HERE, "concat.txt")
    with open(lst, "w", encoding="utf-8") as fh:
        for n in names:
            fh.write("file '%s'\n" % os.path.join(OUT, n + ".mp4"))
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", lst, "-c", "copy", dst],
        check=True)
    return dst


if __name__ == "__main__":
    only = set(sys.argv[1:])
    for name, cls in SCENES:
        if only and name not in only:
            continue
        print("=" * 30, name)
        try:
            fast_record_scene(cls, out_path=os.path.join(OUT, name + ".mp4"),
                              verbose=True)
        except Exception:
            import traceback
            traceback.print_exc()

    if not only:
        for out_name, names in PAIRS:
            dst = os.path.join(ASSETS, "RTM output", "%s-%s.mp4" % (PAGE, out_name))
            concat(names, dst)
            print("concat ->", dst, os.path.getsize(dst), "bytes")
