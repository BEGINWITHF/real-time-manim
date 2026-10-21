# -*- coding: utf-8 -*-
"""Full source of the five samples in 02-Displaying-Content.md (identical to the code blocks in the page).

Usage: python 02-Displaying-Content.py <scene name>...
With no arguments it renders every clip and concatenates the page's five videos (RTM version).
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    Scene,
    Square, Circle, Triangle, Dot, Text,
    BLUE, RED, GREEN, YELLOW, ORANGE, WHITE,
    UP, DOWN, LEFT, RIGHT,
    FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: Scene.add =================================================
class AddDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim scene named "self" to the RTM window named "win"
        back = Square(color=BLUE, side_length=2.5)   #the first square added
        mid = Circle(color=RED, radius=1.6)   #the second circle added
        top = Triangle(color=YELLOW).scale(1.3).shift(RIGHT * 2.2)   #the third triangle added
        self.add(back)   #earlier additions are drawn at the bottom
        self.add(mid, top)   #later additions cover them; you can pass several at once
        self.add(Text("add order = paint order", font_size=36, color=WHITE).to_edge(UP))   #the text added last is on top
        win.play(Wait(0.5))   #hold 0.5s to see who covers whom
        win.play(FadeIn(Square(color=GREEN, side_length=1.2)), run_time=0.5)   #an object newly added by an animation goes straight to the top
        win.play(Wait(0.5))   #wait another 0.5s
        win.close()   #close the RTM window


# ===== Sample 2: Scene.remove ==============================================
class RemoveDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim scene named "self" to the RTM window named "win"
        back = Square(color=BLUE, side_length=2.5)   #the covered square
        front = Circle(color=RED, radius=1.6)   #the circle on top
        self.add(back, front)   #put the circle covering the square on screen
        win.play(Wait(0.5))   #first see clearly that "the circle covers the square"
        self.remove(front)   #take the circle off screen, revealing the square underneath
        win.play(Wait(0.5))   #wait another 0.5s to see the effect
        win.close()   #close the RTM window


# ===== Sample 3: Scene.clear ===============================================
class ClearDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim scene named "self" to the RTM window named "win"
        self.add(Square(color=BLUE, side_length=2).shift(LEFT * 2))   #put up a square
        self.add(Circle(color=RED, radius=1.2).shift(RIGHT * 2))   #put up a circle
        self.add(Text("before clear", font_size=40, color=YELLOW).to_edge(UP))   #add a title
        win.play(Wait(0.5))   #first see what's on screen
        self.clear()   #one-key clear: both mobjects and foreground_mobjects go off screen
        self.add(Text("after clear", font_size=40, color=GREEN).to_edge(UP))   #put up a new title
        win.play(Wait(0.5))   #only the new title remains on screen
        win.close()   #close the RTM window


# ===== Sample 4: bring_to_front / bring_to_back / foreground ===============
class ZorderDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   #the on-top rule re-sorts objects inside win.play, so wire it up first
        blue = Square(color=BLUE, side_length=2.2).shift(LEFT * 0.6)   #the blue square added first
        red = Square(color=RED, side_length=2.2).shift(RIGHT * 0.6)   #the red square added later, covering the blue
        title = Text("z-order", font_size=40, color=YELLOW).to_edge(UP)   #the title to put on top
        self.add(blue, red)   #red above, blue below
        win.play(Wait(0.5))
        self.bring_to_front(blue)   #move the blue square to the top
        win.play(Wait(0.5))
        self.bring_to_back(blue)   #push the blue square back to the bottom
        win.play(Wait(0.5))
        self.add(title)   #put the title on screen as an ordinary object first
        sweep = Circle(color=GREEN, radius=2.8, fill_opacity=1).shift(LEFT * 9 + UP * 3.5)   #a solid big circle that will sweep across the title
        self.add(sweep)   #the circle added later, covering the title
        win.play(sweep.animate.shift(RIGHT * 8), run_time=0.8)   #the big circle sweeps across and covers the title
        self.add_foreground_mobject(title)   #register the title as foreground: it floats straight to the top
        win.play(Wait(0.5))   #hold 0.5s: the title covers the circle
        self.remove_foreground_mobject(title)   #unregister the foreground; but the title was already moved to the end of the list by add, so it is still on top
        self.bring_to_back(title)   #to get back down you still have to push it back yourself
        win.play(Wait(0.5))   #hold 0.5s: the title is covered by the circle again
        win.close()   #close the RTM window


# ===== Sample 5: Scene.replace + query utilities ===========================
class ReplaceDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim scene named "self" to the RTM window named "win"
        tri = Triangle(color=GREEN).scale(1.3).shift(LEFT * 2.5)   #the triangle to be replaced
        dot = Dot(color=RED, radius=0.35).shift(RIGHT * 2.5)   #the red dot beside it, as a control
        self.add(tri, dot)   #put both objects on screen
        print("before replace: top-level = %d" % len(self.get_top_level_mobjects()))   #query utility get_top_level_mobjects
        win.play(Wait(0.5))
        self.replace(tri, Square(color=ORANGE, side_length=1.8).shift(LEFT * 2.5))   #swap the triangle for a square in place
        print("after replace: top-level = %d" % len(self.get_top_level_mobjects()))   #the count is unchanged; it is just replaced in place
        win.play(Wait(0.5))
        win.close()   #close the RTM window


PAGE = "02-Displaying-Content"

SCENES = [
    ("add", AddDemo),
    ("remove", RemoveDemo),
    ("clear", ClearDemo),
    ("zorder", ZorderDemo),
    ("replace", ReplaceDemo),
]

SAMPLES = [
    ("add", ["add"]),
    ("remove", ["remove"]),
    ("clear", ["clear"]),
    ("zorder", ["zorder"]),
    ("replace", ["replace"]),
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
        for out_name, names in SAMPLES:
            dst = os.path.join(ASSETS, "RTM output", "%s-%s.mp4" % (PAGE, out_name))
            concat(names, dst)
            print("concat ->", dst, os.path.getsize(dst), "bytes")
            if len(names) > 1:
                #multi-clip sample: copy each clip into assets/ too, for segment-by-segment comparison
                for n in names:
                    shutil.copyfile(os.path.join(OUT, n + ".mp4"),
                                    os.path.join(ASSETS, "%s-%s.mp4" % (PAGE, n)))
