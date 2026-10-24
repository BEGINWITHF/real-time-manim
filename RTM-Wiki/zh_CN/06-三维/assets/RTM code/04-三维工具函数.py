# -*- coding: utf-8 -*-
"""04-三维工具函数.md 两个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 04-三维工具函数.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的两条样例视频（输出到上一级 assets/）；
python 04-三维工具函数.py --concat-only 只拼接不渲染。
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
    ThreeDScene, Cube, VGroup, Dot3D, Arrow3D, Text,
    GREEN, GREY_B, RED, YELLOW,
    UP, DOWN, DEGREES,
    get_3d_vmob_start_corner, get_3d_vmob_end_corner,
    get_3d_vmob_end_corner_index,
    get_3d_vmob_gradient_start_and_end_points,
    get_3d_vmob_start_corner_unit_normal, get_3d_vmob_end_corner_unit_normal,
    get_3d_vmob_unit_normal,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：首/尾角点、渐变起止点与首/尾法向 ===========================
class CornersDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 内部会调 self.play，先接到窗口上
        title = Text("04-corners", font_size=34, color=YELLOW).to_edge(UP)   #样例标题
        self.add_fixed_in_frame_mobjects(title)   #标题钉在屏幕上
        cube = Cube(side_length=2, fill_opacity=0.35, stroke_width=3)   #半透明立方体
        face = cube[0]   #取一个面片（单个 VMobject，这些函数对它才有意义）
        p0 = get_3d_vmob_start_corner(face)   #首角点坐标（下标恒为 0）
        p1 = get_3d_vmob_end_corner(face)   #尾角点坐标
        g0, g1 = get_3d_vmob_gradient_start_and_end_points(face)   #渐变起止点 = 首/尾角点
        n0 = get_3d_vmob_start_corner_unit_normal(face)   #首角点单位法向量
        n1 = get_3d_vmob_end_corner_unit_normal(face)   #尾角点单位法向量
        print("start:", p0, " end idx:", get_3d_vmob_end_corner_index(face), "->", p1)   #控制台输出查询结果
        print("gradient:", g0, g1)   #渐变起止点就是首/尾角点
        print("normals:", n0, n1)   #首/尾角点的单位法向量
        d0 = Dot3D(p0, radius=0.09, color=RED)   #红色小球标出首角点
        d1 = Dot3D(p1, radius=0.09, color=YELLOW)   #黄色小球标出尾角点
        a0 = Arrow3D(p0, p0 + 0.8 * n0, color=GREEN, thickness=0.05)   #首角点法向箭头
        a1 = Arrow3D(p1, p1 + 0.8 * n1, color=GREEN, thickness=0.05)   #尾角点法向箭头
        tag = Text("corners(red/yellow) normals(green)", font_size=24, color=GREY_B).to_edge(DOWN)
        self.add(cube, d0, d1, a0, a1, tag)   #把立方体、角点标记和法向箭头放进场景
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)   #摆好斜视角
        win.play(Wait(0.8))   #停 0.8s 看清标记
        self.move_camera(theta=-135 * DEGREES, run_time=1.2)   #带动画环绕 90°
        win.play(Wait(0.4))   #停 0.4s 收工
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：按锚点下标查任意位置的单位法向量 ===========================
class FaceNormalsDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 内部会调 self.play，先接到窗口上
        title = Text("04-face_normals", font_size=34, color=YELLOW).to_edge(UP)   #样例标题
        self.add_fixed_in_frame_mobjects(title)   #标题钉在屏幕上
        face = Cube(side_length=2)[1]   #换一个面片（侧面）来采样多个锚点
        end_idx = get_3d_vmob_end_corner_index(face)   #尾角点在 points 里的下标
        idxs = [0, end_idx // 2, end_idx]   #首 / 中 / 尾三个锚点
        arrows = VGroup()
        for i in idxs:   #在每个锚点处画一根法向箭头
            p = face.points[i]   #锚点坐标
            n = get_3d_vmob_unit_normal(face, i)   #按锚点下标查单位法向量
            arrows.add(Arrow3D(p, p + 0.7 * n, color=GREEN, thickness=0.05))
        tag = Text("normals at idx 0 / %d / %d" % (end_idx // 2, end_idx),   #把三个下标打进标签
                   font_size=24, color=GREY_B).to_edge(DOWN)
        self.add(face, arrows, tag)   #把这个面片和三根箭头放进场景（不用带整只立方体）
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)   #摆好斜视角
        win.play(Wait(0.8))   #停 0.8s 看清三根法向箭头
        self.move_camera(theta=-120 * DEGREES, run_time=1.2)   #带动画环绕 90°
        win.play(Wait(0.4))   #停 0.4s 收工
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("corners", CornersDemo),
    ("face_normals", FaceNormalsDemo),
]

PAIRS = [
    ("corners", ["corners"]),
    ("face_normals", ["face_normals"]),
]

PAGE = "04-三维工具函数"


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
