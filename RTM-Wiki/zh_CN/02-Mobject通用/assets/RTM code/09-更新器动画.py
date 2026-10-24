# -*- coding: utf-8 -*-
"""09-更新器动画.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 09-更新器动画.py <片段名>...
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
    Scene, Square, Circle, Dot, DecimalNumber,
    BLUE, RED, GREEN, YELLOW, PURPLE, WHITE,
    UP, DOWN, LEFT, RIGHT, FadeIn, interpolate_color,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene
from real_time_manim import UpdateFromFunc, UpdateFromAlphaFunc, MaintainPositionRelativeTo


# ===== 样例 1：UpdateFromFunc ============================================
class UpdateFromFuncDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        dot = Dot(color=YELLOW, radius=0.12).shift(LEFT * 4.0)   #黄点
        lab = DecimalNumber(0, num_decimal_places=2, color=WHITE).scale(0.7)   #读数标签
        lab.to_edge(UP, buff=0.5)   #先放到顶部
        self.add(dot, lab)   #进场景

        def follow(m):   #动画期间每帧被调用：标签贴到点上方并显示点的 x 坐标
            m.move_to(dot.get_center() + UP * 1.2)
            m.set_value(round(float(dot.get_x()), 2))

        win.play(dot.animate.shift(RIGHT * 8.0), run_time=1.2)   #点横穿画面（标签还没挂）
        win.play(UpdateFromFunc(lab, follow), dot.animate.shift(LEFT * 8.0), run_time=1.2)   #动画的整个时长里每帧驱动标签
        win.play(Wait(0.3))   #进行 0.3s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：UpdateFromAlphaFunc =======================================
class UpdateAlphaDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=BLUE, side_length=1.2, fill_opacity=0.7)   #蓝色方块
        self.add(sq)   #进场景
        start = sq.get_center().copy()   #记住起点

        def morph(m, alpha):   #按进度插值：颜色蓝→红、向右移动
            m.set_color(interpolate_color(BLUE, RED, alpha))
            m.move_to(start + alpha * RIGHT * 3.0)

        win.play(UpdateFromAlphaFunc(sq, morph, suspend_mobject_updating=False), run_time=1.0)   #alpha 经 rate_func 处理后 0→1
        win.play(Wait(0.3))   #进行 0.3s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：MaintainPositionRelativeTo ================================
class MaintainDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        ref = Square(color=GREEN, side_length=1.0, fill_opacity=0.6).shift(LEFT * 3.5)   #参照方块
        sat = Circle(color=PURPLE, radius=0.35)   #卫星
        sat.next_to(ref, UP, buff=0.25)   #先贴在参照上方：这就是要保持的相对位置
        self.add(ref, sat)   #进场景
        win.play(MaintainPositionRelativeTo(sat, ref), ref.animate.shift(RIGHT * 7.0), run_time=1.2)   #相对位置不变：一起走
        win.play(Wait(0.3))   #进行 0.3s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("update_func", UpdateFromFuncDemo),
    ("update_alpha", UpdateAlphaDemo),
    ("maintain", MaintainDemo),
]

PAIRS = [
    ("update_func", ["update_func"]),
    ("update_alpha", ["update_alpha"]),
    ("maintain", ["maintain"]),
]

PAGE = "09-更新器动画"


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
