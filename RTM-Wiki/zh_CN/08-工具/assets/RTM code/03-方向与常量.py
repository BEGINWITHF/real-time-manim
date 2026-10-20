# -*- coding: utf-8 -*-
"""03-方向与常量.md 两个样例的完整源码（与页面里的代码块逐字一致）。
跑法：python 03-方向与常量.py <片段名>...
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
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    Scene, Text, VGroup, Dot, Arrow, Circle, Arc,
    BLUE, GREEN, RED, ORANGE, PURPLE, YELLOW, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, UL, UR, DL, DR,
    PI, TAU, DEGREES, compass_directions,
    FadeIn, Write, Create,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：方向常量罗盘 =================================================
class DirectionDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("03-direction constants", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        origin = Dot(ORIGIN, radius=0.07, color=WHITE)   #原点 ORIGIN
        win.play(FadeIn(origin), run_time=0.3)   #先把原点亮出来
        lab0 = Text("ORIGIN", font_size=16, color=WHITE).next_to(origin, DOWN, buff=0.2)
        win.play(FadeIn(lab0), run_time=0.25)   #原点标签

        mains = [("RIGHT", RIGHT, BLUE), ("UP", UP, GREEN),   #四个基本方向
                 ("LEFT", LEFT, RED), ("DOWN", DOWN, ORANGE)]
        for nm, d, c in mains:   #按右 → 上 → 左 → 下 依次画箭头
            ar = Arrow(ORIGIN, 2.0 * d, buff=0, color=c, stroke_width=6)   #一单位长的方向箭头
            lb = Text(nm, font_size=20, color=c).next_to(ar.get_end(), d, buff=0.2)   #箭头外侧写常量名
            win.play(Create(ar), run_time=0.45)   #画箭头
            win.play(FadeIn(lb), run_time=0.2)   #补上名字

        diags = [("UR", UR), ("UL", UL), ("DL", DL), ("DR", DR)]   #四个对角方向
        dgrp = VGroup()
        for nm, d in diags:   #对角 = 两个基本方向相加，一次全出
            ar = Arrow(ORIGIN, 1.7 * d, buff=0, color=PURPLE, stroke_width=5)
            lb = Text(nm, font_size=18, color=PURPLE).next_to(ar.get_end(), d, buff=0.18)
            dgrp.add(ar, lb)
        win.play(FadeIn(dgrp), run_time=0.5)   #对角箭头整组淡入
        note = Text("UR = UP + RIGHT   |   IN / OUT = Z axis", font_size=18,
                    color=GREY_B).to_edge(DOWN)   #对角的构造方式与 Z 轴说明
        win.play(FadeIn(note), run_time=0.35)   #说明淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：compass_directions 与数学常量 ================================
class CompassMathDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("03-compass_directions", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 左半：compass_directions 把 start_vect 连转 n 次 ——
        c = [-3.6, -0.4, 0]   #左图圆心
        ring = Circle(radius=1.6, color=GREY_B, stroke_width=3).move_to(c)   #辅助圆
        pts = compass_directions(8, start_vect=RIGHT)   #从正右方起、每次转 TAU/8，得 8 个方向
        dots = VGroup(*[Dot(1.6 * p + c, radius=0.07,
                            color=BLUE if i == 0 else YELLOW) for i, p in enumerate(pts)])   #第 0 个就是 start_vect
        lab_l = Text("compass_directions(8, start_vect=RIGHT)", font_size=15, color=GREY_B)
        lab_l.move_to([-3.6, 1.7, 0])   #左图标题
        lab_r = Text("dot[0] = start_vect", font_size=15, color=BLUE)
        lab_r.next_to(ring, DOWN, buff=0.35)   #蓝点就是起点方向
        win.play(Create(ring), FadeIn(lab_l), run_time=0.5)   #辅助圆与标题
        win.play(FadeIn(dots), FadeIn(lab_r), run_time=0.5)   #8 个均匀方向点
        # —— 右半：TAU / PI / DEGREES 三个数学常量 ——
        cc = [3.0, 0.2, 0]   #右图圆心
        full = Arc(radius=1.5, start_angle=0, angle=TAU, arc_center=cc,
                   color=BLUE, stroke_width=4)   #一整圈 = TAU
        half = Arc(radius=1.5, start_angle=0, angle=PI, arc_center=cc,
                   color=GREEN, stroke_width=7)   #半圈 = PI
        wedge = Arc(radius=1.5, start_angle=0, angle=45 * DEGREES, arc_center=cc,
                    color=RED, stroke_width=12)   #45° = 45 * DEGREES
        vals = VGroup(
            Text("TAU = 6.28319", font_size=17, color=BLUE),
            Text("PI = 3.14159", font_size=17, color=GREEN),
            Text("45 * DEGREES = 0.78540", font_size=17, color=RED),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)   #三行数值与三段弧同色
        vals.move_to([3.0, -2.4, 0])   #放在右图下方
        win.play(Create(full), run_time=0.7)   #先画一整圈
        win.play(Create(half), run_time=0.45)   #再叠上半圈
        win.play(Create(wedge), run_time=0.3)   #最后是 45° 短弧
        win.play(FadeIn(vals), run_time=0.45)   #三行数值淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("directions", DirectionDemo),
    ("compass_math", CompassMathDemo),
]

PAIRS = [
    ("directions", ["directions"]),
    ("compass_math", ["compass_math"]),
]

PAGE = "03-方向与常量"


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
