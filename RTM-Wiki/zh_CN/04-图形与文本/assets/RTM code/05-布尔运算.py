# -*- coding: utf-8 -*-
"""05-布尔运算.md 四个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 05-布尔运算.py <样例名>...
不带参数就渲染全部样例，并拼出页面里的四条样例视频（输出到 assets/RTM output/）。
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
    Scene, Union, Difference, Intersection, Exclusion,
    Circle, Square, Triangle, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


def inputs(a, b):
    """把参与运算的两个形状做成“淡底 + 实描边”的对照版本。"""
    return VGroup(a.copy().set_fill(opacity=0.12), b.copy().set_fill(opacity=0.12))


# ===== 样例 1：Union —— 并集 ===============================================
class UnionDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("05-Union", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 两个形状的并集：重叠部分只留一层轮廓 ——
        a = Circle(radius=0.9, color=BLUE).shift(LEFT * 0.55 + UP * 1.2)
        b = Square(side_length=1.5, color=RED).shift(RIGHT * 0.55 + UP * 1.2)
        src = inputs(a, b).move_to([-4.4, 1.2, 0])
        merged = Union(a, b, color=GREEN).set_fill(GREEN, 0.5).move_to([-1.0, 1.2, 0])   #参数 “*vmobjects”
        win.play(FadeIn(src), FadeIn(Text("a + b", font_size=18, color=GREY_B).next_to(src, DOWN, buff=0.25)), run_time=0.5)
        win.play(FadeIn(merged), FadeIn(Text("Union(a, b, color=GREEN)", font_size=18, color=GREY_B).next_to(merged, DOWN, buff=0.25)), run_time=0.6)

        # —— 三个形状的并集：仍然只有一个轮廓 ——
        c = Circle(radius=0.7, color=TEAL).move_to([2.2, 1.9, 0])
        d = Square(side_length=1.1, color=ORANGE).move_to([3.3, 0.9, 0])
        e = Triangle(color=PURPLE).scale(0.65).move_to([2.0, 0.7, 0])
        three = Union(c, d, e).set_fill(PURPLE, 0.35).move_to([2.7, 1.2, 0])
        win.play(FadeIn(three), FadeIn(Text("Union(c, d, e)", font_size=18, color=GREY_B).next_to(three, DOWN, buff=0.25)), run_time=0.6)

        # —— 样式 kwargs：并集也是一个普通 VMobject ——
        a2 = Circle(radius=0.9, color=BLUE).shift(LEFT * 0.5 + DOWN * 1.6)
        b2 = Square(side_length=1.4, color=RED).shift(RIGHT * 0.5 + DOWN * 1.6)
        src2 = inputs(a2, b2).move_to([-4.4, -1.7, 0])
        styled = Union(a2, b2, color=GOLD, stroke_width=6).set_fill(GOLD, 0.85).move_to([-1.0, -1.7, 0])   #参数 “**kwargs”
        win.play(FadeIn(src2), run_time=0.4)
        win.play(FadeIn(styled), FadeIn(Text("color=GOLD stroke_width=6 fill=0.85", font_size=18, color=GREY_B).next_to(styled, DOWN, buff=0.25)), run_time=0.6)

        # —— 原对象不受影响：把 a / b 原样摆出来对比 ——
        originals = VGroup(a.copy(), b.copy()).move_to([2.7, -1.7, 0])
        win.play(FadeIn(originals), FadeIn(Text("原来的 a / b 没被改动", font_size=18, color=GREY_B).next_to(originals, DOWN, buff=0.25)), run_time=0.6)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：Difference —— 差集 ==========================================
class DifferenceDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("05-Difference", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— subject 减 clip：圆被方块啃掉一块 ——
        subj = Circle(radius=1.0, color=BLUE).move_to([-4.4, 1.3, 0])
        clip = Square(side_length=1.4, color=RED).move_to([-3.8, 0.9, 0])
        diff = Difference(subj, clip, color=GREEN).set_fill(GREEN, 0.5).move_to([-1.0, 1.3, 0])   #参数 “subject / clip”
        win.play(FadeIn(inputs(subj, clip)), FadeIn(diff),
                 FadeIn(Text("Difference(圆, 方块)", font_size=18, color=GREY_B).next_to(diff, DOWN, buff=0.25)), run_time=0.7)

        # —— 换过来：方块减圆（减法有方向）——
        subj2 = Square(side_length=1.6, color=ORANGE).move_to([2.2, 1.3, 0])
        clip2 = Circle(radius=0.85, color=TEAL).move_to([2.9, 1.3, 0])
        diff2 = Difference(subj2, clip2, color=ORANGE).set_fill(ORANGE, 0.5).move_to([4.7, 1.3, 0])
        win.play(FadeIn(inputs(subj2, clip2)), FadeIn(diff2),
                 FadeIn(Text("Difference(方块, 圆)", font_size=18, color=GREY_B).next_to(diff2, DOWN, buff=0.25)), run_time=0.7)

        # —— 样式 kwargs ——
        subj3 = Circle(radius=0.95, color=PURPLE).move_to([-4.4, -1.7, 0])
        clip3 = Triangle(color=GOLD).scale(0.9).move_to([-3.9, -1.9, 0])
        diff3 = Difference(subj3, clip3, color=PURPLE, stroke_width=6).set_fill(PURPLE, 0.8).move_to([-1.0, -1.7, 0])   #参数 “**kwargs”
        win.play(FadeIn(inputs(subj3, clip3)), FadeIn(diff3),
                 FadeIn(Text("color=PURPLE stroke_width=6 fill=0.8", font_size=18, color=GREY_B).next_to(diff3, DOWN, buff=0.25)), run_time=0.7)

        # —— 挖空：clip 完全在 subject 内部时，结果是一个“洞” ——
        ring = Difference(Circle(radius=0.95, color=RED).move_to([2.7, -1.7, 0]),
                          Circle(radius=0.5, color=RED).move_to([2.7, -1.7, 0]),
                          color=RED).set_fill(RED, 0.7)   #内圈留空 = 圆环
        win.play(FadeIn(ring), FadeIn(Text("内部挖空（圆环）", font_size=18, color=GREY_B).next_to(ring, DOWN, buff=0.25)), run_time=0.7)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：Intersection —— 交集 ========================================
class IntersectionDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("05-Intersection", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 两个形状：只留公共区域 ——
        a = Circle(radius=0.9, color=BLUE).move_to([-4.6, 1.2, 0])
        b = Circle(radius=0.9, color=RED).move_to([-3.4, 1.2, 0])
        inter = Intersection(a, b, color=YELLOW).set_fill(YELLOW, 0.8).move_to([-1.4, 1.2, 0])   #参数 “*vmobjects”
        win.play(FadeIn(inputs(a, b)), FadeIn(inter),
                 FadeIn(Text("Intersection(a, b)", font_size=18, color=GREY_B).next_to(inter, DOWN, buff=0.25)), run_time=0.7)

        # —— 三个形状：公共区域更小 ——
        c = Circle(radius=0.85, color=TEAL).move_to([2.1, 1.4, 0])
        d = Circle(radius=0.85, color=GREEN).move_to([3.3, 1.4, 0])
        e = Circle(radius=0.85, color=PURPLE).move_to([2.7, 0.4, 0])
        three = Intersection(c, d, e, color=WHITE).set_fill(WHITE, 0.8).move_to([2.7, 1.3, 0])
        win.play(FadeIn(three), FadeIn(Text("Intersection(c, d, e)", font_size=18, color=GREY_B).next_to(three, DOWN, buff=0.25)), run_time=0.7)

        # —— 样式 kwargs ——
        a2 = Square(side_length=1.5, color=BLUE).move_to([-4.6, -1.8, 0])
        b2 = Circle(radius=0.95, color=RED).move_to([-3.9, -1.4, 0])
        styled = Intersection(a2, b2, color=ORANGE, stroke_width=6).set_fill(ORANGE, 0.9).move_to([-1.4, -1.8, 0])   #参数 “**kwargs”
        win.play(FadeIn(inputs(a2, b2)), FadeIn(styled),
                 FadeIn(Text("color=ORANGE stroke_width=6", font_size=18, color=GREY_B).next_to(styled, DOWN, buff=0.25)), run_time=0.7)

        # —— 不想重叠时交集为空：给个小提示（空结果不画东西）——
        far = Intersection(Circle(radius=0.6, color=GOLD).move_to([2.0, -1.8, 0]),
                           Circle(radius=0.6, color=GOLD).move_to([4.4, -1.8, 0]), color=GOLD)
        win.play(FadeIn(Text("完全分开 -> 空结果", font_size=18, color=GREY_B).move_to([3.2, -2.6, 0])), run_time=0.5)
        win.play(FadeIn(far.set_fill(GOLD, 0.8)), run_time=0.5)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：Exclusion —— 对称差 =========================================
class ExclusionDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("05-Exclusion", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 圆与方块：只保留不重叠的部分（重叠处挖空）——
        a = Circle(radius=0.95, color=BLUE).move_to([-4.5, 1.2, 0])
        b = Square(side_length=1.5, color=RED).move_to([-3.7, 1.2, 0])
        ex = Exclusion(a, b, color=GREEN).set_fill(GREEN, 0.5).move_to([-1.3, 1.2, 0])   #参数 “subject / clip”
        win.play(FadeIn(inputs(a, b)), FadeIn(ex),
                 FadeIn(Text("Exclusion(圆, 方块)", font_size=18, color=GREY_B).next_to(ex, DOWN, buff=0.25)), run_time=0.7)

        # —— 两个圆：得到两片月牙（XOR）——
        c = Circle(radius=0.85, color=ORANGE).move_to([2.2, 1.2, 0])
        d = Circle(radius=0.85, color=TEAL).move_to([3.2, 1.2, 0])
        ex2 = Exclusion(c, d, color=YELLOW).set_fill(YELLOW, 0.7).move_to([4.6, 1.2, 0])
        win.play(FadeIn(inputs(c, d)), FadeIn(ex2),
                 FadeIn(Text("Exclusion(圆, 圆) = 两片月牙", font_size=18, color=GREY_B).next_to(ex2, DOWN, buff=0.25)), run_time=0.7)

        # —— 样式 kwargs ——
        a2 = Circle(radius=0.9, color=PURPLE).move_to([-4.5, -1.7, 0])
        b2 = Triangle(color=GOLD).scale(0.95).move_to([-3.6, -1.8, 0])
        ex3 = Exclusion(a2, b2, color=PURPLE, stroke_width=6).set_fill(PURPLE, 0.8).move_to([-1.3, -1.7, 0])   #参数 “**kwargs”
        win.play(FadeIn(inputs(a2, b2)), FadeIn(ex3),
                 FadeIn(Text("color=PURPLE stroke_width=6", font_size=18, color=GREY_B).next_to(ex3, DOWN, buff=0.25)), run_time=0.7)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("union", UnionDemo),
    ("difference", DifferenceDemo),
    ("intersection", IntersectionDemo),
    ("exclusion", ExclusionDemo),
]

PAIRS = [
    ("union", ["union"]),
    ("difference", ["difference"]),
    ("intersection", ["intersection"]),
    ("exclusion", ["exclusion"]),
]

PAGE = "05-布尔运算"


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
