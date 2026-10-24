# -*- coding: utf-8 -*-
"""02-三维表面.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 02-三维表面.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的三条样例视频（输出到上一级 assets/）；
python 02-三维表面.py --concat-only 只拼接不渲染。
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

import numpy as np

from real_time_manim import (
    ThreeDScene, Surface, Sphere, Torus, Text,
    GREEN, GREY_B, RED, YELLOW, PI, TAU,
    UP, DOWN, LEFT, RIGHT, DEGREES,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：Surface 的参数方程 / resolution / 棋盘格配色 =================
class SurfaceDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 内部会调 self.play，先接到窗口上
        title = Text("02-surface", font_size=34, color=YELLOW).to_edge(UP)   #样例标题
        self.add_fixed_in_frame_mobjects(title)   #标题钉在屏幕上
        surf = Surface(lambda u, v: [v * np.cos(u), v * np.sin(u), u * 0.5],   #螺旋坡道的参数方程
                       u_range=(0, TAU), v_range=(0.3, 1.8),   #u 转一整圈、v 取内外半径
                       resolution=(16, 8))   #低分辨率：控渲染时长，面片也看得清
        self.add(surf)   #把曲面放进场景
        self.set_camera_orientation(phi=60 * DEGREES, theta=-60 * DEGREES)   #摆好斜视角
        win.play(Wait(0.8))   #停 0.8s 看清默认蓝棋盘格
        surf.set_fill_by_checkerboard([GREEN, YELLOW], opacity=0.85)   #方法：原地换棋盘格配色
        win.play(Wait(0.6))   #停 0.6s 看换色效果
        self.move_camera(theta=-150 * DEGREES, run_time=1.2)   #带动画环绕 90°
        win.play(Wait(0.4))   #停 0.4s 收工
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：Sphere 的 v_range 裁球冠 ====================================
class SphereDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 内部会调 self.play，先接到窗口上
        title = Text("02-sphere", font_size=34, color=YELLOW).to_edge(UP)   #样例标题
        self.add_fixed_in_frame_mobjects(title)   #标题钉在屏幕上
        full = Sphere(radius=1, resolution=(24, 12))   #完整球面：u 全圈、v 从北极到南极
        full.shift(LEFT * 2.5)   #摆在左侧
        half = Sphere(radius=1, resolution=(24, 12), v_range=(0, PI / 2))   #v_range 裁出上半球
        half.set_color(RED)   #换色：Surface 子类的 “color=” 参数不生效，要构造后 set_color
        half.shift(RIGHT * 2.5)   #摆在右侧
        tag1 = Text("v_range=(0,PI)", font_size=24, color=GREY_B).next_to(full, DOWN)   #左下角标注
        tag2 = Text("v_range=(0,PI/2)", font_size=24, color=GREY_B).next_to(half, DOWN)   #右下角标注
        self.add(full, half, tag1, tag2)   #把两个球面和标签放进场景
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)   #摆好斜视角
        win.play(Wait(0.8))   #停 0.8s 看清球冠形状
        self.move_camera(theta=-135 * DEGREES, run_time=1.2)   #带动画环绕 90°
        win.play(Wait(0.4))   #停 0.4s 收工
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：Torus 的半径与 v_range 裁半环管 ============================
class TorusDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 内部会调 self.play，先接到窗口上
        title = Text("02-torus", font_size=34, color=YELLOW).to_edge(UP)   #样例标题
        self.add_fixed_in_frame_mobjects(title)   #标题钉在屏幕上
        full = Torus(major_radius=1.6, minor_radius=0.5)   #默认整环：环半径 1.6、管半径 0.5
        full.shift(LEFT * 2.5)   #摆在左侧
        half = Torus(major_radius=1.6, minor_radius=0.5, v_range=(0, PI))   #v_range 裁出半环管
        half.set_color(GREEN)   #换色：Surface 子类的 “color=” 参数不生效，要构造后 set_color
        half.shift(RIGHT * 2.5)   #摆在右侧
        tag1 = Text("full ring", font_size=24, color=GREY_B).next_to(full, DOWN)   #左下角标注
        tag2 = Text("v_range=(0,PI)", font_size=24, color=GREY_B).next_to(half, DOWN)   #右下角标注
        self.add(full, half, tag1, tag2)   #把两个圆环面和标签放进场景
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES)   #摆好斜视角
        win.play(Wait(0.8))   #停 0.8s 看清半环管的剖面
        self.move_camera(theta=-135 * DEGREES, run_time=1.2)   #带动画环绕 90°
        win.play(Wait(0.4))   #停 0.4s 收工
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("surface", SurfaceDemo),
    ("sphere", SphereDemo),
    ("torus", TorusDemo),
]

PAIRS = [
    ("surface", ["surface"]),
    ("sphere", ["sphere"]),
    ("torus", ["torus"]),
]

PAGE = "02-三维表面"


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
    only = set(a for a in sys.argv[1:] if not a.startswith("--"))
    if "--concat-only" not in sys.argv:
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

    for out_name, names in PAIRS:
        if only and out_name not in only:
            continue
        dst = os.path.join(ASSETS, "RTM output", "%s-%s.mp4" % (PAGE, out_name))
        concat(names, dst)
        print("concat ->", dst, os.path.getsize(dst), "bytes")
