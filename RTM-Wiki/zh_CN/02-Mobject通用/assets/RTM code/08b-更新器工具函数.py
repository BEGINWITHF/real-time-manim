# -*- coding: utf-8 -*-
"""08b-更新器工具函数.md 四个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 08b-更新器工具函数.py <片段名>...
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
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    Scene, Square, Triangle, Line, Dot, Text, ValueTracker,
    BLUE, RED, GREEN, YELLOW, GREY, ORANGE,
    UP, DOWN, LEFT, RIGHT, PI, TAU, FadeIn, Rotate,
    always_redraw, always, f_always, always_shift, always_rotate,
    turn_animation_into_updater, cycle_animation, assert_is_mobject_method,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：always_redraw =============================================
class AlwaysRedrawDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        alpha = ValueTracker(0.0)   #数值追踪器
        track = Line(LEFT * 3.0, RIGHT * 3.0, color=GREY)   #一段轨道
        self.add(track)   #进场景
        bead = always_redraw(lambda: Dot(color=RED, radius=0.12).move_to(LEFT * 3.0 + alpha.get_value() * RIGHT))   #每帧按当前值重画圆点
        self.add(bead)   #进场景（返回的就是挂好 updater 的对象）
        win.play(alpha.animate.set_value(6.0), run_time=1.0)   #驱动 tracker：圆点沿轨道匀速走
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：always / f_always（模块级函数）============================
class AlwaysFnDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=BLUE, side_length=1.2).shift(LEFT * 3.0)   #蓝色方块
        self.add(sq)   #进场景
        tag = Text("always", font_size=24, color=YELLOW)   #上方标签
        always(tag.next_to, sq, UP, buff=0.3)   #always：参数挂载时求值一次（引用照用）
        self.add(tag)   #进场景
        tag2 = Text("f_always", font_size=24, color=GREEN)   #下方标签
        f_always(tag2.next_to, lambda: sq, lambda: DOWN, buff=0.3)   #f_always：参数生成器每帧重求值
        self.add(tag2)   #进场景
        win.play(sq.animate.shift(RIGHT * 2.5), run_time=0.8)   #两个标签一上一下全程跟随
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：always_shift / always_rotate ==============================
class AlwaysShiftRotateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        tri = Triangle(color=GREEN).set_fill(GREEN, opacity=1).scale(0.8).shift(DOWN * 1.5 + LEFT * 3.0)   #绿色三角
        self.add(tri)   #进场景
        assert_is_mobject_method(tri.shift)   #入参校验辅助：确认是 Mobject 上的绑定方法（返回 None）
        print("assert_is_mobject_method -> None")
        always_shift(tri, direction=RIGHT, rate=1.0)   #匀速右移：每秒 1.0 单位
        always_rotate(tri, rate=PI / 2)   #匀速自转：每秒 90°
        win.play(Wait(1.2))   #边走边转
        tri.clear_updaters()   #两个 updater 一起停
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：turn_animation_into_updater / cycle_animation =============
class AnimUpdaterDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=BLUE, side_length=1.0).shift(LEFT * 3.5 + UP * 1.5)   #左边：转一圈就结束
        self.add(sq)   #进场景
        turn_animation_into_updater(Rotate(sq, angle=TAU), cycle=False, delay=0)   #动画变 updater：随场景时间推进
        win.play(Wait(0.9))   #看它自己转完一圈
        sq2 = Square(color=ORANGE, side_length=1.0).shift(RIGHT * 3.5 + UP * 1.5)   #右边：无限循环
        self.add(sq2)   #进场景
        cycle_animation(Rotate(sq2, angle=TAU))   #cycle=True 的简写：永远转下去
        win.play(Wait(0.9))   #看它一直转
        sq2.clear_updaters()   #停掉
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("always_redraw", AlwaysRedrawDemo),
    ("always_fn", AlwaysFnDemo),
    ("always_shift_rotate", AlwaysShiftRotateDemo),
    ("anim_updater", AnimUpdaterDemo),
]

PAIRS = [
    ("always_redraw", ["always_redraw"]),
    ("always_fn", ["always_fn"]),
    ("always_shift_rotate", ["always_shift_rotate"]),
    ("anim_updater", ["anim_updater"]),
]

PAGE = "08b-更新器工具函数"


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
