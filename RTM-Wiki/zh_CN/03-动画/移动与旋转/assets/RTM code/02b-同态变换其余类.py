# -*- coding: utf-8 -*-
"""02b-同态变换其余类.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 02b-同态变换其余类.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的三条样例视频（输出到上一级 assets/）。
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

import numpy as np

from real_time_manim import (
    Scene, Text, VGroup, Circle, Square, Dot,
    BLUE, RED, GREY_B, YELLOW, LEFT, UP, DOWN,
    ComplexHomotopy, FadeIn, PhaseFlow, SmoothedVectorizedHomotopy, Write, linear,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：SmoothedVectorizedHomotopy 平滑压扁拉伸 ======================
class SmoothedHomotopyDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02b-SmoothedVectorizedHomotopy", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("SmoothedVectorizedHomotopy(squash, c, run_time=1.8,", font_size=30, color=GREY_B)
        l2 = Text("                            rate_func=linear)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #签名标签
        c = Circle(radius=1.0, color=BLUE).set_fill(BLUE, 0.4).shift(DOWN * 1.5)   #蓝色圆
        win.play(FadeIn(sig, shift=DOWN), FadeIn(c), run_time=0.4)   #标签与圆淡入

        def squash(x, y, z, t):   #参数 “homotopy”：x 拉长、y 压扁
            return (x * (1.0 + 0.9 * t), y * (1.0 - 0.45 * t), z)

        win.play(SmoothedVectorizedHomotopy(squash, c, run_time=1.8, rate_func=linear))
        win.play(Wait(0.6))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：ComplexHomotopy 复平面旋转 90° ===============================
class ComplexHomotopyDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02b-ComplexHomotopy", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("ComplexHomotopy(lambda z, t: z*e^(i*t*PI/2), sq,", font_size=30, color=GREY_B)
        l2 = Text("                run_time=1.8)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #签名标签
        sq = Square(side_length=1.6, color=RED).set_fill(RED, 0.4).shift(DOWN * 1.5)   #红色方块
        win.play(FadeIn(sig, shift=DOWN), FadeIn(sq), run_time=0.4)   #标签与方块淡入
        win.play(ComplexHomotopy(lambda z, t: z * np.exp(1j * t * np.pi / 2), sq,   #参数 “complex_homotopy”（复平面旋转）
                                 run_time=1.8))
        win.play(Wait(0.6))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：PhaseFlow 向量场累积位移 =====================================
class PhaseFlowDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02b-PhaseFlow", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("PhaseFlow(lambda p: [-p[1]-1.3, p[0], 0], dot,", font_size=30, color=GREY_B)
        l2 = Text("          virtual_time=1.2, run_time=2.0, rate_func=linear)", font_size=28, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #签名标签
        dot = Dot(radius=0.13, color=GREY_B).shift(LEFT * 1.9 + DOWN * 1.3)   #被向量场推动的点
        center = Dot(radius=0.06, color=GREY_B).shift(DOWN * 1.3)   #向量场的旋转中心
        win.play(FadeIn(sig, shift=DOWN), FadeIn(VGroup(dot, center)), run_time=0.4)   #标签与点淡入
        win.play(PhaseFlow(lambda p: np.array([-p[1] - 1.3, p[0], 0.0]), dot,   #参数 “function”（向量场）
                           virtual_time=1.2, run_time=2.0, rate_func=linear))   #参数 “virtual_time / run_time / rate_func”
        win.play(Wait(0.6))   #停留看结果
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("smoothed", SmoothedHomotopyDemo),
    ("complex", ComplexHomotopyDemo),
    ("phaseflow", PhaseFlowDemo),
]

PAIRS = [
    ("smoothed", ["smoothed"]),
    ("complex", ["complex"]),
    ("phaseflow", ["phaseflow"]),
]

PAGE = "02b-同态变换其余类"


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
