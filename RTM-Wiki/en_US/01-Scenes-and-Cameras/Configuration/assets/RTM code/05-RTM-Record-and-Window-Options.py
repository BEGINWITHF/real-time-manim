# -*- coding: utf-8 -*-
"""Full source for the samples in 05-RTM-Record-and-Window-Options.md (identical to the code blocks in the page).

The samples on this page demonstrate the parameters of the record functions / the window; the page quotes them verbatim including the call lines.

Usage: python 05-RTM-Record-and-Window-Options.py               # render everything + concatenate
       python 05-RTM-Record-and-Window-Options.py fps mlwindow  # render only the given samples
       python 05-RTM-Record-and-Window-Options.py probes        # run the parameter probes that produce no video
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

from real_time_manim import Scene, Square, Text, BLUE, YELLOW, UP, Create
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene, record_scene

if __name__ == "__main__":
    os.chdir(OUT)   # below all out_path values are written as relative file names, all landing in the final/ directory


# ===== Sample: the three forms of scene ====================================
class SceneFormDemo(Scene):
    TAG = "scene = class"   # passing style: class / instance / no-arg callable

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        label = Text(self.TAG, font_size=40, color=YELLOW).to_edge(UP)   # show the current passing style on screen
        sq = Square(side_length=1.8, color=BLUE).set_fill(BLUE, 0.5).set_stroke(width=4)   # blue square
        self.add(label)   # put the label into the scene
        win.play(Create(sq), run_time=0.8)   # draw the square
        win.play(sq.animate.scale(1.2), run_time=0.6)   # scale the square up
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window


class SceneFormInstance(SceneFormDemo):
    TAG = "scene = instance"   # same scene, changed to the instance form


class SceneFormCallable(SceneFormDemo):
    TAG = "scene = callable"   # same scene, changed to the no-arg callable form


def run_callable():
    SceneFormCallable().construct()   # no-arg callable form: a function that takes no arguments, runs the scene to completion


if __name__ == "__main__" and ("scene_forms" in sys.argv[1:] or not sys.argv[1:]):
    fast_record_scene(SceneFormDemo, out_path="scene_class.mp4", verbose=True)   # class: the most common form
    fast_record_scene(SceneFormInstance(), out_path="scene_instance.mp4", verbose=True)   # instance: build it yourself and pass it
    fast_record_scene(run_callable, out_path="scene_callable.mp4", verbose=True)   # no-arg callable: the whole flow is written by you


# ===== Sample: out_path ====================================================
class OutPathDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        label = Text("out_path = clips/demo.mp4", font_size=38,
                     color=YELLOW).to_edge(UP)   # show the output path on screen
        sq = Square(side_length=1.8, color=BLUE).set_fill(BLUE, 0.5).set_stroke(width=4)   # blue square
        self.add(label)   # put the label into the scene
        win.play(Create(sq), run_time=0.8)   # draw the square
        win.play(sq.animate.scale(1.2), run_time=0.6)   # scale the square up
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window


if __name__ == "__main__" and ("out_path" in sys.argv[1:] or not sys.argv[1:]):
    fast_record_scene(OutPathDemo, out_path="clips/demo.mp4", verbose=True)   # out_path gives the file path directly, subdirectories are created automatically


# ===== Sample: fps =========================================================
class FpsDemo(Scene):
    FPS = 30   # requested frame rate: change it to 60 and the forced correction is not triggered

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        label = Text("fps = %d" % self.FPS, font_size=40, color=YELLOW).to_edge(UP)   # show the requested frame rate on screen
        sq = Square(side_length=1.8, color=BLUE).set_fill(BLUE, 0.5).set_stroke(width=4)   # blue square
        self.add(label)   # put the label into the scene
        win.play(Create(sq), run_time=0.8)   # draw the square
        win.play(sq.animate.scale(1.2), run_time=0.6)   # scale the square up
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window


class FpsDemo60(FpsDemo):
    FPS = 60   # same scene, requests 60 fps


if __name__ == "__main__" and ("fps" in sys.argv[1:] or not sys.argv[1:]):
    fast_record_scene(FpsDemo, out_path="fps_30.mp4", fps=30, verbose=True)   # fps=30: prints "[rtm] forcing 60 fps" and then renders anyway
    fast_record_scene(FpsDemo60, out_path="fps_60.mp4", fps=60, verbose=True)   # fps=60: does not trigger the hint


# ===== Sample: MLWindow's w / h / hidden ===================================
class MLWindowDemo(Scene):
    SIZE = "MLWindow(960, 540)  hidden=True"   # window parameters: size + whether hidden
    W, H = 960, 540   # window size: any other value is force-corrected to 1920x1080

    def construct(self):
        win = MLWindow(self.W, self.H)   # create an RTM window: "w" / "h" are exactly these two parameters
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        label = Text(self.SIZE, font_size=38, color=YELLOW).to_edge(UP)   # show this set of window parameters on screen
        sq = Square(side_length=1.8, color=BLUE).set_fill(BLUE, 0.5).set_stroke(width=4)   # blue square
        self.add(label)   # put the label into the scene
        win.play(Create(sq), run_time=0.8)   # draw the square
        win.play(sq.animate.scale(1.2), run_time=0.6)   # scale the square up
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window


class MLWindowBig(MLWindowDemo):
    SIZE = "MLWindow(3840, 2160)  hidden=False"   # request 4K + visible window: still force-corrected to 1920x1080
    W, H = 3840, 2160   # 4K size: only used to trigger the forced-correction hint


if __name__ == "__main__" and ("mlwindow" in sys.argv[1:] or not sys.argv[1:]):
    fast_record_scene(MLWindowDemo, out_path="mlwin_small.mp4", hidden=True, verbose=True)   # hidden=True: the window never pops up
    fast_record_scene(MLWindowBig, out_path="mlwin_big.mp4", hidden=False, verbose=True)   # hidden=False: pop up a window while rendering


# ===== Sample: record_scene ================================================
class RecordSceneDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        label = Text("record_scene = live window", font_size=38,
                     color=YELLOW).to_edge(UP)   # live recording: the window is visible
        sq = Square(side_length=1.8, color=BLUE).set_fill(BLUE, 0.5).set_stroke(width=4)   # blue square
        self.add(label)   # put the label into the scene
        win.play(Create(sq), run_time=0.8)   # draw the square
        win.play(sq.animate.scale(1.2), run_time=0.6)   # scale the square up
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window


if __name__ == "__main__" and ("record_scene" in sys.argv[1:] or not sys.argv[1:]):
    record_scene(RecordSceneDemo, out_path="record_scene.mp4", fps=60, verbose=True)   # live visible-window recording: pop up a window, run by real time


# ===== Parameters that produce no video: count_only / segment / overwrite / cleanup / verbose ==
if __name__ == "__main__" and "probes" in sys.argv[1:]:
    result = fast_record_scene(FpsDemo, out_path="probe_count.mp4", count_only=True, verbose=True)   # count_only: count frames only, no capture and no file
    print("count_only return value: ", result)   # out_path is returned as usual, but the file is not on disk
    fast_record_scene(FpsDemo, out_path="probe_bmp", segment=(0, 30), verbose=True)   # segment: export a BMP directory by frame range, not an MP4
    fast_record_scene(FpsDemo, out_path="probe_clean.mp4", cleanup=False, verbose=True)   # cleanup=False: keep manim's media/ directory
    try:
        fast_record_scene(FpsDemo, out_path="probe_clean.mp4", overwrite=False, verbose=True)   # overwrite=False: error if the target already exists
    except FileExistsError as exc:
        print("overwrite=False error: ", exc)   # FileExistsError: target already exists
    fast_record_scene(FpsDemo, out_path="probe_quiet.mp4", verbose=False)   # verbose=False: don't print progress lines


OUTPUTS = [
    ("05-RTM-Record-and-Window-Options-scene_forms", ["scene_class", "scene_instance", "scene_callable"]),
    ("05-RTM-Record-and-Window-Options-out_path", ["clips/demo"]),
    ("05-RTM-Record-and-Window-Options-fps", ["fps_30", "fps_60"]),
    ("05-RTM-Record-and-Window-Options-mlwindow", ["mlwin_small", "mlwin_big"]),
    ("05-RTM-Record-and-Window-Options-record_scene", ["record_scene"]),
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


if __name__ == "__main__" and not sys.argv[1:]:
    for out_name, names in OUTPUTS:
        dst = os.path.join(ASSETS, "RTM output", out_name + ".mp4")
        concat(names, dst)
        print("concat ->", dst, os.path.getsize(dst), "bytes")
