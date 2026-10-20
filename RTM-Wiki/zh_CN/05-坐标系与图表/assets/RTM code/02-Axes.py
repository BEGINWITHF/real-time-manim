# -*- coding: utf-8 -*-
"""02-Axes.md 两个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 02-Axes.py <场景名>...
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
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    Scene, Axes, Text,
    YELLOW, BLUE, GREY_B, UP, DOWN,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：Axes 构造参数 ==============================================
class AxesCtorDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02-Axes", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        ax = Axes(x_range=[-4, 4, 1], y_range=[-3, 3, 1],   #参数 “x_range”/“y_range”：数据范围与刻度步长
                  x_length=8, y_length=5,                   #参数 “x_length”/“y_length”：屏幕物理长度
                  tips=False, axis_config={"font_size": 24})   #参数 “tips”：轴端箭头；“axis_config”：两轴公共参数
        ax.add_coordinates()   #两轴挂刻度数字
        labels = ax.get_axis_labels("x", "y")   #x/y 两个轴名称（需自己加入场景）
        curve = ax.plot(lambda x: 0.5 * x**2, color=BLUE)   #顺手画一条抛物线（参数见 05 页）
        lab = Text("x_range=[-4,4,1]  y_range=[-3,3,1]  tips=False",
                   font_size=24, color=GREY_B).to_edge(DOWN)   #参数说明标签
        win.play(Create(ax), run_time=1.0)   #画出坐标系（含刻度数字）
        win.play(FadeIn(labels), FadeIn(lab), run_time=0.4)   #轴名称与说明标签淡入
        win.play(Create(curve), run_time=1.0)   #画出抛物线
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：add_coordinates 的 list / dict 写法 ========================
class AxesAddCoordDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02-add_coordinates", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        ax = Axes(x_range=[-3, 3, 1], y_range=[-2, 2, 1], x_length=9, y_length=5)   #默认 tips=True（轴端带箭头）
        ax.add_coordinates({1: "Mon", 2: "Tue"}, [-2, 0, 2])   #“add_coordinates”：x 轴 dict 数值->标签，y 轴 list 只显指定数值
        labels = ax.get_axis_labels("x", "y")   #轴名称
        lab = Text("add_coordinates({1:Mon,2:Tue}, [-2,0,2])",
                   font_size=24, color=GREY_B).to_edge(DOWN)   #参数说明标签
        win.play(Create(ax), run_time=0.9)   #画出坐标系（含箭头与自定义标签）
        win.play(FadeIn(labels), FadeIn(lab), run_time=0.4)   #轴名称与说明标签淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("02-Axes-ctor", AxesCtorDemo),
    ("02-Axes-addcoordinates", AxesAddCoordDemo),
]

PAIRS = [
    ("02-Axes-ctor", ["02-Axes-ctor"]),
    ("02-Axes-addcoordinates", ["02-Axes-addcoordinates"]),
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
