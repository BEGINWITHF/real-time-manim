# -*- coding: utf-8 -*-
"""Full source of the two samples in 03-Directions-and-Constants.md (identical to the code blocks in the page).
Usage: python 03-Directions-and-Constants.py <clip name>...
With no arguments it renders every clip and concatenates the page's two sample videos (output to the parent assets/).
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
    Scene, Text, VGroup, Dot, Arrow, Circle, Arc,
    BLUE, GREEN, RED, ORANGE, PURPLE, YELLOW, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, UL, UR, DL, DR,
    PI, TAU, DEGREES, compass_directions,
    FadeIn, Write, Create,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: compass of direction constants =============================
class DirectionDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("03-direction constants", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        origin = Dot(ORIGIN, radius=0.07, color=WHITE)   #origin ORIGIN
        win.play(FadeIn(origin), run_time=0.3)   #show the origin first
        lab0 = Text("ORIGIN", font_size=16, color=WHITE).next_to(origin, DOWN, buff=0.2)
        win.play(FadeIn(lab0), run_time=0.25)   #origin label

        mains = [("RIGHT", RIGHT, BLUE), ("UP", UP, GREEN),   #four cardinal directions
                 ("LEFT", LEFT, RED), ("DOWN", DOWN, ORANGE)]
        for nm, d, c in mains:   #draw arrows right → up → left → down in turn
            ar = Arrow(ORIGIN, 2.0 * d, buff=0, color=c, stroke_width=6)   #direction arrow of length one unit
            lb = Text(nm, font_size=20, color=c).next_to(ar.get_end(), d, buff=0.2)   #write the constant name outside the arrow
            win.play(Create(ar), run_time=0.45)   #draw the arrow
            win.play(FadeIn(lb), run_time=0.2)   #then add its name

        diags = [("UR", UR), ("UL", UL), ("DL", DL), ("DR", DR)]   #four diagonal directions
        dgrp = VGroup()
        for nm, d in diags:   #diagonal = sum of two cardinal directions, all at once
            ar = Arrow(ORIGIN, 1.7 * d, buff=0, color=PURPLE, stroke_width=5)
            lb = Text(nm, font_size=18, color=PURPLE).next_to(ar.get_end(), d, buff=0.18)
            dgrp.add(ar, lb)
        win.play(FadeIn(dgrp), run_time=0.5)   #the whole group of diagonal arrows fades in
        note = Text("UR = UP + RIGHT   |   IN / OUT = Z axis", font_size=18,
                    color=GREY_B).to_edge(DOWN)   #note on how diagonals are built and the Z axis
        win.play(FadeIn(note), run_time=0.35)   #note fades in
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window


# ===== Sample 2: compass_directions and math constants ======================
class CompassMathDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("03-compass_directions", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        # —— left half: compass_directions rotates start_vect n times ——
        c = [-3.6, -0.4, 0]   #center of the left figure
        ring = Circle(radius=1.6, color=GREY_B, stroke_width=3).move_to(c)   #helper circle
        pts = compass_directions(8, start_vect=RIGHT)   #start from the right and rotate TAU/8 each time for 8 directions
        dots = VGroup(*[Dot(1.6 * p + c, radius=0.07,
                            color=BLUE if i == 0 else YELLOW) for i, p in enumerate(pts)])   #index 0 is start_vect
        lab_l = Text("compass_directions(8, start_vect=RIGHT)", font_size=15, color=GREY_B)
        lab_l.move_to([-3.6, 1.7, 0])   #left figure title
        lab_r = Text("dot[0] = start_vect", font_size=15, color=BLUE)
        lab_r.next_to(ring, DOWN, buff=0.35)   #the blue dot is the starting direction
        win.play(Create(ring), FadeIn(lab_l), run_time=0.5)   #helper circle and title
        win.play(FadeIn(dots), FadeIn(lab_r), run_time=0.5)   #8 evenly spaced direction dots
        # —— right half: the three math constants TAU / PI / DEGREES ——
        cc = [3.0, 0.2, 0]   #center of the right figure
        full = Arc(radius=1.5, start_angle=0, angle=TAU, arc_center=cc,
                   color=BLUE, stroke_width=4)   #one full turn = TAU
        half = Arc(radius=1.5, start_angle=0, angle=PI, arc_center=cc,
                   color=GREEN, stroke_width=7)   #half turn = PI
        wedge = Arc(radius=1.5, start_angle=0, angle=45 * DEGREES, arc_center=cc,
                    color=RED, stroke_width=12)   #45° = 45 * DEGREES
        vals = VGroup(
            Text("TAU = 6.28319", font_size=17, color=BLUE),
            Text("PI = 3.14159", font_size=17, color=GREEN),
            Text("45 * DEGREES = 0.78540", font_size=17, color=RED),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)   #three value lines, same colors as the three arcs
        vals.move_to([3.0, -2.4, 0])   #placed below the right figure
        win.play(Create(full), run_time=0.7)   #draw the full turn first
        win.play(Create(half), run_time=0.45)   #then overlay the half turn
        win.play(Create(wedge), run_time=0.3)   #finally the 45° arc
        win.play(FadeIn(vals), run_time=0.45)   #the three value lines fade in
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window


SCENES = [
    ("directions", DirectionDemo),
    ("compass_math", CompassMathDemo),
]

PAIRS = [
    ("directions", ["directions"]),
    ("compass_math", ["compass_math"]),
]

PAGE = "03-Directions-and-Constants"


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
