# -*- coding: utf-8 -*-
"""02-速率函数.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 02-速率函数.py <片段名>...
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

from real_time_manim import (
    Scene, Text, VGroup, Line, Dot, Arrow, Rectangle, FunctionGraph,
    BLUE, GREEN, RED, YELLOW, TEAL, PURPLE, GREY_B,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, Write, Create,
)
from real_time_manim import rate_functions
from real_time_manim import (
    exponential_decay, linear, lingering, rush_from, rush_into,
    smooth, squish_rate_func, there_and_back, wiggle,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：常用速率函数的曲线 ===========================================
class RateCurveCommonDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02-common rate_funcs", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        x0, x1, y0, y1 = -6.0, 2.6, -2.4, 1.8   #绘图区：横 t 从左到右、纵 f(t) 从下到上
        lo, hi = -0.05, 1.05   #纵轴显示范围（上下各留 5% 余量）

        def plot(f, color):   #把速率函数画成曲线：屏幕横坐标反算回 t，再把 f(t) 映射进绘图区
            def g(u):
                t = (u - x0) / (x1 - x0)   #屏幕 x → 进度 t
                y = f(t)   #速率函数给出的实际进度
                if y < lo:
                    y = lo   #越界就压到边界（样例 2 的 wiggle 会冲出 0~1）
                elif y > hi:
                    y = hi
                return y0 + (y - lo) / (hi - lo) * (y1 - y0)   #映射成场景 y 坐标
            return FunctionGraph(g, x_range=[x0, x1, (x1 - x0) / 96], color=color, stroke_width=5)

        xax = Arrow([x0 - 0.3, y0, 0], [x1 + 0.4, y0, 0], color=GREY_B, stroke_width=4, buff=0)   #横轴：进度 t
        yax = Arrow([x0, y0 - 0.3, 0], [x0, y1 + 0.35, 0], color=GREY_B, stroke_width=4, buff=0)   #纵轴：实际进度 f(t)
        lt = Text("t", font_size=22, color=GREY_B).next_to(xax, DOWN, buff=0.12)   #横轴名
        lf = Text("f(t)", font_size=22, color=GREY_B).next_to(yax, UP, buff=0.12)   #纵轴名
        l0 = Text("0", font_size=18, color=GREY_B).next_to([x0, y0, 0], DOWN, buff=0.15)   #原点刻度
        l1t = Text("1", font_size=18, color=GREY_B).next_to([x1, y0, 0], DOWN, buff=0.15)   #t=1 刻度
        l1f = Text("1", font_size=18, color=GREY_B).next_to([x0, y1, 0], LEFT, buff=0.15)   #f(t)=1 刻度
        win.play(FadeIn(VGroup(xax, yax, lt, lf, l0, l1t, l1f)), run_time=0.4)   #坐标轴先就位

        names = ["linear", "smooth", "rush_into", "rush_from"]   #四条常用速率函数
        funcs = [linear, smooth, rush_into, rush_from]
        cols = [GREY_B, BLUE, GREEN, RED]
        for i, (nm, f, c) in enumerate(zip(names, funcs, cols)):
            g = plot(f, c)   #第 i 条曲线
            lab = Text(nm, font_size=17, color=c).move_to([3.2, 1.2 - i * 0.8, 0])   #右侧同色图例
            win.play(Create(g), run_time=0.6)   #逐条把曲线画出来
            win.play(FadeIn(lab), run_time=0.2)   #补上它的名字
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：工厂 / 往返 / 标准缓动的曲线 =================================
class RateCurveFactoryDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02-squish / wiggle / ease", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        x0, x1, y0, y1 = -6.0, 2.6, -2.4, 1.8   #绘图区
        lo, hi = -1.1, 1.4   #这一组会冲出 0~1（wiggle 来回摆、ease 有回拉），范围放宽

        def ypos(v):   #把一个 f 值换算成场景 y 坐标（刻度标签用）
            return y0 + (v - lo) / (hi - lo) * (y1 - y0)

        def plot(f, color):   #同样把速率函数画成曲线
            def g(u):
                t = (u - x0) / (x1 - x0)   #屏幕 x → 进度 t
                y = f(t)   #速率函数给出的实际进度
                if y < lo:
                    y = lo   #压到显示边界
                elif y > hi:
                    y = hi
                return ypos(y)
            return FunctionGraph(g, x_range=[x0, x1, (x1 - x0) / 96], color=color, stroke_width=5)

        xax = Arrow([x0 - 0.3, y0, 0], [x1 + 0.4, y0, 0], color=GREY_B, stroke_width=4, buff=0)   #横轴：进度 t
        yax = Arrow([x0, y0 - 0.3, 0], [x0, y1 + 0.35, 0], color=GREY_B, stroke_width=4, buff=0)   #纵轴：实际进度 f(t)
        lt = Text("t", font_size=22, color=GREY_B).next_to(xax, DOWN, buff=0.12)   #横轴名
        lf = Text("f(t)", font_size=22, color=GREY_B).next_to(yax, UP, buff=0.12)   #纵轴名
        ticks = VGroup(*[Text(v, font_size=17, color=GREY_B).next_to([x0, ypos(float(v)), 0], LEFT, buff=0.15)
                         for v in ("1", "0", "-1")])   #纵轴三个刻度：上 1、中 0、下 -1
        l1t = Text("1", font_size=18, color=GREY_B).next_to([x1, y0, 0], DOWN, buff=0.15)   #t=1 刻度
        win.play(FadeIn(VGroup(xax, yax, lt, lf, ticks, l1t)), run_time=0.4)   #坐标轴先就位

        names = ["squish(smooth, .2, .8)", "wiggle(t, 3)", "lingering", "ease_out_bounce"]   #四种“带花样”的速率函数
        funcs = [squish_rate_func(smooth, 0.2, 0.8), lambda t: wiggle(t, 3),
                 lingering, rate_functions.ease_out_bounce]
        cols = [PURPLE, RED, YELLOW, TEAL]
        for i, (nm, f, c) in enumerate(zip(names, funcs, cols)):
            g = plot(f, c)   #第 i 条曲线
            lab = Text(nm, font_size=16, color=c).move_to([3.4, 1.2 - i * 0.8, 0])   #右侧同色图例
            win.play(Create(g), run_time=0.6)   #逐条把曲线画出来
            win.play(FadeIn(lab), run_time=0.2)   #补上它的名字
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：同一条位移动画 × 四种速率 ====================================
class RateMotionDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02-rate_func on a shift", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        names = ["linear", "smooth", "rush_into", "there_and_back"]   #四条泳道各配一种速率
        funcs = [linear, smooth, rush_into, there_and_back]
        cols = [GREY_B, BLUE, GREEN, RED]
        xs0, xs1 = -2.4, 6.0   #位移轨道的起点与终点（四条完全相同）
        mx0, mx1 = -5.0, -3.0   #左侧小曲线盒的横向范围
        lanes, dots = [], []
        for i, (nm, f, c) in enumerate(zip(names, funcs, cols)):
            y = 1.9 - i * 1.2   #四条泳道的纵坐标
            box = Rectangle(width=mx1 - mx0, height=1.0, stroke_width=1)
            box.set_stroke(GREY_B, 1, opacity=0.5).set_fill(opacity=0)   #空心小方框当绘图区
            box.move_to([(mx0 + mx1) / 2, y, 0])
            lab = Text(nm, font_size=15, color=c).next_to(box, LEFT, buff=0.25)   #泳道名放在曲线盒左边

            def g(u, f=f):   #把本泳道的速率函数画进小盒（横 0→1、纵 0→1）
                t = (u - mx0) / (mx1 - mx0)
                v = f(t)
                v = 0.0 if v < 0.0 else (1.0 if v > 1.0 else v)   #越界压到盒边
                return y + (v - 0.5) * 0.8   #f=0 → 盒底、f=1 → 盒顶

            curve = FunctionGraph(g, x_range=[mx0, mx1, (mx1 - mx0) / 40],
                                  color=c, stroke_width=3)   #该泳道的速率曲线缩略图
            trk = Line([xs0, y, 0], [xs1, y, 0], color=GREY_B, stroke_width=2)
            trk.set_stroke(opacity=0.4)   #位移轨道（半透明灰线）
            dot = Dot([xs0, y, 0], radius=0.13, color=c)   #起跑的点，颜色与曲线同色
            lanes += [box, lab, curve, trk]
            dots.append((dot, y, f))
        note = Text("same shift, only rate_func differs", font_size=19, color=YELLOW).to_edge(DOWN)   #底部说明
        win.play(FadeIn(VGroup(*lanes)), FadeIn(note), run_time=0.5)   #四条泳道与说明就位
        self.add(*[d for d, _, _ in dots])   #把四个点加进场景（起点都在轨道左端）
        win.play(*[d.animate(run_time=1.6, rate_func=f).move_to([xs1, y, 0])
                   for d, y, f in dots])   #参数 “rate_func”：同一条位移 × 四种速率同时起跑
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("curves_common", RateCurveCommonDemo),
    ("curves_factory", RateCurveFactoryDemo),
    ("motion", RateMotionDemo),
]

PAIRS = [
    ("curves_common", ["curves_common"]),
    ("curves_factory", ["curves_factory"]),
    ("motion", ["motion"]),
]

PAGE = "02-速率函数"


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
