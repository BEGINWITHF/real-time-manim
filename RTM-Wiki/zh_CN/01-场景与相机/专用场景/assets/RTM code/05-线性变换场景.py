# -*- coding: utf-8 -*-
"""05-线性变换场景.md 的样例在 RTM 下的渲染（每个样例一个类）。

四个样例：
  1. 构造参数 show_coordinates / include_background_plane / leave_ghost_vectors
     -> 四段拼成 05-线性变换场景-ctor.mp4
  2. apply_matrix / apply_inverse / apply_transposed_matrix / apply_inverse_transpose
  3. apply_nonlinear_transformation / apply_function
  4. add_title / add_unit_square / add_vector / write_vector_coordinates /
     add_transformable_label

跑法：python 05-线性变换场景.py             # 全部
      python 05-线性变换场景.py apply       # 只渲指定片段
"""
import math
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
ASSETS = os.path.dirname(HERE)
os.makedirs(OUT, exist_ok=True)

sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")
from real_time_manim import (  # noqa: E402
    DOWN,
    UP,
    YELLOW,
    LinearTransformationScene,
    Text,
    Wait,
)
from real_time_manim.record import fast_record_scene  # noqa: E402
from real_time_manim.vulkan_bind import MLWindow, Wait  # noqa: E402


def say(cap, text):   #瞬间换掉顶部说明文字，不占动画时间
    cap.become(Text(text, font_size=26, color=YELLOW).to_edge(UP))


def say_low(cap, text):   #ComposeDemo 专用：说明放底部，给顶部的 add_title 让位
    cap.become(Text(text, font_size=26, color=YELLOW).to_edge(DOWN))


# ===== 样例 1：LinearTransformationScene 构造参数 ==========================
class CtorBase(LinearTransformationScene):
    KW = {}            #子类填要传给 LinearTransformationScene.__init__ 的构造参数
    LABEL = ""         #子类填本段的标题文字
    TRANSFORM = False  #True 的子类在结尾播一次剪切

    def __init__(self, **kwargs):
        super().__init__(**self.KW, **kwargs)   #把 “KW” 里的键传给 LinearTransformationScene.__init__

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #apply_* 内部会调 self.play，先接到窗口上
        cap = Text(self.LABEL, font_size=26, color=YELLOW)   #顶部标题显示当前构造参数
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(cap)   #放进场景（网格与基向量由 setup 自动加好）
        win.play(Wait(1.3))   #停 1.3s 看清默认布景
        if self.TRANSFORM:
            self.apply_matrix([[1, 1], [0, 1]], run_time=1.2)   #一次水平剪切：残影开关的效果才看得见
            win.play(Wait(0.6))   #停 0.6s 看残影
        win.close()   #关闭 RTM 窗口


class LtsPlain(CtorBase):
    LABEL = "defaults (bg+fg plane, i_hat/j_hat)"   #默认布景
    KW = {}                                          #空字典 = 用 manim 的默认值


class LtsCoords(CtorBase):
    LABEL = "show_coordinates=True"                 #背景网格显示刻度数字
    KW = {"show_coordinates": True}


class LtsBgOff(CtorBase):
    LABEL = "include_background/foreground_plane=False"   #两个网格平面都不要
    KW = {"include_background_plane": False,              #关掉背景平面
          "include_foreground_plane": False}              #关掉前景平面：画面只剩基向量


class LtsGhost(CtorBase):
    LABEL = "leave_ghost_vectors=True"              #变换后保留基向量残影
    KW = {"leave_ghost_vectors": True}
    TRANSFORM = True                                #本段要播一次变换


# ===== 样例 2：apply_matrix / apply_inverse / apply_transposed_matrix =======
class ApplyDemo(LinearTransformationScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #apply_* 内部都会调 self.play，先接到窗口上
        cap = Text("", font_size=26, color=YELLOW)   #顶部说明文字（内容后面换）
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(cap)   #放进场景

        say(cap, "apply_matrix([[1, 1], [0, 1]])")
        self.apply_matrix([[1, 1], [0, 1]], run_time=1.2)   #水平剪切：整格向右上斜
        win.play(Wait(0.5))   #停 0.5s

        say(cap, "apply_inverse([[1, 1], [0, 1]])")
        self.apply_inverse([[1, 1], [0, 1]], run_time=1.2)   #求 M 的逆并施加：撤销上一步
        win.play(Wait(0.5))   #停 0.5s

        say(cap, "apply_transposed_matrix([[1, 1], [0, 1]])")
        self.apply_transposed_matrix([[1, 1], [0, 1]], run_time=1.2)   #传入 M，实际施加 M 的转置（竖直剪切）
        win.play(Wait(0.5))   #停 0.5s

        say(cap, "apply_inverse_transpose([[1, 1], [0, 1]])")
        self.apply_inverse_transpose([[1, 1], [0, 1]], run_time=1.2)   #施加转置之逆：又回到原网格
        win.play(Wait(0.6))   #停 0.6s 收工
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：apply_nonlinear_transformation / apply_function ==============
class NonlinearDemo(LinearTransformationScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #apply_* 内部都会调 self.play，先接到窗口上
        cap = Text("", font_size=26, color=YELLOW)   #顶部说明文字（内容后面换）
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(cap)   #放进场景
        self.add_unit_square(animate=False)   #放个单位正方形，弯曲效果更直观

        def swirl(p):   #按到原点的距离旋转：离原点越远转得越多
            x, y = p[0], p[1]
            a = 0.5 * math.hypot(x, y)   #每单位半径多转 0.5 弧度
            c, s = math.cos(a), math.sin(a)
            return np.array([x * c - y * s, x * s + y * c, p[2]])

        def squash(p):   #纵向压扁：离 x 轴越远压得越狠
            return np.array([p[0], 3.0 * math.tanh(p[1] / 3.0), p[2]])   #tanh 保证有界

        say(cap, "apply_nonlinear_transformation(swirl)")
        self.apply_nonlinear_transformation(swirl, run_time=1.6)   #先细分平面再施加函数
        win.play(Wait(0.6))   #停 0.6s

        say(cap, "apply_function(squash)")
        self.apply_function(squash, run_time=1.6)   #直接对每个点施加函数
        win.play(Wait(0.6))   #停 0.6s 收工
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：add_title / add_unit_square / add_vector / 标签 =============
class ComposeDemo(LinearTransformationScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #add_title / add_unit_square / add_vector 内部会调 self.play，先接到窗口上
        cap = Text("", font_size=26, color=YELLOW)   #说明文字放底部，给顶部的标题让位
        cap.to_edge(DOWN)   #标题挪到画面底端
        self.add(cap)   #放进场景

        say_low(cap, "add_title('Linear Transformation', animate=True)")
        self.add_title("Linear Transformation",   #顶部大标题（自动加背景条、进前景层）
                       scale_factor=0.9, animate=True)   #animate=True 时内部播 Write
        win.play(Wait(0.7))   #停 0.7s

        say_low(cap, "add_unit_square(animate=True)")
        self.add_unit_square(animate=True)   #画出单位正方形（DrawBorderThenFill）
        win.play(Wait(0.5))   #停 0.5s

        say_low(cap, "add_vector([2, 1], color=YELLOW, animate=True)")
        v = self.add_vector([2, 1], color=YELLOW, animate=True)   #放一个向量并登记进 moving_vectors
        win.play(Wait(0.6))   #停 0.6s

        say_low(cap, "write_vector_coordinates(v)")
        self.write_vector_coordinates(v)   #写出列矩阵坐标
        win.play(Wait(0.6))   #停 0.6s

        say_low(cap, "add_transformable_label(v, 'w', ...)")
        self.add_transformable_label(v, "w",   #变换时会自动改写的标签
                                     transformation_name="L",
                                     label_scale_factor=0.8)
        win.play(Wait(0.6))   #停 0.6s

        say_low(cap, "apply_matrix([[0, -1], [1, 0]])  rotate 90°")
        self.apply_matrix([[0, -1], [1, 0]], run_time=1.4)   #旋转 90°：方块变竖、标签随矩阵改写
        win.play(Wait(0.7))   #停 0.7s 收工
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("ctor_plain", LtsPlain),
    ("ctor_coords", LtsCoords),
    ("ctor_bgoff", LtsBgOff),
    ("ctor_ghost", LtsGhost),
    ("apply", ApplyDemo),
    ("nonlinear", NonlinearDemo),
    ("compose", ComposeDemo),
]

PAIRS = [
    ("05-线性变换场景-ctor",
     ["ctor_plain", "ctor_coords", "ctor_bgoff", "ctor_ghost"]),
]


def concat(names, dst):
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    lst = os.path.join(HERE, "concat.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for n in names:
            p = os.path.join(OUT, n + ".mp4")
            f.write("file '%s'\n" % p.replace("\\", "/"))
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
