# -*- coding: utf-8 -*-
"""Full source for the seven samples in 09b-Substrings-and-Lists.md (identical to the code blocks in the page).

Usage: python 09b-Substrings-and-Lists.py <sample names>...
With no arguments it renders every sample and concatenates the page's seven sample videos (written to assets/RTM output/).
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
    Scene, MathTex, BulletedList, Title, Text, Rectangle, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write, MED_LARGE_BUFF,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: set_color_by_tex —— colouring one part ===================
class ColorByTexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("09b-set_color_by_tex", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— the same formula, each of the three coloured once (one "tex / color" pair each time) ——
        pairs = [("x", RED), ("y", GREEN), ("z", BLUE)]   # the "tex / color" parameters
        for i, (tex, col) in enumerate(pairs):
            eq = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2", font_size=52)
            eq.set_color_by_tex(tex, col)   # the "tex = part text / color = target colour" parameters
            eq.move_to([-4.2 + i * 4.2, 0.9, 0])
            cap = Text('set_color_by_tex("%s")' % tex, font_size=18, color=GREY_B).next_to(eq, DOWN, buff=0.4)
            win.play(Write(eq), FadeIn(cap), run_time=0.6)   # colour x red, y green, z blue in turn

        # —— one part can be coloured differently in different formulas ——
        eq2 = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2", font_size=52)
        eq2.set_color_by_tex("x", ORANGE)   # the same "x", this time orange
        eq2.set_color_by_tex("z", PURPLE)   # once more, purple
        eq2.move_to([-1.6, -1.7, 0])
        cap2 = Text('x->ORANGE  z->PURPLE', font_size=18, color=GREY_B).next_to(eq2, DOWN, buff=0.35)
        win.play(Write(eq2), FadeIn(cap2), run_time=0.6)   # chained twice
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: set_color_by_tex_to_color_map —— colour many parts at once
class ColorMapDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("09b-set_color_by_tex_to_color_map", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— method form: pass one dictionary at once ——
        eq = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2", font_size=72)
        eq.set_color_by_tex_to_color_map({"x": RED, "y": GREEN, "z": BLUE})   # the "texs_to_color_map" parameter
        eq.move_to([0, 0.9, 0])
        cap = Text("set_color_by_tex_to_color_map({...})", font_size=18, color=GREY_B).next_to(eq, DOWN, buff=0.4)
        win.play(Write(eq), FadeIn(cap), run_time=0.6)   # colour three parts at once

        # —— construction-argument form: fully equivalent, just write it into MathTex(...) ——
        eq2 = MathTex("{{a}}^2", "+", "{{b}}^2", "=", "{{c}}^2", font_size=72,
                      tex_to_color_map={"a": ORANGE, "b": TEAL, "c": PURPLE})   # the "tex_to_color_map" parameter
        eq2.move_to([0, -1.7, 0])
        cap2 = Text("MathTex(..., tex_to_color_map={...})", font_size=18, color=GREY_B).next_to(eq2, DOWN, buff=0.35)
        win.play(Write(eq2), FadeIn(cap2), run_time=0.6)   # coloured as it is constructed
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: get_part_by_tex —— fetching one part =====================
class GetPartDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("09b-get_part_by_tex", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— the fetched sub-object can be animated on its own (here boxed) ——
        eq = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2", font_size=72).move_to([0, 0.9, 0])
        part = eq.get_part_by_tex("y")   # the "tex = part text" parameter
        box = Rectangle(width=part.width + 0.3, height=part.height + 0.3,
                        color=YELLOW).move_to(part.get_center())   # box the "y" only
        win.play(Write(eq), run_time=0.6)   # write the formula first
        win.play(Create(box), run_time=0.5)   # box the part that was fetched

        # —— the fetched part can also be moved on its own ——
        eq2 = MathTex("{{a}}", "+", "{{b}}", "=", "{{c}}", font_size=72).move_to([0, -1.7, 0])
        part2 = eq2.get_part_by_tex("b")
        win.play(Write(eq2), run_time=0.6)
        win.play(part2.animate.shift(UP * 1.2), run_time=0.6)   # lift the "b" on its own
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 4: set_opacity_by_tex —— highlight one, dim the rest =========
class OpacityByTexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("09b-set_opacity_by_tex", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— opacity defaults to 0.5; without remaining_opacity nothing else moves ——
        eq = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2", font_size=72)
        eq.set_opacity_by_tex("y")   # only the "tex" parameter: opacity=0.5 by default
        eq.move_to([-2.2, 0.9, 0])
        cap = Text("set_opacity_by_tex('y')", font_size=18, color=GREY_B).next_to(eq, DOWN, buff=0.4)
        win.play(Write(eq), FadeIn(cap), run_time=0.6)

        # —— opacity explicit + remaining_opacity: the focus bright, the rest darker ——
        eq2 = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2", font_size=72)
        eq2.set_opacity_by_tex("y", opacity=1.0, remaining_opacity=0.25)   # the "opacity / remaining_opacity" parameters
        eq2.move_to([2.2, 0.9, 0])
        cap2 = Text("opacity=1.0 remaining=0.25", font_size=18, color=GREY_B).next_to(eq2, DOWN, buff=0.4)
        win.play(Write(eq2), FadeIn(cap2), run_time=0.6)

        # —— two calls on the same formula: highlight different parts in turn ——
        eq3 = MathTex("{{a}}", "+", "{{b}}", "=", "{{c}}", font_size=72)
        eq3.set_opacity_by_tex("b", opacity=1.0, remaining_opacity=0.3)
        eq3.move_to([0, -1.7, 0])
        cap3 = Text("highlight 'b'", font_size=18, color=GREY_B).next_to(eq3, DOWN, buff=0.35)
        win.play(Write(eq3), FadeIn(cap3), run_time=0.6)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 5: MathTexPart —— iterating parts and reading tex_string =====
class PartsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("09b-MathTexPart", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— iterating sub-objects: every MathTexPart carries its own .tex_string ——
        eq = MathTex(r"{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2", font_size=64)
        eq.move_to([0, 1.4, 0])
        win.play(Write(eq), run_time=0.8)   # write the formula first

        labels = VGroup()   # print each part's tex_string below in turn
        for i, part in enumerate(eq.submobjects):
            txt = getattr(part, "tex_string", "(no tex_string)")   # the "tex_string" attribute
            labels.add(Text("%d: %s" % (i, txt), font_size=18, color=GREY_B))
        labels.arrange(DOWN, buff=0.08).next_to(eq, DOWN, buff=0.35)
        win.play(FadeIn(labels), run_time=0.6)   # list the part texts one by one
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 6: BulletedList —— a bulleted list =========================
class BulletedListDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("09b-BulletedList", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— buff at its default, dot_scale_factor at its default 2 ——
        bl = BulletedList("first item", "second item", "third item",
                          font_size=40)   # the "*items" parameter
        bl.move_to([-3.2, 0.9, 0])
        win.play(Write(bl), run_time=0.7)   # default spacing and dot size

        # —— buff tightened + dot_scale_factor enlarged ——
        bl2 = BulletedList("tight", "spacing", "list", font_size=40,
                           buff=MED_LARGE_BUFF * 0.3,   # the "buff" parameter: item spacing
                           dot_scale_factor=4)   # the "dot_scale_factor" parameter: dot enlargement
        bl2.move_to([2.6, 0.9, 0])
        cap2 = Text("buff=0.3x  dot_scale_factor=4", font_size=18, color=GREY_B).next_to(bl2, DOWN, buff=0.4)
        win.play(Write(bl2), FadeIn(cap2), run_time=0.7)

        # —— fade_all_but: dim every item except one, by "index" ——
        bl3 = BulletedList("alpha", "beta", "gamma", font_size=40).move_to([-1.6, -1.6, 0])
        win.play(Write(bl3), run_time=0.6)
        bl3.fade_all_but(1, opacity=0.25)   # the "index_or_string=1" parameter: only item 1 stays as it is
        win.play(FadeIn(Text("fade_all_but(1, opacity=0.25)",
                             font_size=18, color=GREY_B).next_to(bl3, DOWN, buff=0.3)),
                 run_time=0.4)
        bl3.fade_all_but(2, opacity=0.25)   # switch the parameter to 2: now dim items 0 and 1
        win.play(FadeIn(Text("fade_all_but(2, opacity=0.25)",
                             font_size=18, color=GREY_B).next_to(bl3, DOWN, buff=0.05)),
                 run_time=0.4)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 7: Title —— the page-header title and its underline ==========
class TitleDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"

        # —— default: comes with an underline as wide as the screen ——
        t1 = Title("Chapter 1")   # the "*text_parts" parameter
        win.play(Write(t1), run_time=0.6)   # the default underline spans the screen width
        win.play(FadeOut(t1), run_time=0.3)

        # —— match_underline_width_to_text: the underline is only as wide as the text ——
        t2 = Title("Chapter 2", match_underline_width_to_text=True)   # the "match_underline_width_to_text=True" parameter
        win.play(Write(t2), run_time=0.6)
        win.play(FadeOut(t2), run_time=0.3)

        # —— include_underline=False: no underline at all ——
        t3 = Title("Chapter 3", include_underline=False)   # the "include_underline=False" parameter
        win.play(Write(t3), run_time=0.6)
        win.play(FadeOut(t3), run_time=0.3)

        # —— underline_buff: the gap between the underline and the text ——
        t4 = Title("Chapter 4", match_underline_width_to_text=True,
                   underline_buff=0.55)   # the "underline_buff=0.55" parameter (MED_SMALL_BUFF by default)
        win.play(Write(t4), run_time=0.8)   # the underline sits visibly further from the text
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


SCENES = [
    ("colorbytex", ColorByTexDemo),
    ("colormap", ColorMapDemo),
    ("getpart", GetPartDemo),
    ("opacitybytex", OpacityByTexDemo),
    ("parts", PartsDemo),
    ("bulletedlist", BulletedListDemo),
    ("title", TitleDemo),
]

PAIRS = [
    ("colorbytex", ["colorbytex"]),
    ("colormap", ["colormap"]),
    ("getpart", ["getpart"]),
    ("opacitybytex", ["opacitybytex"]),
    ("parts", ["parts"]),
    ("bulletedlist", ["bulletedlist"]),
    ("title", ["title"]),
]

PAGE = "09b-Substrings-and-Lists"


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
