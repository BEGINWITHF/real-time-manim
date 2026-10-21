# -*- coding: utf-8 -*-
"""Full source for the samples in 04-ManimCE-CLI-Cheat-Sheet.md (identical to the code blocks in the page).

This page is the only page in the whole wiki allowed to contain ManimCE content; the samples also draw the CLI cheat sheet.

Usage: python 04-ManimCE-CLI-Cheat-Sheet.py <clip names>...
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

from manim import (
    Scene, Text, VGroup,
    ORANGE, GREY_B, YELLOW, GREEN, UP, DOWN, LEFT,
    Write, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: quality tiers =============================================
class QualityTiersDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        rows = VGroup(
            Text("-ql    854x480 @ 15", font_size=32, color=GREY_B),
            Text("-qm    1280x720 @ 30", font_size=32, color=GREY_B),
            Text("-qh    1920x1080 @ 60", font_size=32, color=YELLOW),
            Text("-qp    2560x1440 @ 60", font_size=32, color=GREY_B),
            Text("-qk    3840x2160 @ 60", font_size=32, color=GREY_B),
        ).arrange(DOWN, buff=0.28, aligned_edge=LEFT)   # lay out the five quality tiers top to bottom
        note = Text("RTM = 1920x1080 @ 60 only", font_size=34,
                    color=ORANGE).to_edge(DOWN, buff=0.7)   # RTM has only this one tier
        self.add(rows)   # put the five quality tiers into the scene
        win.play(FadeIn(rows, shift=UP * 0.2), run_time=0.8)   # fade in the five quality tiers
        win.play(Write(note), run_time=0.7)   # write out RTM's fixed tier
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window


# ===== Sample 2: command line <-> RTM call =================================
class CliEquivDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        cli = Text("manim -qh -o my_video --fps 60 scene.py Hello",
                   font_size=30, color=ORANGE).shift(UP * 1.2)   # the ManimCE command line
        same = Text("same output", font_size=26, color=GREY_B)   # the note between the two lines
        call = Text("fast_record_scene(Hello, out_path='my_video.mp4', fps=60)",
                    font_size=30, color=GREEN).shift(DOWN * 1.2)   # the RTM function call
        self.add(cli, same, call)   # put the three lines of text into the scene
        win.play(FadeIn(cli, shift=UP * 0.2), run_time=0.6)   # first the command line
        win.play(FadeIn(same), run_time=0.4)   # then the note in the middle
        win.play(FadeIn(call, shift=DOWN * 0.2), run_time=0.6)   # finally the RTM call
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window


SCENES = [
    ("quality_tiers", QualityTiersDemo),
    ("cli_equiv", CliEquivDemo),
]

OUTPUTS = [
    ("04-ManimCE-CLI-Cheat-Sheet-quality_tiers", ["quality_tiers"]),
    ("04-ManimCE-CLI-Cheat-Sheet-cli_equiv", ["cli_equiv"]),
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
