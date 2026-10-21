# -*- coding: utf-8 -*-
"""Full source for the five samples in 16-Braces.md (identical to the code blocks in the page).

Usage: python 16-Braces.py <sample names>...
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
    Scene, Brace, BraceText, BraceLabel, BraceBetweenPoints, ArcBrace,
    Square, Line, Dot, Text, Arc, VGroup, MathTex, DEGREES,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, GrowFromCenter, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: Brace —— direction / spacing / sharpness / stroke and fill / methods
class BraceDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("16-Brace", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— direction: which side of the object the brace is on ——
        group = VGroup()
        for i, (d, name) in enumerate([(DOWN, "DOWN"), (UP, "UP"), (LEFT, "LEFT"), (RIGHT, "RIGHT")]):   # the "direction" parameter
            sq = Square(side_length=1.2, color=BLUE).move_to([-4.8 + i * 3.2, 1.1, 0])
            br = Brace(sq, direction=d, color=GREEN)   # the "mobject / direction" parameters
            lbl = br.get_text(name, buff=0.06)   # the "get_text" method: the kwargs only go to put_at_tip (i.e. next_to's buff)
            lbl.scale(0.55).set_color(GREY_B)   # a Tex's font size/colour must be set afterwards (get_text does not take those kwargs)
            group.add(sq, br, lbl)
            win.play(Create(sq), GrowFromCenter(br), FadeIn(lbl), run_time=0.45)   # the four directions appear one after another
        win.play(FadeOut(group), run_time=0.3)

        # —— buff / sharpness: spacing from the object, corner sharpness ——
        sq2 = Square(side_length=1.4, color=BLUE).move_to([-2.0, 0.6, 0])
        br2 = Brace(sq2, direction=DOWN, buff=0.9, sharpness=6, color=ORANGE)   # the "buff / sharpness" parameters
        lbl2 = br2.get_text("buff=0.9  sharpness=6")   # the "get_text" method
        lbl2.scale(0.6).set_color(GREY_B)
        win.play(Create(sq2), GrowFromCenter(br2), FadeIn(lbl2), run_time=0.6)
        win.play(FadeOut(sq2), FadeOut(br2), FadeOut(lbl2), run_time=0.25)

        # —— stroke_width / fill_opacity / background_stroke_width / background_stroke_color ——
        ln = Line(LEFT * 2.2, RIGHT * 2.2, color=BLUE)
        br3 = Brace(ln, direction=DOWN, stroke_width=2, fill_opacity=0.5,
                    background_stroke_width=10, background_stroke_color=RED)   # the "stroke_width / fill_opacity / background_*" parameters
        lbl3 = br3.get_text("stroke 2 - fill 0.5 - bg 10 - RED")   # the "get_text" method (Tex is math mode: do not put underscores in the string)
        lbl3.scale(0.5).set_color(GREY_B)
        win.play(Create(ln), GrowFromCenter(br3), FadeIn(lbl3), run_time=0.7)
        win.play(FadeOut(ln), FadeOut(lbl3), run_time=0.25)

        # —— methods: get_tex / put_at_tip / get_tip / get_direction ——
        lbl4 = br3.get_tex(r"x^2+y^2=r^2")   # the "get_tex" method: switch to a MathTex label
        lbl4.scale(0.7).set_color(TEAL)
        win.play(FadeIn(lbl4), run_time=0.4)
        tip = br3.get_tip()   # the "get_tip()" method: get the tip coordinates
        dot = Dot(tip, color=YELLOW, radius=0.07)
        dirn = br3.get_direction()   # the "get_direction()" method: get the orientation vector
        cap = Text("tip + direction = (%d, %d)" % (round(dirn[0]), round(dirn[1])),
                   font_size=20, color=GREY_B).next_to(lbl4, DOWN, buff=0.25)
        win.play(FadeIn(dot), FadeIn(cap), run_time=0.4)
        win.play(FadeOut(lbl4), run_time=0.25)   # the tip label and the get_tex label share a position; take the old one away first
        tag = Text("put_at_tip", font_size=22, color=PURPLE)
        br3.put_at_tip(tag)   # the "put_at_tip(mob)" method: put the object at the tip
        win.play(FadeIn(tag), run_time=0.4)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: BraceText —— brace + ordinary text in one step ==========
class BraceTextDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("16-BraceText", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— default: label_constructor=Text, the brace below ——
        sq = Square(side_length=1.6, color=BLUE).move_to([-3.4, 0.9, 0])
        bt = BraceText(sq, "square", font_size=28)   # the "obj / text" parameters
        win.play(Create(sq), GrowFromCenter(bt), run_time=0.6)   # the text is automatically placed just outside the tip

        # —— label_constructor: switch the label to MathTex ——
        sq2 = Square(side_length=1.6, color=TEAL).move_to([0.6, 0.9, 0])
        bt2 = BraceText(sq2, r"a^2", label_constructor=MathTex, font_size=40)   # the "label_constructor" parameter
        win.play(Create(sq2), GrowFromCenter(bt2), run_time=0.6)

        # —— brace_direction / buff / brace_config: direction, spacing, brace style ——
        sq3 = Square(side_length=1.6, color=GOLD).move_to([-3.4, -1.6, 0])
        bt3 = BraceText(sq3, "buff & config", brace_direction=RIGHT, font_size=24,
                        buff=0.7, brace_config={"color": ORANGE})   # the "brace_direction / buff / brace_config" parameters
        win.play(Create(sq3), GrowFromCenter(bt3), run_time=0.7)

        # —— the brace above, with a larger font ——
        sq4 = Square(side_length=1.6, color=PURPLE).move_to([2.8, -2.2, 0])
        bt4 = BraceText(sq4, "font_size=32", brace_direction=UP, font_size=32)   # the "font_size" parameter
        win.play(Create(sq4), GrowFromCenter(bt4), run_time=0.7)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: BraceLabel —— default MathTex label + four methods =======
class BraceLabelDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("16-BraceLabel", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— default: label_constructor=MathTex ——
        sq = Square(side_length=2.0, color=BLUE).move_to([0, 0.6, 0])
        bl = BraceLabel(sq, r"2 \times 2")   # the "obj / text" parameters
        win.play(Create(sq), bl.creation_anim(), run_time=0.6)   # the "creation_anim" method

        # —— change_label: swap out the label text ——
        old_label = bl.label   # the entrance animation adds the old label to the scene separately: take it away too when changing the label
        bl.change_label(r"\sqrt{2}")   # the "change_label(*text)" method
        win.play(FadeOut(old_label), FadeIn(bl.label), run_time=0.5)

        # —— shift_brace: move the brace to the other side (the text follows) ——
        bl2 = BraceLabel(sq, "LEFT", brace_direction=LEFT, font_size=30,
                         brace_config={"color": TEAL})   # the "brace_direction / font_size / brace_config" parameters
        bl.shift_brace(sq)   # the "shift_brace(obj)" method: re-attach to the object
        win.play(GrowFromCenter(bl2), run_time=0.6)   # one more on the left for comparison

        # —— change_brace_label: change the object + the label ——
        sq2 = Square(side_length=1.4, color=GREEN).move_to([-4.4, -2.0, 0])
        bl2.change_brace_label(sq2, "moved")   # the "change_brace_label(obj, *text)" method
        win.play(Create(sq2), run_time=0.5)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 4: BraceBetweenPoints —— marking the distance between two points
class BraceBetweenDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("16-BraceBetweenPoints", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— direction=DOWN: below two horizontal points ——
        a, b = LEFT * 4.0 + UP * 1.4, RIGHT * 1.0 + UP * 1.4
        d1 = Dot(a, color=BLUE)
        d2 = Dot(b, color=BLUE)
        bb = BraceBetweenPoints(a, b, direction=DOWN, color=GREEN)   # the "point_1 / point_2 / direction" parameters
        lbl = bb.get_text("distance")   # the "get_text" method
        lbl.scale(0.6).set_color(GREY_B)
        win.play(FadeIn(d1), FadeIn(d2), GrowFromCenter(bb), FadeIn(lbl), run_time=0.7)

        # —— direction=UP: above the same pair of points ——
        bb2 = BraceBetweenPoints(a, b, direction=UP, color=ORANGE)   # the parameter switched to UP
        win.play(GrowFromCenter(bb2), run_time=0.5)

        # —— get_tex: use a formula as the label; the same object can just get a label ——
        lbl2 = bb2.get_tex(r"\Delta x")   # the "get_tex" method
        lbl2.scale(0.7).set_color(TEAL)
        win.play(FadeIn(lbl2), run_time=0.5)

        # —— two vertical points + a LEFT direction ——
        c, d = LEFT * 1.0 + DOWN * 2.4, LEFT * 1.0 + UP * 0.4
        bb3 = BraceBetweenPoints(c, d, direction=LEFT, color=PURPLE)
        lbl3 = bb3.get_text("dy")
        lbl3.scale(0.6).set_color(GREY_B)
        win.play(FadeIn(Dot(c, color=YELLOW)), FadeIn(Dot(d, color=YELLOW)),
                 GrowFromCenter(bb3), FadeIn(lbl3), run_time=0.7)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 5: ArcBrace —— a curved brace ===============================
class ArcBraceDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("16-ArcBrace", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— add a brace to an arc: direction=RIGHT ——
        arc = Arc(radius=1.4, start_angle=0, angle=90 * DEGREES, color=BLUE).move_to([-3.2, 0.4, 0])
        ab = ArcBrace(arc, direction=RIGHT, color=ORANGE)   # the "arc / direction" parameters
        win.play(Create(arc), GrowFromCenter(ab), run_time=0.7)

        # —— direction=LEFT: swings to the other side of the arc ——
        ab2 = ArcBrace(arc, direction=LEFT, color=TEAL)   # the parameter switched to LEFT
        win.play(GrowFromCenter(ab2), run_time=0.5)

        # —— with its own arc: a larger arc + a label ——
        arc2 = Arc(radius=1.4, start_angle=90 * DEGREES, angle=90 * DEGREES, color=GREEN).move_to([3.2, 0.4, 0])
        ab3 = ArcBrace(arc2, direction=RIGHT, color=PURPLE)
        lbl = ab3.get_text("90 deg")   # the "get_text" method
        lbl.scale(0.6).set_color(GREY_B)
        win.play(Create(arc2), GrowFromCenter(ab3), FadeIn(lbl), run_time=0.7)

        # —— arc=None: the unit circle by default ——
        ab4 = ArcBrace(direction=RIGHT, color=RED).move_to([0, -2.2, 0])   # the "arc=None" parameter
        cap = Text("arc=None (unit circle)", font_size=20, color=GREY_B).next_to(ab4, DOWN, buff=0.35)
        win.play(GrowFromCenter(ab4), FadeIn(cap), run_time=0.7)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


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

PAGE = "16-Braces"


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
