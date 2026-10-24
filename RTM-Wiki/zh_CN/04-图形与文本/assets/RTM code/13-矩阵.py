# -*- coding: utf-8 -*-
"""13-矩阵.md 七个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 13-矩阵.py <样例名>...
不带参数就渲染全部样例，并拼出页面里的七条样例视频（输出到 assets/RTM output/）。
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

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


# ===== 样例 1：Matrix —— 全部构造参数轮一遍 ================================
class MatrixDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("13-Matrix", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        stage = VGroup()   #上一步的矩阵+字幕：换步时先淡出，避免叠图叠字
        def show(mob, cap, t=0.55):
            nonlocal stage
            grp = VGroup(mob, Text(cap, font_size=18, color=GREY_B).next_to(mob, DOWN, buff=0.35))
            if len(stage):
                win.play(FadeOut(stage), run_time=0.2)
            win.play(Write(mob), run_time=t)
            win.play(FadeIn(grp[1]), run_time=0.25)
            stage = grp

        # —— 默认参数：2x2 整数矩阵 ——
        show(Matrix([[1, 2], [3, 4]], element_to_mobject_config={"font_size": 40}), "Matrix([[1,2],[3,4]])")

        # —— v_buff / h_buff：行距与列距 ——
        show(Matrix([[1, 2], [3, 4]], v_buff=1.6, h_buff=2.6, element_to_mobject_config={"font_size": 40}),
             "v_buff=1.6  h_buff=2.6")

        # —— bracket_h_buff / bracket_v_buff：括号与内容之间的间距 ——
        show(Matrix([[1, 2], [3, 4]], bracket_h_buff=0.8, bracket_v_buff=0.7, element_to_mobject_config={"font_size": 40}),
             "bracket_h_buff=0.8  bracket_v_buff=0.7")

        # —— left_bracket / right_bracket：换括号形状 ——
        show(Matrix([[1, 2], [3, 4]], left_bracket="(", right_bracket=")", element_to_mobject_config={"font_size": 40}),
             'left_bracket="("  right_bracket=")"')
        show(Matrix([[1, 2], [3, 4]], left_bracket=r"\langle", right_bracket=r"\rangle", element_to_mobject_config={"font_size": 40}),
             'left_bracket=r"\\langle"  right_bracket=r"\\rangle"')

        # —— stretch_brackets=False：括号不再随高度拉伸（高瘦矩阵对比明显）——
        show(Matrix([[1], [2], [3], [4]], stretch_brackets=False, element_to_mobject_config={"font_size": 34}),
             "stretch_brackets=False")

        # —— add_background_rectangles_to_entries / include_background_rectangle ——
        show(Matrix([[1, 2], [3, 4]], add_background_rectangles_to_entries=True, element_to_mobject_config={"font_size": 40}),
             "add_background_rectangles_to_entries=True")
        show(Matrix([[1, 2], [3, 4]], include_background_rectangle=True, element_to_mobject_config={"font_size": 40}),
             "include_background_rectangle=True")

        # —— element_to_mobject / element_to_mobject_config：换元素渲染类 ——
        show(Matrix([["a", "b"], ["c", "d"]], element_to_mobject=Text,
                    element_to_mobject_config={"font_size": 36}),
             'element_to_mobject=Text  config={"font_size": 36}')

        # —— element_alignment_corner：换单元格内的对齐角（元素大小不一时看得出）——
        show(Matrix([[1.2345, 2], [3, 4]], element_alignment_corner=UL, element_to_mobject_config={"font_size": 36}),
             "element_alignment_corner=UL")
        show(Matrix([[1.2345, 2], [3, 4]], element_alignment_corner=DR, element_to_mobject_config={"font_size": 36}),
             "element_alignment_corner=DR（默认）")

        # —— bracket_config：只改括号样式 ——
        show(Matrix([[1, 2], [3, 4]], bracket_config={"color": ORANGE}, element_to_mobject_config={"font_size": 40}),
             'bracket_config={"color": ORANGE}')

        # —— 方法：set_column_colors / set_row_colors / add_background_to_entries / get_* ——
        win.play(FadeOut(stage), run_time=0.25)   #先清掉上一步的对比图
        m = Matrix([[1, 2], [3, 4]], element_to_mobject_config={"font_size": 40})
        m2 = m.copy()
        win.play(Write(m), run_time=0.5)
        m.set_column_colors(RED, BLUE)   #方法 “set_column_colors(*colors)”
        win.play(Write(m), run_time=0.3)
        win.play(FadeOut(m), run_time=0.25)
        m2.set_row_colors(GREEN, PURPLE)   #方法 “set_row_colors(*colors)”
        m2.add_background_to_entries()   #方法 “add_background_to_entries()”
        win.play(Write(m2), run_time=0.5)   #行色 + 每格背景块
        info = Text("entries=%d rows=%d cols=%d brackets=%d" % (
            len(m2.get_entries()), len(m2.get_rows()), len(m2.get_columns()),
            len(m2.get_brackets())), font_size=20, color=GREY_B).next_to(m2, DOWN, buff=0.4)
        win.play(FadeIn(info), run_time=0.3)   #方法 “get_entries / get_rows / get_columns / get_brackets”
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：DecimalMatrix —— 小数矩阵 ===================================
class DecimalMatrixDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("13-DecimalMatrix", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 默认：element_to_mobject=DecimalNumber，config 里 num_decimal_places=1 ——
        d1 = DecimalMatrix([[1.2, 3.4], [5.6, 7.8]], element_to_mobject_config={"num_decimal_places": 1, "font_size": 40}).move_to(LEFT * 2.6 + UP * 0.6)
        cap1 = Text("DecimalMatrix([[...]])", font_size=18, color=GREY_B).next_to(d1, DOWN, buff=0.35)
        win.play(Write(d1), FadeIn(cap1), run_time=0.6)   #默认 1 位小数

        # —— element_to_mobject_config：改成 3 位小数 ——
        d2 = DecimalMatrix([[1.2345, 3.4567], [5.6789, 7.891]],
                           element_to_mobject_config={"num_decimal_places": 3, "font_size": 40}).move_to(RIGHT * 2.6 + UP * 0.6)
        cap2 = Text("num_decimal_places=3", font_size=18, color=GREY_B).next_to(d2, DOWN, buff=0.35)
        win.play(Write(d2), FadeIn(cap2), run_time=0.6)   #保留 3 位

        # —— element_to_mobject_config：0 位小数 = 取整显示 ——
        d3 = DecimalMatrix([[1.2, 3.4], [5.6, 7.8]],
                           element_to_mobject_config={"num_decimal_places": 0, "font_size": 40}).move_to(DOWN * 1.8)
        cap3 = Text("num_decimal_places=0", font_size=18, color=GREY_B).next_to(d3, DOWN, buff=0.35)
        win.play(Write(d3), FadeIn(cap3), run_time=0.6)   #0 位小数 = 取整显示

        # —— element_to_mobject：整类换掉（换 Integer 渲染，元素变整数）——
        # 注意别换 Text/MathTex：它们要字符串，而 DecimalMatrix 的元素是浮点数，
        # Text(1.2) 会直接抛 AttributeError（实测）。
        d4 = DecimalMatrix([[1.2, 3.4], [5.6, 7.8]], element_to_mobject=Integer,
                           element_to_mobject_config={"font_size": 40}).move_to(DOWN * 1.8)
        win.play(FadeOut(d3), FadeOut(cap3), run_time=0.25)
        cap4 = Text("element_to_mobject=Integer", font_size=18, color=GREY_B).next_to(d4, DOWN, buff=0.35)
        win.play(Write(d4), FadeIn(cap4), run_time=0.6)   #换成 Integer 渲染（抹掉小数）
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：IntegerMatrix —— 整数矩阵 ==================================
class IntegerMatrixDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("13-IntegerMatrix", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 默认：element_to_mobject=Integer ——
        i1 = IntegerMatrix([[1, 2], [3, 4]], element_to_mobject_config={"font_size": 40}).move_to(LEFT * 2.6 + UP * 0.6)
        cap1 = Text("IntegerMatrix([[...]])", font_size=18, color=GREY_B).next_to(i1, DOWN, buff=0.35)
        win.play(Write(i1), FadeIn(cap1), run_time=0.6)

        # —— element_to_mobject：换成 DecimalNumber 渲染（元素按小数排版）——
        # 别换成 Text/MathTex：它们要字符串，而矩阵元素是数字，Text(1) 会抛
        # AttributeError（实测两引擎一致）。
        i2 = IntegerMatrix([[1.5, 2.5], [3.5, 4.5]], element_to_mobject=DecimalNumber,
                           element_to_mobject_config={"num_decimal_places": 1, "font_size": 40}
                           ).move_to(RIGHT * 2.6 + UP * 0.6)
        cap2 = Text("element_to_mobject=DecimalNumber", font_size=18, color=GREY_B).next_to(i2, DOWN, buff=0.35)
        win.play(Write(i2), FadeIn(cap2), run_time=0.6)

        # —— 其余参数与 Matrix 相同：v_buff / h_buff 也能用 ——
        i3 = IntegerMatrix([[1, 2, 3], [4, 5, 6]], v_buff=1.4, h_buff=2.2,
                           element_to_mobject_config={"font_size": 40}).move_to(DOWN * 1.9)
        cap3 = Text("v_buff=1.4  h_buff=2.2", font_size=18, color=GREY_B).next_to(i3, DOWN, buff=0.35)
        win.play(Write(i3), FadeIn(cap3), run_time=0.6)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：MobjectMatrix —— 元素是任意 Mobject =========================
class MobjectMatrixDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("13-MobjectMatrix", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 默认 element_to_mobject 是恒等函数：直接摆现成对象 ——
        circles = MobjectMatrix([[Circle(radius=0.3, color=TEAL), Square(side_length=0.6, color=GREEN)],
                                 [Triangle(color=ORANGE).scale(0.4), Dot(radius=0.16, color=RED)]],
                                v_buff=1.0, h_buff=1.6).move_to(UP * 0.8)
        cap1 = Text("MobjectMatrix([[Circle, Square], [Triangle, Dot]])",
                    font_size=18, color=GREY_B).next_to(circles, DOWN, buff=0.35)
        win.play(Create(circles), FadeIn(cap1), run_time=0.9)

        # —— element_to_mobject：给一个转换函数（这里统一缩小一半）——
        shrunk = MobjectMatrix([[Circle(radius=0.6, color=BLUE), Square(side_length=1.2, color=GOLD)],
                                [Triangle(color=PURPLE).scale(0.8), Dot(radius=0.3, color=YELLOW)]],
                               element_to_mobject=lambda m: m.copy().scale(0.5),   #参数 “element_to_mobject”
                               v_buff=1.0, h_buff=1.6).move_to(DOWN * 2.2)
        cap2 = Text("element_to_mobject=lambda m: m.copy().scale(0.5)",
                    font_size=18, color=GREY_B).next_to(shrunk, DOWN, buff=0.3)
        win.play(Create(shrunk), FadeIn(cap2), run_time=0.9)
        win.play(Wait(0.5))   #停留对比两组
        win.close()   #关闭 RTM 窗口


# ===== 样例 5：get_det_text —— 行列式标题 ==================================
class DetTextDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("13-get_det_text", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        m = Matrix([[1, 2], [3, 4]], element_to_mobject_config={"font_size": 40})
        win.play(Write(m), run_time=0.5)   #先放矩阵

        # —— determinant=None：只写 det(...) ——
        d0 = get_det_text(m, initial_scale_factor=1.0).next_to(m, DOWN, buff=0.5)   #参数 “matrix / initial_scale_factor”
        win.play(FadeIn(d0), run_time=0.4)

        # —— determinant 给数值：写出 det(A) = 值 ——
        d1 = get_det_text(m, determinant=-2, initial_scale_factor=1.0).next_to(m, DOWN, buff=0.5)   #参数 “determinant”
        win.play(FadeOut(d0), FadeIn(d1), run_time=0.4)

        # —— background_rect=True：给这段文字垫黑底 ——
        d2 = get_det_text(m, determinant=-2, background_rect=True,
                          initial_scale_factor=1.4).next_to(m, DOWN, buff=0.5)   #参数 “background_rect / initial_scale_factor”
        win.play(FadeOut(d1), FadeIn(d2), run_time=0.5)   #字更大且带底色
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 6：matrix_to_tex_string —— 转成 LaTeX 字符串 ===================
class TexStringDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("13-matrix_to_tex_string", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 参数只有一个：二维数据；返回 str（不带括号的裸数组）——
        for i, data in enumerate([np.array([[1, 2], [3, 4]]),
                                  np.array([[1, 2, 3], [4, 5, 6]])]):
            s = matrix_to_tex_string(data)   #参数 “matrix”
            lbl = Text(s.replace(" ", ""), font_size=20, color=TEAL).move_to([0, 0.9 - i * 1.8, 0])
            cap = Text("matrix_to_tex_string(%d x %d)" % data.shape,
                       font_size=18, color=GREY_B).next_to(lbl, DOWN, buff=0.25)
            win.play(FadeIn(lbl), FadeIn(cap), run_time=0.5)   #直接把字符串打在屏幕上
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 7：matrix_to_mobject —— 转成 MathTex 对象 ======================
class TexMobjectDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("13-matrix_to_mobject", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 参数同样只有二维数据；返回 MathTex，可直接上屏/加动画 ——
        mob = matrix_to_mobject(np.array([[1, 2], [3, 4]]))   #参数 “matrix”
        cap = Text("matrix_to_mobject(np.array([[1,2],[3,4]]))",
                   font_size=18, color=GREY_B).next_to(mob, DOWN, buff=0.4)
        win.play(Write(mob), FadeIn(cap), run_time=0.7)   #裸数组排版（无括号）

        mob2 = matrix_to_mobject(np.array([[1.5, 2.5], [3.5, 4.5]])).next_to(mob, DOWN, buff=1.2)
        cap2 = Text("matrix_to_mobject(2 x 2 floats)", font_size=18, color=GREY_B).next_to(mob2, DOWN, buff=0.4)
        win.play(Write(mob2), FadeIn(cap2), run_time=0.7)   #小数也能排
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


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

PAGE = "13-矩阵"


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
