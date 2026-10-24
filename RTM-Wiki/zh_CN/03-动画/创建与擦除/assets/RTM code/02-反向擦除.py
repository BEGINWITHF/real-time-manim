# -*- coding: utf-8 -*-
"""02-反向擦除.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 02-反向擦除.py <片段名>...
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    Scene, Text, Square, Rectangle, Circle, VGroup,
    BLUE, GREEN, RED, YELLOW, GREY_B,
    UP, DOWN, LEFT, RIGHT,
    linear, smooth,
    Create, FadeIn, Uncreate, Unwrite, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait, Succession, Add
from real_time_manim.record import fast_record_scene


# ===== 样例 1：Uncreate 的倒放擦除 ==========================================
class UncreateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02-Uncreate", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("Uncreate(mobject, reverse_rate_function=True, remover=True,",
                  font_size=30, color=GREY_B)
        l2 = Text("         lag_ratio=1.0, run_time=1.2, rate_func=smooth)",
                  font_size=30, color=GREY_B)
        lab1 = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #两行 “Uncreate” 签名标签
        sq = Square(side_length=1.6, color=BLUE).next_to(lab1, DOWN, buff=0.6)   #先画后擦的蓝方块
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)   #标签从下方淡入
        win.play(Create(sq, run_time=1.0), run_time=1.0)   #先把方块画好
        win.play(
            Uncreate(sq,                            #参数 “mobject”
                     reverse_rate_function=True,    #参数 “reverse_rate_function”：倒放
                     remover=True,                  #参数 “remover”：擦完移出场景
                     lag_ratio=1.0,                 #参数 “lag_ratio”
                     run_time=1.2,                  #参数 “run_time”
                     rate_func=smooth),             #参数 “rate_func”
            run_time=1.2,
        )
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：Unwrite 的 reverse=False 从头擦 ==============================
class UnwriteDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02-Unwrite", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l3 = Text("Unwrite(vmobject, rate_func=linear, reverse=False,",
                  font_size=30, color=GREY_B)
        l4 = Text("        run_time=1.4, lag_ratio=0.2)",
                  font_size=30, color=GREY_B)
        lab2 = VGroup(l3, l4).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #两行 “Unwrite” 签名标签
        txt = Text("Goodbye Manim", font_size=44, color=GREEN).next_to(lab2, DOWN, buff=0.6)   #先写后擦的字
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)   #标签从下方淡入
        win.play(Write(txt, rate_func=linear, run_time=1.0), run_time=1.0)   #先把字写好
        win.play(
            Unwrite(txt,                            #参数 “vmobject”
                    rate_func=linear,               #参数 “rate_func”：匀速手擦
                    reverse=False,                  #参数 “reverse”：非默认，从头擦起
                    run_time=1.4,                   #参数 “run_time”
                    lag_ratio=0.2),                 #参数 “lag_ratio”
            run_time=1.4,
        )
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：Add 在 Succession 里排时间轴 =================================
class AddDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02-Add", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l5 = Text("Add(*mobjects, run_time=0.0 instant / 0.5 hold) in Succession",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   #签名标签
        rect = (Rectangle(width=3.4, height=1.4, color=YELLOW)
                .next_to(l5, DOWN, buff=0.6))   #装点的黄框
        dot_a = Circle(radius=0.16, color=GREEN).move_to(rect.get_left() + RIGHT * 0.7)   #第一个被加入的点
        dot_b = Circle(radius=0.16, color=RED).move_to(rect.get_center() + RIGHT * 0.7)   #第二个被加入的点
        dot_c = Circle(radius=0.16, color=BLUE).move_to(rect.get_right() + LEFT * 0.7)   #与 “dot_b” 同组加入
        win.play(FadeIn(l5, shift=DOWN), run_time=0.4)   #标签从下方淡入
        win.play(Create(rect, run_time=0.8), run_time=0.8)   #画出黄框
        win.play(
            Succession(
                Add(dot_a, run_time=0.0),           #参数 “run_time=0.0”：瞬间加入
                Wait(0.4),                          #间隔 0.4s
                Add(dot_b, dot_c, run_time=0.5),    #多于 1 个包成 Group，run_time=0.5 停留半秒
            ),
        )
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("uncreate", UncreateDemo),
    ("unwrite", UnwriteDemo),
    ("add", AddDemo),
]

PAIRS = [
    ("uncreate", ["uncreate"]),
    ("unwrite", ["unwrite"]),
    ("add", ["add"]),
]

PAGE = "02-反向擦除"


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
