# -*- coding: utf-8 -*-
"""02-沿路径与同态变换.md 两个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 02-沿路径与同态变换.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的两条样例视频（输出到上一级 assets/）。
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

import numpy as np

from real_time_manim import (
    Scene, Text, VGroup, Circle, Dot, Rectangle,
    GREY_B, ORANGE, YELLOW, UP, DOWN,
    Create, FadeIn, Write, linear,
)
from real_time_manim.vulkan_bind import MLWindow, MoveAlongPath, Homotopy, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：MoveAlongPath 沿可见轨迹走一圈 ===============================
class MoveAlongPathDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02-MoveAlongPath", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        sig = Text("MoveAlongPath(dot, path, run_time=2.0, rate_func=linear)",
                   font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   #签名标签
        path = Circle(radius=1.9, color=GREY_B).shift(DOWN * 0.9)   #灰色圆形路径
        dot = Dot(radius=0.14, color=ORANGE).move_to(path.point_from_proportion(0.0))   #起点上的橙点
        win.play(FadeIn(sig, shift=DOWN), FadeIn(dot), run_time=0.4)   #标签与点淡入
        win.play(Create(path, run_time=0.8, rate_func=linear))   #把路径画出来（轨迹可见）
        win.play(MoveAlongPath(dot, path, run_time=2.0, rate_func=linear))   #参数 “path / run_time / rate_func”
        win.play(Wait(0.6))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：Homotopy 逐点重映射变波浪 ====================================
class HomotopyDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02-Homotopy", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        sig = Text("Homotopy(wave, rect, run_time=2.0, rate_func=linear)",
                   font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   #签名标签
        rect = Rectangle(width=4.4, height=1.6, color=YELLOW).set_fill(YELLOW, 0.35).shift(DOWN * 1.2)   #黄色矩形
        win.play(FadeIn(sig, shift=DOWN), FadeIn(rect), run_time=0.4)   #标签与矩形淡入

        def wave(x, y, z, t):   #参数 “homotopy”：(x, y, z, t) -> (x', y', z')
            return (x, y + 0.45 * np.sin(2.2 * x + 2.0 * np.pi * t), z)

        win.play(Homotopy(wave, rect, run_time=2.0, rate_func=linear))   #参数 “homotopy / run_time / rate_func”
        win.play(Wait(0.6))   #停留看结果
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("movealongpath", MoveAlongPathDemo),
    ("homotopy", HomotopyDemo),
]

PAIRS = [
    ("movealongpath", ["movealongpath"]),
    ("homotopy", ["homotopy"]),
]

PAGE = "02-沿路径与同态变换"


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
