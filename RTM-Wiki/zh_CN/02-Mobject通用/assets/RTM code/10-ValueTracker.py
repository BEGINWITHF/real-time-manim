# -*- coding: utf-8 -*-
"""10-ValueTracker.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 10-ValueTracker.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的三条样例视频（输出到上一级 assets/）。
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
    Scene, Dot, DecimalNumber, ValueTracker, ComplexValueTracker,
    BLUE, YELLOW, UP, DOWN, LEFT, RIGHT, FadeIn, straight_path,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：构造与 set_value / increment_value ========================
class BasicDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        tracker = ValueTracker(0.0)   #初始值 0
        lbl = DecimalNumber(0, num_decimal_places=2, color=YELLOW).scale(0.8).to_edge(UP, buff=0.5)   #读数标签
        lbl.add_updater(lambda d: d.set_value(round(float(tracker.get_value()), 2)))   #每帧读值显示
        self.add(lbl, tracker)   #tracker 必须进场景才会被驱动
        win.play(tracker.animate.set_value(5.0), run_time=0.8)   #动画式改值：0 → 5
        win.play(tracker.animate.increment_value(-2.0), run_time=0.6)   #动画式增减：-2
        tracker += 2.0   #原地立即改值（+= 原地版本）
        print("after += :", tracker.get_value())   #5.0
        print("(tracker * 3).get_value() =", (tracker * 3).get_value())   #* → 新对象，原对象不变
        print("- / / / // / % / ** =", (tracker - 1).get_value(), (tracker / 2).get_value(), (tracker // 2).get_value(), (tracker % 2).get_value(), (tracker ** 2).get_value())   #各算术运算符 → 新 ValueTracker
        print("bool(tracker) =", bool(tracker))   #bool 等价于 bool(get_value())
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：interpolate ===============================================
class InterpolateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        tracker = ValueTracker(0.0)   #数值追踪器
        lbl = DecimalNumber(0, num_decimal_places=2, color=YELLOW).scale(0.8).to_edge(UP, buff=0.5)   #读数标签
        lbl.add_updater(lambda d: d.set_value(round(float(tracker.get_value()), 2)))   #每帧读值显示
        self.add(lbl, tracker)   #进场景
        win.play(tracker.animate.set_value(4.0), run_time=0.6)   #先动画到 4.0
        tracker.interpolate(ValueTracker(0.0), ValueTracker(2.0), 0.5, path_func=straight_path())   #直接取 0 与 2 在 0.5 处的插值（瞬间）
        print("after interpolate =", tracker.get_value())   #1.0
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：ComplexValueTracker =======================================
class ComplexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        ct = ComplexValueTracker(-2 + 1j)   #复数追踪器：值内部存成 [实部, 虚部, 0]
        cdot = Dot(color=BLUE, radius=0.12)   #蓝点
        cdot.add_updater(lambda x: x.move_to(ct.points))   #点直接跟着内部坐标走
        self.add(cdot, ct)   #进场景
        win.play(ct.animate.set_value(3 + 2j), run_time=1.0)   #动画式改值：点从 (-2, 1) 走到 (3, 2)
        cdot.clear_updaters()   #停掉跟随
        print("ct.get_value() =", ct.get_value())   #3+2j
        #无法演示：ct * 1j / ct + 1 等算术运算
        #    TypeError: float() argument must be a string or a real number, not 'complex'
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("basic", BasicDemo),
    ("interpolate", InterpolateDemo),
    ("complex", ComplexDemo),
]

PAIRS = [
    ("basic", ["basic"]),
    ("interpolate", ["interpolate"]),
    ("complex", ["complex"]),
]

PAGE = "10-ValueTracker"


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
