# -*- coding: utf-8 -*-
"""01-旋转.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 01-旋转.py <片段名>...
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    Scene, Text, VGroup, Square, Arrow, Dot, Triangle,
    BLUE, GOLD, GREY_B, TEAL, ORANGE, YELLOW,
    UP, DOWN, RIGHT, ORIGIN, PI, IN, DEGREES,
    FadeIn, Write, linear, rush_into, smooth,
)
from real_time_manim.vulkan_bind import MLWindow, Rotate, Rotating, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：Rotate 绕定点转 120° =========================================
class RotateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-Rotate", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("Rotate(sq, angle=2*PI/3, about_point=PIVOT,", font_size=30, color=GREY_B)
        l2 = Text("         run_time=1.6, rate_func=smooth)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #签名标签
        pivot = Dot(point=ORIGIN + DOWN * 1.4, radius=0.09, color=ORANGE)   #旋转中心点
        sq = Square(side_length=1.3, color=BLUE).set_fill(BLUE, 0.5).move_to(pivot.get_center() + RIGHT * 2.6)   #蓝色方块
        win.play(FadeIn(sig, shift=DOWN), FadeIn(VGroup(pivot, sq)), run_time=0.4)   #标签与图形淡入
        win.play(Rotate(sq, angle=2 * PI / 3, about_point=pivot.get_center(),   #参数 “angle / about_point”
                        run_time=1.6, rate_func=smooth))                        #参数 “run_time / rate_func”
        win.play(Wait(0.6))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：Rotating 反向转半圈 ==========================================
class RotatingAxisDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-RotatingAxis", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("Rotating(arrow, angle=180*DEGREES, axis=IN,", font_size=30, color=GREY_B)
        l2 = Text("          run_time=1.4, rate_func=linear)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #签名标签
        arrow = Arrow(ORIGIN, RIGHT * 2.0, buff=0, color=GOLD).shift(DOWN * 1.6)   #金色箭头
        win.play(FadeIn(sig, shift=DOWN), FadeIn(arrow), run_time=0.4)   #标签与箭头淡入
        win.play(Rotating(arrow, angle=180 * DEGREES, axis=IN,   #参数 “angle / axis=IN”（2D 画面反向转）
                          run_time=1.4, rate_func=linear))       #参数 “run_time / rate_func”
        win.play(Wait(0.6))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：Rotating 绕上边缘铰链翻转 ====================================
class RotatingEdgeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-RotatingEdge", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("Rotating(tri, angle=90*DEGREES, about_edge=UP,", font_size=30, color=GREY_B)
        l2 = Text("           run_time=1.6, rate_func=rush_into)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #签名标签
        tri = Triangle(color=TEAL).scale(1.1).set_fill(TEAL, 0.5).shift(DOWN * 2.0)   #青色三角
        win.play(FadeIn(sig, shift=DOWN), FadeIn(tri), run_time=0.4)   #标签与三角淡入
        win.play(Rotating(tri, angle=90 * DEGREES, about_edge=UP,   #参数 “about_edge=UP”（上边缘当铰链）
                          run_time=1.6, rate_func=rush_into))       #参数 “run_time / rate_func”
        win.play(Wait(0.6))   #停留看结果
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("rotate", RotateDemo),
    ("rotating_axis", RotatingAxisDemo),
    ("rotating_edge", RotatingEdgeDemo),
]

PAIRS = [
    ("rotate", ["rotate"]),
    ("rotating_axis", ["rotating_axis"]),
    ("rotating_edge", ["rotating_edge"]),
]

PAGE = "01-旋转"


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
