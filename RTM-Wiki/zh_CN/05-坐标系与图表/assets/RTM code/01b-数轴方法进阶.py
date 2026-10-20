# -*- coding: utf-8 -*-
"""01b-数轴方法进阶.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 01b-数轴方法进阶.py <场景名>...
不带参数就渲染全部场景，并拼出页面里的三条视频。
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
    Scene, NumberLine, Dot, Text, VGroup,
    YELLOW, RED, BLUE, GREEN, GREY_B, UP, DOWN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：n2p / p2n 双向换算 =========================================
class N2PP2NDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01b-n2p-p2n", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        line = NumberLine(x_range=[-2.5, 3, 0.5], length=10)   #半格步长数轴
        line.add_numbers(x_values=[-2, 0, 2])   #只在 -2/0/2 处挂数字
        lab = Text("n2p/p2n  value <-> point", font_size=28,
                   color=GREY_B).next_to(line, DOWN, buff=0.6)   #方法说明标签
        win.play(Create(line), run_time=0.8)   #画出数轴
        win.play(FadeIn(lab), run_time=0.3)   #标签淡入

        red = Dot(line.n2p(1.5), color=RED)   #“n2p”：数值 1.5 -> 场景点
        readout = Text("p2n=0.00", font_size=28, color=GREEN).next_to(lab, DOWN, buff=0.35)
        win.play(FadeIn(red), FadeIn(readout), run_time=0.4)   #红点与回读标签淡入
        win.play(red.animate.move_to(line.n2p(-1.5)), run_time=1.0)   #红点移到数值 -1.5
        point = red.get_center()   #取红点当前场景坐标
        readout.become(Text("p2n=%.2f" % line.p2n(point),   #“p2n”：场景点 -> 数值，回读成文字
                            font_size=28, color=GREEN).next_to(lab, DOWN, buff=0.35))
        win.play(Wait(0.6))   #停 0.6s 看回读结果

        yel = Dot(line @ 3, color=YELLOW)   #“@” 写法：等价于 n2p(3)
        tag = Text("line @ 3", font_size=28, color=YELLOW).next_to(yel, UP, buff=0.3)
        win.play(FadeIn(yel), FadeIn(tag), run_time=0.4)   #黄点与标签淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：add_numbers / add_labels ===================================
class AddNumbersLabelsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01b-add_numbers-labels", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        line = NumberLine(x_range=[-2.5, 3, 0.5], length=10)   #半格步长数轴
        line.add_numbers(x_values=[-2, 0, 2], num_decimal_places=1)   #“add_numbers”：只标指定数值，保留一位小数
        line.add_labels({0: "start", 3: "end"}, direction=UP, font_size=28)   #“add_labels”：数值换成任意文字标签
        lab = Text("add_numbers([-2,0,2]) + add_labels({0:start,3:end})",
                   font_size=24, color=GREY_B).next_to(line, DOWN, buff=0.6)   #方法说明标签
        win.play(Create(line), run_time=0.8)   #画出数轴
        win.play(FadeIn(lab), run_time=0.4)   #标签淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：刻度方法与绕数旋转 =========================================
class TicksRotateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01b-ticks-rotate", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        line = NumberLine(x_range=[-2, 2, 1], length=6, include_ticks=False)   #先不画刻度
        line.add_ticks()   #“add_ticks”：事后按 x_range 补齐刻度
        line.get_tick_marks().set_color(YELLOW)   #“get_tick_marks”：取全部刻度统一改色
        lab1 = Text("add_ticks() + get_tick_marks().set_color(YELLOW)",
                    font_size=24, color=GREY_B).next_to(line, DOWN, buff=0.6)   #方法说明标签
        lab2 = Text("unit_size=%.2f" % line.get_unit_size(),   #“get_unit_size”：1 个数值单位的屏幕长度
                    font_size=26, color=GREEN).next_to(lab1, DOWN, buff=0.3)
        win.play(Create(line), run_time=0.8)   #画出数轴（含补的黄色刻度）
        win.play(FadeIn(VGroup(lab1, lab2)), run_time=0.4)   #两行标签淡入
        win.play(Wait(0.4))   #停留看刻度颜色
        win.play(line.animate(run_time=1.0).rotate(0.5, about_point=line.n2p(0)))   #绕数值 0 对应点整体旋转
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("01b-数轴方法进阶-n2p_p2n", N2PP2NDemo),
    ("01b-数轴方法进阶-addnumbers", AddNumbersLabelsDemo),
    ("01b-数轴方法进阶-ticks", TicksRotateDemo),
]

PAIRS = [
    ("01b-数轴方法进阶-n2p_p2n", ["01b-数轴方法进阶-n2p_p2n"]),
    ("01b-数轴方法进阶-addnumbers", ["01b-数轴方法进阶-addnumbers"]),
    ("01b-数轴方法进阶-ticks", ["01b-数轴方法进阶-ticks"]),
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
