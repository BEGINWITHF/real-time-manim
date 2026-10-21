# Ticks and scaling

RTM uses the generic vector fallback renderer (verified by real render on 2026-10-11; the fallback draws correctly). The `scaling=` parameter accepts a `_ScaleBase` subclass and determines the non-linear mapping of number-line ticks.

## LogBase

`LogBase(base=10, custom_labels=True)`

A logarithmic-scale object; pass it to `NumberLine(scaling=...)` or `Axes(y_axis_config={"scaling": LogBase(...)})` to turn the linear step into decade ticks `base**k` and generate LaTeX labels of the form `10^2`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `base` | `float` | `10` | logarithm base |
| `custom_labels` | `bool` | `True` | whether to use custom labels of the form `10^k` (`False` shows ordinary numbers) |

Three core methods (all called automatically by the system, and callable manually):

| Method | Signature | Description |
| --- | --- | --- |
| `function` | `(value) -> float` | `base ** value`: turns an "exponent" into a real value |
| `inverse_function` | `(value) -> float` | real value → exponent; **`value <= 0` raises `ValueError`** |
| `get_custom_labels` | `(val_range, unit_decimal_places=0, **base_config) -> list[Integer]` | generates `10^k` labels |

## LinearBase

`LinearBase(scale_factor=1.0)`

The default linear scale (`function = scale_factor * value`); it is the default `scaling` for every axis. You only need to pass it explicitly when you want to multiply all ticks by a factor.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `scale_factor` | `float` | `1.0` | slope; same methods as `LogBase` (`function`/`inverse_function`), `custom_labels=False` |

## _ScaleBase (custom-scale extension point)

```python
class _ScaleBase:
    def __init__(self, custom_labels: bool = False)
    def function(self, value) -> float            # must override
    def inverse_function(self, value) -> float    # must override
    def get_custom_labels(self, val_range, **kw_args) -> Iterable[VMobject]   # optionally override
```

Despite the leading underscore, it is a **public extension point**: any `scaling=` parameter accepts its subclasses (the handbook does not include `SqrtBase`; for square-root / square scales, subclass it yourself).

- `function`: value → the "logical position" on the axis (`NumberLine` internally runs the whole `x_range` through it).
- `inverse_function`: the inverse of `function`; `n2p`/`p2c` use it to recover the real value.
- `get_custom_labels(val_range)`: returns labels in one-to-one correspondence with `val_range`; only used together with `custom_labels=True`.

## Sample 1: Switching the y axis of `Axes` to `LogBase`

This is the actually-rendered version of the page's `Example`: `Axes` changes **only the y axis** to a log scale and `plot`s a `y=x²`. The same curve shoots up quickly on a linear y axis, while on a log y axis it is squashed into a gently rising curve.

```python
from real_time_manim import (
    Axes, Create, DOWN, FadeIn, GREY_B, LEFT, LinearBase, LogBase,
    NumberLine, Scene, Text, UP, YELLOW, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class LogBaseDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("10-LogBase", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        ax = Axes(x_range=[0, 10, 1], y_range=[-2, 6, 1], tips=False,   #data range of both axes
                  axis_config={"include_numbers": True},   #both axes carry tick numbers
                  y_axis_config={"scaling": LogBase(custom_labels=True)})   #parameter "scaling": change the y axis to a log scale
        graph = ax.plot(lambda x: x**2,   #plot y=x^2: on a log y axis it is "squashed" into a rising curve
                        x_range=[0.001, 10],   #x_min must be > 0 (LogBase's inverse_function raises ValueError for ≤0)
                        use_smoothing=False)
        lab = Text("y_axis_config={'scaling': LogBase()}",
                   font_size=24, color=GREY_B).to_edge(UP).shift(DOWN * 0.9)   #place the caption below the title
        win.play(Create(ax), FadeIn(lab), run_time=0.8)   #the axes and the caption appear together
        win.play(Create(graph), run_time=0.8)   #draw the curve
        win.play(Wait(0.8))   #wait 0.8s
        win.close()   #close the RTM window
```

What this code does:

- `scaling=` is a parameter of the axis object (passable via `axis_config` / `x_axis_config` / `y_axis_config`); `LogBase(custom_labels=True)` turns the linear step into decade ticks `base**k` and generates labels of the form `10^2`.
- Each x of `plot` first goes through `function` to get its position on the axis.
- Note that `LogBase.inverse_function(value<=0)` raises `ValueError: log(0) is undefined`, so the **lower bound of `plot` / `x_range` must be > 0**.

<video src="assets/RTM output/10-Ticks-and-Scaling-logbase.mp4" controls width="560"></video>

> **Do not use `LogBase` directly on `NumberLine`**:
>
> - `NumberLine(x_range=[0, 6, 1], scaling=LogBase(base=10), include_numbers=True)` crashes (`x_range` includes 0, which is equivalent to taking log of 0).
> - Even with `x_range=[1, 6, 1]`, manim places the ticks off the line (measured at `length=9`, the ticks fall at x≈-6.3…-4.9 and `include_numbers` generates 0 labels).
> - To demonstrate a log scale, use `Axes(y_axis_config={"scaling": LogBase(...)})`; that is the path that works.

## Sample 2: `LinearBase` multiplying all ticks by a factor

`LinearBase(scale_factor)` is just `function(v) = scale_factor * v`; with no argument it is `1.0`, i.e. the default scale for all axes. The sample stacks two `NumberLine`s, passes `1.5` to the second, and the tick spacing changes as a whole.

```python
from real_time_manim import (
    Axes, Create, DOWN, FadeIn, GREY_B, LEFT, LinearBase, LogBase,
    NumberLine, Scene, Text, UP, YELLOW, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class LinearBaseDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("10-LinearBase", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        base = NumberLine(x_range=[0, 6, 1], length=9,   #default scale: LinearBase(scale_factor=1.0)
                          include_numbers=True).shift(UP * 0.9 + LEFT * 0.6)
        wide = NumberLine(x_range=[0, 6, 1], length=9,   #parameter "scale_factor": multiply all ticks by 1.5
                          scaling=LinearBase(scale_factor=1.5),
                          include_numbers=True).shift(DOWN * 0.9)
        la = Text("LinearBase(scale_factor=1.0)  # default", font_size=22,
                  color=GREY_B).next_to(base, UP, buff=0.25)
        lb = Text("LinearBase(scale_factor=1.5)", font_size=22,
                  color=GREY_B).next_to(wide, DOWN, buff=0.25)
        win.play(Create(base), Create(wide), FadeIn(la), FadeIn(lb), run_time=0.8)   #the two number lines appear together
        win.play(Wait(0.8))   #wait 0.8s
        win.close()   #close the RTM window
```

What this code does: a `NumberLine`'s tick position = `scaling.function(value)` mapped onto the axis, so `scale_factor=1.5` pushes each tick outward by 1.5× (the 0 point stays put) while the label values stay the same — visually, the "ticks are stretched".

`inverse_function` is its inverse; `n2p` / `p2c` use it to recover the real value.

<video src="assets/RTM output/10-Ticks-and-Scaling-linearbase.mp4" controls width="560"></video>

> The two number lines use **the same `x_range` with only `scaling` changed**: when `scale_factor ≠ 1` the ticks no longer fill the whole line (manim does not re-normalize automatically); this is upstream behaviour, identical in both engines.
>
> To customize the scale (e.g. a square-root / square axis), subclass `_ScaleBase` and override `function` / `inverse_function` (optionally `get_custom_labels`).

See also: [Number line NumberLine](01-NumberLine.md) · [Two-dimensional coordinate system](02-Axes.md) · [Grids and the complex plane](04-Grids-and-Complex-Plane.md)
