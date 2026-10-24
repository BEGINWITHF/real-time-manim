# -*- coding: utf-8 -*-
"""03b-矩形与特殊多边形.md 五个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 03b-矩形与特殊多边形.py <样例名>...
不带参数就渲染全部样例，并拼出页面里的五条样例视频（输出到 assets/RTM output/）。
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
    Scene, Rectangle, Square, RoundedRectangle, Cutout, ConvexHull, Circle,
    Triangle, Dot, VGroup, Text,
    BLUE, GREEN, TEAL, PURPLE, ORANGE, YELLOW, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：Rectangle —— 宽高、网格线 ====================================
class RectangleDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("03b-Rectangle", font_size=28, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 默认 4x2 ——
        r1 = Rectangle(color=BLUE)   #color 参数：默认 WHITE
        r1.move_to([-4.4, 1.4, 0])   #默认 width=4.0 / height=2.0
        cap1 = Text("Rectangle()  4x2", font_size=19, color=GREY_B).move_to([-4.4, 0.1, 0])
        win.play(Create(r1), FadeIn(cap1), run_time=0.6)   #画出默认矩形 + 字幕

        # —— width / height 显式给 ——
        r2 = Rectangle(width=2.4, height=1.6, color=GREEN)   #参数 “width / height”
        r2.move_to([0, 1.4, 0])   #窄而矮
        cap2 = Text("width=2.4 height=1.6", font_size=19, color=GREY_B).move_to([0, 0.1, 0])
        win.play(Create(r2), FadeIn(cap2), run_time=0.6)   #画出自定义尺寸 + 字幕

        # —— grid_xstep / grid_ystep：矩形内部画网格 ——
        r3 = Rectangle(width=3.2, height=1.8, color=ORANGE,
                       grid_xstep=0.8, grid_ystep=0.6)   #参数 “grid_xstep / grid_ystep”
        r3.move_to([4.4, 1.4, 0])   #内部被切成小格
        cap3 = Text("grid_xstep=0.8 grid_ystep=0.6", font_size=19, color=GREY_B).move_to([4.4, 0.1, 0])
        win.play(Create(r3), FadeIn(cap3), run_time=0.6)   #画出带网格矩形 + 字幕
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：Square —— side_length 可读写 ================================
class SquareDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("03b-Square", font_size=28, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        sq1 = Square(color=BLUE, fill_opacity=0.5)   #默认 side_length=2.0
        sq1.move_to([-3.6, 0.4, 0])
        cap1 = Text("Square()  2.0", font_size=19, color=GREY_B).move_to([-3.6, -1.5, 0])
        win.play(Create(sq1), FadeIn(cap1), run_time=0.6)   #画出默认正方形 + 字幕

        sq2 = Square(side_length=1.2, color=TEAL, fill_opacity=0.5)   #参数 “side_length”
        sq2.move_to([0, 0.4, 0])
        cap2 = Text("side_length=1.2", font_size=19, color=GREY_B).move_to([0, -1.5, 0])
        win.play(Create(sq2), FadeIn(cap2), run_time=0.6)   #画出小正方形 + 字幕

        # —— side_length 是可读写属性：赋值当场改形状 ——
        sq3 = Square(color=PURPLE, fill_opacity=0.5)
        sq3.move_to([4.0, 0.4, 0])
        cap3 = Text("sq.side_length = 2.6", font_size=19, color=GREY_B).move_to([4.0, -1.5, 0])
        win.play(Create(sq3), FadeIn(cap3), run_time=0.6)   #先画默认大小
        sq3.side_length = 2.6   #默认 2.0；赋值即改形状（不重新构造）
        win.play(Wait(0.5))   #赋值后停留，让变化可见
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：RoundedRectangle —— 圆角半径（单个 / 四角不同）==============
class RoundedDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("03b-RoundedRectangle", font_size=28, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        rr1 = RoundedRectangle(corner_radius=0.5, width=3.4, height=1.6,
                               color=TEAL, fill_opacity=0.5)   #参数 “corner_radius=0.5”
        rr1.move_to([0, 1.3, 0])
        cap1 = Text("RoundedRectangle(corner_radius=0.5)", font_size=19, color=GREY_B).move_to([0, 0.2, 0])
        win.play(Create(rr1), FadeIn(cap1), run_time=0.6)   #四角同半径 + 字幕

        rr2 = RoundedRectangle(corner_radius=[0.05, 0.35, 0.65, 1.0],
                               width=3.4, height=1.6,
                               color=PURPLE, fill_opacity=0.5)   #参数 “corner_radius=[四个值]”
        rr2.move_to([0, -1.6, 0])
        cap2 = Text("corner_radius=[0.05, 0.35, 0.65, 1.0]", font_size=19, color=GREY_B).move_to([0, -2.7, 0])
        win.play(Create(rr2), FadeIn(cap2), run_time=0.6)   #四角半径各不同 + 字幕
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：Cutout —— 从主形状里挖孔 ====================================
class CutoutDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("03b-Cutout", font_size=28, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        main = Rectangle(width=5.0, height=2.6, color=TEAL,
                         fill_opacity=0.9).move_to([-2.4, -0.4, 0])   #主形状（带填充）
        # 参数 “main_shape / *mobjects”：后面每个形状都从主形状里挖掉
        cut = Cutout(main,
                     Circle(radius=0.55, color=WHITE).move_to([-4.0, -0.4, 0]),   #挖一个圆孔
                     Triangle(color=WHITE).scale(0.7).move_to([-1.2, -0.4, 0]))   #再挖一个三角孔
        cap = Text("Cutout(main, Circle, Triangle)", font_size=19, color=GREY_B).move_to([-2.4, -2.1, 0])
        win.play(Create(main), run_time=0.5)   #先画主形状
        win.play(Create(cut), FadeIn(cap), run_time=0.8)   #换成带孔形状 + 字幕
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 5：ConvexHull —— 一族点的凸包 ==================================
class ConvexHullDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("03b-ConvexHull", font_size=28, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        pts = [[-4.6, -1.2, 0], [-3.2, 1.4, 0], [-1.6, 0.2, 0], [-2.2, -1.6, 0],
               [-0.6, 1.0, 0], [0.4, -0.8, 0], [-1.0, 1.8, 0]]   #不规则的七个点
        dots = VGroup(*[Dot(p, radius=0.07, color=YELLOW) for p in pts])   #先把点画出来
        hull = ConvexHull(*pts, color=GREEN, fill_opacity=0.4)   #参数 “*points / tolerance”
        cap = Text("ConvexHull(*points, tolerance=1e-05)", font_size=19, color=GREY_B).move_to([-2.2, -2.7, 0])
        win.play(FadeIn(dots), run_time=0.5)   #散点
        win.play(FadeIn(hull), FadeIn(cap), run_time=0.8)   #凸包 + 字幕
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("rectangle", RectangleDemo),
    ("square", SquareDemo),
    ("rounded", RoundedDemo),
    ("cutout", CutoutDemo),
    ("convexhull", ConvexHullDemo),
]

PAIRS = [
    ("rectangle", ["rectangle"]),
    ("square", ["square"]),
    ("rounded", ["rounded"]),
    ("cutout", ["cutout"]),
    ("convexhull", ["convexhull"]),
]

PAGE = "03b-矩形与特殊多边形"


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
