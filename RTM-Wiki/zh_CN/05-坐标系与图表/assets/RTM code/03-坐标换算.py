# -*- coding: utf-8 -*-
"""03-坐标换算.md 一个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 03-坐标换算.py
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
    Scene, Axes, Dot, Text, VGroup, np,
    YELLOW, GREEN, BLUE, GREY_B, UP, DOWN, UR, DL,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例：c2p / p2c / @ / 批量换算 =====================================
class C2PDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("03-c2p-p2c", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        ax = Axes(x_range=[-4, 4, 1], y_range=[-3, 3, 1],
                  x_length=8, y_length=5, tips=False)   #无箭头坐标系
        ax.add_coordinates()   #刻度数字
        labels = ax.get_axis_labels("x", "y")   #轴名称
        lab = Text("p = ax.c2p(2, 1.5)   coords = ax.p2c(p)",
                   font_size=26, color=GREY_B).to_edge(DOWN)   #方法说明标签
        win.play(Create(ax), FadeIn(labels), FadeIn(lab), run_time=0.8)   #坐标系与标签一起出场

        p = ax.c2p(2, 1.5)   #“c2p”：数据坐标 -> 屏幕坐标，摆放元素的唯一正确途径
        dot = Dot(p, color=GREEN)   #放在 c2p 结果上的绿点
        coords = ax.p2c(p)   #“p2c”：屏幕坐标 -> 数据坐标（c2p 的逆运算）
        readout = Text("p2c=(%.1f, %.1f)" % (coords[0], coords[1]),   #把回读结果显示在屏幕上
                       font_size=28, color=GREEN).next_to(dot, UR, buff=0.2)
        win.play(FadeIn(dot), FadeIn(readout), run_time=0.5)   #绿点与回读文字淡入
        win.play(Wait(0.6))   #停 0.6s 看回读结果

        q = ax @ (1, -2)   #“@” 写法：等价于 ax.c2p(1, -2)
        assert np.allclose(ax.p2c(q), [1, -2], atol=1e-6)   #往返换算自检：p2c(c2p(x)) == x
        dot2 = Dot(q, color=YELLOW)   #放在 @ 结果上的黄点
        tag2 = Text("ax @ (1,-2)", font_size=26, color=YELLOW).next_to(dot2, DL, buff=0.2)
        win.play(FadeIn(dot2), FadeIn(tag2), run_time=0.5)   #黄点与标签淡入

        batch = ax.c2p([-3, 0, 3], [-2, 0, 2])   #批量换算：传两个等长数组，一次算 3 个点
        dots3 = VGroup(*[Dot(pt, color=BLUE) for pt in batch])   #三个蓝点摆在对角线上
        win.play(FadeIn(dots3), run_time=0.4)   #三个蓝点淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("03-坐标换算-c2p_p2c", C2PDemo),
]

PAIRS = [
    ("03-坐标换算-c2p_p2c", ["03-坐标换算-c2p_p2c"]),
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
