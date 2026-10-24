# -*- coding: utf-8 -*-
"""04b-路径与序列工具.md 两个样例的完整源码（与页面里的代码块逐字一致）。
跑法：python 04b-路径与序列工具.py <片段名>...
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

from real_time_manim import (
    Scene, Text, VGroup, Dot, Line, Circle,
    BLUE, GREEN, RED, YELLOW, GREY_B, TEAL, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI, TAU,
    adjacent_pairs, choose, clip, sigmoid, remove_list_redundancies,
    path_along_arc, Transform,
    FadeIn, Write, Create,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：path_along_arc 的三条变换轨迹 ================================
class PathArcDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("04b-path_along_arc", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        xs0, xs1 = -1.8, 1.8   #三条泳道共用的起点与终点横坐标（弦长相同）
        lanes = [
            (1.1, GREEN, "path_along_arc(-TAU/2)", -TAU / 2),   #上：反向绕半圈（弧线鼓到上方）
            (-0.2, BLUE, "straight (default)", None),   #中：默认直线路径
            (-1.4, RED, "path_along_arc(TAU/2)", TAU / 2),   #下：正向绕半圈（弧线鼓到下方）
        ]
        movers = []
        for y, c, nm, arc in lanes:
            track = Line([xs0, y, 0], [xs1, y, 0], color=GREY_B, stroke_width=2)
            track.set_stroke(opacity=0.3)   #弦（参考直线，半透明）
            lab = Text(nm, font_size=16, color=c).next_to(track, UP, buff=0.15)   #泳道名在轨道上方
            s0 = Circle(radius=0.12, color=GREY_B, stroke_width=2).move_to([xs0, y, 0])   #起点环
            s1 = Circle(radius=0.12, color=GREY_B, stroke_width=2).move_to([xs1, y, 0])   #终点环
            dot = Dot([xs0, y, 0], radius=0.14, color=c)   #出发的点
            target = Dot([xs1, y, 0], radius=0.14, color=c)   #终点处的目标点
            win.play(FadeIn(VGroup(track, lab, s0, s1)), run_time=0.4)   #泳道先就位
            movers.append((dot, target, arc))
        win.play(FadeIn(VGroup(*[m for m, _, _ in movers])), run_time=0.3)   #三个点就位
        win.play(*[Transform(m, t, path_func=path_along_arc(a) if a else None,
                             run_time=1.6)
                   for m, t, a in movers])   #同一条弦 × 三种 path_func 同时出发
        note = Text("Transform(..., path_func=path_along_arc(arc))",
                    font_size=18, color=YELLOW).to_edge(DOWN)   #底部说明
        win.play(FadeIn(note), run_time=0.35)   #说明淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：adjacent_pairs 闭合连边 + 数学小函数 =========================
class SequenceDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("04b-iterables_functions", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        pts = [(-3.2, -0.9, 0), (-1.5, -2.0, 0),   #左边四个点（不规则四边形）
               (-0.9, 0.5, 0), (-2.9, 1.4, 0)]
        head = Text("adjacent_pairs: 4 pts -> 4 edges", font_size=15, color=GREY_B)
        head.move_to([-2.1, 2.1, 0])   #左图标题
        dots = VGroup(*[Dot(p, radius=0.09, color=RED) for p in pts])   #四个顶点
        win.play(FadeIn(head), FadeIn(dots), run_time=0.5)   #标题与顶点先就位
        edges = [Line(a, b, color=BLUE, stroke_width=4)   #相邻对：(1,2)(2,3)(3,4)(4,1)
                 for a, b in adjacent_pairs(pts)]   #最后自动补上 (4,1)，闭合成四边形
        for e in edges:
            win.play(Create(e), run_time=0.35)   #四条边逐条画出（第四条回到起点）

        vals = VGroup(
            Text("choose(5, 2) = %d" % choose(5, 2), font_size=18, color=WHITE),
            Text("clip(3.7, 0, 1) = %.1f" % clip(3.7, 0, 1), font_size=18, color=GREEN),
            Text("sigmoid(0) = %.3f" % sigmoid(0), font_size=18, color=TEAL),
        ).arrange(DOWN, buff=0.28, aligned_edge=LEFT)   #右侧三行取值
        vals.move_to([1.9, 0.3, 0])
        win.play(FadeIn(vals), run_time=0.6)   #三行数值淡入
        note = Text("remove_list_redundancies: [1,2,1,3,2] -> [1,3,2]",
                    font_size=17, color=YELLOW).to_edge(DOWN)   #去重且保留最后一次出现
        win.play(FadeIn(note), run_time=0.35)   #底部说明淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("paths", PathArcDemo),
    ("iterables", SequenceDemo),
]

PAIRS = [
    ("paths", ["paths"]),
    ("iterables", ["iterables"]),
]

PAGE = "04b-路径与序列工具"


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
