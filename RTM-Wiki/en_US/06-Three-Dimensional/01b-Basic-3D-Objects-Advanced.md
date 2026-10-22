# Basic 3D Objects (2): line segments, arrows and solids of revolution

Continuing from the previous page, this page covers the thick 3D line segment `Line3D`, the 3D arrow `Arrow3D`, and the two solids of revolution `Cone` / `Cylinder` built from a swept surface.

## Line3D

```python
Line3D(start: Point3DLike = LEFT, end: Point3DLike = RIGHT, thickness: float = 0.02, color: ParsableManimColor | None = None, resolution: int | tuple[int, int] = 24, **kwargs)
```

A cylinder with thickness, used as a "line" in 3D space; `Arrow3D` is its subclass. The classmethods `Line3D.parallel_to(line, point=ORIGIN, length=5)` / `Line3D.perpendicular_to(line, point=ORIGIN, length=5)` build a parallel/perpendicular segment.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `start` | `Point3DLike` or `Mobject` | `LEFT` | start point; **accepts** `[x, y, z]` or another mobject (its center is taken automatically) |
| `end` | `Point3DLike` or `Mobject` | `RIGHT` | end point |
| `thickness` | `float` | `0.02` | cylinder radius (line thickness); **accepts** any positive number, the sample uses `0.06` so it is easier to see |
| `color` | `ParsableManimColor \| None` | `None` | color; `None` keeps the default white |
| `resolution` | `int \| tuple[int,int]` | `24` | int = number of sample points; passing `(u, v)` also controls the checkerboard count |
| `**kwargs` | `Any` | — | forwarded to `Cylinder` (`stroke_width`, `fill_opacity`, …) |

#### Sample: `Line3D` variations

A thicker yellow main segment drawn piece by piece with `Create`, with two reference segments built by the `parallel_to` / `perpendicular_to` classmethods, orbiting 90° to show the spatial relation.

```python
from real_time_manim import ThreeDScene, Line3D, Text, \
    GREY_B, YELLOW, UP, DOWN, DEGREES, Create
from real_time_manim.vulkan_bind import MLWindow, Wait

class Line3DDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first (this sample's Create goes through win.play and needs no wiring)
        title = Text("01b-line3d", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        line = Line3D(start=[-2, -1, 0], end=[2, 1, 1.5], thickness=0.06, color=YELLOW)   # thicker yellow main segment
        para = Line3D.parallel_to(line, point=[-1, -2.5, 0], length=4)   # a segment through the given point, parallel to the main segment
        perp = Line3D.perpendicular_to(line, point=[2, -2, 0.75], length=3)   # a segment through the given point, perpendicular to the main segment
        self.add(para, perp)   # first add the two reference segments to the scene
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)   # set an oblique view
        win.play(Create(line), run_time=0.8)   # draw the main segment piece by piece
        win.play(Wait(0.5))   # pause 0.5s to see the parallel/perpendicular relation
        self.move_camera(theta=-135 * DEGREES, run_time=1.2)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window
```

What this code does: it first places the two reference segments.

- One is built with `Line3D.parallel_to(main segment, point=..., length=4)`, passing through the given point and parallel to the main segment.
- The other is built with `perpendicular_to` and is perpendicular to the main segment.

Then `Create` draws the yellow main segment piece by piece from start to end; after a 0.5s pause it orbits 90°, confirming from the side that the parallel/perpendicular relation of the three segments holds in 3D space.

<video src="assets/RTM output/01b-Basic-3D-Objects-Advanced-line3d.mp4" controls width="560"></video>

> Note:
>
> - `Create` works in RTM (`Line3D` supports piece-by-piece drawing).
> - **Tested 2026-10-17**: in this sample the only thing that really needs the `self.play = win.play` wiring is `move_camera` (it calls `self.play` internally, so without the wiring the orbit will not move); `Create` is played directly as `win.play(Create(...))`, bypassing `Scene.play`, so it draws even without the wiring.
> - The default `thickness=0.02` is very thin; the clip enlarges it to 0.06 to make it visible.

## Arrow3D

```python
Arrow3D(start: Point3DLike = LEFT, end: Point3DLike = RIGHT, thickness: float = 0.02, height: float = 0.3, base_radius: float = 0.08, color: ParsableManimColor = WHITE, resolution: int | tuple[int, int] = 24, **kwargs)
```

A 3D arrow made of a cylindrical shaft + a conical tip (a `Line3D` subclass), used for axis vectors, force/velocity directions; `get_end()` returns the tip coordinates.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `start` | `Point3DLike` | `LEFT` | start point |
| `end` | `Point3DLike` | `RIGHT` | end point (the arrow-tip location) |
| `thickness` | `float` | `0.02` | shaft radius |
| `height` | `float` | `0.3` | cone height; **accepts** any positive number |
| `base_radius` | `float` | `0.08` | cone base radius |
| `color` | `ParsableManimColor` | `WHITE` | whole-arrow color |
| `resolution` | `int \| tuple[int,int]` | `24` | shaft sample count |
| `**kwargs` | `Any` | — | forwarded to `Line3D`/`Cone` |

#### Sample: `Arrow3D` variations

The default white arrow contrasted against a red "big-cone" arrow (`height=0.6`, `base_radius=0.18`), with a follow label made from the tip coordinates read out by `get_end()`.

```python
from real_time_manim import ThreeDScene, Arrow3D, Text, \
    GREY_B, RED, YELLOW, UP, UR, DEGREES
from real_time_manim.vulkan_bind import MLWindow, Wait

class Arrow3DDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("01b-arrow3d", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        a = Arrow3D(start=[-2, -1, 0], end=[1.5, 0.5, 1.5])   # default white 3D arrow
        b = Arrow3D(start=[0, -2.5, 0], end=[-1.5, -2.5, 2], color=RED,   # red arrow: larger cone
                    thickness=0.08, height=0.6, base_radius=0.18)
        tip = Text("tip=(%.1f, %.1f, %.1f)" % tuple(a.get_end()),   # format the arrow-tip coordinates into a label
                   font_size=24, color=GREY_B).next_to(a.get_end(), UR, buff=0.2)   # place it next to the arrow tip
        self.add_fixed_orientation_mobjects(tip)   # lock orientation only: the text faces the camera but stays in 3D space
        self.add(a, b, tip)   # add the two arrows and the label to the scene
        print("arrow tip:", a.get_end())   # also print a copy to the console
        self.set_camera_orientation(phi=65 * DEGREES, theta=-60 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the two arrows
        self.move_camera(theta=-150 * DEGREES, run_time=1.2)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window
```

What this code does: it places two 3D arrows.

- The white one uses all defaults.
- The red one thickens the shaft (`thickness=0.08`) and enlarges the cone (`height=0.6`, `base_radius=0.18`), showing at a glance that the cone is tunable on its own.

Then `a.get_end()` reads out the white arrow's tip coordinates and formats them into a text label pinned next to the tip (`add_fixed_orientation_mobjects` locks orientation only, so the text always faces the camera). As it orbits 90°, the label follows the tip across the frame.

<video src="assets/RTM output/01b-Basic-3D-Objects-Advanced-arrow3d.mp4" controls width="560"></video>

> Note: `end` is the **arrow tip** location, not the end of the shaft — so the cone sticks out a little past `end` (by the cone height `height`). To point "from A to B", pass B's coordinates directly as `end`.

## Cone

```python
Cone(base_radius: float = 1, height: float = 1, direction: Vector3DLike = Z_AXIS, show_base: bool = False, v_range: tuple[float, float] = (0, TAU), u_min: float = 0, checkerboard_colors: Iterable[ParsableManimColor] | Literal[False] = False, **kwargs)
```

A cone defined by a base radius and a height (a `Surface` subclass), with the apex along `direction`; `set_direction()` changes the orientation and `get_start()/get_end()` return the base center / apex.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `base_radius` | `float` | `1` | base radius; **accepts** any positive number |
| `height` | `float` | `1` | height from base to apex |
| `direction` | `Vector3DLike` | `Z_AXIS` | apex direction (the cone is rotated onto it) |
| `show_base` | `bool` | `False` | whether to draw the base disk; **accepts** `True` / `False` |
| `v_range` | `tuple[float,float]` | `(0, TAU)` | azimuth range; you can cut a fan-shaped cone (e.g. `(0, PI)` for half a turn) |
| `u_min` | `float` | `0` | radius at the apex (>0 gives a "truncated" frustum) |
| `checkerboard_colors` | `Iterable[...] \| False` | `False` | checkerboard colors; `False` means a flat color |
| `**kwargs` | `Any` | — | forwarded to `Surface` (`fill_color`, `resolution`, …) |

#### Sample: `Cone` variations

On the left a standard cone with the base disk (`show_base=True`); on the right a fan-shaped cone cut by `u_min=0.5` (truncated top) + `v_range=(0, PI)` (only half a turn).

```python
from real_time_manim import ThreeDScene, Cone, Text, \
    GREEN, GREY_B, YELLOW, PI, UP, DOWN, LEFT, RIGHT, DEGREES
from real_time_manim.vulkan_bind import MLWindow, Wait

class ConeDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("01b-cone", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        a = Cone(base_radius=1, height=2, show_base=True)   # a standard cone with the base disk
        a.shift(LEFT * 2.5)   # place it on the left
        b = Cone(base_radius=1, height=2, u_min=0.5, v_range=(0, PI))   # truncated top + only half a turn
        b.set_color(GREEN)   # recolor: the "color=" parameter of a Surface subclass has no effect; call set_color after construction
        b.shift(RIGHT * 2.5)   # place it on the right
        tag1 = Text("show_base=True", font_size=24, color=GREY_B).next_to(a, DOWN)   # bottom-left label
        tag2 = Text("u_min=0.5 v_range=(0,PI)", font_size=24, color=GREY_B).next_to(b, DOWN)   # bottom-right label
        self.add(a, b, tag1, tag2)   # add the two cones and labels to the scene
        self.set_camera_orientation(phi=65 * DEGREES, theta=-30 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the shape difference
        self.move_camera(theta=-120 * DEGREES, run_time=1.2)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window
```

What this code does: on the left it places a standard cone with `show_base=True`, its base closed off by a disk; the right one changes three things at once:

- `u_min=0.5` flattens the apex into a frustum.
- `v_range=(0, PI)` generates only half a turn of azimuth, becoming "half a cone sliced open".
- and it is recolored green with `.set_color(GREEN)` (the `color=` parameter has no effect; see the note below).

Orbiting 90° to the side reveals the sliced cross-section and the flattened top.

<video src="assets/RTM output/01b-Basic-3D-Objects-Advanced-cone.mp4" controls width="560"></video>

> Note:
>
> - `u_min > 0` truncates the cone's apex into a frustum, leaving a circular hole of radius `u_min` at the top.
> - After `v_range` is trimmed the cone is "open" and you can see straight inside.
> - `direction` defaults to `Z_AXIS` (apex up); passing `RIGHT` lays it sideways.
> - For recoloring, **do not** write `Cone(..., color=GREEN)` — a `Surface` subclass swallows `color=` during construction before the faces are generated, so the color has no effect (upstream behaviour, identical in both engines); the correct form is to call `.set_color(...)` after construction (as in the sample), or pass `checkerboard_colors=False, fill_color=...`.

## Cylinder

```python
Cylinder(radius: float = 1, height: float = 2, direction: Vector3DLike = Z_AXIS, v_range: tuple[float, float] = (0, TAU), show_ends: bool = True, resolution: int | tuple[int, int] = (24, 24), **kwargs)
```

A cylinder with `direction` as its central axis (a `Surface` subclass), with top and bottom caps by default; it is the base class of `Line3D`. `set_direction()` and `add_bases()` are commonly used.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `radius` | `float` | `1` | radius |
| `height` | `float` | `2` | height along the central axis |
| `direction` | `Vector3DLike` | `Z_AXIS` | central-axis direction; **accepts** direction vectors such as `Z_AXIS`, `RIGHT` |
| `v_range` | `tuple[float,float]` | `(0, TAU)` | azimuth range; a half cylinder is possible (e.g. `(0, PI)`) |
| `show_ends` | `bool` | `True` | whether to draw the top/bottom caps; **accepts** `True` / `False` |
| `resolution` | `int \| tuple[int,int]` | `(24, 24)` | sample resolution |
| `**kwargs` | `Any` | — | forwarded to `Surface` |

#### Sample: `Cylinder` variations

On the left the default cylinder (with top and bottom caps); on the right `show_ends=False` + `v_range=(0, PI)` half a turn of wall + `direction=RIGHT` laid horizontal.

```python
from real_time_manim import ThreeDScene, Cylinder, Text, \
    GREY_B, RED, YELLOW, PI, UP, DOWN, LEFT, RIGHT, DEGREES
from real_time_manim.vulkan_bind import MLWindow, Wait

class CylinderDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("01b-cylinder", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        a = Cylinder(radius=0.8, height=2.5)   # a default cylinder with top and bottom caps
        a.shift(LEFT * 2.5)   # place it on the left
        b = Cylinder(radius=0.8, height=2.5, show_ends=False, v_range=(0, PI),   # no caps + half a turn of the wall
                     direction=RIGHT)   # make the central axis horizontal
        b.set_color(RED)   # recolor: the "color=" parameter of a Surface subclass has no effect; call set_color after construction
        b.shift(RIGHT * 2.5 + UP * 0.4)   # place it on the right, a bit higher
        tag1 = Text("show_ends=True", font_size=24, color=GREY_B).next_to(a, DOWN)   # bottom-left label
        tag2 = Text("half + no ends + direction", font_size=24, color=GREY_B).next_to(b, DOWN)   # bottom-right label
        self.add(a, b, tag1, tag2)   # add the two cylinders and labels to the scene
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the shape difference
        self.move_camera(theta=-135 * DEGREES, run_time=1.2)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window
```

What this code does: on the left is a cylinder with the defaults (`show_ends=True`, capped top and bottom, a solid tube); the right one changes three things:

- `show_ends=False` removes the caps.
- `v_range=(0, PI)` keeps only half a turn of wall, becoming a trough-shaped half cylinder.
- `direction=RIGHT` lays the central axis from vertical to horizontal.

Finally `.set_color(RED)` recolors it red. Orbiting 90° shows the inside of the wall from the open side.

<video src="assets/RTM output/01b-Basic-3D-Objects-Advanced-cylinder.mp4" controls width="560"></video>

> Note:
>
> - `direction` changes the **central-axis direction**: after passing `RIGHT`, `height` is measured along the x axis, so don't keep treating it as a vertical height.
> - `Cylinder` is the base class of `Line3D`, so all of `Line3D`'s parameters (`thickness` is really `radius`) are inherited from here.
> - Recoloring is the same as `Cone`: the `color=` parameter has no effect (it is overwritten by the checkerboard faces, upstream behaviour); call `.set_color(...)` after construction.

---

See also: [Basic 3D Objects (1)](01-Basic-3D-Objects.md) · [Surfaces](02-Surfaces.md)
