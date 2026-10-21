# Derivatives, antiderivatives and tangents

This section covers coordinate conversion on a curve and the calculus trio:

- `input_to_graph_point` / `input_to_graph_coords` turn an x value into a screen point / data coordinates on the curve;
- `plot_derivative_graph` differentiates numerically and draws `f'`;
- `plot_antiderivative_graph` integrates numerically and draws `F`;
- `slope_of_tangent` / `angle_of_tangent` give the tangent slope and angle at any point.

Implicit curves and secant groups are in [Plot labels and helper lines](05b-Plot-Labels-and-Helper-Lines.md).

> Note: these are all **numerical** methods — the derivative uses finite differences and the antiderivative the trapezoid rule; there is no symbolic differentiation. The `graph` parameter must be the return value of `ax.plot`, because the methods read its sampling function internally.

## Axes.input_to_graph_point (alias i2gp)

```python
def input_to_graph_point(
    self,
    x: float,
    graph: ParametricFunction | VMobject,
) -> Point3D:
```

It returns the **screen point** (scene coordinates) at x on the curve; commonly used to place a `Dot` or compute distances.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `x` | `float` | required | the input x value |
| `graph` | `ParametricFunction \| VMobject` | required | the return value of `ax.plot` |

#### Sample: taking points on a curve with `i2gp` / `i2gc`

Draw `y=x²` on a `NumberPlane` with a grid:

- `input_to_graph_point(x=PI)` gets the screen point and places a yellow dot and a label;
- `input_to_graph_coords(x=2.0)` gets the data coordinates, reads them back and displays `(2.0, 4.0)`.

```python
from real_time_manim import (
    Scene, Axes, NumberPlane, Dot, Line, Text, PI,
    YELLOW, PURPLE_B, GREEN, ORANGE, GREY_B, UP, DOWN, UR, DL, DR,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class TakePointDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("05c-input_to_graph", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = NumberPlane(x_range=[-2, 5, 1], y_range=[-1, 7, 1],   # coordinate system with a grid
                         background_line_style={"stroke_opacity": 0.4})   # dim the grid lines so they do not steal the show
        curve = ax.plot(lambda x: x**2, color=PURPLE_B)   # the parabola y=x²
        lab = Text("i2gp(x) -> screen point   i2gc(x) -> data coords",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # method summary label
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   # the coordinate system and the label enter together
        win.play(Create(curve), run_time=0.8)   # draw the parabola

        pos = ax.input_to_graph_point(x=PI, graph=curve)   # "input_to_graph_point" (alias i2gp): the screen point at x
        dot = Dot(pos, color=YELLOW)   # once the screen point is in hand, place a Dot directly
        tag = Text("i2gp(PI)", font_size=24, color=YELLOW).next_to(dot, UR, buff=0.2)
        win.play(FadeIn(dot), FadeIn(tag), run_time=0.4)   # the yellow dot and the label fade in

        coords = ax.input_to_graph_coords(x=2.0, graph=curve)   # "input_to_graph_coords" (alias i2gc): the data coordinates at x
        tag2 = Text("i2gc(2.0)=(%.1f, %.1f)" % coords,   # show the data coordinates read back
                    font_size=24, color=GREEN).next_to(ax.c2p(2, 4), DR, buff=0.3)
        win.play(FadeIn(tag2), run_time=0.4)   # the read-back data coordinates fade in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does:

- `i2gp(PI)` "pins a point" directly on the curve — internally it takes the curve's sampled value at `PI` and runs it through `c2p` to get the screen coordinates; the return value can be fed to `Dot` / `next_to`.
- `i2gc(2.0)` goes the other way, converting the screen point back into **data coordinates** `(2, 4)`; the sample formats it with `%.1f` and shows it next to the point, verifying `2²=4`.

<video src="assets/RTM output/05c-Derivatives-Antiderivatives-and-Tangents-takepoint.mp4" controls width="560"></video>

> Note: `i2gp` returns scene coordinates (you can `Dot(pos)` directly) and `i2gc` returns data coordinates (an `(x, y)` tuple); do not mix the two up.

## Axes.input_to_graph_coords (alias i2gc)

```python
def input_to_graph_coords(
    self, x: float, graph: ParametricFunction
) -> tuple[float, float]:
```

It returns the **data coordinates** `(x, y)` at x on the curve (not a screen point), for reading back the true values on the curve.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `x` | `float` | required | the input x value |
| `graph` | `ParametricFunction` | required | the return value of `ax.plot` |

## Axes.plot_derivative_graph

```python
def plot_derivative_graph(
    self,
    graph: ParametricFunction,
    color: ParsableManimColor = GREEN,
    **kwargs: Any,
) -> ParametricFunction:
```

It differentiates the curve numerically and returns the derivative curve (in the same framing as the original curve).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `graph` | `ParametricFunction` | required | the curve being differentiated |
| `color` | `ParsableManimColor` | `GREEN` | derivative curve colour |
| `**kwargs` | — | — | passed to `ParametricFunction` |

#### Sample: derivative and antiderivative curves

Three lines are drawn in the same coordinate system:

- the original function `x²` (purple);
- the numerical derivative `2x` (green, a line through the origin);
- the numerical antiderivative `x³/3` (orange, the trapezoid rule integrating from 0 to x, `y_intercept=0`).

```python
from real_time_manim import (
    Scene, Axes, NumberPlane, Dot, Line, Text, PI,
    YELLOW, PURPLE_B, GREEN, ORANGE, GREY_B, UP, DOWN, UR, DL, DR,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class DerivativeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("05c-derivative_antiderivative", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[-1, 2.5, 1], y_range=[-2, 7, 1],
                  x_length=9, y_length=5.5)   # framing that encloses the three curves
        c1 = ax.plot(lambda x: x**2, color=PURPLE_B)   # the original curve y=x²
        lab = Text("f=x^2   f'=2x   F=x^3/3 (y_intercept=0)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # method summary label
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   # the coordinate system and the label enter together
        win.play(Create(c1), run_time=0.7)   # draw the original curve

        c2 = ax.plot_derivative_graph(c1, color=GREEN)   # "plot_derivative_graph": numerical differentiation, drawing 2x
        win.play(Create(c2), run_time=0.7)   # draw the derivative (a line through the origin)

        c3 = ax.plot_antiderivative_graph(c1, y_intercept=0,   # "plot_antiderivative_graph": the trapezoid rule integrating from 0 to x
                                           color=ORANGE)   # parameter "y_intercept": the constant of integration (the y-axis intercept)
        win.play(Create(c3), run_time=0.9)   # draw the antiderivative x³/3
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does:

- `plot_derivative_graph(c1)` does a central difference `(f(x+h)-f(x-h))/2h` on `c1`'s sample points; the derivative of `x²` is exactly the line through the origin, `2x`.
- `plot_antiderivative_graph(c1, y_intercept=0)` integrates from 0 to each x with the trapezoid rule. `y_intercept` is the constant of integration — change it to `0.5` and the whole orange line shifts up by 0.5 in parallel.

<video src="assets/RTM output/05c-Derivatives-Antiderivatives-and-Tangents-deriv.mp4" controls width="560"></video>

> Note:
>
> - the derivative and the antiderivative are both **numerical** results, so there are errors where the curve is steep or discontinuous.
> - `plot_antiderivative_graph`'s integration always starts at the minimum x; `y_intercept` only shifts it vertically.

## Axes.plot_antiderivative_graph

```python
def plot_antiderivative_graph(
    self,
    graph: ParametricFunction,
    y_intercept: float = 0,
    samples: int = 50,
    use_vectorized: bool = False,
    **kwargs: Any,
) -> ParametricFunction:
```

It integrates the curve numerically with the trapezoid rule and returns the antiderivative curve.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `graph` | `ParametricFunction` | required | the curve being integrated |
| `y_intercept` | `float` | `0` | the constant of integration (the y-axis intercept) |
| `samples` | `int` | `50` | number of integration samples; the larger, the more accurate and the slower |
| `use_vectorized` | `bool` | `False` | set to `True` for a speed-up when the function accepts array input |
| `**kwargs` | — | — | passed to `ParametricFunction` |

## Axes.slope_of_tangent

```python
def slope_of_tangent(
    self, x: float, graph: ParametricFunction, **kwargs: Any
) -> float:
```

It returns the tangent slope at x on the curve (a numerical difference), which can be fed straight to `Line` to draw the tangent.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `x` | `float` | required | the tangent point's x |
| `graph` | `ParametricFunction` | required | the target curve |
| `**kwargs` | — | — | passed to the underlying difference (e.g. `dx`) |

#### Sample: a dynamic tangent with `slope_of_tangent` + `angle_of_tangent`

Three tangents are drawn at x=-2/0/2 on the gentle parabola `f=0.25x²+1`:

- `slope_of_tangent` gives the slope, the two end points are extrapolated with a half-length of 1.6, and they are joined into a green tangent segment;
- `angle_of_tangent`'s reading (in radians) is shown next to the tangent point together with the slope.

```python
from real_time_manim import (
    Scene, Axes, NumberPlane, Dot, Line, Text, PI,
    YELLOW, PURPLE_B, GREEN, ORANGE, GREY_B, UP, DOWN, UR, DL, DR,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class TangentDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("05c-slope_of_tangent", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[-3, 3, 1], y_range=[-1, 7, 1],
                  x_length=9, y_length=5.5)   # gentle parabola framing
        f = lambda x: 0.25 * x**2 + 1   # a gentler parabola, so the tangents are not too steep
        curve = ax.plot(f, color=PURPLE_B)   # the original curve
        lab = Text("slope_of_tangent(x) + angle_of_tangent(x)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # method summary label
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   # the coordinate system and the label enter together
        win.play(Create(curve), run_time=0.8)   # draw the curve

        for x0, side in ((-2, DL), (0, UP), (2, DR)):   # draw a tangent at three positions
            s = ax.slope_of_tangent(x=x0, graph=curve)   # "slope_of_tangent": the tangent slope, numerically
            ang = ax.angle_of_tangent(x=x0, graph=curve)   # "angle_of_tangent": the angle between the tangent and the x axis (radians)
            p = ax.c2p(x0, f(x0))   # the tangent point
            half = 1.6   # half the tangent length (data units)
            pa = ax.c2p(x0 - half, f(x0) + s * (-half))   # extrapolate the two end points from the slope
            pb = ax.c2p(x0 + half, f(x0) + s * half)
            tline = Line(pa, pb, color=GREEN)   # the tangent segment
            tag = Text("x=%+d  slope=%.1f  ang=%.2frad" % (x0, s, ang),   # show the slope and the angle together
                       font_size=20, color=GREY_B).next_to(p, side, buff=0.25)
            win.play(Create(tline), FadeIn(tag), run_time=0.5)   # the tangent and the readout enter
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: the tangent segment is **constructed by hand**. After `slope_of_tangent` gives the slope `s`, the code extrapolates left and right from the tangent point by `half=1.6` in data coordinates (`y = f(x0) + s·Δx`), then converts to screen points with `c2p` and joins them into a `Line`; `angle_of_tangent` returns radians (`atan(s)`) and is baked into the readout text along with the slope.

At x=0 the slope is 0 and the tangent is horizontal; at x=±2 the two are symmetric and opposite.

<video src="assets/RTM output/05c-Derivatives-Antiderivatives-and-Tangents-tangent.mp4" controls width="560"></video>

> Note:
>
> - `slope_of_tangent` returns the **data slope** (dy/dx); it is fine to use it directly to extrapolate data coordinates, but do not use it as a screen slope (it is skewed when the x/y scales differ).
> - `angle_of_tangent` is in radians.

## Axes.angle_of_tangent

```python
def angle_of_tangent(
    self,
    x: float,
    graph: ParametricFunction,
    dx: float = 1e-8,
) -> float:
```

It returns the angle (in radians) between the tangent to the curve at x and the x axis, `atan(slope_of_tangent(x))`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `x` | `float` | required | the tangent point's x |
| `graph` | `ParametricFunction` | required | the target curve |
| `dx` | `float` | `1e-8` | difference step |

---

See also: [Function graphs](05-Function-Graphs.md) · [Plot labels and helper lines](05b-Plot-Labels-and-Helper-Lines.md) · [Areas and Riemann rectangles](06-Areas-and-Riemann-Rectangles.md)
