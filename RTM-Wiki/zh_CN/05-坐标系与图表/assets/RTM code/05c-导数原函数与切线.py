# -*- coding: utf-8 -*-
"""05c-导数原函数与切线.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 05c-导数原函数与切线.py <场景名>...
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
    Scene, Axes, NumberPlane, Dot, Line, Text, PI,
    YELLOW, PURPLE_B, GREEN, ORANGE, GREY_B, UP, DOWN, UR, DL, DR,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：曲线上取点 i2gp / i2gc ====================================
class TakePointDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("05c-input_to_graph", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        ax = NumberPlane(x_range=[-2, 5, 1], y_range=[-1, 7, 1],   #带网格的坐标系
                         background_line_style={"stroke_opacity": 0.4})   #网格线压暗免得抢戏
        curve = ax.plot(lambda x: x**2, color=PURPLE_B)   #抛物线 y=x²
        lab = Text("i2gp(x) -> screen point   i2gc(x) -> data coords",
                   font_size=24, color=GREY_B).to_edge(DOWN)   #方法说明标签
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   #坐标系与标签一起出场
        win.play(Create(curve), run_time=0.8)   #画出抛物线

        pos = ax.input_to_graph_point(x=PI, graph=curve)   #“input_to_graph_point”（别名 i2gp）：x 处的屏幕点
        dot = Dot(pos, color=YELLOW)   #拿到屏幕点后直接放 Dot
        tag = Text("i2gp(PI)", font_size=24, color=YELLOW).next_to(dot, UR, buff=0.2)
        win.play(FadeIn(dot), FadeIn(tag), run_time=0.4)   #黄点与标签淡入

        coords = ax.input_to_graph_coords(x=2.0, graph=curve)   #“input_to_graph_coords”（别名 i2gc）：x 处的数据坐标
        tag2 = Text("i2gc(2.0)=(%.1f, %.1f)" % coords,   #把回读到的数据坐标显示出来
                    font_size=24, color=GREEN).next_to(ax.c2p(2, 4), DR, buff=0.3)
        win.play(FadeIn(tag2), run_time=0.4)   #数据坐标回读淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：导函数与原函数曲线 ========================================
class DerivativeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("05c-derivative_antiderivative", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        ax = Axes(x_range=[-1, 2.5, 1], y_range=[-2, 7, 1],
                  x_length=9, y_length=5.5)   #取景包住三条曲线
        c1 = ax.plot(lambda x: x**2, color=PURPLE_B)   #原曲线 y=x²
        lab = Text("f=x^2   f'=2x   F=x^3/3 (y_intercept=0)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   #方法说明标签
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   #坐标系与标签一起出场
        win.play(Create(c1), run_time=0.7)   #画出原曲线

        c2 = ax.plot_derivative_graph(c1, color=GREEN)   #“plot_derivative_graph”：数值求导，画出 2x
        win.play(Create(c2), run_time=0.7)   #画出导函数（过原点的直线）

        c3 = ax.plot_antiderivative_graph(c1, y_intercept=0,   #“plot_antiderivative_graph”：梯形法从 0 积到 x
                                           color=ORANGE)   #参数 “y_intercept”：积分常数（y 轴截距）
        win.play(Create(c3), run_time=0.9)   #画出原函数 x³/3
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：slope_of_tangent / angle_of_tangent 动态切线 ==============
class TangentDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("05c-slope_of_tangent", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        ax = Axes(x_range=[-3, 3, 1], y_range=[-1, 7, 1],
                  x_length=9, y_length=5.5)   #缓坡抛物线取景
        f = lambda x: 0.25 * x**2 + 1   #缓一点的抛物线，切线不至于太陡
        curve = ax.plot(f, color=PURPLE_B)   #原曲线
        lab = Text("slope_of_tangent(x) + angle_of_tangent(x)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   #方法说明标签
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   #坐标系与标签一起出场
        win.play(Create(curve), run_time=0.8)   #画出曲线

        for x0, side in ((-2, DL), (0, UP), (2, DR)):   #在三个位置画切线
            s = ax.slope_of_tangent(x=x0, graph=curve)   #“slope_of_tangent”：数值求切线斜率
            ang = ax.angle_of_tangent(x=x0, graph=curve)   #“angle_of_tangent”：切线与 x 轴夹角（弧度）
            p = ax.c2p(x0, f(x0))   #切点
            half = 1.6   #切线半长（数据单位）
            pa = ax.c2p(x0 - half, f(x0) + s * (-half))   #按斜率外推两端点
            pb = ax.c2p(x0 + half, f(x0) + s * half)
            tline = Line(pa, pb, color=GREEN)   #切线段
            tag = Text("x=%+d  slope=%.1f  ang=%.2frad" % (x0, s, ang),   #斜率与夹角一起显示
                       font_size=20, color=GREY_B).next_to(p, side, buff=0.25)
            win.play(Create(tline), FadeIn(tag), run_time=0.5)   #切线与读数出场
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("05c-导数原函数与切线-takepoint", TakePointDemo),
    ("05c-导数原函数与切线-deriv", DerivativeDemo),
    ("05c-导数原函数与切线-tangent", TangentDemo),
]

PAIRS = [
    ("05c-导数原函数与切线-takepoint", ["05c-导数原函数与切线-takepoint"]),
    ("05c-导数原函数与切线-deriv", ["05c-导数原函数与切线-deriv"]),
    ("05c-导数原函数与切线-tangent", ["05c-导数原函数与切线-tangent"]),
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
