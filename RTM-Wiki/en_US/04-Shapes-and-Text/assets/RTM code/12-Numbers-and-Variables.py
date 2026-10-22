# -*- coding: utf-8 -*-
"""Full source for the four samples in 12-Numbers-and-Variables.md (identical to the code blocks in the page).

Usage: python 12-Numbers-and-Variables.py <sample names>...
With no arguments it renders every sample and concatenates the page's three sample videos (written to assets/RTM output/).
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
    Scene, DecimalNumber, Integer, Variable, ValueTracker,
    Text, MathTex, Square, Dot, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene
# RTM-specific: TextDecimalNumber renders numbers with Text and needs no LaTeX; ManimCE has no
# such class, so this sample is RTM-only (the CE version does not produce this comparison clip).
from real_time_manim.animations.text import TextDecimalNumber


def cap(text, mob, buff=0.3, color=GREY_B, size=18):
    return Text(text, font_size=size, color=color).next_to(mob, DOWN, buff=buff)


# ===== Sample 1: DecimalNumber —— numeric display =========================
class DecimalNumberDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("12-DecimalNumber", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title
        caps = VGroup()   # every caption in this section: fades out with the numbers when the section changes, so nothing overlaps
        def c(text, mob, buff=0.3):
            m = cap(text, mob, buff)
            caps.add(m)
            return m

        # —— default 2 decimal places / a longer num_decimal_places / show_ellipsis hinting at truncation ——
        d1 = DecimalNumber(3.14159).move_to([-5.2, 2.0, 0])   # the "number" parameter
        d2 = DecimalNumber(3.14159, num_decimal_places=5).move_to([-2.2, 2.0, 0])   # the "num_decimal_places" parameter
        d3 = DecimalNumber(3.14159, num_decimal_places=2, show_ellipsis=True).move_to([1.2, 2.0, 0])   # the "show_ellipsis" parameter
        win.play(Write(d1), FadeIn(c("default 2 places", d1)), run_time=0.5)
        win.play(Write(d2), FadeIn(c("num_decimal_places=5", d2)), run_time=0.5)
        win.play(Write(d3), FadeIn(c("show_ellipsis=True", d3)), run_time=0.5)

        # —— include_sign / group_with_commas: sign and thousands separators ——
        d4 = DecimalNumber(3.14, include_sign=True).move_to([-5.2, 0.6, 0])   # the "include_sign" parameter
        d5 = DecimalNumber(1234567.89, group_with_commas=True).move_to([-2.0, 0.6, 0])   # the "group_with_commas=True" parameter
        d6 = DecimalNumber(1234567.89, group_with_commas=False).move_to([2.0, 0.6, 0])
        win.play(Write(d4), FadeIn(c("include_sign=True", d4)), run_time=0.5)
        win.play(Write(d5), FadeIn(c("commas=True", d5)), run_time=0.5)
        win.play(Write(d6), FadeIn(c("commas=False", d6)), run_time=0.5)

        # —— digit_buff_per_font_unit / unit + unit_buff_per_font_unit ——
        d7 = DecimalNumber(2024, num_decimal_places=0, digit_buff_per_font_unit=0.06,
                           font_size=60).move_to([-5.0, -1.0, 0])   # the "digit_buff_per_font_unit / font_size" parameters
        d8 = DecimalNumber(3.14, unit=r"\pi", unit_buff_per_font_unit=0.02).move_to([-1.6, -1.0, 0])   # the "unit / unit_buff_per_font_unit" parameters
        win.play(Write(d7), FadeIn(c("digit_buff=0.06", d7)), run_time=0.5)
        win.play(Write(d8), FadeIn(c("unit=pi", d8)), run_time=0.5)

        # —— mob_class / include_background_rectangle / stroke_width / fill_opacity ——
        d9 = DecimalNumber(42, num_decimal_places=0, mob_class=Text).move_to([2.0, -1.0, 0])   # the "mob_class" parameter
        d10 = DecimalNumber(7, num_decimal_places=0, include_background_rectangle=True,
                            stroke_width=2, fill_opacity=0.6,
                            color=ORANGE).move_to([4.6, -1.0, 0])   # the "include_background_rectangle / stroke_width / fill_opacity" parameters
        win.play(Write(d9), FadeIn(c("mob_class=Text", d9)), run_time=0.5)
        win.play(Write(d10), FadeIn(c("bg rect + stroke + fill", d10)), run_time=0.5)
        win.play(FadeOut(VGroup(d1, d2, d3, d4, d5, d6, d7, d8, d9, d10)), FadeOut(caps), run_time=0.4)

        # —— edge_to_fix: which edge stays put when the value changes (the number does not "jitter") ——
        left = DecimalNumber(9.99, edge_to_fix=LEFT, font_size=60).move_to([-3.2, 1.4, 0])   # the "edge_to_fix=LEFT" parameter
        right = DecimalNumber(9.99, edge_to_fix=RIGHT, font_size=60).move_to([1.6, 1.4, 0]).align_to([1.6, 0, 0], RIGHT)
        win.play(Write(left), Write(right),
                 FadeIn(cap("edge_to_fix=LEFT", left)), FadeIn(cap("edge_to_fix=RIGHT", right)), run_time=0.6)
        left.set_value(100.0)   # the "set_value(number)" method
        right.set_value(100.0)
        win.play(Write(left), Write(right), run_time=0.6)   # see which edge did not move

        # —— get_value / increment_value ——
        n = DecimalNumber(5, num_decimal_places=0, font_size=60).move_to([-1.0, -1.6, 0])
        c7 = cap("get_value()=%s" % n.get_value(), n)
        win.play(FadeIn(n), FadeIn(c7), run_time=0.5)   # the "get_value()" method
        n.increment_value(3)   # the "increment_value(delta_t)" method
        c7.become(cap("increment_value(3) -> %s" % n.get_value(), n))
        win.play(Write(n), run_time=0.5)
        n.increment_value(-1)
        c7.become(cap("increment_value(-1) -> %s" % n.get_value(), n))
        win.play(Write(n), run_time=0.5)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: Integer —— an integer counter =============================
class IntegerDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("12-Integer", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— default num_decimal_places=0: no decimal point ——
        i1 = Integer(7).move_to([-5.0, 1.8, 0])   # the "number" parameter
        i2 = Integer(-42, font_size=60).move_to([-2.4, 1.8, 0])
        i3 = Integer(2024, include_sign=True).move_to([1.4, 1.8, 0])   # the other parameters are shared with DecimalNumber
        win.play(Write(i1), FadeIn(cap("Integer(7)", i1)), run_time=0.5)
        win.play(Write(i2), FadeIn(cap("Integer(-42)", i2)), run_time=0.5)
        win.play(Write(i3), FadeIn(cap("include_sign=True", i3)), run_time=0.5)

        # —— num_decimal_places must be 0 for the integer version (writing 2 brings out decimal places) ——
        i4 = Integer(5, num_decimal_places=0).move_to([-4.2, -0.2, 0])   # the "num_decimal_places" parameter
        i5 = DecimalNumber(5, num_decimal_places=2).move_to([-1.6, -0.2, 0])
        win.play(Write(i4), Write(i5),
                 FadeIn(cap("Integer vs DecimalNumber", i4)), run_time=0.6)

        # —— pair it with a ValueTracker to "count up": set_value inside the updater ——
        t = ValueTracker(0)   # the animatable number
        counter = Integer(0, font_size=72, color=TEAL).move_to([3.6, -0.6, 0])
        counter.add_updater(lambda m: m.set_value(int(t.get_value())))   # the "set_value" method
        win.play(FadeIn(counter), FadeIn(t), FadeIn(cap("tracker drives counter 0 -> 100", counter, buff=0.6)), run_time=0.6)
        win.play(t.animate.set_value(100), run_time=2.0)   # the number moves and the display follows
        win.play(FadeIn(cap("get_value()=%s" % counter.get_value(), counter, buff=1.3)), run_time=0.4)   # the "get_value()" method
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: Variable —— "variable = value" ============================
class VariableDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("12-Variable", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— default: var_type=DecimalNumber, num_decimal_places=2 ——
        v1 = Variable(2.5, "v").move_to([-4.4, 1.6, 0])   # the "var / label" parameters
        win.play(Write(v1), FadeIn(cap('Variable(2.5, "v")', v1)), run_time=0.6)

        # —— num_decimal_places + a formula label ——
        v2 = Variable(3.14159, r"{a}_{i}", num_decimal_places=4).move_to([-0.6, 1.6, 0])   # the "label (LaTeX) / num_decimal_places" parameters
        win.play(Write(v2), FadeIn(cap("num_decimal_places=4", v2)), run_time=0.6)

        # —— var_type: render the value with Integer; the label can also be given as a Text directly ——
        v3 = Variable(2024, Text("count", font_size=30), var_type=Integer).move_to([3.4, 1.6, 0])   # the "var_type" parameter
        win.play(Write(v3), FadeIn(cap("var_type=Integer", v3)), run_time=0.6)

        # —— tracker: animate the displayed value ——
        win.play(v1.tracker.animate.set_value(8.75), run_time=1.2)   # the "tracker" attribute: a ValueTracker
        win.play(FadeIn(cap("v1.tracker.animate.set_value(8.75)", v1)), run_time=0.5)

        # —— the three attributes: label / value / tracker ——
        info = VGroup(cap("label=%s" % type(v1.label).__name__, v1, buff=1.0),
                      cap("value=%s" % type(v1.value).__name__, v1, buff=1.5),
                      cap("tracker=%s" % type(v1.tracker).__name__, v1, buff=2.0))
        win.play(FadeIn(info), run_time=0.6)
        win.play(FadeIn(cap("value.get_value()=%s" % v1.value.get_value(), v1, buff=2.5)), run_time=0.5)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 4: TextDecimalNumber —— numbers without LaTeX (RTM-specific) ==
class TextDecimalDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("12-TextDecimalNumber", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— number / num_decimal_places: initial value and decimal places ——
        t1 = TextDecimalNumber(3.14159).move_to([-5.0, 1.6, 0])   # the "number" parameter (default 2 decimal places)
        t2 = TextDecimalNumber(3.14159, num_decimal_places=4).move_to([-1.6, 1.6, 0])   # the "num_decimal_places" parameter
        win.play(FadeIn(t1), FadeIn(cap("number=3.14159", t1)), run_time=0.5)
        win.play(FadeIn(t2), FadeIn(cap("num_decimal_places=4", t2)), run_time=0.5)

        # —— font_size / font: font size and font (both rendered with Text, no LaTeX needed) ——
        t3 = TextDecimalNumber(2024, num_decimal_places=0, font_size=72,
                               font="Arial").move_to([-4.6, -0.6, 0])   # the "font_size / font" parameters
        win.play(FadeIn(t3), FadeIn(cap('font_size=72 font="Arial"', t3)), run_time=0.5)

        # —— changing the value: set_value changes it immediately, only a ValueTracker with an updater animates ——
        t4 = TextDecimalNumber(0, num_decimal_places=1, font_size=60,
                               color=TEAL).move_to([1.6, -0.6, 0])
        tracker = ValueTracker(0)
        t4.add_updater(lambda m: m.set_value(tracker.get_value()))   # the "set_value" method
        win.play(FadeIn(t4), FadeIn(tracker), FadeIn(cap("tracker 0 -> 9.5", t4, buff=0.6)), run_time=0.6)
        win.play(tracker.animate.set_value(9.5), run_time=1.6)   # the number changes continuously

        # —— it really is a Text: every Text attribute works ——
        t5 = TextDecimalNumber(12.5, num_decimal_places=1).move_to([4.4, 1.6, 0])
        win.play(FadeIn(t5), FadeIn(cap("parent = %s" % type(t5).__mro__[1].__name__, t5)), run_time=0.6)
        win.play(FadeIn(cap("accepts only number/font_size/font/num_decimal_places", t5, buff=0.8, size=16)), run_time=0.5)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


SCENES = [
    ("decimal", DecimalNumberDemo),
    ("integer", IntegerDemo),
    ("variable", VariableDemo),
    ("textdecimal", TextDecimalDemo),   # RTM-only (ManimCE has no TextDecimalNumber)
]

PAIRS = [
    ("decimal", ["decimal"]),
    ("integer", ["integer"]),
    ("variable", ["variable"]),
    ("textdecimal", ["textdecimal"]),   # RTM-only
]

PAGE = "12-Numbers-and-Variables"


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
