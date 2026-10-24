# -*- coding: utf-8 -*-
"""04-角度与标注框.md 六个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 04-角度与标注框.py <样例名>...
不带参数就渲染全部样例，并拼出页面里的六条样例视频（输出到 assets/RTM output/）。
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
    Scene, Line, Arrow, Dot, Square, Circle, Triangle, Text, VGroup,
    Angle, RightAngle, SurroundingRectangle, BackgroundRectangle, Cross, Underline,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：Angle —— 半径 / 象限 / 优角 / 圆点 / 直角折角 ================
class AngleDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("04-Angle", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 四个 quadrant：同一个角，标记弧画到不同象限 ——
        quads = [(1, 1), (-1, 1), (1, -1), (-1, -1)]   #参数 “quadrant”
        for i, q in enumerate(quads):
            l1 = Line(ORIGIN, RIGHT * 1.6)   #参数 “line1”
            l2 = Line(ORIGIN, UP * 1.6)   #参数 “line2”
            ang = Angle(l1, l2, radius=0.45, quadrant=q, color=ORANGE)   #参数 “radius / quadrant”
            grp = VGroup(l1, l2, ang).move_to([-4.3 + i * 2.6, 1.5, 0])
            cap = Text("quadrant=%s" % (q,), font_size=18, color=GREY_B).next_to(grp, DOWN, buff=0.25)
            win.play(Create(grp), FadeIn(cap), run_time=0.5)   #逐个画角 + 象限字幕

        # —— other_angle（优角）+ dot 系列：弧内加圆点并改半径/位置/颜色 ——
        l1 = Line(ORIGIN, RIGHT * 1.6)
        l2 = Line(ORIGIN, UP * 1.6)
        big = Angle(l1, l2, radius=1.5, other_angle=True, color=RED)   #参数 “other_angle=True”
        grp = VGroup(l1, l2, big).move_to([-1.4, -1.6, 0])
        cap = Text("other_angle=True", font_size=18, color=GREY_B).next_to(grp, DOWN, buff=0.25)
        win.play(Create(grp), FadeIn(cap), run_time=0.5)   #优角 + 字幕

        l1b = Line(ORIGIN, RIGHT * 1.6)   #第二条边的另一份拷贝（一个对象只能标一次角）
        l2b = Line(ORIGIN, UP * 1.6)
        marked = Angle(l1b, l2b, radius=1.0, dot=True, dot_radius=0.12,
                       dot_distance=0.75, dot_color=YELLOW, color=TEAL)   #参数 “dot / dot_radius / dot_distance / dot_color”
        grp2 = VGroup(l1b, l2b, marked).move_to([1.6, -1.6, 0])
        cap2 = Text("dot=True dot_distance=0.75", font_size=18, color=GREY_B).next_to(grp2, DOWN, buff=0.25)
        win.play(Create(grp2), FadeIn(cap2), run_time=0.5)   #带圆点 + 字幕

        # —— elbow=True：用直角折角代替弧；get_value() 读出角度数值 ——
        l1c = Line(ORIGIN, RIGHT * 1.6)
        l2c = Line(ORIGIN, UP * 1.6)
        elbow = Angle(l1c, l2c, radius=0.6, elbow=True, color=PURPLE)   #参数 “elbow=True”
        grp3 = VGroup(l1c, l2c, elbow).move_to([4.4, -1.6, 0])
        # get_value() 在 ManimCE 0.21 上游是坏的（Angle 里没有 angle_value 属性，
        # 两引擎同崩），这里改用两条边各自的方向角之差读出同一个数值
        deg = (l2c.get_angle() - l1c.get_angle()) % (2 * PI)
        cap3 = Text("elbow=True (%.1f deg)" % (deg / PI * 180),
                    font_size=18, color=GREY_B).next_to(grp3, DOWN, buff=0.25)   #两方向角之差 = 90.0
        win.play(Create(grp3), FadeIn(cap3), run_time=0.6)   #折角 + 角度读数
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：Angle.from_three_points —— 三点定角 =========================
class AngleThreePointsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("04-Angle.from_three_points", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        a = ORIGIN + LEFT * 2.2 + DOWN * 1.2   #参数 “A” 起点
        b = ORIGIN + LEFT * 0.2 + DOWN * 1.2   #参数 “B” 顶点
        c = ORIGIN + RIGHT * 0.6 + UP * 0.8   #参数 “C” 终点
        dots = VGroup(Dot(a, radius=0.07, color=WHITE), Dot(b, radius=0.07, color=WHITE),
                      Dot(c, radius=0.07, color=WHITE))   #三个顶点用小圆点标出
        ang = Angle.from_three_points(a, b, c, radius=0.7, color=GOLD)   #三点定角（B 是顶点）
        cap = Text("Angle.from_three_points(A, B, C)", font_size=20, color=GREY_B).to_edge(DOWN, buff=1.0)
        win.play(FadeIn(dots), run_time=0.4)   #先看点
        win.play(Create(ang), FadeIn(cap), run_time=0.7)   #再画角
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：RightAngle —— 直角标记的长度与颜色 ==========================
class RightAngleDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("04-RightAngle", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— length 显式给 0.25 / 0.6，颜色也不同 ——
        l1 = Line(ORIGIN, RIGHT * 1.6)
        l2 = Line(ORIGIN, UP * 1.6)
        small = RightAngle(l1, l2, length=0.25, color=RED)   #参数 “length=0.25”
        grp = VGroup(l1, l2, small).move_to([-2.6, 0.8, 0])
        cap = Text("length=0.25", font_size=18, color=GREY_B).next_to(grp, DOWN, buff=0.25)
        win.play(Create(grp), FadeIn(cap), run_time=0.5)   #小直角标记 + 字幕

        l3 = Line(ORIGIN, RIGHT * 1.6)
        l4 = Line(ORIGIN, UP * 1.6)
        big = RightAngle(l3, l4, length=0.6, color=GREEN)   #参数 “length=0.6”
        grp2 = VGroup(l3, l4, big).move_to([1.2, 0.8, 0])
        cap2 = Text("length=0.6", font_size=18, color=GREY_B).next_to(grp2, DOWN, buff=0.25)
        win.play(Create(grp2), FadeIn(cap2), run_time=0.5)   #大直角标记 + 字幕

        # —— length 缺省：按两条边自动推算 ——
        l5 = Line(ORIGIN, RIGHT * 1.6)
        l6 = Line(ORIGIN, UP * 1.6)
        auto = RightAngle(l5, l6, color=BLUE)   #不传 length（默认 None）
        grp3 = VGroup(l5, l6, auto).move_to([4.6, 0.8, 0])
        cap3 = Text("length=None (auto)", font_size=18, color=GREY_B).next_to(grp3, DOWN, buff=0.25)
        win.play(Create(grp3), FadeIn(cap3), run_time=0.5)   #自动长度 + 字幕
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：SurroundingRectangle —— 颜色 / 间距 / 圆角 ==================
class SurroundingDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("04-SurroundingRectangle", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 单个对象：默认亮黄、buff 0.1、无圆角 ——
        sq = Square(side_length=1.4, color=BLUE, fill_opacity=0.5).move_to([-3.4, 1.2, 0])
        f1 = SurroundingRectangle(sq)   #参数 “*mobjects” 只给一个
        cap = Text("SurroundingRectangle(sq)", font_size=18, color=GREY_B).next_to(VGroup(sq, f1), DOWN, buff=0.25)
        win.play(Create(sq), run_time=0.4)   #先画被框对象
        win.play(Create(f1), FadeIn(cap), run_time=0.5)   #再套默认框 + 字幕

        # —— buff 放大 + 圆角 + 换色 ——
        ci = Circle(radius=0.7, color=GREEN, fill_opacity=0.5).move_to([0, 1.2, 0])
        f2 = SurroundingRectangle(ci, color=RED, buff=0.45, corner_radius=0.25)   #参数 “color / buff / corner_radius”
        cap2 = Text("buff=0.45 corner_radius=0.25", font_size=18, color=GREY_B).next_to(VGroup(ci, f2), DOWN, buff=0.25)
        win.play(Create(ci), run_time=0.4)
        win.play(Create(f2), FadeIn(cap2), run_time=0.5)   #大间距圆角框 + 字幕

        # —— 多个对象：取整体包围盒 ——
        tri = Triangle(color=PURPLE, fill_opacity=0.5).scale(0.6).move_to([3.0, 1.0, 0])
        dot = Dot(point=[4.6, 1.8, 0], radius=0.1, color=ORANGE)
        f3 = SurroundingRectangle(tri, dot, color=TEAL, buff=0.2)   #参数 “*mobjects” 给两个：整体包围盒
        cap3 = Text("SurroundingRectangle(tri, dot)", font_size=18, color=GREY_B).next_to(VGroup(tri, dot, f3), DOWN, buff=0.25)
        win.play(Create(tri), FadeIn(dot), run_time=0.4)
        win.play(Create(f3), FadeIn(cap3), run_time=0.5)   #整体包围盒 + 字幕
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 5：BackgroundRectangle —— 垫底色 / 描边 / 不透明度 / 边距 =====
class BackgroundDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("04-BackgroundRectangle", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 默认：黑底 75% 不透明，垫在白字下面 ——
        t1 = Text("readable", font_size=34, color=WHITE).move_to([-3.0, 1.2, 0])
        b1 = BackgroundRectangle(t1)   #参数默认值：color=None（按黑）、fill_opacity=0.75、buff=0
        win.play(FadeIn(b1), run_time=0.4)   #先垫底
        win.play(FadeIn(t1), run_time=0.4)   #再上字

        # —— 换底色 + 加描边 + 调不透明度 ——
        t2 = Text("tinted", font_size=34, color=WHITE).move_to([1.4, 1.2, 0])
        b2 = BackgroundRectangle(t2, color=PURPLE, stroke_width=4, stroke_opacity=1,
                                 fill_opacity=0.5)   #参数 “color / stroke_width / stroke_opacity / fill_opacity”
        win.play(FadeIn(b2), run_time=0.4)
        win.play(FadeIn(t2), run_time=0.4)

        # —— buff 放大：底色比字大一圈 ——
        t3 = Text("padded", font_size=34, color=WHITE).move_to([-1.0, -1.4, 0])
        b3 = BackgroundRectangle(t3, color=TEAL, fill_opacity=0.9, buff=0.35)   #参数 “buff=0.35”
        cap = Text("buff=0.35", font_size=18, color=GREY_B).next_to(VGroup(t3, b3), DOWN, buff=0.25)
        win.play(FadeIn(b3), FadeIn(cap), run_time=0.4)
        win.play(FadeIn(t3), run_time=0.4)   #垫底比字大一圈
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 6：Cross / Underline —— 否定的两种画法 =========================
class CrossUnderlineDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("04-Cross / Underline", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— Cross：位置与大小由被叉对象决定 ——
        sq = Square(side_length=1.2, color=BLUE, fill_opacity=0.5).move_to([-3.4, 0.6, 0])
        x1 = Cross(sq)   #参数 “mobject=sq”：叉在方块上，大小跟着方块
        cap1 = Text("Cross(sq)", font_size=18, color=GREY_B).next_to(VGroup(sq, x1), DOWN, buff=0.25)
        win.play(Create(sq), run_time=0.4)
        win.play(Create(x1), FadeIn(cap1), run_time=0.5)

        # —— 换颜色 / 线宽 / 缩放 ——
        ci = Circle(radius=0.6, color=GREEN, fill_opacity=0.5).move_to([0, 0.6, 0])
        x2 = Cross(ci, stroke_color=YELLOW, stroke_width=14, scale_factor=1.4)   #参数 “stroke_color / stroke_width / scale_factor”
        cap2 = Text("stroke_width=14 scale_factor=1.4", font_size=18, color=GREY_B).next_to(VGroup(ci, x2), DOWN, buff=0.25)
        win.play(Create(ci), run_time=0.4)
        win.play(Create(x2), FadeIn(cap2), run_time=0.5)

        # —— Underline：只给线宽和 buff（长度跟着对象宽度）——
        t = Text("underlined", font_size=34, color=WHITE).move_to([3.4, 0.6, 0])
        u1 = Underline(t, buff=0.08, color=RED)   #参数 “buff=0.08”
        cap3 = Text("Underline(t, buff=0.08)", font_size=18, color=GREY_B).next_to(VGroup(t, u1), DOWN, buff=0.35)
        win.play(FadeIn(t), run_time=0.4)
        win.play(Create(u1), FadeIn(cap3), run_time=0.5)

        t2 = Text("loose", font_size=34, color=WHITE).move_to([3.4, -1.6, 0])
        u2 = Underline(t2, buff=0.5, color=ORANGE)   #参数 “buff=0.5”：离字更远
        cap4 = Text("buff=0.5", font_size=18, color=GREY_B).next_to(VGroup(t2, u2), DOWN, buff=0.35)
        win.play(FadeIn(t2), run_time=0.4)
        win.play(Create(u2), FadeIn(cap4), run_time=0.5)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("angle", AngleDemo),
    ("angle3p", AngleThreePointsDemo),
    ("rightangle", RightAngleDemo),
    ("surrounding", SurroundingDemo),
    ("background", BackgroundDemo),
    ("cross", CrossUnderlineDemo),
]

PAIRS = [
    ("angle", ["angle"]),
    ("angle3p", ["angle3p"]),
    ("rightangle", ["rightangle"]),
    ("surrounding", ["surrounding"]),
    ("background", ["background"]),
    ("cross", ["cross"]),
]

PAGE = "04-角度与标注框"


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
