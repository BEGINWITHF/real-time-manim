# -*- coding: utf-8 -*-
"""Full source of the three samples in 01-Colors.md (identical to the code blocks in the page).

Usage: python 01-Colors.py <clip name>...
With no arguments it renders every clip and concatenates the page's three sample videos (output to the parent assets/).
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
    Scene, Square, Text, VGroup,
    ManimColor, color_gradient,
    RED, YELLOW, BLUE, WHITE, GREY_B,
    UP, DOWN, RIGHT, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: the various ManimColor value forms + to_hex =================
class ColorParseDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("01-ManimColor", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        vals = [ManimColor("#FF8800"), ManimColor((255, 0, 0)), ManimColor(0x00FF00),   #hex string / 0-255 int tuple / int
                ManimColor("RED"), ManimColor("BLUE", alpha=0.4)]   #predefined color name / color name + "alpha" param
        labs = ["'#FF8800'", "(255, 0, 0)", "0x00FF00", "'RED'", "alpha=0.4"]   #how each color is written in source
        sw = VGroup(*[Square(side_length=1.0, stroke_width=2).set_fill(c, 1) for c in vals])   #five color blocks, filled 0.9 opaque
        sw.arrange(RIGHT, buff=0.5).move_to(UP * 0.55)   #arrange left to right in a row
        src = VGroup(*[Text(s, font_size=15, color=GREY_B).next_to(m, UP, buff=0.18)
                       for s, m in zip(labs, sw)])   #above each block: how the value is written
        hx = VGroup(*[Text(c.to_hex(), font_size=16, color=WHITE).next_to(m, DOWN, buff=0.18)
                      for c, m in zip(vals, sw)])   #below each block: the to_hex() result
        hint = Text("to_hex() -> '#RRGGBB'", font_size=22, color=YELLOW).to_edge(DOWN)   #note that the bottom row comes from to_hex
        self.add(sw, src, hx, hint)   #add the blocks, both label rows and the hint to the scene
        win.play(FadeIn(sw), run_time=0.6)   #the whole row of blocks fades in
        win.play(FadeIn(src), FadeIn(hx), run_time=0.6)   #source-form and hex-result rows fade in
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window


# ===== Sample 2: darker / lighter ===========================================
class ColorDepthDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("01-darker-lighter", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        base = ManimColor("RED")   #base color: predefined name "RED"
        cols = [base.lighter(0.6), base.lighter(0.3), base,   #two steps toward white + original
                base.darker(0.3), base.darker(0.6)]   #two steps toward black
        labs = ["lighter(0.6)", "lighter(0.3)", "'RED'", "darker(0.3)", "darker(0.6)"]   #where each block comes from
        sw = VGroup(*[Square(side_length=1.1, stroke_width=2).set_fill(c, 1) for c in cols])   #five color blocks
        sw.arrange(RIGHT, buff=0.45).move_to(UP * 0.55)   #arrange left to right in a row
        src = VGroup(*[Text(s, font_size=15, color=GREY_B).next_to(m, UP, buff=0.2)
                       for s, m in zip(labs, sw)])   #label the blend call above each block
        note = Text("new object, original unchanged", font_size=20, color=YELLOW).to_edge(DOWN)   #emphasize "returns a new object"
        self.add(sw, src, note)   #add the blocks, labels and note to the scene
        win.play(FadeIn(sw), run_time=0.6)   #the whole row of blocks fades in
        win.play(FadeIn(src), FadeIn(note), run_time=0.6)   #labels and note fade in
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window


# ===== Sample 3: color_gradient multi-color ramp ============================
class ColorGradientDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("01-color_gradient", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        ramp6 = color_gradient([RED, YELLOW, BLUE], 6)   #expand three reference colors into 6
        sq6 = VGroup(*[Square(side_length=0.7, stroke_width=1).set_fill(c, 1) for c in ramp6])   #6 large color blocks
        sq6.arrange(RIGHT, buff=0.08).move_to(UP * 1.0)   #arrange into a thick ramp
        lab6 = Text("color_gradient([RED, YELLOW, BLUE], 6)", font_size=17, color=GREY_B)
        lab6.next_to(sq6, UP, buff=0.25)   #label the call above the thick ramp

        ramp14 = color_gradient([RED, YELLOW, BLUE], 14)   #same reference colors expanded into 14
        sq14 = VGroup(*[Square(side_length=0.45, stroke_width=1).set_fill(c, 1) for c in ramp14])   #14 small color blocks
        sq14.arrange(RIGHT, buff=0.05).move_to(DOWN * 0.7)   #arrange into a thin ramp
        lab14 = Text("color_gradient([RED, YELLOW, BLUE], 14)", font_size=17, color=GREY_B)
        lab14.next_to(sq14, UP, buff=0.22)   #label the call above the thin ramp
        note = Text("same reference colors, different length_of_output", font_size=19,
                    color=YELLOW).to_edge(DOWN)   #the two rows differ only in count
        self.add(sq6, lab6, sq14, lab14, note)   #add both ramps and the note to the scene
        win.play(FadeIn(sq6), FadeIn(lab6), run_time=0.6)   #thick ramp first
        win.play(FadeIn(sq14), FadeIn(lab14), FadeIn(note), run_time=0.6)   #then the thin ramp and the note
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window


SCENES = [
    ("parse", ColorParseDemo),
    ("depth", ColorDepthDemo),
    ("gradient", ColorGradientDemo),
]

PAIRS = [
    ("parse", ["parse"]),
    ("depth", ["depth"]),
    ("gradient", ["gradient"]),
]

PAGE = "01-Colors"


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
