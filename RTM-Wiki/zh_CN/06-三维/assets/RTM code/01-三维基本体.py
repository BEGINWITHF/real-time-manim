# -*- coding: utf-8 -*-
"""01-三维基本体.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 01-三维基本体.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的三条样例视频（输出到上一级 assets/）；
python 01-三维基本体.py --concat-only 只拼接不渲染。
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
    ThreeDScene, Cube, Prism, Dot3D, Text,
    BLUE, GREEN, GREY_B, RED, YELLOW,
    UP, DOWN, LEFT, RIGHT, UR, DEGREES,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：Cube 的边长 / 颜色 / 不透明度 / 描边 =========================
class CubeDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 内部会调 self.play，先接到窗口上
        title = Text("01-cube", font_size=34, color=YELLOW).to_edge(UP)   #样例标题
        self.add_fixed_in_frame_mobjects(title)   #标题钉在屏幕上，视角怎么转都正对观众
        a = Cube(side_length=2, fill_opacity=0.75, fill_color=BLUE)   #默认参数：边长 2、半透明蓝、无描边
        b = Cube(side_length=1.2, fill_color=GREEN, fill_opacity=1.0, stroke_width=6)   #实心绿、描边加粗
        b.next_to(a, RIGHT, buff=1.2)   #摆在默认立方体右边
        tag1 = Text("default", font_size=26, color=GREY_B).next_to(a, DOWN)   #左下角标注
        tag2 = Text("solid + stroke", font_size=26, color=GREY_B).next_to(b, DOWN)   #右下角标注
        self.add(a, b, tag1, tag2)   #把两个立方体和标签放进场景
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)   #摆好斜视角
        win.play(Wait(0.8))   #停 0.8s 看清立体效果
        self.move_camera(theta=-135 * DEGREES, run_time=1.4)   #带动画环绕 90°，看到另一侧
        win.play(Wait(0.4))   #停 0.4s 收工
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：Prism 的 dimensions 三边长 ==================================
class PrismDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 内部会调 self.play，先接到窗口上
        title = Text("01-prism", font_size=34, color=YELLOW).to_edge(UP)   #样例标题
        self.add_fixed_in_frame_mobjects(title)   #标题钉在屏幕上
        a = Prism(dimensions=[3, 2, 1])   #默认三边长 [x, y, z] = [3, 2, 1]
        b = Prism(dimensions=[1, 1, 3], fill_color=RED, fill_opacity=0.6)   #瘦高的红色棱柱
        b.next_to(a, RIGHT, buff=1.2)   #摆在默认棱柱右边
        tag1 = Text("[3, 2, 1]", font_size=26, color=GREY_B).next_to(a, DOWN)   #左下角标注
        tag2 = Text("[1, 1, 3]", font_size=26, color=GREY_B).next_to(b, DOWN)   #右下角标注
        self.add(a, b, tag1, tag2)   #把两个棱柱和标签放进场景
        self.set_camera_orientation(phi=65 * DEGREES, theta=-60 * DEGREES)   #摆好斜视角
        win.play(Wait(0.8))   #停 0.8s 看清三边长差异
        self.move_camera(theta=-150 * DEGREES, run_time=1.4)   #带动画环绕 90°
        win.play(Wait(0.4))   #停 0.4s 收工
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：Dot3D 的半径 / 颜色 / 分辨率 ================================
class Dot3DDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 内部会调 self.play，先接到窗口上
        title = Text("01-dot3d", font_size=34, color=YELLOW).to_edge(UP)   #样例标题
        self.add_fixed_in_frame_mobjects(title)   #标题钉在屏幕上
        big = Dot3D(2 * UR, radius=0.5, color=RED)   #大号红球标记一个三维点
        rough = Dot3D(LEFT * 2.5 + DOWN, radius=0.4, color=GREEN, resolution=(4, 2))   #极低分辨率：棱角分明
        smooth = Dot3D(RIGHT * 2.5 + DOWN, radius=0.4, color=GREEN)   #默认 (8, 8)：圆滑一些
        tag1 = Text("res=(4,2)", font_size=26, color=GREY_B).next_to(rough, DOWN)   #左下角标注
        tag2 = Text("default (8,8)", font_size=26, color=GREY_B).next_to(smooth, DOWN)   #右下角标注
        self.add(big, rough, smooth, tag1, tag2)   #把三个小球和标签放进场景
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES)   #摆好斜视角
        win.play(Wait(0.8))   #停 0.8s 对比分辨率
        self.move_camera(theta=-135 * DEGREES, run_time=1.4)   #带动画环绕 90°
        win.play(Wait(0.4))   #停 0.4s 收工
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("cube", CubeDemo),
    ("prism", PrismDemo),
    ("dot3d", Dot3DDemo),
]

PAIRS = [
    ("cube", ["cube"]),
    ("prism", ["prism"]),
    ("dot3d", ["dot3d"]),
]

PAGE = "01-三维基本体"


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
