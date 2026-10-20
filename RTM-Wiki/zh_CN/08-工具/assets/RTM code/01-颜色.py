# -*- coding: utf-8 -*-
"""01-颜色.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 01-颜色.py <片段名>...
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
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    Scene, Square, Text, VGroup,
    ManimColor, color_gradient,
    RED, YELLOW, BLUE, WHITE, GREY_B,
    UP, DOWN, RIGHT, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：ManimColor 的各种 value 形式 + to_hex ========================
class ColorParseDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-ManimColor", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        vals = [ManimColor("#FF8800"), ManimColor((255, 0, 0)), ManimColor(0x00FF00),   #十六进制串 / 0~255 整数元组 / 整数
                ManimColor("RED"), ManimColor("BLUE", alpha=0.4)]   #预定义色名 / 色名 + “alpha” 参数
        labs = ["'#FF8800'", "(255, 0, 0)", "0x00FF00", "'RED'", "alpha=0.4"]   #每块颜色的源码写法
        sw = VGroup(*[Square(side_length=1.0, stroke_width=2).set_fill(c, 1) for c in vals])   #五个色块，填满 0.9 不透明
        sw.arrange(RIGHT, buff=0.5).move_to(UP * 0.55)   #从左到右排成一行
        src = VGroup(*[Text(s, font_size=15, color=GREY_B).next_to(m, UP, buff=0.18)
                       for s, m in zip(labs, sw)])   #色块上方：value 写法
        hx = VGroup(*[Text(c.to_hex(), font_size=16, color=WHITE).next_to(m, DOWN, buff=0.18)
                      for c, m in zip(vals, sw)])   #色块下方：to_hex() 结果
        hint = Text("to_hex() -> '#RRGGBB'", font_size=22, color=YELLOW).to_edge(DOWN)   #说明下方那行是 to_hex 出来的
        self.add(sw, src, hx, hint)   #把色块、两行标签与说明放进场景
        win.play(FadeIn(sw), run_time=0.6)   #整排色块淡入
        win.play(FadeIn(src), FadeIn(hx), run_time=0.6)   #写法与十六进制结果两行标签淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：darker / lighter 变暗变亮 ====================================
class ColorDepthDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-darker-lighter", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        base = ManimColor("RED")   #基准色：预定义色名 “RED”
        cols = [base.lighter(0.6), base.lighter(0.3), base,   #往白方向提亮两档 + 原色
                base.darker(0.3), base.darker(0.6)]   #往黑方向压暗两档
        labs = ["lighter(0.6)", "lighter(0.3)", "'RED'", "darker(0.3)", "darker(0.6)"]   #每块的来源
        sw = VGroup(*[Square(side_length=1.1, stroke_width=2).set_fill(c, 1) for c in cols])   #五个色块
        sw.arrange(RIGHT, buff=0.45).move_to(UP * 0.55)   #从左到右排成一行
        src = VGroup(*[Text(s, font_size=15, color=GREY_B).next_to(m, UP, buff=0.2)
                       for s, m in zip(labs, sw)])   #色块上方标注 blend 写法
        note = Text("new object, original unchanged", font_size=20, color=YELLOW).to_edge(DOWN)   #强调“返回新对象”
        self.add(sw, src, note)   #把色块、标签与说明放进场景
        win.play(FadeIn(sw), run_time=0.6)   #整排色块淡入
        win.play(FadeIn(src), FadeIn(note), run_time=0.6)   #标签与说明淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：color_gradient 多色渐变序列 ==================================
class ColorGradientDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-color_gradient", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        ramp6 = color_gradient([RED, YELLOW, BLUE], 6)   #三段参考色展开成 6 个颜色
        sq6 = VGroup(*[Square(side_length=0.7, stroke_width=1).set_fill(c, 1) for c in ramp6])   #6 个大色块
        sq6.arrange(RIGHT, buff=0.08).move_to(UP * 1.0)   #排成一条粗渐变条
        lab6 = Text("color_gradient([RED, YELLOW, BLUE], 6)", font_size=17, color=GREY_B)
        lab6.next_to(sq6, UP, buff=0.25)   #粗条上方标注调用写法

        ramp14 = color_gradient([RED, YELLOW, BLUE], 14)   #同一组参考色展开成 14 个颜色
        sq14 = VGroup(*[Square(side_length=0.45, stroke_width=1).set_fill(c, 1) for c in ramp14])   #14 个小色块
        sq14.arrange(RIGHT, buff=0.05).move_to(DOWN * 0.7)   #排成一条细渐变条
        lab14 = Text("color_gradient([RED, YELLOW, BLUE], 14)", font_size=17, color=GREY_B)
        lab14.next_to(sq14, UP, buff=0.22)   #细条上方标注调用写法
        note = Text("same reference colors, different length_of_output", font_size=19,
                    color=YELLOW).to_edge(DOWN)   #两条只有个数不同
        self.add(sq6, lab6, sq14, lab14, note)   #把两条渐变条与说明放进场景
        win.play(FadeIn(sq6), FadeIn(lab6), run_time=0.6)   #粗条先出
        win.play(FadeIn(sq14), FadeIn(lab14), FadeIn(note), run_time=0.6)   #细条与说明再出
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("parse", ColorParseDemo),
    ("depth", ColorDepthDemo),
    ("gradient", ColorGradientDemo),
]

PAIRS = [
    ("parse", ["parse"]),
    ("depth", ["depth"]),
    ("gradient", ["gradient"]),
]

PAGE = "01-颜色"


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
