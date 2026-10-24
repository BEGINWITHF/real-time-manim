# -*- coding: utf-8 -*-
"""01-等待速率与变速.md 五个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 01-等待速率与变速.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的五条样例视频（输出到上一级 assets/）。
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
    Scene, Text, VGroup, Square, Dot, Line,
    BLUE, GREEN, GREY_B, ORANGE, RED, YELLOW,
    UP, DOWN, LEFT, RIGHT,
    Animation, AnimationGroup, ChangeSpeed, FadeIn, FadeOut, Write,
)
from real_time_manim import (
    exponential_decay, linear, rush_from, rush_into, smooth,
    squish_rate_func, there_and_back, wiggle,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：Wait 的纯等待 ================================================
class WaitDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-Wait", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        lab = Text("win.play(Wait(1.0))   # run_time=1.0s",
                   font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   #签名标签
        sq = Square(side_length=1.1, color=BLUE).set_fill(BLUE, 0.5).next_to(lab, DOWN, buff=0.6)   #等待期间的蓝方块
        txt = Text("waiting...", font_size=30, color=GREY_B).next_to(sq, DOWN, buff=0.4)   #等待提示文字
        win.play(FadeIn(lab, shift=DOWN), FadeIn(sq), FadeIn(txt), run_time=0.4)   #标签与方块淡入
        win.play(Wait(1.0))   #参数 “run_time”：什么都不做地等 1 秒
        win.play(FadeOut(VGroup(lab, sq, txt)), run_time=0.4)   #整组淡出收场
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：ChangeSpeed 按百分比配速 =====================================
class ChangeSpeedDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-ChangeSpeed", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        lab3 = Text("ChangeSpeed(AnimationGroup(a.shift, b.shift),",
                    font_size=30, color=GREY_B)
        lab4 = Text("  speedinfo={0.3:1, 0.5:0.25, 1:2}, rate_func=linear)",
                    font_size=30, color=GREY_B)
        lab = VGroup(lab3, lab4).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #两行签名标签
        a = Dot(radius=0.14, color=RED).move_to(LEFT * 3.2 + DOWN * 1.2)
        b = Dot(radius=0.14, color=BLUE).move_to(RIGHT * 3.2 + DOWN * 1.2)
        trk = Line(LEFT * 3.2 + DOWN * 1.2, RIGHT * 3.2 + DOWN * 1.2, stroke_width=2, color=GREY_B)
        trk.set_stroke(opacity=0.4)
        win.play(FadeIn(lab, shift=DOWN), FadeIn(VGroup(a, b, trk)), run_time=0.4)   #标签与对撞双点淡入
        win.play(ChangeSpeed(
            AnimationGroup(a.animate(run_time=1).shift(RIGHT * 6.4),
                           b.animate(run_time=1).shift(LEFT * 6.4)),
            speedinfo={0.3: 1, 0.5: 0.25, 1: 2},   #参数 “speedinfo”：前 30% 常速、中段 0.25 倍、末段 2 倍
            rate_func=linear,                      #参数 “rate_func”
            affects_speed_updaters=True))          #参数 “affects_speed_updaters”
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：add_updater 挂的 updater 跟着变速 ===========================
class ChangeSpeedUpdaterDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-ChangeSpeed-updater", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        lab5 = Text("ChangeSpeed.add_updater(m, fn)  +  ChangeSpeed(",
                    font_size=30, color=GREY_B)
        lab6 = Text("    Wait(1.6), speedinfo={0.3:1, 0.55:0.15, 1:1})",
                    font_size=30, color=GREY_B)
        lab = VGroup(lab5, lab6).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #两行签名标签
        m = Dot(radius=0.14, color=YELLOW).move_to(LEFT * 3.2 + DOWN * 1.2)
        trk = Line(LEFT * 3.2 + DOWN * 1.2, RIGHT * 3.2 + DOWN * 1.2, stroke_width=2, color=GREY_B)
        trk.set_stroke(opacity=0.4)
        win.play(FadeIn(lab, shift=DOWN), FadeIn(VGroup(m, trk)), run_time=0.4)   #标签与轨道淡入
        ChangeSpeed.add_updater(m, lambda mob, dt: mob.shift(RIGHT * 3.4 * dt))   #参数 “ChangeSpeed.add_updater”：挂变速 updater
        win.play(ChangeSpeed(Wait(1.6), speedinfo={0.3: 1, 0.55: 0.15, 1: 1},   #参数 “speedinfo”：中段 0.15 倍慢放
                             affects_speed_updaters=True))
        m.clear_updaters()   #解除 updater
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：Animation 基类占位 ===========================================
class AnimationDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-Animation", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        lab = Text("Animation(sq, run_time=1.2, rate_func=linear)  # placeholder",
                   font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   #签名标签
        sq = Square(side_length=1.3, color=GREEN).set_fill(GREEN, 0.5).next_to(lab, DOWN, buff=0.6)   #占位不动的绿方块
        win.play(FadeIn(lab, shift=DOWN), FadeIn(sq), run_time=0.4)   #标签与方块淡入
        win.play(Animation(sq, run_time=1.2, rate_func=linear))   #参数 “mobject” / “run_time” / “rate_func”：占 1.2 秒
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 5：8 种速率函数同场对比 =========================================
class RateFuncDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-rate_func", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        cols = [RED, BLUE, GREEN, ORANGE]
        names1 = ["linear", "smooth", "rush_into", "rush_from"]
        funcs1 = [linear, smooth, rush_into, rush_from]
        lab1 = Text("dot.animate(run_time=1.8, rate_func=F).shift(RIGHT*6.4)",
                    font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   #签名标签
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)   #标签从下方淡入
        tracks = VGroup()
        labels1 = VGroup()
        dots1 = []
        for i, nm in enumerate(names1):
            y = 0.55 - i * 1.15
            labels1.add(Text(nm, font_size=26, color=cols[i]).move_to(LEFT * 5.6 + UP * y))
            trk = Line(LEFT * 3.2 + UP * y, RIGHT * 3.2 + UP * y, stroke_width=2, color=GREY_B)
            trk.set_stroke(opacity=0.4)
            tracks.add(trk)
            dots1.append(Dot(radius=0.12, color=cols[i]).move_to(trk.get_start()))
        win.play(FadeIn(labels1), FadeIn(tracks), FadeIn(VGroup(*dots1)), run_time=0.4)   #四条轨道就位
        win.play(*[d.animate(run_time=1.8, rate_func=f).shift(RIGHT * 6.4)
                   for d, f in zip(dots1, funcs1)])   #参数 “rate_func” ×4：同跑拉开差距
        win.play(Wait(0.4))   #停留看结果
        win.play(FadeOut(lab1), FadeOut(labels1), run_time=0.3)   #换标签
        for d in dots1:   #无动画地摆回起点：直接改属性
            d.move_to(LEFT * 3.2 + UP * d.get_center()[1])
        names2 = ["there_and_back", "exponential_decay", "squish(.35,.65)", "wiggle"]
        funcs2 = [there_and_back, exponential_decay, squish_rate_func(linear, 0.35, 0.65), wiggle]
        labels2 = VGroup()
        for i, nm in enumerate(names2):
            labels2.add(Text(nm, font_size=26, color=cols[i]).move_to(LEFT * 5.6 + UP * (0.55 - i * 1.15)))
        lab2 = Text("reset: 4 more rate_funcs (round-trip / overshoot)",
                    font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   #第二批签名标签
        win.play(FadeIn(lab2, shift=DOWN), FadeIn(labels2), run_time=0.3)   #第二批标签淡入
        win.play(*[d.animate(run_time=1.8, rate_func=f).shift(RIGHT * 6.4)
                   for d, f in zip(dots1, funcs2)])   #参数 “rate_func” ×4：往返/衰减/挤压/摆动
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("wait", WaitDemo),
    ("changespeed", ChangeSpeedDemo),
    ("changespeed_updater", ChangeSpeedUpdaterDemo),
    ("animation", AnimationDemo),
    ("ratefunc", RateFuncDemo),
]

PAIRS = [
    ("wait", ["wait"]),
    ("changespeed", ["changespeed"]),
    ("changespeed_updater", ["changespeed_updater"]),
    ("animation", ["animation"]),
    ("ratefunc", ["ratefunc"]),
]

PAGE = "01-等待速率与变速"


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
