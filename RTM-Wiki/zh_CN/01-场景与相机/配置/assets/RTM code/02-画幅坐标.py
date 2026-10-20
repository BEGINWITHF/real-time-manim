# -*- coding: utf-8 -*-
"""02-画幅坐标.md 样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 02-画幅坐标.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的对比视频。
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
ASSETS = os.path.dirname(HERE)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    config,
    Scene, Square, Circle, Dot, Text, VGroup,
    WHITE, RED, GREEN, YELLOW,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, Create,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：默认画幅 ====================================================
class FrameLayoutDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        edge_x = 14.222222 / 2   #画面右边缘的 x：= “frame_width” / 2 = “frame_x_radius”
        edge_y = 8.0 / 2   #画面上边缘的 y：= “frame_height” / 2 = “frame_y_radius”
        label = Text("frame_width=14.222  frame_height=8.0", font_size=34,
                     color=WHITE).to_edge(UP, buff=0.3)   #上屏标注画幅尺寸
        corners = VGroup(*[
            Dot(color=RED, radius=0.1).move_to([sx * (edge_x - 0.25), sy * (edge_y - 0.25), 0])
            for sx in (-1, 1) for sy in (-1, 1)])   #四角各摆一个红点：画幅的四个角
        sq = Square(side_length=1.6, color=YELLOW).set_stroke(width=4).shift(LEFT * 1.2)   #正方形：画幅没变形的证据
        circ = Circle(radius=0.8, color=GREEN).shift(RIGHT * 1.2)   #圆形：同上
        self.add(label)   #把标签放进场景
        win.play(FadeIn(corners), run_time=0.6)   #四个角的红点淡入
        win.play(Create(sq), Create(circ), run_time=0.8)   #画出正方形和圆形
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：改写画幅（两引擎行为不同）===================================
class FrameOverrideDemo(Scene):
    def __init__(self, **kwargs):
        self._saved = (config.frame_x_radius, config.frame_y_radius)   #先记住默认的两个半径
        config.frame_x_radius = 3.555   #改写 “frame_x_radius”：画面宽变成 7.11
        config.frame_y_radius = 2.0     #改写 “frame_y_radius”：画面高变成 4.0
        super().__init__(**kwargs)   #相机在这里构造，CE 会读走改过的画幅

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        label = Text("frame_x_radius=3.555  frame_y_radius=2.0", font_size=34,
                     color=WHITE).to_edge(UP, buff=0.3)   #上屏标注改写后的半径
        corners = VGroup(*[
            Dot(color=RED, radius=0.1).move_to([sx * (3.555 - 0.25), sy * (2.0 - 0.25), 0])
            for sx in (-1, 1) for sy in (-1, 1)])   #四角红点按改写后的画幅摆放
        sq = Square(side_length=1.6, color=YELLOW).set_stroke(width=4).shift(LEFT * 1.2)   #正方形：同上一份样例
        circ = Circle(radius=0.8, color=GREEN).shift(RIGHT * 1.2)   #圆形：同上一份样例
        self.add(label)   #把标签放进场景
        win.play(FadeIn(corners), run_time=0.6)   #四个角的红点淡入
        win.play(Create(sq), Create(circ), run_time=0.8)   #画出正方形和圆形
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口
        config.frame_x_radius, config.frame_y_radius = self._saved   #还原默认值，别影响后面的样例


# ===== 样例 3：四边中点 ====================================================
class EdgePointsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        edge_x = 14.222222 / 2   #画面右边缘的 x：“right_side” 的 x 坐标
        edge_y = 8.0 / 2   #画面上边缘的 y：“top” 的 y 坐标
        pts = VGroup(
            Dot(color=RED, radius=0.12).move_to([0, edge_y - 0.3, 0]),   #top：上边中点
            Dot(color=RED, radius=0.12).move_to([edge_x - 0.3, 0, 0]),   #right_side：右边中点
            Dot(color=RED, radius=0.12).move_to([0, -edge_y + 0.3, 0]),   #bottom：下边中点
            Dot(color=RED, radius=0.12).move_to([-edge_x + 0.3, 0, 0]),   #left_side：左边中点
        )
        names = VGroup(
            Text("top", font_size=28, color=YELLOW).next_to(pts[0], DOWN, buff=0.15),
            Text("right_side", font_size=28, color=YELLOW).next_to(pts[1], LEFT, buff=0.25),
            Text("bottom", font_size=28, color=YELLOW).next_to(pts[2], UP, buff=0.15),
            Text("left_side", font_size=28, color=YELLOW).next_to(pts[3], RIGHT, buff=0.25),
        )
        walker = Dot(color=WHITE, radius=0.18).move_to(pts[3])   #游标：从 “left_side” 出发
        self.add(pts, names, walker)   #把四个边点、四行名字和游标放进场景
        win.play(FadeIn(pts), FadeIn(names), run_time=0.6)   #四个边点和名字淡入
        win.play(walker.animate.move_to(pts[0]), run_time=0.5)   #游标走到 “top”
        win.play(walker.animate.move_to(pts[1]), run_time=0.5)   #游标走到 “right_side”
        win.play(walker.animate.move_to(pts[2]), run_time=0.5)   #游标走到 “bottom”
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("frame_layout", FrameLayoutDemo),
    ("frame_override", FrameOverrideDemo),
    ("edge_points", EdgePointsDemo),
]

OUTPUTS = [
    ("02-画幅坐标-frame_layout", ["frame_layout"]),
    ("02-画幅坐标-frame_override", ["frame_override"]),
    ("02-画幅坐标-edge_points", ["edge_points"]),
]


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
        for out_name, names in OUTPUTS:
            dst = os.path.join(ASSETS, "RTM output", out_name + ".mp4")
            concat(names, dst)
            print("concat ->", dst, os.path.getsize(dst), "bytes")
