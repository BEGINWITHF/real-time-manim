# -*- coding: utf-8 -*-
"""01-基本形状.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 01-基本形状.py <片段名>...
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

from real_time_manim import (
    Scene, Arc, ArcBetweenPoints, TangentialArc, CurvedArrow, CurvedDoubleArrow,
    Circle, Dot, Square, Text, DashedLine,
    BLUE, RED, GREEN, YELLOW, ORANGE, TEAL, GREY_B,
    UP, DOWN, LEFT, RIGHT, PI, TAU, DEGREES,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：弧家族 Arc / ArcBetweenPoints / TangentialArc ==============
class ArcDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-Arc family", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— Arc：radius / start_angle / angle / arc_center ——
        arc = Arc(radius=1.2, start_angle=0, angle=PI, color=BLUE, stroke_width=8,
                  arc_center=[-4.6, -1.0, 0])   #半径 1.2、从正右方逆时针扫过 180° 的上半圆
        cdot = Dot([-4.6, -1.0, 0], radius=0.06, color=YELLOW)   #圆心点 = arc_center
        l1 = Text("Arc(angle=PI)", font_size=24, color=GREY_B)   #弧的标签
        l1.next_to(arc, DOWN, buff=0.3)   #放在弧的正下方
        win.play(Create(arc), FadeIn(cdot), run_time=0.8)   #画弧并点出圆心
        win.play(FadeIn(l1), run_time=0.3)   #标签淡入

        # —— ArcBetweenPoints：angle 控制弯曲方向与大小 ——
        ab1 = ArcBetweenPoints([-1.7, -0.3, 0], [1.7, -0.3, 0], angle=PI / 2,
                               color=GREEN, stroke_width=8)   #正角（逆时针）：向下兜成弧谷
        ab2 = ArcBetweenPoints([-1.7, -2.1, 0], [1.7, -2.1, 0], angle=-PI / 2,
                               color=ORANGE, stroke_width=8)   #负角（顺时针）：向上拱成弧背
        lu = Text("angle=+PI/2", font_size=24, color=GREY_B).next_to(ab1, UP, buff=0.15)
        ld = Text("angle=-PI/2", font_size=24, color=GREY_B).next_to(ab2, DOWN, buff=0.15)
        win.play(Create(ab1), FadeIn(lu), run_time=0.7)   #正角弧 + 上方标签
        win.play(Create(ab2), FadeIn(ld), run_time=0.7)   #负角弧 + 下方标签

        # —— TangentialArc：两条相交直线的拐角圆弧（corner 选象限）——
        ln1 = DashedLine([3.1, -1.0, 0], [6.1, -1.0, 0], color=GREY_B)   #参与相交的水平线
        ln2 = DashedLine([4.6, -2.7, 0], [4.6, 0.7, 0], color=GREY_B)   #参与相交的竖直线
        ta = TangentialArc(ln1, ln2, radius=0.9, corner=(1, 1), color=TEAL)   #交点处的拐角弧
        lt = Text("TangentialArc(corner=(1,1))", font_size=22, color=GREY_B)
        lt.next_to(ln1, DOWN, buff=0.25)   #放在水平虚线下方，避免与辅助线重叠
        win.play(Create(ln1), Create(ln2), run_time=0.6)   #先画两条辅助线
        win.play(Create(ta), FadeIn(lt), run_time=0.7)   #再画拐角弧 + 标签
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：曲线箭头 CurvedArrow / CurvedDoubleArrow ==================
class CurvedArrowDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-CurvedArrow / CurvedDoubleArrow", font_size=32, color=YELLOW)
        title.to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        ca1 = CurvedArrow([-3.2, 1.4, 0], [3.2, 1.4, 0], color=BLUE, stroke_width=6)   #默认 angle=TAU/4：向下兜成弧谷
        l1 = Text("CurvedArrow (default angle)", font_size=24, color=GREY_B)
        l1.next_to(ca1, UP, buff=0.1)   #标签放在箭头上方
        win.play(Create(ca1), FadeIn(l1), run_time=0.8)   #画出默认弯向的曲线箭头

        ca2 = CurvedArrow([-3.2, -0.4, 0], [3.2, -0.4, 0], angle=-TAU / 4,
                          color=GREEN, stroke_width=6)   #负角：弯向反过来（向上拱成弧背）
        l2 = Text("CurvedArrow(angle=-TAU/4)", font_size=24, color=GREY_B)
        l2.next_to(ca2, DOWN, buff=0.15)   #标签放在下方（弧线中间高、两端低）
        win.play(Create(ca2), FadeIn(l2), run_time=0.8)   #画出反向弯的曲线箭头

        cda = CurvedDoubleArrow([-3.2, -2.3, 0], [3.2, -2.3, 0], color=RED, stroke_width=6)   #两端都有尖端
        l3 = Text("CurvedDoubleArrow", font_size=24, color=GREY_B)
        l3.next_to(cda, UP, buff=0.2)   #标签放在弧谷里（凹面一侧，不出画）
        win.play(Create(cda), FadeIn(l3), run_time=0.8)   #画出双头曲线箭头
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：圆与点 Circle / Dot =======================================
class CircleDotDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-Circle / Dot", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— Circle.surround()：把圆缩放到包住任意对象 ——
        sq = Square(side_length=1.3, color=GREEN, fill_opacity=0.4).shift(LEFT * 4.2)   #被包住的方块
        cir = Circle(radius=0.55, color=BLUE, stroke_width=7).shift(LEFT * 4.2 + UP * 1.7)   #初始圆不套着方块
        l1 = Text("Circle.surround()", font_size=24, color=GREY_B)
        l1.next_to(sq, DOWN, buff=0.5)   #标签放在方块下方
        self.add(sq)   #方块先静态进场景
        win.play(FadeIn(cir), run_time=0.5)   #先看到“没套住”的小圆
        win.play(cir.animate.surround(sq), run_time=0.8)   #圆移动缩放，刚好包住方块（1.2 倍余量）
        win.play(FadeIn(l1), run_time=0.3)   #标签淡入
        pdot = Dot(cir.point_at_angle(45 * DEGREES), radius=0.07, color=YELLOW)   #在圆上 45° 处取一个点
        win.play(FadeIn(pdot), run_time=0.3)   #点出圆上的点

        # —— Circle 默认参数：radius=None 当 1，color=RED ——
        red_c = Circle().shift(RIGHT * 3.0)   #默认：半径 1、描边红色
        l2 = Text("Circle() default: r=1, RED", font_size=24, color=GREY_B)
        l2.next_to(red_c, DOWN, buff=0.35)   #标签放在红圈下方
        win.play(Create(red_c), FadeIn(l2), run_time=0.7)   #画出默认红圈

        # —— Dot：point / radius / color / fill_opacity ——
        d1 = Dot(point=[0.6, -2.5, 0])   #默认：半径 0.08、白色实心
        d2 = Dot(point=[2.2, -2.5, 0], radius=0.2, color=ORANGE)   #更大的橙色点
        d3 = Dot(point=[3.8, -2.5, 0], radius=0.12, color=TEAL, fill_opacity=0.5)   #半透明青点
        l3 = Text("Dot(radius=...)", font_size=24, color=GREY_B)
        l3.next_to(d2, DOWN, buff=0.4)   #标签放在中间那个点下方（避开红圈标签）
        win.play(FadeIn(d1), FadeIn(d2), FadeIn(d3), run_time=0.5)   #三个点一起淡入
        win.play(FadeIn(l3), run_time=0.3)   #标签淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("arc", ArcDemo),
    ("curved", CurvedArrowDemo),
    ("circle_dot", CircleDotDemo),
]

PAIRS = [
    ("arc", ["arc"]),
    ("curved", ["curved"]),
    ("circle_dot", ["circle_dot"]),
]

PAGE = "01-基本形状"


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
