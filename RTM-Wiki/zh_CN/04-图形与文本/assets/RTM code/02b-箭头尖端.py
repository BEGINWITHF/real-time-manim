# -*- coding: utf-8 -*-
"""02b-箭头尖端.md 两个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 02b-箭头尖端.py <片段名>...
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
    Scene, Line, Arc, Arrow, Text,
    StealthTip, ArrowTriangleTip, ArrowTriangleFilledTip,
    ArrowCircleTip, ArrowCircleFilledTip, ArrowSquareTip, ArrowSquareFilledTip,
    BLUE, RED, GREEN, TEAL, YELLOW, GREY_B,
    UP, DOWN, LEFT, RIGHT, PI, Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：尖端基类方法 add_tip / get_tip / tip_length ================
class TipsBaseDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02b-add_tip / get_tip / tip_length", font_size=30, color=YELLOW)
        title.to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 线默认没有尖端，add_tip() 现场装 ——
        ln1 = Line([-5.5, 2.0, 0], [0.5, 2.0, 0], color=BLUE, stroke_width=7)   #Line 默认无尖端
        c1 = Text("Line (no tip yet)", font_size=22, color=GREY_B).next_to(ln1, DOWN, buff=0.15)
        win.play(Create(ln1), FadeIn(c1), run_time=0.6)   #画出光杆线 + 字幕

        # —— tip_length 构造期给定；get_tip() 取回尖端对象 ——
        ln2 = Line([-5.5, 0.75, 0], [0.5, 0.75, 0], color=RED, stroke_width=7, tip_length=0.6)   #构造期给 tip_length
        c2 = Text("tip_length=0.6 + add_tip() + get_tip()", font_size=20, color=GREY_B)
        c2.next_to(ln2, DOWN, buff=0.15)   #字幕在下方
        win.play(Create(ln2), run_time=0.5)   #先画光杆
        win.play(ln2.animate.add_tip(), run_time=0.5)   #按 tip_length=0.6 装上尖端
        tip = ln2.get_tip()   #取回刚装上的尖端对象（get_tip 无参数）
        win.play(tip.animate.set_color(YELLOW), FadeIn(c2), run_time=0.4)   #把尖端染黄，证明取到了

        # —— at_start：尖端装在起点那头 ——
        ln3 = Line([-5.5, -0.5, 0], [0.5, -0.5, 0], color=GREEN, stroke_width=7)   #起点在左
        c3 = Text("add_tip(at_start=True)", font_size=22, color=GREY_B).next_to(ln3, DOWN, buff=0.15)
        win.play(Create(ln3), run_time=0.4)   #先画光杆
        win.play(ln3.animate.add_tip(at_start=True), FadeIn(c3), run_time=0.5)   #尖头装到左端

        # —— tip=：直接塞一个造好的尖端实例 ——
        ln4 = Line([-5.5, -1.75, 0], [0.5, -1.75, 0], color=TEAL, stroke_width=7)   #准备装方头
        c4 = Text("add_tip(tip=ArrowSquareTip(...))", font_size=18, color=GREY_B)
        c4.next_to(ln4, DOWN, buff=0.15)   #字幕在下方
        win.play(Create(ln4), run_time=0.4)   #先画光杆
        win.play(ln4.animate.add_tip(tip=ArrowSquareTip(length=0.42)), FadeIn(c4), run_time=0.5)   #装现成的方头实例

        # —— 任意弧也能加尖（弧尾出箭头）——
        arc = Arc(radius=1.1, start_angle=-PI / 4, angle=PI / 2, color=YELLOW, stroke_width=7)
        arc.shift([4.6, 1.0, 0])   #右上一段弧
        c5 = Text("arc.add_tip(tip_length=0.3)", font_size=22, color=GREY_B).move_to([4.6, -0.6, 0])
        win.play(Create(arc), run_time=0.5)   #先画弧
        win.play(arc.animate.add_tip(tip_length=0.3), FadeIn(c5), run_time=0.5)   #弧尾装尖 + 字幕
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：七种尖端外形 tip_shape=... =================================
class TipShapesDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02b-7 tip shapes (tip_shape=...)", font_size=30, color=YELLOW)
        title.to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        names = ["StealthTip", "ArrowTriangleTip", "ArrowTriangleFilledTip",
                 "ArrowCircleTip", "ArrowCircleFilledTip",
                 "ArrowSquareTip", "ArrowSquareFilledTip"]   #七种尖端类名
        shapes = [StealthTip, ArrowTriangleTip, ArrowTriangleFilledTip,
                  ArrowCircleTip, ArrowCircleFilledTip,
                  ArrowSquareTip, ArrowSquareFilledTip]   #七种类本身（传类不传实例）
        ys = [2.6, 1.7, 0.8, -0.1, -1.0, -1.9, -2.8]   #七行的纵坐标
        for name, shape, y in zip(names, shapes, ys):   #逐行画：箭头 + 右侧类名
            a = Arrow([-5.2, y, 0], [2.2, y, 0], buff=0, stroke_width=6,
                      tip_shape=shape)   #tip_shape 传“类”，不加括号
            lab = Text(name, font_size=22, color=GREY_B).next_to(a, RIGHT, buff=0.3)
            win.play(Create(a), FadeIn(lab), run_time=0.45)   #画箭头 + 类名字幕
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("tips_base", TipsBaseDemo),
    ("tip_shapes", TipShapesDemo),
]

PAIRS = [
    ("tips_base", ["tips_base"]),
    ("tip_shapes", ["tip_shapes"]),
]

PAGE = "02b-箭头尖端"


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
