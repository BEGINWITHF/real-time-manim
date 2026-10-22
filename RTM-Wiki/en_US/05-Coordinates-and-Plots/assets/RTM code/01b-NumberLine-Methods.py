# -*- coding: utf-8 -*-
"""Full source for the three samples in 01b-NumberLine-Methods.md (identical to the code blocks in the page).

Usage: python 01b-NumberLine-Methods.py <scene names>...
With no arguments it renders every scene and concatenates the page's three videos.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
ASSETS = os.path.dirname(HERE)
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    Scene, NumberLine, Dot, Text, VGroup,
    YELLOW, RED, BLUE, GREEN, GREY_B, UP, DOWN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: n2p / p2n two-way conversion =============================
class N2PP2NDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01b-n2p-p2n", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        line = NumberLine(x_range=[-2.5, 3, 0.5], length=10)   # half-unit-step number line
        line.add_numbers(x_values=[-2, 0, 2])   # only label -2/0/2
        lab = Text("n2p/p2n  value <-> point", font_size=28,
                   color=GREY_B).next_to(line, DOWN, buff=0.6)   # method description label
        win.play(Create(line), run_time=0.8)   # draw the number line
        win.play(FadeIn(lab), run_time=0.3)   # the label fades in

        red = Dot(line.n2p(1.5), color=RED)   # "n2p": value 1.5 -> scene point
        readout = Text("p2n=0.00", font_size=28, color=GREEN).next_to(lab, DOWN, buff=0.35)
        win.play(FadeIn(red), FadeIn(readout), run_time=0.4)   # the red dot and the readout label fade in
        win.play(red.animate.move_to(line.n2p(-1.5)), run_time=1.0)   # move the red dot to the value -1.5
        point = red.get_center()   # take the red dot's current scene coordinate
        readout.become(Text("p2n=%.2f" % line.p2n(point),   # "p2n": scene point -> value, read back as text
                            font_size=28, color=GREEN).next_to(lab, DOWN, buff=0.35))
        win.play(Wait(0.6))   # pause 0.6s to see the read-back result

        yel = Dot(line @ 3, color=YELLOW)   # the "@" form: equivalent to n2p(3)
        tag = Text("line @ 3", font_size=28, color=YELLOW).next_to(yel, UP, buff=0.3)
        win.play(FadeIn(yel), FadeIn(tag), run_time=0.4)   # the yellow dot and label fade in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


# ===== Sample 2: add_numbers / add_labels =================================
class AddNumbersLabelsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01b-add_numbers-labels", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        line = NumberLine(x_range=[-2.5, 3, 0.5], length=10)   # half-unit-step number line
        line.add_numbers(x_values=[-2, 0, 2], num_decimal_places=1)   # "add_numbers": label only the given values, keeping one decimal place
        line.add_labels({0: "start", 3: "end"}, direction=UP, font_size=28)   # "add_labels": replace values with arbitrary text labels
        lab = Text("add_numbers([-2,0,2]) + add_labels({0:start,3:end})",
                   font_size=24, color=GREY_B).next_to(line, DOWN, buff=0.6)   # method description label
        win.play(Create(line), run_time=0.8)   # draw the number line
        win.play(FadeIn(lab), run_time=0.4)   # the label fades in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


# ===== Sample 3: tick methods and rotate-about-a-value ====================
class TicksRotateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01b-ticks-rotate", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        line = NumberLine(x_range=[-2, 2, 1], length=6, include_ticks=False)   # don't draw ticks to begin with
        line.add_ticks()   # "add_ticks": fill in the ticks afterwards from x_range
        line.get_tick_marks().set_color(YELLOW)   # "get_tick_marks": grab all ticks and recolor them at once
        lab1 = Text("add_ticks() + get_tick_marks().set_color(YELLOW)",
                    font_size=24, color=GREY_B).next_to(line, DOWN, buff=0.6)   # method description label
        lab2 = Text("unit_size=%.2f" % line.get_unit_size(),   # "get_unit_size": the on-screen length of 1 value unit
                    font_size=26, color=GREEN).next_to(lab1, DOWN, buff=0.3)
        win.play(Create(line), run_time=0.8)   # draw the number line (including the added yellow ticks)
        win.play(FadeIn(VGroup(lab1, lab2)), run_time=0.4)   # the two label lines fade in
        win.play(Wait(0.4))   # pause to look at the tick color
        win.play(line.animate(run_time=1.0).rotate(0.5, about_point=line.n2p(0)))   # rotate the whole axis about the point for the value 0
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


SCENES = [
    ("01b-NumberLine-Methods-n2p_p2n", N2PP2NDemo),
    ("01b-NumberLine-Methods-addnumbers", AddNumbersLabelsDemo),
    ("01b-NumberLine-Methods-ticks", TicksRotateDemo),
]

PAIRS = [
    ("01b-NumberLine-Methods-n2p_p2n", ["01b-NumberLine-Methods-n2p_p2n"]),
    ("01b-NumberLine-Methods-addnumbers", ["01b-NumberLine-Methods-addnumbers"]),
    ("01b-NumberLine-Methods-ticks", ["01b-NumberLine-Methods-ticks"]),
]


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
            dst = os.path.join(ASSETS, "RTM output", out_name + ".mp4")
            concat(names, dst)
            print("concat ->", dst, os.path.getsize(dst), "bytes")
