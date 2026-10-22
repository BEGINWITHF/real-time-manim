# Plot labels and helper lines

This section covers how to annotate and support a curve drawn by `ax.plot`:

- `plot_implicit_curve` draws the implicit curve `f(x,y)=0`;
- `get_graph_label` / `get_T_label` place labels and triangle markers on the curve;
- `get_vertical_lines_to_graph` pulls vertical dashed lines from the x axis up to the curve;
- `get_secant_slope_group` builds a Δx / Δy / secant-line group.

Tangents and derivatives are in [Derivatives, antiderivatives and tangents](05c-Derivatives-Antiderivatives-and-Tangents.md).

> Note: these methods all hang off `Axes` (and subclasses such as `NumberPlane`), so a coordinate system must exist first. Also, the `graph` parameter must be the return value of `ax.plot(...)`, because the methods read its sampling function internally.

## Axes.plot_implicit_curve

```python
def plot_implicit_curve(
    self,
    func: Callable[[float, float], float],
    min_depth: int = 5,
    max_quads: int = 1500,
    **kwargs: Any,
) -> ImplicitFunction:
```

It finds the level curve of `f(x, y) = 0` and returns an `ImplicitFunction`. A quadtree recursively subdivides the sampling region; `min_depth` is the minimum recursion depth and `max_quads` the maximum number of subdividing blocks.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `func` | `Callable[[float, float], float]` | required | e.g. `lambda x, y: x**2 + y**2 - 4`, to find the zero level curve |
| `min_depth` | `int` | `5` | minimum quadtree depth; the smaller it is, the faster and the coarser |
| `max_quads` | `int` | `1500` | maximum number of subdividing blocks, to stop a pathological function from exploding |
| `**kwargs` | — | — | passed to the curve (`color`, `stroke_width`…) |

#### Sample: drawing an implicit circle with `plot_implicit_curve`

The coordinate system's framing matches radius 2 (`x_range=[-3,3]`, `y_range=[-2,2]`), and the level curve of `x²+y²-4=0` is the circle of radius 2.

```python
from real_time_manim import (
    Scene, Axes, Text,
    YELLOW, TEAL, PURPLE_B, GREEN, GREY, GREY_B, UP, DOWN, DL,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class ImplicitDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("05b-plot_implicit_curve", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[-3, 3, 1], y_range=[-2, 2, 1],
                  x_length=8, y_length=5)   # range matches radius 2
        circle = ax.plot_implicit_curve(lambda x, y: x**2 + y**2 - 4,   # "plot_implicit_curve": the level curve of f(x,y)=0
                                        color=TEAL)   # x²+y²=4, i.e. the circle of radius 2
        lab = Text("plot_implicit_curve(x^2+y^2-4=0)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # parameter summary label
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   # the coordinate system and the label enter together
        win.play(Create(circle), run_time=1.2)   # draw the implicit circle
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: `plot_implicit_curve` does not need an x range. Inside the framing region it runs a quadtree subdivision on `f(x,y)`, halving the blocks whose sign changes until `min_depth`, and then joins the boundary points into a level curve. Note that the framing (`x_range` / `y_range`) must be able to enclose the whole curve, otherwise only the visible part is drawn.

<video src="assets/RTM output/05b-Plot-Labels-and-Helper-Lines-implicit.mp4" controls width="560"></video>

> Note:
>
> - `plot_implicit_curve` only evaluates inside the coordinate system's framing region; the part of the curve beyond the framing is not drawn.
> - it returns an `ImplicitFunction`, which **cannot** be passed to methods such as `get_area` / `plot_derivative_graph` that need an analytic function.

## Axes.get_graph_label

```python
def get_graph_label(
    self,
    graph: ParametricFunction,
    label: float | str | VMobject = "f(x)",
    x_val: float | None = None,
    direction: Sequence[float] = RIGHT,
    buff: float = MED_SMALL_BUFF,
    color: ParsableManimColor | None = None,
    dot: bool = False,
    dot_config: dict[str, Any] | None = None,
) -> Mobject:
```

It places a label at the given `x_val` on the curve (rendered as `MathTex` by default), optionally adding a dot on the curve at the same time.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `graph` | `ParametricFunction` | required | the return value of `ax.plot` |
| `label` | `float \| str \| VMobject` | `"f(x)"` | label content (a string is rendered through `MathTex`) |
| `x_val` | `float \| None` | `None` → the curve's midpoint | the x the label sits at |
| `direction` | `Sequence[float]` | `RIGHT` | the label's direction relative to the dot, e.g. `DL` (down-left) |
| `buff` | `float` | `MED_SMALL_BUFF` | spacing between the label and the dot |
| `color` | `ParsableManimColor \| None` | `None` → the curve colour | label colour |
| `dot` | `bool` | `False` | whether to also add a dot on the curve |
| `dot_config` | `dict \| None` | `None` | dot configuration (`radius`, `color`…) |

#### Sample: curve labels with `get_graph_label` + `get_T_label`

Two kinds of annotation are demonstrated on the parabola `y=x²`:

- `get_graph_label(x_val=-2, direction=DL, dot=True)` puts an "x²" label at the lower left and adds a dot;
- `get_T_label(x_val=4, label="x-value")` builds a marker group of triangle + vertical line + text at x=4.

```python
from real_time_manim import (
    Scene, Axes, Text,
    YELLOW, TEAL, PURPLE_B, GREEN, GREY, GREY_B, UP, DOWN, DL,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class LabelsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("05b-graph_label_T_label", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[-4, 4, 1], y_range=[-1, 7, 1],
                  x_length=9, y_length=5.5)   # parabola framing
        curve = ax.plot(lambda x: x**2, color=PURPLE_B)   # the parabola y=x²
        lab = Text("get_graph_label(x_val=-2) + get_T_label(x_val=4)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # parameter summary label
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   # the coordinate system and the label enter together
        win.play(Create(curve), run_time=0.8)   # draw the parabola

        label = ax.get_graph_label(curve, "x^2", x_val=-2,   # "get_graph_label": put a label at x=-2 on the curve
                                   direction=DL, dot=True)   # parameter "dot": also add a dot on the curve
        win.play(FadeIn(label), run_time=0.5)   # the label and the dot fade in

        t_label = ax.get_T_label(x_val=4, graph=curve,   # "get_T_label": the marker group at x=4
                                 label="x-value")   # triangle + vertical line + text label
        win.play(FadeIn(t_label), run_time=0.5)   # the T marker group fades in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: both annotations are "construct first, play later".

- `get_graph_label` produces the label with `MathTex("x^2")` and then `next_to`s the point at x=-2 on the curve; `direction=DL` sets the placement direction and `dot=True` pins a dot on the curve as well.
- `get_T_label` returns a `VGroup` (triangle + vertical line pulled from the x axis up to the curve + text), and one `FadeIn` brings the whole group on screen.

<video src="assets/RTM output/05b-Plot-Labels-and-Helper-Lines-labels.mp4" controls width="560"></video>

> Note:
>
> - `get_graph_label`'s `label` goes through `MathTex` (real LaTeX by default; compiled by the Typst backend when the `real-time-manim[typst]` extra is installed and `RTM_TYPST=0` is not set), so write `x^2` rather than `x²`.
> - `get_T_label`'s triangle sits on the x axis and the text beside the line; their `color`s are separate and are controlled with `triangle_color` / `label_color`.

## Axes.get_T_label

```python
def get_T_label(
    self,
    x_val: float,
    graph: ParametricFunction,
    label: float | str | Mobject | None = None,
    label_color: ParsableManimColor | None = None,
    triangle_size: float = MED_SMALL_BUFF,
    triangle_color: ParsableManimColor | None = WHITE,
    line_func: type[Line] = Line,
    line_color: ParsableManimColor = PURE_YELLOW,
) -> VGroup:
```

It builds the whole marker group "triangle on the x axis + vertical line + text label", commonly used to point at the curve point corresponding to an x value.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `x_val` | `float` | required | the x the marker sits at |
| `graph` | `ParametricFunction` | required | the curve the vertical line is pulled up to |
| `label` | `float \| str \| Mobject \| None` | `None` → no text | text label (a string goes through `MathTex`) |
| `label_color` | `ParsableManimColor \| None` | `None` | text colour |
| `triangle_size` | `float` | `MED_SMALL_BUFF` | triangle size |
| `triangle_color` | `ParsableManimColor \| None` | `WHITE` | triangle colour |
| `line_func` | `type[Line]` | `Line` | vertical line type; can be switched to `DashedLine` |
| `line_color` | `ParsableManimColor` | `PURE_YELLOW` | vertical line colour |

## Axes.get_secant_slope_group

```python
def get_secant_slope_group(
    self,
    x: float,
    graph: ParametricFunction,
    dx: float | None = None,
    dx_line_color: ParsableManimColor = PURE_YELLOW,
    dy_line_color: ParsableManimColor | None = None,
    dx_label: float | str | None = None,
    dy_label: float | str | None = None,
    include_secant_line: bool = True,
    secant_line_color: ParsableManimColor = GREEN,
    secant_line_length: float = 10,
) -> VGroup:
```

At `(x, f(x))` it builds a group: Δx horizontal segment + Δy vertical segment + optional text labels + the secant line; use it directly when explaining "secant slope = Δy/Δx".

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `x` | `float` | required | the secant's starting x |
| `graph` | `ParametricFunction` | required | the target curve |
| `dx` | `float \| None` | `None` → 10% of the x-axis length | horizontal increment |
| `dx_line_color` | `ParsableManimColor` | `PURE_YELLOW` | Δx segment colour |
| `dy_line_color` | `ParsableManimColor \| None` | `None` → the same as `dx` | Δy segment colour |
| `dx_label` / `dy_label` | `float \| str \| None` | `None` | text labels beside the segments |
| `include_secant_line` | `bool` | `True` | whether to include the secant line itself |
| `secant_line_color` | `ParsableManimColor` | `GREEN` | secant line colour |
| `secant_line_length` | `float` | `10` | secant line length (scene units) |

#### Sample: `get_vertical_lines_to_graph` + secant group

First `get_vertical_lines_to_graph(x_range=[0,4], num_lines=9)` pulls 9 evenly spaced grey vertical dashed lines up to the curve to show the sampling positions; then `FadeOut` removes them, and finally a secant group with Δx=1 is built at x=2.

```python
from real_time_manim import (
    Scene, Axes, Text,
    YELLOW, TEAL, PURPLE_B, GREEN, GREY, GREY_B, UP, DOWN, DL,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class SecantDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("05b-secant_slope_group", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[-1, 5, 1], y_range=[-1, 7, 1],
                  x_length=9, y_length=5.5)   # parabola framing
        curve = ax.plot(lambda x: x**2, color=PURPLE_B)   # the parabola y=x²
        lab = Text("get_vertical_lines_to_graph(9) + secant(dx=1)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # parameter summary label
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   # the coordinate system and the label enter together
        win.play(Create(curve), run_time=0.8)   # draw the parabola

        vlines = ax.get_vertical_lines_to_graph(curve, x_range=[0, 4],   # "get_vertical_lines_to_graph": pull vertical dashed lines evenly up to the curve
                                                num_lines=9, color=GREY)   # parameter "num_lines": number of dashed lines
        win.play(Create(vlines), run_time=0.6)   # draw the vertical dashed line group
        win.play(FadeOut(vlines), run_time=0.3)   # remove the dashed lines to make room for the secant group

        group = ax.get_secant_slope_group(x=2.0, graph=curve, dx=1.0,   # "get_secant_slope_group": Δx horizontal line + Δy vertical line + secant line as one group
                                          dx_label="dx", dy_label="dy",   # parameters "dx_label"/"dy_label": labels beside the lines
                                          secant_line_color=GREEN, secant_line_length=4)   # parameters "secant_line_color"/"secant_line_length": secant line style
        win.play(FadeIn(group), run_time=0.8)   # the secant group fades in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does:

- `get_vertical_lines_to_graph` takes `num_lines=9` lines at equal spacing within `x_range=[0,4]`, each pulled vertically from the x axis up to the curve (`**kwargs` passes the style, e.g. `color=GREY`).
- `get_secant_slope_group(x=2.0, dx=1.0)` builds a `VGroup` — the horizontal segment [2,3], the vertical segment [f(2),f(3)], the "dx"/"dy" text and the green secant line — and `FadeIn` brings the whole group on screen.

<video src="assets/RTM output/05b-Plot-Labels-and-Helper-Lines-secant.mp4" controls width="560"></video>

> Note:
>
> - `get_secant_slope_group`'s `secant_line_length` is in **scene units**, not data units; give it a small value (e.g. 4) so it does not poke out of the screen.
> - `dx_label` / `dy_label` go through `MathTex`.

## Axes.get_vertical_lines_to_graph

```python
def get_vertical_lines_to_graph(
    self,
    graph: ParametricFunction,
    x_range: Sequence[float] | None = None,
    num_lines: int = 20,
    **kwargs: Any,
) -> VGroup:
```

It pulls vertical dashed lines evenly from the x axis up to the curve, to mark sampling positions.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `graph` | `ParametricFunction` | required | the target curve |
| `x_range` | `Sequence[float] \| None` | `None` → the curve's full range | `[x_min, x_max]`, the interval over which the segments are spread |
| `num_lines` | `int` | `20` | number of lines |
| `**kwargs` | — | — | passed to each `DashedLine` (`color`, `stroke_width`…) |

---

See also: [Function graphs](05-Function-Graphs.md) · [Derivatives, antiderivatives and tangents](05c-Derivatives-Antiderivatives-and-Tangents.md) · [Areas and Riemann rectangles](06-Areas-and-Riemann-Rectangles.md)
