# Polar and 3D coordinates

This section is about non-Cartesian coordinates and 3D:

- `PolarPlane`, the polar plane (`plot_polar_graph` draws a line for `r=f(θ)`);
- `ThreeDAxes`, the 3D coordinate system (`c2p(x,y,z)` conversion, `move_camera` rotates the view);
- `Axes.plot_surface`, parametric surfaces.

All three samples are really rendered (`surface` is covered in the last section).

> Note: A 3D scene must use `ThreeDScene`, and you must wire up `self.play = win.play` before `move_camera`. `move_camera` calls `self.play` internally, so if you don't wire it up it errors out or the picture freezes.

## PolarPlane

```python
def __init__(
    self,
    radius_max: float = 4.0,
    size: float | None = None,
    radius_step: float = 1,
    azimuth_step: int | None = None,
    azimuth_units: str = "PI radians",
    azimuth_compact_fraction: bool = True,
    azimuth_offset: float = 0,
    azimuth_direction: str = "CCW",
    azimuth_label_buff: float = 0.1,
    azimuth_label_font_size: int = 24,
    radius_config: dict[str, Any] | None = None,
    background_line_style: dict[str, Any] | None = None,
    faded_line_style: dict[str, Any] | None = None,
    faded_line_ratio: int = 1,
    make_smooth_after_applying_functions: bool = True,
    **kwargs: Any,
):
```

Polar plane: concentric circles = radius ticks, radial lines = angle ticks; supports `add_coordinates()` (radius numbers + angle labels).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `radius_max` | `float` | `4.0` | maximum radius |
| `size` | `float \| None` | `None` | plane diameter (once given, it overrides the automatic scaling from the radius) |
| `radius_step` | `float` | `1` | spacing between concentric circles |
| `azimuth_units` | `str` | `"PI radians"` | angle label unit: `"PI radians"`/`"radians"`/`"degrees"` |
| `azimuth_step` | `int \| None` | `None` | radial-line spacing (number of π fractions) |
| `azimuth_direction` | `str` | `"CCW"` | positive angle direction (`CCW`/`CW`) |
| `azimuth_label_font_size` | `int` | `24` | angle-label font size |
| `background_line_style` | `dict \| None` | `None` | style of the concentric circles and radial lines (`stroke_color`/`stroke_width`…) |
| `faded_line_ratio` | `int` | `1` | density of the faded subdivision lines (`0` turns them off) |

#### Sample: `plot_polar_graph` drawing a five-petal rose

`PolarPlane(size=6)` labels angles in π fractions, `add_coordinates()` adds tick numbers; `plot_polar_graph(lambda th: 2*sin(5θ))` draws a five-petal rose.

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, ThreeDScene, ThreeDAxes, PolarPlane, Dot, Text, np,
    YELLOW, TEAL, BLUE, ORANGE, RED, GREEN, GREY_B, UP, DOWN, UR, TAU,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class PolarDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("07-PolarPlane", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        plane = PolarPlane(size=5,   #parameter "size": plane diameter
                           azimuth_units="PI radians",   #parameter "azimuth_units": label azimuth angles in π fractions
                           background_line_style={"stroke_color": TEAL, "stroke_width": 2},   #style of the concentric circles and radial lines
                           ).add_coordinates()   #"add_coordinates": radius numbers + angle labels
        rose = plane.plot_polar_graph(lambda th: 2 * np.sin(th * 5),   #"plot_polar_graph": draw a polar curve for r=f(θ)
                                      theta_range=[0, TAU], color=ORANGE)   #five-petal rose
        lab = Text("plot_polar_graph(2*sin(5*theta))",
                   font_size=18, color=GREY_B).to_edge(DOWN, buff=0.3)   #parameter caption label
        win.play(Create(plane), FadeIn(lab), run_time=1.0)   #the polar plane (with labels) and the caption appear together
        win.play(Create(rose), run_time=1.2)   #draw the rose curve
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window


# ===== Sample 2: ThreeDAxes 3D coordinate system ==========================
```

What this code does:

- `PolarPlane`'s concentric circles and radial lines are a grid styled uniformly by `background_line_style`.
- `plot_polar_graph` accepts a scalar `r(θ)` function (not an `(x,y)` vector), samples it over `theta_range=[0, TAU]`, and converts to Cartesian points to connect; `2*sin(5θ)` is the classic five-petal rose.

<video src="assets/RTM output/07-Polar-and-3D-Coordinates-polar.mp4" controls width="560"></video>

> Note:
>
> - The function passed to `plot_polar_graph` returns a **radius** (scalar), not coordinates.
> - RTM and CE differ slightly in the drawing order of the intermediate frames of `Create(PolarPlane)` (the final picture is identical); when comparing frame by frame, accept on the final frame.

## ThreeDAxes

```python
def __init__(
    self,
    x_range: Sequence[float] | None = (-6, 6, 1),
    y_range: Sequence[float] | None = (-5, 5, 1),
    z_range: Sequence[float] | None = (-4, 4, 1),
    x_length: float | None = 10.5,
    y_length: float | None = 10.5,
    z_length: float | None = 6.5,
    z_axis_config: dict[str, Any] | None = None,
    z_normal: Vector3DLike = array([0.0, -1.0, 0.0]),
    num_axis_pieces: int = 20,
    light_source: Point3DLike = array([-7.0, -9.0, 10.0]),
    depth: Any = None,
    gloss: float = 0.5,
    **kwargs,
):
```

3D coordinate system (the 3D version of `Axes`): x/y/z axes + `c2p(x, y, z)` 3D conversion, `add_coordinates(x, y, z)` adds ticks per axis.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `x_range` / `y_range` / `z_range` | `Sequence[float] \| None` | `(-6,6,1)`/`(-5,5,1)`/`(-4,4,1)` | data range and tick step of each axis |
| `x_length` / `y_length` / `z_length` | `float \| None` | `10.5`/`10.5`/`6.5` | on-screen length of each axis |
| `z_axis_config` | `dict \| None` | `None` | z-axis style |
| `z_normal` | `Vector3DLike` | `[0,-1,0]` | z-axis orientation |
| `gloss` | `float` | `0.5` | **Upstream parameter; RTM's Vulkan render path does not read it (no visual effect)** — it only appears in manim's own OpenGL shaders (`manim/renderer/shaders/**/*.glsl`); RTM does not go through that path, so changing this value has no effect |

#### Sample: `ThreeDAxes` + `move_camera` to see depth

After setting up the ticks on `ThreeDAxes`, place two space points `c2p(1,1,2)` / `c2p(-2,2,-3)`; `move_camera(theta=-0.6, phi=1.1)` rotates to a 3D view and the depth difference between the two points becomes immediately visible.

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, ThreeDScene, ThreeDAxes, PolarPlane, Dot, Text, np,
    YELLOW, TEAL, BLUE, ORANGE, RED, GREEN, GREY_B, UP, DOWN, UR, TAU,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class ThreeDAxesDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        self.play = win.play   #move_camera calls self.play internally, so wire it up first
        title = Text("07-ThreeDAxes", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        ax = ThreeDAxes(x_range=(-3, 3, 1), y_range=(-3, 3, 1), z_range=(-4, 4, 1),   #data range of the three axes
                        x_length=7, y_length=7, z_length=5)   #on-screen length of each axis
        ax.add_coordinates(range(-2, 3), None, range(-4, 5, 2))   #"add_coordinates": given ticks for x/z, default for y
        d1 = Dot(ax.c2p(1, 1, 2), color=RED)   #"c2p": 3D data coordinates -> scene point
        d2 = Dot(ax.c2p(-2, 2, -3), color=GREEN)
        lab = Text("ThreeDAxes + c2p(1,1,2) / c2p(-2,2,-3)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   #method caption label
        win.play(Create(ax), FadeIn(lab), run_time=0.8)   #the 3D axes and the caption appear together
        win.play(FadeIn(d1), FadeIn(d2), run_time=0.4)   #the two space points fade in
        self.move_camera(theta=-0.6, phi=1.1, run_time=1.0)   #"move_camera": rotate to a 3D view to show depth
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window


# ===== Sample 3: Axes.plot_surface parametric surface =====================
```

What this code does:

- `self.play = win.play` wires manim's `self.play` to the RTM window (`move_camera` calls it internally).
- `c2p(1,1,2)` converts 3D data coordinates into a scene point, fed straight to `Dot`.
- `move_camera(theta=-0.6, phi=1.1)` rotates the camera — from the initial view the red and green points' overlap hides the depth, but after rotating, the distance along z opens up immediately.

<video src="assets/RTM output/07-Polar-and-3D-Coordinates-threed.mp4" controls width="560"></video>

> Note:
>
> - The **order** is `win.scene = self` first, then `self.play = win.play`, for `move_camera` to take effect.
> - The three arguments of `add_coordinates` correspond to the x/y/z axes (`None` = default ticks).

## plot_surface

`Axes.plot_surface(function, u_range, v_range, resolution)` samples `f(u, v)` into a parametric surface (`resolution=(u segments, v segments)`) and returns a `Surface`. It can be `FadeIn`-ed / `Create`-d / transformed like an ordinary mobject.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `function` | `Callable[[float, float], float]` | required | parametric height function `f(u, v)` |
| `u_range` / `v_range` | `Sequence[float]` | `(0,1)` | the two parameter intervals |
| `resolution` | `Sequence[int]` | `(32,32)` | how many segments to cut along u/v (fewer segments, coarser faces) |

#### Sample: `plot_surface(sin(u)·cos(v))` to see the surface's undulation

Draw `sin(u)*cos(v)` on the same `ThreeDAxes`; `resolution=(12, 12)` keeps the faces clearly visible; finally `move_camera` rotates to a 3D view to show the undulation.

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, ThreeDScene, ThreeDAxes, PolarPlane, Dot, Text, np,
    YELLOW, TEAL, BLUE, ORANGE, RED, GREEN, GREY_B, UP, DOWN, UR, TAU,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class SurfaceDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        self.play = win.play   #move_camera calls self.play internally, so wire it up first
        title = Text("07-plot_surface", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        ax = ThreeDAxes(x_range=(-3, 3, 1), y_range=(-3, 3, 1), z_range=(-2, 2, 1))   #data range of the three axes
        surf = ax.plot_surface(lambda u, v: np.sin(u) * np.cos(v),   #"plot_surface": parametric surface
                               u_range=(-3, 3), v_range=(-3, 3), resolution=(12, 12))   #u/v ranges and grid resolution
        lab = Text("plot_surface(sin(u)*cos(v))",
                   font_size=24, color=GREY_B).to_edge(DOWN)   #method caption label
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   #the axes and the caption appear together
        win.play(FadeIn(surf), run_time=0.6)   #the surface fades in
        self.move_camera(theta=-0.6, phi=1.1, run_time=1.0)   #rotate to a 3D view to show the surface's undulation
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window
```

What this code does: `plot_surface` first cuts `u_range × v_range` into a parametric grid according to `resolution`; for each grid cell it takes the four corners `c2p(u, v, f(u,v))` and joins them into one face, then hands it to the renderer.

`resolution=(12, 12)` gives 144 faces in total; after `FadeIn` each face is shaded by its own normal, so after rotating the view you can see the peaks and troughs of `sin(u)·cos(v)`. This is a **parametric surface** — `u` / `v` do not go through `c2p`; they are fed directly to `plot_surface`'s own height function.

<video src="assets/RTM output/07-Polar-and-3D-Coordinates-surface.mp4" controls width="560"></video>

> Note:
>
> - `plot_surface` is a **parametric surface** (`(u,v) → f(u,v)`), not the same thing as `plot` (`x → f(x)`).
> - `resolution` counts **segments**, not points: `(12, 12)` yields 12×12 = 144 faces; too few segments makes the surface look polygonal.
>
> This page's RTM version is aligned frame by frame with the ManimCE version (198 frames / 3.30s, `frames>4.0: 0`, covered by `tests/test_plot_surface.py`).

---

See also: [Two-dimensional coordinate system](02-Axes.md) · [Grids and the complex plane](04-Grids-and-Complex-Plane.md) · [Plotting function curves](05-Function-Graphs.md)
