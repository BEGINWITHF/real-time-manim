# -*- coding: utf-8 -*-
"""Full source for the five samples in 15-Images-and-SVG.md (identical to the code blocks in the page).

Usage: python 15-Images-and-SVG.py <sample names>...
With no arguments it renders every sample and concatenates the page's five sample videos (written to assets/RTM output/).
The samples use two asset files (kept under assets/): demo_photo.png, demo_icon.svg.
"""
import os
import sys

import svgelements as se
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

from real_time_manim import (
    Scene, ImageMobject, ImageMobjectFromCamera, SVGMobject, VMobjectFromSVGPath,
    Square, Circle, Triangle, Dot, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== Sample 1: ImageMobject —— bitmap images ============================
class ImageDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("15-ImageMobject", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title
        photo = os.path.join(ASSETS, "demo_photo.png")   # the "filename_or_array" parameter: the image path

        # —— default: scale_to_resolution=1080 ——
        a = ImageMobject(photo).scale(1.1).move_to([-4.4, 0.9, 0])
        cap = Text("default", font_size=18, color=GREY_B).next_to(a, DOWN, buff=0.3)
        win.play(FadeIn(a), FadeIn(cap), run_time=0.5)

        # —— scale_to_resolution turned down + NEAREST resampling: pixelation ——
        b = ImageMobject(photo, scale_to_resolution=120)   # the "scale_to_resolution" parameter
        b.set_resampling_algorithm(Image.Resampling.NEAREST)   # the "set_resampling_algorithm" method
        b.scale(1.1).move_to([0, 0.9, 0])
        cap2 = Text("scale_to_resolution=120 + NEAREST", font_size=18, color=GREY_B).next_to(b, DOWN, buff=0.3)
        win.play(FadeIn(b), FadeIn(cap2), run_time=0.5)

        # —— invert=True: invert the colours ——
        c = ImageMobject(photo, invert=True).scale(1.1).move_to([4.4, 0.9, 0])   # the "invert" parameter
        cap3 = Text("invert=True", font_size=18, color=GREY_B).next_to(c, DOWN, buff=0.3)
        win.play(FadeIn(c), FadeIn(cap3), run_time=0.5)

        # —— set_opacity + image_mode: overlay semi-transparently on another one ——
        d = ImageMobject(photo, image_mode="RGB").scale(1.1).move_to([-1.4, -1.9, 0])   # the "image_mode" parameter
        e = ImageMobject(photo).scale(1.1).move_to([-0.2, -1.9, 0])   # the one underneath
        d.set_opacity(0.5)   # the "set_opacity(alpha)" method
        cap4 = Text("set_opacity(0.5)  image_mode='RGB'", font_size=18, color=GREY_B).next_to(d, DOWN, buff=0.3)
        win.play(FadeIn(e), FadeIn(d), FadeIn(cap4), run_time=0.6)

        # —— get_pixel_array: print the shape of the pixel array as a reading ——
        arr = d.get_pixel_array()   # the "get_pixel_array()" method
        cap5 = Text("pixel_array %s %s" % (arr.shape, arr.dtype),
                    font_size=18, color=GREY_B).next_to(e, DOWN, buff=1.0)
        win.play(FadeIn(cap5), run_time=0.4)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: ImageMobjectFromCamera —— using the camera picture as an image
class ImageFromCameraDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("15-ImageMobjectFromCamera", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— place a few objects in the scene first, then "photograph" them with the camera ——
        sq = Square(side_length=1.5, color=BLUE).move_to([-2.4, 1.4, 0])
        tri = Triangle(color=GREEN).scale(0.9).move_to([0.4, 1.4, 0])
        dot = Dot([2.6, 1.4, 0], color=ORANGE, radius=0.35)
        win.play(Create(sq), Create(tri), FadeIn(dot), run_time=0.5)
        self.camera.capture_mobject(VGroup(sq, tri, dot))   # draw these three objects into the camera's pixel array

        # —— default_display_frame_config: specify the frame style at construction ——
        img = ImageMobjectFromCamera(self.camera,
                                     default_display_frame_config={"stroke_width": 6, "stroke_color": YELLOW, "buff": 0})   # the "camera / default_display_frame_config" parameters
        img.set(height=2.4).move_to([-3.6, -1.3, 0])
        win.play(FadeIn(img), run_time=0.7)   # the frame is a thick yellow one

        # —— add_display_frame: add the frame afterwards (can override the style) ——
        img2 = ImageMobjectFromCamera(self.camera)   # the "camera" parameter
        img2.set(height=2.4).move_to([0.8, -1.3, 0])
        img2.add_display_frame(stroke_color=TEAL, buff=0.1)   # the "add_display_frame(**kwargs)" method
        win.play(FadeIn(img2), run_time=0.7)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: AbstractImageMobject —— the pixel array's three methods ===
class AbstractImageDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("15-AbstractImageMobject", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title
        photo = os.path.join(ASSETS, "demo_photo.png")

        # —— an abstract base class is not constructed directly: take a concrete instance and use its methods ——
        img = ImageMobject(photo, scale_to_resolution=200, pixel_array_dtype="uint8")   # the "scale_to_resolution / pixel_array_dtype" parameters
        img.set_resampling_algorithm(Image.Resampling.NEAREST)   # the "set_resampling_algorithm" method
        img.scale(1.3).move_to([-3.4, 0.4, 0])
        arr = img.get_pixel_array()   # the "get_pixel_array()" method
        cap = Text("dtype=%s shape=%s" % (arr.dtype, arr.shape),
                   font_size=18, color=GREY_B).next_to(img, DOWN, buff=0.35)
        win.play(FadeIn(img), FadeIn(cap), run_time=0.6)

        # —— set_color: tint the whole thing ——
        img.set_color(RED)   # the "set_color(color)" method
        cap2 = Text("set_color(RED)", font_size=18, color=GREY_B).next_to(cap, DOWN, buff=0.2)
        win.play(FadeIn(cap2), run_time=0.4)

        # —— the same image with a different resampling algorithm (BICUBIC): smoother edges ——
        img2 = ImageMobject(photo, scale_to_resolution=200, resampling_algorithm=Image.Resampling.BICUBIC)   # the "resampling_algorithm" parameter
        img2.set(height=img.height).move_to([2.6, 0.4, 0])
        cap3 = Text("resampling=BICUBIC", font_size=18, color=GREY_B).next_to(img2, DOWN, buff=0.35)
        win.play(FadeIn(img2), FadeIn(cap3), run_time=0.5)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 4: SVGMobject —— vector files ===============================
class SVGDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("15-SVGMobject", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title
        icon_path = os.path.join(ASSETS, "demo_icon.svg")   # the "file_name" parameter

        # —— default: height=2, should_center=True ——
        i1 = SVGMobject(icon_path).move_to([-5.4, 0.9, 0])
        win.play(FadeIn(i1), FadeIn(Text("default", font_size=18, color=GREY_B).next_to(i1, DOWN, buff=0.2)), run_time=0.5)

        # —— height / color: just change the height and unify the colour ——
        i2 = SVGMobject(icon_path, height=1.1, color=WHITE).move_to([-2.8, 0.9, 0])   # the "height / color" parameters
        win.play(FadeIn(i2), FadeIn(Text("height=1.1 color=WHITE", font_size=18, color=GREY_B).next_to(i2, DOWN, buff=0.2)), run_time=0.5)

        # —— width: scale by width (choose one of height and width) ——
        i3 = SVGMobject(icon_path, width=2.2).move_to([0.2, 0.9, 0])   # the "width" parameter
        win.play(FadeIn(i3), FadeIn(Text("width=2.2", font_size=18, color=GREY_B).next_to(i3, DOWN, buff=0.2)), run_time=0.5)

        # —— should_center=False: no longer centred (the origin stays at the file's origin) ——
        i4 = SVGMobject(icon_path, height=1.1, should_center=False).move_to([2.6, 0.9, 0])   # the "should_center" parameter
        win.play(FadeIn(i4), FadeIn(Text("should_center=False", font_size=18, color=GREY_B).next_to(i4, DOWN, buff=0.2)), run_time=0.5)

        # —— the fill/stroke set + opacity ——
        i5 = SVGMobject(icon_path, height=1.5, opacity=0.6, fill_color=TEAL, fill_opacity=0.8,
                        stroke_color=ORANGE, stroke_opacity=1.0, stroke_width=8,
                        use_svg_cache=False).move_to([-4.6, -2.0, 0])   # the "opacity / fill_* / stroke_* / use_svg_cache" parameters
        win.play(FadeIn(i5), FadeIn(Text("fill/stroke set", font_size=18, color=GREY_B).next_to(i5, DOWN, buff=0.2)), run_time=0.6)

        # —— svg_default / path_string_config: override the default styles inside the file ——
        # svg_default is the **whole** default style table (every key must be present; one missing and it is a KeyError)
        i6 = SVGMobject(icon_path, height=1.5,
                        svg_default={"color": None, "fill_color": RED, "fill_opacity": 1.0,
                                     "stroke_color": YELLOW, "stroke_opacity": 1.0,
                                     "stroke_width": 6, "opacity": None},
                        path_string_config={"long_lines": True}).move_to([-1.4, -2.0, 0])   # the "svg_default / path_string_config" parameters
        win.play(FadeIn(i6), FadeIn(Text("svg_default={full style table}", font_size=18, color=GREY_B).next_to(i6, DOWN, buff=0.2)), run_time=0.6)

        # —— the subobjects are the individual paths: you can recolour them one by one ——
        i7 = SVGMobject(icon_path, height=1.5).move_to([2.2, -2.0, 0])
        i7[0].set_color(PURPLE)   # the first path (the star)
        i7[1].set_color(GREEN)   # the second path (the circle)
        win.play(FadeIn(i7), FadeIn(Text("i7[0] / i7[1] recoloured", font_size=18, color=GREY_B).next_to(i7, DOWN, buff=0.2)), run_time=0.6)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 5: VMobjectFromSVGPath —— path data on hand =================
class SVGPathDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("15-VMobjectFromSVGPath", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— path_obj must be an already-parsed svgelements.Path (passing a string directly raises) ——
        tri = VMobjectFromSVGPath(se.Path("M 0 0 L 2 0 L 2 2 Z"), color=TEAL).move_to([-4.4, 1.0, 0])   # the "path_obj" parameter
        win.play(Create(tri), FadeIn(Text("se.Path(\"M 0 0 L 2 0 L 2 2 Z\")", font_size=18, color=GREY_B).next_to(tri, DOWN, buff=0.25)), run_time=0.6)

        # —— long_lines: how long straight segments are split ——
        curve = VMobjectFromSVGPath(se.Path("M 0 0 C 1 0 2 1 2 2 L 5 2 Z"),
                                    long_lines=True, color=GOLD).move_to([-0.9, 1.0, 0])   # the "long_lines" parameter
        win.play(Create(curve), FadeIn(Text("long_lines=True", font_size=18, color=GREY_B).next_to(curve, DOWN, buff=0.25)), run_time=0.6)

        # —— should_subdivide_sharp_curves: subdivide at sharp corners ——
        sharp = VMobjectFromSVGPath(se.Path("M 0 0 L 2 0 L 2 2 L 0 2 Z"),
                                    should_subdivide_sharp_curves=True, color=ORANGE).move_to([2.8, 1.0, 0])   # the "should_subdivide_sharp_curves" parameter
        win.play(Create(sharp), FadeIn(Text("should_subdivide_sharp_curves=True", font_size=18, color=GREY_B).next_to(sharp, DOWN, buff=0.25)), run_time=0.6)

        # —— should_remove_null_curves: drop zero-length segments ——
        nulls = VMobjectFromSVGPath(se.Path("M 0 0 L 0 0 L 2 0 L 2 0 L 2 2 Z"),
                                    should_remove_null_curves=True, color=PURPLE).move_to([-3.0, -2.0, 0])   # the "should_remove_null_curves" parameter
        win.play(Create(nulls), FadeIn(Text("should_remove_null_curves=True", font_size=18, color=GREY_B).next_to(nulls, DOWN, buff=0.25)), run_time=0.6)

        # —— a d copied out of an SVG file can be used the same way ——
        star = VMobjectFromSVGPath(se.Path("M 60 8 L 74 45 L 114 45 L 82 68 L 94 106 L 60 82 L 26 106 L 38 68 L 6 45 L 46 45 Z"),
                                   color=YELLOW).scale(0.02).move_to([1.2, -2.0, 0])
        win.play(Create(star), FadeIn(Text("d copied from demo_icon.svg", font_size=18, color=GREY_B).next_to(star, DOWN, buff=0.25)), run_time=0.6)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


SCENES = [
    ("image", ImageDemo),
    ("imagefromcamera", ImageFromCameraDemo),
    ("abstractimage", AbstractImageDemo),
    ("svg", SVGDemo),
    ("svgpath", SVGPathDemo),
]

PAIRS = [
    ("image", ["image"]),
    ("imagefromcamera", ["imagefromcamera"]),
    ("abstractimage", ["abstractimage"]),
    ("svg", ["svg"]),
    ("svgpath", ["svgpath"]),
]

PAGE = "15-Images-and-SVG"


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
    import subprocess
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
