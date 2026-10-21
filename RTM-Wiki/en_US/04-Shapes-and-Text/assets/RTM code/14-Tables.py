# -*- coding: utf-8 -*-
"""Full source for the five samples in 14-Tables.md (identical to the code blocks in the page).

Usage: python 14-Tables.py <sample names>...
With no arguments it renders every sample and concatenates the page's five sample videos (written to assets/RTM output/).
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


# ===== Sample 1: Table —— a plain-text table ==============================
class TableDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("14-Table", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        stage = VGroup()   # the current section's table + caption: fade out the previous section first so nothing overlaps
        def show(mob, capt, t=0.6):
            nonlocal stage
            c = Text(capt, font_size=18, color=GREY_B).next_to(mob, DOWN, buff=0.3)
            if len(stage):
                win.play(FadeOut(stage), run_time=0.2)
            win.play(Write(mob), FadeIn(c), run_time=t)
            stage = VGroup(mob, c)

        # —— default: only the inner grid lines are drawn, cells are rendered with Paragraph ——
        t1 = Table([["a", "b"], ["c", "d"]], element_to_mobject=Text,
                   element_to_mobject_config={"font_size": 34})   # the "table" parameter
        t1.scale(0.8).move_to([0, 0.6, 0])
        show(t1, "Table([[a,b],[c,d]])")

        # —— include_outer_lines / include_inner_lines: outer frame and inner lines ——
        t2 = Table([["a", "b"], ["c", "d"]], include_outer_lines=True, include_inner_lines=False,
                   element_to_mobject=Text, element_to_mobject_config={"font_size": 34})
        t2.scale(0.8).move_to([0, 0.6, 0])   # the "include_outer_lines / include_inner_lines" parameters
        show(t2, "outer=True inner=False")

        # —— line_config: line style ——
        t3 = Table([["a", "b"], ["c", "d"]], include_outer_lines=True,
                   line_config={"stroke_width": 4, "color": YELLOW},   # the "line_config" parameter
                   element_to_mobject=Text, element_to_mobject_config={"font_size": 34})
        t3.scale(0.8).move_to([0, 0.6, 0])
        show(t3, "line_config=thick yellow")

        # —— row_labels / col_labels / top_left_entry ——
        t4 = Table([["1", "2"], ["3", "4"]],
                   row_labels=[Text("R1", font_size=28), Text("R2", font_size=28)],   # the "row_labels" parameter
                   col_labels=[Text("C1", font_size=28), Text("C2", font_size=28)],   # the "col_labels" parameter
                   top_left_entry=Text("T", font_size=28, color=TEAL),   # the "top_left_entry" parameter
                   include_outer_lines=True,
                   element_to_mobject=Text, element_to_mobject_config={"font_size": 32})
        t4.scale(0.85).move_to([0, 0.4, 0])
        show(t4, "row/col_labels + top_left_entry", t=0.7)

        # —— v_buff / h_buff + arrange_in_grid_config ——
        t5 = Table([["a", "b"], ["c", "d"]], v_buff=1.6, h_buff=2.6,   # the "v_buff / h_buff" parameters
                   arrange_in_grid_config={"cell_alignment": UP},   # the "arrange_in_grid_config" parameter
                   include_outer_lines=True,
                   element_to_mobject=Text, element_to_mobject_config={"font_size": 32})
        t5.scale(0.7).move_to([0, 0.4, 0])
        show(t5, "v_buff/h_buff/cell_alignment", t=0.7)

        # —— two kinds of background: per-cell background + whole-table background ——
        t6 = Table([["a", "b"], ["c", "d"]], include_outer_lines=True,
                   add_background_rectangles_to_entries=True,   # the "add_background_rectangles_to_entries / entries_background_color" parameters
                   entries_background_color=TEAL,
                   element_to_mobject=Text, element_to_mobject_config={"font_size": 32}).scale(0.7).move_to([0, 0.4, 0])
        show(t6, "per-cell bg TEAL")

        # —— include_background_rectangle + background_rectangle_color ——
        t7 = Table([["a", "b"], ["c", "d"]], include_outer_lines=True,
                   include_background_rectangle=True,   # the "include_background_rectangle / background_rectangle_color" parameters
                   background_rectangle_color=GREEN,
                   element_to_mobject=Text, element_to_mobject_config={"font_size": 32}).scale(0.8).move_to([-2.6, 0.2, 0])
        win.play(FadeOut(stage), run_time=0.2)
        win.play(Write(t7), FadeIn(Text("whole-table bg GREEN", font_size=18, color=GREY_B).next_to(t7, DOWN, buff=0.3)), run_time=0.6)

        # —— methods: reading rows/columns/cells, colouring rows and columns, frame and inner segments, adding a background afterwards ——
        info = VGroup(
            Text("rows=%d cols=%d entries=%d" % (len(t7.get_rows()), len(t7.get_columns()), len(t7.get_entries())), font_size=18, color=GREY_B),   # the "get_rows / get_columns / get_entries" methods
            Text("h_lines=%d v_lines=%d" % (len(t7.get_horizontal_lines()), len(t7.get_vertical_lines())), font_size=18, color=GREY_B),   # the "get_horizontal_lines / get_vertical_lines" methods
        ).arrange(DOWN, buff=0.12).move_to([2.6, 0.6, 0])
        win.play(FadeIn(info), run_time=0.5)
        c7 = Text("set_column_colors(RED, BLUE)", font_size=18, color=GREY_B).next_to(t7, DOWN, buff=0.85)
        win.play(FadeIn(c7), run_time=0.3)
        t7.set_column_colors(RED, BLUE)   # the "set_column_colors(*colors)" method
        win.play(Write(t7), run_time=0.4)
        c7.become(Text("set_row_colors(ORANGE, PURPLE)", font_size=18, color=GREY_B).next_to(t7, DOWN, buff=0.85))
        t7.set_row_colors(ORANGE, PURPLE)   # the "set_row_colors(*colors)" method
        win.play(Write(t7), run_time=0.4)
        c7.become(Text("add_background_to_entries(TEAL)", font_size=18, color=GREY_B).next_to(t7, DOWN, buff=0.85))
        t7.add_background_to_entries(TEAL)   # the "add_background_to_entries(color)" method
        win.play(Write(t7), run_time=0.5)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: MathTable —— a formula table =============================
class MathTableDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("14-MathTable", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— default: cells are rendered with MathTex (LaTeX math mode) ——
        mt = MathTable([[r"x^2", r"\sqrt{y}"], [r"\frac{a}{b}", r"\sum_{i=1}^{n} i"]],
                       include_outer_lines=True)   # the "table" parameter
        mt.scale(0.9).move_to([-3.4, 1.0, 0])
        win.play(Write(mt), FadeIn(Text("MathTable (LaTeX cells)", font_size=18, color=GREY_B).next_to(mt, DOWN, buff=0.35)), run_time=0.8)

        # —— element_to_mobject: switch to Text (only meaningful for cells that can be read as text) ——
        mt2 = MathTable([["x", "y"], ["a", "b"]],
                        element_to_mobject=Text,   # the "element_to_mobject" parameter
                        include_outer_lines=True)
        mt2.scale(0.9).move_to([3.0, 1.0, 0])
        win.play(Write(mt2), FadeIn(Text("element_to_mobject=Text", font_size=18, color=GREY_B).next_to(mt2, DOWN, buff=0.35)), run_time=0.7)

        # —— the remaining parameters are the same as Table: labels, lines, spacing, background ——
        self.clear()   # clear the stage: take away the previous section's table and caption together
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
        win.play(Write(mt3), FadeIn(Text("labels + line style + spacing + per-cell bg", font_size=18, color=GREY_B).move_to([0, -3.6, 0])), run_time=0.8)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: MobjectTable —— shapes in the cells =====================
class MobjectTableDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("14-MobjectTable", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— the default element_to_mobject is the identity function: place ready-made objects directly ——
        m1 = MobjectTable([[Circle(radius=0.3, color=BLUE), Square(side_length=0.6, color=GREEN)],
                           [Dot(radius=0.16, color=RED), Star(color=ORANGE).scale(0.35)]],
                          include_outer_lines=True)   # the "table" parameter
        m1.scale(0.9).move_to([-3.4, 1.0, 0])
        win.play(Create(m1), FadeIn(Text("MobjectTable([[Circle, Square], …])", font_size=18, color=GREY_B).next_to(m1, DOWN, buff=0.35)), run_time=0.9)

        # —— element_to_mobject: a uniform conversion (here every object is shrunk by half) ——
        m2 = MobjectTable([[Circle(radius=0.6, color=TEAL), Square(side_length=1.2, color=GOLD)],
                           [Dot(radius=0.3, color=PURPLE), Star(color=YELLOW).scale(0.7)]],
                          element_to_mobject=lambda m: m.copy().scale(0.5),   # the "element_to_mobject" parameter
                          include_outer_lines=True, v_buff=1.2, h_buff=1.6)
        m2.scale(0.9).move_to([2.8, 1.0, 0])
        win.play(Create(m2), FadeIn(Text("element_to_mobject=lambda m: m.copy().scale(0.5)", font_size=18, color=GREY_B).next_to(m2, DOWN, buff=0.35)), run_time=0.9)

        # —— shapes + text mixed: one cell an object, one cell text ——
        self.clear()   # clear the stage: take away the previous section's table and caption together
        self.add(title)
        m3 = MobjectTable([[Text("circle", font_size=30, color=BLUE), Circle(radius=0.28, color=BLUE)],
                           [Text("square", font_size=30, color=GREEN), Square(side_length=0.55, color=GREEN)]],
                          include_outer_lines=True, v_buff=1.0, h_buff=1.4,
                          line_config={"stroke_width": 3, "color": GREY_B})
        m3.scale(0.9).move_to([0, -2.0, 0])
        win.play(Create(m3), FadeIn(Text("shapes and text mixed", font_size=18, color=GREY_B).next_to(m3, DOWN, buff=0.35)), run_time=0.9)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 4: IntegerTable —— an integer table ========================
class IntegerTableDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("14-IntegerTable", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— default: cells are rendered with Integer ——
        it = IntegerTable([[1, 2, 3], [4, 5, 6]], include_outer_lines=True)   # the "table" parameter
        it.scale(0.9).move_to([-3.2, 1.0, 0])
        win.play(Write(it), FadeIn(Text("IntegerTable([[1,2,3],[4,5,6]])", font_size=18, color=GREY_B).next_to(it, DOWN, buff=0.35)), run_time=0.8)

        # —— element_to_mobject: switch to DecimalNumber (any numeric element is accepted) ——
        it2 = IntegerTable([[7, 8], [9, 10]], element_to_mobject=DecimalNumber,
                           element_to_mobject_config={"num_decimal_places": 0},   # the "element_to_mobject / config" parameters
                           include_outer_lines=True)
        it2.scale(0.9).move_to([2.4, 1.0, 0])
        win.play(Write(it2), FadeIn(Text("element_to_mobject=DecimalNumber", font_size=18, color=GREY_B).next_to(it2, DOWN, buff=0.35)), run_time=0.8)

        # —— the remaining parameters are the same as Table: row and column labels + colour ——
        self.clear()   # clear the stage: take away the previous section's table and caption together
        self.add(title)
        it3 = IntegerTable([[10, 20], [30, 40]],
                           row_labels=[Text("r1", font_size=26), Text("r2", font_size=26)],
                           col_labels=[Text("c1", font_size=26), Text("c2", font_size=26)],
                           include_outer_lines=True, v_buff=1.2, h_buff=2.0,
                           color=TEAL)
        it3.scale(0.85).move_to([0, -2.0, 0])
        win.play(Write(it3), FadeIn(Text("labels + color=TEAL", font_size=18, color=GREY_B).move_to([0, -3.6, 0])), run_time=0.8)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 5: DecimalTable —— a decimal table =========================
class DecimalTableDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("14-DecimalTable", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— default num_decimal_places=1 ——
        dt = DecimalTable([[1.25, 3.5], [7.75, 9.0]], include_outer_lines=True)   # the "table" parameter
        dt.scale(0.9).move_to([-3.2, 1.0, 0])
        win.play(Write(dt), FadeIn(Text("default 1 decimal", font_size=18, color=GREY_B).next_to(dt, DOWN, buff=0.35)), run_time=0.8)

        # —— element_to_mobject_config: 3 decimal places ——
        dt2 = DecimalTable([[1.2345, 3.4567], [5.6789, 7.891]],
                           element_to_mobject_config={"num_decimal_places": 3},   # the "element_to_mobject_config" parameter
                           include_outer_lines=True)
        dt2.scale(0.9).move_to([2.4, 1.0, 0])
        win.play(Write(dt2), FadeIn(Text("num_decimal_places=3", font_size=18, color=GREY_B).next_to(dt2, DOWN, buff=0.35)), run_time=0.8)

        # —— element_to_mobject: switch to Integer (any numeric element is accepted; here it rounds) ——
        self.clear()   # clear the stage: take away the previous section's table and caption together
        self.add(title)
        dt3 = DecimalTable([[1.25, 3.5], [7.75, 9.0]], element_to_mobject=Integer,
                           element_to_mobject_config={"font_size": 40},   # the "element_to_mobject" parameter
                           include_outer_lines=True)
        dt3.scale(0.9).move_to([0, -2.0, 0])
        win.play(Write(dt3), FadeIn(Text("element_to_mobject=Integer", font_size=18, color=GREY_B).next_to(dt3, DOWN, buff=0.35)), run_time=0.8)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


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

PAGE = "14-Tables"


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
