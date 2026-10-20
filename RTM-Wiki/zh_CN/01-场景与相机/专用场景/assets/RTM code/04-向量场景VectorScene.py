# -*- coding: utf-8 -*-
"""04-向量场景VectorScene.md 五个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 04-向量场景VectorScene.py <场景名>...
不带参数就渲染全部 6 个场景，并拼出页面里的第一条对比视频（plane）。
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
ASSETS = os.path.dirname(HERE)
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    GREEN, RED, WHITE, YELLOW, UP, Dot, Text, VectorScene,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


def say(cap, text):   #瞬间换掉顶部说明文字，不占动画时间
    cap.become(Text(text, font_size=28, color=YELLOW).to_edge(UP))


# ===== 样例 1：构造参数、add_plane、add_axes ===============================
class PlaneAxesBase(VectorScene):
    STROKE = 6.0   #子类改小，看基向量变细
    TAG = ""       #子类填标题里的线宽数字

    def __init__(self, **kwargs):
        super().__init__(basis_vector_stroke_width=self.STROKE, **kwargs)   #把 “basis_vector_stroke_width” 传给 VectorScene.__init__

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #add_plane / add_axes 内部会调 self.play，先接到窗口上
        cap = Text("", font_size=28, color=YELLOW)   #顶部说明文字（内容后面换）
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(cap)   #放进场景

        say(cap, "add_plane(animate=True)")
        plane = self.add_plane(animate=True)   #用 Create 画出网格平面
        self.plane = plane   #get_vector / add_vector 都要读 self.plane，手动挂上
        win.play(Wait(0.6))   #停 0.6s

        say(cap, "add_axes(animate=True, color=WHITE)")
        self.remove(plane)   #把网格收走
        self.add_axes(animate=True, color=WHITE)   #用 Create 画出坐标轴
        win.play(Wait(0.4))   #停 0.4s

        say(cap, "get_basis_vectors() stroke=%.1f" % self.STROKE)
        self.add(self.get_basis_vectors())   #放上 i_hat / j_hat，线宽就是构造参数
        win.play(Wait(0.8))   #停 0.8s 收工
        win.close()   #关闭 RTM 窗口


class PlaneAxesWide(PlaneAxesBase):
    STROKE = 6.0   #默认线宽
    TAG = "6.0"


class PlaneAxesThin(PlaneAxesBase):
    STROKE = 2.0   #细一档
    TAG = "2.0"


# ===== 样例 2：add_vector / get_vector =====================================
class VectorAddDemo(VectorScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #add_vector 内部会调 self.play，先接到窗口上
        cap = Text("", font_size=28, color=YELLOW)   #顶部说明文字（内容后面换）
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(cap)   #放进场景
        plane = self.add_plane(animate=False)   #直接放上网格
        self.plane = plane   #get_vector / add_vector 都要读 self.plane，手动挂上

        say(cap, "add_vector([2, 1], color=YELLOW, animate=True)")
        self.add_vector([2, 1], color=YELLOW, animate=True)   #坐标生成向量，GrowArrow 出场
        win.play(Wait(0.8))   #停 0.8s

        say(cap, "get_vector([-2, 1]) -> self.add(arrow)")
        arrow = self.get_vector([-2, 1])   #只生成 Arrow：不加入场景、不登记
        self.add(arrow)   #自己决定什么时候加进去
        win.play(Wait(0.8))   #停 0.8s 收工
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：write_vector_coordinates / label_vector / get_vector_label ==
class VectorLabelDemo(VectorScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #下面几个方法内部都会调 self.play，先接到窗口上
        cap = Text("", font_size=28, color=YELLOW)   #顶部说明文字（内容后面换）
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(cap)   #放进场景
        plane = self.add_plane(animate=False)   #直接放上网格
        self.plane = plane   #add_vector 要读 self.plane，手动挂上
        v = self.add_vector([2, 1], color=YELLOW, animate=True)   #先要有一个向量对象

        say(cap, "write_vector_coordinates(v)")
        self.write_vector_coordinates(v)   #写出列矩阵 [2, 1]，并登记进前景层
        win.play(Wait(0.8))   #停 0.8s

        say(cap, "label_vector(v, 'v')")
        self.label_vector(v, "v")   #在向量旁 Write 一个标签；单字符会排成箭头字母 v
        win.play(Wait(0.8))   #停 0.8s

        say(cap, "get_vector_label(v, 'w', at_tip=True, ...)")
        lab = self.get_vector_label(   #只生成标签、不播动画，参数都在这里
            v, "w", at_tip=True, direction="right",
            rotate=False, color=GREEN, label_scale_factor=1.0)
        self.add(lab)   #自己加进场景
        win.play(Wait(0.8))   #停 0.8s 收工
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：get_basis_vectors / get_basis_vector_labels =================
class BasisDemo(VectorScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        cap = Text("", font_size=28, color=YELLOW)   #顶部说明文字（内容后面换）
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(cap)   #放进场景
        plane = self.add_plane(animate=False)   #直接放上网格
        self.plane = plane   #与向量无关，只是摆个背景

        say(cap, "get_basis_vectors() 默认 X_COLOR / Y_COLOR")
        basis = self.get_basis_vectors()   #默认：i_hat 绿（X_COLOR）、j_hat 红（Y_COLOR）
        labels = self.get_basis_vector_labels()   #i_hat / j_hat 的 MathTex 标签
        self.add(basis, labels)   #一起放进场景
        win.play(Wait(0.9))   #停 0.9s

        self.remove(basis, labels)   #收走默认色的基向量
        say(cap, "get_basis_vectors(i_hat_color=GREEN, j_hat_color=RED)")
        basis2 = self.get_basis_vectors(   #换成 manim 标准 GREEN / RED（和默认色不同）
            i_hat_color=GREEN, j_hat_color=RED)
        self.add(basis2, labels)   #标签复用，颜色换了
        win.play(Wait(0.9))   #停 0.9s 收工
        win.close()   #关闭 RTM 窗口


# ===== 样例 5：vector_to_coords ============================================
class CoordsDemo(VectorScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #vector_to_coords 内部会调 self.play，先接到窗口上
        cap = Text("", font_size=28, color=YELLOW)   #顶部说明文字（内容后面换）
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(cap)   #放进场景
        plane = self.add_plane(animate=False)   #直接放上网格
        self.plane = plane   #与向量无关，只是摆个背景

        say(cap, "vector_to_coords([-1, 2], integer_labels=True)")
        self.vector_to_coords([-1, 2], integer_labels=True, clean_up=True)   #向量->坐标的分解动画，结束恢复原状
        win.play(Wait(0.5))   #停 0.5s

        say(cap, "vector_to_coords([1.5, -1], integer_labels=False)")
        self.vector_to_coords([1.5, -1], integer_labels=False, clean_up=True)   #小数就显示小数标签
        win.play(Wait(0.5))   #停 0.5s 收工
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("plane_wide", PlaneAxesWide),
    ("plane_thin", PlaneAxesThin),
    ("addvec", VectorAddDemo),
    ("labels", VectorLabelDemo),
    ("basis", BasisDemo),
    ("coords", CoordsDemo),
]

PAIRS = [
    ("04-向量场景VectorScene-plane", ["plane_wide", "plane_thin"]),
]


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

    for out_name, names in PAIRS:
        dst = os.path.join(ASSETS, "RTM output", out_name + ".mp4")
        concat(names, dst)
        print("concat ->", dst, os.path.getsize(dst), "bytes")

    import shutil   #单段样例也要发布成页面成片：<页名>-<片段名>.mp4
    PAGE = os.path.splitext(os.path.basename(__file__))[0]
    used = {n for _, names in PAIRS for n in names}
    for name, _ in SCENES:
        if name in used or (only and name not in only):
            continue
        src = os.path.join(OUT, name + ".mp4")
        if os.path.exists(src):
            shutil.copy(src, os.path.join(HERE, "..", PAGE + "-" + name + ".mp4"))
            print("publish ->", PAGE + "-" + name + ".mp4")
