# -*- coding: utf-8 -*-
"""Full source for the samples in 01-Quality-and-Output.md (identical to the code blocks in the page).

Usage: python 01-Quality-and-Output.py <clip names>...
With no arguments it renders every clip and concatenates the page's comparison videos.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
ASSETS = os.path.dirname(HERE)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import Scene, Square, Text, WHITE, UP, Create
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample: background_color ============================================
class BackgroundColorDemo(Scene):
    BG = "#12233a"    # background colour: change it to "#e8e4d8" and run again, the whole clear colour follows
    TXT = "#e8e4d8"   # label colour: a light background needs a dark colour to stay legible

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        self.camera.background_color = self.BG   # hand "background_color" to the camera: that is the clear colour
        label = Text("background_color = %s" % self.BG, font_size=38,
                     color=self.TXT).to_edge(UP)   # show the current background colour on screen
        sq = Square(side_length=2.0, color=WHITE).set_fill(WHITE, 0.8).set_stroke(width=4)   # white square: contrast against the background
        self.add(label)   # put the label into the scene
        win.play(Create(sq), run_time=0.8)   # draw the white square
        win.play(sq.animate.scale(1.25), run_time=0.6)   # scale the square up a little
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window


class BackgroundColorLight(BackgroundColorDemo):
    BG = "#e8e4d8"    # same scene, just swap "background_color" to off-white
    TXT = "#12233a"   # swap the label back to deep blue


SCENES = [
    ("bg_dark", BackgroundColorDemo),
    ("bg_light", BackgroundColorLight),
]

OUTPUTS = [
    ("01-Quality-and-Output-background_color", ["bg_dark", "bg_light"]),
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

    if not only:
        for out_name, names in OUTPUTS:
            dst = os.path.join(ASSETS, "RTM output", out_name + ".mp4")
            concat(names, dst)
            print("concat ->", dst, os.path.getsize(dst), "bytes")
