# -*- coding: utf-8 -*-
"""Full source of the seven samples in 06-Copying-Deriving-and-State.md (identical to the code blocks in the page).

Usage: python 06-Copying-Deriving-and-State.py <clip name>...
With no arguments it renders every clip and concatenates the page's seven sample videos (output to the parent assets/).
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
    Scene, VGroup, Square, Rectangle, Circle, Text,
    BLUE, RED, GREEN, YELLOW, ORANGE, PURPLE, TEAL, GREY,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI, FadeIn, MoveToTarget, straight_path,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: copy =====================================================
class CopyDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.4, fill_opacity=0.6).shift(LEFT * 3.5)   #the original
        self.add(sq)   #add to the scene
        twin = sq.copy()   #deep copy: an independent copy that does not enter the scene automatically
        twin.set_color(RED).shift(RIGHT * 2.0)   #recolor the copy and move it away: independent of the original
        self.add(twin)   #add the copy to the scene
        win.play(FadeIn(twin), run_time=0.5)   #fade the copy in
        win.play(sq.animate.set_color(GREEN), run_time=0.5)   #recolor the original: the copy does not move at all
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


# ===== Sample 2: become ===================================================
class BecomeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        circ = Circle(radius=0.9, color=ORANGE, fill_opacity=0.7)   #circle
        self.add(circ)   #add to the scene
        rect = Rectangle(width=3.0, height=1.4, color=PURPLE, fill_opacity=0.7).shift(RIGHT * 3.2)   #the target rectangle is on the right
        win.play(circ.animate.become(rect), run_time=0.6)   #shape and position both turn into the target's
        print("after become: width =", round(circ.width, 2), "position =", circ.get_center().round(2))   #3.0, it has moved to the right
        dot = Circle(radius=0.3, color=TEAL).shift(LEFT * 3.2)   #the target small circle is on the left
        win.play(circ.animate.become(dot, match_center=True, stretch=True),
                 run_time=0.5)   #stretch pulls the target to its own 3.0×1.4 (small circle → ellipse), match_center keeps the position put
        print("after stretch+center:", round(circ.width, 2), round(circ.height, 2), circ.get_center().round(2))   #3.0 1.4, position unchanged
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


# ===== Sample 3: save_state / restore ====================================
class SaveRestoreDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.4, fill_opacity=0.7).shift(LEFT * 3.0)   #blue square
        self.add(sq)   #add to the scene
        sq.save_state()   #save position/size/color/structure into saved_state
        win.play(sq.animate.scale(1.8).set_color(GREEN).shift(RIGHT * 3.0), run_time=0.7)   #scale up, turn green, move right
        win.play(sq.animate.restore(), run_time=0.6)   #restore to the state at save time
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


# ===== Sample 4: generate_target + MoveToTarget ===========================
class TargetDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=YELLOW, side_length=1.2).shift(LEFT * 3.5)   #yellow square
        self.add(sq)   #add to the scene
        sq.generate_target(use_deepcopy=False)   #generate the self.target snapshot (the object itself does not disappear)
        sq.target.shift(RIGHT * 3.0).scale(1.6).set_color(TEAL)   #arrange the target shape on the snapshot
        win.play(MoveToTarget(sq), run_time=0.7)   #animate the object to the target shape
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


# ===== Sample 5: interpolate =============================================
class InterpolateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=GREEN, side_length=1.2)   #green square
        self.add(sq)   #add to the scene
        win.play(Wait(0.4))   #see the start state
        s1 = sq.copy()   #start state
        s2 = sq.copy().shift(RIGHT * 2.5).scale(1.5).rotate(PI / 4)   #end state
        sq.interpolate(s1, s2, 0.5, path_func=straight_path())   #take the interpolated state at alpha=0.5 directly (instantly)
        win.play(Wait(0.5))   #see the mid state
        win.play(sq.animate.become(s2), run_time=0.4)   #then animate to the end state for comparison
        win.play(Wait(0.3))   #wait 0.3s
        win.close()   #close the RTM window


# ===== Sample 6: match_dim_size / match_width / match_height / match_depth =
class MatchSizeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        ref = Rectangle(width=2.6, height=1.0, color=GREY, fill_opacity=0.5).shift(UP * 1.6)   #the reference rectangle
        m1 = Square(color=BLUE, side_length=1.0).shift(LEFT * 3.0)   #the proportional comparison
        m2 = Square(color=RED, side_length=1.8).shift(LEFT * 1.0)   #the stretched comparison
        self.add(ref, m1, m2)   #add to the scene
        win.play(m1.animate.match_width(ref), run_time=0.5)   #scale proportionally to the reference's width
        print("after match_width:", round(m1.width, 2), round(m1.height, 2))   #2.6 2.6
        win.play(m2.animate.match_dim_size(ref, 1, stretch=True), run_time=0.5)   #match_dim_size: dim=1, squash only this dimension
        print("after match_dim_size:", round(m2.width, 2), round(m2.height, 2))   #1.8 1.0
        m2.match_depth(ref)   #match_depth: a safe no-op for flat objects (all dimension lengths are 0)
        print("after match_depth:", round(m2.width, 2), round(m2.height, 2))   #unchanged
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


# ===== Sample 7: match_coord / match_points / align_points ===============
class MatchPosDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        ref = Circle(radius=0.8, color=GREY, fill_opacity=0.5).shift(UP * 1.5 + RIGHT * 2.0)   #the reference circle
        m1 = Square(color=BLUE, side_length=1.0).shift(LEFT * 3.5 + DOWN * 1.5)   #the x-alignment comparison
        m2 = Square(color=RED, side_length=1.0).shift(LEFT * 1.5 + DOWN * 1.5)   #the y-edge-alignment comparison
        self.add(ref, m1, m2)   #add to the scene
        win.play(m1.animate.match_x(ref), run_time=0.5)   #match_x: align x to the reference's centre
        win.play(m2.animate.match_coord(ref, 1, direction=DOWN), run_time=0.5)   #match_coord: dim=1, align by the bottom edge
        print("ref centre =", ref.get_center().round(2), "| m1 centre =", m1.get_center().round(2))   #x is the same
        mp = Circle(color=TEAL, radius=0.4).shift(LEFT * 3.5 + UP * 1.5)   #the circle to be reshaped
        self.add(mp)   #add to the scene
        win.play(mp.animate.match_points(ref), run_time=0.5)   #match_points: copy the reference's vertices outright (shape and size both change)
        print("after match_points width =", round(mp.width, 2))   #1.6, matching the reference
        mp.align_points(ref)   #align_points: align the vertex counts (a prerequisite of interpolation)
        print("points after align_points =", mp.get_num_points(), ref.get_num_points())   #both the same
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window


SCENES = [
    ("copy", CopyDemo),
    ("become", BecomeDemo),
    ("save_restore", SaveRestoreDemo),
    ("target", TargetDemo),
    ("interpolate", InterpolateDemo),
    ("match_size", MatchSizeDemo),
    ("match_pos", MatchPosDemo),
]

PAIRS = [
    ("copy", ["copy"]),
    ("become", ["become"]),
    ("save_restore", ["save_restore"]),
    ("target", ["target"]),
    ("interpolate", ["interpolate"]),
    ("match_size", ["match_size"]),
    ("match_pos", ["match_pos"]),
]

PAGE = "06-Copying-Deriving-and-State"


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
