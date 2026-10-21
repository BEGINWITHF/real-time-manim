# Camera (the Cairo base camera)

The base camera that quietly does the work behind every scene: RTM builds it for you from the window, and you will hardly ever construct it by hand. In everyday use only three things are actually usable: background color, the `is_in_frame` test, and `use_z_index` draw order.

The remaining constructor parameters, and the "read pixels / capture frames by hand" half of the API, belong to the Cairo pixel pipeline — RTM renders with Vulkan and has no wiring for them (marked below).

## Parameters

### class Camera (constructor parameters)

```python
def __init__(self, background_image: str | None = None, frame_center: Point3D = ORIGIN, image_mode: str = "RGBA", n_channels: int = 4, pixel_array_dtype: str = "uint8", cairo_line_width_multiple: float = 0.01, use_z_index: bool = True, background: PixelArray | None = None, pixel_height: int | None = None, pixel_width: int | None = None, frame_height: float | None = None, frame_width: float | None = None, frame_rate: float | None = None, background_color: ParsableManimColor | None = None, background_opacity: float | None = None, **kwargs: Any) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `background_image` | `str \| None` | `None` | background image path; **not wired up**: background images belong to Cairo pixel compositing, which RTM's vector rendering does not recognize |
| `frame_center` | `Point3D` | `ORIGIN` | picture center; **not advisable to change**: CE shifts the picture by it, while RTM's picture stays fixed in the center (it only changes the center used by the `is_in_frame` test), so the two engines differ |
| `image_mode` | `str` | `"RGBA"` | pixel mode; **not wired up** (pixel-array only; RTM has no `pixel_array`) |
| `n_channels` | `int` | `4` | number of pixel channels; **not wired up**, as above |
| `pixel_array_dtype` | `str` | `"uint8"` | pixel-array dtype; **not wired up**, as above |
| `cairo_line_width_multiple` | `float` | `0.01` | Cairo line-width multiple; **not wired up**: RTM rasterizes strokes itself and does not use this factor |
| `use_z_index` | `bool` | `True` | whether to draw sorted by `z_index`; **accepts** `True`/`False`, effective in both engines (changing the attribute at runtime works too, see sample 3) |
| `background` | `PixelArray \| None` | `None` | initial background pixel array; **not wired up**, pixel-array only |
| `pixel_height` | `int \| None` | `None` → takes `config` | output pixel height; **not advisable to change**: RTM only outputs 1920×1080, so nothing you pass changes the picture |
| `pixel_width` | `int \| None` | `None` → takes `config` | output pixel width; as above |
| `frame_height` | `float \| None` | `None` → takes `config` | logical frame height (default 8.0); **not advisable to change**: coordinate conversion always follows the `config` frame, so changing it has no effect |
| `frame_width` | `float \| None` | `None` → takes `config` | logical frame width (default 14.222); as above |
| `frame_rate` | `float \| None` | `None` → takes `config` | frame rate; **not advisable to change**: RTM is fixed at 60fps |
| `background_color` | `ParsableManimColor \| None` | `None` → `config.background_color` | background color; any color is accepted, but the constructor parameter cannot get through (see below), so the property is more direct (sample 1) |
| `background_opacity` | `float \| None` | `None` → `config.background_opacity` | background opacity 0–1; readable and writable but the output does not change (sample 1) |
| `**kwargs` | `Any` | — | extra keyword parameters (listed in the signature) |

**Returns**: none (constructs an instance). Every parameter that is `None` automatically takes the same-named value from `config`.

Why this section has no video: `Scene` only stores the **class** `camera_class`, and the renderer builds the camera with a no-argument `camera_class()` call — constructor parameters simply cannot get through (to pass them you must use `functools.partial(Camera, ...)` or a subclass overriding the defaults).

And none of these parameters is worth the effort:

- the pixel-pipeline parameters, which RTM does not use at all;
- the two background-related ones — change the property directly (sample 1);
- `use_z_index` — changing the attribute at runtime works just as well (sample 3).

### Camera.background_color / Camera.background_opacity (properties)

```python
def background_color(self) -> ManimColor:
def background_color(self, color: ManimColor) -> None:
def background_opacity(self) -> float:
def background_opacity(self, alpha: float) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | `ManimColor` | — | assigning rebuilds the background immediately; **accepts** any color string or constant (`"#1E3A5F"`, `BLUE`, …) |
| `alpha` | `float` | — | 0–1; **readable and writable, but the output picture does not change** — the video stores only RGB, with no alpha channel |

**Returns**: the getter returns `ManimColor` / `float`; the setter returns nothing, and the assignment takes effect immediately (no need to wait for the next frame's animation).

#### Sample: background_color / background_opacity

```python
from real_time_manim import (
    BLUE, RED, WHITE, YELLOW,
    DOWN, LEFT, RIGHT, UP,
    Circle, FadeIn, Scene, Square, Text,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class BackgroundDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=BLUE).set_fill(BLUE, 0.8)   #a blue square as a reference
        cap = Text("default background", font_size=32, color=YELLOW).to_edge(UP)   #caption at the top
        self.add(sq, cap)   #add the square and the caption to the scene
        win.play(FadeIn(sq), run_time=0.5)   #the square fades in: at this point still the default black background
        win.play(Wait(0.4))   #hold 0.4s
        self.camera.background_color = "#1E3A5F"   #change the background color: the assignment takes effect immediately
        cap.become(Text("background_color = '#1E3A5F'", font_size=32, color=YELLOW).to_edge(UP))   #swap the caption text for the background color
        win.play(Wait(0.8))   #hold 0.8s to see the navy background
        self.camera.background_opacity = 0.6   #change the background opacity: readable and writable
        info = Text("background_opacity = 0.6 (video unchanged)", font_size=26, color=WHITE).next_to(cap, DOWN)   #read the opacity back: the output is an opaque MP4
        self.add(info)   #add the reading to the scene
        win.play(Wait(0.8))   #hold 0.8s: the picture does not fade
        win.close()   #close the RTM window
```

What this code does: it first puts up a blue square; at this point the background is still manim's default black.

Then the single line `self.camera.background_color = "#1E3A5F"` switches the background to navy — no animation has to be played; the picture changes the instant the assignment happens, and you can clearly see the background jump color in the video.

Then it writes `background_opacity = 0.6` and prints the current value on screen: the value can be read and written, but the output is an opaque MP4 (RGB only), so the picture in the second half does not budge.

<video src="assets/RTM output/01-Camera-background.mp4" controls width="560"></video>

> Note:
>
> - the background color can be changed at any time and takes effect at once, so a "color-swap transition" needs no extra animation.
> - `background_opacity` is just a number recorded on the camera and is discarded when exporting the video — for a translucent effect set `fill_opacity` on the mobject itself, and don't expect the background to fade.
> - `MLWindow(960, 540)` is forcibly corrected to 1920×1080 and prints a hint line; this is not an error.

### Camera.is_in_frame(mobject)

```python
def is_in_frame(self, mobject: Mobject) -> bool:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | the object to test; **accepts** any mobject (its children are not counted separately) |

**Returns**: `bool`. A purely mathematical test against the viewfinder bounds: if the whole object is off screen it returns `False`, and **showing even a sliver counts as `True`** (under RTM the viewfinder is fixed at the default 14.222×8 frame with center `ORIGIN`; under `MovingCamera` it is computed from its `frame`).

#### Sample: is_in_frame

```python
from real_time_manim import (
    BLUE, RED, WHITE, YELLOW,
    DOWN, LEFT, RIGHT, UP,
    Circle, FadeIn, Scene, Square, Text,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class IsInFrameDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        near = Square(color=BLUE).set_fill(BLUE, 0.8)   #the square in the middle of the screen: inside the viewfinder
        far = Circle(radius=0.8, color=RED).shift(RIGHT * 10)   #the distant circle: outside the viewfinder
        cap = Text("camera.is_in_frame(mobject) -> bool", font_size=30, color=YELLOW).to_edge(UP)   #caption at the top
        info = Text("square=%s  circle=%s" % (self.camera.is_in_frame(near), self.camera.is_in_frame(far)),
                    font_size=28, color=WHITE).next_to(cap, DOWN)   #first set of readings: square True, circle False
        self.add(near, far, cap, info)   #add the four objects to the scene
        win.play(FadeIn(near), run_time=0.5)   #the square fades in
        win.play(Wait(0.5))   #hold 0.5s
        win.play(near.animate.shift(RIGHT * 8.5), run_time=0.8)   #push the square out of the viewfinder
        info.become(Text("after move: square=%s" % self.camera.is_in_frame(near),
                    font_size=28, color=WHITE).next_to(cap, DOWN))   #second set of readings: the square becomes False
        win.play(Wait(0.8))   #hold 0.8s and wrap up
        win.close()   #close the RTM window
```

What this code does: it puts a square in the middle of the screen and a circle far off to the right (so far it is completely invisible), and first reads a set of `is_in_frame` results onto the screen — square `True`, circle `False`; then it slides the square out of the picture and tests again after the animation, and the reading flips to `False`.

The whole test is pure geometric computation that does not touch rendering, so calling it at any moment returns instantly; it is often used for logic like "switch the shot when an object leaves the frame".

<video src="assets/RTM output/01-Camera-is_in_frame.mp4" controls width="560"></video>

> Note:
>
> - the criterion is "does it intersect the viewfinder", and an object half off screen still returns `True`; the circle placed at `RIGHT * 10` and added to the scene is completely invisible, which is exactly the effect of `False` — you don't have to guess whether something is on screen, just ask it.
> - a plain `Camera`'s viewfinder is always the default frame; if `frame_center` changes it changes too (but the picture does not move, see the table above), so if unsure, leave `frame_center` alone.

### Camera.use_z_index

**What it does**: whether to draw sorted by `z_index`. The attribute is readable and writable (`True`/`False`), and changing it takes effect on the next frame.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `use_z_index` | `bool` | `True` | **accepts** `True` (sorted by `z_index`, larger `z_index` drawn on top) / `False` (drawn in add order, later additions on top) |

**Returns**: none (an ordinary attribute assignment).

#### Sample: use_z_index

```python
from real_time_manim import (
    BLUE, RED, WHITE, YELLOW,
    DOWN, LEFT, RIGHT, UP,
    Circle, FadeIn, Scene, Square, Text,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class UseZIndexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        a = Square(color=BLUE).set_fill(BLUE, 0.9).shift(LEFT * 0.4)   #the blue square: added to the scene first
        a.z_index = 1   #high z-order: drawn on top when use_z_index=True
        b = Square(color=RED).set_fill(RED, 0.9).shift(RIGHT * 0.4)   #the red square: added to the scene later
        b.z_index = 0   #low z-order: drawn on top only when drawing purely in add order
        cap = Text("use_z_index=True", font_size=32, color=YELLOW).to_edge(UP)   #caption at the top
        self.add(a, b, cap)   #add a then b to the scene
        win.play(Wait(1.0))   #hold 1.0s: blue on top (drawn sorted by z_index)
        self.camera.use_z_index = False   #turn z-order off: switch to drawing in add order
        cap.become(Text("use_z_index=False", font_size=32, color=YELLOW).to_edge(UP))   #swap the caption text accordingly
        win.play(Wait(1.0))   #hold 1.0s: red on top (later additions drawn on top)
        win.close()   #close the RTM window
```

What this code does: two translucent squares stacked with an offset; blue is added first but has `z_index=1`, red is added later but has `z_index=0`.

In the first half `use_z_index=True` (the default), drawing is sorted by `z_index` and the overlap has blue over red; midway the single line `self.camera.use_z_index = False` turns z-order off and immediately switches to drawing in add order, flipping the overlap to red over blue.

The same pair of objects in the same position; changing just this one boolean reverses the whole stacking.

<video src="assets/RTM output/01-Camera-use_z_index.mp4" controls width="560"></video>

> Note: this is a runtime attribute and the camera does not need to be rebuilt — constructor parameters cannot get into `Camera` (see the top of this page), so just write `self.camera.use_z_index = False`.
>
> Also, when two objects have the same `z_index` the two modes look exactly the same (both follow add order), so to see a difference you must give the objects different `z_index` values as in the sample.

### Pixel reads and manual capture (capture_mobjects / capture_mobject / get_image / set_background_from_func)

```python
def capture_mobjects(self, mobjects: Iterable[Mobject], **kwargs: Any) -> None:
def capture_mobject(self, mobject: Mobject, **kwargs: Any) -> None:
def get_image(self, pixel_array: PixelArray | list | tuple | None = None) -> Image.Image:
def set_background_from_func(self, coords_to_colors_func: Callable[[np.ndarray], np.ndarray]) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobjects` | `Iterable[Mobject]` | — | `capture_mobjects`: the objects to capture |
| `mobject` | `Mobject` | — | `capture_mobject`: the object to capture |
| `**kwargs` | `Any` | — | forwarded to `get_mobjects_to_display`, e.g. `excluded_mobjects=[...]` |
| `pixel_array` | `PixelArray \| list \| tuple \| None` | `None` | `get_image`: when `None`, takes the current frame |
| `coords_to_colors_func` | `Callable[[np.ndarray], np.ndarray]` | — | `set_background_from_func`: takes an (x,y) coordinate pair and outputs a 4-element RGBA float array |

**Returns**: `capture_mobjects` / `capture_mobject` / `set_background_from_func` return nothing; `get_image` returns a `PIL.Image.Image`.

**No video**: these four are APIs of the Cairo pixel-array pipeline — they draw the picture into `camera.pixel_array` and read it back. RTM uses Vulkan vector rendering and goes straight to the window/encoder after drawing, so there is no readable pixel array at all, and these calls cannot get the current frame's image.

To "grab a frame", use `fast_record_scene` to produce a clip and then extract a frame with ffmpeg.

**A further distinction**: the **camera**'s `background_image` (a constructor parameter) is not wired up under RTM (see the parameter table at the top of this page); what is meant here is `Mobject.color_using_background_image`, for **a mobject** — RTM only takes that image's average color as the object's stroke color (`real_time_manim/background_color.py:1-40`), which has nothing to do with "grabbing a frame as a background" and is not a frame-grabbing method either.

---

See also: [MovingCamera](02-MovingCamera.md), [ThreeDCamera](03-ThreeDCamera.md), [MovingCameraScene](../Special-Scenes/01-MovingCameraScene.md), [Scene basics](../Scenes/01-Scene-Basics.md)
