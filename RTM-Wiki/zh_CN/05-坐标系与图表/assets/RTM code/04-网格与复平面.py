# -*- coding: utf-8 -*-
"""04-网格与复平面.md 两个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 04-网格与复平面.py <场景名>...
不带参数就渲染全部场景，并拼出页面里的两条视频。
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
    Scene, NumberPlane, ComplexPlane, Dot, MathTex, Text,
    YELLOW, TEAL, BLUE_E, GREEN, GREY_B, UP, DOWN, UR,
    Create, FadeIn, GrowArrow, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：NumberPlane 网格画布 =======================================
class NumberPlaneDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("04-NumberPlane", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        plane = NumberPlane(
            background_line_style={"stroke_color": TEAL, "stroke_width": 4, "stroke_opacity": 0.6},   #参数 “background_line_style”：主网格线样式
            faded_line_ratio=2,   #参数 “faded_line_ratio”：每格细分成 2x2 份淡色线
        )
        lab = Text("faded_line_ratio=2  (each cell -> 4)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   #参数说明标签
        win.play(Create(plane), run_time=1.2)   #画出主网格 + 淡色细分线
        win.play(FadeIn(lab), run_time=0.3)   #说明标签淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：ComplexPlane 复平面 ========================================
class ComplexPlaneDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("04-ComplexPlane", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        cplane = ComplexPlane(
            x_range=[-3, 3, 1], y_range=[-3, 3, 1],   #范围/步长参数与 NumberPlane 相同
            background_line_style={"stroke_color": BLUE_E, "stroke_width": 2},   #网格线换成蓝色系
        ).add_coordinates()   #y 轴标签自动带 i（1i、2i…）
        d1 = Dot(cplane.n2p(2 + 1j), color=YELLOW)   #“n2p”：复数 2+i 直接换算成场景点
        label = MathTex("2+i").next_to(d1, UR, buff=0.2)   #复数标签
        vec = cplane.get_vector([1, -2], color=GREEN)   #“get_vector”：原点 -> (1,-2) 的箭头
        lab = Text("n2p(2+1j) + get_vector([1,-2])",
                   font_size=24, color=GREY_B).to_edge(DOWN)   #方法说明标签
        win.play(Create(cplane), run_time=1.0)   #画出复平面（含 i 标签）
        win.play(FadeIn(lab), run_time=0.3)   #说明标签淡入
        win.play(FadeIn(d1), Write(label), run_time=0.6)   #黄点与 “2+i” 标签出场
        win.play(GrowArrow(vec), run_time=0.6)   #绿色箭头从原点长出来
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("04-网格与复平面-numberplane", NumberPlaneDemo),
    ("04-网格与复平面-complexplane", ComplexPlaneDemo),
]

PAIRS = [
    ("04-网格与复平面-numberplane", ["04-网格与复平面-numberplane"]),
    ("04-网格与复平面-complexplane", ["04-网格与复平面-complexplane"]),
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

    if not only:
        for out_name, names in PAIRS:
            dst = os.path.join(ASSETS, "RTM output", out_name + ".mp4")
            concat(names, dst)
            print("concat ->", dst, os.path.getsize(dst), "bytes")
