# -*- coding: utf-8 -*-
"""01b-基本形状进阶.md 两个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 01b-基本形状进阶.py <片段名>...
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
    Scene, AnnotationDot, LabeledDot, Ellipse, AnnularSector, Sector, Annulus,
    CubicBezier, ArcPolygon, ArcPolygonFromArcs, ArcBetweenPoints, Dot, Text,
    ORANGE, RED, GREEN, BLUE, TEAL, PURPLE, YELLOW, GREY_B,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI, TAU,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：强调点与标签点、椭圆 ======================================
class DotsEllipseDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01b-AnnotationDot / LabeledDot / Ellipse", font_size=30, color=YELLOW)
        title.to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— AnnotationDot：带白描边的强调圆点（对照默认 Dot）——
        ad = AnnotationDot().move_to([-4.2, 0.6, 0])   #默认：蓝底、白描边 5、半径 0.104（无位置参数，画完再挪）
        d = Dot([-2.7, 0.6, 0])   #对照：默认白色小点（半径 0.08、无描边）
        l1 = Text("AnnotationDot vs Dot", font_size=22, color=GREY_B)
        l1.move_to([-3.45, -0.15, 0])   #标签放在两点下方居中
        win.play(FadeIn(ad), FadeIn(d), run_time=0.5)   #两个点一起淡入
        win.play(FadeIn(l1), run_time=0.3)   #标签淡入

        # —— LabeledDot：中心带标签的圆点（字符串自动按 MathTex 渲染）——
        ld1 = LabeledDot("x").shift([0, 0.7, 0])   #半径按标签自适应
        ld2 = LabeledDot("42", radius=0.55).shift(DOWN * 1.15)   #半径手动指定
        l2 = Text("LabeledDot(label, radius)", font_size=22, color=GREY_B)
        l2.move_to([0, -2.35, 0])   #标签放在两个标签点下方
        win.play(FadeIn(ld1), run_time=0.5)   #自适应半径的标签点
        win.play(FadeIn(ld2), run_time=0.5)   #手动半径的标签点
        win.play(FadeIn(l2), run_time=0.3)   #标签淡入

        # —— Ellipse：width / height 两轴长 ——
        e1 = Ellipse(width=4.2, height=1.6, color=PURPLE).shift([4.3, 0.9, 0])   #扁椭圆
        e2 = Ellipse(width=1.6, height=3.0, color=TEAL).shift([4.3, -1.4, 0])   #瘦椭圆
        l3 = Text("Ellipse(width=, height=)", font_size=22, color=GREY_B)
        l3.move_to([4.3, -3.4, 0])   #标签放在两个椭圆下方
        win.play(Create(e1), run_time=0.6)   #画出扁椭圆
        win.play(Create(e2), run_time=0.6)   #画出瘦椭圆
        win.play(FadeIn(l3), run_time=0.3)   #标签淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：扇环家族、贝塞尔曲线与弧多边形 ============================
class SectorsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01b-AnnularSector / Sector / Annulus / Bezier / ArcPolygon",
                     font_size=24, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 第一排：三种"扇环/圆环"填色块 ——
        asec = AnnularSector(inner_radius=0.5, outer_radius=1.2, angle=2.0,
                             start_angle=PI / 2, color=ORANGE).shift(LEFT * 4.4 + UP * 0.9)   #环形扇区
        cap1 = Text("AnnularSector", font_size=20, color=GREY_B).next_to(asec, DOWN, buff=0.3)
        win.play(Create(asec), FadeIn(cap1), run_time=0.6)   #画出环形扇区

        sec = Sector(radius=0.95, angle=TAU / 3, color=RED).shift(UP * 0.9)   #实心扇形（饼图一块）
        cap2 = Text("Sector", font_size=20, color=GREY_B).next_to(sec, DOWN, buff=0.3)
        win.play(Create(sec), FadeIn(cap2), run_time=0.6)   #画出实心扇形

        ann = Annulus(inner_radius=0.4, outer_radius=1.0, color=GREEN).shift(RIGHT * 4.4 + UP * 0.9)   #圆环（甜甜圈）
        cap3 = Text("Annulus", font_size=20, color=GREY_B).next_to(ann, DOWN, buff=0.3)
        win.play(Create(ann), FadeIn(cap3), run_time=0.6)   #画出圆环

        # —— 第二排：手绘贝塞尔、顶点间用弧连的多边形 ——
        cb = CubicBezier([-6.2, -2.6, 0], [-4.9, -0.9, 0], [-3.9, -3.5, 0], [-2.7, -1.8, 0],
                         color=PURPLE, stroke_width=6)   #两个锚点 + 两个控制柄
        cap4 = Text("CubicBezier(4 pts)", font_size=20, color=GREY_B).move_to([-4.45, -3.7, 0])
        win.play(Create(cb), FadeIn(cap4), run_time=0.6)   #画出 S 形贝塞尔曲线

        ap = ArcPolygon([-1.7, -2.9, 0], [0, -1.5, 0], [1.7, -2.9, 0],
                        angle=PI / 6, color=BLUE, stroke_width=6)   #三顶点、边用弧连
        cap5 = Text("ArcPolygon(angle=PI/6)", font_size=20, color=GREY_B).move_to([0, -3.7, 0])
        win.play(Create(ap), FadeIn(cap5), run_time=0.6)   #画出弧边三角

        a1 = ArcBetweenPoints([2.7, -2.9, 0], [4.4, -1.6, 0], angle=-PI / 3, color=TEAL)   #上拱的第一段弧
        a2 = ArcBetweenPoints([4.4, -1.6, 0], [6.1, -2.9, 0], angle=PI / 3, color=TEAL)   #下凹的第二段弧
        apa = ArcPolygonFromArcs(a1, a2)   #两段弧首尾相接拼成一个对象
        cap6 = Text("ArcPolygonFromArcs", font_size=20, color=GREY_B).move_to([4.4, -3.7, 0])
        win.play(Create(a1), run_time=0.4)   #先画第一段
        win.play(Create(a2), run_time=0.4)   #再画第二段
        win.play(FadeIn(cap6), run_time=0.3)   #标签淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("dots_ellipse", DotsEllipseDemo),
    ("sectors", SectorsDemo),
]

PAIRS = [
    ("dots_ellipse", ["dots_ellipse"]),
    ("sectors", ["sectors"]),
]

PAGE = "01b-基本形状进阶"


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
