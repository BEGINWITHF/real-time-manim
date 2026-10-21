# -*- coding: utf-8 -*-
"""Full source of the four samples in 03-ThreeDCamera.md (identical to the code blocks in the page).

Usage: python 03-ThreeDCamera.py <clip name>...
With no arguments it renders all 9 scenes and concatenates the page's four videos.
"""
import os
import subprocess
import sys
from functools import partial

HERE = os.path.dirname(os.path.abspath(__file__))
FRAG = os.path.join(HERE, "final",
                       os.path.splitext(os.path.basename(__file__))[0])
ASSETS = os.path.dirname(HERE)
os.makedirs(FRAG, exist_ok=True)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    BLUE, GREEN, WHITE, YELLOW,
    DEGREES, DOWN, LEFT, ORIGIN, OUT, RIGHT, UP,
    Cube, FadeIn, Text, ThreeDAxes, ThreeDCamera, ThreeDScene,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: the class ThreeDCamera constructor parameters ==============
class CtorAngleDemo(ThreeDScene):
    def __init__(self, **kwargs):
        #"camera_class" only takes a class (the renderer calls it with no arguments to build the camera),
        #constructor parameters must be wrapped in functools.partial to get through
        super().__init__(camera_class=partial(ThreeDCamera, phi=70 * DEGREES, theta=-60 * DEGREES), **kwargs)

    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        self.play = win.play   #a scene method calls self.play internally, so wire it to the window first
        axes = ThreeDAxes()   #the default 3D axes
        cube = Cube(side_length=1.5).set_color(BLUE)   #a blue cube as a reference
        cap = Text("ctor phi=70 theta=-60 (no set_camera_orientation)", font_size=26, color=YELLOW)   #caption at the top
        self.camera.add_fixed_in_frame_mobjects(cap)   #pin the title to the screen so it does not turn with the camera
        cap.to_edge(UP)   #move the title to the top of the picture
        self.add(axes, cube, cap)   #add the axes, the cube and the title to the scene
        win.play(FadeIn(cube), run_time=0.5)   #the cube fades in: the view is already angled
        win.play(Wait(1.2))   #hold 1.2s: the initial view from the constructor parameters takes effect directly
        win.close()   #close the RTM window


class CtorLightDemo(ThreeDScene):
    def __init__(self, **kwargs):
        #also pass "light_source_start_point" into the constructor with partial: the light flips to the upper-right-front
        super().__init__(camera_class=partial(
            ThreeDCamera, light_source_start_point=9 * UP + 7 * RIGHT + 10 * OUT), **kwargs)

    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        self.play = win.play   #a scene method calls self.play internally, so wire it to the window first
        axes = ThreeDAxes()   #the default 3D axes
        cube = Cube(side_length=1.5).set_color(BLUE)   #a blue cube as a reference
        cap = Text("ctor light=9U+7R+10O", font_size=30, color=YELLOW)   #caption at the top
        self.camera.add_fixed_in_frame_mobjects(cap)   #pin the title to the screen
        cap.to_edge(UP)   #move the title to the top of the picture
        self.add(axes, cube, cap)   #add the axes, the cube and the title to the scene
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #explicitly set the view back to the previous segment's angle, to compare only the lighting
        win.play(FadeIn(cube), run_time=0.5)   #the cube fades in: its light/dark faces are opposite to the previous segment
        win.play(Wait(1.0))   #hold 1.0s
        win.close()   #close the RTM window


class CtorShadingDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        self.play = win.play   #a scene method calls self.play internally, so wire it to the window first
        axes = ThreeDAxes()   #the default 3D axes
        cube = Cube(side_length=1.5).set_color(BLUE)   #a blue cube as a reference
        cap = Text("should_apply_shading=True", font_size=30, color=YELLOW)   #caption at the top
        self.camera.add_fixed_in_frame_mobjects(cap)   #pin the title to the screen
        cap.to_edge(UP)   #move the title to the top of the picture
        self.add(axes, cube, cap)   #add the axes, the cube and the title to the scene
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #set the view explicitly
        win.play(FadeIn(cube), run_time=0.5)   #the cube fades in: the faces have different brightness
        win.play(Wait(0.7))   #hold 0.7s
        self.camera.should_apply_shading = False   #turn shading off: all faces become the same color
        cap.become(Text("should_apply_shading=False", font_size=30, color=YELLOW).to_edge(UP))   #swap the caption text accordingly
        win.play(Wait(1.0))   #hold 1.0s to see the flat color
        win.close()   #close the RTM window


# ===== Sample 2: get_* / set_* / get_value_trackers =========================
class ViewZoomDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        self.play = win.play   #a scene method calls self.play internally, so wire it to the window first
        cam = self.camera   #ThreeDScene's built-in ThreeDCamera
        axes = ThreeDAxes()   #the default 3D axes
        cube = Cube(side_length=1.5).set_color(BLUE)   #a blue cube as a reference
        cap = Text("get_phi / get_theta / get_gamma / get_zoom / get_focal_distance", font_size=22, color=YELLOW)   #caption at the top
        cam.add_fixed_in_frame_mobjects(cap)   #pin the title to the screen
        cap.to_edge(UP)   #move the title to the top of the picture
        info = Text("phi=%.2f theta=%.2f gamma=%.2f zoom=%.2f focal=%.1f" % (
            cam.get_phi(), cam.get_theta(), cam.get_gamma(), cam.get_zoom(), cam.get_focal_distance()),
            font_size=24, color=WHITE).next_to(cap, DOWN)   #readings of the five view parameters
        cam.add_fixed_in_frame_mobjects(info)   #pin the readings to the screen too
        self.add(axes, cube, cap, info)   #add the axes, the cube, the title and the readings to the scene
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #set the view explicitly
        win.play(FadeIn(cube), run_time=0.5)   #the cube fades in
        cam.set_focal_distance(18.0)   #change the focal length: takes effect immediately
        cam.set_zoom(1.15)   #change the zoom: takes effect immediately
        info.become(Text("phi=%.2f theta=%.2f gamma=%.2f zoom=%.2f focal=%.1f" % (
            cam.get_phi(), cam.get_theta(), cam.get_gamma(), cam.get_zoom(), cam.get_focal_distance()),
            font_size=24, color=WHITE).next_to(cap, DOWN))   #refresh the readings
        win.play(Wait(1.2))   #hold 1.2s to see the zoomed-in picture
        win.close()   #close the RTM window


class ViewTrackerDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        self.play = win.play   #a scene method calls self.play internally, so wire it to the window first
        cam = self.camera   #ThreeDScene's built-in ThreeDCamera
        axes = ThreeDAxes()   #the default 3D axes
        cube = Cube(side_length=1.5).set_color(BLUE)   #a blue cube as a reference
        cap = Text("get_value_trackers()[1].animate.set_value(-1.2)", font_size=26, color=YELLOW)   #caption at the top
        cam.add_fixed_in_frame_mobjects(cap)   #pin the title to the screen
        cap.to_edge(UP)   #move the title to the top of the picture
        self.add(axes, cube, cap)   #add the axes, the cube and the title to the scene
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #set the view explicitly
        trackers = cam.get_value_trackers()   #5 ValueTrackers: phi, theta, focal_distance, gamma, zoom
        win.play(FadeIn(cube), run_time=0.5)   #the cube fades in
        win.play(trackers[1].animate.set_value(-1.2), run_time=1.0)   #animate the theta tracker: the camera orbits
        win.play(Wait(0.6))   #hold 0.6s and wrap up
        win.close()   #close the RTM window


class ViewAngleDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        self.play = win.play   #a scene method calls self.play internally, so wire it to the window first
        cam = self.camera   #ThreeDScene's built-in ThreeDCamera
        axes = ThreeDAxes()   #the default 3D axes
        cube = Cube(side_length=1.5).set_color(BLUE)   #a blue cube as a reference
        cap = Text("set_phi(0.6) / set_gamma(0.25)", font_size=28, color=YELLOW)   #caption at the top
        cam.add_fixed_in_frame_mobjects(cap)   #pin the title to the screen
        cap.to_edge(UP)   #move the title to the top of the picture
        self.add(axes, cube, cap)   #add the axes, the cube and the title to the scene
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #set the view explicitly
        win.play(FadeIn(cube), run_time=0.5)   #the cube fades in
        cam.set_phi(0.6)   #change the polar angle: takes effect immediately, a shallower top-down look
        cam.set_gamma(0.25)   #change the roll angle: takes effect immediately, the picture rolls about the view axis
        win.play(Wait(1.2))   #hold 1.2s to see the view after the jump
        win.close()   #close the RTM window


# ===== Sample 3: add_fixed_in_frame_mobjects / add_fixed_orientation_mobjects ==
class FixedDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        self.play = win.play   #move_camera calls self.play internally, so wire it to the window first
        cam = self.camera   #ThreeDScene's built-in ThreeDCamera
        axes = ThreeDAxes()   #the default 3D axes
        cube = Cube(side_length=1.2).set_color(BLUE)   #a blue cube as a reference
        title = Text("fixed_in_frame", font_size=34, color=YELLOW)   #a title demonstrating screen pinning
        tag = Text("fixed_orientation", font_size=26, color=GREEN)   #a label demonstrating the orientation lock
        tag.next_to(cube, UP)   #place the label in 3D space above the cube
        cam.add_fixed_in_frame_mobjects(title)   #title: both position and orientation locked to the screen
        title.to_edge(UP)   #move the title to the top of the picture
        cam.add_fixed_orientation_mobjects(tag)   #label: only the orientation is locked, the position stays in 3D space
        self.add(axes, cube, tag, title)   #add the four objects to the scene: the camera's add_fixed_* only registers the draw mode, it does not add for you
        self.set_camera_orientation(phi=65 * DEGREES, theta=-50 * DEGREES)   #set the view explicitly
        win.play(Wait(0.8))   #hold 0.8s to see the two objects' positions
        self.move_camera(theta=-140 * DEGREES, run_time=1.6)   #orbit 90°: the title does not budge, the label moves with the cube across the picture
        win.play(Wait(0.4))   #hold 0.4s
        cam.remove_fixed_in_frame_mobjects(title)   #undo the screen pinning
        cam.remove_fixed_orientation_mobjects(tag)   #undo the orientation lock
        self.move_camera(theta=-190 * DEGREES, run_time=1.4)   #orbit once more: both objects become ordinary 3D objects
        win.play(Wait(0.4))   #hold 0.4s and wrap up
        win.close()   #close the RTM window


# ===== Sample 4: project_point / project_points, exponential_projection =====
class ProjectDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        self.play = win.play   #a scene method calls self.play internally, so wire it to the window first
        cam = self.camera   #ThreeDScene's built-in ThreeDCamera
        axes = ThreeDAxes()   #the default 3D axes
        cap = Text("project_point(ORIGIN) / project_points([ORIGIN, RIGHT, UP])", font_size=22, color=YELLOW)   #caption at the top
        cam.add_fixed_in_frame_mobjects(cap)   #pin the title to the screen
        cap.to_edge(UP)   #move the title to the top of the picture
        self.add(axes, cap)   #add the axes and the title to the scene
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #set the view explicitly
        p1 = cam.project_point(ORIGIN)   #the projected coordinate of the origin
        pts = cam.project_points([ORIGIN, RIGHT, UP])   #the projected coordinates of the three points
        info = Text("origin=(%.2f, %.2f)  right=(%.2f, %.2f)  up=(%.2f, %.2f)" % (
            p1[0], p1[1], pts[1][0], pts[1][1], pts[2][0], pts[2][1]),
            font_size=24, color=WHITE).next_to(cap, DOWN)   #put the projection result on screen
        cam.add_fixed_in_frame_mobjects(info)   #pin the readings to the screen
        self.add(info)   #add the readings to the scene
        win.play(Wait(1.2))   #hold 1.2s to see the projection values
        win.close()   #close the RTM window


class ExponentialDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        self.play = win.play   #a scene method calls self.play internally, so wire it to the window first
        cam = self.camera   #ThreeDScene's built-in ThreeDCamera
        axes = ThreeDAxes()   #the default 3D axes
        near = Cube(side_length=1.2).set_color(BLUE)   #the near cube
        far = Cube(side_length=1.2).set_color(GREEN).shift(DOWN * 2.5 + RIGHT * 2.5)   #the far cube
        cap = Text("exponential_projection=False", font_size=28, color=YELLOW)   #caption at the top
        cam.add_fixed_in_frame_mobjects(cap)   #pin the title to the screen
        cap.to_edge(UP)   #move the title to the top of the picture
        self.add(axes, near, far, cap)   #add the axes, the two cubes and the title to the scene
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #set the view explicitly
        cam.set_focal_distance(6.0)   #pull the focal length closer: stronger perspective, so the difference between the two projections shows
        win.play(FadeIn(near, far), run_time=0.5)   #the two cubes fade in
        win.play(Wait(0.8))   #hold 0.8s to see the ordinary projection
        cam.exponential_projection = True   #switch to exponential projection: distant objects are no longer over-magnified
        cap.become(Text("exponential_projection=True", font_size=28, color=YELLOW).to_edge(UP))   #swap the caption text accordingly
        win.play(Wait(1.0))   #hold 1.0s to compare
        win.close()   #close the RTM window


SCENES = [
    ("03-ThreeDCamera-ctor_angle_1", CtorAngleDemo),
    ("03-ThreeDCamera-ctor_light_2", CtorLightDemo),
    ("03-ThreeDCamera-ctor_shading_3", CtorShadingDemo),
    ("03-ThreeDCamera-view_zoom_1", ViewZoomDemo),
    ("03-ThreeDCamera-view_trackers_2", ViewTrackerDemo),
    ("03-ThreeDCamera-view_angles_3", ViewAngleDemo),
    ("03-ThreeDCamera-fixed_1", FixedDemo),
    ("03-ThreeDCamera-project_coords_1", ProjectDemo),
    ("03-ThreeDCamera-project_exponential_2", ExponentialDemo),
]

PAIRS = [
    ("03-ThreeDCamera-ctor", ["03-ThreeDCamera-ctor_angle_1", "03-ThreeDCamera-ctor_light_2",
                              "03-ThreeDCamera-ctor_shading_3"]),
    ("03-ThreeDCamera-view", ["03-ThreeDCamera-view_zoom_1", "03-ThreeDCamera-view_trackers_2",
                              "03-ThreeDCamera-view_angles_3"]),
    ("03-ThreeDCamera-fixed", ["03-ThreeDCamera-fixed_1"]),
    ("03-ThreeDCamera-project", ["03-ThreeDCamera-project_coords_1", "03-ThreeDCamera-project_exponential_2"]),
]


def concat(names, dst):
    lst = os.path.join(HERE, "concat-03-ThreeDCamera.txt")
    with open(lst, "w", encoding="utf-8") as fh:
        for n in names:
            fh.write("file '%s'\n" % os.path.join(FRAG, n + ".mp4"))
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
            fast_record_scene(cls, out_path=os.path.join(FRAG, name + ".mp4"),
                              verbose=True)
        except Exception:
            import traceback
            traceback.print_exc()

    if not only:
        for out_name, names in PAIRS:
            dst = os.path.join(ASSETS, "RTM output", out_name + ".mp4")
            concat(names, dst)
            print("concat ->", dst, os.path.getsize(dst), "bytes")
