# Images and SVG

The entry classes for putting bitmap photos and SVG vector files into a scene. One sample per class, and each sample changes each of that class's **fillable parameters** once (`ImageMobjectFromCamera` and `VMobjectFromSVGPath` used to be "not filmed separately" and have now been added).

> **Three easy traps (all verified in the samples, identical on both engines)**
> 1. The class name is **`ImageMobject`** (lower-case `m`), not the `ImageMObject` of older docs; `real_time_manim` exports `ImageMobject`, `ImageMobjectFromCamera`, `SVGMobject`, `VMobjectFromSVGPath` and `Camera` at the top level; `AbstractImageMobject` is **not** at the top level and has to be imported from `manim.mobject.types.image_mobject` (usually you do not construct it directly).
> 2. `SVGMobject(..., svg_default={...})` is the **whole** default style table: every key must be present (`color` / `fill_color` / `fill_opacity` / `stroke_color` / `stroke_opacity` / `stroke_width` / `opacity`), and one missing key gives `KeyError: 'color'`.
> 3. `VMobjectFromSVGPath(path_obj, ...)` wants an **already-parsed `svgelements.Path`** (`se.Path("M 0 0 L 2 0 L 2 2 Z")`); passing a `d` string directly raises `AttributeError: 'str' object has no attribute 'approximate_arcs_with_quads'` — the `str` written in the page's old table is wrong.

## Parameters

### `ImageMobject`

```python
def __init__(self, filename_or_array: StrPath | np.ndarray, scale_to_resolution: int = 1080, invert: bool = False, image_mode: str = "RGBA", **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `filename_or_array` | `str \| Path \| np.ndarray` | required | image path (png/jpg…) or a pixel array; the sample uses `assets/demo_photo.png` |
| `scale_to_resolution` | `int` | `1080` | the target resolution height the image is scaled to; set it to `120` with `NEAREST` and it pixelates clearly |
| `invert` | `bool` | `False` | colour inversion (common for scans/dark-background images) |
| `image_mode` | `str` | `'RGBA'` | pixel mode (`'RGBA'` with an alpha channel, `'RGB'` without) |

Methods: `set_opacity(alpha)`, `get_pixel_array()` (returns a `(H, W, 4)` `uint8` array), `set_resampling_algorithm(algorithm)`.

#### Sample: default / low resolution + NEAREST / `invert` / `set_opacity` + `image_mode` / reading the pixel array

```python
import os
import sys
import svgelements as se
from PIL import Image
from real_time_manim import (
    Scene, ImageMobject, ImageMobjectFromCamera, SVGMobject, VMobjectFromSVGPath,
    Square, Circle, Triangle, Dot, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

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
```

What this code does: the same file rendered five times.

- The first uses the default (`scale_to_resolution=1080`).
- The second squeezes the resolution down to 120 and switches the resampling algorithm to `NEAREST`, which looks like mosaic tiles when enlarged.
- The third is `invert=True`, reversing all the colours.
- The fourth is `image_mode='RGB'` with `set_opacity(0.5)`, overlaid semi-transparently on another copy of the same image, so you can see the one underneath showing through.
- Finally the shape and dtype of `get_pixel_array()` are printed as readings.

<video src="assets/RTM output/15-Images-and-SVG-image.mp4" controls width="560"></video>

> Note: `scale_to_resolution` decides "how far the pixels are reduced on load", while how large the image appears on screen is decided by `.scale()`/`.set(height=…)`; the mosaic is only visible when both are small, so the sample deliberately turns both directions down.

### `ImageMobjectFromCamera`

```python
def __init__(self, camera: MovingCamera, default_display_frame_config: dict | None = None, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `camera` | `Camera` | required | the source camera; in a scene it is `self.camera`, and you must `capture_mobject(...)` first to capture the picture into `pixel_array` before there is any content |
| `default_display_frame_config` | `dict \| None` | `{"stroke_width": 3, "stroke_color": WHITE, "buff": 0}` | the default style of the outer frame; the sample gives a thick yellow frame `{"stroke_width": 6, "stroke_color": YELLOW, "buff": 0}` |

Methods: `add_display_frame(**kwargs)` (add/change the outer frame afterwards; the kwargs override `default_display_frame_config`), `get_pixel_array()`.

#### Sample: `capture_mobject` + the constructor's frame + `add_display_frame`

```python
import os
import sys
import svgelements as se
from PIL import Image
from real_time_manim import (
    Scene, ImageMobject, ImageMobjectFromCamera, SVGMobject, VMobjectFromSVGPath,
    Square, Circle, Triangle, Dot, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

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
```

What this code does: it first places three objects in the scene (a square, a triangle, a dot) and uses `self.camera.capture_mobject(...)` to "photograph" them into the camera. Then the same camera picture is made into two image objects — the left one is given a thick yellow frame at construction (`default_display_frame_config`), and the right one uses the default frame and then `add_display_frame(stroke_color=TEAL, buff=0.1)` changes it to a teal frame afterwards.

<video src="assets/RTM output/15-Images-and-SVG-imagefromcamera.mp4" controls width="560"></video>

> Note: it takes the camera's `pixel_array` at that **moment**, so the order is "place the objects → `capture_mobject` → then construct the image object"; changing the scene afterwards does not write back into this picture (it is a static snapshot).

### `AbstractImageMobject`

```python
def __init__(self, scale_to_resolution: int, pixel_array_dtype: str = "uint8", resampling_algorithm: Resampling = Resampling.BICUBIC, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `scale_to_resolution` | `int` | required | target resolution height (the concrete class `ImageMobject` fills in `1080` for you) |
| `pixel_array_dtype` | `str` | `'uint8'` | pixel array type; the sample writes `"uint8"` and prints it as a reading |
| `resampling_algorithm` | `Resampling` | `BICUBIC` | the resampling algorithm used when scaling; the sample compares `Image.Resampling.BICUBIC` against `NEAREST` |

**Do not construct it directly** (it is an abstract base class and is not exported at the top level either): when you care about the pixel array and resampling, use its methods — `get_pixel_array()`, `set_resampling_algorithm(...)`, `set_color(...)`.

#### Sample: `NEAREST` + `set_color` + a `BICUBIC` comparison

```python
import os
import sys
import svgelements as se
from PIL import Image
from real_time_manim import (
    Scene, ImageMobject, ImageMobjectFromCamera, SVGMobject, VMobjectFromSVGPath,
    Square, Circle, Triangle, Dot, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

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
```

What this code does: it uses an `ImageMobject` instance to demonstrate the base-class interface.

- First `scale_to_resolution=200` and `pixel_array_dtype="uint8"` are given, with `NEAREST` resampling, and the dtype/shape of `get_pixel_array()` is read once and printed below.
- Then `set_color(RED)` tints the whole image.
- On the right the same image is placed but with `resampling_algorithm=BICUBIC`, and its edges are smoother than the left one.

<video src="assets/RTM output/15-Images-and-SVG-abstractimage.mp4" controls width="560"></video>

> Note: `set_color()` "tints a layer of colour" over the whole image (a multiply), not a palette replacement; for fade in/out, `set_opacity()` is more natural.

### `SVGMobject`

```python
def __init__(self, file_name: str | Path | None = None, should_center: bool = True, height: float | None = 2, width: float | None = None, color: ManimColor | None = None, opacity: float | None = None, fill_color: ManimColor | None = None, fill_opacity: float | None = None, stroke_color: ManimColor | None = None, stroke_opacity: float | None = None, stroke_width: float | None = None, svg_default: dict | None = None, path_string_config: dict | None = None, use_svg_cache: bool = True, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `file_name` | `str \| Path \| None` | `None` | SVG file path (the sample uses `assets/demo_icon.svg`) |
| `should_center` | `bool` | `True` | whether to move the shape to the origin and centre it; `False` keeps the coordinate origin in the file |
| `height` | `float \| None` | `2` | the height after loading (the sample uses `1.1`, `1.5`) |
| `width` | `float \| None` | `None` | scale by width (choose one of `height` and `width`; the sample uses `2.2`) |
| `color` | `ManimColor \| None` | `None` | a single colour for everything (both fill and stroke change); the sample uses `WHITE` |
| `opacity` | `float \| None` | `None` | overall opacity; the sample uses `0.6` |
| `fill_color` | `ManimColor \| None` | `None` | fill colour; the sample uses `TEAL` |
| `fill_opacity` | `float \| None` | `None` | fill opacity; the sample uses `0.8` |
| `stroke_color` | `ManimColor \| None` | `None` | stroke colour; the sample uses `ORANGE` |
| `stroke_opacity` | `float \| None` | `None` | stroke opacity; the sample uses `1.0` |
| `stroke_width` | `float \| None` | `None` | stroke width; the sample uses `8` |
| `svg_default` | `dict \| None` | `None` | the **whole** default style table (every key must be present, otherwise `KeyError: 'color'`); usually the `fill_*`/`stroke_*` parameters above are easier |
| `path_string_config` | `dict \| None` | `None` | the config passed to each path's parsing (e.g. `{"long_lines": True}`) |
| `use_svg_cache` | `bool` | `True` | reuse the parse cache for the same file; turn it off when comparing drawings |

Returns an `SVGMobject` (its subobjects are the individual paths, each of which can be recoloured/animated); `Text` itself is a subclass of it.

#### Sample: default / `height` + `color` / `width` / `should_center` / the fill-and-stroke set / `svg_default` / recolouring path by path

```python
import os
import sys
import svgelements as se
from PIL import Image
from real_time_manim import (
    Scene, ImageMobject, ImageMobjectFromCamera, SVGMobject, VMobjectFromSVGPath,
    Square, Circle, Triangle, Dot, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

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
```

What this code does: seven takes of the same icon.

- Default: height 2, centred.
- `height=1.1` plus `color=WHITE`.
- `width=2.2`.
- `should_center=False`: you can see it is not moved back to the origin.
- `opacity` + `fill_color/fill_opacity` + `stroke_color/stroke_opacity/stroke_width` given together, with `use_svg_cache=False`.
- `svg_default` given a whole style table (red fill, yellow stroke), together with `path_string_config`.
- Finally `i7[0]` (the star) and `i7[1]` (the circle) are tinted purple and green, proving that the subobjects are the individual paths.

<video src="assets/RTM output/15-Images-and-SVG-svg.mp4" controls width="560"></video>

> Note: `color` overrides both fill and stroke, so if you want fill and stroke in different colours, do not use `color`, use `fill_color` + `stroke_color`; once `svg_default` is given it **replaces** the whole set of default styles (it is not merged), which is why the sample writes all seven keys.

### `VMobjectFromSVGPath`

```python
def __init__(self, path_obj: svgelements.Path, long_lines: bool = False, should_subdivide_sharp_curves: bool = False, should_remove_null_curves: bool = False, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `path_obj` | `svgelements.Path` | required | an **already-parsed** path object: `se.Path("M 0 0 L 2 0 L 2 2 Z")`; passing a `str` raises `AttributeError: 'str' object has no attribute 'approximate_arcs_with_quads'` |
| `long_lines` | `bool` | `False` | how long straight segments are split (the sample compares `True`) |
| `should_subdivide_sharp_curves` | `bool` | `False` | subdivide at sharp corners (the sample uses `True`) |
| `should_remove_null_curves` | `bool` | `False` | remove zero-length segments (the sample uses `True`; two duplicate points are deliberately stuffed into the path) |

Every glyph leaf of `Text` / `MathTex` is an object of this kind (so it is in fact being rendered routinely all along); you only need to construct one yourself when "you have only the `d` data on hand and no SVG file".

#### Sample: a triangle / `long_lines` / the three switches / a `d` copied from an SVG file

```python
import os
import sys
import svgelements as se
from PIL import Image
from real_time_manim import (
    Scene, ImageMobject, ImageMobjectFromCamera, SVGMobject, VMobjectFromSVGPath,
    Square, Circle, Triangle, Dot, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

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
```

What this code does: four `d` strings are handed to `se.Path(...)` to parse, then fed to `VMobjectFromSVGPath`.

- Triangle: the most basic usage.
- A path with a curve: paired with `long_lines=True`.
- Square: paired with `should_subdivide_sharp_curves=True`.
- A path with duplicate points: paired with `should_remove_null_curves=True`.

Finally the star's `d` is copied out of `demo_icon.svg` and drawn the same way.

<video src="assets/RTM output/15-Images-and-SVG-svgpath.mp4" controls width="560"></video>

> Note: the comments on the three switches `long_lines` / `should_subdivide_sharp_curves` / `should_remove_null_curves` say "only effective under the OpenGL renderer" — on non-OpenGL paths passing them does **not** raise an error, the shape simply does not change, and the sample draws them all for easy comparison.

---

See also: [Text](08-Text.md) · [Braces](16-Braces.md) · [Containers and grouping](06-Containers-and-Grouping.md)
