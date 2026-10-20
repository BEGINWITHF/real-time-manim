# -*- coding: utf-8 -*-
"""14-表格.md 五个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 14-表格.py <样例名>...
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
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    Scene, Table, MathTable, MobjectTable, IntegerTable, DecimalTable, Integer,
    DecimalNumber, Text, MathTex, Square, Circle, Dot, Arrow, Star, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


def cap(text, mob, buff=0.35, color=GREY_B, size=18):
    return Text(text, font_size=size, color=color).next_to(mob, DOWN, buff=buff)


# ===== 样例 1：Table —— 纯文本表格 =========================================
class TableDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("14-Table", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        stage = VGroup()   #当前这一段的表格+字幕：换段先淡出，避免叠图叠字
        def show(mob, capt, t=0.6):
            nonlocal stage
            c = Text(capt, font_size=18, color=GREY_B).next_to(mob, DOWN, buff=0.3)
            if len(stage):
                win.play(FadeOut(stage), run_time=0.2)
            win.play(Write(mob), FadeIn(c), run_time=t)
            stage = VGroup(mob, c)

        # —— 默认：只画内部网格线，单元格用 Paragraph 渲染 ——
        t1 = Table([["a", "b"], ["c", "d"]], element_to_mobject=Text,
                   element_to_mobject_config={"font_size": 34})   #参数 “table”
        t1.scale(0.8).move_to([0, 0.6, 0])
        show(t1, "Table([[a,b],[c,d]])")

        # —— include_outer_lines / include_inner_lines：外框与内线 ——
        t2 = Table([["a", "b"], ["c", "d"]], include_outer_lines=True, include_inner_lines=False,
                   element_to_mobject=Text, element_to_mobject_config={"font_size": 34})
        t2.scale(0.8).move_to([0, 0.6, 0])   #参数 “include_outer_lines / include_inner_lines”
        show(t2, "outer=True inner=False")

        # —— line_config：线样式 ——
        t3 = Table([["a", "b"], ["c", "d"]], include_outer_lines=True,
                   line_config={"stroke_width": 4, "color": YELLOW},   #参数 “line_config”
                   element_to_mobject=Text, element_to_mobject_config={"font_size": 34})
        t3.scale(0.8).move_to([0, 0.6, 0])
        show(t3, "line_config=粗黄线")

        # —— row_labels / col_labels / top_left_entry ——
        t4 = Table([["1", "2"], ["3", "4"]],
                   row_labels=[Text("R1", font_size=28), Text("R2", font_size=28)],   #参数 “row_labels”
                   col_labels=[Text("C1", font_size=28), Text("C2", font_size=28)],   #参数 “col_labels”
                   top_left_entry=Text("T", font_size=28, color=TEAL),   #参数 “top_left_entry”
                   include_outer_lines=True,
                   element_to_mobject=Text, element_to_mobject_config={"font_size": 32})
        t4.scale(0.85).move_to([0, 0.4, 0])
        show(t4, "row/col_labels + top_left_entry", t=0.7)

        # —— v_buff / h_buff + arrange_in_grid_config ——
        t5 = Table([["a", "b"], ["c", "d"]], v_buff=1.6, h_buff=2.6,   #参数 “v_buff / h_buff”
                   arrange_in_grid_config={"cell_alignment": UP},   #参数 “arrange_in_grid_config”
                   include_outer_lines=True,
                   element_to_mobject=Text, element_to_mobject_config={"font_size": 32})
        t5.scale(0.7).move_to([0, 0.4, 0])
        show(t5, "v_buff/h_buff/cell_alignment", t=0.7)

        # —— 两种背景：每格背景 + 整表背景 ——
        t6 = Table([["a", "b"], ["c", "d"]], include_outer_lines=True,
                   add_background_rectangles_to_entries=True,   #参数 “add_background_rectangles_to_entries / entries_background_color”
                   entries_background_color=TEAL,
                   element_to_mobject=Text, element_to_mobject_config={"font_size": 32}).scale(0.7).move_to([0, 0.4, 0])
        show(t6, "每格背景 TEAL")

        # —— include_background_rectangle + background_rectangle_color ——
        t7 = Table([["a", "b"], ["c", "d"]], include_outer_lines=True,
                   include_background_rectangle=True,   #参数 “include_background_rectangle / background_rectangle_color”
                   background_rectangle_color=GREEN,
                   element_to_mobject=Text, element_to_mobject_config={"font_size": 32}).scale(0.8).move_to([-2.6, 0.2, 0])
        win.play(FadeOut(stage), run_time=0.2)
        win.play(Write(t7), FadeIn(Text("整表背景 GREEN", font_size=18, color=GREY_B).next_to(t7, DOWN, buff=0.3)), run_time=0.6)

        # —— 方法：行列/单元格取数、行列染色、外框与内部线段、事后加背景 ——
        info = VGroup(
            Text("rows=%d cols=%d entries=%d" % (len(t7.get_rows()), len(t7.get_columns()), len(t7.get_entries())), font_size=18, color=GREY_B),   #方法 “get_rows / get_columns / get_entries”
            Text("h_lines=%d v_lines=%d" % (len(t7.get_horizontal_lines()), len(t7.get_vertical_lines())), font_size=18, color=GREY_B),   #方法 “get_horizontal_lines / get_vertical_lines”
        ).arrange(DOWN, buff=0.12).move_to([2.6, 0.6, 0])
        win.play(FadeIn(info), run_time=0.5)
        c7 = Text("set_column_colors(RED, BLUE)", font_size=18, color=GREY_B).next_to(t7, DOWN, buff=0.85)
        win.play(FadeIn(c7), run_time=0.3)
        t7.set_column_colors(RED, BLUE)   #方法 “set_column_colors(*colors)”
        win.play(Write(t7), run_time=0.4)
        c7.become(Text("set_row_colors(ORANGE, PURPLE)", font_size=18, color=GREY_B).next_to(t7, DOWN, buff=0.85))
        t7.set_row_colors(ORANGE, PURPLE)   #方法 “set_row_colors(*colors)”
        win.play(Write(t7), run_time=0.4)
        c7.become(Text("add_background_to_entries(TEAL)", font_size=18, color=GREY_B).next_to(t7, DOWN, buff=0.85))
        t7.add_background_to_entries(TEAL)   #方法 “add_background_to_entries(color)”
        win.play(Write(t7), run_time=0.5)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：MathTable —— 公式表格 =======================================
class MathTableDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("14-MathTable", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 默认：单元格用 MathTex 渲染（LaTeX 数学模式）——
        mt = MathTable([[r"x^2", r"\sqrt{y}"], [r"\frac{a}{b}", r"\sum_{i=1}^{n} i"]],
                       include_outer_lines=True)   #参数 “table”
        mt.scale(0.9).move_to([-3.4, 1.0, 0])
        win.play(Write(mt), FadeIn(Text("MathTable(LaTeX 单元格)", font_size=18, color=GREY_B).next_to(mt, DOWN, buff=0.35)), run_time=0.8)

        # —— element_to_mobject：换成 Text（只对能当文本读的单元格有意义）——
        mt2 = MathTable([["x", "y"], ["a", "b"]],
                        element_to_mobject=Text,   #参数 “element_to_mobject”
                        include_outer_lines=True)
        mt2.scale(0.9).move_to([3.0, 1.0, 0])
        win.play(Write(mt2), FadeIn(Text("element_to_mobject=Text", font_size=18, color=GREY_B).next_to(mt2, DOWN, buff=0.35)), run_time=0.7)

        # —— 其余参数与 Table 相同：标签、线、间距、背景 ——
        self.clear()   #清场：上一段的表格与字幕一起收掉
        self.add(title)
        mt3 = MathTable([[r"1", r"2"], [r"3", r"4"]],
                        row_labels=[MathTex(r"i"), MathTex(r"j")],
                        col_labels=[MathTex(r"a"), MathTex(r"b")],
                        top_left_entry=MathTex(r"\times"),
                        include_outer_lines=True, include_inner_lines=True,
                        line_config={"stroke_width": 3, "color": ORANGE},
                        v_buff=1.0, h_buff=1.6,
                        add_background_rectangles_to_entries=True,
                        entries_background_color=BLUE)
        mt3.scale(0.8).move_to([0, -2.0, 0])
        win.play(Write(mt3), FadeIn(Text("标签 + 线样式 + 间距 + 每格背景", font_size=18, color=GREY_B).move_to([0, -3.6, 0])), run_time=0.8)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：MobjectTable —— 格子里放图形 ================================
class MobjectTableDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("14-MobjectTable", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 默认 element_to_mobject 是恒等函数：直接摆现成对象 ——
        m1 = MobjectTable([[Circle(radius=0.3, color=BLUE), Square(side_length=0.6, color=GREEN)],
                           [Dot(radius=0.16, color=RED), Star(color=ORANGE).scale(0.35)]],
                          include_outer_lines=True)   #参数 “table”
        m1.scale(0.9).move_to([-3.4, 1.0, 0])
        win.play(Create(m1), FadeIn(Text("MobjectTable([[Circle, Square], …])", font_size=18, color=GREY_B).next_to(m1, DOWN, buff=0.35)), run_time=0.9)

        # —— element_to_mobject：统一转换（这里把每个对象缩小一半）——
        m2 = MobjectTable([[Circle(radius=0.6, color=TEAL), Square(side_length=1.2, color=GOLD)],
                           [Dot(radius=0.3, color=PURPLE), Star(color=YELLOW).scale(0.7)]],
                          element_to_mobject=lambda m: m.copy().scale(0.5),   #参数 “element_to_mobject”
                          include_outer_lines=True, v_buff=1.2, h_buff=1.6)
        m2.scale(0.9).move_to([2.8, 1.0, 0])
        win.play(Create(m2), FadeIn(Text("element_to_mobject=lambda m: m.copy().scale(0.5)", font_size=18, color=GREY_B).next_to(m2, DOWN, buff=0.35)), run_time=0.9)

        # —— 图形 + 文字混排：一格对象、一格文本 ——
        self.clear()   #清场：上一段的表格与字幕一起收掉
        self.add(title)
        m3 = MobjectTable([[Text("圆", font_size=30, color=BLUE), Circle(radius=0.28, color=BLUE)],
                           [Text("方", font_size=30, color=GREEN), Square(side_length=0.55, color=GREEN)]],
                          include_outer_lines=True, v_buff=1.0, h_buff=1.4,
                          line_config={"stroke_width": 3, "color": GREY_B})
        m3.scale(0.9).move_to([0, -2.0, 0])
        win.play(Create(m3), FadeIn(Text("图文混排", font_size=18, color=GREY_B).next_to(m3, DOWN, buff=0.35)), run_time=0.9)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：IntegerTable —— 整数表格 ====================================
class IntegerTableDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("14-IntegerTable", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 默认：单元格用 Integer 渲染 ——
        it = IntegerTable([[1, 2, 3], [4, 5, 6]], include_outer_lines=True)   #参数 “table”
        it.scale(0.9).move_to([-3.2, 1.0, 0])
        win.play(Write(it), FadeIn(Text("IntegerTable([[1,2,3],[4,5,6]])", font_size=18, color=GREY_B).next_to(it, DOWN, buff=0.35)), run_time=0.8)

        # —— element_to_mobject：换成 DecimalNumber（数字元素都能接）——
        it2 = IntegerTable([[7, 8], [9, 10]], element_to_mobject=DecimalNumber,
                           element_to_mobject_config={"num_decimal_places": 0},   #参数 “element_to_mobject / config”
                           include_outer_lines=True)
        it2.scale(0.9).move_to([2.4, 1.0, 0])
        win.play(Write(it2), FadeIn(Text("element_to_mobject=DecimalNumber", font_size=18, color=GREY_B).next_to(it2, DOWN, buff=0.35)), run_time=0.8)

        # —— 其余参数与 Table 相同：行列标签 + 颜色 ——
        self.clear()   #清场：上一段的表格与字幕一起收掉
        self.add(title)
        it3 = IntegerTable([[10, 20], [30, 40]],
                           row_labels=[Text("r1", font_size=26), Text("r2", font_size=26)],
                           col_labels=[Text("c1", font_size=26), Text("c2", font_size=26)],
                           include_outer_lines=True, v_buff=1.2, h_buff=2.0,
                           color=TEAL)
        it3.scale(0.85).move_to([0, -2.0, 0])
        win.play(Write(it3), FadeIn(Text("带标签 + color=TEAL", font_size=18, color=GREY_B).move_to([0, -3.6, 0])), run_time=0.8)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 5：DecimalTable —— 小数表格 ====================================
class DecimalTableDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("14-DecimalTable", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 默认 num_decimal_places=1 ——
        dt = DecimalTable([[1.25, 3.5], [7.75, 9.0]], include_outer_lines=True)   #参数 “table”
        dt.scale(0.9).move_to([-3.2, 1.0, 0])
        win.play(Write(dt), FadeIn(Text("默认 1 位小数", font_size=18, color=GREY_B).next_to(dt, DOWN, buff=0.35)), run_time=0.8)

        # —— element_to_mobject_config：3 位小数 ——
        dt2 = DecimalTable([[1.2345, 3.4567], [5.6789, 7.891]],
                           element_to_mobject_config={"num_decimal_places": 3},   #参数 “element_to_mobject_config”
                           include_outer_lines=True)
        dt2.scale(0.9).move_to([2.4, 1.0, 0])
        win.play(Write(dt2), FadeIn(Text("num_decimal_places=3", font_size=18, color=GREY_B).next_to(dt2, DOWN, buff=0.35)), run_time=0.8)

        # —— element_to_mobject：换成 Integer（数字元素都能接，这里取整）——
        self.clear()   #清场：上一段的表格与字幕一起收掉
        self.add(title)
        dt3 = DecimalTable([[1.25, 3.5], [7.75, 9.0]], element_to_mobject=Integer,
                           element_to_mobject_config={"font_size": 40},   #参数 “element_to_mobject”
                           include_outer_lines=True)
        dt3.scale(0.9).move_to([0, -2.0, 0])
        win.play(Write(dt3), FadeIn(Text("element_to_mobject=Integer", font_size=18, color=GREY_B).next_to(dt3, DOWN, buff=0.35)), run_time=0.8)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("table", TableDemo),
    ("mathtable", MathTableDemo),
    ("mobjecttable", MobjectTableDemo),
    ("integertable", IntegerTableDemo),
    ("decimaltable", DecimalTableDemo),
]

PAIRS = [
    ("table", ["table"]),
    ("mathtable", ["mathtable"]),
    ("mobjecttable", ["mobjecttable"]),
    ("integertable", ["integertable"]),
    ("decimaltable", ["decimaltable"]),
]

PAGE = "14-表格"


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
