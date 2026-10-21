# Plotting function curves (plot and parametric curves)

How to draw the two kinds of curve, `y = f(x)` and parametric equations: `ax.plot` samples and plots on a coordinate system (it supports `discontinuities` for declaring discontinuity points), `FunctionGraph` draws directly without a coordinate system, and `plot_parametric_curve` draws parametric curves such as Lissajous figures. Areas/Riemann rectangles are in [Areas and Riemann rectangles](06-Areas-and-Riemann-Rectangles.md), and plot labels are in 05b/05c.

> Note: the source has **no** aliases from older tutorials such as `ax.get_graph(...)` or `plot_area`; the only entry point is `ax.plot(...)`.

## Axes.plot

```python
def plot(self, function: Callable[[float], float], x_range: Sequence[float] | None = None,
         use_vectorized: bool = False, colorscale=None, colorscale_axis: int = 1,
         **kwargs) -> ParametricFunction
```

It samples along `x_range` and converts to screen points through `coords_to_point`, returning a `ParametricFunction`. `**kwargs` goes to `ParametricFunction`; the most common ones are the last 5 rows of the table below.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `function` | `Callable[[float], float]` | required | e.g. `lambda x: np.sin(x)` |
| `x_range` | `Sequence[float] \| None` | `None` = the whole x axis | `[x_min, x_max]` or `[x_min, x_max, x_step]`; `x_step` is the **sampling step** (not a tick), and the smaller it is, the smoother and slower |
| `use_vectorized` | `bool` | `False` | set to `True` when the function accepts array input, a big speed-up |
| `colorscale` | colour sequence / `(color, pivot)` sequence \| `None` | `None` | gradient colouring by y value; **must be passed together with `x_range`**, otherwise a `TypeError` is raised |
| `colorscale_axis` | `int` | `1` | the axis the gradient follows: `0`=x, `1`=y |
| `color` | `ParsableManimColor` | `PURE_YELLOW` | curve colour (`**kwargs`) |
| `discontinuities` | `Iterable[float] \| None` | `None` | x values of the discontinuity points, e.g. `[-2, 2]`; without them a vertical line joins across |
| `dt` | `float` | `1e-8` | tolerance around a discontinuity, usually written `0.1` |
| `use_smoothing` | `bool` | `True` | whether to smooth (turning it off is more truthful when there are few points or the function is very steep) |
| `stroke_width` | `float` | inherited | line width |

> **Returns**: a `ParametricFunction`; `graph.underlying_function` (the original function), `graph.t_min`/`graph.t_max` (the sampling interval, used by `get_area` and friends).

#### Sample: declaring discontinuities with `discontinuities`/`dt`

The same function with a vertical asymptote is drawn twice: the red version without declared discontinuities is "joined up" by a vertical line at `-2` and `2` (the wrong way), while the green version with `discontinuities=[-2, 2], dt=0.1` breaks at the discontinuities (the right way).

```python
from real_time_manim import (
    Scene, Axes, NumberPlane, FunctionGraph, Text, np,
    YELLOW, RED, GREEN, BLUE, ORANGE, GREY_B, UP, DOWN, TAU,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class PlotDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("05-plot", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = NumberPlane(x_range=[-3, 3, 1], y_range=[-4, 4, 1])   # coordinate system with a grid
        f = lambda x: max(-60, min(60, (x**2 - 2) / (x**2 - 4)))   # vertical asymptotes at -2 and 2; clamp y to ±60 first: near the poles floating point produces huge values of 1e14 that cannot be drawn
        lab = Text("plot(discontinuities=[-2,2], dt=0.1)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # parameter summary label
        win.play(Create(ax), run_time=0.7)   # draw the coordinate grid
        win.play(FadeIn(lab), run_time=0.3)   # the summary label fades in

        bad = ax.plot(f, color=RED)   # no discontinuity points declared: at -2 and 2 a vertical line "joins them up"
        win.play(Create(bad), run_time=1.0)   # look at the wrong way first
        win.play(FadeOut(bad), run_time=0.4)   # remove the wrong way

        good = ax.plot(f, discontinuities=[-2, 2], dt=0.1,   # parameters "discontinuities"/"dt": declare the discontinuity points and the tolerance
                       color=GREEN, use_smoothing=False)   # parameter "use_smoothing": turning smoothing off on steep stretches is more truthful
        win.play(Create(good), run_time=1.2)   # now look at the right way
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: it first draws the red version "with no discontinuity points declared" — the samples are positive on one side of the asymptote and negative on the other, and a straight line joins them into a vertical line crossing the frame, which is the classic wrong way. After `FadeOut` removes it, the green version is drawn: `discontinuities=[-2, 2]` declares the two discontinuity points and `dt=0.1` gives the skip tolerance, so the curve really does break at the discontinuities; on top of that `use_smoothing=False` on the steep stretches keeps Bézier smoothing from rounding the sharp corner off.

<video src="assets/RTM output/05-Function-Graphs-plot.mp4" controls width="560"></video>

> Note:
>
> - **an asymptotic function must have an upper bound on its y values** (the `max(-60, min(60, ...))` in the sample) — near a pole floating point produces huge values of the order of `1e14`, and drawing them directly always goes wrong.
> - the `dt` default of `1e-8` is too small; in practice write `0.1`.

## FunctionGraph

```python
def __init__(self, function: Callable[[float], Any], x_range: tuple | None = None,
             color: ParsableManimColor = PURE_YELLOW, **kwargs) -> None:
```

It draws `y = f(x)` directly without a coordinate system (by default spanning the whole width of the screen), which suits scenes that show no axes, such as "comparing two functions".

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `function` | `Callable[[float], Any]` | required | `lambda t: np.cos(t)` |
| `x_range` | `tuple \| None` | `None` → `(-frame_x_radius, frame_x_radius)` | sampling interval (the third item is the step) |
| `color` | `ParsableManimColor` | `PURE_YELLOW` | curve colour |
| `**kwargs` | — | — | passed through to `ParametricFunction` (`discontinuities`, `use_smoothing`…) |

#### Sample: cosine vs sine comparison

No coordinate system is created; two `FunctionGraph`s are overlaid directly: blue `cos(3t)` and green `sin(3t)`, visibly half a grid cell out of phase.

```python
from real_time_manim import (
    Scene, Axes, NumberPlane, FunctionGraph, Text, np,
    YELLOW, RED, GREEN, BLUE, ORANGE, GREY_B, UP, DOWN, TAU,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class FunctionGraphDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("05-FunctionGraph", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        g1 = FunctionGraph(lambda t: np.cos(3 * t), x_range=[-4, 4], color=BLUE)   # cosine curve
        g2 = FunctionGraph(lambda t: np.sin(3 * t), x_range=[-4, 4], color=GREEN)   # sine curve
        lab = Text("FunctionGraph(cos 3t) vs FunctionGraph(sin 3t)",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # method summary label
        win.play(Create(g1), run_time=0.9)   # draw the cosine curve
        win.play(Create(g2), run_time=0.9)   # draw the sine curve (half a grid cell out of phase)
        win.play(FadeIn(lab), run_time=0.4)   # the summary label fades in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: `FunctionGraph` needs no coordinate system — give it a function from `t` to `y` and it draws the line; `x_range=[-4, 4]` limits the sampling interval (without it the whole screen width is used). The two lines are `Create`d one after the other in different colours, and the half-cell phase difference is obvious at a glance.

<video src="assets/RTM output/05-Function-Graphs-functiongraph.mp4" controls width="560"></video>

> Note: `FunctionGraph`'s `x_range` is a **sampling interval**, not data coordinates (it has no idea about a coordinate system at all); for ticks and a grid use `ax.plot` instead.

## ParametricFunction (table only)

```python
def __init__(self, function: Callable[[float], Point3DLike], t_range: tuple = (0, 1),
             scaling: _ScaleBase = LinearBase(), dt: float = 1e-8,
             discontinuities: Iterable[float] | None = None, use_smoothing: bool = True,
             use_vectorized: bool = False, **kwargs) -> None:
```

The underlying class for parametric curves: `function(t) -> (x, y, z)`. It can draw parametric curves such as Lissajous figures on its own, and it is also what `Axes.plot` returns.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `function` | `Callable[[float], Point3DLike]` | required | `lambda t: (x(t), y(t), z(t))` |
| `t_range` | `tuple` | `(0, 1)` | `(t_min, t_max)` or `(t_min, t_max, step)`; a missing step is filled in as `0.01` |
| `scaling` | `_ScaleBase` | `LinearBase()` | parameter scaling (a logarithmic axis inherits the axis scaling automatically) |
| `dt` | `float` | `1e-8` | discontinuity tolerance |
| `discontinuities` | `Iterable[float] \| None` | `None` | discontinuity points on the parameter t |
| `use_smoothing` | `bool` | `True` | whether to smooth |
| `use_vectorized` | `bool` | `False` | whether to pass the whole t array into the function (output shape `[[x…],[y…],[z…]]`) |
| `**kwargs` | — | — | passed to `VMobject` (`color`, `stroke_width`…) |

## CoordinateSystem.plot_parametric_curve

```python
def plot_parametric_curve(self, function: Callable[[float], np.ndarray],
                          use_vectorized: bool = False, **kwargs) -> ParametricFunction
```

Draws a parametric curve inside a coordinate system: the function returns **data coordinates** and `c2p` is applied internally; use it for parametric equations such as cardioids and Lissajous figures.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `function` | `Callable[[float], np.ndarray]` | required | `lambda t: np.array([x(t), y(t), 0])` |
| `use_vectorized` | `bool` | `False` | whether the function supports vectorisation |
| `**kwargs` | — | — | passed to `ParametricFunction`; **`t_range` is passed through here too** (e.g. `t_range=[0, 2*PI]`) |

#### Sample: drawing a Lissajous curve from a parametric equation with `t_range`

In a coordinate system framed as a square, `np.array([sin(3t), sin(4t), 0])` draws a Lissajous curve, with `t_range=[0, TAU]` passed in through `**kwargs`.

```python
from real_time_manim import (
    Scene, Axes, NumberPlane, FunctionGraph, Text, np,
    YELLOW, RED, GREEN, BLUE, ORANGE, GREY_B, UP, DOWN, TAU,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class ParametricCurveDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("05-parametric_curve", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[-2, 2, 1], y_range=[-2, 2, 1],
                  x_length=6, y_length=6)   # square framing, so the Lissajous figure is not distorted
        curve = ax.plot_parametric_curve(   # "plot_parametric_curve": draw a curve from a parametric equation
            lambda t: np.array([np.sin(3 * t), np.sin(4 * t), 0]),   # x=sin(3t), y=sin(4t)
            t_range=[0, TAU], color=ORANGE)   # the parameter "t_range" is passed through **kwargs
        lab = Text("plot_parametric_curve(sin(3t), sin(4t))",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # parameter summary label
        win.play(Create(ax), run_time=0.6)   # draw the coordinate system
        win.play(Create(curve), run_time=1.4)   # draw the Lissajous curve
        win.play(FadeIn(lab), run_time=0.4)   # the summary label fades in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: `x_length=y_length=6` combined with the `[-2,2]²` range makes the x and y scales equal, which is the key to not distorting the Lissajous figure. The function returns **data coordinates** `np.array([sin(3t), sin(4t), 0])`, and `plot_parametric_curve` applies `c2p` internally; `t_range=[0, TAU]` goes through `**kwargs` and is passed on to `ParametricFunction`.

<video src="assets/RTM output/05-Function-Graphs-parametric.mp4" controls width="560"></video>

> Note:
>
> - `plot_parametric_curve`'s function returns **data coordinates** (a three-item `np.array`), unlike `ParametricFunction`, which returns scene coordinates directly.
> - do not write `t_range` into the function's parameters; pass it through `**kwargs`.

---

See also: [2D coordinate systems](02-Axes.md) · [Plot labels and helper lines](05b-Plot-Labels-and-Helper-Lines.md) · [Derivatives, antiderivatives and tangents](05c-Derivatives-Antiderivatives-and-Tangents.md) · [Areas and Riemann rectangles](06-Areas-and-Riemann-Rectangles.md)
