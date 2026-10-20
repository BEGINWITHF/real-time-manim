# -*- coding: utf-8 -*-
"""07-极坐标与三维坐标系.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 07-极坐标与三维坐标系.py <场景名>...
不带参数就渲染全部场景，并拼出页面里的三条视频。
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
ASSETS = os.path.dirname(HERE)
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    Scene, ThreeDScene, ThreeDAxes, PolarPlane, Dot, Text, np,
    YELLOW, TEAL, BLUE, ORANGE, RED, GREEN, GREY_B, UP, DOWN, UR, TAU,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：PolarPlane 极坐标平面 ======================================
class PolarDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("07-PolarPlane", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        plane = PolarPlane(size=5,   #参数 “size”：平面直径
                           azimuth_units="PI radians",   #参数 “azimuth_units”：方位角按 π 分数标注
                           background_line_style={"stroke_color": TEAL, "stroke_width": 2},   #同心圆与放射线样式
                           ).add_coordinates()   #“add_coordinates”：半径数字 + 角度标签
        rose = plane.plot_polar_graph(lambda th: 2 * np.sin(th * 5),   #“plot_polar_graph”：按 r=f(θ) 画极坐标曲线
                                      theta_range=[0, TAU], color=ORANGE)   #五瓣玫瑰线
        lab = Text("plot_polar_graph(2*sin(5*theta))",
                   font_size=18, color=GREY_B).to_edge(DOWN, buff=0.3)   #参数说明标签
        win.play(Create(plane), FadeIn(lab), run_time=1.0)   #极坐标平面（含标签）与说明一起出场
        win.play(Create(rose), run_time=1.2)   #画出玫瑰线
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：ThreeDAxes 三维坐标系 ======================================
class ThreeDAxesDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 内部会调 self.play，必须先接上
        title = Text("07-ThreeDAxes", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        ax = ThreeDAxes(x_range=(-3, 3, 1), y_range=(-3, 3, 1), z_range=(-4, 4, 1),   #三轴数据范围
                        x_length=7, y_length=7, z_length=5)   #各轴屏幕长度
        ax.add_coordinates(range(-2, 3), None, range(-4, 5, 2))   #“add_coordinates”：x/z 轴给定刻度，y 轴默认
        d1 = Dot(ax.c2p(1, 1, 2), color=RED)   #“c2p”：三维数据坐标 -> 场景点
        d2 = Dot(ax.c2p(-2, 2, -3), color=GREEN)
        lab = Text("ThreeDAxes + c2p(1,1,2) / c2p(-2,2,-3)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   #方法说明标签
        win.play(Create(ax), FadeIn(lab), run_time=0.8)   #三维坐标系与说明一起出场
        win.play(FadeIn(d1), FadeIn(d2), run_time=0.4)   #两个空间点淡入
        self.move_camera(theta=-0.6, phi=1.1, run_time=1.0)   #“move_camera”：转到 3D 视角看深度
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：Axes.plot_surface 曲面 ======================================
class SurfaceDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 内部会调 self.play，必须先接上
        title = Text("07-plot_surface", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        ax = ThreeDAxes(x_range=(-3, 3, 1), y_range=(-3, 3, 1), z_range=(-2, 2, 1))   #三轴数据范围
        surf = ax.plot_surface(lambda u, v: np.sin(u) * np.cos(v),   #“plot_surface”：参数方程曲面
                               u_range=(-3, 3), v_range=(-3, 3), resolution=(12, 12))   #u/v 范围与网格分辨率
        lab = Text("plot_surface(sin(u)*cos(v))",
                   font_size=24, color=GREY_B).to_edge(DOWN)   #方法说明标签
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   #坐标系与说明一起出场
        win.play(FadeIn(surf), run_time=0.6)   #曲面淡入
        self.move_camera(theta=-0.6, phi=1.1, run_time=1.0)   #转到 3D 视角看曲面起伏
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("07-极坐标与三维坐标系-polar", PolarDemo),
    ("07-极坐标与三维坐标系-threed", ThreeDAxesDemo),
    ("07-极坐标与三维坐标系-surface", SurfaceDemo),
]

PAIRS = [
    ("07-极坐标与三维坐标系-polar", ["07-极坐标与三维坐标系-polar"]),
    ("07-极坐标与三维坐标系-threed", ["07-极坐标与三维坐标系-threed"]),
    ("07-极坐标与三维坐标系-surface", ["07-极坐标与三维坐标系-surface"]),
]


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
            dst = os.path.join(ASSETS, "RTM output", out_name + ".mp4")
            concat(names, dst)
            print("concat ->", dst, os.path.getsize(dst), "bytes")
