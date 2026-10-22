# -*- coding: utf-8 -*-
"""Full source for the four samples in 01b-Graph-Editing-and-Layout.md (character-for-character identical to the code blocks in the page).

Usage: python 01b-Graph-Editing-and-Layout.py <clip-name>...
With no arguments it renders every clip and concatenates the four sample videos shown in the page (written to the parent assets/).
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
    Scene, Graph, Text, VGroup,
    BLACK, YELLOW, GREY_B, ORANGE, UP, DOWN, LEFT,
    Write, FadeIn, Create,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: g[k] index access to vertices/edges =======================
class GetItemDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01b-Graph-getitem", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = Text("g[2].animate.shift(...)   g[(1,2)].animate.set_stroke(...)",
                   font_size=26, color=GREY_B).next_to(title, DOWN, buff=0.3)   # signature label
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        g = Graph(
            [1, 2, 3, 4], [(1, 2), (2, 3), (3, 4), (4, 1)],   # four vertices on a ring
            layout="circular", layout_scale=2.2,             # circular layout
            labels=True, label_fill_color=BLACK,             # numeric vertex labels
        )
        win.play(Create(g), run_time=0.8)   # draw the whole graph stroke by stroke
        win.play(g[2].animate.shift(UP + LEFT), run_time=0.8)   # parameter "k": move vertex 2; its edges follow automatically
        win.play(g[(1, 2)].animate.set_stroke(ORANGE, width=8), run_time=0.5)   # parameter "k": thicken and recolor the (1,2) edge
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


# ===== Sample 2: add_vertices / add_edges ==================================
class GraphAddDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # the graph's dynamic methods replay animations internally: wire "self.play" to win.play first
        title = Text("01b-Graph-add", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = Text("g.animate.add_edges((1,4), positions=..., labels=True)",
                   font_size=26, color=GREY_B).next_to(title, DOWN, buff=0.3)   # signature label
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        g = Graph(
            [1, 2, 3], [(1, 2), (2, 3)],   # start with three vertices and two edges
            layout="circular", layout_scale=2.0,   # circular layout
            labels=True, label_fill_color=BLACK,   # numeric vertex labels
        )
        win.play(Create(g), run_time=0.6)   # draw the initial graph stroke by stroke
        win.play(g.animate.add_edges((1, 4), positions={4: [3.2, 1.2, 0]},   # parameters "*edges" / "positions"
                                     labels=True), run_time=0.8)   # the new edge grows out together with the new vertex 4
        win.play(g.animate.add_vertices(5, positions={5: [3.2, -1.4, 0]},   # parameter "*vertices"
                                         labels=True), run_time=0.6)   # add a single isolated vertex 5 only
        win.play(g.animate.add_edges((4, 5)), run_time=0.5)   # then connect the two new vertices 4 and 5
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


# ===== Sample 3: remove_vertices / remove_edges ============================
class GraphRemoveDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # the graph's dynamic methods replay animations internally: wire "self.play" to win.play first
        title = Text("01b-Graph-remove", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = Text("g.animate.remove_edges((1,3))  then  g.animate.remove_vertices(4)",
                   font_size=24, color=GREY_B).next_to(title, DOWN, buff=0.3)   # signature label
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        g = Graph(
            [1, 2, 3, 4], [(1, 2), (2, 3), (3, 4), (4, 1), (1, 3)],   # four vertices on a ring plus one chord
            layout="circular", layout_scale=2.2,   # circular layout
            labels=True, label_fill_color=BLACK,   # numeric vertex labels
        )
        win.play(Create(g), run_time=0.8)   # draw the whole graph stroke by stroke
        win.play(g.animate.remove_edges((1, 3)), run_time=0.5)   # parameter "*edges": remove edges only, keep the vertices
        win.play(g.animate.remove_vertices(4), run_time=0.5)   # parameter "*vertices": remove the vertex and its incident edges
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


# ===== Sample 4: change_layout =============================================
class GraphChangeLayoutDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # the graph's dynamic methods replay animations internally: wire "self.play" to win.play first
        title = Text("01b-Graph-change_layout", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = VGroup(
            Text('g.animate.change_layout("spring", layout_config={"seed":7})',
                 font_size=26, color=GREY_B),
            Text("g.animate.change_layout({1:[-3.2,0,0], ...})  # manual",
                 font_size=26, color=GREY_B),
        ).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.3)   # two-line signature label
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        g = Graph(
            [1, 2, 3, 4, 5], [(1, 2), (2, 3), (3, 4), (4, 5), (5, 1)],   # five vertices on a ring
            layout="circular", layout_scale=2.2,   # initial circular layout
            labels=True, label_fill_color=BLACK,   # numeric vertex labels
        )
        win.play(Create(g), run_time=0.6)   # draw the whole graph stroke by stroke
        win.play(g.animate.change_layout("spring", layout_config={"seed": 7}),   # parameter "layout"
                 run_time=1.0)   # every vertex moves to the new layout, edges follow
        win.play(g.animate.change_layout(
            {1: [-3.2, 0, 0], 2: [-1.6, 0, 0], 3: [0, 0, 0],   # a hand-written coordinate dict is a valid layout too
             4: [1.6, 0, 0], 5: [3.2, 0, 0]}), run_time=1.0)   # this time line up the five vertices horizontally
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


SCENES = [
    ("getitem", GetItemDemo),
    ("add", GraphAddDemo),
    ("remove", GraphRemoveDemo),
    ("change_layout", GraphChangeLayoutDemo),
]

PAIRS = [
    ("getitem", ["getitem"]),
    ("add", ["add"]),
    ("remove", ["remove"]),
    ("change_layout", ["change_layout"]),
]

PAGE = "01b-Graph-Editing-and-Layout"


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
