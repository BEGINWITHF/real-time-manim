# -*- coding: utf-8 -*-
"""Full source for the four samples in 01-Construction-and-Containers.md (identical to the code blocks in the page).

Usage: python 01-Construction-and-Containers.py <clip names>...
With no arguments it renders every clip and concatenates the page's four sample videos (written to the parent assets/).
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
    Scene, Mobject, Group, VGroup,
    Square, Circle, Text, Dot,
    BLUE, RED, GREEN, YELLOW, PURPLE, ORANGE,
    RIGHT, UP, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: Mobject constructor parameters ============================
class CtorDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        front = Square(color=RED, side_length=2.4, fill_opacity=0.8, name="hero", z_index=2)   # name "hero", layer 2
        back = Square(color=BLUE, side_length=2.4, fill_opacity=0.8)   # everything else default: name taken from the class, z_index=0
        back.shift(RIGHT * 1.2)   # offset it right a little so the two squares overlap
        self.add(front, back)   # "front" added before "back", but the higher layer still shows on top
        print("color =", back.color, "| name =", back.name, "| dim =", back.dim)   # color, name, vertex-coordinate dimension
        print("target =", front.target, "| z_index =", front.z_index, back.z_index)   # the target cache is empty by default
        win.play(FadeIn(front), FadeIn(back), run_time=0.6)   # fade in both squares together
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window


# ===== Sample 2: the Group container =======================================
class GroupDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.2)   # square
        label = Text("G", font_size=48, color=YELLOW)   # text: a different class from the square
        dot = Dot(color=GREEN, radius=0.35)   # dot: yet another type
        g = Group(sq, label, dot, z_index=1)   # "Group" accepts any type; "z_index" forwards to Mobject
        g.arrange(RIGHT, buff=0.6)   # line the three children up in a row
        self.add(g)   # add the whole group to the scene
        print("len(g) =", len(g), "| type =", [type(m).__name__ for m in g])   # all three children are there
        g.add(sq)   # add the same object again: ignored, only one copy kept
        print("len(g) after duplicate add =", len(g))   # still 3
        try:
            VGroup(Mobject())   # "VGroup" accepts only vector objects
        except TypeError as exc:   # a bare "Mobject" has no vector data
            print("VGroup rejects non-vector objects ->", exc)
        win.play(FadeIn(g), run_time=0.6)   # fade in the whole group
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window


# ===== Sample 3: add / remove / add_to_back / insert =======================
class AddRemoveDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        box = Square(color=RED, side_length=2.6, fill_opacity=0.8)   # red square (with fill)
        disc = Circle(color=BLUE, radius=1.25, fill_opacity=0.8)   # blue disc (with fill)
        g = Group(box)   # put the square into a "Group" first
        g.add(disc)   # add: the disc appends to the tail, showing above the square
        self.add(g)   # add the whole group to the scene
        win.play(FadeIn(g), run_time=0.5)   # fade in: the disc covers the square's center
        g.remove(disc)   # remove: the disc leaves the group, only the square is left on screen
        win.play(Wait(0.4))   # pause 0.4s to see the result
        g.add_to_back(disc)   # add_to_back: the disc prepends to the head, showing below the square
        win.play(Wait(0.4))   # pause 0.4s to see the result
        g.remove(disc)   # take it off first: insert does not de-duplicate, an existing object gains a second reference
        g.insert(1, disc)   # insert: insert by index at the tail, the disc covers the square again
        win.play(Wait(0.4))   # pause 0.4s to see the result
        win.close()   # close the RTM window


# ===== Sample 4: indexing, slicing, and iteration ==========================
class IndexingDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        colors = (RED, BLUE, GREEN, YELLOW, PURPLE)   # five colors
        g = VGroup(*[Square(color=c, side_length=0.9) for c in colors])   # put five squares into a "VGroup"
        g.arrange(RIGHT, buff=0.35)   # line them up in a row
        self.add(g)   # add the whole group to the scene
        print("len(g) =", len(g))   # child count
        print("g[0] =", type(g[0]).__name__, "| g[1:3] =", type(g[1:3]).__name__)   # a slice returns a new group of the same type
        win.play(g[2].animate.shift(UP * 1.2), run_time=0.5)   # a child pulled out by index can be animated directly
        part = g[1:3]   # slice out the two middle squares
        win.play(part.animate.set_color(ORANGE), run_time=0.5)   # recolor only these two
        print("iteration =", [type(m).__name__ for m in g])   # a for loop yields the children in order
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window


SCENES = [
    ("ctor", CtorDemo),
    ("group", GroupDemo),
    ("add_remove", AddRemoveDemo),
    ("indexing", IndexingDemo),
]

PAIRS = [
    ("ctor", ["ctor"]),
    ("group", ["group"]),
    ("add_remove", ["add_remove"]),
    ("indexing", ["indexing"]),
]

PAGE = "01-Construction-and-Containers"


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
