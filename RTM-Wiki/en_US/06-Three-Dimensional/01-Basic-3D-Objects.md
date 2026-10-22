# Basic 3D Objects (1): the face base class and Cube

A 3D object has to be put into a `ThreeDScene` and have the camera view set (`set_camera_orientation(phi=..., theta=...)`) before its solid form shows.

This page covers the 3D vector-face base class `ThreeDVMobject`, plus three common primitives `Cube` / `Prism` / `Dot3D`.

## ThreeDVMobject

```python
ThreeDVMobject(shade_in_3d: bool = True, **kwargs: Any)
```

The 3D variant of `VMobject` and the base class of every 3D vector face; it is shaded by 3D lighting (the "bright front / dark side" 3D look comes from it). In everyday use you go straight to its subclasses (`Cube` faces, a 3D-ised `Polygon`, etc.) and rarely construct it on its own.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `shade_in_3d` | `bool` | `True` | whether it takes part in 3D lighting shading; with `False` it shades like an ordinary flat object (all six faces equally bright, the 3D look disappears) |
| `**kwargs` | `Any` | — | forwarded to `VMobject.__init__` (`stroke_width`, `fill_color`, …) |

> **Returns**: none (constructs an instance). The base class has no sample video of its own; the lighting effect is directly visible in the `Cube` sample below (the two cubes' faces are lit to different brightness).

## Cube

```python
Cube(side_length: float = 2, fill_opacity: float = 0.75, fill_color: ParsableManimColor = BLUE, stroke_width: float = 0, **kwargs)
```

A cube made of 6 `Square` faces (a `VGroup` subclass), translucent blue with no stroke by default.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `side_length` | `float` | `2` | edge length; **accepts** any positive number |
| `fill_opacity` | `float` | `0.75` | fill opacity (0–1); lower it and the back faces show through |
| `fill_color` | `ParsableManimColor` | `BLUE` | fill color; **accepts** any color constant or hex |
| `stroke_width` | `float` | `0` | face stroke width; **accepts** any non-negative number, no stroke by default |
| `**kwargs` | `Any` | — | forwarded to `VGroup`/`Mobject` |

#### Sample: `Cube` variations

A default translucent blue cube, contrasted against a small solid green one with a thicker stroke; `move_camera` orbits 90° to show the other side.

```python
from real_time_manim import ThreeDScene, Cube, Text, \
    BLUE, GREEN, GREY_B, YELLOW, UP, DOWN, RIGHT, DEGREES
from real_time_manim.vulkan_bind import MLWindow, Wait

class CubeDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("01-cube", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen so it always faces the viewer
        a = Cube(side_length=2, fill_opacity=0.75, fill_color=BLUE)   # defaults: side length 2, translucent blue, no stroke
        b = Cube(side_length=1.2, fill_color=GREEN, fill_opacity=1.0, stroke_width=6)   # solid green, thicker stroke
        b.next_to(a, RIGHT, buff=1.2)   # place it to the right of the default cube
        tag1 = Text("default", font_size=26, color=GREY_B).next_to(a, DOWN)   # bottom-left label
        tag2 = Text("solid + stroke", font_size=26, color=GREY_B).next_to(b, DOWN)   # bottom-right label
        self.add(a, b, tag1, tag2)   # add the two cubes and labels to the scene
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the 3D effect
        self.move_camera(theta=-135 * DEGREES, run_time=1.4)   # animate a 90° orbit to see the other side
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window
```

What this code does: it first opens an RTM window, binds the scene to it, and pins the sample title to the screen.

Then it places two cubes: on the left the defaults (side length 2, translucent blue, no stroke), on the right the tweaked one (side length 1.2, solid green, stroke 6), each with a ground label.

`set_camera_orientation` snaps to the oblique view in one frame and pauses 0.8s; then `move_camera` animates a 90° orbit, and you can see the cube's side faces change brightness as it turns — that is the 3D lighting shading at work.

<video src="assets/RTM output/01-Basic-3D-Objects-cube.mp4" controls width="560"></video>

> Note:
>
> - `move_camera` calls `self.play` internally; in RTM you must write `self.play = win.play` first, or the camera will not move.
> - `Cube` defaults to `fill_opacity=0.75` (translucent), so the back faces faintly show through; pass `1.0` for a solid cube.
> - The labels are ordinary 3D text (lying on the ground) and tilt with the view — which is exactly the proof that they live in 3D space.

## Prism

```python
Prism(dimensions: Vector3DLike = [3, 2, 1], **kwargs)
```

`Cube`'s generalisation: a cuboid stretched to the three side lengths `[x, y, z]`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `dimensions` | `Vector3DLike` | `[3, 2, 1]` | the three side lengths `[x, y, z]`; **accepts** any three positive numbers |
| `**kwargs` | `Any` | — | same as `Cube` (`fill_color`, `fill_opacity`, `stroke_width`, …) |

#### Sample: `Prism` variations

The default flat `[3, 2, 1]` cuboid, contrasted against a tall thin red `[1, 1, 3]` prism, orbiting 90° to show the three side ratios.

```python
from real_time_manim import ThreeDScene, Prism, Text, \
    GREY_B, RED, YELLOW, UP, DOWN, RIGHT, DEGREES
from real_time_manim.vulkan_bind import MLWindow, Wait

class PrismDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("01-prism", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        a = Prism(dimensions=[3, 2, 1])   # default side lengths [x, y, z] = [3, 2, 1]
        b = Prism(dimensions=[1, 1, 3], fill_color=RED, fill_opacity=0.6)   # tall thin red prism
        b.next_to(a, RIGHT, buff=1.2)   # place it to the right of the default prism
        tag1 = Text("[3, 2, 1]", font_size=26, color=GREY_B).next_to(a, DOWN)   # bottom-left label
        tag2 = Text("[1, 1, 3]", font_size=26, color=GREY_B).next_to(b, DOWN)   # bottom-right label
        self.add(a, b, tag1, tag2)   # add the two prisms and labels to the scene
        self.set_camera_orientation(phi=65 * DEGREES, theta=-60 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the side-length difference
        self.move_camera(theta=-150 * DEGREES, run_time=1.4)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window
```

What this code does: it places two prisms — the default `[3, 2, 1]` on the left (wide and flat), and `[1, 1, 3]` recolored translucent red on the right (thin and tall) — each with a ground label listing its side lengths. After the oblique view pauses 0.8s, it orbits 90°, and when it reaches the side you can clearly see that `[1, 1, 3]` "tall pillar" standing upright.

<video src="assets/RTM output/01-Basic-3D-Objects-prism.mp4" controls width="560"></video>

> Note: `Prism` is just `Cube` rescaled along the three sides; `dimensions` is ordered `[x, y, z]` (z is vertical), so don't swap them. Passing `[1, 1, 1]` gives a `Cube` of side length 1.

## Dot3D

```python
Dot3D(point: Point3D = ORIGIN, radius: float = DEFAULT_DOT_RADIUS, color: ParsableManimColor = WHITE, resolution: int | tuple[int, int] | None = (8, 8), **kwargs)
```

A specialisation of `Sphere`: a low-resolution small sphere used to mark a point in 3D space (the 3D analogue of the 2D `Dot`).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `point` | `Point3D` | `ORIGIN` | sphere center; **accepts** `[x, y, z]` or a direction vector like `UR` |
| `radius` | `float` | `DEFAULT_DOT_RADIUS` (0.08) | radius; **accepts** any positive number, the sample uses `0.4` / `0.5` so it is easier to see |
| `color` | `ParsableManimColor` | `WHITE` | color |
| `resolution` | `int \| tuple[int,int] \| None` | `(8, 8)` | u/v sample counts; larger is smoother and slower; the sample uses `(4, 2)` to contrast the faceted look |
| `**kwargs` | `Any` | — | forwarded to `Sphere` |

#### Sample: `Dot3D` variations

Three enlarged spheres: a big red one marks a point, and two green ones compare the smoothness of the very low resolution `(4, 2)` against the default `(8, 8)`.

```python
from real_time_manim import ThreeDScene, Dot3D, Text, \
    GREEN, GREY_B, RED, YELLOW, UP, DOWN, LEFT, RIGHT, UR, DEGREES
from real_time_manim.vulkan_bind import MLWindow, Wait

class Dot3DDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("01-dot3d", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        big = Dot3D(2 * UR, radius=0.5, color=RED)   # large red sphere marking a 3D point
        rough = Dot3D(LEFT * 2.5 + DOWN, radius=0.4, color=GREEN, resolution=(4, 2))   # very low resolution: sharp facets
        smooth = Dot3D(RIGHT * 2.5 + DOWN, radius=0.4, color=GREEN)   # default (8, 8): a bit smoother
        tag1 = Text("res=(4,2)", font_size=26, color=GREY_B).next_to(rough, DOWN)   # bottom-left label
        tag2 = Text("default (8,8)", font_size=26, color=GREY_B).next_to(smooth, DOWN)   # bottom-right label
        self.add(big, rough, smooth, tag1, tag2)   # add the three spheres and labels to the scene
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to compare resolution
        self.move_camera(theta=-135 * DEGREES, run_time=1.4)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window
```

What this code does: it places three enlarged spheres in 3D space.

- A big red sphere up and to the right (`radius=0.5`) demonstrating how to mark a point by coordinates.
- A green sphere at the lower left, using `resolution=(4, 2)`, with very few faces and sharp facets.
- A green sphere at the lower right, using the default `(8, 8)`, clearly smoother.

Orbiting 90° shows the low-resolution sphere's "polygonal edges" next to the smooth surface of the high-resolution one.

<video src="assets/RTM output/01-Basic-3D-Objects-dot3d.mp4" controls width="560"></video>

> Note:
>
> - `Dot3D`'s default `radius=0.08` is very small; the clip enlarges it to 0.4–0.5 just to see it. When marking real points, pick the radius to suit the scene scale.
> - The lower `resolution`, the less render time; for marking purposes it is good enough as-is.

---

See also: [Basic 3D Objects (2)](01b-Basic-3D-Objects-Advanced.md) · [Surfaces](02-Surfaces.md)
