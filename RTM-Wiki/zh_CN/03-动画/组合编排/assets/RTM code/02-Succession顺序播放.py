# -*- coding: utf-8 -*-
"""02-Succession顺序播放.md 两个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 02-Succession顺序播放.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的两条样例视频（输出到上一级 assets/）。
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
    Scene, Text, VGroup, Square, Circle,
    RED, BLUE, GREEN, GREY_B, YELLOW,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, Write, smooth,
)
from real_time_manim.vulkan_bind import MLWindow, Succession, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：四段串行一次 play 排完 =======================================
class SuccessionDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02-Succession", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("Succession(sq1.animate.move_to(sq2),", font_size=30, color=GREY_B)
        l2 = Text("           sq2.animate.move_to(sq3), Wait(0.6),", font_size=30, color=GREY_B)
        l3 = Text("           sq3.animate(run_time=0.8).set_color(RED))", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2, l3).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #签名标签
        sq1 = Square(side_length=1.1, color=BLUE).set_fill(BLUE, 0.5).shift(LEFT * 3.6 + DOWN * 2.1)   #蓝色方块
        sq2 = Square(side_length=1.1, color=GREEN).set_fill(GREEN, 0.5).shift(DOWN * 2.1)   #绿色方块
        sq3 = Square(side_length=1.1, color=GREY_B).shift(RIGHT * 3.6 + DOWN * 2.1)   #灰色方块
        win.play(FadeIn(sig, shift=DOWN), FadeIn(VGroup(sq1, sq2, sq3)), run_time=0.4)   #标签与方块淡入
        win.play(Succession(                                      #参数 “*animations”（4 个子动画）
            sq1.animate(run_time=1.0).move_to(sq2.get_center()),
            sq2.animate(run_time=1.0).move_to(sq3.get_center()),
            Wait(0.6),                                            #参数 “*animations”（Wait 直接当空段）
            sq3.animate(run_time=0.8).set_color(RED),
        ))
        win.play(Wait(0.6))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：rate_func 作用于整条串行轴 ===================================
class SuccessionRateFuncDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02-SuccessionRateFunc", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("Succession(a.animate.shift(UP), b.animate.shift(UP),", font_size=30, color=GREY_B)
        l2 = Text("           rate_func=smooth)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #签名标签
        a = Circle(radius=0.55, color=RED).set_fill(RED, 0.5).shift(LEFT * 2.2 + DOWN * 2.3)   #红色圆
        b = Circle(radius=0.55, color=BLUE).set_fill(BLUE, 0.5).shift(RIGHT * 2.2 + DOWN * 2.3)   #蓝色圆
        win.play(FadeIn(sig, shift=DOWN), FadeIn(VGroup(a, b)), run_time=0.4)   #标签与圆淡入
        win.play(Succession(                                      #参数 “rate_func”（作用于整条串行时间轴）
            a.animate(run_time=1.0).shift(UP * 1.6),
            b.animate(run_time=1.0).shift(UP * 1.6),
            rate_func=smooth,
        ))
        win.play(Wait(0.6))   #停留看结果
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("succession", SuccessionDemo),
    ("ratefunc", SuccessionRateFuncDemo),
]

PAIRS = [
    ("succession", ["succession"]),
    ("ratefunc", ["ratefunc"]),
]

PAGE = "02-Succession顺序播放"


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
