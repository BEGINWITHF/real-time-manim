# Two-dimensional coordinate system Axes

`Axes` is a rectangular coordinate system assembled from two `NumberLine`s: `x_range`/`y_range` set the data range and `x_length`/`y_length` set the on-screen length. `c2p`/`p2c` handle conversion, `plot` draws curves and `get_area` computes areas (for conversion see [Coordinate conversion](03-Coordinate-Conversion.md), for curves see [05 Function graphs](05-Function-Graphs.md)).

## Parameters

### class Axes

```python
def __init__(self, x_range: Sequence[float] | None = None, y_range: Sequence[float] | None = None,
             x_length: float | None = None, y_length: float | None = None,
             axis_config: dict | None = None, x_axis_config: dict | None = None,
             y_axis_config: dict | None = None, tips: bool = True, **kwargs: Any) -> None:
```

`x_range`/`y_range` decide **the data range and the tick step**, while `x_length`/`y_length` decide **the on-screen physical length**; together they fix the scale (= `x_length / (x_max - x_min)`).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `x_range` | `Sequence[float] \| None` | `None` → `[-7, 7, 1]` | `[x_min, x_max, x_step]`; a two-element tuple gets `step=1` filled in automatically; `step` only affects tick/label density, not the scale |
| `y_range` | `Sequence[float] \| None` | `None` → `[-4, 4, 1]` | same as above |
| `x_length` | `float \| None` | `None` → inferred from the frame width (about 12) | the x axis's on-screen length (Manim units) |
| `y_length` | `float \| None` | `None` → inferred from the frame height (about 6) | the y axis's on-screen length |
| `axis_config` | `dict \| None` | `{"include_tip": tips, "numbers_to_exclude": [0]}` | common parameters passed to **both** `NumberLine`s (`font_size`, `include_numbers`, `scaling`…) |
| `x_axis_config` | `dict \| None` | `{}` | applies to the x axis only, merged with `axis_config` (the latter has lower priority) |
| `y_axis_config` | `dict \| None` | `{"rotation": 90*DEGREES, "label_direction": LEFT}` | applies to the y axis only (rotated 90° by default) |
| `tips` | `bool` | `True` | whether both axes carry an arrow |
| `**kwargs` | — | — | forwarded to `VGroup`/`CoordinateSystem` (`color`, `stroke_width`…) |

> **Returns**: an `Axes` instance. Key semantics: when 0 is not inside `[min, max]` the coordinate system shifts automatically so that 0 (or the nearest endpoint) lands at the centre of the screen, and `c2p` stays correct. Common attributes: `x_axis`, `y_axis`, `axes`, `x_range`, `y_range`, `dimension=2`.

#### Sample: basic construction with `x_range`/`length`/`tips`/`axis_config`

Range `[-4,4]×[-3,3]`, screen `8×5`, no axis-end arrows, a smaller on-axis font size, then tick numbers, axis names, and a parabola.

```python
from real_time_manim import Scene, Axes, Text, \
    YELLOW, BLUE, GREY_B, UP, DOWN, Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class AxesCtorDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02-Axes", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[-4, 4, 1], y_range=[-3, 3, 1],   # parameters "x_range"/"y_range": data range and tick step
                  x_length=8, y_length=5,                   # parameters "x_length"/"y_length": on-screen physical length
                  tips=False, axis_config={"font_size": 24})   # parameter "tips": axis-end arrows; "axis_config": common parameters for both axes
        ax.add_coordinates()   # attach tick numbers to both axes
        labels = ax.get_axis_labels("x", "y")   # the two axis names x/y (you have to add them to the scene yourself)
        curve = ax.plot(lambda x: 0.5 * x**2, color=BLUE)   # draw a parabola along the way (see page 05 for the parameters)
        lab = Text("x_range=[-4,4,1]  y_range=[-3,3,1]  tips=False",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # parameter description label
        win.play(Create(ax), run_time=1.0)   # draw the coordinate system (including tick numbers)
        win.play(FadeIn(labels), FadeIn(lab), run_time=0.4)   # the axis names and the description label fade in
        win.play(Create(curve), run_time=1.0)   # draw the parabola
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: it first builds the coordinate system from "data range [-4,4]×[-3,3], screen 8×5", which fixes the scale (1 Manim unit per data unit in x, about 0.83 in y). `tips=False` removes the axis-end arrows and `axis_config={"font_size": 24}` shrinks the numbers on both axes at once.

`add_coordinates()` attaches tick numbers (0 is excluded by default), `get_axis_labels("x", "y")` generates the two axis names (you have to add the return value to the scene yourself), and finally `plot` draws a parabola to demonstrate "drawing a function straight onto a coordinate system".

<video src="assets/RTM output/02-Axes-ctor.mp4" controls width="560"></video>

> Note:
>
> - The return value of `get_axis_labels(...)` **does not enter the scene automatically**; forget `self.add`/`FadeIn` and it is simply empty.
> - 0 being excluded from the tick numbers is the work of the `axis_config` default `numbers_to_exclude=[0]`; to show 0, pass `axis_config={"numbers_to_exclude": []}` explicitly.

### add_coordinates

```python
def add_coordinates(self, *axes_numbers: Iterable[float] | None | dict, **kwargs) -> Self
```

Adds tick numbers or custom labels to the axes, taking arguments one by one in axis order:

- no arguments: every axis uses the default numbers
- `None`: that axis keeps its default
- `list`: show only these values
- `dict`: map values to arbitrary labels

Retrieve the labels with `ax.coordinate_labels` (a `VGroup`).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*axes_numbers` | `Iterable[float] \| None \| dict` | all `None` | given one by one in axis order (x, y, [z]); `None`=default numbers, `list`=the given values, `dict`=value→label |
| `**kwargs` | — | — | forwarded to `NumberLine.add_numbers`/`add_labels` (e.g. `font_size`) |

> **Returns**: `Self` (chainable).

#### Sample: the list / dict forms of `add_coordinates`

The x axis uses a dict to map the values 1/2 to "Mon"/"Tue"; the y axis uses a list to show only the three numbers -2/0/2; an axis given no argument keeps its default numbers.

```python
from real_time_manim import Scene, Axes, Text, \
    YELLOW, GREY_B, UP, DOWN, Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class AxesAddCoordDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02-add_coordinates", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[-3, 3, 1], y_range=[-2, 2, 1], x_length=9, y_length=5)   # default tips=True (arrows at the axis ends)
        ax.add_coordinates({1: "Mon", 2: "Tue"}, [-2, 0, 2])   # "add_coordinates": x axis dict value->label, y axis list shows only the given values
        labels = ax.get_axis_labels("x", "y")   # axis names
        lab = Text("add_coordinates({1:Mon,2:Tue}, [-2,0,2])",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # parameter description label
        win.play(Create(ax), run_time=0.9)   # draw the coordinate system (including arrows and custom labels)
        win.play(FadeIn(labels), FadeIn(lab), run_time=0.4)   # the axis names and the description label fade in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: `add_coordinates` takes arguments one by one in axis order — the x axis receives a dict, so the values 1/2 display "Mon"/"Tue" (the remaining ticks are no longer labelled); the y axis receives the list `[-2, 0, 2]` and only hangs numbers under those three ticks. For everything default, pass no arguments at all; to leave one axis alone, pass `None`.

<video src="assets/RTM output/02-Axes-addcoordinates.mp4" controls width="560"></video>

> Note:
>
> - A dict's `str` value is rendered with `MathTex` (math italic); for an upright face pass a `Tex`/`Text` object.
> - `add_coordinates` **overwrites** the numbers already on that axis; before calling it again, remove `ax.coordinate_labels` first, otherwise old and new labels stack up.

### Axis getters: get_axis / get_axes / get_x_axis / get_y_axis / get_origin / get_*_unit_size (table only)

```python
def get_axis(self, index: int) -> NumberLine
def get_axes(self) -> VGroup
def get_x_axis(self) -> NumberLine
def get_y_axis(self) -> NumberLine
def get_origin(self) -> Point3D
def get_x_unit_size(self) -> float
def get_y_unit_size(self) -> float
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `index` | `int` | required | `0`=x, `1`=y; `get_origin()` returns the scene point of `(0,0)`, and `get_*_unit_size()` returns the on-screen length of 1 data unit (the scale) |

### Axis labels: get_axis_labels / get_x_axis_label / get_y_axis_label (table only)

```python
def get_axis_labels(self, x_label: float | str | Mobject = "x", y_label: float | str | Mobject = "y") -> VGroup
def get_x_axis_label(self, label, edge=UR, direction=UR, buff=0.1, **kwargs) -> Mobject
def get_y_axis_label(self, label, edge=UR, direction=UP * 0.5 + RIGHT, buff=0.1, **kwargs) -> Mobject
```

Generate the x/y labels in one call (stored in `ax.axis_labels`), or use the individual methods to control the position precisely; **the returned labels need `self.add(...)` yourself** (see the `FadeIn(labels)` in the sample above).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `x_label` / `y_label` / `label` | `float \| str \| Mobject` | `"x"` / `"y"` | `str`/`float` are rendered with `MathTex`; you can also pass `Tex`/`Text` directly |
| `edge` | `Vector3D` | `UR` | the axis edge the label hugs |
| `direction` | `Vector3D` | see the signature | further placement direction relative to `edge` |
| `buff` | `float` | `0.1` | distance to the axis |
| `**kwargs` | — | — | forwarded (the `ThreeDAxes` version also supports `rotation`, `rotation_axis`) |

---

See also: [Coordinate conversion](03-Coordinate-Conversion.md) · [Guide lines and line graphs](02b-Lines-and-Plots.md) · [Plotting function curves](05-Function-Graphs.md) · [Number line NumberLine](01-NumberLine.md)
