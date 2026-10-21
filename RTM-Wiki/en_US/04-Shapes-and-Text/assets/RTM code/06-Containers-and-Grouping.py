# -*- coding: utf-8 -*-
"""Full source for the five samples in 06-Containers-and-Grouping.md (identical to the code blocks in the page).

Usage: python 06-Containers-and-Grouping.py <sample names>...
With no arguments it renders every sample and concatenates the page's five sample videos (written to assets/RTM output/).
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
    Scene, VGroup, VDict, DashedVMobject, VectorizedPoint, CurvesAsSubmobjects,
    Circle, Square, Triangle, Dot, Line, Rectangle, Text, Arc, Star,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, DR,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: VGroup —— packing vector objects ==========================
class VGroupDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("06-VGroup", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— construction: pack three shapes together ——
        vg = VGroup(Circle(radius=0.5, color=BLUE),
                    Square(side_length=0.9, color=GREEN),
                    Triangle(color=ORANGE).scale(0.5))   # the "*vmobjects" parameter
        vg.arrange(RIGHT, buff=0.4).move_to([-3.4, 1.2, 0])   # the "arrange(direction, buff)" method
        cap = Text("VGroup(circle, square, triangle)", font_size=18, color=GREY_B).next_to(vg, DOWN, buff=0.35)
        win.play(Create(vg), FadeIn(cap), run_time=0.6)

        # —— a whole-group transform: the whole set moves together ——
        win.play(vg.animate.shift(RIGHT * 1.2).scale(1.15), run_time=0.7)   # shift the whole group right and scale it up

        # —— add / remove: add and remove submobjects at any time (the caption updates in place, no overlapping text) ——
        vg.add(Dot([1.6, 0, 0], color=RED, radius=0.14))   # the "add(*vmobjects)" method
        cap.become(Text("add(Dot)", font_size=18, color=GREY_B).next_to(vg, DOWN, buff=0.35))
        win.play(FadeIn(vg[-1]), run_time=0.5)
        vg.remove(vg[1])   # the "remove(*vmobjects)" method: take the square out
        cap.become(Text("remove(square)", font_size=18, color=GREY_B).next_to(vg, DOWN, buff=0.35))
        win.play(FadeOut(vg[1].copy().move_to(vg[1])), run_time=0.5)

        # —— indexing and colouring one by one: vg[i] is a submobject ——
        vg2 = VGroup(*[Dot(point=[-4.0 + i * 0.9, -1.4, 0], radius=0.16) for i in range(7)])
        vg2[0].set_color(RED)   # positional indexing
        vg2[3].set_color(TEAL)
        vg2[-1].set_color(GOLD)
        cap2 = Text("vg2[0] / vg2[3] / vg2[-1] coloured individually", font_size=18, color=GREY_B).next_to(vg2, DOWN, buff=0.4)
        win.play(FadeIn(vg2), FadeIn(cap2), run_time=0.6)

        # —— whole-group style: acts on all submobjects at once ——
        win.play(vg2.animate.set_color_by_gradient(BLUE, PURPLE), run_time=0.7)
        cap2.become(Text("set_color_by_gradient applies to all", font_size=18, color=GREY_B).next_to(vg2, DOWN, buff=0.4))
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: VDict —— the container with names ==========================
class VDictDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("06-VDict", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— dictionary form + show_keys=True: the key is shown next to each submobject ——
        vd = VDict({"c": Circle(radius=0.55, color=BLUE),
                    "s": Square(side_length=0.9, color=GREEN)},
                   show_keys=True)   # the "mapping_or_iterable / show_keys" parameters
        vd.arrange(RIGHT, buff=1.1).move_to([-3.2, 1.2, 0])
        cap = Text('VDict({"c":…, "s":…}, show_keys=True)', font_size=18, color=GREY_B).next_to(vd, DOWN, buff=0.4)
        win.play(FadeIn(vd), FadeIn(cap), run_time=0.6)

        # —— key-value list form + show_keys=False ——
        vd2 = VDict([("tri", Triangle(color=ORANGE).scale(0.55)),
                     ("dot", Dot([0.5, 0, 0], color=RED, radius=0.16))],
                    show_keys=False)   # the "mapping_or_iterable" parameter given an iterable
        vd2.arrange(RIGHT, buff=1.0).move_to([1.6, 1.2, 0])
        win.play(FadeIn(vd2), FadeIn(Text('[("tri",…), ("dot",…)] show_keys=False', font_size=18, color=GREY_B).next_to(vd2, DOWN, buff=0.4)), run_time=0.6)

        # —— fetching by key: vd["c"] gets that submobject ——
        vd["c"].set_color(YELLOW)   # fetch a submobject by index/key
        cap.become(Text('vd["c"].set_color(YELLOW)', font_size=18, color=GREY_B).next_to(vd, DOWN, buff=0.4))
        win.play(Wait(0.4), run_time=0.4)

        # —— add / add_key_value_pair / remove: add and remove at any time (note it is by key, not by index) ——
        vd3 = VDict({"t": Triangle(color=TEAL).scale(0.5),
                     "d": Dot([0.6, 0, 0], color=PURPLE, radius=0.14)})
        vd3.arrange(RIGHT, buff=0.9).move_to([-3.2, -1.6, 0])
        win.play(FadeIn(vd3), run_time=0.5)
        vd3.add({"s2": Square(side_length=0.6, color=GREEN)})   # the "add(mapping)" method
        vd3.add_key_value_pair("c2", Circle(radius=0.32, color=BLUE))   # the "add_key_value_pair(key, value)" method
        vd3.arrange(RIGHT, buff=0.7).move_to([-3.2, -1.6, 0])
        cap3 = Text('add + add_key_value_pair + remove("t")', font_size=18, color=GREY_B).next_to(vd3, DOWN, buff=0.4)
        win.play(FadeIn(vd3["s2"]), FadeIn(vd3["c2"]), FadeIn(cap3), run_time=0.5)   # fetching by key: vd3["s2"]
        vd3.remove("t")   # the "remove(key)" method
        vd3.arrange(RIGHT, buff=0.7).move_to([-3.2, -1.6, 0])

        # —— get_all_submobjects: list the submobjects and move them all together ——
        subs = vd3.get_all_submobjects()   # the "get_all_submobjects()" method
        win.play(vd3.animate.shift(RIGHT * 0.8), run_time=0.6)
        cap3.become(Text("get_all_submobjects() -> %d items" % len(subs), font_size=18, color=GREY_B).next_to(vd3, DOWN, buff=0.4))
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: DashedVMobject —— dashing =================================
class DashedDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("06-DashedVMobject", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— num_dashes: the number of dash segments (10 versus 40) ——
        base = Circle(radius=0.85, color=BLUE)
        d10 = DashedVMobject(base, num_dashes=10, color=BLUE).move_to([-4.6, 1.3, 0])   # the "vmobject / num_dashes" parameters
        d40 = DashedVMobject(base, num_dashes=40, color=TEAL).move_to([-1.8, 1.3, 0])
        win.play(FadeIn(d10), FadeIn(Text("num_dashes=10", font_size=18, color=GREY_B).next_to(d10, DOWN, buff=0.25)), run_time=0.5)
        win.play(FadeIn(d40), FadeIn(Text("num_dashes=40", font_size=18, color=GREY_B).next_to(d40, DOWN, buff=0.25)), run_time=0.5)

        # —— dashed_ratio: the solid fraction (0.5 versus 0.1) ——
        d50 = DashedVMobject(base, num_dashes=20, dashed_ratio=0.5, color=ORANGE).move_to([1.2, 1.3, 0])   # the "dashed_ratio" parameter
        ddot = DashedVMobject(base, num_dashes=20, dashed_ratio=0.1, color=YELLOW).move_to([4.0, 1.3, 0])
        win.play(FadeIn(d50), FadeIn(Text("dashed_ratio=0.5", font_size=18, color=GREY_B).next_to(d50, DOWN, buff=0.25)), run_time=0.5)
        win.play(FadeIn(ddot), FadeIn(Text("dashed_ratio=0.1 (dotted)", font_size=18, color=GREY_B).next_to(ddot, DOWN, buff=0.25)), run_time=0.5)

        # —— dash_offset: the start offset (where on the path the dashes begin) ——
        off0 = DashedVMobject(base, num_dashes=12, color=GREEN).move_to([-4.6, -1.6, 0])   # the "dash_offset" parameter, 0 by default
        off5 = DashedVMobject(base, num_dashes=12, dash_offset=0.5, color=PURPLE).move_to([-1.8, -1.6, 0])
        win.play(FadeIn(off0), FadeIn(Text("dash_offset=0", font_size=18, color=GREY_B).next_to(off0, DOWN, buff=0.25)), run_time=0.5)
        win.play(FadeIn(off5), FadeIn(Text("dash_offset=0.5", font_size=18, color=GREY_B).next_to(off5, DOWN, buff=0.25)), run_time=0.5)

        # —— equal_lengths=False: the segments are unequal (the long ones still follow arc-length proportion) ——
        circle = Circle(radius=0.85, color=BLUE).move_to([1.2, -1.6, 0])
        eq = DashedVMobject(circle, num_dashes=12, equal_lengths=False, color=GOLD).move_to([1.2, -1.6, 0])   # the "equal_lengths" parameter
        win.play(FadeIn(eq), FadeIn(Text("equal_lengths=False", font_size=18, color=GREY_B).next_to(eq, DOWN, buff=0.25)), run_time=0.5)

        # —— not limited to circles: any vector object can be dashed ——
        rr = DashedVMobject(Rectangle(width=2.4, height=1.2, color=RED), num_dashes=24,
                            dashed_ratio=0.6, color=RED).move_to([4.0, -1.6, 0])
        win.play(FadeIn(rr), FadeIn(Text("a rectangle can be dashed too", font_size=18, color=GREY_B).next_to(rr, DOWN, buff=0.25)), run_time=0.5)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 4: VectorizedPoint —— the invisible anchor ====================
class VectorizedPointDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("06-VectorizedPoint", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— default: completely invisible, but it occupies a very small "reported size" ——
        p = VectorizedPoint(location=[-4.6, 1.5, 0])   # the "location" parameter
        box = Rectangle(width=p.width + 0.4, height=p.height + 0.4,
                        color=GREY_B).move_to(p.get_location())
        cap = Text("default 0.01 x 0.01", font_size=16, color=GREY_B).next_to(box, DOWN, buff=0.3)
        win.play(Create(box), FadeIn(cap), run_time=0.6)

        # —— artificial_width / artificial_height: inflate the "reported size" ——
        p2 = VectorizedPoint(location=[-1.6, 1.5, 0], artificial_width=0.8,
                             artificial_height=0.5)   # the "artificial_width / artificial_height" parameters
        box2 = Rectangle(width=p2.width + 0.2, height=p2.height + 0.2,
                         color=GREY_B).move_to(p2.get_location())
        cap2 = Text("artificial 0.8 x 0.5", font_size=16, color=GREY_B).next_to(box2, DOWN, buff=0.3)
        win.play(Create(box2), FadeIn(cap2), run_time=0.6)

        # —— color / fill_opacity / stroke_width: it can also be drawn as a small visible dot ——
        p3 = VectorizedPoint(location=[1.6, 1.5, 0], color=RED, fill_opacity=1.0,
                             stroke_width=0, artificial_width=0.06,
                             artificial_height=0.06)   # the "color / fill_opacity / stroke_width" parameters
        dot = Dot(p3.get_location(), color=YELLOW, radius=0.05)
        cap3 = Text("visible (fill_opacity=1)", font_size=16, color=GREY_B).next_to(p3.get_location(), DOWN, buff=0.35)
        win.play(FadeIn(dot), FadeIn(cap3), run_time=0.6)

        # —— get_location / set_location: move it around as an anchor ——
        target = Dot([-3.0, -1.9, 0], color=TEAL, radius=0.1)
        p.set_location([-3.0, -1.9, 0])   # the "set_location(new_loc)" method
        win.play(FadeIn(target), run_time=0.4)

        # —— use the anchor to position another object: move the box to where it now is ——
        win.play(box.animate.move_to(p.get_location()), run_time=0.8)   # the "get_location()" method
        cap.become(Text("set_location + get_location: the box follows the anchor", font_size=16, color=GREY_B).next_to(target, DOWN, buff=0.4))
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 5: CurvesAsSubmobjects —— splitting into segments ============
class CurvesDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("06-CurvesAsSubmobjects", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— a circle is made of several Bézier curve segments: once split you can count them one by one ——
        cs = CurvesAsSubmobjects(Circle(radius=1.1, color=BLUE))   # the "vmobject" parameter
        cs.move_to([-3.4, 0.4, 0])
        cap = Text("circle -> %d segments" % len(cs), font_size=18, color=GREY_B).next_to(cs, DOWN, buff=0.8)
        win.play(Create(cs), FadeIn(cap), run_time=0.7)

        # —— colouring per segment: each segment is a separate submobject ——
        colors = [RED, ORANGE, YELLOW, GREEN, TEAL, BLUE, PURPLE, GOLD]
        for i, part in enumerate(cs):
            part.set_color(colors[i % len(colors)])
        cap.become(Text("per-segment set_color", font_size=18, color=GREY_B).next_to(cs, DOWN, buff=0.8))
        win.play(Wait(0.4), run_time=0.4)

        # —— per-segment animation: move each segment apart a little, proving they are independent ——
        for i, part in enumerate(cs):
            part.shift(DR * 0.22 * (i % 3))

        # —— split a more complex object: the multi-segment straight lines of a `Star` can be coloured per segment too ——
        star = Star(outer_radius=1.2, color=TEAL)
        cs2 = CurvesAsSubmobjects(star)   # the "vmobject" parameter
        cs2.scale(0.85).move_to([2.6, 0.4, 0])
        cap2 = Text("Star -> %d segments" % len(cs2), font_size=18, color=GREY_B).next_to(cs2, DOWN, buff=0.4)
        win.play(Create(cs2), FadeIn(cap2), run_time=0.8)

        # —— gradient on the split segments: colouring per segment is handier ——
        win.play(cs2.animate.set_color_by_gradient(ORANGE, PURPLE), run_time=0.8)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


SCENES = [
    ("vgroup", VGroupDemo),
    ("vdict", VDictDemo),
    ("dashed", DashedDemo),
    ("vpoint", VectorizedPointDemo),
    ("curves", CurvesDemo),
]

PAIRS = [
    ("vgroup", ["vgroup"]),
    ("vdict", ["vdict"]),
    ("dashed", ["dashed"]),
    ("vpoint", ["vpoint"]),
    ("curves", ["curves"]),
]

PAGE = "06-Containers-and-Grouping"


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
