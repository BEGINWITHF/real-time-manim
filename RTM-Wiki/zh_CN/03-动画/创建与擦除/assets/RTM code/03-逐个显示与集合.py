# -*- coding: utf-8 -*-
"""03-逐个显示与集合.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 03-逐个显示与集合.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的三条样例视频（输出到上一级 assets/）。
"""
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    Scene, Text, VGroup, Circle, Square, Triangle,
    BLUE, GREEN, GREY_B, ORANGE, RED, YELLOW,
    UP, DOWN, RIGHT,
    FadeIn, ShowIncreasingSubsets, ShowSubmobjectsOneByOne, SpiralIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：ShowIncreasingSubsets 一个接一个蹦出 ==========================
class IncreasingSubsetsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("03-ShowIncreasingSubsets", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("ShowIncreasingSubsets(group, suspend_mobject_updating=False,",
                  font_size=30, color=GREY_B)
        l2 = Text("    int_func=np.floor, reverse_rate_function=False)",
                  font_size=30, color=GREY_B)
        lab1 = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #两行签名标签
        g1 = VGroup(Circle(radius=0.35, color=BLUE),
                    Square(side_length=0.9, color=GREEN),
                    Triangle(color=ORANGE).scale(0.6),
                    Circle(radius=0.35, color=RED),
                    ).arrange(RIGHT, buff=0.7).next_to(lab1, DOWN, buff=0.6)   #被逐个显示的四个形状
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)   #标签从下方淡入
        self.add(g1)   #构造时就把子对象 set_opacity(0)，先加入场景
        win.play(
            ShowIncreasingSubsets(                  #参数 “group”
                g1,
                suspend_mobject_updating=False,     #参数 “suspend_mobject_updating”
                int_func=np.floor,                  #参数 “int_func”：已显示个数取整
                reverse_rate_function=False,        #参数 “reverse_rate_function”
                run_time=2.0,                       #参数 “run_time”
            ),
            run_time=2.0,
        )
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：ShowSubmobjectsOneByOne 同一时刻只亮一个 ======================
class OneByOneDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("03-ShowSubmobjectsOneByOne", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l3 = Text("ShowSubmobjectsOneByOne(group, int_func=np.ceil, run_time=2.0)",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   #签名标签
        g2 = VGroup(Circle(radius=0.35, color=YELLOW),
                    Square(side_length=0.9, color=RED),
                    Triangle(color=BLUE).scale(0.6),
                    Circle(radius=0.35, color=GREEN),
                    ).arrange(RIGHT, buff=0.7).next_to(l3, DOWN, buff=0.6)   #轮流闪现的四个形状
        win.play(FadeIn(l3, shift=DOWN), run_time=0.4)   #标签从下方淡入
        self.add(g2)   #构造时就置 0，先加入场景
        win.play(
            ShowSubmobjectsOneByOne(                #参数 “group”
                g2,
                int_func=np.ceil,                   #参数 “int_func”：取整函数
                run_time=2.0,                       #参数 “run_time”
            ),
            run_time=2.0,
        )
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：SpiralIn 沿螺旋轨迹飞入 ======================================
class SpiralInDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("03-SpiralIn", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l5 = Text("SpiralIn(shapes, scale_factor=6, fade_in_fraction=0.3,",
                  font_size=30, color=GREY_B)
        l6 = Text("        run_time=1.8)",
                  font_size=30, color=GREY_B)
        lab3 = VGroup(l5, l6).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #两行签名标签
        g3 = VGroup(Circle(radius=0.4, color=GREEN),
                    Square(side_length=1.0, color=BLUE),
                    Triangle(color=RED).scale(0.7),
                    Circle(radius=0.4, color=ORANGE),
                    ).arrange(RIGHT, buff=0.7).next_to(lab3, DOWN, buff=0.6)   #沿螺旋飞入的四个形状
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)   #标签从下方淡入
        #不提前 add：SpiralIn 构造时把子对象搬到螺旋起点，以 introducer 身份进场景
        win.play(
            SpiralIn(g3,                            #参数 “shapes”
                     scale_factor=6,                #参数 “scale_factor”：非默认 8
                     fade_in_fraction=0.3,          #参数 “fade_in_fraction”
                     run_time=1.8),                 #参数 “run_time”
            run_time=1.8,
        )
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("increasing_subsets", IncreasingSubsetsDemo),
    ("one_by_one", OneByOneDemo),
    ("spiral_in", SpiralInDemo),
]

PAIRS = [
    ("increasing_subsets", ["increasing_subsets"]),
    ("one_by_one", ["one_by_one"]),
    ("spiral_in", ["spiral_in"]),
]

PAGE = "03-逐个显示与集合"


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
