# -*- coding: utf-8 -*-
"""10-Typst.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 10-Typst.py <样例名>...
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
    Scene, Typst, TypstMath, MathTex, Text,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


def cap(text, mob, buff=0.35, color=GREY_B, size=18):
    return Text(text, font_size=size, color=color).next_to(mob, DOWN, buff=buff)


# ===== 样例 1：Typst —— 用 Typst 排版文本/公式 ============================
class TypstDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("10-Typst", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 默认：font_size=48、居中；Typst 语法（$...$ 里是数学）——
        t1 = Typst("The area is $pi r^2$", font_size=40).move_to([0, 1.4, 0])   #参数 “typst_code / font_size”
        win.play(Write(t1), FadeIn(cap("Typst(...font_size=40)", t1)), run_time=0.7)

        # —— color / stroke_width：整体颜色与描边 ——
        t2 = Typst("bold text #text(fill: red)[red]", font_size=40,
                   color=TEAL, stroke_width=1).move_to([0, -0.2, 0])   #参数 “color / stroke_width”
        win.play(Write(t2), FadeIn(cap("color=TEAL, stroke_width=1", t2)), run_time=0.7)

        # —— typst_preamble：给整块代码加前置定义（这里定义颜色）——
        t3 = Typst("#let hot = rgb(\"#ff6600\")\nA #text(fill: hot)[hot] word",
                   font_size=36, typst_preamble='#set text(size: 12pt)')   #参数 “typst_preamble”
        t3.move_to([0, -1.8, 0])
        win.play(Write(t3), FadeIn(cap("typst_preamble 前置定义", t3)), run_time=0.7)

        # —— should_center / height：不居中、按高度缩放 ——
        t4 = Typst("H", font_size=72, should_center=False, height=1.2)   #参数 “should_center / height”
        t4.move_to([4.6, 1.4, 0])
        win.play(Write(t4), FadeIn(cap("height=1.2", t4)), run_time=0.6)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：TypstMath —— 只写数学表达式 =================================
class TypstMathDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("10-TypstMath", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 默认：直接写表达式（会自动包进 $ ... $）——
        m1 = TypstMath("sum_(i=1)^n i = (n(n+1))/2", font_size=44).move_to([0, 1.4, 0])   #参数 “math_expression”
        win.play(Write(m1), FadeIn(cap("TypstMath(求和公式)", m1)), run_time=0.8)

        # —— 其余参数透传给 Typst：color / font_size ——
        m2 = TypstMath("integral_0^1 x^2 dif x = 1/3", font_size=44,
                       color=ORANGE).move_to([0, -0.4, 0])   #参数 “**kwargs（color）”
        win.play(Write(m2), FadeIn(cap("color=ORANGE", m2)), run_time=0.8)

        # —— 分式/根号/矩阵 ——
        m3 = TypstMath("mat(1, 2; 3, 4)", font_size=40).move_to([-3.4, -2.2, 0])
        m4 = TypstMath("sqrt(2) approx 1.414", font_size=40).move_to([2.6, -2.2, 0])
        win.play(Write(m3), FadeIn(cap("mat(1, 2; 3, 4)", m3)), run_time=0.7)
        win.play(Write(m4), FadeIn(cap("sqrt(2)", m4)), run_time=0.7)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：自动路由 —— MathTex 在 RTM 下走 Typst ======================
class AutoRouteDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("10-Typst 自动路由", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— MathTex 照常写 LaTeX，RTM 内部转成 Typst 排版（无需本机 LaTeX）——
        mt = MathTex(r"\frac{a}{b} + \sqrt{x}").move_to([0, 1.0, 0])   #参数 “MathTex（自动路由）”
        win.play(Write(mt), FadeIn(cap("MathTex(\\frac{a}{b}+\\sqrt{x})", mt)), run_time=0.8)

        # —— 同一公式用 TypstMath 写，形状与位置一致 ——
        tm = TypstMath("a/b + sqrt(x)", font_size=48).move_to([0, -0.6, 0])
        win.play(Write(tm), FadeIn(cap("TypstMath(a/b + sqrt(x))", tm)), run_time=0.8)

        # —— MathTex 的片段上色等接口照常可用 ——
        mt2 = MathTex(r"E = mc^2").move_to([0, -2.2, 0])
        mt2[0].set_color(YELLOW)
        win.play(Write(mt2), FadeIn(cap("MathTex 片段上色照常", mt2)), run_time=0.8)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("typst", TypstDemo),   # RTM-only
    ("typstmath", TypstMathDemo),   # RTM-only
    ("autoroute", AutoRouteDemo),   # RTM-only
]

PAIRS = [
    ("typst", ["typst"]),   # RTM-only
    ("typstmath", ["typstmath"]),   # RTM-only
    ("autoroute", ["autoroute"]),   # RTM-only
]

PAGE = "10-Typst"


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
