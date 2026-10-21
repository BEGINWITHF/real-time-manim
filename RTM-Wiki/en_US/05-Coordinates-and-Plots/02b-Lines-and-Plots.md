# Guide lines and line graphs

Methods on `Axes` for "reading a graph" annotation and for "discrete-data line graphs": adding horizontal and vertical guide lines to a curve/point (`get_vertical_line` etc.), and drawing a line graph from discrete data points (`plot_line_graph`).

## Methods

### get_vertical_line / get_horizontal_line / get_lines_to_point

```python
def get_vertical_line(self, point: Point3DLike, **kwargs) -> Line
def get_horizontal_line(self, point: Point3DLike, **kwargs) -> Line
def get_lines_to_point(self, point: Point3DLike, **kwargs) -> VGroup
```

Draws a guide line from the x axis / y axis to a scene point (a `DashedLine` by default); the most common annotation when "reading a graph"; `get_lines_to_point` gives both the horizontal and the vertical line at once.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `point` | `Point3DLike` | required | the target point (usually from `ax.c2p(...)`) |
| `**kwargs` | — | — | forwarded to `get_line_from_axis_to_point`: `line_func` (e.g. `Line`), `line_config` (e.g. `{"dashed_ratio": 0.85}`), `color`, `stroke_width` |

> **Returns**: `Line` / `VGroup` (hand it to `play`, or `add` it to the scene).

### get_line_from_axis_to_point

```python
def get_line_from_axis_to_point(self, index: int, point: Point3DLike, line_func: type[Line] = DashedLine,
                                line_config: dict | None = None, color: ParsableManimColor | None = None,
                                stroke_width: float = 2) -> Line
```

The general version behind the two methods above: draw a line from axis number `index` to `point`, with a customisable line class.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `index` | `int` | required | `0`=x axis, `1`=y axis |
| `point` | `Point3DLike` | required | target point |
| `line_func` | `type[Line]` | `DashedLine` | line class, e.g. `Line`, `Arrow` |
| `line_config` | `dict \| None` | `None` | parameters passed to `line_func` |
| `color` | `ParsableManimColor \| None` | the mobject's default color | line color |
| `stroke_width` | `float` | `2` | stroke width |

> **Returns**: `Line`.

#### Sample: a vertical dashed line / both lines / the general version with a chosen line class

Three kinds of guide line drawn one after another on the same coordinate system: a blue vertical dashed line from the x axis to a point, a grey pair of horizontal and vertical lines, and a green **solid** line from the y axis to a point (the general version with `line_func=Line`).

```python
from real_time_manim import Scene, Axes, Dot, Line, Text, \
    YELLOW, RED, BLUE, GREEN, GREY, GREY_B, UP, DOWN, Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class GuideLinesDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02b-guide-lines", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[-4, 4, 1], y_range=[-3, 3, 1],
                  x_length=9, y_length=5.5).add_coordinates()   # a coordinate system with tick numbers
        p = ax.c2p(2, 1.5)   # target point: data coordinates (2, 1.5)
        dot = Dot(p, color=RED)   # the target-point dot
        vline = ax.get_vertical_line(p, color=BLUE)   # "get_vertical_line": a vertical dashed line from the x axis to the point
        both = ax.get_lines_to_point(ax.c2p(-3, -1), color=GREY)   # "get_lines_to_point": both a horizontal and a vertical guide line
        solid = ax.get_line_from_axis_to_point(   # "get_line_from_axis_to_point": the general version, with a chosen line class
            1, ax.c2p(3, -2), line_func=Line, color=GREEN)   # pull a solid line from the y axis (index=1) to the point
        lab = Text("vertical / lines_to_point / from_axis(1, Line)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # method description label
        win.play(Create(ax), run_time=0.8)   # draw the coordinate system
        win.play(FadeIn(lab), run_time=0.3)   # the description label fades in
        win.play(FadeIn(dot), run_time=0.3)   # the target point fades in
        win.play(Create(vline), run_time=0.6)   # the blue vertical dashed line grows from the x axis to the point
        win.play(Create(both), run_time=0.6)   # the grey horizontal and vertical guide lines
        win.play(Create(solid), run_time=0.6)   # the green solid line connects the y axis to the point
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: a red dot is pinned at the data coordinate (2, 1.5), and `get_vertical_line` drops a dashed line up from the **x axis**; `get_lines_to_point` gives a horizontal and a vertical line at (-3, -1) in one go; finally the general version `get_line_from_axis_to_point(1, ...)` pulls a **solid** line (`line_func=Line`) from the **y axis** (`index=1`) to (3, -2). The products of all three methods are ordinary `Line`-family objects that `Create` can draw directly.

<video src="assets/RTM output/02b-Lines-and-Plots-lines.mp4" controls width="560"></video>

> Note:
>
> - A guide line's anchor is a **scene point**, not a data coordinate: call `ax.c2p(...)` first, then pass it in.
> - `get_vertical_line` always starts from the x axis; to start from the y axis, use the general version with `index=1`.

### plot_line_graph

```python
def plot_line_graph(self, x_values: Iterable[float], y_values: Iterable[float],
                    z_values: Iterable[float] | None = None, line_color: ParsableManimColor = PURE_YELLOW,
                    add_vertex_dots: bool = True, vertex_dot_radius: float = 0.08,
                    vertex_dot_style: dict | None = None, **kwargs) -> VDict
```

Draws a line graph from **discrete data points** (not function sampling): each point is `c2p`-converted and then joined by straight segments, and by default a `Dot` is placed at every vertex. Returns a `VDict`; the polyline is `line_graph["line_graph"]` and the dots are `line_graph["vertex_dots"]`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `x_values` | `Iterable[float]` | required | x data |
| `y_values` | `Iterable[float]` | required | y data (must be the same length as x) |
| `z_values` | `Iterable[float] \| None` | `None` (all 0) | 3D data |
| `line_color` | `ParsableManimColor` | `PURE_YELLOW` | polyline color |
| `add_vertex_dots` | `bool` | `True` | whether to draw the vertex dots |
| `vertex_dot_radius` | `float` | `0.08` | dot radius |
| `vertex_dot_style` | `dict \| None` | `None` | style passed to `Dot` |
| `**kwargs` | — | — | passed to the polyline `VGroup` (e.g. `stroke_width=4`) |

> **Returns**: a `VDict` (key `"line_graph"` polyline, `"vertex_dots"` dots).

#### Sample: a `plot_line_graph` discrete line graph

Four discrete data points joined into a golden polyline (stroke width 4), then the vertex dots fade in — the "corner" between the two segments is the data point itself.

```python
from real_time_manim import Scene, Axes, Text, \
    YELLOW, GREY_B, UP, DOWN, GOLD_E, Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class LineGraphDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02b-plot_line_graph", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[0, 5, 1], y_range=[0, 5, 1],
                  x_length=8, y_length=5).add_coordinates()   # a first-quadrant coordinate system
        lg = ax.plot_line_graph(x_values=[0, 1.5, 2.8, 4],   # "plot_line_graph": joins discrete data points (not function sampling)
                                y_values=[1, 3, 4, 2.5],
                                line_color=GOLD_E, stroke_width=4)   # parameters "line_color"/"stroke_width": polyline color and stroke width
        lab = Text("plot_line_graph(x=[0,1.5,2.8,4], y=[1,3,4,2.5])",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # parameter description label
        win.play(Create(ax), run_time=0.7)   # draw the coordinate system
        win.play(FadeIn(lab), run_time=0.3)   # the description label fades in
        win.play(Create(lg["line_graph"]), run_time=1.0)   # the polyline itself (the returned VDict's "line_graph" key)
        win.play(FadeIn(lg["vertex_dots"]), run_time=0.5)   # the vertex dots (the "vertex_dots" key)
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: `plot_line_graph` takes the four data points `(0,1) (1.5,3) (2.8,4) (4,2.5)`, converts each with `c2p` and joins them with straight segments — it draws a **discrete polyline** and does no interpolation between points, so the "corners" are the data points themselves. The return value is a `VDict`: take the polyline from `lg["line_graph"]` and the vertex dots from `lg["vertex_dots"]`, and the two can be animated separately (the sample draws the line first and lights up the dots afterwards).

<video src="assets/RTM output/02b-Lines-and-Plots-linegraph.mp4" controls width="560"></video>

> Note: `x_values`/`y_values` must have the same length (internally `zip(strict=True)`, a mismatch raises `ValueError`); for a smooth curve use [`ax.plot`](05-Function-Graphs.md) instead.

---

See also: [Two-dimensional coordinate system](02-Axes.md) · [Coordinate conversion](03-Coordinate-Conversion.md) · [Plot labels and helper lines](05b-Plot-Labels-and-Helper-Lines.md)
