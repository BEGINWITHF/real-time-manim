# -*- coding: utf-8 -*-
"""16-花括号标注.md 五个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 16-花括号标注.py <样例名>...
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
    Scene, Brace, BraceText, BraceLabel, BraceBetweenPoints, ArcBrace,
    Square, Line, Dot, Text, Arc, VGroup, MathTex, DEGREES,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, GrowFromCenter, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：Brace —— 朝向 / 间距 / 尖锐度 / 描边填充 / 方法 ==============
class BraceDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("16-Brace", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— direction：花括号在对象的哪一侧 ——
        group = VGroup()
        for i, (d, name) in enumerate([(DOWN, "DOWN"), (UP, "UP"), (LEFT, "LEFT"), (RIGHT, "RIGHT")]):   #参数 “direction”
            sq = Square(side_length=1.2, color=BLUE).move_to([-4.8 + i * 3.2, 1.1, 0])
            br = Brace(sq, direction=d, color=GREEN)   #参数 “mobject / direction”
            lbl = br.get_text(name, buff=0.06)   #方法 “get_text”：kwargs 只会传给 put_at_tip（即 next_to 的 buff）
            lbl.scale(0.55).set_color(GREY_B)   #Tex 的字号/颜色要事后设（get_text 不吃这些 kwargs）
            group.add(sq, br, lbl)
            win.play(Create(sq), GrowFromCenter(br), FadeIn(lbl), run_time=0.45)   #四种朝向依次出现
        win.play(FadeOut(group), run_time=0.3)

        # —— buff / sharpness：与对象的间距、拐角尖锐度 ——
        sq2 = Square(side_length=1.4, color=BLUE).move_to([-2.0, 0.6, 0])
        br2 = Brace(sq2, direction=DOWN, buff=0.9, sharpness=6, color=ORANGE)   #参数 “buff / sharpness”
        lbl2 = br2.get_text("buff=0.9  sharpness=6")   #方法 “get_text”
        lbl2.scale(0.6).set_color(GREY_B)
        win.play(Create(sq2), GrowFromCenter(br2), FadeIn(lbl2), run_time=0.6)
        win.play(FadeOut(sq2), FadeOut(br2), FadeOut(lbl2), run_time=0.25)

        # —— stroke_width / fill_opacity / background_stroke_width / background_stroke_color ——
        ln = Line(LEFT * 2.2, RIGHT * 2.2, color=BLUE)
        br3 = Brace(ln, direction=DOWN, stroke_width=2, fill_opacity=0.5,
                    background_stroke_width=10, background_stroke_color=RED)   #参数 “stroke_width / fill_opacity / background_*”
        lbl3 = br3.get_text("stroke 2 - fill 0.5 - bg 10 - RED")   #方法 “get_text”（Tex 是数学模式：字符串里别带下划线）
        lbl3.scale(0.5).set_color(GREY_B)
        win.play(Create(ln), GrowFromCenter(br3), FadeIn(lbl3), run_time=0.7)
        win.play(FadeOut(ln), FadeOut(lbl3), run_time=0.25)

        # —— 方法：get_tex / put_at_tip / get_tip / get_direction ——
        lbl4 = br3.get_tex(r"x^2+y^2=r^2")   #方法 “get_tex”：改用 MathTex 标签
        lbl4.scale(0.7).set_color(TEAL)
        win.play(FadeIn(lbl4), run_time=0.4)
        tip = br3.get_tip()   #方法 “get_tip()”：拿到尖端坐标
        dot = Dot(tip, color=YELLOW, radius=0.07)
        dirn = br3.get_direction()   #方法 “get_direction()”：拿到朝向向量
        cap = Text("tip + direction = (%d, %d)" % (round(dirn[0]), round(dirn[1])),
                   font_size=20, color=GREY_B).next_to(lbl4, DOWN, buff=0.25)
        win.play(FadeIn(dot), FadeIn(cap), run_time=0.4)
        win.play(FadeOut(lbl4), run_time=0.25)   #尖端标签和 get_tex 标签同一位置，先收掉旧的
        tag = Text("put_at_tip", font_size=22, color=PURPLE)
        br3.put_at_tip(tag)   #方法 “put_at_tip(mob)”：把对象放到尖端
        win.play(FadeIn(tag), run_time=0.4)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：BraceText —— 花括号 + 普通文本一步到位 =====================
class BraceTextDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("16-BraceText", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 默认：label_constructor=Text，花括号在下方 ——
        sq = Square(side_length=1.6, color=BLUE).move_to([-3.4, 0.9, 0])
        bt = BraceText(sq, "方形", font_size=28)   #参数 “obj / text”
        win.play(Create(sq), GrowFromCenter(bt), run_time=0.6)   #文字自动放在尖端外侧

        # —— label_constructor：把标签换成 MathTex ——
        sq2 = Square(side_length=1.6, color=TEAL).move_to([0.6, 0.9, 0])
        bt2 = BraceText(sq2, r"a^2", label_constructor=MathTex, font_size=40)   #参数 “label_constructor”
        win.play(Create(sq2), GrowFromCenter(bt2), run_time=0.6)

        # —— brace_direction / buff / brace_config：朝向、间距、花括号样式 ——
        sq3 = Square(side_length=1.6, color=GOLD).move_to([-3.4, -1.6, 0])
        bt3 = BraceText(sq3, "buff & config", brace_direction=RIGHT, font_size=24,
                        buff=0.7, brace_config={"color": ORANGE})   #参数 “brace_direction / buff / brace_config”
        win.play(Create(sq3), GrowFromCenter(bt3), run_time=0.7)

        # —— 花括号在上方、字号加大 ——
        sq4 = Square(side_length=1.6, color=PURPLE).move_to([2.8, -2.2, 0])
        bt4 = BraceText(sq4, "font_size=32", brace_direction=UP, font_size=32)   #参数 “font_size”
        win.play(Create(sq4), GrowFromCenter(bt4), run_time=0.7)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：BraceLabel —— 默认 MathTex 标签 + 四个方法 ==================
class BraceLabelDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("16-BraceLabel", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 默认：label_constructor=MathTex ——
        sq = Square(side_length=2.0, color=BLUE).move_to([0, 0.6, 0])
        bl = BraceLabel(sq, r"2 \times 2")   #参数 “obj / text”
        win.play(Create(sq), bl.creation_anim(), run_time=0.6)   #方法 “creation_anim”

        # —— change_label：换掉标签文字 ——
        old_label = bl.label   #入场动画把旧标签单独加进了场景：换标签时要一起收掉
        bl.change_label(r"\sqrt{2}")   #方法 “change_label(*text)”
        win.play(FadeOut(old_label), FadeIn(bl.label), run_time=0.5)

        # —— shift_brace：花括号换到另一侧（同时文字跟着走）——
        bl2 = BraceLabel(sq, "LEFT", brace_direction=LEFT, font_size=30,
                         brace_config={"color": TEAL})   #参数 “brace_direction / font_size / brace_config”
        bl.shift_brace(sq)   #方法 “shift_brace(obj)”：按对象重新贴一次
        win.play(GrowFromCenter(bl2), run_time=0.6)   #左侧再来一个做对比

        # —— change_brace_label：换对象 + 换标签 ——
        sq2 = Square(side_length=1.4, color=GREEN).move_to([-4.4, -2.0, 0])
        bl2.change_brace_label(sq2, "moved")   #方法 “change_brace_label(obj, *text)”
        win.play(Create(sq2), run_time=0.5)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：BraceBetweenPoints —— 标两点之间的距离 ======================
class BraceBetweenDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("16-BraceBetweenPoints", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— direction=DOWN：横向两点的下方 ——
        a, b = LEFT * 4.0 + UP * 1.4, RIGHT * 1.0 + UP * 1.4
        d1 = Dot(a, color=BLUE)
        d2 = Dot(b, color=BLUE)
        bb = BraceBetweenPoints(a, b, direction=DOWN, color=GREEN)   #参数 “point_1 / point_2 / direction”
        lbl = bb.get_text("distance")   #方法 “get_text”
        lbl.scale(0.6).set_color(GREY_B)
        win.play(FadeIn(d1), FadeIn(d2), GrowFromCenter(bb), FadeIn(lbl), run_time=0.7)

        # —— direction=UP：同一对点的上方 ——
        bb2 = BraceBetweenPoints(a, b, direction=UP, color=ORANGE)   #参数换成 UP
        win.play(GrowFromCenter(bb2), run_time=0.5)

        # —— get_tex：用公式当标签；同一对象可以只加标签 ——
        lbl2 = bb2.get_tex(r"\Delta x")   #方法 “get_tex”
        lbl2.scale(0.7).set_color(TEAL)
        win.play(FadeIn(lbl2), run_time=0.5)

        # —— 竖直两点 + LEFT 朝向 ——
        c, d = LEFT * 1.0 + DOWN * 2.4, LEFT * 1.0 + UP * 0.4
        bb3 = BraceBetweenPoints(c, d, direction=LEFT, color=PURPLE)
        lbl3 = bb3.get_text("dy")
        lbl3.scale(0.6).set_color(GREY_B)
        win.play(FadeIn(Dot(c, color=YELLOW)), FadeIn(Dot(d, color=YELLOW)),
                 GrowFromCenter(bb3), FadeIn(lbl3), run_time=0.7)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 5：ArcBrace —— 弧线花括号 ======================================
class ArcBraceDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("16-ArcBrace", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 给一段圆弧加花括号：direction=RIGHT ——
        arc = Arc(radius=1.4, start_angle=0, angle=90 * DEGREES, color=BLUE).move_to([-3.2, 0.4, 0])
        ab = ArcBrace(arc, direction=RIGHT, color=ORANGE)   #参数 “arc / direction”
        win.play(Create(arc), GrowFromCenter(ab), run_time=0.7)

        # —— direction=LEFT：甩到弧的另一侧 ——
        ab2 = ArcBrace(arc, direction=LEFT, color=TEAL)   #参数换成 LEFT
        win.play(GrowFromCenter(ab2), run_time=0.5)

        # —— 配自己的弧：更大的弧 + 标签 ——
        arc2 = Arc(radius=1.4, start_angle=90 * DEGREES, angle=90 * DEGREES, color=GREEN).move_to([3.2, 0.4, 0])
        ab3 = ArcBrace(arc2, direction=RIGHT, color=PURPLE)
        lbl = ab3.get_text("90 deg")   #方法 “get_text”
        lbl.scale(0.6).set_color(GREY_B)
        win.play(Create(arc2), GrowFromCenter(ab3), FadeIn(lbl), run_time=0.7)

        # —— arc=None：默认用单位圆 ——
        ab4 = ArcBrace(direction=RIGHT, color=RED).move_to([0, -2.2, 0])   #参数 “arc=None”
        cap = Text("arc=None（单位圆）", font_size=20, color=GREY_B).next_to(ab4, DOWN, buff=0.35)
        win.play(GrowFromCenter(ab4), FadeIn(cap), run_time=0.7)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("brace", BraceDemo),
    ("bracetext", BraceTextDemo),
    ("bracelabel", BraceLabelDemo),
    ("bracebetween", BraceBetweenDemo),
    ("arcbrace", ArcBraceDemo),
]

PAIRS = [
    ("brace", ["brace"]),
    ("bracetext", ["bracetext"]),
    ("bracelabel", ["bracelabel"]),
    ("bracebetween", ["bracebetween"]),
    ("arcbrace", ["arcbrace"]),
]

PAGE = "16-花括号标注"


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
