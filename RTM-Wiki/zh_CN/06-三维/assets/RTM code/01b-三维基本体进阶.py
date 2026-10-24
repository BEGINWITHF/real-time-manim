# -*- coding: utf-8 -*-
"""01b-三维基本体进阶.md 四个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 01b-三维基本体进阶.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的四条样例视频（输出到上一级 assets/）；
python 01b-三维基本体进阶.py --concat-only 只拼接不渲染。
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
    ThreeDScene, Line3D, Arrow3D, Cone, Cylinder, Text,
    GREEN, GREY_B, RED, YELLOW, PI,
    UP, DOWN, LEFT, RIGHT, UR, DEGREES,
    Create,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：Line3D 的粗细与平行/垂直类方法 ==============================
class Line3DDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #Create 与 move_camera 内部都会调 self.play，先接到窗口上
        title = Text("01b-line3d", font_size=34, color=YELLOW).to_edge(UP)   #样例标题
        self.add_fixed_in_frame_mobjects(title)   #标题钉在屏幕上
        line = Line3D(start=[-2, -1, 0], end=[2, 1, 1.5], thickness=0.06, color=YELLOW)   #加粗的黄色主线段
        para = Line3D.parallel_to(line, point=[-1, -2.5, 0], length=4)   #过指定点、与主线段平行的线段
        perp = Line3D.perpendicular_to(line, point=[2, -2, 0.75], length=3)   #过指定点、与主线段垂直的线段
        self.add(para, perp)   #先把两条参照线段放进场景
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)   #摆好斜视角
        win.play(Create(line), run_time=0.8)   #把主线段逐段画出来
        win.play(Wait(0.5))   #停 0.5s 看清平行/垂直关系
        self.move_camera(theta=-135 * DEGREES, run_time=1.2)   #带动画环绕 90°
        win.play(Wait(0.4))   #停 0.4s 收工
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：Arrow3D 的箭头尺寸与 get_end ================================
class Arrow3DDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 内部会调 self.play，先接到窗口上
        title = Text("01b-arrow3d", font_size=34, color=YELLOW).to_edge(UP)   #样例标题
        self.add_fixed_in_frame_mobjects(title)   #标题钉在屏幕上
        a = Arrow3D(start=[-2, -1, 0], end=[1.5, 0.5, 1.5])   #默认白色三维箭头
        b = Arrow3D(start=[0, -2.5, 0], end=[-1.5, -2.5, 2], color=RED,   #红色箭头：箭头锥更大
                    thickness=0.08, height=0.6, base_radius=0.18)
        tip = Text("tip=(%.1f, %.1f, %.1f)" % tuple(a.get_end()),   #把箭尖坐标格式化成标注
                   font_size=24, color=GREY_B).next_to(a.get_end(), UR, buff=0.2)   #摆在箭尖旁边
        self.add_fixed_orientation_mobjects(tip)   #只锁朝向：文字正对镜头但留在 3D 空间
        self.add(a, b, tip)   #把两支箭头和标注放进场景
        print("箭尖坐标：", a.get_end())   #控制台也打一份
        self.set_camera_orientation(phi=65 * DEGREES, theta=-60 * DEGREES)   #摆好斜视角
        win.play(Wait(0.8))   #停 0.8s 看清两支箭头
        self.move_camera(theta=-150 * DEGREES, run_time=1.2)   #带动画环绕 90°
        win.play(Wait(0.4))   #停 0.4s 收工
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：Cone 的 show_base / u_min / v_range =========================
class ConeDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 内部会调 self.play，先接到窗口上
        title = Text("01b-cone", font_size=34, color=YELLOW).to_edge(UP)   #样例标题
        self.add_fixed_in_frame_mobjects(title)   #标题钉在屏幕上
        a = Cone(base_radius=1, height=2, show_base=True)   #带底面圆盘的标准圆锥
        a.shift(LEFT * 2.5)   #摆在左侧
        b = Cone(base_radius=1, height=2, u_min=0.5, v_range=(0, PI))   #截顶 + 只留半圈的扇形锥
        b.set_color(GREEN)   #换色：Surface 子类的 “color=” 参数不生效，要构造后 set_color
        b.shift(RIGHT * 2.5)   #摆在右侧
        tag1 = Text("show_base=True", font_size=24, color=GREY_B).next_to(a, DOWN)   #左下角标注
        tag2 = Text("u_min=0.5 v_range=(0,PI)", font_size=24, color=GREY_B).next_to(b, DOWN)   #右下角标注
        self.add(a, b, tag1, tag2)   #把两个圆锥和标签放进场景
        self.set_camera_orientation(phi=65 * DEGREES, theta=-30 * DEGREES)   #摆好斜视角
        win.play(Wait(0.8))   #停 0.8s 看清形态差异
        self.move_camera(theta=-120 * DEGREES, run_time=1.2)   #带动画环绕 90°
        win.play(Wait(0.4))   #停 0.4s 收工
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：Cylinder 的 show_ends / v_range / direction =================
class CylinderDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 内部会调 self.play，先接到窗口上
        title = Text("01b-cylinder", font_size=34, color=YELLOW).to_edge(UP)   #样例标题
        self.add_fixed_in_frame_mobjects(title)   #标题钉在屏幕上
        a = Cylinder(radius=0.8, height=2.5)   #默认带上下底盖的圆柱
        a.shift(LEFT * 2.5)   #摆在左侧
        b = Cylinder(radius=0.8, height=2.5, show_ends=False, v_range=(0, PI),   #无底盖 + 半圈筒壁
                     direction=RIGHT)   #中轴改为水平
        b.set_color(RED)   #换色：Surface 子类的 “color=” 参数不生效，要构造后 set_color
        b.shift(RIGHT * 2.5 + UP * 0.4)   #摆在右侧、稍微抬高
        tag1 = Text("show_ends=True", font_size=24, color=GREY_B).next_to(a, DOWN)   #左下角标注
        tag2 = Text("half + no ends + direction", font_size=24, color=GREY_B).next_to(b, DOWN)   #右下角标注
        self.add(a, b, tag1, tag2)   #把两个圆柱和标签放进场景
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)   #摆好斜视角
        win.play(Wait(0.8))   #停 0.8s 看清形态差异
        self.move_camera(theta=-135 * DEGREES, run_time=1.2)   #带动画环绕 90°
        win.play(Wait(0.4))   #停 0.4s 收工
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("line3d", Line3DDemo),
    ("arrow3d", Arrow3DDemo),
    ("cone", ConeDemo),
    ("cylinder", CylinderDemo),
]

PAIRS = [
    ("line3d", ["line3d"]),
    ("arrow3d", ["arrow3d"]),
    ("cone", ["cone"]),
    ("cylinder", ["cylinder"]),
]

PAGE = "01b-三维基本体进阶"


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
