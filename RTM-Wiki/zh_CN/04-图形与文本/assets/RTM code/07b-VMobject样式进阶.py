# -*- coding: utf-8 -*-
"""07b-VMobject样式进阶.md 九个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 07b-VMobject样式进阶.py <样例名>...
不带参数就渲染全部样例，并拼出页面里的九条样例视频（输出到 assets/RTM output/）。
"""
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

from real_time_manim import (
    Scene, Square, Circle, Polygon, Line, Dot, Triangle, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：set_opacity —— 整体透明化 + family 开关 ======================
class OpacityDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("07b-set_opacity", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— opacity 三档：0.25 / 0.6 / 1.0（不调用就是 1.0）——
        for i, op in enumerate([0.25, 0.6, 1.0]):
            sq = Square(side_length=1.3, color=BLUE).set_fill(BLUE, 0.9)
            sq.move_to([-4.0 + i * 1.8, 1.3, 0])
            sq.set_opacity(op)   #参数 “opacity”：填充与描边一起变
            cap = Text("opacity=%.2f" % op, font_size=18, color=GREY_B).next_to(sq, DOWN, buff=0.2)
            win.play(Create(sq), FadeIn(cap), run_time=0.45)   #逐个画 + 字幕

        # —— family：同一个 VGroup，True 连子对象一起改，False 只改容器自己 ——
        g1 = VGroup(Square(side_length=0.9, color=GREEN).set_fill(GREEN, 0.9),
                    Circle(radius=0.5, color=GREEN).set_fill(GREEN, 0.9))
        g1.arrange(RIGHT, buff=0.3).move_to([-2.6, -1.4, 0])
        g1.set_opacity(0.3, family=True)   #参数 “family=True”：容器与子对象一起降
        cap1 = Text("family=True", font_size=18, color=GREY_B).next_to(g1, DOWN, buff=0.2)
        win.play(FadeIn(g1), FadeIn(cap1), run_time=0.5)   #两个子对象都变淡

        g2 = VGroup(Square(side_length=0.9, color=ORANGE).set_fill(ORANGE, 0.9),
                    Circle(radius=0.5, color=ORANGE).set_fill(ORANGE, 0.9))
        g2.arrange(RIGHT, buff=0.3).move_to([2.6, -1.4, 0])
        g2.set_opacity(0.3, family=False)   #参数 “family=False”：只改容器
        cap2 = Text("family=False", font_size=18, color=GREY_B).next_to(g2, DOWN, buff=0.2)
        win.play(FadeIn(g2), FadeIn(cap2), run_time=0.5)   #子对象保持自己的 0.9
        win.play(Wait(0.5))   #停留对比两组
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：set_sheen / set_sheen_direction —— 光泽渐变 ==================
class SheenDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("07b-set_sheen", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— factor 三档 ——
        for i, f in enumerate([0.0, 0.6, 1.5]):
            sq = Square(side_length=1.2, color=BLUE).set_fill(BLUE, 1.0)
            sq.move_to([-4.0 + i * 1.7, 1.3, 0])
            sq.set_sheen(f, direction=UP)   #参数 “factor / direction=UP”
            cap = Text("factor=%.1f" % f, font_size=18, color=GREY_B).next_to(sq, DOWN, buff=0.2)
            win.play(Create(sq), FadeIn(cap), run_time=0.45)   #0 关闭 / 0.6 / 1.5

        # —— direction 换成 RIGHT，光泽改成从左到右 ——
        sq2 = Square(side_length=1.2, color=TEAL).set_fill(TEAL, 1.0).move_to([1.4, -1.2, 0])
        sq2.set_sheen(1.0, direction=RIGHT)   #参数 “direction=RIGHT”
        cap2 = Text("direction=RIGHT", font_size=18, color=GREY_B).next_to(sq2, DOWN, buff=0.2)
        win.play(Create(sq2), FadeIn(cap2), run_time=0.5)

        # —— set_sheen_direction：单独改方向，强度沿用上一次的 factor ——
        sq3 = Square(side_length=1.2, color=PURPLE).set_fill(PURPLE, 1.0).move_to([4.4, -1.2, 0])
        sq3.set_sheen(1.0, direction=UP)   #先按 UP
        sq3.set_sheen_direction(DOWN)   #再单独改方向（family 默认 True）
        cap3 = Text("set_sheen_direction(DOWN)", font_size=18, color=GREY_B).next_to(sq3, DOWN, buff=0.2)
        win.play(Create(sq3), FadeIn(cap3), run_time=0.5)
        win.play(Wait(0.5))   #停留看渐变方向
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：make_smooth —— 折线变平滑曲线 ==============================
class MakeSmoothDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("07b-make_smooth", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        verts = [[-3.2, 1.0, 0], [-1.6, -0.6, 0], [-0.2, 1.2, 0], [1.4, -0.4, 0]]   #折线顶点
        raw = Polygon(*verts, color=GREY_B, stroke_width=5)   #原样（折角）
        smoothed = Polygon(*verts, color=GREEN, stroke_width=5)   #待平滑的那份
        smoothed.make_smooth()   #把角点改成平滑锚点：折线变曲线
        raw.shift(DOWN * 1.4)   #上：原样
        smoothed.shift(DOWN * 1.4)
        cap1 = Text("jagged (raw)", font_size=20, color=GREY_B).next_to(raw, UP, buff=0.25)
        cap2 = Text("make_smooth()", font_size=20, color=GREEN).next_to(smoothed, UP, buff=0.25)
        win.play(Create(raw), FadeIn(cap1), run_time=0.6)   #先看折线
        win.play(Create(smoothed), FadeIn(cap2), run_time=0.6)   #再看平滑后的同一条路径
        win.play(Wait(0.5))   #停留对比
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：make_jagged —— 平滑曲线改回折线 ============================
class MakeJaggedDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("07b-make_jagged", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        circle = Circle(radius=1.2, color=BLUE).set_fill(BLUE, 0.3)   #圆本身就是平滑的
        circle.move_to(LEFT * 2.2 + DOWN * 0.6)
        jagged = Circle(radius=1.2, color=ORANGE).set_fill(ORANGE, 0.3)
        jagged.make_jagged()   #把平滑锚点改回折角：圆变成多边形
        jagged.move_to(RIGHT * 2.2 + DOWN * 0.6)
        cap1 = Text("Circle (smooth)", font_size=20, color=BLUE).next_to(circle, UP, buff=0.25)
        cap2 = Text("make_jagged()", font_size=20, color=ORANGE).next_to(jagged, UP, buff=0.25)
        win.play(Create(circle), FadeIn(cap1), run_time=0.6)   #先看圆
        win.play(Create(jagged), FadeIn(cap2), run_time=0.6)   #再看同半径的"折线圆"
        win.play(Wait(0.5))   #停留对比
        win.close()   #关闭 RTM 窗口


# ===== 样例 5：pointwise_become_partial —— 沿路径截取一段 ==================
class PartialDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("07b-pointwise_become_partial", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 同一条圆，四段 [a, b] 各截一次 ——
        spans = [(0.0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.0)]   #参数 “a / b”
        for i, (a, b) in enumerate(spans):
            src = Circle(radius=0.9, color=TEAL, stroke_width=6)   #源对象
            part = Circle(radius=0.9)   #接收截取结果的对象
            part.pointwise_become_partial(src, a, b)   #参数 “vmobject / a / b”
            part.set_stroke(TEAL, 6)
            part.move_to([-4.0 + i * 2.2, 1.2, 0])
            cap = Text("[%.2f, %.2f]" % (a, b), font_size=18, color=GREY_B).next_to(part, DOWN, buff=0.25)
            win.play(Create(part), FadeIn(cap), run_time=0.45)   #四段四分之一弧

        # —— [0, 1] 就是整条路径（与源对象等长）——
        src = Circle(radius=0.9, color=GOLD, stroke_width=6)
        whole = Circle(radius=0.9)
        whole.pointwise_become_partial(src, 0, 1)   #a=0, b=1：整条
        whole.set_stroke(GOLD, 6).move_to([-1.0, -1.4, 0])
        cap = Text("[0, 1] = whole path", font_size=18, color=GREY_B).next_to(whole, DOWN, buff=0.25)
        win.play(Create(whole), FadeIn(cap), run_time=0.5)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 6：get_stroke_width —— 读出当前线宽 ============================
class GetWidthDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("07b-get_stroke_width", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        ln = Line([-4.4, 1.0, 0], [-0.4, 1.0, 0], color=BLUE, stroke_width=4)   #初始线宽 4
        info = Text("get_stroke_width() = %.1f" % ln.get_stroke_width(), font_size=24, color=WHITE)
        info.next_to(ln, DOWN, buff=0.4)
        win.play(Create(ln), FadeIn(info), run_time=0.5)   #读出来是 4.0

        ln.set_stroke(width=14)   #改线宽
        info.become(Text("after set_stroke(width=14) = %.1f" % ln.get_stroke_width(),
                         font_size=24, color=WHITE).next_to(ln, DOWN, buff=0.4))
        win.play(Create(ln), run_time=0.4)   #线变粗
        win.play(FadeIn(info), run_time=0.3)   #读出来变 14.0

        # —— background=True：读的是"背景描边宽度"（默认 0，未设置过就是 0）——
        info2 = Text("get_stroke_width(background=True) = %.1f" % ln.get_stroke_width(background=True),
                     font_size=24, color=ORANGE).next_to(info, DOWN, buff=0.25)
        win.play(FadeIn(info2), run_time=0.4)   #参数 “background=True”
        win.play(Wait(0.5))   #停留看读数
        win.close()   #关闭 RTM 窗口


# ===== 样例 7：set_cap_style —— 三种线端点样式 ============================
class CapStyleDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("07b-set_cap_style", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        from manim import CapStyleType   #三种端点样式的枚举
        styles = [("ROUND", CapStyleType.ROUND), ("BUTT", CapStyleType.BUTT),
                  ("SQUARE", CapStyleType.SQUARE)]   #参数 “cap_style”
        for i, (name, style) in enumerate(styles):
            ln = Line([-4.4, 1.4 - i * 1.5, 0], [-1.2, 1.4 - i * 1.5, 0],
                      color=TEAL, stroke_width=40)   #粗线才看得清端点
            ln.set_cap_style(style)   #参数 “cap_style=CapStyleType.%s” % name
            cap = Text("CapStyleType.%s" % name, font_size=20, color=GREY_B).next_to(ln, RIGHT, buff=0.4)
            win.play(Create(ln), FadeIn(cap), run_time=0.5)   #三种端点依次出现
        win.play(Wait(0.5))   #停留对比
        win.close()   #关闭 RTM 窗口


# ===== 样例 8：change_anchor_mode —— smooth / jagged 两档 =================
class AnchorModeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("07b-change_anchor_mode", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        verts = [[-3.0, 0.8, 0], [-1.4, -0.8, 0], [0.2, 1.0, 0], [1.8, -0.6, 0]]
        smooth = Polygon(*verts, color=GREEN, stroke_width=5)
        smooth.change_anchor_mode("smooth")   #参数 “mode="smooth"”
        smooth.shift(UP * 0.9 + LEFT * 1.4)
        jagged = Polygon(*verts, color=ORANGE, stroke_width=5)
        jagged.change_anchor_mode("jagged")   #参数 “mode="jagged"”
        jagged.shift(DOWN * 1.2 + LEFT * 1.4)
        cap1 = Text('mode="smooth"', font_size=20, color=GREEN).next_to(smooth, RIGHT, buff=0.4)
        cap2 = Text('mode="jagged"', font_size=20, color=ORANGE).next_to(jagged, RIGHT, buff=0.4)
        win.play(Create(smooth), FadeIn(cap1), run_time=0.6)   #平滑档
        win.play(Create(jagged), FadeIn(cap2), run_time=0.6)   #折角档
        win.play(Wait(0.5))   #停留对比
        win.close()   #关闭 RTM 窗口


# ===== 样例 9：apply_function —— 自定义形变与参考点 ========================
class ApplyFunctionDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("07b-apply_function", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 逐点扭曲：正弦波改 x ——
        wave = lambda p: p + 0.35 * np.sin(p[1] * PI) * RIGHT   #参数 “function”：逐点改 x
        a = Square(side_length=1.6, color=BLUE).set_fill(BLUE, 0.6).move_to([-3.6, 1.2, 0])
        a.apply_function(wave)   #参数 “function”
        cap1 = Text("apply_function(wave)", font_size=18, color=GREY_B).next_to(a, DOWN, buff=0.25)
        win.play(Create(a), FadeIn(cap1), run_time=0.5)   #方块被扭成波浪边

        # —— 整体放大：p * 1.5 ——
        b = Square(side_length=1.2, color=GREEN).set_fill(GREEN, 0.6).move_to([1.2, 1.2, 0])
        b.apply_function(lambda p: p * 1.5)   #参数 “function”：整体缩放
        cap2 = Text("function = p * 1.5", font_size=18, color=GREY_B).next_to(b, DOWN, buff=0.25)
        win.play(Create(b), FadeIn(cap2), run_time=0.5)   #方块整体变大

        # —— 缩放 + 平移：p * 0.8 + UP * 0.4 ——
        c = Square(side_length=1.2, color=RED).set_fill(RED, 0.6).move_to([1.2, -1.4, 0])
        c.apply_function(lambda p: p * 0.8 + UP * 0.4)   #参数 “function”：缩放后再整体上移
        cap3 = Text("function = p * 0.8 + UP * 0.4", font_size=18, color=GREY_B).next_to(c, DOWN, buff=0.25)
        win.play(Create(c), FadeIn(cap3), run_time=0.5)   #缩小并上移

        # —— 只改一个坐标：把 y 压扁 ——
        d = Square(side_length=1.2, color=PURPLE).set_fill(PURPLE, 0.6).move_to([4.2, -1.4, 0])
        d.apply_function(lambda p: p * [1.0, 0.5, 1.0])   #参数 “function”：只压 y
        cap4 = Text("function = p * [1, 0.5, 1]", font_size=18, color=GREY_B).next_to(d, DOWN, buff=0.25)
        win.play(Create(d), FadeIn(cap4), run_time=0.5)   #方块被压扁
        win.play(Wait(0.5))   #停留对比
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("opacity", OpacityDemo),
    ("sheen", SheenDemo),
    ("smooth", MakeSmoothDemo),
    ("jagged", MakeJaggedDemo),
    ("partial", PartialDemo),
    ("strokewidth", GetWidthDemo),
    ("capstyle", CapStyleDemo),
    ("anchor", AnchorModeDemo),
    ("applyfunc", ApplyFunctionDemo),
]

PAIRS = [
    ("opacity", ["opacity"]),
    ("sheen", ["sheen"]),
    ("smooth", ["smooth"]),
    ("jagged", ["jagged"]),
    ("partial", ["partial"]),
    ("strokewidth", ["strokewidth"]),
    ("capstyle", ["capstyle"]),
    ("anchor", ["anchor"]),
    ("applyfunc", ["applyfunc"]),
]

PAGE = "07b-VMobject样式进阶"


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
