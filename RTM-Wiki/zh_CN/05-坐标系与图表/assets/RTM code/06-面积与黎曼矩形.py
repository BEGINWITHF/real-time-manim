# -*- coding: utf-8 -*-
"""06-面积与黎曼矩形.md 两个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 06-面积与黎曼矩形.py <场景名>...
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
    Scene, Axes, Text,
    YELLOW, BLUE, BLUE_C, RED, GREEN, GREEN_B, GREEN_D, GREY_B, UP, DOWN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：get_area 曲线下方面积 ======================================
class AreaDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("06-get_area", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        ax = Axes(x_range=[-3, 3, 1], y_range=[-2, 6, 1],
                  x_length=9, y_length=5.5).add_coordinates()   #带刻度数字的坐标系
        quad = ax.plot(lambda x: 0.5 * x**2 - 0.5, color=BLUE)   #抛物线
        lab = Text("get_area(x_range=(0,2)) + bounded_graph",
                   font_size=24, color=GREY_B).to_edge(DOWN)   #参数说明标签
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   #坐标系与标签一起出场
        win.play(Create(quad), run_time=0.7)   #画出抛物线

        area = ax.get_area(quad, x_range=(0, 2),   #“get_area”：曲线下方到 x 轴的面积
                           color=(GREEN_B, GREEN_D), opacity=1)   #参数 “color”/“opacity”：单色、渐变列表与不透明度
        win.play(FadeIn(area), run_time=0.6)   #渐变绿面积淡入
        win.play(FadeOut(area), run_time=0.3)   #撤掉，腾地方演示两曲线之间

        bound = ax.plot(lambda x: 3, color=RED)   #第二条曲线 y=3
        area2 = ax.get_area(quad, x_range=(-1.5, 1.5),   #“get_area” 加 “bounded_graph”：两曲线之间的面积
                            bounded_graph=bound, color=(BLUE_C, GREEN), opacity=0.6)
        win.play(Create(bound), run_time=0.4)   #画出上边界直线
        win.play(FadeIn(area2), run_time=0.6)   #两线之间的面积淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：get_riemann_rectangles 黎曼矩形 ============================
class RiemannDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("06-get_riemann_rectangles", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        ax = Axes(x_range=[-3, 3, 1], y_range=[-2, 6, 1],
                  x_length=9, y_length=5.5).add_coordinates()   #带刻度数字的坐标系
        quad = ax.plot(lambda x: 0.5 * x**2 - 0.5, color=BLUE)   #被逼近的抛物线
        lab = Text("dx=0.25 left  ->  dx=0.5 center",
                   font_size=24, color=GREY_B).to_edge(DOWN)   #参数说明标签
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   #坐标系与标签一起出场
        win.play(Create(quad), run_time=0.7)   #画出抛物线

        rects = ax.get_riemann_rectangles(quad, x_range=[-2.5, 2.5],   #“get_riemann_rectangles”：黎曼和矩形组
                                          dx=0.25,   #参数 “dx”：矩形宽
                                          input_sample_type="left",   #参数 “input_sample_type”：左端点取样
                                          color=YELLOW)   #参数 “color”：单色填充（负面积自动反色）
        win.play(FadeIn(rects), run_time=0.6)   #左端取样矩形淡入
        win.play(FadeOut(rects), run_time=0.3)   #撤掉，换中点取样

        rects2 = ax.get_riemann_rectangles(quad, x_range=[-2.5, 2.5],
                                           dx=0.5,   #宽一点，少几个矩形
                                           input_sample_type="center",   #中点取样
                                           color=(BLUE, GREEN))   #多色列表：自动做渐变
        win.play(FadeIn(rects2), run_time=0.6)   #中点取样 + 渐变矩形淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("06-面积与黎曼矩形-area", AreaDemo),
    ("06-面积与黎曼矩形-riemann", RiemannDemo),
]

PAIRS = [
    ("06-面积与黎曼矩形-area", ["06-面积与黎曼矩形-area"]),
    ("06-面积与黎曼矩形-riemann", ["06-面积与黎曼矩形-riemann"]),
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
