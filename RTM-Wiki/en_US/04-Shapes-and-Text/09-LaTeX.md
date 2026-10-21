# LaTeX

This section covers the three typesetting classes `Tex` / `MathTex` / `SingleStringMathTex`: mixing body text with formulas, pure formulas (with splittable parts), and the lightest single-string formula. Each class comes with one sample.

> **Both RTM and ManimCE go through LaTeX**: `Tex` / `MathTex` need a usable LaTeX distribution on the machine; if you do not want to install LaTeX, use [Typst](10-Typst.md) (`Typst` / `TypstMath`, or just write `MathTex` and let RTM route it automatically).
>
> **The first render waits for the compiler**: with a cold cache a LaTeX compile can stall for 1–2 seconds; with a visible window RTM pops up a small "compiling formula" notice (see [Live window MLWindow](../00-Getting-Started/03-Live-Window-MLWindow.md)); it is not a hang.

## Parameters

### `Tex`

```python
def __init__(self, *tex_strings: str, font_size: float = 48, color: ParsableManimColor | None = None, tex_environment: str = "document", **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*tex_strings` | `str...` | required | mixing body text with formulas; formulas go inside `$...$`, e.g. the sample's `r"The area is $A = \pi r^2$."` |
| `font_size` | `float` | `48` | font size; the sample uses 40 / 48 / 36 |
| `color` | `ManimColor \| None` | `None` | overall colour (body text and formulas change together); the sample uses `TEAL` |
| `tex_environment` | `str` | `"document"` | outer LaTeX environment; the sample switches it to `"align*"` (a maths environment) |

#### Sample: font size / colour / switching environment

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Tex, MathTex, SingleStringMathTex, Text,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class TexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("09-Tex", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— default: write formulas in $...$ inside body text; font_size controls the overall size ——
        t1 = Tex(r"The area is $A = \pi r^2$.", font_size=40).move_to([0, 1.5, 0])   # the "*tex_strings / font_size" parameters
        win.play(Write(t1), FadeIn(cap("Tex(...font_size=40)", t1)), run_time=0.7)

        # —— color: the overall colour (body text and formulas change together) ——
        t2 = Tex(r"$E = mc^2$", font_size=48, color=TEAL).move_to([0, 0.2, 0])   # the "color" parameter
        win.play(Write(t2), FadeIn(cap("color=TEAL", t2)), run_time=0.7)

        # —— tex_environment: switch to a maths environment (document by default) ——
        t3 = Tex(r"a + b = c", font_size=36,
                 tex_environment="align*").move_to([0, -1.4, 0])   # the "tex_environment" parameter
        win.play(Write(t3), FadeIn(cap('tex_environment="align*"', t3)), run_time=0.7)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: MathTex —— pure formulas with splittable parts ===========
```

What this code does:

- The first is mixed body text (`$A = \pi r^2$` is an inline formula, font size 40).
- The second holds just one formula, coloured `TEAL` as a whole.
- The third switches `tex_environment` to `"align*"` to see how the same content lays out in a maths environment.

<video src="assets/RTM output/09-LaTeX-tex.mp4" controls width="560"></video>

> Note: under `tex_environment="document"` **do not** use `\\` to break lines manually (it fails to compile, consistent across both engines in testing); to get a line break, split into several `Tex` objects or switch to an environment such as `align*`/`gather*`.

### `MathTex`

```python
def __init__(self, *tex_strings: str, font_size: float = 48, color: ParsableManimColor | None = None, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*tex_strings` | `str...` | required | each positional argument is one part; `{{ }}` then splits one part into several (see [Part methods](09b-Substrings-and-Lists.md)) |
| `font_size` | `float` | `48` | font size; the sample uses 48 / 44 |
| `color` | `ManimColor \| None` | `None` | overall colour; the sample uses `ORANGE` |

#### Sample: a whole formula string / colouring explicit parts / overall style

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Tex, MathTex, SingleStringMathTex, Text,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class MathTexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("09-MathTex", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— default: each positional argument is one part; a single string may contain several $...$ ——
        m1 = MathTex(r"x^2 + y^2 = z^2", font_size=48).move_to([0, 1.4, 0])   # the "*tex_strings" parameter
        win.play(Write(m1), FadeIn(cap("MathTex(r\"x^2 + y^2 = z^2\")", m1)), run_time=0.8)

        # —— explicit parts: each part is its own unit, handy for colouring one later ——
        m2 = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2", font_size=48).move_to([0, 0.0, 0])   # the "{{ }}" part splitting
        m2[0].set_color(RED)
        m2[2].set_color(GREEN)
        m2[4].set_color(BLUE)
        win.play(Write(m2), FadeIn(cap("each part coloured separately", m2)), run_time=0.8)

        # —— color / font_size: the overall style ——
        m3 = MathTex(r"\int_0^1 x^2\,dx = \frac{1}{3}", font_size=44,
                     color=ORANGE).move_to([0, -1.6, 0])   # the "color / font_size" parameters
        win.play(Write(m3), FadeIn(cap("color=ORANGE, font_size=44", m3)), run_time=0.8)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: SingleStringMathTex —— a single formula string ===========
```

What this code does: the first writes a whole formula string directly; the second uses `{{ }}` to split `x^2+y^2=z^2` into five parts and colours the `x`/`y`/`z` parts red, green and blue; the third is a definite integral, given `color=ORANGE` and font size 44.

<video src="assets/RTM output/09-LaTeX-mathtex.mp4" controls width="560"></video>

> Note: inside `MathTex` you do not write `$` again (it is in maths mode already); to fetch by part, split explicitly, because `{{ }}` inside a single string only splits out the first part (consistent across both engines in testing).

### `SingleStringMathTex`

```python
def __init__(self, tex_string: str, font_size: float = 48, color: ParsableManimColor | None = None, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `tex_string` | `str` | required | takes **one** string only and does not split parts; it is the glyph leaf of `Text` / `MathTex` |
| `font_size` | `float` | `48` | font size; the sample uses 44 / 64 |
| `color` | `ManimColor \| None` | `None` | overall colour; the sample uses `TEAL` |

#### Sample: a sum / colouring the whole string / enlarging the font size

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Tex, MathTex, SingleStringMathTex, Text,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class SingleStringDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("09-SingleStringMathTex", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— takes a single string only: no part splitting, the lightest formula object ——
        s1 = SingleStringMathTex(r"\sum_{i=1}^{n} i = \frac{n(n+1)}{2}",
                                 font_size=44).move_to([0, 1.2, 0])   # the "tex_string" parameter
        win.play(Write(s1), FadeIn(cap("SingleStringMathTex(sum)", s1)), run_time=0.8)

        # —— difference from MathTex: it has a single part, so you cannot fetch by part ——
        s2 = SingleStringMathTex(r"[a, b] = [c, d]", font_size=44,
                                 color=TEAL).move_to([0, -0.4, 0])
        win.play(Write(s2), FadeIn(cap("one object for the whole string (color=TEAL)", s2)), run_time=0.8)

        # —— change font_size once more to see the scaling ——
        s3 = SingleStringMathTex(r"f(x) = e^{-x^2}", font_size=64).move_to([0, -2.2, 0])
        win.play(Write(s3), FadeIn(cap("font_size=64", s3)), run_time=0.8)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window
```

What this code does:

- The first is a sum formula (size 44).
- The second colours the whole string `TEAL`.
- The third raises `font_size` to 64 to see proportional scaling—all three are a single part with no sub-parts to split.

<video src="assets/RTM output/09-LaTeX-singlestring.mp4" controls width="560"></video>

> Note: `SingleStringMathTex` is the lightest of the three (a single layer of glyph leaves) and suits cases where a formula only needs to be displayed, not split into parts; to colour by term, use `MathTex` and split explicitly.

---

See also: [Substrings and lists](09b-Substrings-and-Lists.md) · [Typst](10-Typst.md) · [Text](08-Text.md)
