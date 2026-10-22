# -*- coding: utf-8 -*-
"""Full source for the four samples in 08-Text.md (identical to the code blocks in the page).

Usage: python 08-Text.py <sample names>...
With no arguments it renders every sample and concatenates the page's four sample videos (written to assets/RTM output/).
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
    Scene, Text, MarkupText, Paragraph, register_font,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


def cap(text, mob, buff=0.35, color=GREY_B, size=18):
    return Text(text, font_size=size, color=color).next_to(mob, DOWN, buff=buff)


# ===== Sample 1: Text —— plain text (font / size / weight / slant / spacing / colours) ==
class TextDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("08-Text", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— default: a single line of text ——
        t1 = Text("Hello RTM").move_to([0, 1.6, 0])   # the "text" parameter
        win.play(Write(t1), FadeIn(cap('Text("Hello RTM")', t1)), run_time=0.6)

        # —— font / font_size / weight / slant ——
        t2 = Text("Arial 40 bold italic", font="Arial", font_size=40,
                  weight="BOLD", slant="ITALIC").move_to([0, 0.5, 0])   # the "font / font_size / weight / slant" parameters
        win.play(Write(t2), FadeIn(cap('font="Arial" weight=BOLD slant=ITALIC', t2)), run_time=0.7)

        # —— color / line_spacing: overall colour and line spacing of two lines ——
        t3 = Text("first line\nsecond line", font_size=34, color=TEAL,
                  line_spacing=1.2).move_to([0, -1.0, 0])   # the "color / line_spacing" parameters
        win.play(Write(t3), FadeIn(cap("color=TEAL, line_spacing=1.2", t3)), run_time=0.7)

        # —— t2c: colour a given substring on its own ——
        t4 = Text("red green blue", font_size=34,
                  t2c={"red": RED, "green": GREEN, "blue": BLUE}).move_to([0, -2.3, 0])   # the "t2c" parameter
        win.play(Write(t4), FadeIn(cap('t2c={"red": RED, …}', t4)), run_time=0.7)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: MarkupText —— Pango markup text ==========================
class MarkupDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("08-MarkupText", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— markup syntax: <b> / <i> / <span foreground=…> ——
        m1 = MarkupText('<b>bold</b> and <i>italic</i>',
                        font_size=36).move_to([0, 1.3, 0])   # the "text" parameter (Pango markup)
        win.play(Write(m1), FadeIn(cap('MarkupText("<b>…</b> <i>…</i>")', m1)), run_time=0.8)

        # —— color / font_size: the overall colour and font size (colours in the markup win) ——
        m2 = MarkupText('colored markup text',
                        font_size=32, color=TEAL).move_to([0, 0.0, 0])   # the "color / font_size" parameters
        win.play(Write(m2), FadeIn(cap("color=TEAL", m2)), run_time=0.8)

        # —— line_spacing / justify: multiple lines and alignment ——
        m3 = MarkupText("line one\nline two is longer", font_size=30,
                        line_spacing=1.4).move_to([0, -1.5, 0])   # the "line_spacing" parameter
        win.play(Write(m3), FadeIn(cap("line_spacing=1.4", m3)), run_time=0.8)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: Paragraph —— multiple text blocks, aligned line by line ===
class ParagraphDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("08-Paragraph", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— each positional argument is one block; alignment controls the whole block ——
        p1 = Paragraph("first paragraph", "second paragraph", "third",
                       alignment="left", font_size=32).move_to([-0.6, 0.9, 0])   # the "*text / alignment" parameters
        win.play(Write(p1), FadeIn(cap('alignment="left"', p1)), run_time=0.8)

        # —— line_spacing: spacing between blocks ——
        p2 = Paragraph("tight", "spacing", line_spacing=0.6,
                       alignment="center", font_size=32).move_to([-0.6, -1.4, 0])   # the "line_spacing" parameter
        win.play(Write(p2), FadeIn(cap("line_spacing=0.6", p2)), run_time=0.8)

        # —— **kwargs passed through: colour / font ——
        p3 = Paragraph("colored", "paragraph", font_size=32, color=ORANGE,
                       font="Arial").move_to([2.6, -1.4, 0])   # the "**kwargs (color / font)" parameters
        win.play(Write(p3), FadeIn(cap("color=ORANGE, font=Arial", p3)), run_time=0.8)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 4: register_font —— temporarily register a font file ========
class RegisterFontDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("08-register_font", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— usage: register a font file inside a with block; a Text built in the block can use that family name ——
        font_file = r"C:\Windows\Fonts\arial.ttf"   # the "font_file" parameter: path to the font file
        with register_font(font_file):   # the "font_file" parameter
            t1 = Text("Registered: Arial", font="Arial", font_size=44).move_to([0, 0.9, 0])
            win.play(Write(t1), FadeIn(cap("with register_font(arial.ttf): Text(..., font=\"Arial\")", t1)), run_time=0.8)

        # —— same family name outside the block: already in the font cache, so it still lays out ——
        t2 = Text("outside the with-block", font="Arial", font_size=36,
                  color=TEAL).move_to([0, -0.8, 0])
        win.play(Write(t2), FadeIn(cap("same family name outside the block", t2)), run_time=0.8)

        # —— control case without registering: a family name the system lacks warns and falls back ——
        t3 = Text("fallback family", font_size=36, color=GREY_B).move_to([0, -2.2, 0])
        win.play(Write(t3), FadeIn(cap("an unregistered family falls back to the default font", t3)), run_time=0.8)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


SCENES = [
    ("text", TextDemo),
    ("markup", MarkupDemo),
    ("paragraph", ParagraphDemo),
    ("registerfont", RegisterFontDemo),
]

PAIRS = [
    ("text", ["text"]),
    ("markup", ["markup"]),
    ("paragraph", ["paragraph"]),
    ("registerfont", ["registerfont"]),
]

PAGE = "08-Text"


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
