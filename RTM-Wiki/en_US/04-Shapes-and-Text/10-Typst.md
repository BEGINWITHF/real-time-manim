# Typst

RTM has a built-in **Typst** rendering path: typeset formulas and text without installing LaTeX. The three samples are `Typst` (typesetting a whole block of content), `TypstMath` (writing just a maths expression), and `MathTex`'s **automatic routing** (write LaTeX as usual and it is converted to Typst typesetting internally).

> **RTM-only**: `Typst` / `TypstMath` are RTM typesetting classes; ManimCE 0.21 does **not** have `TypstMath`, so all three samples in this section are **RTM renders only** (there is no ManimCE counterpart).
>
> **The first render waits for the compiler**: with a cold cache a Typst (or fallback LaTeX) compile takes a few hundred milliseconds to a second or two; with a visible window RTM pops up a small "compiling formula" notice (see [Live window MLWindow](../00-Getting-Started/03-Live-Window-MLWindow.md)); it is not a hang.

## Parameters

### `Typst`

```python
def __init__(self, typst_code: str, *, font_size: float = 48, typst_preamble: str = "", color: ParsableManimColor | None = None, stroke_width: float | None = None, font_paths: list[str | Path] | None = None, track_baselines: bool = False, should_center: bool = True, height: float | None = None) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `typst_code` | `str` | required | the Typst source; maths goes inside `$...$` (e.g. `"The area is $pi r^2$"`) |
| `font_size` | `float` | `48` | font size; the sample uses 40 / 36 |
| `typst_preamble` | `str` | `""` | **definitions prepended** to the source (`#set`, `#let`, etc.); the sample uses it to set the text size |
| `color` | `ManimColor \| None` | `None` | overall colour; the sample uses `TEAL` |
| `stroke_width` | `float \| None` | `None` | stroke width; the sample uses `1` |
| `font_paths` | `list \| None` | `None` | extra font directories (for custom fonts) |
| `track_baselines` | `bool` | `False` | whether to lay out on baselines (useful for multi-line text) |
| `should_center` | `bool` | `True` | whether to centre the result at the origin; `False` in the sample keeps the original position |
| `height` | `float \| None` | `None` | scale to a given height (an alternative to `font_size`) |

#### Sample: font size / colour and stroke / preamble / not centred + height

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Typst, TypstMath, MathTex, Text,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class TypstDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("10-Typst", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— default: font_size=48, centred; Typst syntax ($...$ holds maths) ——
        t1 = Typst("The area is $pi r^2$", font_size=40).move_to([0, 1.4, 0])   # the "typst_code / font_size" parameters
        win.play(Write(t1), FadeIn(cap("Typst(...font_size=40)", t1)), run_time=0.7)

        # —— color / stroke_width: overall colour and stroke ——
        t2 = Typst("bold text #text(fill: red)[red]", font_size=40,
                   color=TEAL, stroke_width=1).move_to([0, -0.2, 0])   # the "color / stroke_width" parameters
        win.play(Write(t2), FadeIn(cap("color=TEAL, stroke_width=1", t2)), run_time=0.7)

        # —— typst_preamble: prepend definitions to the whole block (here defining a colour) ——
        t3 = Typst("#let hot = rgb(\"#ff6600\")\nA #text(fill: hot)[hot] word",
                   font_size=36, typst_preamble='#set text(size: 12pt)')   # the "typst_preamble" parameter
        t3.move_to([0, -1.8, 0])
        win.play(Write(t3), FadeIn(cap("typst_preamble definitions", t3)), run_time=0.7)

        # —— should_center / height: not centred, scaled by height ——
        t4 = Typst("H", font_size=72, should_center=False, height=1.2)   # the "should_center / height" parameters
        t4.move_to([4.6, 1.4, 0])
        win.play(Write(t4), FadeIn(cap("height=1.2", t4)), run_time=0.6)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: TypstMath —— writing just a maths expression =============
```

What this code does: four `Typst` objects, each demonstrating one group of parameters.

- The first is the plainest Typst text (`$pi r^2$` is maths).
- The second adds `color=TEAL` and `stroke_width=1`.
- The third uses `typst_preamble` to write `#set text(size: 12pt)` first, which makes the `#text(fill: hot)[hot]` in the body take effect.
- The upper right sets `should_center=False` and `height=1.2`, so it only shows the scaled result without returning to the origin.

<video src="assets/RTM output/10-Typst-typst.mp4" controls width="560"></video>

> Note: Typst maths is wrapped in `$...$` (unlike LaTeX's `$`, which must be written in pairs inside the string), and things like colours defined with `#let` must go in `typst_preamble` or ahead of the body; when both `height` and `font_size` are given, `height` wins.

### `TypstMath`

```python
def __init__(self, math_expression: str, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `math_expression` | `str` | required | write the maths expression only (it is wrapped in `$ ... $` internally); the sample uses `sum_(i=1)^n i = (n(n+1))/2`, `mat(1, 2; 3, 4)` |
| `**kwargs` | `Any` | — | passed through to `Typst` (`font_size` / `color` / `stroke_width` …); the sample gives `color=ORANGE` |

#### Sample: sum / integral / matrix / square root

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Typst, TypstMath, MathTex, Text,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class TypstMathDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("10-TypstMath", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— default: write the expression directly (it is wrapped in $ ... $ automatically) ——
        m1 = TypstMath("sum_(i=1)^n i = (n(n+1))/2", font_size=44).move_to([0, 1.4, 0])   # the "math_expression" parameter
        win.play(Write(m1), FadeIn(cap("TypstMath(sum formula)", m1)), run_time=0.8)

        # —— the remaining parameters pass through to Typst: color / font_size ——
        m2 = TypstMath("integral_0^1 x^2 dif x = 1/3", font_size=44,
                       color=ORANGE).move_to([0, -0.4, 0])   # the "**kwargs (color)" parameter
        win.play(Write(m2), FadeIn(cap("color=ORANGE", m2)), run_time=0.8)

        # —— fractions / square roots / matrices ——
        m3 = TypstMath("mat(1, 2; 3, 4)", font_size=40).move_to([-3.4, -2.2, 0])
        m4 = TypstMath("sqrt(2) approx 1.414", font_size=40).move_to([2.6, -2.2, 0])
        win.play(Write(m3), FadeIn(cap("mat(1, 2; 3, 4)", m3)), run_time=0.7)
        win.play(Write(m4), FadeIn(cap("sqrt(2)", m4)), run_time=0.7)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: automatic routing —— MathTex goes through Typst under RTM =
```

What this code does:

- Above is the sum formula (the default size 44).
- In the middle is a definite integral with `color=ORANGE` (parameters passed through).
- On the lower row, `mat(1, 2; 3, 4)` on the left typesets a matrix and `sqrt(2) approx 1.414` on the right, showing Typst's maths-function syntax (`mat` / `sqrt` / `integral` / `approx`).

<video src="assets/RTM output/10-Typst-typstmath.mp4" controls width="560"></video>

> Note: Typst maths syntax differs from LaTeX (`sqrt(x)` rather than `\sqrt{x}`, fractions as `a/b`, matrices as `mat(...)`); inside `TypstMath` **do not** write `$` yourself, or you get two nested layers.

### Automatic routing: `MathTex` writing LaTeX as usual

```python
MathTex(r"\frac{a}{b} + \sqrt{x}")   # under RTM it is converted to Typst typesetting internally
```

| Item | Description |
| --- | --- |
| `MathTex` | written the same as LaTeX (`\frac`, `\sqrt`…), and RTM **converts it to Typst** internally, so no LaTeX installation is needed locally |
| Part interface | `MathTex`'s part colouring / fetching (`set_color_by_tex`, `get_part_by_tex`, etc.) works as usual; see [Part methods](09b-Substrings-and-Lists.md) |
| `TypstMath` counterpart | the same formula written in Typst syntax (`a/b + sqrt(x)`), with the same shape and position |

#### Sample: `MathTex` / `TypstMath` side by side on the same formula / part colouring

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Typst, TypstMath, MathTex, Text,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class AutoRouteDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("10-Typst autoroute", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— MathTex writes LaTeX as usual; RTM converts it to Typst typesetting internally (no local LaTeX needed) ——
        mt = MathTex(r"\frac{a}{b} + \sqrt{x}").move_to([0, 1.0, 0])   # the "MathTex (automatic routing)" parameter
        win.play(Write(mt), FadeIn(cap("MathTex(\\frac{a}{b}+\\sqrt{x})", mt)), run_time=0.8)

        # —— the same formula written with TypstMath, same shape and position ——
        tm = TypstMath("a/b + sqrt(x)", font_size=48).move_to([0, -0.6, 0])
        win.play(Write(tm), FadeIn(cap("TypstMath(a/b + sqrt(x))", tm)), run_time=0.8)

        # —— MathTex's part-colouring and other interfaces still work as usual ——
        mt2 = MathTex(r"E = mc^2").move_to([0, -2.2, 0])
        mt2[0].set_color(YELLOW)
        win.play(Write(mt2), FadeIn(cap("MathTex part colouring as usual", mt2)), run_time=0.8)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window
```

What this code does: above, `MathTex(r"\frac{a}{b} + \sqrt{x}")` writes LaTeX; below, `TypstMath("a/b + sqrt(x)")` writes the same expression, and the two typeset almost identically—so LaTeX syntax is converted to Typst under RTM; finally `MathTex(r"E = mc^2")` with `mt2[0].set_color(YELLOW)` colours a part, showing the part interface still works.

<video src="assets/RTM output/10-Typst-autoroute.mp4" controls width="560"></video>

> Note: automatic routing works for **common LaTeX commands**, but a very few macros (custom `\newcommand`, complex `tikz`-style ones) have no equivalent; when something will not typeset, switch to `TypstMath` and write Typst syntax directly.

---

See also: [LaTeX](09-LaTeX.md) · [Text](08-Text.md) · [Part methods](09b-Substrings-and-Lists.md)
