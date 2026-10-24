# -*- coding: utf-8 -*-
"""09-LaTeX公式.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 09-LaTeX公式.py <样例名>...
不带参数就渲染全部样例，并拼出页面里的三条样例视频（输出到 assets/RTM output/）。
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

from real_time_manim import (
    Scene, Tex, MathTex, SingleStringMathTex, Text,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


def cap(text, mob, buff=0.35, color=GREY_B, size=18):
    return Text(text, font_size=size, color=color).next_to(mob, DOWN, buff=buff)


# ===== 样例 1：Tex —— 文本与公式混排 ======================================
class TexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("09-Tex", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 默认：正文里用 $...$ 写公式，font_size 控制整体字号 ——
        t1 = Tex(r"The area is $A = \pi r^2$.", font_size=40).move_to([0, 1.5, 0])   #参数 “*tex_strings / font_size”
        win.play(Write(t1), FadeIn(cap("Tex(...font_size=40)", t1)), run_time=0.7)

        # —— color：整体颜色（正文与公式一起变）——
        t2 = Tex(r"$E = mc^2$", font_size=48, color=TEAL).move_to([0, 0.2, 0])   #参数 “color”
        win.play(Write(t2), FadeIn(cap("color=TEAL", t2)), run_time=0.7)

        # —— tex_environment：换一个数学环境（默认是 document）——
        t3 = Tex(r"a + b = c", font_size=36,
                 tex_environment="align*").move_to([0, -1.4, 0])   #参数 “tex_environment”
        win.play(Write(t3), FadeIn(cap('tex_environment="align*"', t3)), run_time=0.7)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：MathTex —— 纯公式、可拆片段 =================================
class MathTexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("09-MathTex", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 默认：每个位置参数是一个片段，单个字符串可含多个 $...$ ——
        m1 = MathTex(r"x^2 + y^2 = z^2", font_size=48).move_to([0, 1.4, 0])   #参数 “*tex_strings”
        win.play(Write(m1), FadeIn(cap("MathTex(r\"x^2 + y^2 = z^2\")", m1)), run_time=0.8)

        # —— 显式分片：每片独立单位，便于后面单片上色 ——
        m2 = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2", font_size=48).move_to([0, 0.0, 0])   #参数 “{{ }} 分片”
        m2[0].set_color(RED)
        m2[2].set_color(GREEN)
        m2[4].set_color(BLUE)
        win.play(Write(m2), FadeIn(cap("每片独立上色", m2)), run_time=0.8)

        # —— color / font_size：整体样式 ——
        m3 = MathTex(r"\int_0^1 x^2\,dx = \frac{1}{3}", font_size=44,
                     color=ORANGE).move_to([0, -1.6, 0])   #参数 “color / font_size”
        win.play(Write(m3), FadeIn(cap("color=ORANGE, font_size=44", m3)), run_time=0.8)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：SingleStringMathTex —— 单个公式串 ===========================
class SingleStringDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("09-SingleStringMathTex", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 只接一个字符串：不拆片段，最轻量的公式对象 ——
        s1 = SingleStringMathTex(r"\sum_{i=1}^{n} i = \frac{n(n+1)}{2}",
                                 font_size=44).move_to([0, 1.2, 0])   #参数 “tex_string”
        win.play(Write(s1), FadeIn(cap("SingleStringMathTex(求和)", s1)), run_time=0.8)

        # —— 与 MathTex 的差别：它只有一片，不能按片段取 ——
        s2 = SingleStringMathTex(r"[a, b] = [c, d]", font_size=44,
                                 color=TEAL).move_to([0, -0.4, 0])
        win.play(Write(s2), FadeIn(cap("整串一个对象（color=TEAL）", s2)), run_time=0.8)

        # —— font_size 再变一次，看缩放 ——
        s3 = SingleStringMathTex(r"f(x) = e^{-x^2}", font_size=64).move_to([0, -2.2, 0])
        win.play(Write(s3), FadeIn(cap("font_size=64", s3)), run_time=0.8)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("tex", TexDemo),
    ("mathtex", MathTexDemo),
    ("singlestring", SingleStringDemo),
]

PAIRS = [
    ("tex", ["tex"]),
    ("mathtex", ["mathtex"]),
    ("singlestring", ["singlestring"]),
]

PAGE = "09-LaTeX公式"


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
