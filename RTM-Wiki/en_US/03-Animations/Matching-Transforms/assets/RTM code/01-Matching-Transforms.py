# -*- coding: utf-8 -*-
"""Full source of the four samples in 01-Matching-Transforms.md (word for word identical to the code blocks on the page).

Usage: python 01-Matching-Transforms.py <clip-name>...
With no arguments it renders every clip and concatenates the four sample videos shown on the page (written to the parent assets/).
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
    GREY_B,
    YELLOW,
    DOWN,
    LEFT,
    UP,
    PI,
    FadeIn,
    FadeOut,
    MathTex,
    Scene,
    Text,
    VGroup,
    Write,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    TransformMatchingShapes,
    TransformMatchingTex,
    Wait,
)
from real_time_manim.record import fast_record_scene


# ===== Sample 1: Shapes' default same-shape matching ========================
class ShapesDefaultDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-ShapesDefault", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l1 = Text("TransformMatchingShapes(src, tar, transform_mismatches=False,",
                  font_size=28, color=GREY_B)
        l2 = Text("    fade_transform_mismatches=False, key_map=None, path_arc=PI/2)",
                  font_size=28, color=GREY_B)
        lab1 = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # two-line signature label
        src = Text("the morse code", font_size=44).next_to(lab1, DOWN, buff=0.8)   # source: the sentence to rearrange
        tar = Text("here come dots", font_size=44).move_to(src)   # target: the rearranged sentence
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)   # label fades in from below
        self.add(src)   # add the source to the scene first (it is removed when finished and the target takes over)
        win.play(
            TransformMatchingShapes(                # parameter "mobject" (source, removed when finished)
                src,
                tar,                                # parameter "target_mobject" (takes over the scene when finished)
                transform_mismatches=False,         # parameter "transform_mismatches": False, differently-shaped parts fade out and in
                fade_transform_mismatches=False,    # parameter "fade_transform_mismatches": False
                key_map=None,                       # parameter "key_map": None, no manual pairing
                path_arc=PI / 2,                    # parameter "path_arc" (**kwargs): same-shape parts travel along an arc
            ),
            run_time=2.6,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


# ===== Sample 2: transform_mismatches=True forcing a deformation ============
class ShapesMismatchDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-ShapesMismatch", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l3 = Text("TransformMatchingShapes(src, tar, transform_mismatches=True, ...)",
                  font_size=28, color=GREY_B).next_to(title, DOWN, buff=0.4)   # signature label
        src2 = Text("the morse code", font_size=44).next_to(l3, DOWN, buff=0.8)   # source: the sentence to rearrange
        tar2 = Text("here come dots", font_size=44).move_to(src2)   # target: the rearranged sentence
        win.play(FadeIn(l3, shift=DOWN), run_time=0.4)   # label fades in from below
        self.add(src2)   # add the source to the scene first (it is removed when finished and the target takes over)
        win.play(
            TransformMatchingShapes(                # parameter "mobject" (source, removed when finished)
                src2,
                tar2,                               # parameter "target_mobject" (takes over the scene when finished)
                transform_mismatches=True,          # parameter "transform_mismatches": True, differently-shaped parts are forcibly deformed too
                fade_transform_mismatches=False,    # parameter "fade_transform_mismatches": False
                key_map=None,                       # parameter "key_map": None, no manual pairing
                path_arc=PI / 2,                    # parameter "path_arc" (**kwargs): same-shape parts travel along an arc
            ),
            run_time=2.4,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


# ===== Sample 3: key_map manual key pairing =================================
class ShapesKeyMapDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-ShapesKeyMap", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l4 = Text("key_map = {shape_key('c'): shape_key('h')}  # manual key pairing",
                  font_size=28, color=GREY_B).next_to(title, DOWN, buff=0.4)   # signature label
        l5 = Text("TransformMatchingShapes(cat, hat, key_map=key_map, ...)",
                  font_size=28, color=GREY_B).next_to(l4, DOWN, buff=0.06)   # second signature line
        lab2 = VGroup(l4, l5)
        src3 = Text("cat", font_size=52, color=GREY_B).next_to(lab2, DOWN, buff=0.8).shift(LEFT * 2.0)   # source word cat
        tar3 = Text("hat", font_size=52, color=GREY_B).move_to(src3)   # target word hat (only the first letter changes)
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)   # label fades in from below
        self.add(src3)   # add the source to the scene first (it is removed when finished and the target takes over)
        key_map = {
            TransformMatchingShapes.get_mobject_key(src3[0]):   # the shape key of the source letter "c"
            TransformMatchingShapes.get_mobject_key(tar3[0]),   # the shape key of the target letter "h"
        }
        win.play(
            TransformMatchingShapes(                # parameter "mobject" (source, removed when finished)
                src3,
                tar3,                               # parameter "target_mobject" (takes over the scene when finished)
                transform_mismatches=False,         # parameter "transform_mismatches": False
                fade_transform_mismatches=False,    # parameter "fade_transform_mismatches": False
                key_map=key_map,                    # parameter "key_map" ("c" -> "h" forced pairing)
                path_arc=PI / 2,                    # parameter "path_arc" (**kwargs): same-shape parts travel along an arc
            ),
            run_time=2.4,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


# ===== Sample 4: TransformMatchingTex fade contrasted with the default ======
class MatchingTexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-MatchingTex", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l6 = Text("TransformMatchingTex(eq1, eq2, transform_mismatches=False,",
                  font_size=28, color=GREY_B)
        l7 = Text("    fade_transform_mismatches=True, key_map=None)",
                  font_size=28, color=GREY_B)
        lab3 = VGroup(l6, l7).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # two-line signature label
        eq1 = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2").next_to(lab3, DOWN, buff=0.8)   # source formula x²+y²=z²
        eq2 = MathTex("{{x}}^2", "=", "{{z}}^2", "-", "{{y}}^2").move_to(eq1)   # target formula x²=z²−y²
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)   # label fades in from below
        self.add(eq1)   # add the source formula to the scene first (it is removed when finished and the target takes over)
        win.play(
            TransformMatchingTex(                  # parameter "mobject" (source, removed when finished)
                eq1,
                eq2,                                # parameter "target_mobject" (takes over the scene when finished)
                transform_mismatches=False,         # parameter "transform_mismatches": False
                fade_transform_mismatches=True,     # parameter "fade_transform_mismatches": True, differently-shaped parts use FadeTransformPieces
                key_map=None,                       # parameter "key_map": None, no manual pairing
            ),
            run_time=2.4,
        )
        # comparison against the same transform's default behaviour: differently-shaped parts fade out / in directly
        eq3 = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2").move_to(eq1)   # comparison: the source formula is swapped back
        eq4 = MathTex("{{x}}^2", "=", "{{z}}^2", "-", "{{y}}^2").move_to(eq1)   # comparison: the same target formula
        l8 = Text("(default) transform_mismatches=False, fade_transform_mismatches=False",
                  font_size=28, color=GREY_B).next_to(title, DOWN, buff=0.4)   # comparison label
        win.play(FadeOut(VGroup(lab3, eq2)), FadeIn(l8, shift=DOWN), run_time=0.5)   # swap the label and let the result give way
        self.add(eq3)   # add the comparison's source formula to the scene
        win.play(
            TransformMatchingTex(                  # parameter "mobject" (source, removed when finished)
                eq3,
                eq4,                                # parameter "target_mobject" (takes over the scene when finished)
                transform_mismatches=False,         # parameter "transform_mismatches": False
                fade_transform_mismatches=False,    # parameter "fade_transform_mismatches": False, differently-shaped parts fade out and in directly
                key_map=None,                       # parameter "key_map": None, no manual pairing
            ),
            run_time=2.4,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window


SCENES = [
    ("shapes_default", ShapesDefaultDemo),
    ("shapes_mismatch", ShapesMismatchDemo),
    ("shapes_keymap", ShapesKeyMapDemo),
    ("tex", MatchingTexDemo),
]

PAIRS = [
    ("shapes_default", ["shapes_default"]),
    ("shapes_mismatch", ["shapes_mismatch"]),
    ("shapes_keymap", ["shapes_keymap"]),
    ("tex", ["tex"]),
]

PAGE = "01-Matching-Transforms"


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
