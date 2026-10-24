# -*- coding: utf-8 -*-
"""02-线与箭头.md 两个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 02-线与箭头.py <片段名>...
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
    Scene, Line, DashedLine, TangentLine, Elbow, Arc, Arrow, Vector, DoubleArrow,
    Text, BLUE, RED, GREEN, YELLOW, ORANGE, TEAL, PURPLE, WHITE, GREY_B,
    UP, DOWN, LEFT, RIGHT, UR, PI, Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：线族 Line / DashedLine / TangentLine / Elbow ===============
class LinesDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02-Line / DashedLine / TangentLine / Elbow", font_size=28, color=YELLOW)
        title.to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— Line：起点终点 + path_arc 把“直线”掰弯 ——
        ln = Line([-5.6, 2.2, 0], [0.4, 2.2, 0], stroke_width=6, color=YELLOW)   #默认 path_arc=0：直的
        c1 = Text("Line(start, end)", font_size=22, color=GREY_B).next_to(ln, DOWN, buff=0.15)
        win.play(Create(ln), FadeIn(c1), run_time=0.6)   #画出直线 + 字幕

        ln2 = Line([-5.6, 0.9, 0], [0.4, 0.9, 0], path_arc=0.6, stroke_width=6, color=ORANGE)   #同两端点，path_arc≠0 弯成弧
        c2 = Text("Line(path_arc=0.6)", font_size=22, color=GREY_B).next_to(ln2, DOWN, buff=0.15)
        win.play(Create(ln2), FadeIn(c2), run_time=0.6)   #画出弧线 + 字幕

        # —— DashedLine：dash_length / dashed_ratio ——
        dl = DashedLine([-5.6, -0.7, 0], [0.4, -0.7, 0], dash_length=0.15,
                       dashed_ratio=0.55, color=TEAL, stroke_width=5)   #实段 0.15、实占 0.55
        c3 = Text("DashedLine(dash_length=0.15)", font_size=22, color=GREY_B).next_to(dl, DOWN, buff=0.15)
        win.play(Create(dl), FadeIn(c3), run_time=0.6)   #画出虚线 + 字幕

        # —— TangentLine：曲线在 alpha 处的切线 ——
        arc = Arc(radius=1.0, start_angle=-PI / 3, angle=2 * PI / 3, color=BLUE, stroke_width=6)
        arc.shift([4.6, 1.9, 0])   #右上角放一段圆弧
        tl = TangentLine(arc, 0.5, length=2.4, color=RED, stroke_width=6)   #弧中点（alpha=0.5）处的切线
        c4 = Text("TangentLine(arc, 0.5)", font_size=22, color=GREY_B).move_to([4.6, 0.3, 0])   #切线下方
        win.play(Create(arc), run_time=0.5)   #先画弧
        win.play(Create(tl), FadeIn(c4), run_time=0.6)   #再画切线 + 字幕

        # —— Elbow：直角拐角（angle 转方向）——
        e1 = Elbow(width=0.5, angle=0, color=GREEN, stroke_width=6).shift([3.8, -1.9, 0])   #原始朝向
        e2 = Elbow(width=0.5, angle=PI / 2, color=GREEN, stroke_width=6).shift([5.4, -1.9, 0])   #转 90°
        c5 = Text("Elbow(angle=0 / PI/2)", font_size=22, color=GREY_B).move_to([4.6, -2.9, 0])
        win.play(FadeIn(e1), FadeIn(e2), run_time=0.5)   #两个拐角一起出现
        win.play(FadeIn(c5), run_time=0.3)   #字幕淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：箭头一家 Arrow / Vector / DoubleArrow ======================
class ArrowsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02-Arrow / Vector / DoubleArrow", font_size=30, color=YELLOW)
        title.to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— Arrow：比例自动控制，短线不会头重脚轻 ——
        a1 = Arrow([-5.6, 2.0, 0], [0.6, 2.0, 0], color=BLUE, buff=0)   #常规长度
        c1 = Text("Arrow(start, end, buff=0)", font_size=22, color=GREY_B).next_to(a1, DOWN, buff=0.15)
        win.play(Create(a1), FadeIn(c1), run_time=0.7)   #画出常规箭头 + 字幕

        a2 = Arrow([-5.6, 0.6, 0], [-2.4, 0.6, 0], color=RED, buff=0, stroke_width=14)   #又短又粗：尖端自动限比例
        c2 = Text("short arrow + stroke_width=14", font_size=22, color=GREY_B).next_to(a2, DOWN, buff=0.15)
        win.play(Create(a2), FadeIn(c2), run_time=0.7)   #画出短粗箭头 + 字幕

        # —— DoubleArrow：两端都有尖端 ——
        da = DoubleArrow([3.4, 2.0, 0], [6.6, 2.0, 0], color=PURPLE, buff=0)   #双头（尺寸标注线，右移给坐标标注让位）
        c3 = Text("DoubleArrow", font_size=22, color=GREY_B).next_to(da, DOWN, buff=0.15)
        win.play(Create(da), FadeIn(c3), run_time=0.7)   #画出双头箭头 + 字幕

        # —— Vector：原点出发 + coordinate_label 标坐标 ——
        v = Vector([2.4, 1.4, 0], color=GREEN).shift([-4.8, -1.7, 0])   #方向向量（从“原点”指向 direction）
        c4 = Text("Vector([2.4, 1.4])", font_size=22, color=GREY_B).move_to([-4.4, -3.0, 0])
        win.play(Create(v), FadeIn(c4), run_time=0.7)   #画出向量 + 字幕

        v2 = Vector([2, 1, 0], color=TEAL)   #放原点：coordinate_label 按端点世界坐标取整
        lab = v2.coordinate_label(color=WHITE).next_to(v2.get_end(), UR, buff=0.2)   #端点旁标 (2, 1)
        c5 = Text("coordinate_label()", font_size=22, color=GREY_B).move_to([1.4, -0.9, 0])
        win.play(Create(v2), run_time=0.5)   #画出向量
        win.play(FadeIn(lab), FadeIn(c5), run_time=0.5)   #坐标标注 + 字幕
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("lines", LinesDemo),
    ("arrows", ArrowsDemo),
]

PAIRS = [
    ("lines", ["lines"]),
    ("arrows", ["arrows"]),
]

PAGE = "02-线与箭头"


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
