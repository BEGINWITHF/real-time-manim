# -*- coding: utf-8 -*-
"""Full source of the six samples in 05-Style-and-Color.md (identical to the code blocks in the page).

Usage: python 05-Style-and-Color.py <clip name>...
With no arguments it renders every clip and concatenates the page's six sample videos (output to the parent assets/).
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
    Scene, Group, VGroup, Square, Circle, Text, Rectangle,
    BLUE, RED, GREEN, YELLOW, PURPLE, ORANGE, WHITE, BLACK, TEAL,
    UP, DOWN, LEFT, RIGHT, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: set_color ===============================================
class SetColorDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=2.2, fill_opacity=0.7)   #blue square
        kid = Square(color=YELLOW, side_length=0.8, fill_opacity=0.9)   #small yellow square
        g = Group(sq, kid)   #put the small square into the group as a submobject
        self.add(g)   #add to the scene
        win.play(g.animate.set_color(ORANGE), run_time=0.6)   #default family=True: change the whole group including submobjects
        win.play(g.animate.set_color(GREEN, family=False), run_time=0.6)   #family=False: change only the group's own attributes
        print("sq =", sq.get_color(), "| kid =", kid.get_color())   #the submobject stays orange: family=False does not propagate down
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


# ===== Sample 2: the gradient quartet ====================================
class GradientDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        r1 = VGroup(*[Square(side_length=0.8) for _ in range(4)])   #a row of four squares
        r1.arrange(RIGHT, buff=0.25).shift(UP * 2.2)
        self.add(r1)   #add to the scene
        win.play(r1.animate.set_color_by_gradient(BLUE, RED), run_time=0.5)   #gradient across the group: the four squares take the in-between colors in turn
        r2 = VGroup(*[Square(side_length=0.8) for _ in range(4)])   #second row
        r2.arrange(RIGHT, buff=0.25).shift(UP * 0.7)
        self.add(r2)   #add to the scene
        win.play(r2.animate.set_submobject_colors_by_gradient(GREEN, PURPLE), run_time=0.5)   #color the submobjects one by one directly (an equivalent implementation)
        r3 = VGroup(*[Circle(radius=0.2 + 0.15 * i) for i in range(3)])   #third row: circles of different sizes
        r3.arrange(RIGHT, buff=0.35).shift(DOWN * 1.0)
        self.add(r3)   #add to the scene
        win.play(r3.animate.set_colors_by_radial_gradient(radius=1.6, inner_color=WHITE, outer_color=BLUE), run_time=0.5)   #radial: colors taken by distance from the centre
        r4 = VGroup(*[Circle(radius=0.2 + 0.15 * i) for i in range(3)])   #fourth row
        r4.arrange(RIGHT, buff=0.35).shift(DOWN * 2.4)
        self.add(r4)   #add to the scene
        win.play(r4.animate.set_submobject_colors_by_radial_gradient(radius=1.6, inner_color=YELLOW, outer_color=RED), run_time=0.5)   #same as above
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


# ===== Sample 3: fade_to / fade ==========================================
class FadeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        f1 = Square(color=BLUE, side_length=1.4, fill_opacity=0.8).shift(LEFT * 2.5)   #left: blend colors
        f2 = Square(color=BLUE, side_length=1.4, fill_opacity=0.8).shift(RIGHT * 2.5)   #right: fade
        self.add(f1, f2)   #add to the scene
        win.play(f1.animate.fade_to(RED, 0.7), run_time=0.6)   #blend 70% toward red
        win.play(f2.animate.fade(darkness=0.6), run_time=0.6)   #fade the vector object by 60%
        print("f1 =", f1.get_color(), "| f2 =", f2.get_color())   #verify by reading the colors
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


# ===== Sample 4: get_color / match_color / to_original_color =============
class GetMatchDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        a = Square(color=RED, side_length=1.4).shift(LEFT * 3.0 + UP * 1.2)   #red square
        b = Square(color=GREEN, side_length=1.4).shift(RIGHT * 3.0 + UP * 1.2)   #green square
        self.add(a, b)   #add to the scene
        print("a =", a.get_color())   #read the current color
        win.play(a.animate.match_color(b), run_time=0.6)   #set a's color to b's
        print("after match: a =", a.get_color(), "b =", b.get_color())
        w = Text("color", font_size=38, color=WHITE).shift(DOWN * 1.6)   #white text: the glyphs can be colored individually
        w[0:2].set_color(RED)   #color only the first two letters red
        self.add(w)   #add to the scene
        win.play(FadeIn(w), run_time=0.4)   #fade the text in
        win.play(Wait(0.5))   #see that the first two letters are red
        w.to_original_color()   #reset to self.color across the board: the glyphs' individual colors are cleared
        print("after reset w =", w.get_color())   #the attribute prints black (Text's color defaults to black)
        win.play(Wait(0.5))   #see that all the glyphs are restored
        win.close()   #close the RTM window


# ===== Sample 5: set_z_index / set_z_index_by_z_Point3D ==================
class ZIndexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        zA = Square(color=RED, side_length=2.2, fill_opacity=0.85).shift(LEFT * 2.2)   #red square
        zB = Square(color=BLUE, side_length=2.2, fill_opacity=0.85).shift(LEFT * 1.3)   #blue square
        self.add(zA, zB)   #the blue one added later is on top (equal levels fall back to insertion order)
        win.play(Wait(0.5))   #look at the default stacking first
        zA.set_z_index(2)   #set the red level to 2: it overtakes to the upper layer instantly
        win.play(Wait(0.5))   #pause to see the red cover the blue
        zB.set_z(3.0)   #give the blue one a z coordinate (no visible position change on a 2D canvas)
        zB.set_z_index_by_z_Point3D()   #blue level = centre z coordinate = 3: it covers again
        print("z_index:", zA.z_index, zB.z_index)   #2 3
        win.play(Wait(0.5))   #pause to see the blue cover the red
        win.close()   #close the RTM window


# ===== Sample 6: the three add_background_rectangle variants =============
class BgRectDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        bg = VGroup(*[Rectangle(width=2.0, height=6.0, color=c, fill_opacity=1.0) for c in (RED, BLUE, GREEN)])   #three colored vertical bars
        bg.arrange(RIGHT, buff=0)
        self.add(bg)   #busy background
        txt = Text("READABLE", font_size=44, color=WHITE).shift(UP * 1.6)   #white text
        txt.add_background_rectangle(color=BLACK, opacity=0.75)   #put a semi-transparent black block behind it
        self.add(txt)
        win.play(FadeIn(bg), FadeIn(txt), run_time=0.6)   #fade in the background and the text together
        duo = VGroup(Text("A", font_size=36), Text("B", font_size=36)).arrange(RIGHT, buff=0.9)
        duo.shift(UP * 0.1)
        duo.add_background_rectangle_to_submobjects(color=BLACK, opacity=0.7)   #give each letter its own block
        self.add(duo)
        rings = VGroup(Circle(radius=0.35), Circle(radius=0.35)).arrange(RIGHT, buff=0.4).shift(DOWN * 1.8)
        rings.add_background_rectangle_to_family_members_with_points(color=BLACK, opacity=0.7)   #give each member with vertices its own block
        self.add(rings)
        win.play(FadeIn(duo), FadeIn(rings), run_time=0.5)   #fade in the two groups
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


SCENES = [
    ("set_color", SetColorDemo),
    ("gradient", GradientDemo),
    ("fade", FadeDemo),
    ("get_match", GetMatchDemo),
    ("z_index", ZIndexDemo),
    ("background", BgRectDemo),
]

PAIRS = [
    ("set_color", ["set_color"]),
    ("gradient", ["gradient"]),
    ("fade", ["fade"]),
    ("get_match", ["get_match"]),
    ("z_index", ["z_index"]),
    ("background", ["background"]),
]

PAGE = "05-Style-and-Color"


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
