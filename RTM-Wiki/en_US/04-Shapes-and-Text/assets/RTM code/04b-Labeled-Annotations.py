# -*- coding: utf-8 -*-
"""Full source for the four samples in 04b-Labeled-Annotations.md (identical to the code blocks in the page).

Usage: python 04b-Labeled-Annotations.py <sample names>...
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
    Scene, Label, LabeledLine, LabeledArrow, LabeledPolygram,
    Line, Arrow, Polygon, Triangle, Square, Text,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: Label —— text + background box + frame ====================
class LabelDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("04b-Label", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— default: white text + the default background box ——
        l1 = Label("x")   # the "label" parameter: a string is rendered with MathTex
        l1.move_to([-4.2, 1.2, 0])
        cap1 = Text('Label("x")', font_size=18, color=GREY_B).next_to(l1, DOWN, buff=0.3)
        win.play(FadeIn(l1), FadeIn(cap1), run_time=0.5)

        # —— label_config: only effective for string labels (colour / font size) ——
        l2 = Label("y", label_config={"color": RED, "font_size": 72})   # the "label_config" parameter
        l2.move_to([-0.6, 1.2, 0])
        cap2 = Text('label_config={"color": RED, "font_size": 72}', font_size=18, color=GREY_B).next_to(l2, DOWN, buff=0.3)
        win.play(FadeIn(l2), FadeIn(cap2), run_time=0.5)

        # —— box_config: colour and opacity of the background box ——
        l3 = Label("z", box_config={"color": TEAL, "fill_opacity": 0.8})   # the "box_config" parameter
        l3.move_to([3.0, 1.2, 0])
        cap3 = Text('box_config={"color": TEAL, "fill_opacity": 0.8}', font_size=18, color=GREY_B).next_to(l3, DOWN, buff=0.3)
        win.play(FadeIn(l3), FadeIn(cap3), run_time=0.5)

        # —— frame_config: colour and stroke width of the frame ——
        l4 = Label("w", frame_config={"color": ORANGE, "stroke_width": 6})   # the "frame_config" parameter
        l4.move_to([-4.2, -1.0, 0])
        cap4 = Text('frame_config={"color": ORANGE, "stroke_width": 6}', font_size=18, color=GREY_B).next_to(l4, DOWN, buff=0.3)
        win.play(FadeIn(l4), FadeIn(cap4), run_time=0.5)

        # —— when label is not a string, *_config is not read: use a ready-made mobject as the label ——
        l5 = Label(Text("hi", color=YELLOW, font_size=40),
                   label_config={"color": RED})   # the "label" parameter given a Mobject: config is ignored
        l5.move_to([-0.6, -1.0, 0])
        cap5 = Text("Label(Text(...))  config ignored", font_size=18, color=GREY_B).next_to(l5, DOWN, buff=0.3)
        win.play(FadeIn(l5), FadeIn(cap5), run_time=0.5)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: LabeledLine —— a label on a line ===========================
class LabeledLineDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("04b-LabeledLine", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— label_position: ratio of the label's position along the line (0 start to 1 end) ——
        for i, pos in enumerate([0.2, 0.5, 0.8]):   # the "label_position" parameter
            ln = LabeledLine("3cm", start=[-4.4, 1.5 - i * 1.5, 0], end=[-0.4, 1.5 - i * 1.5, 0],
                             label_position=pos)   # the "start / end must be keywords" parameters
            cap = Text("label_position=%.1f" % pos, font_size=18, color=GREY_B).next_to(ln, RIGHT, buff=0.4)
            win.play(Create(ln), FadeIn(cap), run_time=0.5)   # the label slides along the line

        # —— the label_config / box_config / frame_config trio ——
        ln2 = LabeledLine("L", start=[1.6, 0.4, 0], end=[5.4, 0.4, 0],
                          label_config={"color": RED, "font_size": 64},
                          box_config={"color": TEAL, "fill_opacity": 0.8},
                          frame_config={"color": ORANGE, "stroke_width": 5})
        cap2 = Text("label/box/frame_config", font_size=18, color=GREY_B).next_to(ln2, DOWN, buff=0.4)
        win.play(Create(ln2), FadeIn(cap2), run_time=0.6)

        # —— the same line can also take a ready-made mobject as the label ——
        ln3 = LabeledLine(Text("Tetra", color=YELLOW, font_size=32),
                          start=[1.6, -1.4, 0], end=[5.4, -1.4, 0], label_position=0.35)
        cap3 = Text("label=Text(...)  label_position=0.35", font_size=18, color=GREY_B).next_to(ln3, DOWN, buff=0.4)
        win.play(Create(ln3), FadeIn(cap3), run_time=0.6)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: LabeledArrow —— the arrow version ==========================
class LabeledArrowDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("04b-LabeledArrow", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— the same set of parameters as LabeledLine, only the shape is an arrow ——
        for i, pos in enumerate([0.2, 0.6]):   # the "label_position" parameter
            arr = LabeledArrow("5m", start=[-4.4, 1.2 - i * 1.9, 0], end=[0.4, 1.2 - i * 1.9, 0],
                               label_position=pos, color=GOLD)   # colour and the like keep forwarding to Arrow
            cap = Text("label_position=%.1f" % pos, font_size=18, color=GREY_B).next_to(arr, DOWN, buff=0.35)
            win.play(Create(arr), FadeIn(cap), run_time=0.6)

        # —— the config trio works here too ——
        arr2 = LabeledArrow("A", start=[2.0, 0.2, 0], end=[5.6, 0.2, 0],
                            label_config={"color": RED, "font_size": 60},
                            box_config={"color": PURPLE, "fill_opacity": 0.8},
                            frame_config={"color": YELLOW, "stroke_width": 5})
        cap2 = Text("label/box/frame_config", font_size=18, color=GREY_B).next_to(arr2, DOWN, buff=0.4)
        win.play(Create(arr2), FadeIn(cap2), run_time=0.6)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 4: LabeledPolygram —— it finds the position inside the polygon ===
class LabeledPolygramDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("04b-LabeledPolygram", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— one vertex group (one closed ring): the label lands automatically at the "roomiest" spot inside the polygon ——
        ring = [[-5.4, -0.4, 0], [-3.4, -0.4, 0], [-4.4, 1.6, 0]]   # the "*vertex_groups" parameter: each group is one ring of vertices
        tri = LabeledPolygram(ring, label="A", color=TEAL)   # the "label" parameter
        win.play(Create(tri), FadeIn(Text("one ring, label=\"A\"", font_size=18, color=GREY_B).next_to(tri, DOWN, buff=0.35)),
                 run_time=0.6)

        # —— precision: the search precision of the PolyLabel algorithm, which must match the figure's scale ——
        square = [[-1.8, -0.6, 0], [1.4, -0.6, 0], [1.4, 1.6, 0], [-1.8, 1.6, 0]]
        big = LabeledPolygram(square, label="B", precision=0.5, color=GREEN)   # the "precision=0.5" parameter
        win.play(Create(big), FadeIn(Text("precision=0.5", font_size=18, color=GREY_B).next_to(big, DOWN, buff=0.35)),
                 run_time=0.6)

        # —— several vertex groups: each ring closes on its own and the label lands in the largest one ——
        two = LabeledPolygram([[3.2, 0.2, 0], [5.6, 0.2, 0], [4.4, 1.8, 0]],   # first ring: the large triangle
                              [[6.0, 0.2, 0], [6.8, 0.2, 0], [6.4, 0.8, 0]],   # second ring: the small triangle
                              label="2x", color=ORANGE)   # the "*vertex_groups" parameter: two rings
        win.play(Create(two), FadeIn(Text("two rings, label=\"2x\"", font_size=18, color=GREY_B).next_to(two, DOWN, buff=0.35)),
                 run_time=0.6)

        # —— the label config trio: label_config / box_config / frame_config ——
        poly = LabeledPolygram([[-5.4, -2.6, 0], [-3.4, -2.6, 0], [-4.4, -1.0, 0]],
                               label="C",
                               label_config={"color": RED, "font_size": 60},
                               box_config={"color": TEAL, "fill_opacity": 0.8},
                               frame_config={"color": ORANGE, "stroke_width": 5})
        win.play(Create(poly), FadeIn(Text("label/box/frame_config", font_size=18, color=GREY_B).next_to(poly, DOWN, buff=0.35)),
                 run_time=0.6)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


SCENES = [
    ("label", LabelDemo),
    ("labeledline", LabeledLineDemo),
    ("labeledarrow", LabeledArrowDemo),
    ("labeledpoly", LabeledPolygramDemo),
]

PAIRS = [
    ("label", ["label"]),
    ("labeledline", ["labeledline"]),
    ("labeledarrow", ["labeledarrow"]),
    ("labeledpoly", ["labeledpoly"]),
]

PAGE = "04b-Labeled-Annotations"


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
