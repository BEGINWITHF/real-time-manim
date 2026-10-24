# -*- coding: utf-8 -*-
"""02-向量场与流线.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 02-向量场与流线.py <片段名>...
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

import numpy as np
from real_time_manim import (
    Scene, Text, VGroup, Dot, Line, ArrowVectorField,
    RED, ORANGE, GREEN, YELLOW, GREY_B, UP, DOWN, LEFT, RIGHT,
    Write, FadeIn, Create,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：ArrowVectorField 构造参数 ===================================
class ArrowVectorFieldDemo(Scene):
    TUNED = False   #False 用默认配色与长度函数；True 换单色 + 线性长度

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02-ArrowVectorField", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题
        lab = Text(
            "color=RED, length_func=lambda x: x/3, vector_config={stroke_width:2}"
            if self.TUNED else "default: color=norm gradient, length_func=0.45*sigmoid",
            font_size=24, color=GREY_B,
        ).next_to(title, DOWN, buff=0.3)   #显示当前构造参数
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   #标签从下方淡入
        func = lambda pos: np.sin(pos[1] / 2) * RIGHT + np.cos(pos[0] / 2) * UP   #场函数：位置 -> 向量
        if self.TUNED:
            vf = ArrowVectorField(
                func,                                   #参数 “func”
                x_range=[-4, 4, 1], y_range=[-2.5, 2.5, 1],   #采样网格
                color=RED,                              #参数 “color”：整体单色
                length_func=lambda x: x / 3,            #参数 “length_func”：线性定长
                vector_config={"stroke_width": 2},      #参数 “vector_config”
            )
        else:
            vf = ArrowVectorField(
                func,                                   #参数 “func”
                x_range=[-4, 4, 1], y_range=[-2.5, 2.5, 1],   #采样网格
            )
        win.play(FadeIn(vf), run_time=0.8)   #整片箭头淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


class ArrowVectorFieldTuned(ArrowVectorFieldDemo):
    TUNED = True   #同一张场：单色 + 线性长度函数 + 细箭杆


# ===== 样例 2：nudge 单步与持续 updater ====================================
class NudgeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02-VectorField-nudge", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题
        lab = VGroup(
            Text("vf.nudge(dot, dt=1, substeps=20)   # one RK4 step",
                 font_size=26, color=GREY_B),
            Text("dot.add_updater(vf.get_nudge_updater(speed=1))",
                 font_size=26, color=GREY_B),
        ).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.3)   #两行签名标签
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   #标签从下方淡入
        func = lambda pos: np.sin(pos[1] / 2) * RIGHT + np.cos(pos[0] / 2) * UP   #场函数
        vf = ArrowVectorField(func, x_range=[-4, 4, 1], y_range=[-2.5, 2.5, 1],
                              opacity=0.4)   #半透明的场当背景
        dot = Dot(radius=0.12, color=RED).move_to([-3.5, -1.4, 0])   #出发点
        win.play(FadeIn(vf), FadeIn(dot), run_time=0.5)   #场与红点淡入
        start = dot.get_center().copy()   #记住起点
        vf.nudge(dot, dt=1, substeps=20)   #参数 “dt” / “substeps”：RK4 推一大步（直接落位）
        step = Line(start, dot.get_center(), stroke_width=4, color=ORANGE)   #画出这一步的位移
        win.play(Create(step), run_time=0.4)   #橙色线段标出单步位移
        win.play(Wait(0.3))   #进行 0.3s 的等待
        dot.add_updater(vf.get_nudge_updater(speed=1))   #参数 “speed”：换成持续沿场流动
        win.play(Wait(2.0))   #红点沿场线流动 2 秒
        dot.clear_updaters()   #解除 updater，点停住
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：子 mobject 群体流动 =========================================
class SubmobjectMoveDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02-VectorField-submobjects", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题
        lab = Text("vf.start_submobject_movement(speed=1.5) ... stop_...()",
                   font_size=26, color=GREY_B).next_to(title, DOWN, buff=0.3)   #签名标签
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   #标签从下方淡入
        func = lambda pos: np.sin(pos[1] / 2) * RIGHT + np.cos(pos[0] / 2) * UP   #场函数
        vf = ArrowVectorField(func, x_range=[-4, 4, 1.5], y_range=[-2.25, 2.25, 1.5],
                              color=GREEN)   #稀疏一点的绿色箭头网格
        win.play(FadeIn(vf), run_time=0.5)   #整片箭头淡入
        vf.start_submobject_movement(speed=1.5)   #参数 “speed”：所有箭头一起沿场漂移
        win.play(Wait(2.0))   #漂移 2 秒
        vf.stop_submobject_movement()   #停在当前位置
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("field_default", ArrowVectorFieldDemo),
    ("field_tuned", ArrowVectorFieldTuned),
    ("nudge", NudgeDemo),
    ("submobject", SubmobjectMoveDemo),
]

PAIRS = [
    ("field", ["field_default", "field_tuned"]),
    ("nudge", ["nudge"]),
    ("submobject", ["submobject"]),
]

PAGE = "02-向量场与流线"


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
