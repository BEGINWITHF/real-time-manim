# -*- coding: utf-8 -*-
"""01b-颜色进阶.md 两个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 01b-颜色进阶.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的两条样例视频（输出到上一级 assets/）。
"""
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    Scene, Square, Rectangle, Text, VGroup,
    ManimColor, average_color, interpolate_color, random_bright_color, random_color,
    RED, BLUE, YELLOW, WHITE, GREY_B,
    UP, DOWN, LEFT, RIGHT, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：interpolate 两色插值 =========================================
class ColorInterpolateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01b-interpolate", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        cols = [RED.interpolate(BLUE, i / 8) for i in range(9)]   #alpha 从 0 到 1 均分 9 档
        sq = VGroup(*[Square(side_length=0.85, stroke_width=1).set_fill(c, 1) for c in cols])   #9 个色块
        sq.arrange(RIGHT, buff=0.12).move_to(UP * 0.55)   #从左到右排成一条插值带
        sq[4].set_fill(interpolate_color(RED, BLUE, 0.5), 1)   #正中那块改用函数式写法，颜色与 interpolate 逐位相同
        lab = Text("RED.interpolate(BLUE, i / 8)", font_size=18, color=GREY_B)
        lab.next_to(sq, UP, buff=0.3)   #插值带上方标注调用写法
        l0 = Text("alpha=0  RED", font_size=16, color=GREY_B).next_to(sq[0], DOWN, buff=0.22)   #左端 = 自身
        l1 = Text("alpha=1  BLUE", font_size=16, color=GREY_B).next_to(sq[-1], DOWN, buff=0.22)   #右端 = 目标色
        lm = Text("interpolate_color(RED, BLUE, 0.5)", font_size=16, color=WHITE)
        lm.next_to(sq[4], DOWN, buff=0.55)   #正中那块 = 函数式写法的同一个结果
        self.add(lab, l0, l1, lm)   #先把标签放进场景（色块稍后逐块淡入）
        for m in sq:   #按 alpha 从小到大逐块淡入，肉眼看到颜色一路渐变
            win.play(FadeIn(m), run_time=0.12)
        win.play(FadeIn(lab), FadeIn(l0), FadeIn(l1), FadeIn(lm), run_time=0.5)   #三处标签淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：average / random 与 invert / opacity / contrasting ===========
class ColorHelpersDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01b-ColorHelpers", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        random.seed(7)   #固定随机种子，保证每次运行（含两引擎）取到同一批随机色
        # —— 第一行：三个取色函数 ——
        gen = [average_color(RED, BLUE), random_color(), random_bright_color()]   #平均色 / 随机色 / 亮随机色
        glab = ["average_color(RED, BLUE)", "random_color()", "random_bright_color()"]
        gsw = VGroup(*[Square(side_length=1.3, stroke_width=2).set_fill(c, 1) for c in gen])
        gsw.arrange(RIGHT, buff=1.2).move_to(UP * 1.7)   #横排三块，中间留出标签宽度
        gt = VGroup(*[Text(s, font_size=15, color=GREY_B).next_to(m, DOWN, buff=0.18)
                      for s, m in zip(glab, gsw)])   #函数名在色块下方
        gh = VGroup(*[Text(c.to_hex(), font_size=15, color=WHITE).next_to(m, UP, buff=0.18)
                      for c, m in zip(gen, gsw)])   #十六进制结果在色块上方
        # —— 第二行：三个实例方法 ——
        src = ManimColor("RED")
        meth = [src, src.invert(), src.opacity(0.35)]   #原色 / 逐通道取反 / 只换 alpha
        mlab = ["'RED'", "invert()", "opacity(0.35)"]
        msw = VGroup(*[Square(side_length=1.3, stroke_width=2).set_fill(c, 1) for c in meth])
        msw.arrange(RIGHT, buff=1.2).move_to(DOWN * 0.35)   #横排三块
        mt = VGroup(*[Text(s, font_size=15, color=GREY_B).next_to(m, DOWN, buff=0.18)
                      for s, m in zip(mlab, msw)])   #方法名在色块下方
        # —— 第三行：contrasting 自动挑可读的字色 ——
        dark = Rectangle(width=3.6, height=1.0, stroke_width=2).set_fill("#333333", 1)
        dark.set_stroke(GREY_B, 1).move_to(LEFT * 2.1 + DOWN * 2.5)   #深色底板
        dtx = Text("dark bg -> white text", font_size=20,
                   color=ManimColor("#333333").contrasting()).move_to(dark)   #深底上挑出白字
        lite = Rectangle(width=3.6, height=1.0, stroke_width=2).set_fill("#DDDDDD", 1)
        lite.set_stroke(GREY_B, 1).move_to(RIGHT * 2.1 + DOWN * 2.5)   #浅色底板
        ltx = Text("light bg -> black text", font_size=20,
                   color=ManimColor("#DDDDDD").contrasting()).move_to(lite)   #浅底上挑出黑字
        self.add(gt, gh, mt)   #标签先进场
        win.play(FadeIn(gsw), FadeIn(gt), FadeIn(gh), run_time=0.6)   #第一行色块与标签
        win.play(FadeIn(msw), FadeIn(mt), run_time=0.6)   #第二行色块与标签
        win.play(FadeIn(VGroup(dark, dtx, lite, ltx)), run_time=0.6)   #第三行对照底板
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("interpolate", ColorInterpolateDemo),
    ("helpers", ColorHelpersDemo),
]

PAIRS = [
    ("interpolate", ["interpolate"]),
    ("helpers", ["helpers"]),
]

PAGE = "01b-颜色进阶"


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
