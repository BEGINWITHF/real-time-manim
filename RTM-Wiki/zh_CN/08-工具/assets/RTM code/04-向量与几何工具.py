# -*- coding: utf-8 -*-
"""04-向量与几何工具.md 三个样例的完整源码（与页面里的代码块逐字一致）。
跑法：python 04-向量与几何工具.py <片段名>...
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

import numpy as np
from real_time_manim import (
    Scene, Text, VGroup, Dot, Vector, Line, Arc, Polygon, Circle,
    BLUE, GREEN, RED, YELLOW, GREY_B, WHITE, PURPLE, GOLD, TEAL,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI, TAU,
    rotate_vector, angle_between_vectors, angle_of_vector,
    center_of_mass, midpoint, regular_vertices, shoelace, shoelace_direction,
    FadeIn, Write, Create,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：rotate_vector 绕轴旋转向量 ===================================
class RotateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("04-rotate_vector", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        o = Dot(ORIGIN, radius=0.06, color=WHITE)   #坐标原点
        v0 = Vector(2.4 * RIGHT, color=GREY_B)   #基准向量：RIGHT 本身
        l0 = Text("RIGHT", font_size=18, color=GREY_B).next_to(v0.get_end(), DOWN, buff=0.2)
        win.play(FadeIn(o), Create(v0), FadeIn(l0), run_time=0.7)   #先把基准箭头画出来

        v45 = Vector(2.4 * rotate_vector(RIGHT, PI / 4), color=YELLOW)   #绕默认轴 OUT 逆时针转 45°
        a45 = Arc(radius=1.2, start_angle=0, angle=PI / 4, arc_center=ORIGIN,
                  color=YELLOW, stroke_width=5)   #0 → 45° 的角弧
        l45 = Text("rotate(PI/4)", font_size=17, color=YELLOW).move_to([1.3, 1.9, 0])   #45° 标签（放在角弧外侧）
        win.play(Create(a45), Create(v45), FadeIn(l45), run_time=0.7)   #转 45° 的结果

        v90 = Vector(2.4 * rotate_vector(RIGHT, PI / 2), color=GREEN)   #转 90°：RIGHT 恰好转成 UP
        a90 = Arc(radius=1.7, start_angle=0, angle=PI / 2, arc_center=ORIGIN,
                  color=GREEN, stroke_width=4)   #0 → 90° 的角弧（更大的一圈）
        l90 = Text("rotate(PI/2)", font_size=17, color=GREEN).move_to([2.1, 0.8, 0])   #90° 标签
        win.play(Create(a90), Create(v90), FadeIn(l90), run_time=0.7)   #转 90° 的结果
        note = Text("rotate_vector(v, angle, axis=OUT) returns a new vector",
                    font_size=18, color=YELLOW).to_edge(DOWN)   #底部说明：不改原向量
        win.play(FadeIn(note), run_time=0.35)   #说明淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：夹角与质心 ===================================================
class AngleCentroidDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("04-angle_centroid", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        a = Vector([2.6, 0.9, 0], color=RED)   #向量 1
        b = Vector([1.1, 2.4, 0], color=BLUE)   #向量 2
        la = Text("v1", font_size=18, color=RED).next_to(a.get_end(), RIGHT, buff=0.15)
        lb = Text("v2", font_size=18, color=BLUE).next_to(b.get_end(), UP, buff=0.15)
        ang = angle_between_vectors(a.get_end(), b.get_end())   #两向量夹角，恒在 [0, PI]
        aa, ab = angle_of_vector(a.get_end()), angle_of_vector(b.get_end())   #各自的极角，用来摆角弧
        arc = Arc(radius=1.15, start_angle=aa, angle=ab - aa, arc_center=ORIGIN,
                  color=YELLOW, stroke_width=6)   #两箭头之间的角弧
        lt = Text("%.3f rad" % ang, font_size=17, color=YELLOW).move_to([1.05, 0.45, 0])   #夹角数值
        win.play(Create(a), FadeIn(la), run_time=0.5)   #先画 v1
        win.play(Create(b), FadeIn(lb), run_time=0.5)   #再画 v2
        win.play(Create(arc), FadeIn(lt), run_time=0.5)   #量出夹角

        pts = [np.array([-3.1, -1.0, 0]), np.array([-1.2, -2.0, 0]),   #左下四个点（不规则四边形）
               np.array([-0.7, 0.5, 0]), np.array([-2.9, 1.3, 0])]
        quad = Polygon(*pts, color=GREY_B, stroke_width=3)   #按顺序连线成四边形
        pdots = VGroup(*[Dot(p, radius=0.09, color=RED) for p in pts])   #四个顶点
        com = center_of_mass(pts)   #质心 = 各点算术平均
        star = Dot(com, radius=0.12, color=GOLD)   #质心点
        lc = Text("center_of_mass", font_size=16, color=GOLD).next_to(star, DOWN, buff=0.18)
        mid = midpoint(pts[0], pts[1])   #底边中点
        mdot = Dot(mid, radius=0.09, color=GREEN)
        lm = Text("midpoint", font_size=15, color=GREEN).next_to(mdot, DOWN, buff=0.15)
        win.play(Create(quad), FadeIn(pdots), run_time=0.7)   #不规则四边形
        win.play(FadeIn(star), FadeIn(lc), run_time=0.4)   #质心落点
        win.play(FadeIn(mdot), FadeIn(lm), run_time=0.4)   #中点落点
        note = Text("angle_between_vectors -> [0, PI]", font_size=18, color=YELLOW).to_edge(DOWN)
        win.play(FadeIn(note), run_time=0.35)   #底部说明淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：shoelace 鞋带面积与 regular_vertices 正多边形顶点 ===========
class PolygonDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("04-shoelace_regular_vertices", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        verts, sa = regular_vertices(5, radius=1.4, start_angle=PI / 2)   #半径 1.4 的正五边形顶点 + 起始角
        poly = Polygon(*verts, color=PURPLE, fill_opacity=0.3, stroke_width=5).shift([-2.3, -0.4, 0])   #左半：正五边形
        vdots = VGroup(*[Dot(v + np.array([-2.3, -0.4, 0]), radius=0.08, color=GOLD)
                         for v in verts])   #五个顶点打点
        lv = Text("regular_vertices(n=5, radius=1.4)", font_size=15, color=GREY_B)
        lv.move_to([-2.3, 2.4, 0])   #左图标题
        area = shoelace(np.array(list(verts) + [verts[0]]))   #鞋带公式：有向面积（喂 np.array，手动补回首点闭合）
        dire = shoelace_direction(np.array(verts))   #顶点走向：“CW” 或 “CCW”
        la = Text("shoelace = %.3f" % area, font_size=16, color=PURPLE).move_to([-2.3, -2.75, 0])   #面积数值
        ld = Text("shoelace_direction = " + dire, font_size=16, color=YELLOW).move_to([-2.3, -3.2, 0])   #走向
        win.play(FadeIn(lv), Create(poly), FadeIn(vdots), run_time=0.9)   #正五边形整体亮相
        win.play(FadeIn(la), FadeIn(ld), run_time=0.5)   #面积与走向两行

        sq = [np.array([1.0, -1.0, 0]), np.array([1.0, 1.0, 0]),   #右半：顺时针顺序的正方形
              np.array([3.0, 1.0, 0]), np.array([3.0, -1.0, 0])]   #（左下 → 左上 → 右上 → 右下）
        sqp = Polygon(*sq, color=TEAL, fill_opacity=0.3, stroke_width=5)
        sqdots = VGroup(*[Dot(p, radius=0.08, color=GREEN) for p in sq])
        ls = Text("clockwise order (4 pts)", font_size=15, color=GREY_B).move_to([2.0, 2.4, 0])   #右图标题
        sarea = shoelace(np.array(sq + [sq[0]]))   #顺时针顺序 + 闭合首点 → 有向面积为正
        sdir = shoelace_direction(np.array(sq))
        lsa = Text("shoelace = %.1f" % sarea, font_size=16, color=TEAL).move_to([2.0, -1.6, 0])
        lsd = Text("shoelace_direction = " + sdir, font_size=16, color=YELLOW).move_to([2.0, -2.05, 0])
        win.play(Create(sqp), FadeIn(sqdots), FadeIn(ls), run_time=0.7)   #顺时针正方形
        win.play(FadeIn(lsa), FadeIn(lsd), run_time=0.5)   #它的面积与走向
        note = Text("shoelace(np.array) + close the loop", font_size=18, color=YELLOW).to_edge(DOWN)   #底部说明：要闭合、要 np.array
        win.play(FadeIn(note), run_time=0.35)   #底部说明：要闭合、要 np.array
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("rotate", RotateDemo),
    ("angle_centroid", AngleCentroidDemo),
    ("polygon", PolygonDemo),
]

PAIRS = [
    ("rotate", ["rotate"]),
    ("angle_centroid", ["angle_centroid"]),
    ("polygon", ["polygon"]),
]

PAGE = "04-向量与几何工具"


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
