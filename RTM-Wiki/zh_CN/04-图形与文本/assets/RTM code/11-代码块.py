# -*- coding: utf-8 -*-
"""11-代码块.md 两个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 11-代码块.py <样例名>...
不带参数就渲染全部样例，并拼出页面里的两条样例视频（输出到 assets/RTM output/）。
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
    Scene, Code, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B,
    UP, DOWN, LEFT, RIGHT,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


def cap(text, mob, buff=0.35, color=GREY_B, size=18):
    return Text(text, font_size=size, color=color).next_to(mob, DOWN, buff=buff)


# ===== 样例 1：Code —— 语法高亮的代码块 ====================================
class CodeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("11-Code", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— code_string + language：默认 tab_width=4、带行号、rectangle 背景 ——
        c1 = Code(code_string="def f(x):\n    return x ** 2\n\nprint(f(3))",
                  language="python")   #参数 “code_string / language”
        c1.scale(0.75).move_to([0, 0.9, 0])
        win.play(Write(c1), FadeIn(cap('language="python"', c1)), run_time=0.8)

        # —— tab_width / add_line_numbers / line_numbers_from ——
        c2 = Code(code_string="a = 1\nif a:\n\tprint(a)",
                  language="python", tab_width=8,   #参数 “tab_width”
                  add_line_numbers=True, line_numbers_from=10)   #参数 “add_line_numbers / line_numbers_from”
        c2.scale(0.75).move_to([-3.6, -1.9, 0])
        win.play(Write(c2), FadeIn(cap("tab_width=8, 行号从 10", c2)), run_time=0.7)

        # —— background="window" + formatter_style：窗口式背景与配色 ——
        c3 = Code(code_string="x = [1, 2, 3]\nprint(sum(x))",
                  language="python", background="window",   #参数 “background”
                  formatter_style="monokai")   #参数 “formatter_style”
        c3.scale(0.75).move_to([3.4, -1.9, 0])
        win.play(Write(c3), FadeIn(cap('background="window", style="monokai"', c3)), run_time=0.7)

        # —— background_config / paragraph_config：透传样式 ——
        c4 = Code(code_string="s = 'hi'",
                  language="python",
                  background_config={"stroke_color": TEAL, "fill_opacity": 0.3},   #参数 “background_config”
                  paragraph_config={"font": "monospace"})   #参数 “paragraph_config”
        c4.scale(0.75).move_to([0, -3.2, 0])
        win.play(Write(c4), run_time=0.6)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：Code.get_styles_list —— 可用的配色方案 ======================
class StylesDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("11-Code.get_styles_list", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        styles = Code.get_styles_list()   #方法 “get_styles_list()”：返回全部可用配色名
        # —— 前六个名字逐个上屏（也说明数量远多于常用的那几个）——
        names = VGroup(*[Text(s, font_size=22, color=GREY_B) for s in styles[:6]])
        names.arrange(DOWN, buff=0.18).move_to([-4.2, 0.4, 0])
        cnt = Text("共 %d 种" % len(styles), font_size=24, color=TEAL).next_to(names, DOWN, buff=0.4)
        win.play(FadeIn(names), FadeIn(cnt), run_time=0.7)

        # —— 同一个代码块换三种 style，直观看出差别 ——
        for i, style in enumerate(("vim", "monokai", "friendly")):
            code = Code(code_string="def f(x):\n    return x ** 2",
                        language="python", formatter_style=style)   #参数 “formatter_style”
            code.scale(0.6).move_to([0.6 + (i % 2) * 3.2, 0.9 - i * 1.9, 0])
            win.play(Write(code), FadeIn(cap(style, code, buff=0.2, size=16)), run_time=0.6)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("code", CodeDemo),
    ("styles", StylesDemo),
]

PAIRS = [
    ("code", ["code"]),
    ("styles", ["styles"]),
]

PAGE = "11-代码块"


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
