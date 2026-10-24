# -*- coding: utf-8 -*-
"""Full source for the samples in 03-Paths-and-Windows.md (identical to the code blocks in the page).

Usage: python 03-Paths-and-Windows.py <clip names>...
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import Scene, Text, VGroup, ORANGE, GREY_B, UP, DOWN, LEFT, Write, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample: config_to_rtm ===============================================
class ConfigToRtmDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        title = Text("config  ->  RTM", font_size=42, color=ORANGE).to_edge(UP, buff=0.7)   # title line
        rows = VGroup(
            Text("media_dir / video_dir  ->  out_path = my.mp4", font_size=30, color=GREY_B),
            Text("window_size / window_position  ->  MLWindow(w, h)", font_size=30, color=GREY_B),
            Text("fullscreen / force_window  ->  hidden", font_size=30, color=GREY_B),
            Text("preview  ->  hidden=False", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT).next_to(title, DOWN, buff=0.7)   # lay out the four rows
        self.add(title)   # put the title into the scene
        win.play(Write(title), run_time=0.7)   # write the title
        for row in rows:   # bring the correspondence rows onto the screen one by one
            win.play(FadeIn(row, shift=UP * 0.15), run_time=0.4)   # fade in one row
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window


SCENES = [
    ("config_to_rtm", ConfigToRtmDemo),
]

OUTPUTS = [
    ("03-Paths-and-Windows-config_to_rtm", ["config_to_rtm"]),
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
