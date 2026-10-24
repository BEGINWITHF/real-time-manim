# -*- coding: utf-8 -*-
"""The samples of 05-LinearTransformationScene.md rendered under RTM (one class per sample).

Four samples:
  1. the constructor parameters show_coordinates / include_background_plane / leave_ghost_vectors
     -> four clips stitched into 05-LinearTransformationScene-ctor.mp4
  2. apply_matrix / apply_inverse / apply_transposed_matrix / apply_inverse_transpose
  3. apply_nonlinear_transformation / apply_function
  4. add_title / add_unit_square / add_vector / write_vector_coordinates /
     add_transformable_label

Usage: python 05-LinearTransformationScene.py            # everything
       python 05-LinearTransformationScene.py apply      # render only the named clips
"""
import math
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
ASSETS = os.path.dirname(HERE)
os.makedirs(OUT, exist_ok=True)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))
from real_time_manim import (  # noqa: E402
    DOWN,
    UP,
    YELLOW,
    LinearTransformationScene,
    Text,
    Wait,
)
from real_time_manim.record import fast_record_scene  # noqa: E402
from real_time_manim.vulkan_bind import MLWindow, Wait  # noqa: E402


def say(cap, text):   # instantly swap the top caption text without spending animation time
    cap.become(Text(text, font_size=26, color=YELLOW).to_edge(UP))


def say_low(cap, text):   # for ComposeDemo only: put the caption at the bottom to make room for add_title at the top
    cap.become(Text(text, font_size=26, color=YELLOW).to_edge(DOWN))


# ===== Sample 1: LinearTransformationScene constructor parameters ==========
class CtorBase(LinearTransformationScene):
    KW = {}            # subclasses fill in the constructor parameters to pass to LinearTransformationScene.__init__
    LABEL = ""         # subclasses fill in this clip's title text
    TRANSFORM = False  # subclasses with True play one shear at the end

    def __init__(self, **kwargs):
        super().__init__(**self.KW, **kwargs)   # pass the keys in "KW" to LinearTransformationScene.__init__

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # apply_* calls self.play internally, so wire it to the window first
        cap = Text(self.LABEL, font_size=26, color=YELLOW)   # top title shows the current constructor parameters
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(cap)   # add it to the scene (setup adds the grids and basis vectors automatically)
        win.play(Wait(1.3))   # pause 1.3s to see the default staging
        if self.TRANSFORM:
            self.apply_matrix([[1, 1], [0, 1]], run_time=1.2)   # one horizontal shear: only then is the ghost switch visible
            win.play(Wait(0.6))   # pause 0.6s to see the ghost
        win.close()   # close the RTM window


class LtsPlain(CtorBase):
    LABEL = "defaults (bg+fg plane, i_hat/j_hat)"   # default staging
    KW = {}                                          # an empty dict = manim's defaults


class LtsCoords(CtorBase):
    LABEL = "show_coordinates=True"                 # the background grid shows tick numbers
    KW = {"show_coordinates": True}


class LtsBgOff(CtorBase):
    LABEL = "include_background/foreground_plane=False"   # both grid planes gone
    KW = {"include_background_plane": False,              # switch off the background plane
          "include_foreground_plane": False}              # switch off the foreground plane: only the basis vectors remain


class LtsGhost(CtorBase):
    LABEL = "leave_ghost_vectors=True"              # keep the basis vectors' ghost after the transform
    KW = {"leave_ghost_vectors": True}
    TRANSFORM = True                                # this clip plays one transform


# ===== Sample 2: apply_matrix / apply_inverse / apply_transposed_matrix =====
class ApplyDemo(LinearTransformationScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # every apply_* calls self.play internally, so wire it to the window first
        cap = Text("", font_size=26, color=YELLOW)   # top caption text (content swapped later)
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(cap)   # add it to the scene

        say(cap, "apply_matrix([[1, 1], [0, 1]])")
        self.apply_matrix([[1, 1], [0, 1]], run_time=1.2)   # horizontal shear: the whole grid leans up and to the right
        win.play(Wait(0.5))   # pause 0.5s

        say(cap, "apply_inverse([[1, 1], [0, 1]])")
        self.apply_inverse([[1, 1], [0, 1]], run_time=1.2)   # invert M and apply it, undoing the previous step
        win.play(Wait(0.5))   # pause 0.5s

        say(cap, "apply_transposed_matrix([[1, 1], [0, 1]])")
        self.apply_transposed_matrix([[1, 1], [0, 1]], run_time=1.2)   # pass M, apply its transpose (a vertical shear)
        win.play(Wait(0.5))   # pause 0.5s

        say(cap, "apply_inverse_transpose([[1, 1], [0, 1]])")
        self.apply_inverse_transpose([[1, 1], [0, 1]], run_time=1.2)   # apply the inverse transpose, back to the original grid
        win.play(Wait(0.6))   # pause 0.6s and finish
        win.close()   # close the RTM window


# ===== Sample 3: apply_nonlinear_transformation / apply_function ============
class NonlinearDemo(LinearTransformationScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # every apply_* calls self.play internally, so wire it to the window first
        cap = Text("", font_size=26, color=YELLOW)   # top caption text (content swapped later)
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(cap)   # add it to the scene
        self.add_unit_square(animate=False)   # add a unit square to make the bending more obvious

        def swirl(p):   # rotate by distance from the origin: the further out, the more it turns
            x, y = p[0], p[1]
            a = 0.5 * math.hypot(x, y)   # turn 0.5 radians more per unit of radius
            c, s = math.cos(a), math.sin(a)
            return np.array([x * c - y * s, x * s + y * c, p[2]])

        def squash(p):   # flatten vertically: the further from the x axis, the harder the squeeze
            return np.array([p[0], 3.0 * math.tanh(p[1] / 3.0), p[2]])   # tanh keeps it bounded

        say(cap, "apply_nonlinear_transformation(swirl)")
        self.apply_nonlinear_transformation(swirl, run_time=1.6)   # subdivide the plane first, then apply the function
        win.play(Wait(0.6))   # pause 0.6s

        say(cap, "apply_function(squash)")
        self.apply_function(squash, run_time=1.6)   # apply the function to every point directly
        win.play(Wait(0.6))   # pause 0.6s and finish
        win.close()   # close the RTM window


# ===== Sample 4: add_title / add_unit_square / add_vector / label ==========
class ComposeDemo(LinearTransformationScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # add_title / add_unit_square / add_vector call self.play internally, so wire it to the window first
        cap = Text("", font_size=26, color=YELLOW)   # put the caption at the bottom to make room for the title at the top
        cap.to_edge(DOWN)   # move the title to the bottom of the frame
        self.add(cap)   # add it to the scene

        say_low(cap, "add_title('Linear Transformation', animate=True)")
        self.add_title("Linear Transformation",   # the big top title (automatically gets a background bar and joins the foreground layer)
                       scale_factor=0.9, animate=True)   # with animate=True it plays Write internally
        win.play(Wait(0.7))   # pause 0.7s

        say_low(cap, "add_unit_square(animate=True)")
        self.add_unit_square(animate=True)   # draw the unit square (DrawBorderThenFill)
        win.play(Wait(0.5))   # pause 0.5s

        say_low(cap, "add_vector([2, 1], color=YELLOW, animate=True)")
        v = self.add_vector([2, 1], color=YELLOW, animate=True)   # add a vector and register it in moving_vectors
        win.play(Wait(0.6))   # pause 0.6s

        say_low(cap, "write_vector_coordinates(v)")
        self.write_vector_coordinates(v)   # write the column-matrix coordinates
        win.play(Wait(0.6))   # pause 0.6s

        say_low(cap, "add_transformable_label(v, 'w', ...)")
        self.add_transformable_label(v, "w",   # a label rewritten automatically on a transform
                                     transformation_name="L",
                                     label_scale_factor=0.8)
        win.play(Wait(0.6))   # pause 0.6s

        say_low(cap, "apply_matrix([[0, -1], [1, 0]])  rotate 90°")
        self.apply_matrix([[0, -1], [1, 0]], run_time=1.4)   # rotate 90°: the square turns vertical, the label is rewritten with the matrix
        win.play(Wait(0.7))   # pause 0.7s and finish
        win.close()   # close the RTM window


SCENES = [
    ("ctor_plain", LtsPlain),
    ("ctor_coords", LtsCoords),
    ("ctor_bgoff", LtsBgOff),
    ("ctor_ghost", LtsGhost),
    ("apply", ApplyDemo),
    ("nonlinear", NonlinearDemo),
    ("compose", ComposeDemo),
]

PAIRS = [
    ("05-LinearTransformationScene-ctor",
     ["ctor_plain", "ctor_coords", "ctor_bgoff", "ctor_ghost"]),
]


def concat(names, dst):
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    lst = os.path.join(HERE, "concat.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for n in names:
            p = os.path.join(OUT, n + ".mp4")
            f.write("file '%s'\n" % p.replace("\\", "/"))
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
