# -*- coding: utf-8 -*-
"""05b-曲线标注与辅助线.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 05b-曲线标注与辅助线.py <场景名>...
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
    Scene, Axes, Text,
    YELLOW, TEAL, PURPLE_B, GREEN, GREY, GREY_B, UP, DOWN, DL,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：plot_implicit_curve 隐式曲线 ===============================
class ImplicitDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("05b-plot_implicit_curve", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        ax = Axes(x_range=[-3, 3, 1], y_range=[-2, 2, 1],
                  x_length=8, y_length=5)   #范围与半径 2 匹配
        circle = ax.plot_implicit_curve(lambda x, y: x**2 + y**2 - 4,   #“plot_implicit_curve”：f(x,y)=0 的等值线
                                        color=TEAL)   #x²+y²=4 即半径 2 的圆
        lab = Text("plot_implicit_curve(x^2+y^2-4=0)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   #参数说明标签
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   #坐标系与标签一起出场
        win.play(Create(circle), run_time=1.2)   #画出隐式圆
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：get_graph_label + get_T_label 曲线标注 =====================
class LabelsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("05b-graph_label_T_label", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        ax = Axes(x_range=[-4, 4, 1], y_range=[-1, 7, 1],
                  x_length=9, y_length=5.5)   #抛物线取景
        curve = ax.plot(lambda x: x**2, color=PURPLE_B)   #抛物线 y=x²
        lab = Text("get_graph_label(x_val=-2) + get_T_label(x_val=4)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   #参数说明标签
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   #坐标系与标签一起出场
        win.play(Create(curve), run_time=0.8)   #画出抛物线

        label = ax.get_graph_label(curve, "x^2", x_val=-2,   #“get_graph_label”：在曲线 x=-2 处放标签
                                   direction=DL, dot=True)   #参数 “dot”：同时在曲线上加圆点
        win.play(FadeIn(label), run_time=0.5)   #标签与圆点淡入

        t_label = ax.get_T_label(x_val=4, graph=curve,   #“get_T_label”：x=4 处的标记组合
                                 label="x-value")   #三角形 + 竖直线 + 文字标签
        win.play(FadeIn(t_label), run_time=0.5)   #T 标记组淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：get_vertical_lines_to_graph + 割线组 =======================
class SecantDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("05b-secant_slope_group", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        ax = Axes(x_range=[-1, 5, 1], y_range=[-1, 7, 1],
                  x_length=9, y_length=5.5)   #抛物线取景
        curve = ax.plot(lambda x: x**2, color=PURPLE_B)   #抛物线 y=x²
        lab = Text("get_vertical_lines_to_graph(9) + secant(dx=1)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   #参数说明标签
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   #坐标系与标签一起出场
        win.play(Create(curve), run_time=0.8)   #画出抛物线

        vlines = ax.get_vertical_lines_to_graph(curve, x_range=[0, 4],   #“get_vertical_lines_to_graph”：曲线上均匀拉竖直虚线
                                                num_lines=9, color=GREY)   #参数 “num_lines”：虚线条数
        win.play(Create(vlines), run_time=0.6)   #画出竖直虚线组
        win.play(FadeOut(vlines), run_time=0.3)   #撤掉虚线组，给割线组腾地方

        group = ax.get_secant_slope_group(x=2.0, graph=curve, dx=1.0,   #“get_secant_slope_group”：Δx 横线 + Δy 竖线 + 割线一组
                                          dx_label="dx", dy_label="dy",   #参数 “dx_label”/“dy_label”：线旁标签
                                          secant_line_color=GREEN, secant_line_length=4)   #参数 “secant_line_color”/“secant_line_length”：割线样式
        win.play(FadeIn(group), run_time=0.8)   #割线组淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("05b-曲线标注与辅助线-implicit", ImplicitDemo),
    ("05b-曲线标注与辅助线-labels", LabelsDemo),
    ("05b-曲线标注与辅助线-secant", SecantDemo),
]

PAIRS = [
    ("05b-曲线标注与辅助线-implicit", ["05b-曲线标注与辅助线-implicit"]),
    ("05b-曲线标注与辅助线-labels", ["05b-曲线标注与辅助线-labels"]),
    ("05b-曲线标注与辅助线-secant", ["05b-曲线标注与辅助线-secant"]),
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
