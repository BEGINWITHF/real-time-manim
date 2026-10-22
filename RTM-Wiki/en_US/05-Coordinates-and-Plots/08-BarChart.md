# Bar chart BarChart

RTM uses the generic vector fallback renderer (verified by real render on 2026-10-11; the fallback draws correctly). Bar charts inherit from `Axes`, so `c2p`, `plot`, `get_area`, `x_axis_config` / `y_axis_config` are all available.

## BarChart

`BarChart(values, bar_names=None, y_range=None, x_length=None, y_length=None, bar_colors=["#003f5c", "#58508d", "#bc5090", "#ff6361", "#ffa600"], bar_width=0.6, bar_fill_opacity=0.7, bar_stroke_width=3, **kwargs)`

Construction lays out the bars, adds numbers to the y axis and `bar_names` labels to the x axis automatically. Internally `x_range=[0, len(values), 1]` and `tips=False` are fixed; the x axis defaults to `font_size=24` and `label_constructor=Tex`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `values` | `MutableSequence[float]` | required | the value of each bar, **may be negative** |
| `bar_names` | `Sequence[str] \| None` | `None` | x-axis labels; shorter than `values` is fine, **longer than `values` will index out of range**; labels for negative bars are placed above the axis automatically |
| `y_range` | `Sequence[float] \| None` | automatic `[min(0,min(v)), max(0,max(v)), round(max(v)/y_length, 2)]` | y-axis range and step; passing a 2-tuple fills in the step automatically |
| `x_length` | `float \| None` | `min(len(values), frame_width-2)` | x-axis length |
| `y_length` | `float \| None` | `frame_height - 4` (=4) | y-axis length |
| `bar_colors` | `Iterable[str]` | 5-color palette (see signature) | bar color; interpolates a gradient automatically when the length differs from `values`; **must be a list** (passing a `str` is removed after v0.17 and warns) |
| `bar_width` | `float` | `0.6` | bar width (0~1, fraction of the cell) |
| `bar_fill_opacity` | `float` | `0.7` | fill opacity |
| `bar_stroke_width` | `float` | `3` | bar stroke width |
| `**kwargs` | — | — | forwarded to `Axes`: `x_axis_config`, `y_axis_config`, `y_range`, etc. |

Key attributes: `bars` (`VGroup[Rectangle]`), `values`, `bar_names`, `bar_colors`, `x_labels`, `bar_labels`.

## BarChart.get_bar_labels

`BarChart.get_bar_labels(color=None, font_size=24, buff=0.25, label_constructor=Tex) -> VGroup`

Adds a value label to the top of each bar (above for positive bars, below for negative bars). It **only returns; it does not add automatically** — you must call `self.add(...)` yourself. It also does not write back to `chart.bar_labels` (that attribute is `None` at construction); store the return value in a variable.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | `ParsableManimColor \| None` | `None` (follows the bar fill color) | label color |
| `font_size` | `float` | `24` | font size |
| `buff` | `float` | `0.25` | distance from the bar |
| `label_constructor` | `type[MathTex]` | `Tex` | text class (pass `MathTex` for a math font) |

## BarChart.change_bar_values

`BarChart.change_bar_values(values, update_colors=True) -> None`

**Updates the bar heights in place** (without rebuilding the chart); it is the core method for "value growth" animations (`Transform` / `always_redraw`). The new `values` need not have the same length as the old ones (extra entries are ignored); a bar whose old height was 0 is rebuilt.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `values` | `Iterable[float]` | required | the new bar values |
| `update_colors` | `bool` | `True` | whether to re-apply the `bar_colors` gradient |

## Sample 1: Construction + `get_bar_labels`

Construction lays out the bars, adds numbers to the y axis and `bar_names` labels to the x axis automatically; `get_bar_labels` additionally **returns** top-of-bar value labels. The sample uses `values` with negative numbers so negative bars point down automatically, and gives `y_range` as only a 2-tuple so the step is filled in automatically.

```python
from real_time_manim import (
    BarChart, DOWN, FadeIn, GREY_B, Scene, Text, UP, WHITE, YELLOW,
    Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class BasicDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("08-BarChart", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        chart = BarChart(values=[-4, 6, -2, 3],   #parameter "values": may be negative; negative bars point down automatically
                         bar_names=["one", "two", "three", "four"],   #parameter "bar_names": x-axis labels
                         y_range=[-7, 9, 2],   #parameter "y_range": a 2-tuple fills in the step automatically
                         y_length=5.5, x_length=10,   #on-screen length of both axes
                         x_axis_config={"font_size": 24})   #forwarded to Axes: x-axis tick font size
        labels = chart.get_bar_labels(color=WHITE, font_size=24)   #"get_bar_labels": top-of-bar value labels (only returns; add them yourself)
        win.play(FadeIn(chart), run_time=0.8)   #the whole coordinate system and the bars fade in
        win.play(FadeIn(labels), run_time=0.4)   #the value labels fade in
        win.play(Wait(0.8))   #wait 0.8s
        win.close()   #close the RTM window
```

What this code does:

- `BarChart` inherits from `Axes`; at construction it turns `values` into a row of `Rectangle`s (`chart.bars`), with negative bars drawn downward; the y-axis tick numbers and the x-axis `bar_names` labels are generated together (`label_constructor` defaults to `Tex`).
- `get_bar_labels()` then generates a `VGroup` of value labels at the top of each bar (the bottom for negative bars) — it **only returns and does not put anything on screen automatically**; the sample explicitly `FadeIn(labels)`.

<video src="assets/RTM output/08-BarChart-basic.mp4" controls width="560"></video>

> Note:
>
> - `bar_names` **longer than** `values` **will index out of range** (shorter is fine).
> - The return value of `get_bar_labels` is not written back to `chart.bar_labels` (that attribute is `None` at construction); store it in a variable yourself before putting it on screen.

## Sample 2: `change_bar_values` changes bar heights in place

`change_bar_values(values)` **changes the bar heights in place** without rebuilding the chart; playing it through `.animate` gives smooth growth / shrink. The sample goes from `[3, 4, 2]` to `[7, 5, 3]` and then `[1, 2, 9]`.

```python
from real_time_manim import (
    BarChart, DOWN, FadeIn, GREY_B, Scene, Text, UP, WHITE, YELLOW,
    Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class ChangeValuesDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("08-change_bar_values", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        chart = BarChart(values=[3, 4, 2],   #starting bar heights
                         bar_names=["A", "B", "C"],
                         y_range=[0, 10, 2],
                         y_length=5, x_length=9,
                         x_axis_config={"font_size": 24})
        lab = Text("chart.animate.change_bar_values(...)", font_size=24,
                   color=GREY_B).to_edge(UP).shift(DOWN * 0.9)   #place the caption below the title
        win.play(FadeIn(chart), FadeIn(lab), run_time=0.8)   #the coordinate system and the caption appear together
        win.play(chart.animate.change_bar_values([7, 5, 3]),   #"change_bar_values": change bar heights in place
                 run_time=1.0)   #smooth transition through .animate
        win.play(chart.animate.change_bar_values([1, 2, 9]),
                 run_time=1.0)   #change them again
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window
```

What this code does: `change_bar_values` is itself a synchronous method, so calling it directly only snaps in the next frame. The sample wraps it as an animation with `chart.animate.change_bar_values(...)`, so the bar heights and colors interpolate continuously over 1 second.

This is the core technique for "value growth" animations; combined with `always_redraw` / `ValueTracker` it can follow frame by frame.

<video src="assets/RTM output/08-BarChart-changevalues.mp4" controls width="560"></video>

> Note:
>
> - The new `values` length **need not** match the old ones (extra entries are ignored; a bar whose old height was 0 is rebuilt).
> - `update_colors=True` (the default) re-applies the `bar_colors` gradient.

See also: [Two-dimensional coordinate system](02-Axes.md) · [Coordinate conversion](03-Coordinate-Conversion.md) · [Areas and Riemann rectangles](06-Areas-and-Riemann-Rectangles.md)
