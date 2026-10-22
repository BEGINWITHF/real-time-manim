# Numbers and variables

Numeric displays, counters, and "variable = value" equation typesetting all live in `mobject/text/numbers.py`. They are often driven by a `ValueTracker` (an animatable number, covered in its own section in the manual) together with `set_value()` updates.

Four classes, one sample each; every sample changes each of that class's **fillable parameters** once.

> **`Integer` and `DecimalNumber` are the same parameters with two different defaults**: `Integer` is just the shortcut version with `num_decimal_places=0`, and every other parameter is shared.
> `show_ellipsis=True` appends a `...` when "the number is truncated by rounding" (e.g. `3.14159` with 2 decimal places → `3.14...`).
>
> **RTM-specific: `TextDecimalNumber`** (`real_time_manim/animations/text.py`, `class TextDecimalNumber(Text)`) — an equivalent display class rendered with `Text`, which **does not need LaTeX**, for scenes that do not depend on TeX.
> It is **not** a replacement for `DecimalNumber`: it has no `unit`/`edge_to_fix` and other parameters, and its constructor parameters are only `number`/`font_size`/`font`/`num_decimal_places`.
> ManimCE 0.21 **does not have** this class; only RTM provides it.

## Parameters

### `DecimalNumber`

```python
def __init__(self, number: float = 0, num_decimal_places: int = 2, mob_class: type[SingleStringMathTex] = MathTex, include_sign: bool = False, group_with_commas: bool = True, digit_buff_per_font_unit: float = 0.001, show_ellipsis: bool = False, unit: str | None = None, unit_buff_per_font_unit: float = 0, include_background_rectangle: bool = False, edge_to_fix: Vector3DLike = LEFT, font_size: float = 48, stroke_width: float = 0, fill_opacity: float = 1.0, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `number` | `int \| float` | `0` | initial value (the sample uses `3.14159` / `1234567.89` / `-42`) |
| `num_decimal_places` | `int` | `2` | decimal places; the sample tries 2 / 5 / 0 |
| `mob_class` | `class` | `MathTex` | the class that renders the number; the sample switches it to `Text` (no LaTeX needed) |
| `include_sign` | `bool` | `False` | whether positive numbers also show a `+` sign |
| `group_with_commas` | `bool` | `True` | thousands separators (`1,234,567.89`); the sample compares `True`/`False` |
| `digit_buff_per_font_unit` | `float` | `0.001` | digit-spacing factor (scales with the font size); the sample's `0.06` pulls them clearly apart |
| `show_ellipsis` | `bool` | `False` | append `...` when the number is truncated by rounding |
| `unit` | `str \| None` | `None` | unit suffix (the string goes through LaTeX, the sample uses `r"\pi"`) |
| `unit_buff_per_font_unit` | `float` | `0` | spacing between the unit and the number; the sample uses `0.02` |
| `include_background_rectangle` | `bool` | `False` | a background rectangle of its own (improves readability in busy scenes) |
| `edge_to_fix` | `array-like` | `LEFT` | which edge stays put when the value changes (left/right aligned, so the number does not "jitter") |
| `font_size` | `float` | `48` | font size |
| `stroke_width` | `float` | `0` | stroke width |
| `fill_opacity` | `float` | `1.0` | opacity |

Methods: `set_value(number)`, `get_value()`, `increment_value(delta_t=1)`; `font_size` is a readable and writable attribute. `digit_to_depth` and `show_tractable_zeros`, which appear in some references, **do not exist** in the current source.

#### Sample: cycling through the 13 constructor parameters + three methods

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, DecimalNumber, Integer, Variable, ValueTracker,
    Text, MathTex, Square, Dot, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene
from real_time_manim.animations.text import TextDecimalNumber

class DecimalNumberDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("12-DecimalNumber", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title
        caps = VGroup()   # every caption in this section: fades out with the numbers when the section changes, so nothing overlaps
        def c(text, mob, buff=0.3):
            m = cap(text, mob, buff)
            caps.add(m)
            return m

        # —— default 2 decimal places / a longer num_decimal_places / show_ellipsis hinting at truncation ——
        d1 = DecimalNumber(3.14159).move_to([-5.2, 2.0, 0])   # the "number" parameter
        d2 = DecimalNumber(3.14159, num_decimal_places=5).move_to([-2.2, 2.0, 0])   # the "num_decimal_places" parameter
        d3 = DecimalNumber(3.14159, num_decimal_places=2, show_ellipsis=True).move_to([1.2, 2.0, 0])   # the "show_ellipsis" parameter
        win.play(Write(d1), FadeIn(c("default 2 places", d1)), run_time=0.5)
        win.play(Write(d2), FadeIn(c("num_decimal_places=5", d2)), run_time=0.5)
        win.play(Write(d3), FadeIn(c("show_ellipsis=True", d3)), run_time=0.5)

        # —— include_sign / group_with_commas: sign and thousands separators ——
        d4 = DecimalNumber(3.14, include_sign=True).move_to([-5.2, 0.6, 0])   # the "include_sign" parameter
        d5 = DecimalNumber(1234567.89, group_with_commas=True).move_to([-2.0, 0.6, 0])   # the "group_with_commas=True" parameter
        d6 = DecimalNumber(1234567.89, group_with_commas=False).move_to([2.0, 0.6, 0])
        win.play(Write(d4), FadeIn(c("include_sign=True", d4)), run_time=0.5)
        win.play(Write(d5), FadeIn(c("commas=True", d5)), run_time=0.5)
        win.play(Write(d6), FadeIn(c("commas=False", d6)), run_time=0.5)

        # —— digit_buff_per_font_unit / unit + unit_buff_per_font_unit ——
        d7 = DecimalNumber(2024, num_decimal_places=0, digit_buff_per_font_unit=0.06,
                           font_size=60).move_to([-5.0, -1.0, 0])   # the "digit_buff_per_font_unit / font_size" parameters
        d8 = DecimalNumber(3.14, unit=r"\pi", unit_buff_per_font_unit=0.02).move_to([-1.6, -1.0, 0])   # the "unit / unit_buff_per_font_unit" parameters
        win.play(Write(d7), FadeIn(c("digit_buff=0.06", d7)), run_time=0.5)
        win.play(Write(d8), FadeIn(c("unit=pi", d8)), run_time=0.5)

        # —— mob_class / include_background_rectangle / stroke_width / fill_opacity ——
        d9 = DecimalNumber(42, num_decimal_places=0, mob_class=Text).move_to([2.0, -1.0, 0])   # the "mob_class" parameter
        d10 = DecimalNumber(7, num_decimal_places=0, include_background_rectangle=True,
                            stroke_width=2, fill_opacity=0.6,
                            color=ORANGE).move_to([4.6, -1.0, 0])   # the "include_background_rectangle / stroke_width / fill_opacity" parameters
        win.play(Write(d9), FadeIn(c("mob_class=Text", d9)), run_time=0.5)
        win.play(Write(d10), FadeIn(c("bg rect + stroke + fill", d10)), run_time=0.5)
        win.play(FadeOut(VGroup(d1, d2, d3, d4, d5, d6, d7, d8, d9, d10)), FadeOut(caps), run_time=0.4)

        # —— edge_to_fix: which edge stays put when the value changes (the number does not "jitter") ——
        left = DecimalNumber(9.99, edge_to_fix=LEFT, font_size=60).move_to([-3.2, 1.4, 0])   # the "edge_to_fix=LEFT" parameter
        right = DecimalNumber(9.99, edge_to_fix=RIGHT, font_size=60).move_to([1.6, 1.4, 0]).align_to([1.6, 0, 0], RIGHT)
        win.play(Write(left), Write(right),
                 FadeIn(cap("edge_to_fix=LEFT", left)), FadeIn(cap("edge_to_fix=RIGHT", right)), run_time=0.6)
        left.set_value(100.0)   # the "set_value(number)" method
        right.set_value(100.0)
        win.play(Write(left), Write(right), run_time=0.6)   # see which edge did not move

        # —— get_value / increment_value ——
        n = DecimalNumber(5, num_decimal_places=0, font_size=60).move_to([-1.0, -1.6, 0])
        c7 = cap("get_value()=%s" % n.get_value(), n)
        win.play(FadeIn(n), FadeIn(c7), run_time=0.5)   # the "get_value()" method
        n.increment_value(3)   # the "increment_value(delta_t)" method
        c7.become(cap("increment_value(3) -> %s" % n.get_value(), n))
        win.play(Write(n), run_time=0.5)
        n.increment_value(-1)
        c7.become(cap("increment_value(-1) -> %s" % n.get_value(), n))
        win.play(Write(n), run_time=0.5)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: Integer —— an integer counter =============================
```

What this code does: it walks through the parameters and methods of `DecimalNumber` one section at a time.

- The top half lays out four numbers first: the default 2 places, `num_decimal_places=5`, `show_ellipsis=True`, `include_sign=True`.
- The next row puts the thousands separator on and off, plus `digit_buff_per_font_unit` and `unit`+`unit_buff_per_font_unit`.
- Then one number is rendered with `mob_class=Text`, and another gets a background rectangle plus stroke and fill.
- Then a separate block compares `edge_to_fix=LEFT` against `RIGHT`: both change from `9.99` to `100.0`, and you can see that the left-aligned one keeps its left edge and the right-aligned one keeps its right edge.
- Finally `get_value()` prints the reading, and `increment_value(3)` / `increment_value(-1)` make the number jump twice in a row.

<video src="assets/RTM output/12-Numbers-and-Variables-decimal.mp4" controls width="560"></video>

> Note:
>
> - `edge_to_fix` only shows an effect when the **value gets longer or shorter** (`9.99 → 100.0`); when the length does not change, neither edge moves.
> - `set_value`/`increment_value` **change the object immediately**; to animate the change, use a `ValueTracker` with an updater (see the next sample).

### `Integer`

```python
def __init__(self, number: int = 0, num_decimal_places: int = 0, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `number` | `int` | `0` | initial integer |
| `num_decimal_places` | `int` | `0` | decimal places (the integer version fixes this at 0; the sample puts it side by side with `DecimalNumber(5, num_decimal_places=2)`) |
| Others | — | — | all of `DecimalNumber`'s parameters (the sample uses `font_size`, `color`, `include_sign`) |

Methods: `get_value()` (inherited from `DecimalNumber`).

#### Sample: default / negative / `include_sign` / compared with the decimal version / counting with `ValueTracker`

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, DecimalNumber, Integer, Variable, ValueTracker,
    Text, MathTex, Square, Dot, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene
from real_time_manim.animations.text import TextDecimalNumber

class IntegerDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("12-Integer", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— default num_decimal_places=0: no decimal point ——
        i1 = Integer(7).move_to([-5.0, 1.8, 0])   # the "number" parameter
        i2 = Integer(-42, font_size=60).move_to([-2.4, 1.8, 0])
        i3 = Integer(2024, include_sign=True).move_to([1.4, 1.8, 0])   # the other parameters are shared with DecimalNumber
        win.play(Write(i1), FadeIn(cap("Integer(7)", i1)), run_time=0.5)
        win.play(Write(i2), FadeIn(cap("Integer(-42)", i2)), run_time=0.5)
        win.play(Write(i3), FadeIn(cap("include_sign=True", i3)), run_time=0.5)

        # —— num_decimal_places must be 0 for the integer version (writing 2 brings out decimal places) ——
        i4 = Integer(5, num_decimal_places=0).move_to([-4.2, -0.2, 0])   # the "num_decimal_places" parameter
        i5 = DecimalNumber(5, num_decimal_places=2).move_to([-1.6, -0.2, 0])
        win.play(Write(i4), Write(i5),
                 FadeIn(cap("Integer vs DecimalNumber", i4)), run_time=0.6)

        # —— pair it with a ValueTracker to "count up": set_value inside the updater ——
        t = ValueTracker(0)   # the animatable number
        counter = Integer(0, font_size=72, color=TEAL).move_to([3.6, -0.6, 0])
        counter.add_updater(lambda m: m.set_value(int(t.get_value())))   # the "set_value" method
        win.play(FadeIn(counter), FadeIn(t), FadeIn(cap("tracker drives counter 0 -> 100", counter, buff=0.6)), run_time=0.6)
        win.play(t.animate.set_value(100), run_time=2.0)   # the number moves and the display follows
        win.play(FadeIn(cap("get_value()=%s" % counter.get_value(), counter, buff=1.3)), run_time=0.4)   # the "get_value()" method
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: Variable —— "variable = value" ============================
```

What this code does: three blocks demonstrated one after another.

- First three static values: `Integer(7)`, `Integer(-42, font_size=60)`, `Integer(2024, include_sign=True)`.
- Then `Integer(5)` and `DecimalNumber(5, num_decimal_places=2)` side by side, showing that the "integer version" is just 0 decimal places.
- Finally a `ValueTracker(0)` wired to `counter.add_updater(lambda m: m.set_value(int(t.get_value())))`, so that `t.animate.set_value(100)` counts the counter up from 0 to 100, and at the end `get_value()` is printed as a reading.

<video src="assets/RTM output/12-Numbers-and-Variables-integer.mp4" controls width="560"></video>

> Note: `set_value` expects a number, so inside the updater it is best to round according to what should be displayed (`int(...)`). The updater runs every frame, so do not create new objects inside it, or garbage keeps piling up.

### `Variable`

```python
def __init__(self, var: float, label: str | Tex | MathTex | Text | SingleStringMathTex, var_type: type[DecimalNumber | Integer] = DecimalNumber, num_decimal_places: int = 2, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `var` | `int \| float` | required | initial value of the variable |
| `label` | `str \| Tex \| Text \| MathTex` | required | variable name; a string is converted to `MathTex` automatically (the sample gives `"v"` and `r"{a}_{i}"`), and a `Text` can also be passed directly |
| `var_type` | `class` | `DecimalNumber` | the class that renders the value; the sample switches it to `Integer` |
| `num_decimal_places` | `int` | `2` | decimal places; the sample uses `4` |

Returns a `Variable` (a `VGroup`); the attributes `variable.label` (the label), `variable.value` (the value object) and `variable.tracker` (a `ValueTracker`), and `tracker.animate.set_value(x)` updates the displayed value.

#### Sample: default / formula label + places / `var_type=Integer` / `tracker` update / the three attributes

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, DecimalNumber, Integer, Variable, ValueTracker,
    Text, MathTex, Square, Dot, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene
from real_time_manim.animations.text import TextDecimalNumber

class VariableDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("12-Variable", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— default: var_type=DecimalNumber, num_decimal_places=2 ——
        v1 = Variable(2.5, "v").move_to([-4.4, 1.6, 0])   # the "var / label" parameters
        win.play(Write(v1), FadeIn(cap('Variable(2.5, "v")', v1)), run_time=0.6)

        # —— num_decimal_places + a formula label ——
        v2 = Variable(3.14159, r"{a}_{i}", num_decimal_places=4).move_to([-0.6, 1.6, 0])   # the "label (LaTeX) / num_decimal_places" parameters
        win.play(Write(v2), FadeIn(cap("num_decimal_places=4", v2)), run_time=0.6)

        # —— var_type: render the value with Integer; the label can also be given as a Text directly ——
        v3 = Variable(2024, Text("count", font_size=30), var_type=Integer).move_to([3.4, 1.6, 0])   # the "var_type" parameter
        win.play(Write(v3), FadeIn(cap("var_type=Integer", v3)), run_time=0.6)

        # —— tracker: animate the displayed value ——
        win.play(v1.tracker.animate.set_value(8.75), run_time=1.2)   # the "tracker" attribute: a ValueTracker
        win.play(FadeIn(cap("v1.tracker.animate.set_value(8.75)", v1)), run_time=0.5)

        # —— the three attributes: label / value / tracker ——
        info = VGroup(cap("label=%s" % type(v1.label).__name__, v1, buff=1.0),
                      cap("value=%s" % type(v1.value).__name__, v1, buff=1.5),
                      cap("tracker=%s" % type(v1.tracker).__name__, v1, buff=2.0))
        win.play(FadeIn(info), run_time=0.6)
        win.play(FadeIn(cap("value.get_value()=%s" % v1.value.get_value(), v1, buff=2.5)), run_time=0.5)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 4: TextDecimalNumber —— numbers without LaTeX (RTM-specific) ==
```

What this code does: first three "variable = value" pieces side by side.

- `Variable(2.5, "v")`: the default 2 decimal places, with a `MathTex` label.
- `Variable(3.14159, r"{a}_{i}", num_decimal_places=4)`: a LaTeX label + 4 decimal places.
- `Variable(2024, Text("count"), var_type=Integer)`: the label is given directly as a `Text`, and the value is rendered as an integer.

Then `v1.tracker.animate.set_value(8.75)` animates the value inside the equation, and at the end the types of the three attributes `v1.label` / `v1.value` / `v1.tracker` and `value.get_value()` are printed as readings.

<video src="assets/RTM output/12-Numbers-and-Variables-variable.mp4" controls width="560"></video>

> Note: the thing to animate is the **`tracker`** (`v.tracker.animate.set_value(...)`), not `value` — calling `v.value.set_value(...)` directly changes it instantly with no transition. Also, `Variable`'s label string goes through LaTeX, so something like `"{a}_{i}"` can be written directly.

### `TextDecimalNumber` RTM-specific

```python
def __init__(self, number: float = 0, font_size: float = 48, font: str = "Times New Roman", num_decimal_places: int = 2, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `number` | `float` | `0` | initial value (formatted with `f"{number:.Nf}"` and handed to `Text`) |
| `font_size` | `float` | `48` | font size (part of the cache key) |
| `font` | `str` | `"Times New Roman"` | font name (goes through Pango, the sample switches it to `"Arial"`) |
| `num_decimal_places` | `int` | `2` | decimal places; the sample does 2 / 4 / 0 once each |
| `**kwargs` | — | — | the rest is handed to `Text` (such as `color`) |

**ManimCE 0.21 does not have this class** (it only lives in `real_time_manim.animations.text`). It is a subclass of `Text`, and its method `set_value(number)` reuses the glyphs in the internal `_value_cache`, so changing the value does not re-typeset.

Because what it needs is a string, it **only accepts numbers**; it has none of `DecimalNumber`'s `unit`/`edge_to_fix`/`include_sign` parameters.

#### Sample: `number` / `num_decimal_places` / `font_size`+`font` / driven by a `tracker` / parent class

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, DecimalNumber, Integer, Variable, ValueTracker,
    Text, MathTex, Square, Dot, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene
from real_time_manim.animations.text import TextDecimalNumber

class TextDecimalDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("12-TextDecimalNumber", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— number / num_decimal_places: initial value and decimal places ——
        t1 = TextDecimalNumber(3.14159).move_to([-5.0, 1.6, 0])   # the "number" parameter (default 2 decimal places)
        t2 = TextDecimalNumber(3.14159, num_decimal_places=4).move_to([-1.6, 1.6, 0])   # the "num_decimal_places" parameter
        win.play(FadeIn(t1), FadeIn(cap("number=3.14159", t1)), run_time=0.5)
        win.play(FadeIn(t2), FadeIn(cap("num_decimal_places=4", t2)), run_time=0.5)

        # —— font_size / font: font size and font (both rendered with Text, no LaTeX needed) ——
        t3 = TextDecimalNumber(2024, num_decimal_places=0, font_size=72,
                               font="Arial").move_to([-4.6, -0.6, 0])   # the "font_size / font" parameters
        win.play(FadeIn(t3), FadeIn(cap('font_size=72 font="Arial"', t3)), run_time=0.5)

        # —— changing the value: set_value changes it immediately, only a ValueTracker with an updater animates ——
        t4 = TextDecimalNumber(0, num_decimal_places=1, font_size=60,
                               color=TEAL).move_to([1.6, -0.6, 0])
        tracker = ValueTracker(0)
        t4.add_updater(lambda m: m.set_value(tracker.get_value()))   # the "set_value" method
        win.play(FadeIn(t4), FadeIn(tracker), FadeIn(cap("tracker 0 -> 9.5", t4, buff=0.6)), run_time=0.6)
        win.play(tracker.animate.set_value(9.5), run_time=1.6)   # the number changes continuously

        # —— it really is a Text: every Text attribute works ——
        t5 = TextDecimalNumber(12.5, num_decimal_places=1).move_to([4.4, 1.6, 0])
        win.play(FadeIn(t5), FadeIn(cap("parent = %s" % type(t5).__mro__[1].__name__, t5)), run_time=0.6)
        win.play(FadeIn(cap("accepts only number/font_size/font/num_decimal_places", t5, buff=0.8, size=16)), run_time=0.5)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window
```

What this code does: four sections.

- First `TextDecimalNumber(3.14159)` (the default 2 places) and `num_decimal_places=4` (two places more).
- Then `font_size=72` and `font="Arial"` are given together, showing that both the font size and the font can be changed and that **no LaTeX is needed**.
- Then a `ValueTracker(0)` is wired to its `set_value`, rolling the number continuously from 0 to 9.5 (internally it swaps cached glyphs rather than recompiling LaTeX, so the roll is very light).
- Finally its parent class name is printed on screen, labelled "accepts only `number/font_size/font/num_decimal_places`".

<video src="assets/RTM output/12-Numbers-and-Variables-textdecimal.mp4" controls width="560"></video>

> Note: it is **not** a replacement for `DecimalNumber` — `DecimalNumber`'s digits go through LaTeX (math font, can write `unit`, can `edge_to_fix`), while this is ordinary text typesetting. To display numbers in an environment without TeX it is a good fit; for a "mathematical flavour" of number, use `DecimalNumber`.

---

See also: [LaTeX](09-LaTeX.md) · [Text](08-Text.md) · [Matrices](13-Matrices.md)
