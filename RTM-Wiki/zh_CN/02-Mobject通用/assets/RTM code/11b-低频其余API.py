# -*- coding: utf-8 -*-
"""11b-低频其余API.md 三个样例的完整源码（与页面里的代码块逐字一致）。

get_image / show / save_image 与 mobject.utils 三个工厂函数无法出片（见页面说明），
因此没有对应样例类。

跑法：python 11b-低频其余API.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的三条样例视频（输出到上一级 assets/）。
"""
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

from real_time_manim import (
    Scene, Group, VGroup, Square, Circle, Line, Dot,
    BLUE, RED, GREEN, YELLOW, PURPLE, ORANGE, GREY,
    UP, DOWN, LEFT, RIGHT, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：sort / shuffle / invert ===================================
class SortShuffleInvertDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        colors = (RED, BLUE, GREEN, YELLOW, PURPLE)   #五个颜色
        spots = (LEFT * 3.5 + UP * 1.4, RIGHT * 2.0 + UP * 0.6, LEFT * 1.0 + DOWN * 1.2, RIGHT * 3.2 + DOWN * 1.6, LEFT * 2.4)   #五个互不相同的散乱位置
        v = VGroup(*[Square(color=c, side_length=0.8).shift(p) for c, p in zip(colors, spots)])   #先散乱摆放
        self.add(v)   #进场景
        win.play(Wait(0.4))   #看清初始散乱位置
        v.sort()   #sort：按当前中心 x 从左到右改列表顺序
        win.play(v.animate.arrange(RIGHT, buff=0.3), run_time=0.5)   #按列表顺序排成一行：颜色按位置排好
        v.invert(recursive=False)   #invert：反转列表顺序
        win.play(v.animate.arrange(RIGHT, buff=0.3), run_time=0.5)   #顺序整个反过来
        random.seed(7)   #固定随机种子，便于复现
        v.shuffle(recursive=False)   #shuffle：随机打乱
        win.play(v.animate.arrange(RIGHT, buff=0.3), run_time=0.5)   #随机顺序
        v.sort(submob_func=lambda m: str(m.color))   #submob_func 优先级更高：按颜色名排序
        win.play(v.animate.arrange(RIGHT, buff=0.3), run_time=0.5)   #颜色名从 A 到 Z
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：apply_to_family ===========================================
class ApplyFamilyDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        v = VGroup(*[Square(color=BLUE, side_length=0.9) for _ in range(3)])   #三个方块
        v.arrange(RIGHT, buff=0.3).shift(UP * 1.5)
        self.add(v)   #进场景
        v.apply_to_family(lambda m: m.set_stroke(width=6))   #对每个有顶点的成员调用一次
        win.play(FadeIn(v), run_time=0.4)   #粗描边的方块淡入
        g = Group(Circle(radius=0.45), Circle(radius=0.45)).arrange(RIGHT, buff=0.4).shift(DOWN * 1.5)   #两个圆
        self.add(g)   #进场景
        g.apply_to_family(lambda m: m.set_stroke(color=RED, width=6))   #对圆同样生效
        win.play(FadeIn(g), run_time=0.4)   #红粗描边的圆淡入
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：路径取点一族 ==============================================
class PathDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        line = Line(LEFT * 3.5, RIGHT * 0.5, color=YELLOW).shift(UP * 1.5)   #一段线
        self.add(line)   #进场景
        print("get_start =", line.get_start().round(2))   #第一个顶点
        print("get_end =", line.get_end().round(2))   #最后一个顶点
        p = line.point_from_proportion(0.25)   #沿路径 25% 处
        self.add(Dot(color=RED, radius=0.09).move_to(p))   #打点标出来
        print("point_from_proportion(0.25) =", p.round(2))
        pieces = line.get_pieces(4)   #切成 4 段
        pieces.set_color_by_gradient(RED, BLUE)
        self.add(pieces)   #进场景
        win.play(FadeIn(pieces), run_time=0.5)   #四段渐变色显示
        c = Circle(radius=0.9, color=ORANGE).shift(RIGHT * 3.0 + DOWN * 1.2)   #圆：曲线上的取点更直观
        self.add(c)   #进场景
        q = c.point_from_proportion(0.25)
        print("circle 25% =", q.round(2))
        print("proportion_from_point =", round(c.proportion_from_point(q), 4))   #反算比例
        win.play(FadeIn(c), run_time=0.4)   #圆淡入
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("sort_shuffle_invert", SortShuffleInvertDemo),
    ("apply_family", ApplyFamilyDemo),
    ("path", PathDemo),
]

PAIRS = [
    ("sort_shuffle_invert", ["sort_shuffle_invert"]),
    ("apply_family", ["apply_family"]),
    ("path", ["path"]),
]

PAGE = "11b-低频其余API"


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
