# -*- coding: utf-8 -*-
"""01-NumberLine.md 两个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 01-NumberLine.py <场景名>...
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

from real_time_manim import (
    Scene, NumberLine, UnitInterval, Dot, Text, VGroup,
    YELLOW, RED, GREY_B, UP, DOWN,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：基本构造参数 ================================================
class NumberLineBasicDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-NumberLine", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        line = NumberLine(x_range=[-4, 4, 1], length=8,   #参数 “x_range”：数据范围与步长；“length”：总长 8
                         include_numbers=True, include_tip=True)   #参数 “include_numbers”/“include_tip”：数字标签 + 末端箭头
        dot = Dot(line.n2p(2), color=RED)   #用 “n2p” 把数值 2 换成场景点（见 01b）
        lab = Text("x_range=[-4,4,1]  length=8  tip+numbers",
                   font_size=26, color=GREY_B).next_to(line, DOWN, buff=0.6)   #参数说明标签
        win.play(Create(line), run_time=0.8)   #画出整条数轴（含刻度、数字、箭头）
        win.play(FadeIn(dot), FadeIn(lab), run_time=0.4)   #红点与标签淡入
        win.play(dot.animate.move_to(line.n2p(-3)), run_time=1.0)   #红点沿轴移到数值 -3
        win.play(dot.animate.move_to(line.n2p(3.5)), run_time=1.0)   #再移到数值 3.5（刻度之间也能停）
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：UnitInterval 子类 ==========================================
class UnitIntervalDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-UnitInterval", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        line = UnitInterval(unit_size=10)   #参数 “unit_size”：0~1 铺满 10 个 Manim 单位
        line.add_numbers()   #步长 0.1 自动出一位小数标签，0/1 处刻度加长
        lab = Text("UnitInterval(unit_size=10)", font_size=28,
                   color=GREY_B).next_to(line, DOWN, buff=0.6)   #参数说明标签
        win.play(Create(line), run_time=0.8)   #画出 [0,1] 专用数轴
        win.play(FadeIn(lab), run_time=0.4)   #标签淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("01-NumberLine-basic", NumberLineBasicDemo),
    ("01-NumberLine-unitinterval", UnitIntervalDemo),
]

PAIRS = [
    ("01-NumberLine-basic", ["01-NumberLine-basic"]),
    ("01-NumberLine-unitinterval", ["01-NumberLine-unitinterval"]),
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
