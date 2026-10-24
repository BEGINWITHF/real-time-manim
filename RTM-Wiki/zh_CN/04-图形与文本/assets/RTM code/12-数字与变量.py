# -*- coding: utf-8 -*-
"""12-数字与变量.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 12-数字与变量.py <样例名>...
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
    Scene, DecimalNumber, Integer, Variable, ValueTracker,
    Text, MathTex, Square, Dot, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene
# RTM 特有：TextDecimalNumber 用 Text 渲染数字，不需要 LaTeX；ManimCE 无此类，
# 所以这一条只有 RTM 单边样例（CE 版不生成这条对比片）。
from real_time_manim.animations.text import TextDecimalNumber


def cap(text, mob, buff=0.3, color=GREY_B, size=18):
    return Text(text, font_size=size, color=color).next_to(mob, DOWN, buff=buff)


# ===== 样例 1：DecimalNumber —— 数值显示 ===================================
class DecimalNumberDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("12-DecimalNumber", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题
        caps = VGroup()   #本段所有字幕：换段时和数字一起淡出，避免叠字
        def c(text, mob, buff=0.3):
            m = cap(text, mob, buff)
            caps.add(m)
            return m

        # —— 默认 2 位小数 / num_decimal_places 加长 / show_ellipsis 提示被截断 ——
        d1 = DecimalNumber(3.14159).move_to([-5.2, 2.0, 0])   #参数 “number”
        d2 = DecimalNumber(3.14159, num_decimal_places=5).move_to([-2.2, 2.0, 0])   #参数 “num_decimal_places”
        d3 = DecimalNumber(3.14159, num_decimal_places=2, show_ellipsis=True).move_to([1.2, 2.0, 0])   #参数 “show_ellipsis”
        win.play(Write(d1), FadeIn(c("默认 2 位", d1)), run_time=0.5)
        win.play(Write(d2), FadeIn(c("num_decimal_places=5", d2)), run_time=0.5)
        win.play(Write(d3), FadeIn(c("show_ellipsis=True", d3)), run_time=0.5)

        # —— include_sign / group_with_commas：符号与千分位 ——
        d4 = DecimalNumber(3.14, include_sign=True).move_to([-5.2, 0.6, 0])   #参数 “include_sign”
        d5 = DecimalNumber(1234567.89, group_with_commas=True).move_to([-2.0, 0.6, 0])   #参数 “group_with_commas=True”
        d6 = DecimalNumber(1234567.89, group_with_commas=False).move_to([2.0, 0.6, 0])
        win.play(Write(d4), FadeIn(c("include_sign=True", d4)), run_time=0.5)
        win.play(Write(d5), FadeIn(c("commas=True", d5)), run_time=0.5)
        win.play(Write(d6), FadeIn(c("commas=False", d6)), run_time=0.5)

        # —— digit_buff_per_font_unit / unit + unit_buff_per_font_unit ——
        d7 = DecimalNumber(2024, num_decimal_places=0, digit_buff_per_font_unit=0.06,
                           font_size=60).move_to([-5.0, -1.0, 0])   #参数 “digit_buff_per_font_unit / font_size”
        d8 = DecimalNumber(3.14, unit=r"\pi", unit_buff_per_font_unit=0.02).move_to([-1.6, -1.0, 0])   #参数 “unit / unit_buff_per_font_unit”
        win.play(Write(d7), FadeIn(c("digit_buff=0.06", d7)), run_time=0.5)
        win.play(Write(d8), FadeIn(c("unit=pi", d8)), run_time=0.5)

        # —— mob_class / include_background_rectangle / stroke_width / fill_opacity ——
        d9 = DecimalNumber(42, num_decimal_places=0, mob_class=Text).move_to([2.0, -1.0, 0])   #参数 “mob_class”
        d10 = DecimalNumber(7, num_decimal_places=0, include_background_rectangle=True,
                            stroke_width=2, fill_opacity=0.6,
                            color=ORANGE).move_to([4.6, -1.0, 0])   #参数 “include_background_rectangle / stroke_width / fill_opacity”
        win.play(Write(d9), FadeIn(c("mob_class=Text", d9)), run_time=0.5)
        win.play(Write(d10), FadeIn(c("背景框 + stroke + fill", d10)), run_time=0.5)
        win.play(FadeOut(VGroup(d1, d2, d3, d4, d5, d6, d7, d8, d9, d10)), FadeOut(caps), run_time=0.4)

        # —— edge_to_fix：改值时固定哪条边（数字不“跳动”）——
        left = DecimalNumber(9.99, edge_to_fix=LEFT, font_size=60).move_to([-3.2, 1.4, 0])   #参数 “edge_to_fix=LEFT”
        right = DecimalNumber(9.99, edge_to_fix=RIGHT, font_size=60).move_to([1.6, 1.4, 0]).align_to([1.6, 0, 0], RIGHT)
        win.play(Write(left), Write(right),
                 FadeIn(cap("edge_to_fix=LEFT", left)), FadeIn(cap("edge_to_fix=RIGHT", right)), run_time=0.6)
        left.set_value(100.0)   #方法 “set_value(number)”
        right.set_value(100.0)
        win.play(Write(left), Write(right), run_time=0.6)   #看哪条边没动

        # —— get_value / increment_value ——
        n = DecimalNumber(5, num_decimal_places=0, font_size=60).move_to([-1.0, -1.6, 0])
        c7 = cap("get_value()=%s" % n.get_value(), n)
        win.play(FadeIn(n), FadeIn(c7), run_time=0.5)   #方法 “get_value()”
        n.increment_value(3)   #方法 “increment_value(delta_t)”
        c7.become(cap("increment_value(3) -> %s" % n.get_value(), n))
        win.play(Write(n), run_time=0.5)
        n.increment_value(-1)
        c7.become(cap("increment_value(-1) -> %s" % n.get_value(), n))
        win.play(Write(n), run_time=0.5)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：Integer —— 整数计数器 =======================================
class IntegerDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("12-Integer", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 默认 num_decimal_places=0：不带小数点 ——
        i1 = Integer(7).move_to([-5.0, 1.8, 0])   #参数 “number”
        i2 = Integer(-42, font_size=60).move_to([-2.4, 1.8, 0])
        i3 = Integer(2024, include_sign=True).move_to([1.4, 1.8, 0])   #其余参数与 DecimalNumber 通用
        win.play(Write(i1), FadeIn(cap("Integer(7)", i1)), run_time=0.5)
        win.play(Write(i2), FadeIn(cap("Integer(-42)", i2)), run_time=0.5)
        win.play(Write(i3), FadeIn(cap("include_sign=True", i3)), run_time=0.5)

        # —— num_decimal_places 写 0 才是整数版（写 2 会带出小数位）——
        i4 = Integer(5, num_decimal_places=0).move_to([-4.2, -0.2, 0])   #参数 “num_decimal_places”
        i5 = DecimalNumber(5, num_decimal_places=2).move_to([-1.6, -0.2, 0])
        win.play(Write(i4), Write(i5),
                 FadeIn(cap("Integer vs DecimalNumber", i4)), run_time=0.6)

        # —— 配 ValueTracker 做“跳数”：updater 里 set_value ——
        t = ValueTracker(0)   #可动画数值
        counter = Integer(0, font_size=72, color=TEAL).move_to([3.6, -0.6, 0])
        counter.add_updater(lambda m: m.set_value(int(t.get_value())))   #方法 “set_value”
        win.play(FadeIn(counter), FadeIn(t), FadeIn(cap("tracker 驱动计数 0 -> 100", counter, buff=0.6)), run_time=0.6)
        win.play(t.animate.set_value(100), run_time=2.0)   #数值动起来，显示跟着变
        win.play(FadeIn(cap("get_value()=%s" % counter.get_value(), counter, buff=1.3)), run_time=0.4)   #方法 “get_value()”
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：Variable —— “变量 = 值” =====================================
class VariableDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("12-Variable", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 默认：var_type=DecimalNumber、num_decimal_places=2 ——
        v1 = Variable(2.5, "v").move_to([-4.4, 1.6, 0])   #参数 “var / label”
        win.play(Write(v1), FadeIn(cap('Variable(2.5, "v")', v1)), run_time=0.6)

        # —— num_decimal_places + 公式标签 ——
        v2 = Variable(3.14159, r"{a}_{i}", num_decimal_places=4).move_to([-0.6, 1.6, 0])   #参数 “label（LaTeX）/ num_decimal_places”
        win.play(Write(v2), FadeIn(cap("num_decimal_places=4", v2)), run_time=0.6)

        # —— var_type：值换成 Integer 渲染；标签也能直接给 Text ——
        v3 = Variable(2024, Text("count", font_size=30), var_type=Integer).move_to([3.4, 1.6, 0])   #参数 “var_type”
        win.play(Write(v3), FadeIn(cap("var_type=Integer", v3)), run_time=0.6)

        # —— tracker：动画更新显示值 ——
        win.play(v1.tracker.animate.set_value(8.75), run_time=1.2)   #属性 “tracker”：ValueTracker
        win.play(FadeIn(cap("v1.tracker.animate.set_value(8.75)", v1)), run_time=0.5)

        # —— 三个属性：label / value / tracker ——
        info = VGroup(cap("label=%s" % type(v1.label).__name__, v1, buff=1.0),
                      cap("value=%s" % type(v1.value).__name__, v1, buff=1.5),
                      cap("tracker=%s" % type(v1.tracker).__name__, v1, buff=2.0))
        win.play(FadeIn(info), run_time=0.6)
        win.play(FadeIn(cap("value.get_value()=%s" % v1.value.get_value(), v1, buff=2.5)), run_time=0.5)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：TextDecimalNumber —— 不依赖 LaTeX 的数字（RTM 特有）=========
class TextDecimalDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("12-TextDecimalNumber", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— number / num_decimal_places：初始值与小数位 ——
        t1 = TextDecimalNumber(3.14159).move_to([-5.0, 1.6, 0])   #参数 “number”（默认 2 位小数）
        t2 = TextDecimalNumber(3.14159, num_decimal_places=4).move_to([-1.6, 1.6, 0])   #参数 “num_decimal_places”
        win.play(FadeIn(t1), FadeIn(cap("number=3.14159", t1)), run_time=0.5)
        win.play(FadeIn(t2), FadeIn(cap("num_decimal_places=4", t2)), run_time=0.5)

        # —— font_size / font：字号与字体（都用 Text 渲染，不需要 LaTeX）——
        t3 = TextDecimalNumber(2024, num_decimal_places=0, font_size=72,
                               font="Arial").move_to([-4.6, -0.6, 0])   #参数 “font_size / font”
        win.play(FadeIn(t3), FadeIn(cap('font_size=72 font="Arial"', t3)), run_time=0.5)

        # —— 改值：set_value 立即改，ValueTracker 配 updater 才有动画 ——
        t4 = TextDecimalNumber(0, num_decimal_places=1, font_size=60,
                               color=TEAL).move_to([1.6, -0.6, 0])
        tracker = ValueTracker(0)
        t4.add_updater(lambda m: m.set_value(tracker.get_value()))   #方法 “set_value”
        win.play(FadeIn(t4), FadeIn(tracker), FadeIn(cap("tracker 0 -> 9.5", t4, buff=0.6)), run_time=0.6)
        win.play(tracker.animate.set_value(9.5), run_time=1.6)   #数字连续变化

        # —— 它其实是个 Text：Text 的属性都能用 ——
        t5 = TextDecimalNumber(12.5, num_decimal_places=1).move_to([4.4, 1.6, 0])
        win.play(FadeIn(t5), FadeIn(cap("父类 = %s" % type(t5).__mro__[1].__name__, t5)), run_time=0.6)
        win.play(FadeIn(cap("只吃 number/font_size/font/num_decimal_places", t5, buff=0.8, size=16)), run_time=0.5)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("decimal", DecimalNumberDemo),
    ("integer", IntegerDemo),
    ("variable", VariableDemo),
    ("textdecimal", TextDecimalDemo),   # RTM-only（ManimCE 无 TextDecimalNumber）
]

PAIRS = [
    ("decimal", ["decimal"]),
    ("integer", ["integer"]),
    ("variable", ["variable"]),
    ("textdecimal", ["textdecimal"]),   # RTM-only
]

PAGE = "12-数字与变量"


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
