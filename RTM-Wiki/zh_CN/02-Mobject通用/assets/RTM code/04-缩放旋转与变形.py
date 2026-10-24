# -*- coding: utf-8 -*-
"""04-缩放旋转与变形.md 四个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 04-缩放旋转与变形.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的四条样例视频（输出到上一级 assets/）。
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
    Scene, Square, Rectangle, Line, Arrow, Dot,
    BLUE, GREEN, YELLOW, PURPLE, RED,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    DEGREES, PI, FadeIn, Rotate,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：scale ======================================================
class ScaleDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=BLUE, side_length=1.6, fill_opacity=0.5)   #蓝色方块
        anchor = Dot(color=RED, radius=0.08).move_to(RIGHT * 2.5)   #缩放基准点的标记
        self.add(sq, anchor)   #进场景
        win.play(sq.animate.scale(1.6), run_time=0.6)   #默认绕自身中心放大
        win.play(sq.animate.scale(0.6, about_point=RIGHT * 2.5), run_time=0.6)   #绕红点缩放：红点位置不变
        win.play(sq.animate.scale(1.8, about_edge=DOWN), run_time=0.6)   #绕下边缘缩放：底边不动
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：rotate / rotate_about_origin ===============================
class RotateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        rect = Rectangle(width=2.4, height=1.0, color=GREEN, fill_opacity=0.5)   #长方形：转起来看得清
        self.add(rect)   #进场景
        win.play(rect.animate.rotate(90 * DEGREES), run_time=0.6)   #绕自身中心转 90°（弧度 = 90*DEGREES）
        win.play(rect.animate.rotate(60 * DEGREES, about_point=LEFT * 2), run_time=0.6)   #绕指定点转
        win.play(Rotate(rect, angle=180 * DEGREES), run_time=0.8)   #“animate.rotate” 只是插值；连续转要用 Rotate 动画
        win.play(rect.animate.rotate_about_origin(90 * DEGREES), run_time=0.6)   #绕场景原点 (0, 0, 0) 旋转
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：flip =======================================================
class FlipDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        s = Line(LEFT * 2, RIGHT * 2 + UP * 1.2, color=YELLOW)   #右高左低的斜线：镜像看得出来
        self.add(s)   #进场景
        win.play(s.animate.flip(axis=UP), run_time=0.6)   #绕竖直轴转 180° = 左右镜像
        win.play(s.animate.flip(axis=RIGHT, about_point=RIGHT * 2), run_time=0.6)   #绕水平轴转 180° = 上下镜像，基准点在右
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：stretch / stretch_about_point ==============================
class StretchDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=PURPLE, side_length=1.4, fill_opacity=0.5)   #紫色方块
        self.add(sq)   #进场景
        win.play(sq.animate.stretch(2.2, 0), run_time=0.6)   #只拉宽：dim=0
        win.play(sq.animate.stretch(0.5, 1, about_point=ORIGIN), run_time=0.6)   #dim=1 压扁，绕原点
        win.play(sq.animate.stretch_about_point(1.8, 0, sq.get_left()), run_time=0.6)   #左端不动向右拉
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("scale", ScaleDemo),
    ("rotate", RotateDemo),
    ("flip", FlipDemo),
    ("stretch", StretchDemo),
]

PAIRS = [
    ("scale", ["scale"]),
    ("rotate", ["rotate"]),
    ("flip", ["flip"]),
    ("stretch", ["stretch"]),
]

PAGE = "04-缩放旋转与变形"


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
