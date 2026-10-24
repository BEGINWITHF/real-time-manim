# -*- coding: utf-8 -*-
"""Full source of the two samples in 04b-Path-and-Sequence-Utilities.md (identical to the code blocks in the page).
Usage: python 04b-Path-and-Sequence-Utilities.py <clip name>...
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

from real_time_manim import (
    Scene, Text, VGroup, Dot, Line, Circle,
    BLUE, GREEN, RED, YELLOW, GREY_B, TEAL, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI, TAU,
    adjacent_pairs, choose, clip, sigmoid, remove_list_redundancies,
    path_along_arc, Transform,
    FadeIn, Write, Create,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: the three transform trajectories of path_along_arc =========
class PathArcDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("04b-path_along_arc", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        xs0, xs1 = -1.8, 1.8   #shared start and end x of the three lanes (same chord length)
        lanes = [
            (1.1, GREEN, "path_along_arc(-TAU/2)", -TAU / 2),   #top: half turn in reverse (arc bulges upward)
            (-0.2, BLUE, "straight (default)", None),   #middle: default straight path
            (-1.4, RED, "path_along_arc(TAU/2)", TAU / 2),   #bottom: half turn forward (arc bulges downward)
        ]
        movers = []
        for y, c, nm, arc in lanes:
            track = Line([xs0, y, 0], [xs1, y, 0], color=GREY_B, stroke_width=2)
            track.set_stroke(opacity=0.3)   #chord (reference straight line, translucent)
            lab = Text(nm, font_size=16, color=c).next_to(track, UP, buff=0.15)   #lane name above the track
            s0 = Circle(radius=0.12, color=GREY_B, stroke_width=2).move_to([xs0, y, 0])   #start ring
            s1 = Circle(radius=0.12, color=GREY_B, stroke_width=2).move_to([xs1, y, 0])   #end ring
            dot = Dot([xs0, y, 0], radius=0.14, color=c)   #departing dot
            target = Dot([xs1, y, 0], radius=0.14, color=c)   #target dot at the end
            win.play(FadeIn(VGroup(track, lab, s0, s1)), run_time=0.4)   #lane positions first
            movers.append((dot, target, arc))
        win.play(FadeIn(VGroup(*[m for m, _, _ in movers])), run_time=0.3)   #the three dots take position
        win.play(*[Transform(m, t, path_func=path_along_arc(a) if a else None,
                             run_time=1.6)
                   for m, t, a in movers])   #one chord × three path_funcs starting together
        note = Text("Transform(..., path_func=path_along_arc(arc))",
                    font_size=18, color=YELLOW).to_edge(DOWN)   #bottom note
        win.play(FadeIn(note), run_time=0.35)   #note fades in
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window


# ===== Sample 2: adjacent_pairs closed edges + small math functions ========
class SequenceDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("04b-iterables_functions", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        pts = [(-3.2, -0.9, 0), (-1.5, -2.0, 0),   #four points on the left (an irregular quadrilateral)
               (-0.9, 0.5, 0), (-2.9, 1.4, 0)]
        head = Text("adjacent_pairs: 4 pts -> 4 edges", font_size=15, color=GREY_B)
        head.move_to([-2.1, 2.1, 0])   #left figure title
        dots = VGroup(*[Dot(p, radius=0.09, color=RED) for p in pts])   #four vertices
        win.play(FadeIn(head), FadeIn(dots), run_time=0.5)   #title and vertices position first
        edges = [Line(a, b, color=BLUE, stroke_width=4)   #adjacent pairs: (1,2)(2,3)(3,4)(4,1)
                 for a, b in adjacent_pairs(pts)]   #the last pair (4,1) is added automatically, closing the quadrilateral
        for e in edges:
            win.play(Create(e), run_time=0.35)   #draw the four edges one by one (the fourth returns to the start)

        vals = VGroup(
            Text("choose(5, 2) = %d" % choose(5, 2), font_size=18, color=WHITE),
            Text("clip(3.7, 0, 1) = %.1f" % clip(3.7, 0, 1), font_size=18, color=GREEN),
            Text("sigmoid(0) = %.3f" % sigmoid(0), font_size=18, color=TEAL),
        ).arrange(DOWN, buff=0.28, aligned_edge=LEFT)   #three value lines on the right
        vals.move_to([1.9, 0.3, 0])
        win.play(FadeIn(vals), run_time=0.6)   #the three value lines fade in
        note = Text("remove_list_redundancies: [1,2,1,3,2] -> [1,3,2]",
                    font_size=17, color=YELLOW).to_edge(DOWN)   #dedup keeping the last occurrence
        win.play(FadeIn(note), run_time=0.35)   #bottom note fades in
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window


SCENES = [
    ("paths", PathArcDemo),
    ("iterables", SequenceDemo),
]

PAIRS = [
    ("paths", ["paths"]),
    ("iterables", ["iterables"]),
]

PAGE = "04b-Path-and-Sequence-Utilities"


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
