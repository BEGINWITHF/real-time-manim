# -*- coding: utf-8 -*-
"""Full source for the three samples in 14b-Table-Methods.md (identical to the code blocks in the page).

Usage: python 14b-Table-Methods.py <sample names>...
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

from real_time_manim import (
    Scene, Table, Text, Rectangle, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


def cap(text, mob, buff=0.4, color=GREY_B, size=18):
    return Text(text, font_size=size, color=color).next_to(mob, DOWN, buff=buff)


# ===== Sample 1: add_highlighted_cell —— adding a highlight block to a cell =
class HighlightDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("14b-add_highlighted_cell", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        t = Table([["a", "b"], ["c", "d"]], include_outer_lines=True,
                  element_to_mobject=Text, element_to_mobject_config={"font_size": 34})
        t.scale(0.9).move_to([0, 0.6, 0])
        win.play(Write(t), FadeIn(cap("Table([[a,b],[c,d]])", t)), run_time=0.7)

        # —— pos locates with (row, column) (1-based), color is the highlight block's colour ——
        t.add_highlighted_cell((1, 2), color=YELLOW)   # the "pos / color" parameters
        win.play(Write(t), run_time=0.5)
        c1 = Text("add_highlighted_cell((1, 2), YELLOW)",
                  font_size=18, color=GREY_B).move_to([0, -1.5, 0])
        win.play(FadeIn(c1), run_time=0.4)

        # —— **kwargs is passed on to the background block (e.g. fill_opacity) ——
        t.add_highlighted_cell((2, 1), color=BLUE, fill_opacity=0.4)   # the "**kwargs" parameter
        win.play(Write(t), run_time=0.5)
        newc = Text("add_highlighted_cell((2, 1), BLUE, fill_opacity=0.4)",
                    font_size=18, color=GREY_B).move_to([0, -2.1, 0])
        win.play(FadeIn(newc), run_time=0.4)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: get_cell / get_highlighted_cell —— taking a cell out =====
class GetCellDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("14b-get_cell / get_highlighted_cell", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        t = Table([["1", "2"], ["3", "4"]], include_outer_lines=True,
                  element_to_mobject=Text, element_to_mobject_config={"font_size": 34})
        t.scale(0.9).move_to([0, 0.6, 0])
        win.play(Write(t), FadeIn(cap("Table([[1,2],[3,4]])", t)), run_time=0.7)

        # —— get_cell: get the cell polygon and change its style on its own ——
        cell = t.get_cell((1, 2))   # the "pos" parameter
        win.play(cell.animate.set_fill(RED, 0.45), run_time=0.6)
        c1 = Text("get_cell((1, 2)) -> Polygon",
                  font_size=18, color=GREY_B).move_to([0, -1.5, 0])
        win.play(FadeIn(c1), run_time=0.4)

        # —— get_highlighted_cell: get the "already highlighted" background block directly ——
        hl = t.get_highlighted_cell((2, 2), color=TEAL)   # the "pos / color" parameters
        win.play(FadeIn(hl), run_time=0.5)
        newc = Text("get_highlighted_cell((2, 2), TEAL)",
                    font_size=18, color=GREY_B).move_to([0, -2.1, 0])
        win.play(FadeIn(newc), run_time=0.4)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: create —— the table's arranged entrance animation ========
class CreateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("14b-Table.create", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— default create(): lines Create, labels Write, elements Create, entries FadeIn ——
        t1 = Table([["a", "b"], ["c", "d"]], include_outer_lines=True,
                   element_to_mobject=Text, element_to_mobject_config={"font_size": 32})
        t1.scale(0.8).move_to([0, 0.8, 0])
        win.play(t1.create(), FadeIn(cap("create() (default animation)", t1)), run_time=1.2)

        # —— lag_ratio / line_animation / label_animation can be replaced ——
        t2 = Table([["1", "2"], ["3", "4"]], include_outer_lines=True,
                   element_to_mobject=Text, element_to_mobject_config={"font_size": 32})
        t2.scale(0.8).move_to([0, -1.8, 0])
        win.play(FadeOut(t1),
                 t2.create(lag_ratio=0.15, line_animation=Write),   # the "lag_ratio / line_animation" parameters
                 FadeIn(cap("create(lag_ratio=0.15, line_animation=Write)", t2)), run_time=1.2)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


SCENES = [
    ("highlight", HighlightDemo),
    ("getcell", GetCellDemo),
    ("create", CreateDemo),
]

PAIRS = [
    ("highlight", ["highlight"]),
    ("getcell", ["getcell"]),
    ("create", ["create"]),
]

PAGE = "14b-Table-Methods"


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
