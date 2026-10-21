# -*- coding: utf-8 -*-
"""Full source for the two samples in 03-Special-Entrances.md (identical to the code blocks in the page).

Usage: python 03-Special-Entrances.py <clip name>...
With no arguments it renders every clip and concatenates the page's two sample videos (output to the parent assets/).
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
    Scene, Text, VGroup, Circle, Dot,
    TEAL_A, GREY_B, YELLOW, LEFT, UP, DOWN,
    Broadcast, FadeIn, Write, smooth,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: Broadcast, a 6-ring radar wave ============================
class BroadcastDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        title = Text("03-Broadcast", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        l1 = Text("Broadcast(ring, focal_point=ORIGIN, n_mobs=6,", font_size=30, color=GREY_B)
        l2 = Text("           initial_opacity=1.0, final_opacity=0.0, initial_width=0.2,", font_size=28, color=GREY_B)
        l3 = Text("           lag_ratio=0.3, run_time=2.4)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2, l3).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # signature label
        focal = Dot(point=DOWN * 1.4, radius=0.07, color=TEAL_A)   # emission centre
        ring = Circle(radius=2.0, color=TEAL_A).move_to(focal)   # the ring being broadcast
        win.play(FadeIn(sig, shift=DOWN), FadeIn(focal), run_time=0.4)   # fade in the label and the focal point
        win.play(Broadcast(ring, focal_point=focal.get_center(), n_mobs=6,   # parameter "focal_point / n_mobs"
                           initial_opacity=1.0, final_opacity=0.0, initial_width=0.2,   # parameter "opacity / initial_width"
                           lag_ratio=0.3, run_time=2.4))   # parameter "lag_ratio / run_time"
        win.play(Wait(0.6))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: Broadcast parameter comparison ============================
class BroadcastTunedDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        title = Text("03-BroadcastTuned", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        l1 = Text("Broadcast(ring, focal_point=SPOT, n_mobs=4,", font_size=30, color=GREY_B)
        l2 = Text("           initial_opacity=0.9, final_opacity=0.4, initial_width=0.5,", font_size=28, color=GREY_B)
        l3 = Text("           lag_ratio=0.5, run_time=2.2, rate_func=smooth)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2, l3).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # signature label
        spot = Dot(point=LEFT * 2.6 + DOWN * 1.4, radius=0.09, color=GREY_B)   # the new emission centre
        ring = Circle(radius=1.5, color=TEAL_A).move_to(spot)   # a smaller ring
        win.play(FadeIn(sig, shift=DOWN), FadeIn(spot), run_time=0.4)   # fade in the label and the focal point
        win.play(Broadcast(ring, focal_point=spot.get_center(), n_mobs=4,   # parameter "n_mobs=4" (fewer rings)
                           initial_opacity=0.9, final_opacity=0.4, initial_width=0.5,   # parameter "opacity / initial_width" (semi-transparent finish)
                           lag_ratio=0.5, run_time=2.2, rate_func=smooth))   # parameter "lag_ratio / rate_func"
        win.play(Wait(0.6))   # hold to see the result
        win.close()   # close the RTM window


SCENES = [
    ("broadcast", BroadcastDemo),
    ("broadcast_tuned", BroadcastTunedDemo),
]

PAIRS = [
    ("broadcast", ["broadcast"]),
    ("broadcast_tuned", ["broadcast_tuned"]),
]

PAGE = "03-Special-Entrances"


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
