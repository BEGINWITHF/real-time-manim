# -*- coding: utf-8 -*-
"""01-Create与画线族.md 四个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 01-Create与画线族.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的四条样例视频（输出到上一级 assets/）。
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
    Scene, Text, Circle, Square, VGroup,
    BLUE, GREEN, ORANGE, YELLOW, GREY_B,
    UP, DOWN,
    double_smooth, linear, smooth,
    Create, DrawBorderThenFill, FadeIn, ShowPartial, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：Create 的 lag_ratio 与公共参数全套 ===========================
class CreateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-Create", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("Create(mobject, lag_ratio=0.3, introducer=True,",
                  font_size=30, color=GREY_B)
        l2 = Text("         run_time=1.3, rate_func=smooth, remover=False, ...)",
                  font_size=30, color=GREY_B)
        lab1 = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #两行 “Create” 签名标签
        obj1 = Text("Create", font_size=52, color=BLUE).next_to(lab1, DOWN, buff=0.7)   #被逐笔画出的字
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)   #标签从下方淡入
        win.play(
            Create(obj1,                               #参数 “mobject”
                   lag_ratio=0.3,                      #参数 “lag_ratio”：字母依次画
                   introducer=True,                    #参数 “introducer”
                   run_time=1.3,                       #参数 “run_time”
                   rate_func=smooth,                   #参数 “rate_func”
                   remover=False,                      #参数 “remover”：画完保留
                   name="Create(Text)",                #参数 “name”
                   suspend_mobject_updating=True,      #参数 “suspend_mobject_updating”
                   reverse_rate_function=False,        #参数 “reverse_rate_function”
                   use_override=True),                 #参数 “use_override”
            run_time=1.3,
        )
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：Write 的 linear 与显式覆盖自动 run_time/lag_ratio ============
class WriteDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-Write", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l3 = Text("Write(vmobject, rate_func=linear, reverse=False,",
                  font_size=30, color=GREY_B)
        l4 = Text("        run_time=1.5, lag_ratio=0.2, stroke_width=2, ...)",
                  font_size=30, color=GREY_B)
        lab2 = VGroup(l3, l4).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #两行 “Write” 签名标签
        obj2 = Text("Hello Manim", font_size=48, color=GREEN).next_to(lab2, DOWN, buff=0.7)   #被写出的字
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)   #标签从下方淡入
        win.play(
            Write(obj2,                                #参数 “vmobject”
                  rate_func=linear,                    #参数 “rate_func”：匀速手写
                  reverse=False,                       #参数 “reverse”：正序书写
                  run_time=1.5,                        #参数 “run_time”：覆盖自动值
                  lag_ratio=0.2,                       #参数 “lag_ratio”：覆盖自动值
                  stroke_width=2,                      #参数 “stroke_width”
                  stroke_color=None),                  #参数 “stroke_color”
            run_time=1.5,
        )
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：DrawBorderThenFill 先轮廓、再填充 ============================
class BorderFillDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-DrawBorderThenFill", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l5 = Text("DrawBorderThenFill(vmobject, run_time=1.8,",
                  font_size=30, color=GREY_B)
        l6 = Text("    rate_func=double_smooth, stroke_width=6,",
                  font_size=30, color=GREY_B)
        l7 = Text("    stroke_color=BLUE, introducer=True)",
                  font_size=30, color=GREY_B)
        lab3 = VGroup(l5, l6, l7).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #三行签名标签
        obj3 = (Square(side_length=1.8, color=ORANGE)
                .set_fill(ORANGE, 1.0).next_to(lab3, DOWN, buff=0.6))   #带填充的橙色方块
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)   #标签从下方淡入
        win.play(
            DrawBorderThenFill(                        #参数 “vmobject”
                obj3,
                run_time=1.8,                          #参数 “run_time”
                rate_func=double_smooth,               #参数 “rate_func”：两段各一次平滑
                stroke_width=6,                        #参数 “stroke_width”：轮廓更粗
                stroke_color=BLUE,                     #参数 “stroke_color”：蓝色轮廓
                introducer=True),                      #参数 “introducer”
            run_time=1.8,
        )
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：ShowPartial 抽象基类直传一播（RTM 实测可播） =================
class ShowPartialDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-ShowPartial", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l8 = Text("ShowPartial(mobject, run_time=1.3, introducer=True)",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   #签名标签
        obj4 = Circle(radius=0.7, color=GREEN).next_to(l8, DOWN, buff=0.7)   #被逐帧画出的圆
        win.play(FadeIn(l8, shift=DOWN), run_time=0.4)   #标签从下方淡入
        win.play(
            ShowPartial(obj4,                          #参数 “mobject”
                        run_time=1.3,                  #参数 “run_time”
                        introducer=True),              #参数 “introducer”
            run_time=1.3,
        )
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("create", CreateDemo),
    ("write", WriteDemo),
    ("border_fill", BorderFillDemo),
    ("showpartial", ShowPartialDemo),
]

PAIRS = [
    ("create", ["create"]),
    ("write", ["write"]),
    ("border_fill", ["border_fill"]),
    ("showpartial", ["showpartial"]),
]

PAGE = "01-Create与画线族"


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
