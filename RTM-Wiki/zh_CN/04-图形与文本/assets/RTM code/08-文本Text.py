# -*- coding: utf-8 -*-
"""08-文本Text.md 四个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 08-文本Text.py <样例名>...
不带参数就渲染全部样例，并拼出页面里的四条样例视频（输出到 assets/RTM output/）。
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
    Scene, Text, MarkupText, Paragraph, register_font,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


def cap(text, mob, buff=0.35, color=GREY_B, size=18):
    return Text(text, font_size=size, color=color).next_to(mob, DOWN, buff=buff)


# ===== 样例 1：Text —— 普通文本（字体 / 字号 / 粗细 / 斜体 / 行距 / 分色）==
class TextDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("08-Text", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 默认：单行文本 ——
        t1 = Text("Hello RTM").move_to([0, 1.6, 0])   #参数 “text”
        win.play(Write(t1), FadeIn(cap('Text("Hello RTM")', t1)), run_time=0.6)

        # —— font / font_size / weight / slant ——
        t2 = Text("Arial 40 bold italic", font="Arial", font_size=40,
                  weight="BOLD", slant="ITALIC").move_to([0, 0.5, 0])   #参数 “font / font_size / weight / slant”
        win.play(Write(t2), FadeIn(cap('font="Arial" weight=BOLD slant=ITALIC', t2)), run_time=0.7)

        # —— color / line_spacing：两行文本的整体颜色与行距 ——
        t3 = Text("first line\nsecond line", font_size=34, color=TEAL,
                  line_spacing=1.2).move_to([0, -1.0, 0])   #参数 “color / line_spacing”
        win.play(Write(t3), FadeIn(cap("color=TEAL, line_spacing=1.2", t3)), run_time=0.7)

        # —— t2c：把指定子串单独上色 ——
        t4 = Text("red green blue", font_size=34,
                  t2c={"red": RED, "green": GREEN, "blue": BLUE}).move_to([0, -2.3, 0])   #参数 “t2c”
        win.play(Write(t4), FadeIn(cap('t2c={"red": RED, …}', t4)), run_time=0.7)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：MarkupText —— Pango 标记文本 ===============================
class MarkupDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("08-MarkupText", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 标记语法：<b> / <i> / <span foreground=…> ——
        m1 = MarkupText('<b>bold</b> and <i>italic</i>',
                        font_size=36).move_to([0, 1.3, 0])   #参数 “text（Pango 标记）”
        win.play(Write(m1), FadeIn(cap('MarkupText("<b>…</b> <i>…</i>")', m1)), run_time=0.8)

        # —— color / font_size：整体颜色与字号（标记里的颜色优先）——
        m2 = MarkupText('colored markup text',
                        font_size=32, color=TEAL).move_to([0, 0.0, 0])   #参数 “color / font_size”
        win.play(Write(m2), FadeIn(cap("color=TEAL", m2)), run_time=0.8)

        # —— line_spacing / justify：多行与对齐 ——
        m3 = MarkupText("line one\nline two is longer", font_size=30,
                        line_spacing=1.4).move_to([0, -1.5, 0])   #参数 “line_spacing”
        win.play(Write(m3), FadeIn(cap("line_spacing=1.4", m3)), run_time=0.8)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：Paragraph —— 多段文本，逐行对齐 ============================
class ParagraphDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("08-Paragraph", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 每个位置参数是一段；alignment 控制整块对齐 ——
        p1 = Paragraph("first paragraph", "second paragraph", "third",
                       alignment="left", font_size=32).move_to([-0.6, 0.9, 0])   #参数 “*text / alignment”
        win.play(Write(p1), FadeIn(cap('alignment="left"', p1)), run_time=0.8)

        # —— line_spacing：段间距 ——
        p2 = Paragraph("tight", "spacing", line_spacing=0.6,
                       alignment="center", font_size=32).move_to([-0.6, -1.4, 0])   #参数 “line_spacing”
        win.play(Write(p2), FadeIn(cap("line_spacing=0.6", p2)), run_time=0.8)

        # —— **kwargs 透传：颜色 / 字体 ——
        p3 = Paragraph("colored", "paragraph", font_size=32, color=ORANGE,
                       font="Arial").move_to([2.6, -1.4, 0])   #参数 “**kwargs（color / font）”
        win.play(Write(p3), FadeIn(cap("color=ORANGE, font=Arial", p3)), run_time=0.8)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：register_font —— 临时注册字体文件 ==========================
class RegisterFontDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("08-register_font", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 用法：with 块内注册字体文件，块内构造的 Text 就能用这个族名 ——
        font_file = r"C:\Windows\Fonts\arial.ttf"   #参数 “font_file”：字体文件路径
        with register_font(font_file):   #参数 “font_file”
            t1 = Text("Registered: Arial", font="Arial", font_size=44).move_to([0, 0.9, 0])
            win.play(Write(t1), FadeIn(cap("with register_font(arial.ttf): Text(..., font=\"Arial\")", t1)), run_time=0.8)

        # —— 块外用同一族名：字体缓存里已有，照常能排 ——
        t2 = Text("outside the with-block", font="Arial", font_size=36,
                  color=TEAL).move_to([0, -0.8, 0])
        win.play(Write(t2), FadeIn(cap("块外沿用同一族名", t2)), run_time=0.8)

        # —— 不注册时的对照：用系统里没有的族名会打警告并回退 ——
        t3 = Text("fallback family", font_size=36, color=GREY_B).move_to([0, -2.2, 0])
        win.play(Write(t3), FadeIn(cap("未注册的族名会回退到默认字体", t3)), run_time=0.8)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("text", TextDemo),
    ("markup", MarkupDemo),
    ("paragraph", ParagraphDemo),
    ("registerfont", RegisterFontDemo),
]

PAIRS = [
    ("text", ["text"]),
    ("markup", ["markup"]),
    ("paragraph", ["paragraph"]),
    ("registerfont", ["registerfont"]),
]

PAGE = "08-文本Text"


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
