# -*- coding: utf-8 -*-
"""Full source for the five samples in 04-VectorScene.md (identical to the code blocks in the page).

Usage: python 04-VectorScene.py <clip names>...
With no arguments it renders all 6 clips and concatenates the page's first comparison video (plane).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
ASSETS = os.path.dirname(HERE)
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    GREEN, RED, WHITE, YELLOW, UP, Dot, Text, VectorScene,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


def say(cap, text):   # instantly swap the top caption text without spending animation time
    cap.become(Text(text, font_size=28, color=YELLOW).to_edge(UP))


# ===== Sample 1: constructor parameters, add_plane, add_axes ===============
class PlaneAxesBase(VectorScene):
    STROKE = 6.0   # subclasses lower it to see the basis vectors get thinner
    TAG = ""       # subclasses fill in the stroke-width number for the title

    def __init__(self, **kwargs):
        super().__init__(basis_vector_stroke_width=self.STROKE, **kwargs)   # pass "basis_vector_stroke_width" to VectorScene.__init__

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # add_plane / add_axes call self.play internally, so wire it to the window first
        cap = Text("", font_size=28, color=YELLOW)   # top caption text (content swapped later)
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(cap)   # add it to the scene

        say(cap, "add_plane(animate=True)")
        plane = self.add_plane(animate=True)   # draw the grid plane with Create
        self.plane = plane   # get_vector / add_vector both read self.plane, so hang it on by hand
        win.play(Wait(0.6))   # pause 0.6s

        say(cap, "add_axes(animate=True, color=WHITE)")
        self.remove(plane)   # take the grid away
        self.add_axes(animate=True, color=WHITE)   # draw the axes with Create
        win.play(Wait(0.4))   # pause 0.4s

        say(cap, "get_basis_vectors() stroke=%.1f" % self.STROKE)
        self.add(self.get_basis_vectors())   # put i_hat / j_hat on screen, at the constructor's stroke width
        win.play(Wait(0.8))   # pause 0.8s and finish
        win.close()   # close the RTM window


class PlaneAxesWide(PlaneAxesBase):
    STROKE = 6.0   # default stroke width
    TAG = "6.0"


class PlaneAxesThin(PlaneAxesBase):
    STROKE = 2.0   # one step thinner
    TAG = "2.0"


# ===== Sample 2: add_vector / get_vector ===================================
class VectorAddDemo(VectorScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # add_vector calls self.play internally, so wire it to the window first
        cap = Text("", font_size=28, color=YELLOW)   # top caption text (content swapped later)
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(cap)   # add it to the scene
        plane = self.add_plane(animate=False)   # put the grid on screen directly
        self.plane = plane   # get_vector / add_vector both read self.plane, so hang it on by hand

        say(cap, "add_vector([2, 1], color=YELLOW, animate=True)")
        self.add_vector([2, 1], color=YELLOW, animate=True)   # build the vector from coordinates, entering with GrowArrow
        win.play(Wait(0.8))   # pause 0.8s

        say(cap, "get_vector([-2, 1]) -> self.add(arrow)")
        arrow = self.get_vector([-2, 1])   # only build the Arrow: not added to the scene, not registered
        self.add(arrow)   # decide for yourself when to add it
        win.play(Wait(0.8))   # pause 0.8s and finish
        win.close()   # close the RTM window


# ===== Sample 3: write_vector_coordinates / label_vector / get_vector_label
class VectorLabelDemo(VectorScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # several methods below call self.play internally, so wire it to the window first
        cap = Text("", font_size=28, color=YELLOW)   # top caption text (content swapped later)
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(cap)   # add it to the scene
        plane = self.add_plane(animate=False)   # put the grid on screen directly
        self.plane = plane   # add_vector reads self.plane, so hang it on by hand
        v = self.add_vector([2, 1], color=YELLOW, animate=True)   # you need a vector object first

        say(cap, "write_vector_coordinates(v)")
        self.write_vector_coordinates(v)   # write the column matrix [2, 1] and register it in the foreground layer
        win.play(Wait(0.8))   # pause 0.8s

        say(cap, "label_vector(v, 'v')")
        self.label_vector(v, "v")   # Write a label next to the vector; a single character is typeset as the arrow letter v
        win.play(Wait(0.8))   # pause 0.8s

        say(cap, "get_vector_label(v, 'w', at_tip=True, ...)")
        lab = self.get_vector_label(   # only builds the label, plays no animation; all the parameters are here
            v, "w", at_tip=True, direction="right",
            rotate=False, color=GREEN, label_scale_factor=1.0)
        self.add(lab)   # add it to the scene yourself
        win.play(Wait(0.8))   # pause 0.8s and finish
        win.close()   # close the RTM window


# ===== Sample 4: get_basis_vectors / get_basis_vector_labels ===============
class BasisDemo(VectorScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        cap = Text("", font_size=28, color=YELLOW)   # top caption text (content swapped later)
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(cap)   # add it to the scene
        plane = self.add_plane(animate=False)   # put the grid on screen directly
        self.plane = plane   # nothing to do with the vectors, just a backdrop

        say(cap, "get_basis_vectors() default X_COLOR / Y_COLOR")
        basis = self.get_basis_vectors()   # default: i_hat green (X_COLOR), j_hat red (Y_COLOR)
        labels = self.get_basis_vector_labels()   # the MathTex labels for i_hat / j_hat
        self.add(basis, labels)   # add them to the scene together
        win.play(Wait(0.9))   # pause 0.9s

        self.remove(basis, labels)   # take the default-colour basis vectors away
        say(cap, "get_basis_vectors(i_hat_color=GREEN, j_hat_color=RED)")
        basis2 = self.get_basis_vectors(   # swap in manim's standard GREEN / RED (different from the defaults)
            i_hat_color=GREEN, j_hat_color=RED)
        self.add(basis2, labels)   # reuse the labels, only the colors changed
        win.play(Wait(0.9))   # pause 0.9s and finish
        win.close()   # close the RTM window


# ===== Sample 5: vector_to_coords ==========================================
class CoordsDemo(VectorScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # vector_to_coords calls self.play internally, so wire it to the window first
        cap = Text("", font_size=28, color=YELLOW)   # top caption text (content swapped later)
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(cap)   # add it to the scene
        plane = self.add_plane(animate=False)   # put the grid on screen directly
        self.plane = plane   # nothing to do with the vectors, just a backdrop

        say(cap, "vector_to_coords([-1, 2], integer_labels=True)")
        self.vector_to_coords([-1, 2], integer_labels=True, clean_up=True)   # vector-to-coordinates decomposition, restored at the end
        win.play(Wait(0.5))   # pause 0.5s

        say(cap, "vector_to_coords([1.5, -1], integer_labels=False)")
        self.vector_to_coords([1.5, -1], integer_labels=False, clean_up=True)   # decimals get decimal labels
        win.play(Wait(0.5))   # pause 0.5s and finish
        win.close()   # close the RTM window


SCENES = [
    ("plane_wide", PlaneAxesWide),
    ("plane_thin", PlaneAxesThin),
    ("addvec", VectorAddDemo),
    ("labels", VectorLabelDemo),
    ("basis", BasisDemo),
    ("coords", CoordsDemo),
]

PAIRS = [
    ("04-VectorScene-plane", ["plane_wide", "plane_thin"]),
]


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

    for out_name, names in PAIRS:
        dst = os.path.join(ASSETS, "RTM output", out_name + ".mp4")
        concat(names, dst)
        print("concat ->", dst, os.path.getsize(dst), "bytes")

    import shutil   # single clips are published as page videos too: <page name>-<clip name>.mp4
    PAGE = os.path.splitext(os.path.basename(__file__))[0]
    used = {n for _, names in PAIRS for n in names}
    for name, _ in SCENES:
        if name in used or (only and name not in only):
            continue
        src = os.path.join(OUT, name + ".mp4")
        if os.path.exists(src):
            shutil.copy(src, os.path.join(HERE, "..", PAGE + "-" + name + ".mp4"))
            print("publish ->", PAGE + "-" + name + ".mp4")
