# -*- coding: utf-8 -*-
"""03-多面体.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 03-多面体.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的三条样例视频（输出到上一级 assets/）；
python 03-多面体.py --concat-only 只拼接不渲染。
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
    ThreeDScene, Polyhedron, Tetrahedron, Octahedron, Icosahedron,
    Dodecahedron, ConvexHull3D, VGroup, Dot3D, Text,
    BLUE, GREEN, GREY_B, RED, YELLOW,
    UP, DOWN, LEFT, RIGHT, DEGREES,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：四种柏拉图立体 + graph/faces 访问 ===========================
class PlatonicDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 内部会调 self.play，先接到窗口上
        title = Text("03-platonic", font_size=34, color=YELLOW).to_edge(UP)   #样例标题
        self.add_fixed_in_frame_mobjects(title)   #标题钉在屏幕上
        solids = VGroup(
            Tetrahedron(edge_length=1),      #4 面正四面体
            Octahedron(edge_length=1),       #8 面正八面体
            Icosahedron(edge_length=0.9),    #20 面正二十面体
            Dodecahedron(edge_length=0.7),   #12 面正十二面体
        ).arrange(RIGHT, buff=1.2)   #从左到右排成一行
        solids.to_edge(DOWN, buff=1.4)   #整体下沉一点，给标题留位
        octa = solids[1]   #取正八面体演示访问
        octa.graph[0].set_color(RED)   #给一个顶点上色（graph 是顶点 Graph）
        octa.faces[2].set_color(YELLOW)   #给一个面上色（faces 是面片 VGroup）
        tag = Text("tetra / octa / icosa / dodeca", font_size=24, color=GREY_B).next_to(solids, DOWN)
        self.add(solids, tag)   #把四个立体和标签放进场景
        self.set_camera_orientation(phi=65 * DEGREES, theta=-30 * DEGREES)   #摆好斜视角
        win.play(Wait(0.8))   #停 0.8s 看清四个立体
        self.move_camera(theta=-120 * DEGREES, run_time=1.4)   #带动画环绕 90°
        win.play(Wait(0.4))   #停 0.4s 收工
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：自定义顶点/面表 + 拖动顶点形变 ==============================
class PolyhedronDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 与 animate 内部都会调 self.play，先接到窗口上
        title = Text("03-polyhedron", font_size=34, color=YELLOW).to_edge(UP)   #样例标题
        self.add_fixed_in_frame_mobjects(title)   #标题钉在屏幕上
        pyramid = Polyhedron(
            vertex_coords=[[1, 1, 0], [1, -1, 0], [-1, -1, 0], [-1, 1, 0], [0, 0, 2]],   #4 个底面顶点 + 1 个锥顶
            faces_list=[[0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4], [0, 1, 2, 3]],   #4 个侧面 + 1 个底面
            faces_config={"fill_opacity": 0.6, "fill_color": BLUE},   #面片配置：半透明蓝
        )
        pyramid.shift(LEFT * 2)   #整体左移，给形变留出空间
        pyramid.faces[2].set_color(YELLOW)   #给第 3 个面（侧面）换个颜色
        pyramid.graph[4].set_color(RED)   #给锥顶顶点上色
        print("面片数：", len(pyramid.faces), "顶点数：", len(pyramid.graph))   #控制台确认结构
        tag = Text("faces[2] / graph[4]", font_size=24, color=GREY_B).next_to(pyramid, DOWN)
        self.add(pyramid, tag)   #把棱锥和标签放进场景
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)   #摆好斜视角
        win.play(Wait(0.8))   #停 0.8s 看清上色的面和顶点
        win.play(pyramid.graph[4].animate.shift(DOWN + RIGHT * 0.5), run_time=1.0)   #拖动锥顶：updater 带动整个立体形变
        win.play(Wait(0.4))   #停 0.4s 收工
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：ConvexHull3D 自动求凸包 ====================================
class HullDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 内部会调 self.play，先接到窗口上
        title = Text("03-hull", font_size=34, color=YELLOW).to_edge(UP)   #样例标题
        self.add_fixed_in_frame_mobjects(title)   #标题钉在屏幕上
        pts = [[1.9, 0.4, -1.5], [-0.9, 1.2, 0.6], [0.4, 0.4, -1.8],   #6 个三维点
               [-1.5, -0.8, -0.5], [0.8, -1.4, 0.9], [-0.2, 0.1, 2.0]]
        hull = ConvexHull3D(*pts, faces_config={"fill_opacity": 0.4, "fill_color": GREEN})   #自动求凸包成多面体
        dots = VGroup(*[Dot3D(p, radius=0.08, color=RED) for p in pts])   #原始点用小红球标出
        tag = Text("ConvexHull3D(*points)", font_size=24, color=GREY_B).to_edge(DOWN)
        self.add(hull, dots, tag)   #把凸包、点和标签放进场景
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)   #摆好斜视角
        win.play(Wait(0.8))   #停 0.8s 看清凸包包络
        self.move_camera(theta=-135 * DEGREES, run_time=1.4)   #带动画环绕 90°
        win.play(Wait(0.4))   #停 0.4s 收工
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("platonic", PlatonicDemo),
    ("polyhedron", PolyhedronDemo),
    ("hull", HullDemo),
]

PAIRS = [
    ("platonic", ["platonic"]),
    ("polyhedron", ["polyhedron"]),
    ("hull", ["hull"]),
]

PAGE = "03-多面体"


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
