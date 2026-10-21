# Grids and the complex plane (NumberPlane / ComplexPlane)

Laying a background grid over `Axes` gives the most common "canvas" coordinate system: `NumberPlane` provides the graph paper, and `ComplexPlane` is its complex-numbered version (the y-axis labels carry an `i`). `c2p`/`n2p`/`plot`/`add_coordinates` all work on both; for the parameters see [2D coordinate systems](02-Axes.md).

## NumberPlane

```python
def __init__(self, x_range: Sequence[float] | None = None, y_range: Sequence[float] | None = None,
             x_length: float | None = None, y_length: float | None = None,
             background_line_style: dict | None = None, faded_line_style: dict | None = None,
             faded_line_ratio: int = 1, make_smooth_after_applying_functions: bool = True,
             **kwargs: Any) -> None:
```

No tick numbers and no arrow tips by default; the axis labels point down-right; `c2p`/`plot`/`add_coordinates` are all inherited from `Axes`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `x_range` / `y_range` | `Sequence[float] \| None` | `±frame_x_radius` / `±frame_y_radius`, step 1 | same as `Axes`; the default uses the **un-rounded** frame radii |
| `x_length` / `y_length` | `float \| None` | `None` | `None` ⇒ 1 data unit = 1 Manim unit (the grid fills the screen) |
| `background_line_style` | `dict \| None` | `{"stroke_color": BLUE_D, "stroke_width": 2, "stroke_opacity": 1}` | style of the main grid lines (`stroke_color`/`stroke_width`/`stroke_opacity` are all adjustable) |
| `faded_line_style` | `dict \| None` | the main style with its numbers halved | style of the faded subdivision lines |
| `faded_line_ratio` | `int` | `1` | subdivision density: `2` → 4 parts per cell, `3` → 9 parts, `0` draws no faded lines |
| `make_smooth_after_applying_functions` | `bool` | `True` | no effect at present, keep the default |
| `**kwargs` | — | — | passed through to `Axes` (`axis_config`, `y_axis_config`, `tips`…) |

> **Returns**: a `NumberPlane` instance. After construction, `background_lines` and `faded_lines` (both `VGroup`) can be taken out on their own.

#### Sample: `background_line_style` / `faded_line_ratio` grid canvas

The main grid lines become semi-transparent thick teal lines (`stroke_opacity=0.6`, `stroke_width=4`), and `faded_line_ratio=2` subdivides every cell into 2×2 faded lines again, so the whole screen is one evenly subdivided sheet of graph paper.

```python
from real_time_manim import (
    Scene, NumberPlane, ComplexPlane, Dot, MathTex, Text,
    YELLOW, TEAL, BLUE_E, GREEN, GREY_B, UP, DOWN, UR,
    Create, FadeIn, GrowArrow, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class NumberPlaneDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("04-NumberPlane", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        plane = NumberPlane(
            background_line_style={"stroke_color": TEAL, "stroke_width": 4, "stroke_opacity": 0.6},   # parameter "background_line_style": style of the main grid lines
            faded_line_ratio=2,   # parameter "faded_line_ratio": subdivide each cell into 2x2 faded lines
        )
        lab = Text("faded_line_ratio=2  (each cell -> 4)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # parameter summary label
        win.play(Create(plane), run_time=1.2)   # draw the main grid + faded subdivision lines
        win.play(FadeIn(lab), run_time=0.3)   # the summary label fades in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: `NumberPlane()` with no ranges passed is "the default sheet of graph paper filling the screen"; `background_line_style` only changes the main grid's colour/width/opacity, and `faded_line_ratio` controls the subdivision density of each cell (set it to `0` to draw only the main grid). `Create` draws the main grid and the faded lines together, in order.

<video src="assets/RTM output/04-Grids-and-Complex-Plane-numberplane.mp4" controls width="560"></video>

> Note: `NumberPlane` defaults to `x_length=None` (1 data unit = 1 Manim unit), so changing `x_range` directly changes how dense the grid is; to fix the on-screen proportions pass `x_length`/`y_length` explicitly, just like `Axes`.

## ComplexPlane

```python
def __init__(self, **kwargs: Any) -> None:
```

A `NumberPlane` customised for complex numbers: the y-axis labels automatically carry an `i` (`1i, 2i, -1i…`), and every parameter is inherited from `NumberPlane` (`x_range`, `y_range`, `background_line_style`…).

| Method | Signature | Description |
| --- | --- | --- |
| `number_to_point` / `n2p` | `(number: float \| complex) -> np.ndarray` | `n2p(2 + 1j)` → scene point; a complex number locates the point directly |
| `point_to_number` / `p2n` | `(point) -> complex` | scene point → complex number (the inverse of `n2p`) |
| `get_coordinate_labels` | `(*numbers, **kwargs) -> VGroup` | by default produces real labels on the x axis and `1i, 2i…` on the y axis |
| `add_coordinates` | `(*numbers, **kwargs) -> Self` | adds coordinate labels; pass `[2, 1j, -3, -2j]` to customise |

#### Sample: landing a complex number with `n2p` + a vector with `get_vector`

On a blue complex plane: a yellow dot is placed directly with `n2p(2+1j)` and paired with a `MathTex` label, and a green arrow runs from the origin to `1-2i` with `get_vector([1, -2])`.

```python
from real_time_manim import (
    Scene, NumberPlane, ComplexPlane, Dot, MathTex, Text,
    YELLOW, TEAL, BLUE_E, GREEN, GREY_B, UP, DOWN, UR,
    Create, FadeIn, GrowArrow, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class ComplexPlaneDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("04-ComplexPlane", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        cplane = ComplexPlane(
            x_range=[-3, 3, 1], y_range=[-3, 3, 1],   # range/step parameters are the same as for NumberPlane
            background_line_style={"stroke_color": BLUE_E, "stroke_width": 2},   # switch the grid lines to blues
        ).add_coordinates()   # the y-axis labels carry an i automatically (1i, 2i…)
        d1 = Dot(cplane.n2p(2 + 1j), color=YELLOW)   # "n2p": convert the complex number 2+i straight into a scene point
        label = MathTex("2+i").next_to(d1, UR, buff=0.2)   # complex-number label
        vec = cplane.get_vector([1, -2], color=GREEN)   # "get_vector": an arrow from the origin to (1,-2)
        lab = Text("n2p(2+1j) + get_vector([1,-2])",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # method summary label
        win.play(Create(cplane), run_time=1.0)   # draw the complex plane (including the i labels)
        win.play(FadeIn(lab), run_time=0.3)   # the summary label fades in
        win.play(FadeIn(d1), Write(label), run_time=0.6)   # the yellow dot and the "2+i" label enter
        win.play(GrowArrow(vec), run_time=0.6)   # the green arrow grows out of the origin
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: `ComplexPlane` is just a `NumberPlane` with complex-number semantics. After `add_coordinates()` the y-axis labels become `1i/2i`; `n2p(2+1j)` converts the complex number straight into scene coordinates for the yellow dot; `get_vector([1, -2])` pulls an arrow from the origin to `1-2i` (the coordinates are passed in x/y order).

<video src="assets/RTM output/04-Grids-and-Complex-Plane-complexplane.mp4" controls width="560"></video>

> Note:
>
> - `get_vector` takes an **x/y sequence of numbers** `[1, -2]`, not a complex number; for a complex number call `n2p` first and then draw the arrow by hand.
> - the `i` labels on the y axis go through `MathTex`; the font depends on the RTM/CE typesetting engine and is a normal difference.

## NumberPlane.get_vector (table only)

```python
def get_vector(self, coords: Sequence[float], **kwargs) -> Arrow
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `coords` | sequence | required | data coordinates (x, y order); returns an `Arrow` from the **origin** to that point (`buff=0`) |
| `**kwargs` | — | — | passed to `Arrow` (`color`, `stroke_width`, `max_stroke_width_to_length_ratio`…) |

> **Returns**: an `Arrow`; see the ComplexPlane section above for a sample (`GrowArrow` grows it out).

## NumberPlane.prepare_for_nonlinear_transform (table only)

```python
def prepare_for_nonlinear_transform(self, num_inserted_curves: int = 50) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `num_inserted_curves` | `int` | `50` | minimum number of Bézier segments inserted into every path, to make later non-linear animations such as `ApplyFunction` smooth; call it once before the deformation animation |

---

See also: [2D coordinate systems](02-Axes.md) · [Coordinate conversion](03-Coordinate-Conversion.md) · [Polar and 3D coordinate systems](07-Polar-and-3D-Coordinates.md)
