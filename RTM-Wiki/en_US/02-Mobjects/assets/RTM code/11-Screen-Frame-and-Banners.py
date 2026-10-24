# -*- coding: utf-8 -*-
"""Full source of the three samples in 11-Screen-Frame-and-Banners.md (identical to the code blocks in the page).

Usage: python 11-Screen-Frame-and-Banners.py <clip name>...
With no arguments it renders every clip and concatenates the page's three sample videos (output to the parent assets/).
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
    Scene, Square, Text, ScreenRectangle, FullScreenRectangle, ManimBanner,
    BLUE, GREEN, WHITE, BLACK, UP, DOWN, LEFT, RIGHT, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: ScreenRectangle =========================================
class ScreenRectDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        s1 = ScreenRectangle(height=2.6, color=BLUE)   # a mock screen generated at 16:9
        s1.shift(LEFT * 3.4)   # put it on the left
        s2 = ScreenRectangle(height=2.6, color=GREEN).next_to(s1, RIGHT, buff=0.5)   # a comparison on the right
        self.add(s1, s2)   # add to the scene
        print("s1 width, height =", round(s1.width, 2), round(s1.height, 2))   #16:9
        win.play(FadeIn(s1), FadeIn(s2), run_time=0.5)   # fade in
        s2.aspect_ratio = 1.0   # extra read/write property: becomes a square, height unchanged (takes effect instantly)
        print("s2 after =", round(s2.aspect_ratio, 2), round(s2.width, 2), round(s2.height, 2))   #1.0 2.6 2.6
        win.play(Wait(0.5))   # pause to see the result
        win.close()   # close the RTM window


# ===== Sample 2: FullScreenRectangle =====================================
class FullScreenDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        txt = Text("SCENE", font_size=48, color=WHITE)   # white text
        sq = Square(color=BLUE, side_length=1.5).shift(DOWN * 1.5)   # blue square
        self.add(txt, sq)   # add to the scene
        win.play(FadeIn(txt), FadeIn(sq), run_time=0.4)   # fade the content in
        mask = FullScreenRectangle(fill_opacity=0.7, color=BLACK)   # a dimming mask covering the whole screen
        self.add(mask)   # add to the scene
        win.play(FadeIn(mask), run_time=0.5)   # the mask fades in: the whole screen dims
        win.play(Wait(0.4))   # pause to see the mask effect
        self.remove(mask)   # take the mask off
        win.play(Wait(0.3))   # pause 0.3s
        win.close()   # close the RTM window


# ===== Sample 3: ManimBanner =============================================
class BannerDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        banner = ManimBanner(dark_theme=True)   # dark-theme banner
        banner.scale(0.8)   # must use the overridden scale: it scales the not-yet-mounted letter group in step
        banner.to_edge(DOWN, buff=0.8)   # put it at the bottom
        print("font_color =", banner.font_color, "| scale_factor =", banner.scale_factor)   # common attributes
        self.add(banner)   # add to the scene
        win.play(banner.create(run_time=1.2))   # logo shape spins in + letter M fades in
        win.play(banner.expand(run_time=1.0, direction="center"))   # expand into the full "manim" banner
        try:
            banner.expand(direction="up")   # an illegal direction raises ValueError
        except ValueError as exc:
            print("expand illegal direction ->", str(exc)[:50])
        print("anim attribute =", getattr(banner, "anim", None) is not None)   # anim is mounted only after expanding
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window


SCENES = [
    ("screen_rect", ScreenRectDemo),
    ("fullscreen", FullScreenDemo),
    ("banner", BannerDemo),
]

PAIRS = [
    ("screen_rect", ["screen_rect"]),
    ("fullscreen", ["fullscreen"]),
    ("banner", ["banner"]),
]

PAGE = "11-Screen-Frame-and-Banners"


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
