# -*- coding: utf-8 -*-
"""05-函数曲线.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 05-函数曲线.py <场景名>...
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
    Scene, Axes, NumberPlane, FunctionGraph, Text, np,
    YELLOW, RED, GREEN, BLUE, ORANGE, GREY_B, UP, DOWN, TAU,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：plot 与间断点 ==============================================
class PlotDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("05-plot", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        ax = NumberPlane(x_range=[-3, 3, 1], y_range=[-4, 4, 1])   #带网格的坐标系
        f = lambda x: max(-60, min(60, (x**2 - 2) / (x**2 - 4)))   #在 -2、2 处有垂直渐近线；y 先钳到 ±60：极点附近浮点会算出 1e14 巨值，画不出来
        lab = Text("plot(discontinuities=[-2,2], dt=0.1)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   #参数说明标签
        win.play(Create(ax), run_time=0.7)   #画出坐标网格
        win.play(FadeIn(lab), run_time=0.3)   #说明标签淡入

        bad = ax.plot(f, color=RED)   #不标间断点：-2、2 处会被一条竖线“连起来”
        win.play(Create(bad), run_time=1.0)   #先看错误画法
        win.play(FadeOut(bad), run_time=0.4)   #撤掉错误画法

        good = ax.plot(f, discontinuities=[-2, 2], dt=0.1,   #参数 “discontinuities”/“dt”：声明间断点与容差
                       color=GREEN, use_smoothing=False)   #参数 “use_smoothing”：陡峭段关平滑更真实
        win.play(Create(good), run_time=1.2)   #再看正确画法
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：FunctionGraph 脱离坐标系 ===================================
class FunctionGraphDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("05-FunctionGraph", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        g1 = FunctionGraph(lambda t: np.cos(3 * t), x_range=[-4, 4], color=BLUE)   #余弦曲线
        g2 = FunctionGraph(lambda t: np.sin(3 * t), x_range=[-4, 4], color=GREEN)   #正弦曲线
        lab = Text("FunctionGraph(cos 3t) vs FunctionGraph(sin 3t)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   #方法说明标签
        win.play(Create(g1), run_time=0.9)   #画出余弦曲线
        win.play(Create(g2), run_time=0.9)   #画出正弦曲线（相差半格相位）
        win.play(FadeIn(lab), run_time=0.4)   #说明标签淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：plot_parametric_curve 参数曲线 =============================
class ParametricCurveDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("05-parametric_curve", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        ax = Axes(x_range=[-2, 2, 1], y_range=[-2, 2, 1],
                  x_length=6, y_length=6)   #正方形取景，李萨如不变形
        curve = ax.plot_parametric_curve(   #“plot_parametric_curve”：按参数方程画曲线
            lambda t: np.array([np.sin(3 * t), np.sin(4 * t), 0]),   #x=sin(3t)、y=sin(4t)
            t_range=[0, TAU], color=ORANGE)   #参数 “t_range” 经 **kwargs 传入
        lab = Text("plot_parametric_curve(sin(3t), sin(4t))",
                   font_size=24, color=GREY_B).to_edge(DOWN)   #参数说明标签
        win.play(Create(ax), run_time=0.6)   #画出坐标系
        win.play(Create(curve), run_time=1.4)   #画出李萨如曲线
        win.play(FadeIn(lab), run_time=0.4)   #说明标签淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("05-函数曲线-plot", PlotDemo),
    ("05-函数曲线-functiongraph", FunctionGraphDemo),
    ("05-函数曲线-parametric", ParametricCurveDemo),
]

PAIRS = [
    ("05-函数曲线-plot", ["05-函数曲线-plot"]),
    ("05-函数曲线-functiongraph", ["05-函数曲线-functiongraph"]),
    ("05-函数曲线-parametric", ["05-函数曲线-parametric"]),
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
