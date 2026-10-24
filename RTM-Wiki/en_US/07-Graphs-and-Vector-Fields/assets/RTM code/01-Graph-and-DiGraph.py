# -*- coding: utf-8 -*-
"""Full source for the four samples in 01-Graph-and-DiGraph.md (character-for-character identical to the code blocks in the page).

Usage: python 01-Graph-and-DiGraph.py <clip-name>...
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

import networkx as nx
from real_time_manim import (
    Scene, Graph, DiGraph, Text, VGroup,
    BLACK, YELLOW, GREY_B, RED, BLUE, BLUE_E, GREEN, ORANGE,
    UP, DOWN, Write, FadeIn, Create,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: the three layouts =========================================
class GraphLayoutDemo(Scene):
    LAYOUT = "circular"   # layout name: switch to "spring" for the force-directed spread, "partite" is shown in the variant below
    PARTITIONS = None     # columns for the "partite" layout; leave None for other layouts
    CONFIG = {}           # "layout_config": layout algorithm kwargs (e.g. spring's random seed)

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-Graph-layout", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = Text('layout="%s"' % self.LAYOUT, font_size=30, color=GREY_B)   # current layout name
        lab.next_to(title, DOWN, buff=0.35)   # place the label right below the title
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        g = Graph(
            [1, 2, 3, 4, 5, 6],                                        # vertices: any hashable value
            [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 1), (1, 4)],  # edges: (u, v) tuples
            layout=self.LAYOUT,                                        # parameter "layout"
            layout_config=self.CONFIG,                                 # parameter "layout_config"
            partitions=self.PARTITIONS,                                # parameter "partitions"
            labels=True,                                               # parameter "labels"
            label_fill_color=BLACK,                                    # parameter "label_fill_color"
        )
        win.play(Create(g), run_time=1.2)   # draw the whole graph stroke by stroke
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


class GraphLayoutSpringDemo(GraphLayoutDemo):
    LAYOUT = "spring"                      # switch to the force-directed layout
    CONFIG = {"seed": 7}                   # pin the random seed so both engines match


class GraphLayoutPartiteDemo(GraphLayoutDemo):
    LAYOUT = "partite"                          # switch to the column layout
    PARTITIONS = [[1, 2, 3], [4, 5, 6]]         # two columns of three vertices each


# ===== Sample 2: vertex_config / edge_config ===============================
class GraphConfigDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-Graph-config", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = VGroup(
            Text("vertex_config={radius:0.16, color:YELLOW, 3:{color:RED}}",
                 font_size=26, color=GREY_B),
            Text("edge_config={stroke_width:5, color:BLUE, (1,3):{...:10}}",
                 font_size=26, color=GREY_B),
        ).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.3)   # two-line parameter summary
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        g = Graph(
            [1, 2, 3, 4, 5],                                   # five vertices
            [(1, 2), (2, 3), (3, 4), (4, 5), (1, 5), (1, 3)],  # six edges
            layout="circular", layout_scale=2.4,               # circular layout, scaled up a bit
            labels=True,                                       # parameter "labels"
            label_fill_color=BLACK,                            # parameter "label_fill_color"
            vertex_config={"radius": 0.16, "color": YELLOW,    # common vertex style
                           3: {"color": RED, "radius": 0.26}}, # vertex 3 overridden individually
            edge_config={"stroke_width": 5, "color": BLUE,     # common edge style
                         (1, 3): {"stroke_width": 10,          # this edge overridden individually
                                  "color": ORANGE}},
        )
        win.play(Create(g), run_time=1.0)   # draw the whole graph stroke by stroke
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


# ===== Sample 3: DiGraph's tip_config ======================================
class DiGraphTipDemo(Scene):
    TIP = None   # tip config: None uses the default size, {...} enlarges the tip one notch

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-DiGraph-tip", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = Text(
            "tip_config=%s" % ("{tip_length:0.3, tip_width:0.26}"
                               if self.TIP else "{}"),
            font_size=28, color=GREY_B,
        ).next_to(title, DOWN, buff=0.35)   # show the current tip config
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        d = DiGraph(
            [1, 2, 3, 4],                               # vertices
            [(1, 2), (2, 3), (1, 3), (3, 4), (4, 1)],   # directed edges: u points to v
            layout="circular", layout_scale=2.2,        # circular layout
            labels=True,                                # parameter "labels"
            label_fill_color=BLACK,                     # parameter "label_fill_color"
            edge_config={"color": BLUE_E, "stroke_width": 5,   # common edge style
                         "tip_config": self.TIP or {}},        # parameter "tip_config"
        )
        win.play(Create(d), run_time=1.0)   # draw the whole graph stroke by stroke (tips are repositioned by their updater)
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


class DiGraphTipBig(DiGraphTipDemo):
    TIP = {"tip_length": 0.3, "tip_width": 0.26}   # enlarge the tip one notch


# ===== Sample 4: from_networkx =============================================
class FromNetworkxDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-Graph-from_networkx", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = Text('Graph.from_networkx(nx.wheel_graph(7), layout="spring")',
                   font_size=26, color=GREY_B).next_to(title, DOWN, buff=0.35)   # parameter summary
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        nxg = nx.wheel_graph(7)   # networkx wheel graph: center 0 plus outer ring 1..6
        g = Graph.from_networkx(
            nxg,                                                 # the existing networkx graph
            layout="spring", layout_config={"seed": 5},          # layout name and random seed
            labels=True, label_fill_color=BLACK,                # parameter "labels"
            vertex_config={"color": GREEN, "radius": 0.15},      # common vertex style
        )
        win.play(Create(g), run_time=1.2)   # draw the whole graph stroke by stroke
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window


SCENES = [
    ("graph_layout_circular", GraphLayoutDemo),
    ("graph_layout_spring", GraphLayoutSpringDemo),
    ("graph_layout_partite", GraphLayoutPartiteDemo),
    ("graph_config", GraphConfigDemo),
    ("digraph_tip_default", DiGraphTipDemo),
    ("digraph_tip_big", DiGraphTipBig),
    ("graph_from_networkx", FromNetworkxDemo),
]

PAIRS = [
    ("layout", ["graph_layout_circular", "graph_layout_spring",
                "graph_layout_partite"]),
    ("config", ["graph_config"]),
    ("digraph", ["digraph_tip_default", "digraph_tip_big"]),
    ("from_networkx", ["graph_from_networkx"]),
]

PAGE = "01-Graph-and-DiGraph"


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
