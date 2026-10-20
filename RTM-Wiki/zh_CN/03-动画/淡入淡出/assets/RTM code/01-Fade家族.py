# -*- coding: utf-8 -*-
"""01-Fade家族.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 01-Fade家族.py <片段名>...
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
    Scene, Square, Circle, Triangle, Text, VGroup,
    BLUE, GREEN, RED, YELLOW, GREY_B,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    smooth, linear,
    AnimationGroup, Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：FadeIn 的 shift / scale / target_position ===================
class FadeInDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-FadeIn", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("FadeIn(mobject, shift=DOWN, scale=0.5, run_time=1.1,",
                  font_size=30, color=GREY_B)
        l2 = Text("        lag_ratio=0.0, name='FadeIn')   FadeIn(c, target_position=ORIGIN)",
                  font_size=30, color=GREY_B)
        lab1 = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #两行 “FadeIn” 签名标签
        sq = Square(side_length=1.3, color=BLUE).next_to(lab1, DOWN, buff=0.6).shift(LEFT * 2.2)   #演示对象 “sq”
        ci = Circle(radius=0.6, color=GREEN).next_to(lab1, DOWN, buff=0.6).shift(RIGHT * 2.2)   #演示对象 “ci”
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)   #标签从下方淡入
        win.play(
            FadeIn(sq,                               #“*mobjects” 之一
                   shift=DOWN,                       #参数 “shift”：从下方进入
                   scale=0.5,                        #参数 “scale”：从半大长回原大
                   run_time=1.1,                     #参数 “run_time”
                   lag_ratio=0.0,                    #参数 “lag_ratio”
                   name="FadeIn(Square)",            #参数 “name”
                   suspend_mobject_updating=True,    #参数 “suspend_mobject_updating”
                   reverse_rate_function=False,      #参数 “reverse_rate_function”
                   use_override=True),               #参数 “use_override”
            FadeIn(ci,                               #“*mobjects” 之二（另一实例）
                   target_position=ORIGIN,           #参数 “target_position”：从中心飘来
                   run_time=1.1),                    #参数 “run_time”
            run_time=1.1, rate_func=smooth,          #play 级 “rate_func”
        )
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：FadeOut 的 shift / scale / target_position ==================
class FadeOutDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-FadeOut", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("FadeIn(mobject, shift=DOWN, scale=0.5, run_time=1.1,",
                  font_size=30, color=GREY_B)
        l2 = Text("        lag_ratio=0.0, name='FadeIn')   FadeIn(c, target_position=ORIGIN)",
                  font_size=30, color=GREY_B)
        lab1 = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #上一段演示留下的签名标签
        sq = Square(side_length=1.3, color=BLUE).next_to(lab1, DOWN, buff=0.6).shift(LEFT * 2.2)   #待淡出的对象 “sq”
        ci = Circle(radius=0.6, color=GREEN).next_to(lab1, DOWN, buff=0.6).shift(RIGHT * 2.2)   #待淡出的对象 “ci”
        self.add(lab1, sq, ci)   #演示对象先静态进场景（本样例的主角是 “FadeOut”）
        l3 = Text("FadeOut(sq, shift=UP, run_time=1.0)   FadeOut(ci, scale=0.3, ...)",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   #换行标签（与 lab1 同槽位）
        win.play(FadeOut(lab1), FadeIn(l3, shift=DOWN), run_time=0.4)   #旧标签淡出、新标签就地换上
        win.play(
            FadeOut(sq,                              #“*mobjects” 之一
                    shift=UP,                        #参数 “shift”：朝上飘出
                    run_time=1.0,                    #参数 “run_time”
                    lag_ratio=0.0),                  #参数 “lag_ratio”
            FadeOut(ci,                              #“*mobjects” 之二
                    scale=0.3,                       #参数 “scale”：淡出时缩到 0.3 倍
                    target_position=ORIGIN,          #参数 “target_position”：朝中心淡走
                    run_time=1.0,                    #参数 “run_time”
                    name="FadeOut(Circle)"),         #参数 “name”
            run_time=1.0, rate_func=linear,          #play 级 “rate_func”
        )
        win.play(FadeOut(l3), run_time=0.4)   #标签也淡出
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：手册「换页组合」AnimationGroup 一换一 ========================
class SwapGroupDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-AnimationGroup swap", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l4 = Text("AnimationGroup(FadeOut(x, shift=UP), FadeIn(y1, y2, shift=UP))",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   #组合签名标签
        x = (Square(side_length=1.2, color=RED).set_fill(RED, 0.6)
             .next_to(l4, DOWN, buff=0.7).shift(LEFT * 2.0))   #要被换下的红方块 “x”
        ya = Circle(radius=0.5, color=YELLOW).move_to(x)   #换上对象一：叠在 “x” 原位
        yb = (Triangle(color=GREEN).scale(0.9)
              .next_to(l4, DOWN, buff=0.7).shift(RIGHT * 2.0))   #换上对象二
        win.play(FadeIn(l4, shift=DOWN), run_time=0.4)   #标签从下方淡入
        win.play(Create(x), run_time=0.7)   #先画出要被换下的方块
        win.play(
            AnimationGroup(
                FadeOut(x, shift=UP),                #换下：朝上飘出
                FadeIn(ya, yb, shift=UP),            #换上：新对象从下方淡入
                lag_ratio=0.0,                       #参数 “lag_ratio”：同起同落
            ),
            run_time=1.2,
        )
        win.play(Wait(0.8))   #进行 0.8s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("fadein", FadeInDemo),
    ("fadeout", FadeOutDemo),
    ("swap", SwapGroupDemo),
]

PAIRS = [
    ("fadein", ["fadein"]),
    ("fadeout", ["fadeout"]),
    ("swap", ["swap"]),
]

PAGE = "01-Fade家族"


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
