# -*- coding: utf-8 -*-
"""02-摆放位置.md 五个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 02-摆放位置.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的五条样例视频（输出到上一级 assets/）。
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
    Scene, Square, Dot, VGroup, ScreenRectangle,
    BLUE, RED, GREEN, YELLOW, PURPLE, ORANGE, TEAL, WHITE, GREY,
    UP, DOWN, LEFT, RIGHT, UR, DL, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：shift ======================================================
class ShiftDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=BLUE, side_length=1.4, fill_opacity=0.6)   #蓝色方块
        self.add(sq)   #进场景
        win.play(sq.animate.shift(RIGHT * 2.0), run_time=0.5)   #沿一个向量平移：向右 2
        win.play(sq.animate.shift(UP * 1.2, LEFT * 4.0), run_time=0.6)   #传多个向量：内部求和，走向左 4、向上 1.2
        sq.shift(DOWN * 2.4, RIGHT * 1.2)   #不加 “animate” 是瞬间平移：下 2.4 + 右 1.2
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：move_to ====================================================
class MoveToDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        dot = Dot(color=YELLOW, radius=0.12)   #目标点
        dot.move_to(LEFT * 3.0 + UP * 1.6)   #把目标点放到画面左上
        sq = Square(color=RED, side_length=1.2, fill_opacity=0.6)   #要移动的方块
        self.add(dot, sq)   #都进场景
        win.play(sq.animate.move_to(dot), run_time=0.6)   #默认中心对中心
        win.play(sq.animate.move_to(RIGHT * 3.0 + UP * 1.6, aligned_edge=UR), run_time=0.6)   #用自己右上角对到目标点
        win.play(sq.animate.move_to(RIGHT * 3.0 + DOWN * 1.8, coor_mask=np.array([1, 0, 0])), run_time=0.6)   #只对齐 x，y 保持不动
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：next_to ====================================================
class NextToDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        box = Square(color=BLUE, side_length=1.6, fill_opacity=0.6)   #参照物
        self.add(box)   #进场景
        right = Square(color=RED, side_length=0.8).next_to(box, RIGHT, buff=0.3)   #direction / buff：垂直居中贴右侧
        up = Square(color=GREEN, side_length=0.8).next_to(box, UP, buff=0.2)   #direction=UP：水平居中贴上侧
        low = Square(color=ORANGE, side_length=0.8).next_to(box, RIGHT, buff=1.2, aligned_edge=DOWN)   #aligned_edge=DOWN：下边缘对齐，不垂直居中
        duo = VGroup(Square(color=PURPLE, side_length=0.5), Square(color=TEAL, side_length=0.5))   #两个小方块一组
        duo.arrange(DOWN, buff=0.2)   #上下排好
        duo.next_to(box, LEFT, buff=0.3, submobject_to_align=duo[1])   #用自己第二个子对象去对齐
        self.add(right, up, low, duo)   #四个邻居进场景
        win.play(FadeIn(right), FadeIn(up), run_time=0.5)   #右侧、上方的邻居淡入
        win.play(FadeIn(low), FadeIn(duo), run_time=0.5)   #下对齐的、左侧的一组淡入
        ref = VGroup(Square(color=TEAL, side_length=0.6), Square(color=TEAL, side_length=0.6))   #参照组：两个子对象
        ref.arrange(RIGHT, buff=0.2).shift(DOWN * 2.3)   #放到底部
        self.add(ref)   #进场景
        tag = VGroup(Square(color=YELLOW, side_length=0.3), Square(color=WHITE, side_length=0.3))   #两段标记
        tag.arrange(RIGHT, buff=0.1)   #排成一行
        tag.next_to(ref, UP, buff=0.25, index_of_submobject_to_align=1)   #自己和参照物都用第 2 个子对象对齐
        self.add(tag)   #进场景
        win.play(FadeIn(ref), FadeIn(tag), run_time=0.5)   #参照组与标记淡入
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：to_edge / to_corner ========================================
class EdgeCornerDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        frame = ScreenRectangle(height=6.8, color=GREY)   #示意画面边界
        self.add(frame)   #进场景
        top = Square(color=RED, side_length=0.9)   #贴上边的方块
        bottom = Square(color=BLUE, side_length=0.9)   #贴下边的方块
        side = Square(color=GREEN, side_length=0.9)   #贴左边的方块
        corner = Square(color=YELLOW, side_length=0.9)   #贴右上角的方块
        top.to_edge(UP, buff=0.3)   #贴上边，留白 0.3
        bottom.to_edge(DOWN, buff=0.3)   #贴下边
        side.shift(UP * 1.2)   #先往上挪一点
        side.to_edge(LEFT, buff=0.3)   #贴左边：y 坐标不受影响
        corner.to_corner(UR, buff=0.5)   #贴右上角，留白 0.5
        self.add(top, bottom, side, corner)   #都进场景
        win.play(FadeIn(top), FadeIn(bottom), FadeIn(side), FadeIn(corner), run_time=0.6)   #四个方块淡入
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 5：center / align_to ==========================================
class CenterAlignDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=BLUE, side_length=1.2, fill_opacity=0.6)   #蓝色方块
        sq.shift(LEFT * 3.2 + UP * 1.4)   #先挪到左上
        self.add(sq)   #进场景
        win.play(sq.animate.center(), run_time=0.6)   #center：回到原点 (0, 0, 0)
        big = Square(color=RED, side_length=2.0, fill_opacity=0.4)   #参照大方块
        big.shift(RIGHT * 3.2)   #放右边
        small = Square(color=YELLOW, side_length=1.0)   #待对齐的小方块
        small.shift(RIGHT * 3.2 + UP * 1.8)   #先放高一点
        self.add(big, small)   #进场景
        win.play(small.animate.align_to(big, UP), run_time=0.6)   #align_to：上边缘齐平，x 不动
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("shift", ShiftDemo),
    ("move_to", MoveToDemo),
    ("next_to", NextToDemo),
    ("edge_corner", EdgeCornerDemo),
    ("center_align", CenterAlignDemo),
]

PAIRS = [
    ("shift", ["shift"]),
    ("move_to", ["move_to"]),
    ("next_to", ["next_to"]),
    ("edge_corner", ["edge_corner"]),
    ("center_align", ["center_align"]),
]

PAGE = "02-摆放位置"


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
