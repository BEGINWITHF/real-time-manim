# -*- coding: utf-8 -*-
"""Full source for the seven samples in 13-Matrices.md (identical to the code blocks in the page).

Usage: python 13-Matrices.py <sample names>...
With no arguments it renders every sample and concatenates the page's seven sample videos (written to assets/RTM output/).
"""
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    Scene, Matrix, DecimalMatrix, IntegerMatrix, MobjectMatrix, Integer,
    get_det_text, matrix_to_tex_string, matrix_to_mobject, DecimalNumber,
    Text, Circle, Square, Triangle, Dot, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, DR, UL, MED_SMALL_BUFF,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: Matrix —— cycling through every constructor parameter ====
class MatrixDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("13-Matrix", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        stage = VGroup()   # the previous step's matrix + caption: fade out before the next step so nothing overlaps
        def show(mob, cap, t=0.55):
            nonlocal stage
            grp = VGroup(mob, Text(cap, font_size=18, color=GREY_B).next_to(mob, DOWN, buff=0.35))
            if len(stage):
                win.play(FadeOut(stage), run_time=0.2)
            win.play(Write(mob), run_time=t)
            win.play(FadeIn(grp[1]), run_time=0.25)
            stage = grp

        # —— default parameters: a 2x2 integer matrix ——
        show(Matrix([[1, 2], [3, 4]], element_to_mobject_config={"font_size": 40}), "Matrix([[1,2],[3,4]])")

        # —— v_buff / h_buff: row and column spacing ——
        show(Matrix([[1, 2], [3, 4]], v_buff=1.6, h_buff=2.6, element_to_mobject_config={"font_size": 40}),
             "v_buff=1.6  h_buff=2.6")

        # —— bracket_h_buff / bracket_v_buff: spacing between the brackets and the content ——
        show(Matrix([[1, 2], [3, 4]], bracket_h_buff=0.8, bracket_v_buff=0.7, element_to_mobject_config={"font_size": 40}),
             "bracket_h_buff=0.8  bracket_v_buff=0.7")

        # —— left_bracket / right_bracket: swap the bracket shapes ——
        show(Matrix([[1, 2], [3, 4]], left_bracket="(", right_bracket=")", element_to_mobject_config={"font_size": 40}),
             'left_bracket="("  right_bracket=")"')
        show(Matrix([[1, 2], [3, 4]], left_bracket=r"\langle", right_bracket=r"\rangle", element_to_mobject_config={"font_size": 40}),
             'left_bracket=r"\\langle"  right_bracket=r"\\rangle"')

        # —— stretch_brackets=False: the brackets no longer stretch with the height (obvious on a tall, thin matrix) ——
        show(Matrix([[1], [2], [3], [4]], stretch_brackets=False, element_to_mobject_config={"font_size": 34}),
             "stretch_brackets=False")

        # —— add_background_rectangles_to_entries / include_background_rectangle ——
        show(Matrix([[1, 2], [3, 4]], add_background_rectangles_to_entries=True, element_to_mobject_config={"font_size": 40}),
             "add_background_rectangles_to_entries=True")
        show(Matrix([[1, 2], [3, 4]], include_background_rectangle=True, element_to_mobject_config={"font_size": 40}),
             "include_background_rectangle=True")

        # —— element_to_mobject / element_to_mobject_config: swap the element rendering class ——
        show(Matrix([["a", "b"], ["c", "d"]], element_to_mobject=Text,
                    element_to_mobject_config={"font_size": 36}),
             'element_to_mobject=Text  config={"font_size": 36}')

        # —— element_alignment_corner: swap the alignment corner inside the cell (visible when elements differ in size) ——
        show(Matrix([[1.2345, 2], [3, 4]], element_alignment_corner=UL, element_to_mobject_config={"font_size": 36}),
             "element_alignment_corner=UL")
        show(Matrix([[1.2345, 2], [3, 4]], element_alignment_corner=DR, element_to_mobject_config={"font_size": 36}),
             "element_alignment_corner=DR (default)")

        # —— bracket_config: change only the bracket style ——
        show(Matrix([[1, 2], [3, 4]], bracket_config={"color": ORANGE}, element_to_mobject_config={"font_size": 40}),
             'bracket_config={"color": ORANGE}')

        # —— methods: set_column_colors / set_row_colors / add_background_to_entries / get_* ——
        win.play(FadeOut(stage), run_time=0.25)   # clear the previous step's comparison first
        m = Matrix([[1, 2], [3, 4]], element_to_mobject_config={"font_size": 40})
        m2 = m.copy()
        win.play(Write(m), run_time=0.5)
        m.set_column_colors(RED, BLUE)   # the "set_column_colors(*colors)" method
        win.play(Write(m), run_time=0.3)
        win.play(FadeOut(m), run_time=0.25)
        m2.set_row_colors(GREEN, PURPLE)   # the "set_row_colors(*colors)" method
        m2.add_background_to_entries()   # the "add_background_to_entries()" method
        win.play(Write(m2), run_time=0.5)   # row colours + a per-cell background block
        info = Text("entries=%d rows=%d cols=%d brackets=%d" % (
            len(m2.get_entries()), len(m2.get_rows()), len(m2.get_columns()),
            len(m2.get_brackets())), font_size=20, color=GREY_B).next_to(m2, DOWN, buff=0.4)
        win.play(FadeIn(info), run_time=0.3)   # the "get_entries / get_rows / get_columns / get_brackets" methods
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: DecimalMatrix —— a decimal matrix ========================
class DecimalMatrixDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("13-DecimalMatrix", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— default: element_to_mobject=DecimalNumber, num_decimal_places=1 in the config ——
        d1 = DecimalMatrix([[1.2, 3.4], [5.6, 7.8]], element_to_mobject_config={"num_decimal_places": 1, "font_size": 40}).move_to(LEFT * 2.6 + UP * 0.6)
        cap1 = Text("DecimalMatrix([[...]])", font_size=18, color=GREY_B).next_to(d1, DOWN, buff=0.35)
        win.play(Write(d1), FadeIn(cap1), run_time=0.6)   # default 1 decimal place

        # —— element_to_mobject_config: change to 3 decimal places ——
        d2 = DecimalMatrix([[1.2345, 3.4567], [5.6789, 7.891]],
                           element_to_mobject_config={"num_decimal_places": 3, "font_size": 40}).move_to(RIGHT * 2.6 + UP * 0.6)
        cap2 = Text("num_decimal_places=3", font_size=18, color=GREY_B).next_to(d2, DOWN, buff=0.35)
        win.play(Write(d2), FadeIn(cap2), run_time=0.6)   # keep 3 places

        # —— element_to_mobject_config: 0 decimal places = rounded display ——
        d3 = DecimalMatrix([[1.2, 3.4], [5.6, 7.8]],
                           element_to_mobject_config={"num_decimal_places": 0, "font_size": 40}).move_to(DOWN * 1.8)
        cap3 = Text("num_decimal_places=0", font_size=18, color=GREY_B).next_to(d3, DOWN, buff=0.35)
        win.play(Write(d3), FadeIn(cap3), run_time=0.6)   # 0 places = rounded display

        # —— element_to_mobject: swap the whole class (switch to Integer rendering, elements become integers) ——
        # do not swap in Text/MathTex: they want strings, while DecimalMatrix's elements are floats,
        # so Text(1.2) raises AttributeError straight away (measured).
        d4 = DecimalMatrix([[1.2, 3.4], [5.6, 7.8]], element_to_mobject=Integer,
                           element_to_mobject_config={"font_size": 40}).move_to(DOWN * 1.8)
        win.play(FadeOut(d3), FadeOut(cap3), run_time=0.25)
        cap4 = Text("element_to_mobject=Integer", font_size=18, color=GREY_B).next_to(d4, DOWN, buff=0.35)
        win.play(Write(d4), FadeIn(cap4), run_time=0.6)   # switch to Integer rendering (wipes out the decimals)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: IntegerMatrix —— an integer matrix =======================
class IntegerMatrixDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("13-IntegerMatrix", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— default: element_to_mobject=Integer ——
        i1 = IntegerMatrix([[1, 2], [3, 4]], element_to_mobject_config={"font_size": 40}).move_to(LEFT * 2.6 + UP * 0.6)
        cap1 = Text("IntegerMatrix([[...]])", font_size=18, color=GREY_B).next_to(i1, DOWN, buff=0.35)
        win.play(Write(i1), FadeIn(cap1), run_time=0.6)

        # —— element_to_mobject: switch to DecimalNumber rendering (elements typeset as decimals) ——
        # do not swap in Text/MathTex: they want strings, while the matrix elements are numbers, so Text(1)
        # raises AttributeError (measured identically on both engines).
        i2 = IntegerMatrix([[1.5, 2.5], [3.5, 4.5]], element_to_mobject=DecimalNumber,
                           element_to_mobject_config={"num_decimal_places": 1, "font_size": 40}
                           ).move_to(RIGHT * 2.6 + UP * 0.6)
        cap2 = Text("element_to_mobject=DecimalNumber", font_size=18, color=GREY_B).next_to(i2, DOWN, buff=0.35)
        win.play(Write(i2), FadeIn(cap2), run_time=0.6)

        # —— the remaining parameters are the same as Matrix: v_buff / h_buff also work ——
        i3 = IntegerMatrix([[1, 2, 3], [4, 5, 6]], v_buff=1.4, h_buff=2.2,
                           element_to_mobject_config={"font_size": 40}).move_to(DOWN * 1.9)
        cap3 = Text("v_buff=1.4  h_buff=2.2", font_size=18, color=GREY_B).next_to(i3, DOWN, buff=0.35)
        win.play(Write(i3), FadeIn(cap3), run_time=0.6)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 4: MobjectMatrix —— the elements are arbitrary Mobjects =====
class MobjectMatrixDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("13-MobjectMatrix", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— the default element_to_mobject is the identity function: place ready-made objects directly ——
        circles = MobjectMatrix([[Circle(radius=0.3, color=TEAL), Square(side_length=0.6, color=GREEN)],
                                 [Triangle(color=ORANGE).scale(0.4), Dot(radius=0.16, color=RED)]],
                                v_buff=1.0, h_buff=1.6).move_to(UP * 0.8)
        cap1 = Text("MobjectMatrix([[Circle, Square], [Triangle, Dot]])",
                    font_size=18, color=GREY_B).next_to(circles, DOWN, buff=0.35)
        win.play(Create(circles), FadeIn(cap1), run_time=0.9)

        # —— element_to_mobject: give it a conversion function (here it shrinks everything by half) ——
        shrunk = MobjectMatrix([[Circle(radius=0.6, color=BLUE), Square(side_length=1.2, color=GOLD)],
                                [Triangle(color=PURPLE).scale(0.8), Dot(radius=0.3, color=YELLOW)]],
                               element_to_mobject=lambda m: m.copy().scale(0.5),   # the "element_to_mobject" parameter
                               v_buff=1.0, h_buff=1.6).move_to(DOWN * 2.2)
        cap2 = Text("element_to_mobject=lambda m: m.copy().scale(0.5)",
                    font_size=18, color=GREY_B).next_to(shrunk, DOWN, buff=0.3)
        win.play(Create(shrunk), FadeIn(cap2), run_time=0.9)
        win.play(Wait(0.5))   # hold to compare the two groups
        win.close()   # close the RTM window


# ===== Sample 5: get_det_text —— a determinant title ======================
class DetTextDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("13-get_det_text", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        m = Matrix([[1, 2], [3, 4]], element_to_mobject_config={"font_size": 40})
        win.play(Write(m), run_time=0.5)   # place the matrix first

        # —— determinant=None: only writes det(...) ——
        d0 = get_det_text(m, initial_scale_factor=1.0).next_to(m, DOWN, buff=0.5)   # the "matrix / initial_scale_factor" parameters
        win.play(FadeIn(d0), run_time=0.4)

        # —— determinant given a value: writes det(A) = value ——
        d1 = get_det_text(m, determinant=-2, initial_scale_factor=1.0).next_to(m, DOWN, buff=0.5)   # the "determinant" parameter
        win.play(FadeOut(d0), FadeIn(d1), run_time=0.4)

        # —— background_rect=True: pads this text with a black background ——
        d2 = get_det_text(m, determinant=-2, background_rect=True,
                          initial_scale_factor=1.4).next_to(m, DOWN, buff=0.5)   # the "background_rect / initial_scale_factor" parameters
        win.play(FadeOut(d1), FadeIn(d2), run_time=0.5)   # larger text with a background
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 6: matrix_to_tex_string —— converting to a LaTeX string =====
class TexStringDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("13-matrix_to_tex_string", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— only one parameter: the 2D data; returns a str (a bare array, no brackets) ——
        for i, data in enumerate([np.array([[1, 2], [3, 4]]),
                                  np.array([[1, 2, 3], [4, 5, 6]])]):
            s = matrix_to_tex_string(data)   # the "matrix" parameter
            lbl = Text(s.replace(" ", ""), font_size=20, color=TEAL).move_to([0, 0.9 - i * 1.8, 0])
            cap = Text("matrix_to_tex_string(%d x %d)" % data.shape,
                       font_size=18, color=GREY_B).next_to(lbl, DOWN, buff=0.25)
            win.play(FadeIn(lbl), FadeIn(cap), run_time=0.5)   # print the string straight onto the screen
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 7: matrix_to_mobject —— converting to a MathTex object ======
class TexMobjectDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("13-matrix_to_mobject", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— again the only parameter is the 2D data; returns a MathTex that can go straight on screen / take animation ——
        mob = matrix_to_mobject(np.array([[1, 2], [3, 4]]))   # the "matrix" parameter
        cap = Text("matrix_to_mobject(np.array([[1,2],[3,4]]))",
                   font_size=18, color=GREY_B).next_to(mob, DOWN, buff=0.4)
        win.play(Write(mob), FadeIn(cap), run_time=0.7)   # bare-array typesetting (no brackets)

        mob2 = matrix_to_mobject(np.array([[1.5, 2.5], [3.5, 4.5]])).next_to(mob, DOWN, buff=1.2)
        cap2 = Text("matrix_to_mobject(2 x 2 floats)", font_size=18, color=GREY_B).next_to(mob2, DOWN, buff=0.4)
        win.play(Write(mob2), FadeIn(cap2), run_time=0.7)   # decimals typeset too
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


SCENES = [
    ("matrix", MatrixDemo),
    ("decimal", DecimalMatrixDemo),
    ("integer", IntegerMatrixDemo),
    ("mobject", MobjectMatrixDemo),
    ("dettext", DetTextDemo),
    ("texstr", TexStringDemo),
    ("texmob", TexMobjectDemo),
]

PAIRS = [
    ("matrix", ["matrix"]),
    ("decimal", ["decimal"]),
    ("integer", ["integer"]),
    ("mobject", ["mobject"]),
    ("dettext", ["dettext"]),
    ("texstr", ["texstr"]),
    ("texmob", ["texmob"]),
]

PAGE = "13-Matrices"


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
