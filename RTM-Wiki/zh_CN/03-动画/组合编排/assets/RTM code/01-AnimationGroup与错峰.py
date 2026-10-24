# -*- coding: utf-8 -*-
"""01-AnimationGroup与错峰.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 01-AnimationGroup与错峰.py <片段名>...
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    Scene, Text, VGroup, Square, Circle, Triangle, Dot,
    RED, BLUE, GREEN, PURPLE, GREY_B, YELLOW,
    UP, DOWN, LEFT, RIGHT,
    ApplyMethod, FadeIn, LaggedStart, LaggedStartMap, Write,
    linear, there_and_back,
)
from real_time_manim.vulkan_bind import MLWindow, AnimationGroup, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：AnimationGroup 依次启动 ======================================
class AnimationGroupDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-AnimationGroup", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("AnimationGroup(sq.animate.shift(UP),", font_size=30, color=GREY_B)
        l2 = Text("              ci.animate.shift(DOWN), tr.animate.shift(UP),", font_size=28, color=GREY_B)
        l3 = Text("              lag_ratio=0.5, rate_func=linear);  ag.run_time = 1.8", font_size=28, color=GREY_B)
        sig = VGroup(l1, l2, l3).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #签名标签
        sq = Square(side_length=1.2, color=RED).set_fill(RED, 0.5).shift(LEFT * 3.4 + DOWN * 2.1)   #红色方块
        ci = Circle(radius=0.65, color=BLUE).set_fill(BLUE, 0.5).shift(DOWN * 2.1)   #蓝色圆
        tr = Triangle(color=GREEN).scale(0.8).set_fill(GREEN, 0.5).shift(RIGHT * 3.4 + DOWN * 2.1)   #绿色三角
        win.play(FadeIn(sig, shift=DOWN), FadeIn(VGroup(sq, ci, tr)), run_time=0.4)   #标签与图形淡入
        ag = AnimationGroup(                                      #参数 “*animations”（3 个 .animate 构建器）
            sq.animate.shift(UP * 1.4),
            ci.animate.shift(DOWN * 1.4),
            tr.animate.shift(UP * 1.4),
            lag_ratio=0.5,                                        #参数 “lag_ratio”（红→蓝→绿依次启动）
            rate_func=linear,                                     #参数 “rate_func”（组级）
        )
        ag.run_time = 1.8                                         #参数 “run_time”（属性赋值整体拉伸到 1.8s）
        win.play(ag)   #三个动作依次启动
        win.play(Wait(0.6))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：LaggedStart 流水错峰 =========================================
class LaggedStartDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-LaggedStart", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("LaggedStart(*[FadeIn(d, shift=DOWN) for d in dots],", font_size=30, color=GREY_B)
        l2 = Text("            lag_ratio=0.3, run_time=1.6)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #签名标签
        cols = [RED, YELLOW, GREEN, BLUE, PURPLE]   #5 个轨道的颜色
        dots = VGroup(*[Dot(radius=0.18, color=c).shift(LEFT * 4.4 + RIGHT * 2.2 * i + DOWN * 1.8)   #5 个彩色点
                        for i, c in enumerate(cols)])
        win.play(FadeIn(sig, shift=DOWN), run_time=0.4)   #标签淡入
        win.play(LaggedStart(                                    #参数 “*animations”（5 个不同颜色的 FadeIn）
            *[FadeIn(d, shift=DOWN) for d in dots],
            lag_ratio=0.3,                                       #参数 “lag_ratio”（流水式错峰）
            run_time=1.6,                                        #参数 “run_time”
        ))
        win.play(Wait(0.6))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：LaggedStartMap 批量套动画 ====================================
class LaggedStartMapDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-LaggedStartMap", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("LaggedStartMap(ApplyMethod, words,", font_size=30, color=GREY_B)
        l2 = Text("   lambda m: (m.set_color, YELLOW),", font_size=30, color=GREY_B)
        l3 = Text("   lag_ratio=0.15, run_time=2.0, rate_func=there_and_back)", font_size=28, color=GREY_B)
        sig = VGroup(l1, l2, l3).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #签名标签
        words = Text("manim", font_size=64, color=GREY_B).shift(DOWN * 1.9)   #被逐字染色的词
        win.play(FadeIn(sig, shift=DOWN), FadeIn(words), run_time=0.4)   #标签与词淡入
        win.play(LaggedStartMap(                                 #参数 “animation_class / mobject / arg_creator”
            ApplyMethod, words,
            lambda m: (m.set_color, YELLOW),                     #参数 “arg_creator”（submob -> 参数元组）
            lag_ratio=0.15,                                      #参数 “lag_ratio”
            run_time=2.0,                                        #参数 “run_time”
            rate_func=there_and_back,                            #参数 “**kwargs”（透传给每个子动画）
        ))
        win.play(Wait(0.6))   #停留看结果
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("animationgroup", AnimationGroupDemo),
    ("laggedstart", LaggedStartDemo),
    ("laggedstartmap", LaggedStartMapDemo),
]

PAIRS = [
    ("animationgroup", ["animationgroup"]),
    ("laggedstart", ["laggedstart"]),
    ("laggedstartmap", ["laggedstartmap"]),
]

PAGE = "01-AnimationGroup与错峰"


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
