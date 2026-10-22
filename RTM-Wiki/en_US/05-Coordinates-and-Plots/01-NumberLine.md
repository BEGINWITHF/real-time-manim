# Number line NumberLine

`NumberLine` is a straight line with ticks, and it is the underlying implementation of every axis of `Axes` / `NumberPlane` / `BarChart`. You can also use it on its own as a timeline or to animate a point moving along a number line. This page covers the constructor parameters; the methods (`n2p`, `add_numbers`, `add_labels`, …) are on [Number line methods](01b-NumberLine-Methods.md).

## Parameters

### class NumberLine

```python
def __init__(self, x_range: Sequence[float] | None = None, length: float | None = None,
             unit_size: float = 1, include_ticks: bool = True, tick_size: float = 0.1,
             numbers_with_elongated_ticks: Iterable[float] | None = None,
             longer_tick_multiple: int = 2, exclude_origin_tick: bool = False,
             rotation: float = 0, stroke_width: float = 2.0, include_tip: bool = False,
             tip_width: float = 0.35, tip_height: float = 0.35,
             tip_shape: type[ArrowTip] | None = None, include_numbers: bool = False,
             font_size: float = 36, label_direction: Point3DLike = DOWN,
             label_constructor: type = MathTex, scaling: _ScaleBase = LinearBase(),
             line_to_number_buff: float = 0.25, decimal_number_config: dict | None = None,
             numbers_to_exclude: Iterable[float] | None = None,
             numbers_to_include: Iterable[float] | None = None, **kwargs: Any) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `x_range` | `Sequence[float] \| None` | `None` → `[-7, 7, 1]` | `[x_min, x_max, x_step]`; a two-element tuple gets `step=1` filled in automatically; `step` sets how dense the ticks / number labels are |
| `length` | `float \| None` | `None` | total length of the number line (Manim units); once given it overrides `unit_size` and back-solves it |
| `unit_size` | `float` | `1` | spacing between adjacent integer ticks; takes effect when `length` is not given |
| `include_ticks` | `bool` | `True` | whether to draw tick marks |
| `tick_size` | `float` | `0.1` | tick mark length |
| `numbers_with_elongated_ticks` | `Iterable[float] \| None` | `None` | values whose ticks should be elongated, e.g. `[-2, 4]` |
| `longer_tick_multiple` | `int` | `2` | how many times longer an elongated tick is than an ordinary one |
| `exclude_origin_tick` | `bool` | `False` | whether to drop the tick at 0 (`Axes` linear axes set this to `True` by default) |
| `rotation` | `float` | `0` | rotation angle of the whole number line (radians) |
| `stroke_width` | `float` | `2.0` | stroke width |
| `include_tip` | `bool` | `False` | whether to add an arrow at the end |
| `tip_width` | `float` | `0.35` | arrow width |
| `tip_height` | `float` | `0.35` | arrow height |
| `tip_shape` | `type[ArrowTip] \| None` | `None` | arrow-tip class (e.g. `StealthTip`); `None` uses the default tip |
| `include_numbers` | `bool` | `False` | whether to show number labels in the `label_direction` |
| `font_size` | `float` | `36` | font size of the numbers / labels |
| `label_direction` | `Point3DLike` | `DOWN` | direction of the labels relative to the number line |
| `label_constructor` | `type` | `MathTex` | label text class (`MathTex`/`Tex`/`Text`…) |
| `scaling` | `_ScaleBase` | `LinearBase()` | tick scaling mode; pass `LogBase()` for a logarithmic line (see [Ticks and scaling](10-Ticks-and-Scaling.md)) |
| `line_to_number_buff` | `float` | `0.25` | distance between the labels and the number line |
| `decimal_number_config` | `dict \| None` | automatic | forwarded to `DecimalNumber`; by default the number of decimal places is inferred from `step` |
| `numbers_to_exclude` | `Iterable[float] \| None` | `None` | do not label these values |
| `numbers_to_include` | `Iterable[float] \| None` | `None` | label only these values (passing it triggers adding numbers, no need for `include_numbers=True`) |
| `**kwargs` | — | — | forwarded to `Line` (`color`, `stroke_opacity`, …) |

> **Returns**: a `NumberLine` instance (`VMobject`). Commonly used attributes after construction: `numbers` (the number group), `labels`, `ticks`, `x_range`/`x_min`/`x_max`/`x_step`, `unit_size`, `scaling`.

> When `x_range` contains both positive and negative values, ticks count from 0, and there is **not necessarily** a tick at `min`/`max` (it depends on `step`).

#### Sample: basic construction with `x_range`/`length`/`include_tip`/`include_numbers`

The four most-used parameters in one go: data range `[-4,4]`, total length `8`, with an arrow and with numbers; the red dot moves along the axis with `n2p`.

```python
from real_time_manim import Scene, NumberLine, Dot, Text, \
    YELLOW, RED, GREY_B, UP, DOWN, Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class NumberLineBasicDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-NumberLine", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        line = NumberLine(x_range=[-4, 4, 1], length=8,   # parameter "x_range": data range and step; "length": total length 8
                         include_numbers=True, include_tip=True)   # parameters "include_numbers"/"include_tip": number labels + end arrow
        dot = Dot(line.n2p(2), color=RED)   # use "n2p" to turn the value 2 into a scene point (see 01b)
        lab = Text("x_range=[-4,4,1]  length=8  tip+numbers",
                   font_size=26, color=GREY_B).next_to(line, DOWN, buff=0.6)   # parameter description label
        win.play(Create(line), run_time=0.8)   # draw the whole number line (ticks, numbers, arrow)
        win.play(FadeIn(dot), FadeIn(lab), run_time=0.4)   # the red dot and the label fade in
        win.play(dot.animate.move_to(line.n2p(-3)), run_time=1.0)   # move the red dot along the axis to the value -3
        win.play(dot.animate.move_to(line.n2p(3.5)), run_time=1.0)   # then to the value 3.5 (it can stop between ticks)
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: it first draws a number line running from -4 to 4, 8 Manim units long. `x_range` sets the data range and the tick step, `length` sets the on-screen length, and together they fix the scale; `include_numbers=True` automatically hangs numbers below the axis and `include_tip=True` adds an arrow at the right end.

Then the red dot lands on the value 2 via `n2p(2)` and moves to -3 and 3.5 in turn — `n2p` is the "value → scene point" converter.

<video src="assets/RTM output/01-NumberLine-basic.mp4" controls width="560"></video>

> Note:
>
> - Once you give `length`, stop worrying about `unit_size`; it gets back-solved and overridden.
> - The arrow is drawn beyond `x_max`, so do not put the red dot / label exactly on `x_max` or it will overlap the arrow.
> - Number-line numbers use `MathTex` by default: **with the `real-time-manim[typst]` extra installed (and `RTM_TYPST=0` not set) they are compiled by the Typst backend, otherwise they are real LaTeX**; for a plain-text look pass `label_constructor=Text`.

### UnitInterval

```python
def __init__(self, unit_size: float = 10, numbers_with_elongated_ticks: list[float] | None = None,
             decimal_number_config: dict | None = None, **kwargs: Any) -> None:
```

A number line specialised for the `[0, 1]` interval; it is a `NumberLine` subclass and has all of its methods. The default step is 0.1 with one decimal place, and the ticks at 0 and 1 are elongated — the building block for probability intervals and Bayesian diagrams.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `unit_size` | `float` | `10` | unit length (longer than an ordinary number line, filling the frame) |
| `numbers_with_elongated_ticks` | `list[float] \| None` | `[0, 1]` | positions of the elongated ticks |
| `decimal_number_config` | `dict \| None` | `{"num_decimal_places": 1}` | number format |
| `**kwargs` | — | — | forwarded to `NumberLine` (`x_range` etc. is forwarded and overridden too) |

> **Returns**: a `UnitInterval` instance.

#### Sample: the default look of `UnitInterval`

The defaults work straight away: 0~1 filling 10 units, a 0.1 tick step, one-decimal labels, and elongated ticks at both ends.

```python
from real_time_manim import Scene, UnitInterval, Text, \
    YELLOW, GREY_B, UP, DOWN, Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class UnitIntervalDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-UnitInterval", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        line = UnitInterval(unit_size=10)   # parameter "unit_size": 0~1 fills 10 Manim units
        line.add_numbers()   # a 0.1 step automatically gives one-decimal labels, and 0/1 ticks are elongated
        lab = Text("UnitInterval(unit_size=10)", font_size=28,
                   color=GREY_B).next_to(line, DOWN, buff=0.6)   # parameter description label
        win.play(Create(line), run_time=0.8)   # draw the number line for [0,1]
        win.play(FadeIn(lab), run_time=0.4)   # the label fades in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: `UnitInterval(unit_size=10)` draws a number line dedicated to [0,1], and `add_numbers()` hangs a one-decimal number under every 0.1 tick, with the ticks at 0 and 1 elongated to twice their length by default. Compared with writing `NumberLine(x_range=[0,1,0.1], ...)` by hand, it has the "elongated end ticks + decimal labels" pair configured by default.

<video src="assets/RTM output/01-NumberLine-unitinterval.mp4" controls width="560"></video>

> Note:
>
> - `UnitInterval`'s `x_range` can still be overridden through `**kwargs`, but once overridden it is no longer a "unit interval" and you might as well use `NumberLine` directly.
> - Numbers on the axis use `MathTex` (**with the `real-time-manim[typst]` extra installed and `RTM_TYPST=0` not set they are compiled by the Typst backend, otherwise they are real LaTeX**); a slight difference from CE's LaTeX letterforms is normal.

---

See also: [Number line methods](01b-NumberLine-Methods.md) · [Two-dimensional coordinate system](02-Axes.md) · [Ticks and scaling](10-Ticks-and-Scaling.md)
