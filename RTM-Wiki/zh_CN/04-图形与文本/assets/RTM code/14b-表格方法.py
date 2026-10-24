# -*- coding: utf-8 -*-
"""14b-表格方法.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 14b-表格方法.py <样例名>...
不带参数就渲染全部样例，并拼出页面里的三条样例视频（输出到 assets/RTM output/）。
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
    Scene, Table, Text, Rectangle, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


def cap(text, mob, buff=0.4, color=GREY_B, size=18):
    return Text(text, font_size=size, color=color).next_to(mob, DOWN, buff=buff)


# ===== 样例 1：add_highlighted_cell —— 给单元格加高亮块 ====================
class HighlightDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("14b-add_highlighted_cell", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        t = Table([["a", "b"], ["c", "d"]], include_outer_lines=True,
                  element_to_mobject=Text, element_to_mobject_config={"font_size": 34})
        t.scale(0.9).move_to([0, 0.6, 0])
        win.play(Write(t), FadeIn(cap("Table([[a,b],[c,d]])", t)), run_time=0.7)

        # —— pos 用 (行, 列) 定位（1 起算），color 是高亮块颜色 ——
        t.add_highlighted_cell((1, 2), color=YELLOW)   #参数 “pos / color”
        win.play(Write(t), run_time=0.5)
        c1 = Text("add_highlighted_cell((1, 2), YELLOW)",
                  font_size=18, color=GREY_B).move_to([0, -1.5, 0])
        win.play(FadeIn(c1), run_time=0.4)

        # —— **kwargs 继续传给背景块（如 fill_opacity）——
        t.add_highlighted_cell((2, 1), color=BLUE, fill_opacity=0.4)   #参数 “**kwargs”
        win.play(Write(t), run_time=0.5)
        newc = Text("add_highlighted_cell((2, 1), BLUE, fill_opacity=0.4)",
                    font_size=18, color=GREY_B).move_to([0, -2.1, 0])
        win.play(FadeIn(newc), run_time=0.4)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：get_cell / get_highlighted_cell —— 取出单元格 ===============
class GetCellDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("14b-get_cell / get_highlighted_cell", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        t = Table([["1", "2"], ["3", "4"]], include_outer_lines=True,
                  element_to_mobject=Text, element_to_mobject_config={"font_size": 34})
        t.scale(0.9).move_to([0, 0.6, 0])
        win.play(Write(t), FadeIn(cap("Table([[1,2],[3,4]])", t)), run_time=0.7)

        # —— get_cell：拿到单元格多边形，可以单独改样式 ——
        cell = t.get_cell((1, 2))   #参数 “pos”
        win.play(cell.animate.set_fill(RED, 0.45), run_time=0.6)
        c1 = Text("get_cell((1, 2)) -> Polygon",
                  font_size=18, color=GREY_B).move_to([0, -1.5, 0])
        win.play(FadeIn(c1), run_time=0.4)

        # —— get_highlighted_cell：直接拿到“已高亮好”的背景块 ——
        hl = t.get_highlighted_cell((2, 2), color=TEAL)   #参数 “pos / color”
        win.play(FadeIn(hl), run_time=0.5)
        newc = Text("get_highlighted_cell((2, 2), TEAL)",
                    font_size=18, color=GREY_B).move_to([0, -2.1, 0])
        win.play(FadeIn(newc), run_time=0.4)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：create —— 表格的编排出场动画 ================================
class CreateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("14b-Table.create", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 默认 create()：线 Create、标签 Write、元素 Create、条目 FadeIn ——
        t1 = Table([["a", "b"], ["c", "d"]], include_outer_lines=True,
                   element_to_mobject=Text, element_to_mobject_config={"font_size": 32})
        t1.scale(0.8).move_to([0, 0.8, 0])
        win.play(t1.create(), FadeIn(cap("create()（默认动画）", t1)), run_time=1.2)

        # —— lag_ratio / line_animation / label_animation 可替换 ——
        t2 = Table([["1", "2"], ["3", "4"]], include_outer_lines=True,
                   element_to_mobject=Text, element_to_mobject_config={"font_size": 32})
        t2.scale(0.8).move_to([0, -1.8, 0])
        win.play(FadeOut(t1),
                 t2.create(lag_ratio=0.15, line_animation=Write),   #参数 “lag_ratio / line_animation”
                 FadeIn(cap("create(lag_ratio=0.15, line_animation=Write)", t2)), run_time=1.2)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("highlight", HighlightDemo),
    ("getcell", GetCellDemo),
    ("create", CreateDemo),
]

PAIRS = [
    ("highlight", ["highlight"]),
    ("getcell", ["getcell"]),
    ("create", ["create"]),
]

PAGE = "14b-表格方法"


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
