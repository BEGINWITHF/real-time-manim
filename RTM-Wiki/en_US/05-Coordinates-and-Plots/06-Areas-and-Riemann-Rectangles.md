# Areas and Riemann rectangles

This section covers the area under a curve and integral approximation:

- `get_area` produces the filled area from the curve to the x axis (or to another curve);
- `get_riemann_rectangles` produces the Riemann-sum rectangle group (left / right / midpoint sampling).

Tangents and derivatives are in [Derivatives, antiderivatives and tangents](05c-Derivatives-Antiderivatives-and-Tangents.md).

> Note:
>
> - both methods require `graph` to be the return value of `ax.plot`; internally they read its sampling function and `t_min` / `t_max`.
> - the sign of the area is handled automatically — when the curve is below the x axis, `get_riemann_rectangles` inverts the colour to show negative area.

## Axes.get_area

```python
def get_area(
    self,
    graph: ParametricFunction,
    x_range: tuple[float, float] | None = None,
    color: ParsableManimColor | Iterable[ParsableManimColor] = (BLUE, GREEN),
    opacity: float = 0.3,
    bounded_graph: ParametricFunction | None = None,
    **kwargs: Any,
) -> Polygon:
```

It returns a `Polygon` representing the area under the curve within `x_range` (or the area between two curves).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `graph` | `ParametricFunction` | required | the target curve |
| `x_range` | `tuple[float, float] \| None` | `None` → the curve's full range | the x interval of the area |
| `color` | single colour / colour sequence | `(BLUE, GREEN)` | a list makes a gradient along x |
| `opacity` | `float` | `0.3` | fill opacity |
| `bounded_graph` | `ParametricFunction \| None` | `None` | upper boundary curve; once given, the area is **between** the two curves |
| `**kwargs` | — | — | passed to `Polygon` |

#### Sample: area under a curve with `get_area`

Two kinds of area are demonstrated in turn on the parabola `0.5x²-0.5`:

- first the green gradient area from `[0,2]` to the x axis;
- after removing it, the line `y=3` is added and the between-two-curves area of `bounded_graph` is demonstrated.

```python
from real_time_manim import (
    Scene, Axes, Text,
    YELLOW, BLUE, BLUE_C, RED, GREEN, GREEN_B, GREEN_D, GREY_B, UP, DOWN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class AreaDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("06-get_area", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[-3, 3, 1], y_range=[-2, 6, 1],
                  x_length=9, y_length=5.5).add_coordinates()   # coordinate system with tick numbers
        quad = ax.plot(lambda x: 0.5 * x**2 - 0.5, color=BLUE)   # the parabola
        lab = Text("get_area(x_range=(0,2)) + bounded_graph",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # parameter summary label
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   # the coordinate system and the label enter together
        win.play(Create(quad), run_time=0.7)   # draw the parabola

        area = ax.get_area(quad, x_range=(0, 2),   # "get_area": the area from under the curve to the x axis
                           color=(GREEN_B, GREEN_D), opacity=1)   # parameters "color"/"opacity": single colour, gradient list and opacity
        win.play(FadeIn(area), run_time=0.6)   # the green gradient area fades in
        win.play(FadeOut(area), run_time=0.3)   # remove it to make room for the between-two-curves demo

        bound = ax.plot(lambda x: 3, color=RED)   # the second curve y=3
        area2 = ax.get_area(quad, x_range=(-1.5, 1.5),   # "get_area" plus "bounded_graph": the area between the two curves
                            bounded_graph=bound, color=(BLUE_C, GREEN), opacity=0.6)
        win.play(Create(bound), run_time=0.4)   # draw the upper boundary line
        win.play(FadeIn(area2), run_time=0.6)   # the area between the two lines fades in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does:

- the first `get_area` gets no `bounded_graph`, so the area is that between the curve and the x axis; passing a colour list `color=(GREEN_B, GREEN_D)` makes a gradient along x, and `opacity=1` makes it solid.
- the second one first draws the upper boundary `y=3`, then `bounded_graph=bound` switches the integration region to between the two curves (the curve below, the line above), and `opacity=0.6` keeps a little transparency.

<video src="assets/RTM output/06-Areas-and-Riemann-Rectangles-area.mp4" controls width="560"></video>

> Note:
>
> - `bounded_graph` must be **above** `graph`, otherwise the area is negative and the direction flips.
> - `get_area` returns a `Polygon`, which can be wrapped in `FadeIn` / `Transform` animations.

## Axes.get_riemann_rectangles

```python
def get_riemann_rectangles(
    self,
    graph: ParametricFunction,
    x_range: Sequence[float] | None = None,
    dx: float = 0.1,
    input_sample_type: str = "left",
    stroke_width: float = 1,
    stroke_color: ParsableManimColor = BLACK,
    fill_opacity: float = 1,
    color: Iterable[ParsableManimColor] | ParsableManimColor = (BLUE, GREEN),
    show_signed_area: bool = True,
    bounded_graph: ParametricFunction | None = None,
    blend: bool = False,
    width_scale_factor: float = 1.001,
) -> VGroup:
```

It produces the Riemann-sum rectangle group (a `VGroup`), divided into cells by `dx` and with heights set by sampling according to `input_sample_type`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `graph` | `ParametricFunction` | required | the curve being approximated |
| `x_range` | `Sequence[float] \| None` | `None` → the curve's full range | the interval over which the rectangles are spread |
| `dx` | `float` | `0.1` | rectangle width (data units) |
| `input_sample_type` | `str` | `"left"` | sample point: `"left"`/`"right"`/`"center"` |
| `stroke_width` | `float` | `1` | rectangle stroke width |
| `stroke_color` | `ParsableManimColor` | `BLACK` | stroke colour |
| `fill_opacity` | `float` | `1` | fill opacity |
| `color` | colour / colour sequence | `(BLUE, GREEN)` | single colour or gradient (interpolated by position) |
| `show_signed_area` | `bool` | `True` | inverts the colour to show negative area when the curve is below the x axis |
| `bounded_graph` | `ParametricFunction \| None` | `None` | Riemann rectangles between two curves |
| `blend` | `bool` | `False` | whether neighbouring rectangles blend their colours |
| `width_scale_factor` | `float` | `1.001` | fine-tuning factor for the rectangle width (removing seams at the stroke) |

#### Sample: Riemann-sum approximation with `get_riemann_rectangles`

Two versions of rectangles are drawn for the same parabola:

- `dx=0.25` left-endpoint sampling (yellow, negative area colour-inverted automatically);
- after removing them, `dx=0.5` midpoint sampling + a `(BLUE, GREEN)` gradient.

```python
from real_time_manim import (
    Scene, Axes, Text,
    YELLOW, BLUE, BLUE_C, RED, GREEN, GREEN_B, GREEN_D, GREY_B, UP, DOWN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class RiemannDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("06-get_riemann_rectangles", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[-3, 3, 1], y_range=[-2, 6, 1],
                  x_length=9, y_length=5.5).add_coordinates()   # coordinate system with tick numbers
        quad = ax.plot(lambda x: 0.5 * x**2 - 0.5, color=BLUE)   # the parabola being approximated
        lab = Text("dx=0.25 left  ->  dx=0.5 center",
                   font_size=24, color=GREY_B).to_edge(DOWN)   # parameter summary label
        win.play(Create(ax), FadeIn(lab), run_time=0.6)   # the coordinate system and the label enter together
        win.play(Create(quad), run_time=0.7)   # draw the parabola

        rects = ax.get_riemann_rectangles(quad, x_range=[-2.5, 2.5],   # "get_riemann_rectangles": the Riemann-sum rectangle group
                                          dx=0.25,   # parameter "dx": rectangle width
                                          input_sample_type="left",   # parameter "input_sample_type": left-endpoint sampling
                                          color=YELLOW)   # parameter "color": single-colour fill (negative area colour-inverted automatically)
        win.play(FadeIn(rects), run_time=0.6)   # the left-endpoint rectangles fade in
        win.play(FadeOut(rects), run_time=0.3)   # remove them and switch to midpoint sampling

        rects2 = ax.get_riemann_rectangles(quad, x_range=[-2.5, 2.5],
                                           dx=0.5,   # wider, so there are fewer rectangles
                                           input_sample_type="center",   # midpoint sampling
                                           color=(BLUE, GREEN))   # multi-colour list: a gradient is made automatically
        win.play(FadeIn(rects2), run_time=0.6)   # the midpoint + gradient rectangles fade in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does:

- `dx=0.25` cuts 20 rectangles over `[-2.5, 2.5]`; left-endpoint sampling means the height is the function value at the **left end** of each small interval — the heights are negative where the curve is below the x axis, and `show_signed_area=True` inverts their colour automatically (blue-green).
- the second version has `dx=0.5`, half the number, and `input_sample_type="center"` takes the midpoint (a better approximation); `color=(BLUE, GREEN)` makes the rectangle colours run from blue to green by position.

<video src="assets/RTM output/06-Areas-and-Riemann-Rectangles-riemann.mp4" controls width="560"></video>

> Note:
>
> - the smaller `dx` is, the better the approximation, but the more rectangles there are, the slower it is.
> - `input_sample_type` must be written in full as `"left"` / `"right"` / `"center"`; abbreviations are not accepted.
> - the inverted negative area is controlled by `show_signed_area`.

---

See also: [Function graphs](05-Function-Graphs.md) · [Plot labels and helper lines](05b-Plot-Labels-and-Helper-Lines.md) · [Derivatives, antiderivatives and tangents](05c-Derivatives-Antiderivatives-and-Tangents.md)
