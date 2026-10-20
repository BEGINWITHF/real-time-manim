# -*- coding: utf-8 -*-
"""04b-缩放旋转与变形-进阶.md 六个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 04b-缩放旋转与变形-进阶.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的六条样例视频（输出到上一级 assets/）。
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
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    Scene, Square, Rectangle, Circle, Triangle, Line, Dot, Arc, VGroup,
    BLUE, RED, GREEN, YELLOW, GREY, TEAL,
    UP, DOWN, LEFT, RIGHT, ORIGIN, TAU, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：rescale_to_fit =============================================
class RescaleDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=BLUE, side_length=1.0, fill_opacity=0.5)   #1×1 的方块
        self.add(sq)   #进场景
        win.play(sq.animate.rescale_to_fit(4.0, 0), run_time=0.6)   #宽调到 4.0：stretch=False 等比
        print("等比后：width =", round(sq.width, 2), "height =", round(sq.height, 2))   #4.0 4.0
        win.play(sq.animate.rescale_to_fit(1.0, 1, stretch=True), run_time=0.6)   #高强制设为 1.0：只压这一维
        print("拉伸后：width =", round(sq.width, 2), "height =", round(sq.height, 2))   #4.0 1.0
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：scale_to_fit_* / stretch_to_fit_* ===========================
class FitDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        a = Rectangle(width=1.0, height=1.0, color=BLUE, fill_opacity=0.4)   #左边：保长宽比的一组
        a.shift(LEFT * 4.0 + UP * 1.4)
        b = Rectangle(width=1.0, height=1.0, color=RED, fill_opacity=0.4)   #右边：会变形的一组
        b.shift(RIGHT * 4.0 + UP * 1.4)
        self.add(a, b)   #进场景
        win.play(a.animate.scale_to_fit_width(3.0), run_time=0.6)   #等比：宽 3 高也变 3
        a.scale_to_fit_height(1.0)   #等比：高设为 1，宽也跟着回 1
        print("scale_to_fit 后：", round(a.width, 2), round(a.height, 2))   #1.0 1.0
        win.play(b.animate.stretch_to_fit_width(3.0), run_time=0.6)   #只拉宽，高不变
        b.stretch_to_fit_height(1.0)   #只压高
        print("stretch_to_fit 后：", round(b.width, 2), round(b.height, 2))   #3.0 1.0
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：pose_at_angle ==============================================
class PoseDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        tri = Triangle(color=YELLOW, fill_opacity=0.4).scale(1.2)   #摆姿势的三角形
        flat = Triangle(color=GREY, fill_opacity=0.3).shift(RIGHT * 3.2)   #不摆姿势的对照
        self.add(tri, flat)   #进场景
        print("pose 前：width =", round(tri.width, 2))   #摆之前的宽度
        win.play(tri.animate.pose_at_angle(), run_time=0.7)   #等价于 rotate(TAU/14, RIGHT + UP)
        print("pose 后：width =", round(tri.width, 2), "height =", round(tri.height, 2))   #斜向投影后变小
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：apply_function / apply_matrix / apply_complex_function =====
class ApplyDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        c1 = Circle(radius=0.8, color=BLUE, fill_opacity=0.4)   #第一个圆：先在原点变形
        self.add(c1)   #进场景
        win.play(c1.animate.apply_function(
            lambda p: np.array([p[0], p[1] + 0.55 * p[0], p[2]])), run_time=0.6)   #逐点映射：y 随 x 抬升 = 斜切
        win.play(c1.animate.move_to(LEFT * 4.2 + UP * 1.4), run_time=0.4)   #变形完挪到左上
        c2 = Circle(radius=0.8, color=RED, fill_opacity=0.4)   #第二个圆：同样先在原点
        self.add(c2)   #进场景
        win.play(c2.animate.apply_matrix(
            np.array([[1.0, 0.45, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])), run_time=0.6)   #线性变换：错切
        win.play(c2.animate.move_to(UP * 1.4), run_time=0.4)   #变形完挪到中上
        c3 = Circle(radius=0.8, color=GREEN, fill_opacity=0.4)   #第三个圆：同样先在原点
        self.add(c3)   #进场景
        win.play(c3.animate.apply_complex_function(
            lambda z: np.exp(z) * 0.5), run_time=0.6)   #复映射：圆变成豆形
        win.play(c3.animate.move_to(RIGHT * 4.2 + UP * 1.4), run_time=0.4)   #变形完挪到右上
        d1 = Dot(color=YELLOW, radius=0.13).shift(LEFT * 3.0 + DOWN * 1.6)   #只移中心的点
        self.add(d1)   #进场景
        win.play(d1.animate.apply_function_to_position(lambda p: p + RIGHT * 1.6), run_time=0.5)   #只移动自身中心
        pair = VGroup(Dot(color=TEAL, radius=0.13), Dot(color=TEAL, radius=0.13))   #两个子对象
        pair.arrange(RIGHT, buff=0.4).shift(RIGHT * 1.2 + DOWN * 1.6)
        self.add(pair)   #进场景
        win.play(pair.animate.apply_function_to_submobject_positions(lambda p: p + UP * 0.8), run_time=0.5)   #每个子对象中心各移一段
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 5：apply_points_function_about_point ==========================
class PointsFuncDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        ln = Line(LEFT * 1.5, RIGHT * 1.5, color=BLUE)   #一段水平线
        ln.shift(UP * 1.5)
        self.add(ln)   #进场景
        win.play(ln.animate.apply_points_function_about_point(
            lambda pts: pts * 1.6, about_point=ln.get_center()), run_time=0.6)   #成批处理点：绕中心放大 1.6
        win.play(ln.animate.apply_points_function_about_point(
            lambda pts: pts + np.array([0.0, -1.4, 0.0]), about_point=ORIGIN), run_time=0.6)   #批量平移：整体下移
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 6：repeat / reverse_points ====================================
class RepeatRevDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        arc = Arc(radius=1.5, start_angle=0, angle=TAU * 0.7, color=YELLOW)   #不闭合的弧：首尾分明
        mark = Dot(color=RED, radius=0.09).move_to(arc.point_from_proportion(0.25))   #路径 25% 处的标记
        self.add(arc, mark)   #进场景
        arc.reverse_points()   #反转路径方向：起点终点对调（弧的外观不变）
        win.play(mark.animate.move_to(arc.point_from_proportion(0.25)), run_time=0.5)   #25% 处随方向跳到另一端
        print("repeat 前点数 =", len(arc.points))   #反转后的点数
        arc.repeat(2)   #顶点序列重复 2 遍：外观不变
        print("repeat 后点数 =", len(arc.points))   #翻倍
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("rescale", RescaleDemo),
    ("fit", FitDemo),
    ("pose", PoseDemo),
    ("apply", ApplyDemo),
    ("points_func", PointsFuncDemo),
    ("repeat_rev", RepeatRevDemo),
]

PAIRS = [
    ("rescale", ["rescale"]),
    ("fit", ["fit"]),
    ("pose", ["pose"]),
    ("apply", ["apply"]),
    ("points_func", ["points_func"]),
    ("repeat_rev", ["repeat_rev"]),
]

PAGE = "04b-缩放旋转与变形-进阶"


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
