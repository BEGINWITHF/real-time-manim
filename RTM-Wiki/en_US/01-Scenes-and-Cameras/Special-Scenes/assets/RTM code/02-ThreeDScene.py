# -*- coding: utf-8 -*-
"""Full source for the five samples in 02-ThreeDScene.md (identical to the code blocks in the page).

Usage: python 02-ThreeDScene.py <clip names>...
With no arguments it renders all 7 clips and concatenates the page's first comparison video (ctor).
"""
import os
import subprocess
import sys
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
ASSETS = os.path.dirname(HERE)
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    BLUE, GREEN, YELLOW, UP, DOWN, DEGREES, ORIGIN, FadeIn,
    Line, Text, ThreeDAxes, Cube, VGroup, VectorizedPoint, config,
    ThreeDScene, SpecialThreeDScene,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


def say(cap, text):   # instantly swap the top caption text without spending animation time
    cap.become(Text(text, font_size=30, color=YELLOW).to_edge(UP))


# ===== Sample 1: ThreeDScene constructor parameters, set_to_default_angled_camera_orientation =
class CtorDefault(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # scene methods call self.play internally, so wire it to the window first
        axes = ThreeDAxes()   # default 3D axes
        cube = Cube(side_length=1.5).set_color(BLUE)   # a blue cube as a reference
        cap = Text("", font_size=30, color=YELLOW)   # top caption text (content swapped later)
        self.add_fixed_in_frame_mobjects(cap)   # pin the title to the screen so it faces the viewer however the view turns
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(axes, cube, cap)   # add the axes, the cube and the title to the scene
        say(cap, "default phi=0° theta=0°")   # nothing passed: the start is the straight-on view
        win.play(FadeIn(cube), run_time=0.5)   # fade in the cube
        win.play(Wait(1.4))   # pause 1.4s to see the default view
        self.set_to_default_angled_camera_orientation()   # apply the stored default angled view {phi:70°, theta:-135°}
        say(cap, "set_to_default_angled_camera_orientation()")
        win.play(Wait(1.6))   # jump to manim's classic oblique view
        win.close()   # close the RTM window


class CtorAngled(ThreeDScene):
    def __init__(self, **kwargs):
        # the constructor parameter is only stored into self.default_angled_camera_orientation_kwargs; nobody uses it on their own
        super().__init__(
            default_angled_camera_orientation_kwargs=
            {"phi": 60 * DEGREES, "theta": -45 * DEGREES}, **kwargs)

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # scene methods call self.play internally, so wire it to the window first
        axes = ThreeDAxes()   # default 3D axes
        cube = Cube(side_length=1.5).set_color(BLUE)   # a blue cube as a reference
        cap = Text("", font_size=30, color=YELLOW)   # top caption text (content swapped later)
        self.add_fixed_in_frame_mobjects(cap)   # pin the title to the screen
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(axes, cube, cap)   # add the axes, the cube and the title to the scene
        say(cap, "ctor kwarg stored ... view unchanged")   # a constructor parameter was passed, but nobody reads it
        win.play(FadeIn(cube), run_time=0.5)   # fade in the cube
        win.play(Wait(1.4))   # still the straight-on view: passing the parameter alone has no effect
        self.set_to_default_angled_camera_orientation()   # only calling this method reads and applies it
        say(cap, "set_to_default_angled_camera_orientation()")
        win.play(Wait(1.6))   # this time it jumps to the custom phi=60° theta=-45°
        win.close()   # close the RTM window


class CtorAmbient(ThreeDScene):
    def __init__(self, **kwargs):
        # this constructor parameter is likewise only stored into self.ambient_camera_rotation; nobody in the library reads it (upstream is like this)
        super().__init__(ambient_camera_rotation={"theta": 0.15}, **kwargs)

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # scene methods call self.play internally, so wire it to the window first
        axes = ThreeDAxes()   # default 3D axes
        cube = Cube(side_length=1.5).set_color(BLUE)   # a blue cube as a reference
        cap = Text("", font_size=30, color=YELLOW)   # top caption text (content swapped later)
        self.add_fixed_in_frame_mobjects(cap)   # pin the title to the screen
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(axes, cube, cap)   # add the axes, the cube and the title to the scene
        self.set_camera_orientation(phi=65 * DEGREES, theta=-90 * DEGREES)   # set an oblique view first so you can tell whether it rotates
        say(cap, "ambient_camera_rotation ... no effect")
        win.play(FadeIn(cube), run_time=0.5)   # fade in the cube
        win.play(Wait(1.5))   # the frame does not budge: nobody reads this parameter
        self.begin_ambient_camera_rotation(rate=0.15)   # ambient rotation only works through the method
        say(cap, "begin_ambient_camera_rotation(rate=0.15)")
        win.play(Wait(1.5))   # now it starts turning
        self.stop_ambient_camera_rotation()   # stop
        win.play(Wait(0.3))   # pause 0.3s and finish
        win.close()   # close the RTM window


# ===== Sample 2: set_camera_orientation / move_camera ======================
class OrientationDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        axes = ThreeDAxes()   # default 3D axes
        cube = Cube(side_length=1.5).set_color(BLUE)   # a blue cube as a reference
        cap = Text("", font_size=30, color=YELLOW)   # top caption text (content swapped later)
        self.add_fixed_in_frame_mobjects(cap)   # pin the title to the screen
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(axes, cube, cap)   # add the three objects to the scene

        say(cap, "set_camera_orientation phi=30° theta=-60°")
        self.set_camera_orientation(phi=30 * DEGREES, theta=-60 * DEGREES)   # jump to a new view instantly, no animation
        win.play(Wait(0.8))   # pause 0.8s to see the result

        say(cap, "move_camera phi=70° theta=-45°")
        self.move_camera(phi=70 * DEGREES, theta=-45 * DEGREES, run_time=1.2)   # animate the orbit to the new phi/theta
        win.play(Wait(0.3))   # pause 0.3s

        say(cap, "move_camera gamma=25°")
        self.move_camera(gamma=25 * DEGREES, run_time=0.8)   # roll the frame 25° about the view axis
        win.play(Wait(0.3))   # pause 0.3s

        say(cap, "move_camera zoom=1.8")
        self.move_camera(zoom=1.8, run_time=0.8)   # zoom in to 1.8x
        win.play(Wait(0.3))   # pause 0.3s

        say(cap, "move_camera frame_center=cube")
        self.move_camera(frame_center=cube, run_time=0.8)   # move the frame centre onto the cube
        win.play(Wait(0.6))   # pause 0.6s

        say(cap, "set_camera_orientation reset all")
        self.set_camera_orientation(phi=70 * DEGREES, theta=-135 * DEGREES,   # reset phi/theta/gamma/zoom in one step
                                    gamma=0, zoom=1, frame_center=ORIGIN)
        win.play(Wait(0.5))   # pause 0.5s and finish
        win.close()   # close the RTM window


# ===== Sample 3: begin/stop_ambient_camera_rotation, 3dillusion ============
class RotationDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # scene methods call self.play internally, so wire it to the window first
        axes = ThreeDAxes()   # default 3D axes
        cube = Cube(side_length=1.5).set_color(BLUE)   # a blue cube as a reference
        cap = Text("", font_size=30, color=YELLOW)   # top caption text (content swapped later)
        self.add_fixed_in_frame_mobjects(cap)   # pin the title to the screen
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(axes, cube, cap)   # add the three objects to the scene
        self.set_camera_orientation(phi=60 * DEGREES, theta=-90 * DEGREES)   # set an oblique view first

        say(cap, "ambient rate=0.15 about=theta")
        self.begin_ambient_camera_rotation(rate=0.15, about="theta")   # orbit steadily about the vertical axis, 0.15 radians per second
        win.play(Wait(1.6))   # keep waiting while it turns, so the frame keeps rotating
        self.stop_ambient_camera_rotation()   # stop (about must match the one passed to begin)

        say(cap, "ambient rate=0.2 about=phi")
        self.begin_ambient_camera_rotation(rate=0.2, about="phi")   # switch to turning about the polar-angle direction
        win.play(Wait(1.6))   # keep waiting while it turns
        self.stop_ambient_camera_rotation(about="phi")   # stop

        say(cap, "3dillusion rate=1")
        self.begin_3dillusion_camera_rotation(rate=1)   # wobble slightly around the current view for a sense of depth
        win.play(Wait(1.6))   # keep waiting while it wobbles
        self.stop_3dillusion_camera_rotation()   # stop
        win.play(Wait(0.3))   # pause 0.3s and finish
        win.close()   # close the RTM window


# ===== Sample 4: fixed_in_frame / fixed_orientation ========================
class FixedDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        axes = ThreeDAxes()   # default 3D axes
        cube = Cube(side_length=1.2).set_color(BLUE)   # a blue cube as a reference
        title = Text("fixed_in_frame", font_size=34, color=YELLOW)   # title demonstrating screen pinning
        tag = Text("fixed_orientation", font_size=26, color=GREEN)   # label demonstrating the orientation lock
        tag.next_to(cube, UP)   # put the label above the cube in 3D space
        self.add_fixed_in_frame_mobjects(title)   # title: position and orientation both locked to the screen
        title.to_edge(UP)   # move the title to the top of the frame
        self.add_fixed_orientation_mobjects(tag)   # label: orientation locked only, position still in 3D space
        self.add(axes, cube, tag)   # add the axes, the cube and the label to the scene (the title is already pinned)
        self.set_camera_orientation(phi=65 * DEGREES, theta=-50 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the position of the two objects

        self.move_camera(theta=-140 * DEGREES, run_time=1.6)   # orbit 90°: the title does not budge, the label moves with the cube in the frame
        win.play(Wait(0.4))   # pause 0.4s

        self.remove_fixed_in_frame_mobjects(title)   # release the screen pin
        self.remove_fixed_orientation_mobjects(tag)   # release the orientation lock
        self.move_camera(theta=-190 * DEGREES, run_time=1.4)   # orbit once more: both objects become ordinary 3D objects and tilt with the view
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window


# ===== Sample 5: SpecialThreeDScene ========================================
# upstream manim 0.21 bug 2: the tick_frequency in the default three_d_axes_config
# no longer exists in 0.21's NumberLine, so passing it as-is raises TypeError; drop that entry
AXIS_CFG = {
    "num_axis_pieces": 1,
    "axis_config": {
        "unit_size": 2,
        "numbers_with_elongated_ticks": [0, 1, 2],
        "stroke_width": 2,
    },
}


class SpecialDemo(SpecialThreeDScene):
    def __init__(self, **kwargs):
        # upstream manim 0.21 bug 1: SpecialThreeDScene reads self.renderer
        # before super().__init__(), so stuff in a stand-in that only carries camera_config
        self.renderer = SimpleNamespace(
            camera_config={"pixel_width": config.pixel_width})
        super().__init__(three_d_axes_config=AXIS_CFG, **kwargs)   # swap out the default axes config that carries tick_frequency

    def get_axes(self):
        # upstream manim 0.21 bug 3: NumberLine no longer has a tick_marks attribute,
        # so use get_tick_marks() instead; the rest is word for word from the manim source
        axes = ThreeDAxes(**self.three_d_axes_config)
        for axis in axes:
            if self.cut_axes_at_radius:
                p0 = axis.get_start()
                p1 = axis.number_to_point(-1)
                p2 = axis.number_to_point(1)
                p3 = axis.get_end()
                new_pieces = VGroup(Line(p0, p1), Line(p1, p2), Line(p2, p3))
                for piece in new_pieces:
                    piece.shade_in_3d = True
                new_pieces.match_style(axis.pieces)
                axis.pieces.submobjects = new_pieces.submobjects
            for tick in axis.get_tick_marks():
                tick.add(VectorizedPoint(1.5 * tick.get_center()))
        return axes

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        axes = self.get_axes()   # built from three_d_axes_config; the axes are cut off at the sphere's radius
        sphere = self.get_sphere(color=BLUE, fill_opacity=0.55)   # sphere_config defaults radius=2, resolution=(24, 48)
        cap = Text("SpecialThreeDScene", font_size=32, color=YELLOW)   # top title
        self.add_fixed_in_frame_mobjects(cap)   # pin the title to the screen
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(axes, sphere, cap)   # add the axes, the sphere and the title to the scene
        self.set_camera_to_default_position()   # back to default_angled_camera_position (phi=70° theta=-110°)
        print("default view:", self.get_default_camera_position())   # print the default view to the console
        win.play(Wait(0.8))   # pause 0.8s to see the default oblique view
        self.move_camera(phi=50 * DEGREES, theta=-150 * DEGREES, run_time=1.4)   # orbit to show the sense of depth
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window


SCENES = [
    ("ctor_default", CtorDefault),
    ("ctor_angled", CtorAngled),
    ("ctor_ambient", CtorAmbient),
    ("camera", OrientationDemo),
    ("rotation", RotationDemo),
    ("fixed", FixedDemo),
    ("special", SpecialDemo),
]

PAIRS = [
    ("02-ThreeDScene-ctor", ["ctor_default", "ctor_angled", "ctor_ambient"]),
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
