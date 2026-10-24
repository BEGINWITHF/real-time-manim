# -*- coding: utf-8 -*-
"""09-概率与SampleSpace.md 两个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 09-概率与SampleSpace.py <场景名>...
不带参数就渲染全部场景，并拼出页面里的两条视频。
"""
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
ASSETS = os.path.dirname(HERE)
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

from real_time_manim import (  # noqa: E402
    BLACK, BLUE_E, Brace, Create, DOWN, FadeIn, GRAY, GREEN_E, GREY_B, LEFT,
    RIGHT, SampleSpace, Scene, Text, UP, WHITE, YELLOW,
    Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait  # noqa: E402
from real_time_manim.record import fast_record_scene  # noqa: E402


# ===== 样例 1：divide_vertically + 花括号标签 ==============================
class VerticalDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("09-SampleSpace", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        poly = SampleSpace(width=2, height=2, stroke_width=5, fill_opacity=0.1)   #样本空间方框
        poly.divide_vertically(   #“divide_vertically”：按概率列表垂直切块
            p_list=np.array([0.37, 0.13, 0.5]),   #参数 “p_list”：各块占比（和不足 1 自动补余量）
            colors=[BLACK, WHITE, GRAY],   #参数 “colors”：配色（自动做渐变）
            vect=RIGHT)   #参数 “vect”：切分方向
        poly.add_title("Sample space")   #“add_title”：方框上方的标题
        win.play(Create(poly), run_time=0.8)   #画出方框与切块
        win.play(Wait(0.5))   #进行 0.5s 的等待

        b0 = Brace(poly.vertical_parts[0], LEFT)   #给第 0 块在左侧挂花括号
        t0 = b0.get_text("0.37")   #“get_text”：花括号旁的标签
        b2 = Brace(poly.vertical_parts[2], RIGHT)   #最右一块在右侧挂
        t2 = b2.get_text("0.50")
        win.play(FadeIn(b0), FadeIn(t0), run_time=0.4)   #左右两个标签依次淡入
        win.play(FadeIn(b2), FadeIn(t2), run_time=0.4)
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：divide_horizontally + 占比不足自动补余量 ====================
class HorizontalDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("09-divide_horizontally", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        grid = SampleSpace(height=2.5, width=3, fill_opacity=0.6)   #更扁的样本空间
        grid.divide_horizontally(   #“divide_horizontally”：按概率列表水平切块
            p_list=[0.4, 0.25],   #只给两块 = 0.65，剩余 0.35 由 complete_p_list 自动补成第三块
            colors=[GREEN_E, BLUE_E],
            vect=DOWN)   #参数 “vect”：切分方向
        grid.add_title("horizontal division")   #标题写明切分方式（Tex 里别写 `_`）
        win.play(Create(grid), run_time=0.8)   #画出三块
        win.play(Wait(0.5))   #进行 0.5s 的等待

        labels = ["0.40", "0.25", "0.35"]
        braces = [Brace(grid.horizontal_parts[i], LEFT) for i in range(3)]   #每行左侧一个花括号
        texts = [braces[i].get_text(labels[i]) for i in range(3)]
        win.play(*[FadeIn(b) for b in braces], run_time=0.4)   #三个花括号一起淡入
        win.play(*[FadeIn(t) for t in texts], run_time=0.4)   #三个标签一起淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("09-概率与SampleSpace-basic", VerticalDemo),
    ("09-概率与SampleSpace-horizontal", HorizontalDemo),
]

PAIRS = [
    ("09-概率与SampleSpace-basic", ["09-概率与SampleSpace-basic"]),
    ("09-概率与SampleSpace-horizontal", ["09-概率与SampleSpace-horizontal"]),
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
