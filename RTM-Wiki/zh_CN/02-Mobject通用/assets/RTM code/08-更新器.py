# -*- coding: utf-8 -*-
"""08-更新器.md 五个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 08-更新器.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的五条样例视频（输出到上一级 assets/）。
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
    Scene, Square, Dot, Text, DecimalNumber,
    BLUE, RED, GREEN, YELLOW,
    UP, DOWN, LEFT, RIGHT, DEGREES, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：add_updater ===============================================
class AddUpdaterDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=BLUE, side_length=1.0, fill_opacity=0.6).shift(LEFT * 3.5)   #蓝色方块
        self.add(sq)   #进场景（带 updater 的对象必须进场景才会被驱动）
        spin = lambda m, dt: m.rotate(dt * 90 * DEGREES)   #时间型 f(mob, dt)：每秒转 90°
        sq.add_updater(spin)   #挂上更新器
        lbl = DecimalNumber(0, num_decimal_places=2, color=YELLOW).scale(0.7).shift(LEFT * 3.5 + DOWN * 1.6)   #读数标签
        val = lambda d: d.set_value(round(float(sq.get_width()), 2))   #非时间型 f(mob)：每帧读方块包围盒宽度
        pos = lambda d: d.next_to(sq, DOWN, buff=0.3)   #非时间型：标签跟着方块走
        lbl.add_updater(val)   #默认追加到列表末尾
        lbl.add_updater(pos, index=0, call_updater=True)   #插到开头，且挂载时立即执行一次
        self.add(lbl)   #标签进场景
        win.play(Wait(1.0))   #停留 1 秒：方块持续旋转、数字持续刷新
        win.play(sq.animate.shift(RIGHT * 2.0), run_time=0.5)   #动画期间 updater 照常驱动
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：remove_updater / clear_updaters ============================
class RemoveClearDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=GREEN, side_length=1.0, fill_opacity=0.6).shift(LEFT * 3.0)   #绿色方块
        spin = lambda m, dt: m.rotate(dt * 120 * DEGREES)   #命名保存：移除时要传同一个函数对象
        sq.add_updater(spin)   #挂上
        self.add(sq)   #进场景
        print("挂载后 updaters =", len(sq.get_updaters()))   #1
        win.play(Wait(0.6))   #转起来
        sq.remove_updater(spin)   #按同一个函数对象移除
        print("remove 后 updaters =", len(sq.get_updaters()))   #0
        sq.add_updater(lambda m, dt: m.shift(DOWN * dt))   #再挂一个匿名函数：每秒下落 1
        win.play(Wait(0.5))   #往下掉
        sq.clear_updaters()   #清空全部 updater（递归）
        print("clear 后 updaters =", len(sq.get_updaters()))   #0
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：suspend_updating / resume_updating / update ===============
class SuspendDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=RED, side_length=1.0, fill_opacity=0.6).shift(UP * 1.5)   #红色方块
        sq.add_updater(lambda m, dt: m.rotate(dt * 120 * DEGREES))   #每秒转 120°
        self.add(sq)   #进场景
        win.play(Wait(0.5))   #转起来
        sq.suspend_updating(recursive=True)   #暂停：函数还在列表里，只是不执行
        win.play(Wait(0.5))   #停转
        sq.resume_updating(recursive=True)   #恢复：立即以 dt=0 跑一遍
        win.play(Wait(0.3))   #又转起来
        sq.update(dt=0, recursive=True)   #手动触发一次（渲染循环之外才需要）
        win.play(Wait(0.3))   #进行 0.3s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：always（属性）=============================================
class AlwaysDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=BLUE, side_length=1.2, fill_opacity=0.6).shift(LEFT * 3.0)   #蓝色方块
        self.add(sq)   #进场景
        tag = Text("tag", font_size=28, color=YELLOW)   #跟随标签
        tag.always.next_to(sq, UP, buff=0.3)   #语法糖：等价 add_updater(..., call_updater=True)
        self.add(tag)   #进场景
        win.play(sq.animate.shift(RIGHT * 2.5), run_time=0.8)   #标签全程跟随
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 5：查询与 match_updaters =====================================
class QueryMatchDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=GREEN, side_length=1.0, fill_opacity=0.6).shift(LEFT * 3.0)   #绿色方块
        spin = lambda m, dt: m.rotate(dt * 90 * DEGREES)   #命名保存
        sq.add_updater(spin)   #挂上
        self.add(sq)   #进场景
        print("get_updaters =", len(sq.get_updaters()))   #1
        print("get_time_based_updaters =", len(sq.get_time_based_updaters()))   #1
        print("has_time_based_updater =", sq.has_time_based_updater())   #True
        d2 = Dot(color=RED, radius=0.1).shift(RIGHT * 3.0)   #红点
        d2.match_updaters(sq)   #照搬 sq 的 updater 列表（只搬 sq 自己的）
        self.add(d2)   #进场景
        print("d2 updaters =", len(d2.get_updaters()))   #1
        win.play(Wait(0.8))   #两个都在转
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("add_updater", AddUpdaterDemo),
    ("remove_clear", RemoveClearDemo),
    ("suspend", SuspendDemo),
    ("always", AlwaysDemo),
    ("query_match", QueryMatchDemo),
]

PAIRS = [
    ("add_updater", ["add_updater"]),
    ("remove_clear", ["remove_clear"]),
    ("suspend", ["suspend"]),
    ("always", ["always"]),
    ("query_match", ["query_match"]),
]

PAGE = "08-更新器"


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
