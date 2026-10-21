# Number line methods (conversion, labels and ticks)

Every commonly used method on `NumberLine` besides its constructor parameters lives here:

- Two-way value ⇄ scene-point conversion: `n2p` / `p2n`
- Hanging numbers and arbitrary labels after the fact: `add_numbers` / `add_labels`
- Adding ticks and recoloring them all at once: `add_ticks` / `get_tick_marks`
- Rotating about a value: `rotate_about_number`

## Methods

### n2p / p2n (value ⇄ scene point)

```python
def number_to_point(number: float | np.ndarray) -> np.ndarray:   # alias n2p
def point_to_number(point: Point3DLike) -> float:                # alias p2n
```

The two-way "value ↔ scene coordinate" conversion on a number line, and the only correct way to place any element (`Dot`, `Text`, `next_to`); a scaled number line (`LogBase`) runs through `scaling.inverse_function` first. The `number_line @ value` form is also supported.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `number` | `float \| np.ndarray` | required | the value on the number line; you can pass an array to convert several at once |
| `point` | `Point3DLike` | required | scene coordinate point `[x, y, z]`; you can also pass an array of points |

> **Returns**: `n2p` → an `np.ndarray` scene point; `p2n` → `float` (an array input returns an `np.ndarray`).

#### Sample: two-way conversion with `n2p`/`p2n`/`@`

The red dot first lands via `n2p(1.5)` and then moves along the axis; once it arrives, `p2n` reads the scene coordinate back into a numeric text. The yellow dot demonstrates the `number_line @ value` `@` form.

```python
from real_time_manim import Scene, NumberLine, Dot, Text, \
    YELLOW, RED, GREEN, GREY_B, UP, DOWN, Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class N2PP2NDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01b-n2p-p2n", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        line = NumberLine(x_range=[-2.5, 3, 0.5], length=10)   # half-unit-step number line
        line.add_numbers(x_values=[-2, 0, 2])   # only label -2/0/2
        lab = Text("n2p/p2n  value <-> point", font_size=28,
                   color=GREY_B).next_to(line, DOWN, buff=0.6)   # method description label
        win.play(Create(line), run_time=0.8)   # draw the number line
        win.play(FadeIn(lab), run_time=0.3)   # the label fades in

        red = Dot(line.n2p(1.5), color=RED)   # "n2p": value 1.5 -> scene point
        readout = Text("p2n=0.00", font_size=28, color=GREEN).next_to(lab, DOWN, buff=0.35)
        win.play(FadeIn(red), FadeIn(readout), run_time=0.4)   # the red dot and the readout label fade in
        win.play(red.animate.move_to(line.n2p(-1.5)), run_time=1.0)   # move the red dot to the value -1.5
        point = red.get_center()   # take the red dot's current scene coordinate
        readout.become(Text("p2n=%.2f" % line.p2n(point),   # "p2n": scene point -> value, read back as text
                            font_size=28, color=GREEN).next_to(lab, DOWN, buff=0.35))
        win.play(Wait(0.6))   # pause 0.6s to see the read-back result

        yel = Dot(line @ 3, color=YELLOW)   # the "@" form: equivalent to n2p(3)
        tag = Text("line @ 3", font_size=28, color=YELLOW).next_to(yel, UP, buff=0.3)
        win.play(FadeIn(yel), FadeIn(tag), run_time=0.4)   # the yellow dot and label fade in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: the red dot is born at `n2p(1.5)` (the scene point for the value 1.5); after it moves to -1.5, `p2n(red.get_center())` reverses its scene coordinate back into a value, and `-1.50` is displayed directly at the bottom of the screen — the two methods are each other's inverse. The yellow dot uses `line @ 3` to sit at the value 3, with exactly the same effect as `n2p(3)`.

<video src="assets/RTM output/01b-NumberLine-Methods-n2p_p2n.mp4" controls width="560"></video>

> Note: `number_line @ value` only accepts a scalar value; the other way round, `point @ number_line` can only take a plain `list`/`tuple` — an `np.ndarray` is grabbed by numpy and interpreted as matrix multiplication, raising an error; to be safe use `p2c`/`p2n`.

### add_numbers / add_labels

```python
def add_numbers(self, x_values: Iterable[float] | None = None, excluding: Iterable[float] | None = None,
                font_size: float | None = None, label_constructor: type | None = None,
                **kwargs) -> Self
def add_labels(self, dict_values: dict[float, str | float | VMobject], direction: Point3DLike | None = None,
               buff: float | None = None, font_size: float | None = None,
               label_constructor: type | None = None) -> Self
```

`add_numbers` hangs `DecimalNumber` labels at the given values; with `x_values=None` it uses every tick value from `get_tick_range()`, and after creation they are reachable via `self.numbers`. `add_labels` places arbitrary labels at given positions using a `{value: label}` dict (`Axes.add_coordinates(dict)` calls it internally), and the label group is stored in `self.labels`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `x_values` | `Iterable[float] \| None` | `None` | values to label; all ticks by default |
| `excluding` | `Iterable[float] \| None` | `numbers_to_exclude` | values to exclude |
| `dict_values` | `dict[float, str \| float \| VMobject]` | required | e.g. `{1: "Monday"}`; a `str` is handed to `label_constructor` |
| `direction` | `Point3DLike \| None` | `label_direction` | placement direction of the labels relative to the number line |
| `buff` | `float \| None` | `line_to_number_buff` | distance to the number line |
| `font_size` | `float \| None` | `font_size` | font size (the label must have a `font_size` attribute, otherwise an `AttributeError` is raised) |
| `label_constructor` | `type \| None` | the number line's `label_constructor` | class used to render `str` labels |
| `**kwargs` | — | — | `add_numbers` forwards them to `get_number_mobject` (e.g. `num_decimal_places`) |

> **Returns**: `Self` (chainable).

#### Sample: `add_numbers` with explicit values + arbitrary `add_labels`

On the same half-unit-step number line: `add_numbers([-2,0,2], num_decimal_places=1)` labels only three values with one decimal place, and `add_labels({0:"start", 3:"end"}, direction=UP)` puts two text labels above the axis.

```python
from real_time_manim import Scene, NumberLine, Text, \
    YELLOW, GREY_B, UP, DOWN, Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class AddNumbersLabelsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01b-add_numbers-labels", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        line = NumberLine(x_range=[-2.5, 3, 0.5], length=10)   # half-unit-step number line
        line.add_numbers(x_values=[-2, 0, 2], num_decimal_places=1)   # "add_numbers": label only the given values, keeping one decimal place
        line.add_labels({0: "start", 3: "end"}, direction=UP, font_size=28)   # "add_labels": replace values with arbitrary text labels
        lab = Text("add_numbers([-2,0,2]) + add_labels({0:start,3:end})",
                   font_size=24, color=GREY_B).next_to(line, DOWN, buff=0.6)   # method description label
        win.play(Create(line), run_time=0.8)   # draw the number line
        win.play(FadeIn(lab), run_time=0.4)   # the label fades in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: the number line has ticks every 0.5, but `add_numbers(x_values=[-2, 0, 2], num_decimal_places=1)` only hangs numbers at -2.0, 0.0 and 2.0. Number positions need not correspond one-to-one with the ticks; `num_decimal_places` is forwarded to the number generator through `**kwargs`.

`add_labels({0: "start", 3: "end"}, direction=UP)` then puts two custom texts **above** the axis, with the dict's keys deciding the position and its values being exactly the displayed content.

<video src="assets/RTM output/01b-NumberLine-Methods-addnumbers.mp4" controls width="560"></video>

> Note:
>
> - `add_labels` renders `str` values with `MathTex` by default (math italic); for an upright look, pass a `Text` object as the value or change to `label_constructor=Text`.
> - `font_size` requires the label object to have an attribute of the same name; `Text`/`MathTex`/`DecimalNumber` all have one, while a bare `VMobject` does not and raises `AttributeError`.

### Ticks and rotation: get_tick_range / add_ticks / get_tick_marks / rotate_about_number / get_unit_size

```python
def get_tick_range(self) -> np.ndarray                  # compute the array of tick values from x_range
def add_ticks(self) -> None                             # draw the ticks from x_range
def get_tick(self, x: float, size: float | None = None) -> Line
def get_tick_marks(self) -> VGroup                      # the full tick group
def rotate_about_number(self, number: float, angle: float, axis: Vector3D = OUT, **kwargs) -> Self
def get_unit_size(self) -> float                        # how many Manim units 1 value unit is
def get_unit_vector(self) -> Vector3D                   # the directed step per unit
```

`get_tick_range()` accounts for `exclude_origin_tick` and `scaling`, and is the behind-the-scenes computation for `include_numbers`/`add_ticks`. `get_tick(x)` builds a single tick, and `get_tick_marks()` retrieves the whole tick group so you can recolor or animate it all at once. `rotate_about_number` rotates the whole axis about the point corresponding to a value (`ThreeDAxes` uses it to place the z axis too).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `x` / `number` | `float` | required | the value the tick sits at / the value at the rotation centre |
| `size` | `float \| None` | `tick_size` | scale factor of a single tick (only `get_tick`) |
| `angle` | `float` | required | rotation angle (radians) |
| `axis` | `Vector3D` | `OUT` | rotation axis |

> **Returns**: see the signature; `rotate_about_number` returns `Self` (chainable).

#### Sample: `add_ticks`/`get_tick_marks` to add and recolor ticks, `rotate` about zero

First build a number line with no ticks, then `add_ticks()` fills them in after the fact, `get_tick_marks()` grabs every tick and colors them all yellow, then the `get_unit_size()` value is displayed and the whole axis is rotated 0.5 radians about the value 0.

```python
from real_time_manim import Scene, NumberLine, Text, VGroup, \
    YELLOW, GREEN, GREY_B, UP, DOWN, Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class TicksRotateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01b-ticks-rotate", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        line = NumberLine(x_range=[-2, 2, 1], length=6, include_ticks=False)   # don't draw ticks to begin with
        line.add_ticks()   # "add_ticks": fill in the ticks afterwards from x_range
        line.get_tick_marks().set_color(YELLOW)   # "get_tick_marks": grab all ticks and recolor them at once
        lab1 = Text("add_ticks() + get_tick_marks().set_color(YELLOW)",
                    font_size=24, color=GREY_B).next_to(line, DOWN, buff=0.6)   # method description label
        lab2 = Text("unit_size=%.2f" % line.get_unit_size(),   # "get_unit_size": the on-screen length of 1 value unit
                    font_size=26, color=GREEN).next_to(lab1, DOWN, buff=0.3)
        win.play(Create(line), run_time=0.8)   # draw the number line (including the added yellow ticks)
        win.play(FadeIn(VGroup(lab1, lab2)), run_time=0.4)   # the two label lines fade in
        win.play(Wait(0.4))   # pause to look at the tick color
        win.play(line.animate(run_time=1.0).rotate(0.5, about_point=line.n2p(0)))   # rotate the whole axis about the point for the value 0
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: `include_ticks=False` builds a bare axis, `add_ticks()` puts the ticks back afterwards from `x_range`, and `get_tick_marks()` grabs them all at once and colors them yellow (`get_tick(2.0)` can also build or edit a single one). The bottom of the screen shows `get_unit_size()` — here `length=6` over a span of 4, so exactly 1.5 Manim units per value unit. Finally `rotate(0.5, about_point=line.n2p(0))` spins the whole axis about the scene point for the value 0, with the same effect as `rotate_about_number(0, 0.5)`.

<video src="assets/RTM output/01b-NumberLine-Methods-ticks.mp4" controls width="560"></video>

### Number mobjects: get_number_mobject / get_number_mobjects / get_labels (table only)

```python
def get_number_mobject(self, x: float, direction: Vector3D | None = None, buff: float | None = None,
                       font_size: float | None = None, label_constructor: type | None = None,
                       **number_config) -> VMobject
def get_number_mobjects(self, *numbers: float, **kwargs) -> VGroup
def get_labels(self) -> VGroup
```

Generates a position-placed number mobject **without adding it** to the number line straight away, which is handy for animating a single number on its own; `get_labels()` is equivalent to `get_number_mobjects()` with no arguments.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `x` | `float` | required | the value to generate a label for |
| `direction` | `Vector3D \| None` | `label_direction` | placement direction |
| `buff` | `float \| None` | `line_to_number_buff` | distance to the axis |
| `font_size` | `float \| None` | `font_size` | font size |
| `label_constructor` | `type \| None` | the number line's setting | text constructor class |
| `**number_config` | — | — | merged into `decimal_number_config`, e.g. `num_decimal_places=2` |

---

See also: [Number line NumberLine](01-NumberLine.md) · [Coordinate conversion](03-Coordinate-Conversion.md) · [Ticks and scaling](10-Ticks-and-Scaling.md)
