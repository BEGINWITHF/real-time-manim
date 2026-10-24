# -*- coding: utf-8 -*-
"""02b-引导线与折线图.md 两个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 02b-引导线与折线图.py <场景名>...
不带参数就渲染全部场景，并拼出页面里的两条视频。
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
ASSETS = os.path.dirname(HERE)
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

from real_time_manim import (
    Scene, Axes, Dot, Line, Text, VGroup,
    YELLOW, RED, BLUE, GREEN, GREY, GREY_B, GOLD_E, UP, DOWN,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：横竖引导线三件套 ===========================================
class GuideLinesDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02b-guide-lines", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        ax = Axes(x_range=[-4, 4, 1], y_range=[-3, 3, 1],
                  x_length=9, y_length=5.5).add_coordinates()   #带刻度数字的坐标系
        p = ax.c2p(2, 1.5)   #目标点：数据坐标 (2, 1.5)
        dot = Dot(p, color=RED)   #目标点圆点
        vline = ax.get_vertical_line(p, color=BLUE)   #“get_vertical_line”：x 轴 -> 点的竖直虚线
        both = ax.get_lines_to_point(ax.c2p(-3, -1), color=GREY)   #“get_lines_to_point”：横竖两条引导线
        solid = ax.get_line_from_axis_to_point(   #“get_line_from_axis_to_point”：通用版，指定线型类
            1, ax.c2p(3, -2), line_func=Line, color=GREEN)   #从 y 轴（index=1）拉一条实线到点
        lab = Text("vertical / lines_to_point / from_axis(1, Line)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   #方法说明标签
        win.play(Create(ax), run_time=0.8)   #画出坐标系
        win.play(FadeIn(lab), run_time=0.3)   #说明标签淡入
        win.play(FadeIn(dot), run_time=0.3)   #目标点淡入
        win.play(Create(vline), run_time=0.6)   #蓝色竖直虚线从 x 轴长到点
        win.play(Create(both), run_time=0.6)   #灰色横竖两条引导线
        win.play(Create(solid), run_time=0.6)   #绿色实线从 y 轴连到点
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：plot_line_graph 离散折线图 =================================
class LineGraphDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02b-plot_line_graph", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        ax = Axes(x_range=[0, 5, 1], y_range=[0, 5, 1],
                  x_length=8, y_length=5).add_coordinates()   #第一象限坐标系
        lg = ax.plot_line_graph(x_values=[0, 1.5, 2.8, 4],   #“plot_line_graph”：按离散数据点连线（不是函数采样）
                                y_values=[1, 3, 4, 2.5],
                                line_color=GOLD_E, stroke_width=4)   #参数 “line_color”/“stroke_width”：折线颜色与线宽
        lab = Text("plot_line_graph(x=[0,1.5,2.8,4], y=[1,3,4,2.5])",
                   font_size=24, color=GREY_B).to_edge(DOWN)   #参数说明标签
        win.play(Create(ax), run_time=0.7)   #画出坐标系
        win.play(FadeIn(lab), run_time=0.3)   #说明标签淡入
        win.play(Create(lg["line_graph"]), run_time=1.0)   #折线本体（返回 VDict 的 “line_graph” 键）
        win.play(FadeIn(lg["vertex_dots"]), run_time=0.5)   #顶点圆点（“vertex_dots” 键）
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("02b-引导线与折线图-lines", GuideLinesDemo),
    ("02b-引导线与折线图-linegraph", LineGraphDemo),
]

PAIRS = [
    ("02b-引导线与折线图-lines", ["02b-引导线与折线图-lines"]),
    ("02b-引导线与折线图-linegraph", ["02b-引导线与折线图-linegraph"]),
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
