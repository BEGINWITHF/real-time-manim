# -*- coding: utf-8 -*-
"""03-多边形与星形.md 两个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 03-多边形与星形.py <片段名>...
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
    Scene, Polygram, Polygon, RegularPolygon, Triangle, Star, RegularPolygram,
    Dot, VGroup, Text,
    TEAL, GREEN, PURPLE, ORANGE, BLUE, GOLD, YELLOW, GREY_B,
    UP, DOWN, Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：Polygram / Polygon / RegularPolygon / Triangle ==============
class PolygonsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("03-Polygram / Polygon / RegularPolygon / Triangle", font_size=26, color=YELLOW)
        title.to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— Polygram：一组顶点=一个位置参数，顺序乱穿可自交 ——
        pb = Polygram([[-5.6, 2.0, 0], [-2.6, 0.8, 0], [-3.6, 2.0, 0], [-4.6, 0.8, 0]],
                      color=TEAL, stroke_width=5)   #顶点按“左上→右下→右上→左下”穿插
        cap1 = Text("Polygram (crossed order)", font_size=20, color=GREY_B).move_to([-4.6, 0.4, 0])
        win.play(Create(pb), FadeIn(cap1), run_time=0.7)   #画出蝴蝶结形 + 字幕

        # —— Polygon：按顶点顺序连线闭合、可填充 ——
        pg = Polygon([-1.6, 2.0, 0], [1.6, 2.0, 0], [0.9, 0.7, 0], [-0.7, 0.7, 0],
                     color=GREEN, fill_opacity=0.55, stroke_width=5)   #四顶点不规则四边形
        cap2 = Text("Polygon(*vertices)", font_size=20, color=GREY_B).move_to([0, 0.4, 0])
        win.play(Create(pg), FadeIn(cap2), run_time=0.7)   #画出四边形 + 字幕

        # —— Triangle：等边三角形（n=3 特化）——
        tri = Triangle(radius=1.2, color=BLUE, fill_opacity=0.55).shift([4.6, 1.5, 0])   #等边三角
        cap3 = Text("Triangle()", font_size=20, color=GREY_B).move_to([4.6, 0.4, 0])
        win.play(Create(tri), FadeIn(cap3), run_time=0.6)   #画出三角形 + 字幕

        # —— RegularPolygon：n 边数一变形状即变 ——
        r4 = RegularPolygon(n=4, radius=1.1, color=PURPLE, fill_opacity=0.55).shift([-4.6, -1.5, 0])   #n=4
        r6 = RegularPolygon(n=6, radius=1.1, color=ORANGE, fill_opacity=0.55).shift([0, -1.5, 0])   #n=6
        r8 = RegularPolygon(n=8, radius=1.1, color=BLUE, fill_opacity=0.55).shift([4.6, -1.5, 0])   #n=8
        cap4 = Text("RegularPolygon(n=4 / 6 / 8)", font_size=22, color=GREY_B).move_to([0, -2.8, 0])
        win.play(Create(r4), run_time=0.45)   #画 n=4
        win.play(Create(r6), run_time=0.45)   #画 n=6
        win.play(Create(r8), FadeIn(cap4), run_time=0.45)   #画 n=8 + 字幕
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：Star / RegularPolygram / round_corners / get_vertices ======
class StarsRoundDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("03-Star / RegularPolygram / round_corners / get_vertices",
                     font_size=24, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 第一排：三种星 ——
        s5 = Star(n=5, outer_radius=1.5, inner_radius=0.6, color=GOLD, fill_opacity=0.9)
        s5.shift([-4.7, 1.5, 0])   #内半径手动指定的五角星
        cap1 = Text("Star(inner_radius=0.6)", font_size=19, color=GREY_B).move_to([-4.7, 0.4, 0])
        win.play(Create(s5), FadeIn(cap1), run_time=0.6)   #画金五角星 + 字幕

        rp = RegularPolygram(5, density=2, radius=1.4, color=TEAL, stroke_width=5)
        rp.shift([-0.6, 1.5, 0])   #正五角星基类：隔 1 点连线（自带交叉线）
        cap2 = Text("RegularPolygram(density=2)", font_size=19, color=GREY_B).move_to([-0.6, 0.4, 0])
        win.play(Create(rp), FadeIn(cap2), run_time=0.6)   #画五角星线框 + 字幕

        s7 = Star(n=7, outer_radius=1.4, density=3, color=BLUE, fill_opacity=0.6)
        s7.shift([4.6, 1.5, 0])   #七角星：inner_radius 交给 density 推算
        cap3 = Text("Star(n=7, density=3)", font_size=19, color=GREY_B).move_to([4.6, 0.4, 0])
        win.play(Create(s7), FadeIn(cap3), run_time=0.6)   #画七角星 + 字幕

        # —— 第二排：同形梯形，只差圆角半径 ——
        t1 = Polygon([-5.9, -0.7, 0], [-3.3, -0.7, 0], [-3.7, -2.5, 0], [-5.5, -2.5, 0],
                     color=ORANGE, fill_opacity=0.55).round_corners(0.15)   #轻微圆角
        cap4 = Text("round_corners(0.15)", font_size=19, color=GREY_B).move_to([-4.6, -2.85, 0])
        win.play(Create(t1), FadeIn(cap4), run_time=0.6)   #画小圆角梯形 + 字幕

        t2 = Polygon([-2.7, -0.7, 0], [-0.1, -0.7, 0], [-0.5, -2.5, 0], [-2.3, -2.5, 0],
                     color=PURPLE, fill_opacity=0.55).round_corners(0.55)   #大圆角
        cap5 = Text("round_corners(0.55)", font_size=19, color=GREY_B).move_to([-1.4, -2.85, 0])
        win.play(Create(t2), FadeIn(cap5), run_time=0.6)   #画大圆角梯形 + 字幕

        # —— get_vertices()：把每个顶点标出来 ——
        hexa = RegularPolygon(n=6, radius=1.1, color=BLUE, fill_opacity=0.3).shift([4.6, -1.6, 0])   #六边形坯子
        dots = VGroup(*[Dot(p, radius=0.07, color=YELLOW) for p in hexa.get_vertices()])   #顶点处摆黄点
        cap6 = Text("get_vertices() -> dots", font_size=19, color=GREY_B).move_to([4.6, -2.85, 0])
        win.play(Create(hexa), run_time=0.5)   #先画六边形
        win.play(FadeIn(dots), FadeIn(cap6), run_time=0.5)   #顶点黄点 + 字幕
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("polygons", PolygonsDemo),
    ("stars_round", StarsRoundDemo),
]

PAIRS = [
    ("polygons", ["polygons"]),
    ("stars_round", ["stars_round"]),
]

PAGE = "03-多边形与星形"


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
