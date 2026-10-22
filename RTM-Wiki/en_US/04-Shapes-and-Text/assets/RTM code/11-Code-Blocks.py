# -*- coding: utf-8 -*-
"""Full source for the two samples in 11-Code-Blocks.md (identical to the code blocks in the page).

Usage: python 11-Code-Blocks.py <sample names>...
With no arguments it renders every sample and concatenates the page's two sample videos (written to assets/RTM output/).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                   os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

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


# ===== Sample 1: Code —— syntax-highlighted code blocks ===================
class CodeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("11-Code", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— code_string + language: default tab_width=4, line numbers on, rectangle background ——
        c1 = Code(code_string="def f(x):\n    return x ** 2\n\nprint(f(3))",
                  language="python")   # the "code_string / language" parameters
        c1.scale(0.75).move_to([0, 0.9, 0])
        win.play(Write(c1), FadeIn(cap('language="python"', c1)), run_time=0.8)

        # —— tab_width / add_line_numbers / line_numbers_from ——
        c2 = Code(code_string="a = 1\nif a:\n\tprint(a)",
                  language="python", tab_width=8,   # the "tab_width" parameter
                  add_line_numbers=True, line_numbers_from=10)   # the "add_line_numbers / line_numbers_from" parameters
        c2.scale(0.75).move_to([-3.6, -1.9, 0])
        win.play(Write(c2), FadeIn(cap("tab_width=8, line numbers from 10", c2)), run_time=0.7)

        # —— background="window" + formatter_style: a window-style background and colour scheme ——
        c3 = Code(code_string="x = [1, 2, 3]\nprint(sum(x))",
                  language="python", background="window",   # the "background" parameter
                  formatter_style="monokai")   # the "formatter_style" parameter
        c3.scale(0.75).move_to([3.4, -1.9, 0])
        win.play(Write(c3), FadeIn(cap('background="window", style="monokai"', c3)), run_time=0.7)

        # —— background_config / paragraph_config: passing styles through ——
        c4 = Code(code_string="s = 'hi'",
                  language="python",
                  background_config={"stroke_color": TEAL, "fill_opacity": 0.3},   # the "background_config" parameter
                  paragraph_config={"font": "monospace"})   # the "paragraph_config" parameter
        c4.scale(0.75).move_to([0, -3.2, 0])
        win.play(Write(c4), run_time=0.6)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: Code.get_styles_list —— the available colour schemes =====
class StylesDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("11-Code.get_styles_list", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        styles = Code.get_styles_list()   # the "get_styles_list()" method: returns every available colour-scheme name
        # —— the first six names go on screen one by one (which also shows there are far more than the usual few) ——
        names = VGroup(*[Text(s, font_size=22, color=GREY_B) for s in styles[:6]])
        names.arrange(DOWN, buff=0.18).move_to([-4.2, 0.4, 0])
        cnt = Text("%d styles" % len(styles), font_size=24, color=TEAL).next_to(names, DOWN, buff=0.4)
        win.play(FadeIn(names), FadeIn(cnt), run_time=0.7)

        # —— the same code block in three styles, to see the difference at a glance ——
        for i, style in enumerate(("vim", "monokai", "friendly")):
            code = Code(code_string="def f(x):\n    return x ** 2",
                        language="python", formatter_style=style)   # the "formatter_style" parameter
            code.scale(0.6).move_to([0.6 + (i % 2) * 3.2, 0.9 - i * 1.9, 0])
            win.play(Write(code), FadeIn(cap(style, code, buff=0.2, size=16)), run_time=0.6)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


SCENES = [
    ("code", CodeDemo),
    ("styles", StylesDemo),
]

PAIRS = [
    ("code", ["code"]),
    ("styles", ["styles"]),
]

PAGE = "11-Code-Blocks"


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
