# Matrices

Renders a 2D list as a matrix with brackets (`mobject/matrix.py`): the brackets are rendered with LaTeX and the elements with `MathTex` by default. One sample per function, and the `Matrix` sample cycles through **all of its constructor parameters**.

> **`font_size` is not a matrix parameter**: `Matrix(..., font_size=40)` raises `TypeError: Mobject.__init__() got an unexpected keyword argument 'font_size'` (`**kwargs` ultimately reaches `Mobject.__init__`).
> To adjust the element font size, use `element_to_mobject_config={"font_size": …}`.
> When the elements are **numbers**, do not swap `element_to_mobject` for `Text`/`MathTex` (they want strings, and `Text(1.2)` raises `AttributeError: 'int' object has no attribute 'find'`); use `DecimalNumber`/`Integer` for numeric elements.

## Parameters

### `Matrix`

```python
def __init__(self, matrix: Iterable[Iterable[Any] | Vector2DLike], v_buff: float = 0.8, h_buff: float = 1.3, bracket_h_buff: float = MED_SMALL_BUFF, bracket_v_buff: float = MED_SMALL_BUFF, add_background_rectangles_to_entries: bool = False, include_background_rectangle: bool = False, element_to_mobject: type[VMobject] | Callable[..., VMobject] = MathTex, element_to_mobject_config: dict = {}, element_alignment_corner: Vector3DLike = DR, left_bracket: str = "[", right_bracket: str = "]", stretch_brackets: bool = True, bracket_config: dict = {}, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `matrix` | `list \| np.ndarray` | required | 2D data; the elements are given as strings (rendered with `MathTex` by default) or numbers |
| `v_buff` | `float` | `0.8` | row spacing; the sample's `1.6` pulls them apart for comparison |
| `h_buff` | `float` | `1.3` | column spacing; the sample uses `2.6` |
| `bracket_h_buff` | `float` | `MED_SMALL_BUFF` (0.25) | **horizontal** spacing between the brackets and the content; the sample uses `0.8` |
| `bracket_v_buff` | `float` | `MED_SMALL_BUFF` | **vertical** spacing between the brackets and the content; the sample uses `0.7` |
| `add_background_rectangles_to_entries` | `bool` | `False` | pad **every element** with a background block |
| `include_background_rectangle` | `bool` | `False` | pad the **whole matrix** with a background |
| `element_to_mobject` | `class`/`callable` | `MathTex` | element rendering class; when the matrix elements are **numbers** use a class that accepts numbers (`DecimalNumber`/`Integer`) |
| `element_to_mobject_config` | `dict` | `{}` | the config passed to the element rendering class (e.g. `{"font_size": 40}`) |
| `element_alignment_corner` | `array-like` | `DR` | the alignment corner of an element inside its cell; the sample compares `UL` against the default `DR` |
| `left_bracket` | `str` | `"["` | left bracket shape; the sample switches it to `"("` and `r"\langle"` |
| `right_bracket` | `str` | `"]"` | right bracket shape; paired with `r"\rangle"` |
| `stretch_brackets` | `bool` | `True` | whether the brackets stretch with the matrix height; with `False` a tall, thin matrix's brackets no longer grow |
| `bracket_config` | `dict` | `{}` | bracket style config; the sample uses `{"color": ORANGE}` |

Methods: `get_rows()` / `get_columns()` / `get_entries()` / `get_brackets()` / `get_mob_matrix()` return the corresponding structures; `set_row_colors(*colors)` / `set_column_colors(*colors)` colour by row/column; `add_background_to_entries()` adds a background to each cell afterwards.

#### Sample: cycling through the twelve constructor parameters + three methods

```python
import os
import subprocess
import sys
import numpy as np
from real_time_manim import (
    Scene, Matrix, DecimalMatrix, IntegerMatrix, MobjectMatrix, Integer,
    get_det_text, matrix_to_tex_string, matrix_to_mobject, DecimalNumber,
    Text, Circle, Square, Triangle, Dot, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, DR, UL, MED_SMALL_BUFF,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class MatrixDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("13-Matrix", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        stage = VGroup()   # the previous step's matrix + caption: fade out before the next step so nothing overlaps
        def show(mob, cap, t=0.55):
            nonlocal stage
            grp = VGroup(mob, Text(cap, font_size=18, color=GREY_B).next_to(mob, DOWN, buff=0.35))
            if len(stage):
                win.play(FadeOut(stage), run_time=0.2)
            win.play(Write(mob), run_time=t)
            win.play(FadeIn(grp[1]), run_time=0.25)
            stage = grp

        # —— default parameters: a 2x2 integer matrix ——
        show(Matrix([[1, 2], [3, 4]], element_to_mobject_config={"font_size": 40}), "Matrix([[1,2],[3,4]])")

        # —— v_buff / h_buff: row and column spacing ——
        show(Matrix([[1, 2], [3, 4]], v_buff=1.6, h_buff=2.6, element_to_mobject_config={"font_size": 40}),
             "v_buff=1.6  h_buff=2.6")

        # —— bracket_h_buff / bracket_v_buff: spacing between the brackets and the content ——
        show(Matrix([[1, 2], [3, 4]], bracket_h_buff=0.8, bracket_v_buff=0.7, element_to_mobject_config={"font_size": 40}),
             "bracket_h_buff=0.8  bracket_v_buff=0.7")

        # —— left_bracket / right_bracket: swap the bracket shapes ——
        show(Matrix([[1, 2], [3, 4]], left_bracket="(", right_bracket=")", element_to_mobject_config={"font_size": 40}),
             'left_bracket="("  right_bracket=")"')
        show(Matrix([[1, 2], [3, 4]], left_bracket=r"\langle", right_bracket=r"\rangle", element_to_mobject_config={"font_size": 40}),
             'left_bracket=r"\\langle"  right_bracket=r"\\rangle"')

        # —— stretch_brackets=False: the brackets no longer stretch with the height (obvious on a tall, thin matrix) ——
        show(Matrix([[1], [2], [3], [4]], stretch_brackets=False, element_to_mobject_config={"font_size": 34}),
             "stretch_brackets=False")

        # —— add_background_rectangles_to_entries / include_background_rectangle ——
        show(Matrix([[1, 2], [3, 4]], add_background_rectangles_to_entries=True, element_to_mobject_config={"font_size": 40}),
             "add_background_rectangles_to_entries=True")
        show(Matrix([[1, 2], [3, 4]], include_background_rectangle=True, element_to_mobject_config={"font_size": 40}),
             "include_background_rectangle=True")

        # —— element_to_mobject / element_to_mobject_config: swap the element rendering class ——
        show(Matrix([["a", "b"], ["c", "d"]], element_to_mobject=Text,
                    element_to_mobject_config={"font_size": 36}),
             'element_to_mobject=Text  config={"font_size": 36}')

        # —— element_alignment_corner: swap the alignment corner inside the cell (visible when elements differ in size) ——
        show(Matrix([[1.2345, 2], [3, 4]], element_alignment_corner=UL, element_to_mobject_config={"font_size": 36}),
             "element_alignment_corner=UL")
        show(Matrix([[1.2345, 2], [3, 4]], element_alignment_corner=DR, element_to_mobject_config={"font_size": 36}),
             "element_alignment_corner=DR (default)")

        # —— bracket_config: change only the bracket style ——
        show(Matrix([[1, 2], [3, 4]], bracket_config={"color": ORANGE}, element_to_mobject_config={"font_size": 40}),
             'bracket_config={"color": ORANGE}')

        # —— methods: set_column_colors / set_row_colors / add_background_to_entries / get_* ——
        win.play(FadeOut(stage), run_time=0.25)   # clear the previous step's comparison first
        m = Matrix([[1, 2], [3, 4]], element_to_mobject_config={"font_size": 40})
        m2 = m.copy()
        win.play(Write(m), run_time=0.5)
        m.set_column_colors(RED, BLUE)   # the "set_column_colors(*colors)" method
        win.play(Write(m), run_time=0.3)
        win.play(FadeOut(m), run_time=0.25)
        m2.set_row_colors(GREEN, PURPLE)   # the "set_row_colors(*colors)" method
        m2.add_background_to_entries()   # the "add_background_to_entries()" method
        win.play(Write(m2), run_time=0.5)   # row colours + a per-cell background block
        info = Text("entries=%d rows=%d cols=%d brackets=%d" % (
            len(m2.get_entries()), len(m2.get_rows()), len(m2.get_columns()),
            len(m2.get_brackets())), font_size=20, color=GREY_B).next_to(m2, DOWN, buff=0.4)
        win.play(FadeIn(info), run_time=0.3)   # the "get_entries / get_rows / get_columns / get_brackets" methods
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: DecimalMatrix —— a decimal matrix ========================
```

What this code does: it reworks the same 2×2 matrix one section at a time.

- First the default look, then one at a time: `v_buff`/`h_buff`, `bracket_h_buff`/`bracket_v_buff`, `left_bracket`/`right_bracket` (round brackets, angle brackets), `stretch_brackets`, the two kinds of background block, `element_to_mobject`, `element_alignment_corner` and `bracket_config`; each section has a line of parameter caption below it.
- The last section demonstrates the methods: `set_column_colors` colours by column, `set_row_colors` colours by row, `add_background_to_entries()` adds a background afterwards, and then the lengths of `get_entries/get_rows/get_columns/get_brackets` are printed as one line of readings.

<video src="assets/RTM output/13-Matrices-matrix.mp4" controls width="560"></video>

> Note: `**kwargs` falls all the way through to `Mobject.__init__`, so a key like `font_size`, which "looks like it should exist", actually raises `TypeError`. The brackets are drawn by LaTeX — `stretch_brackets=False` only stops the stretching, the shape still goes through LaTeX — so the bracket style can also be coloured with `bracket_config`.

### `DecimalMatrix`

```python
def __init__(self, matrix: Iterable[Iterable[Any]], element_to_mobject: type[VMobject] | Callable[..., VMobject] = DecimalNumber, element_to_mobject_config: dict = {"num_decimal_places": 1}, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `matrix` | `list \| np.ndarray` | required | numeric data (floats) |
| `element_to_mobject` | `class`/`callable` | `DecimalNumber` | element rendering class. You **can** put `DecimalNumber` (the default) or another class that accepts numbers (such as `Integer`); do not put `Text`/`MathTex` — `Text(1.2)` raises `AttributeError` |
| `element_to_mobject_config` | `dict` | `{"num_decimal_places": 1}` | element config; the sample does 1 / 3 / 0 decimal places once each |

#### Sample: 1 place / 3 places / 0 places + switching to `Integer` rendering

```python
import os
import subprocess
import sys
import numpy as np
from real_time_manim import (
    Scene, Matrix, DecimalMatrix, IntegerMatrix, MobjectMatrix, Integer,
    get_det_text, matrix_to_tex_string, matrix_to_mobject, DecimalNumber,
    Text, Circle, Square, Triangle, Dot, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, DR, UL, MED_SMALL_BUFF,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class DecimalMatrixDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("13-DecimalMatrix", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— default: element_to_mobject=DecimalNumber, num_decimal_places=1 in the config ——
        d1 = DecimalMatrix([[1.2, 3.4], [5.6, 7.8]], element_to_mobject_config={"num_decimal_places": 1, "font_size": 40}).move_to(LEFT * 2.6 + UP * 0.6)
        cap1 = Text("DecimalMatrix([[...]])", font_size=18, color=GREY_B).next_to(d1, DOWN, buff=0.35)
        win.play(Write(d1), FadeIn(cap1), run_time=0.6)   # default 1 decimal place

        # —— element_to_mobject_config: change to 3 decimal places ——
        d2 = DecimalMatrix([[1.2345, 3.4567], [5.6789, 7.891]],
                           element_to_mobject_config={"num_decimal_places": 3, "font_size": 40}).move_to(RIGHT * 2.6 + UP * 0.6)
        cap2 = Text("num_decimal_places=3", font_size=18, color=GREY_B).next_to(d2, DOWN, buff=0.35)
        win.play(Write(d2), FadeIn(cap2), run_time=0.6)   # keep 3 places

        # —— element_to_mobject_config: 0 decimal places = rounded display ——
        d3 = DecimalMatrix([[1.2, 3.4], [5.6, 7.8]],
                           element_to_mobject_config={"num_decimal_places": 0, "font_size": 40}).move_to(DOWN * 1.8)
        cap3 = Text("num_decimal_places=0", font_size=18, color=GREY_B).next_to(d3, DOWN, buff=0.35)
        win.play(Write(d3), FadeIn(cap3), run_time=0.6)   # 0 places = rounded display

        # —— element_to_mobject: swap the whole class (switch to Integer rendering, elements become integers) ——
        # do not swap in Text/MathTex: they want strings, while DecimalMatrix's elements are floats,
        # so Text(1.2) raises AttributeError straight away (measured).
        d4 = DecimalMatrix([[1.2, 3.4], [5.6, 7.8]], element_to_mobject=Integer,
                           element_to_mobject_config={"font_size": 40}).move_to(DOWN * 1.8)
        win.play(FadeOut(d3), FadeOut(cap3), run_time=0.25)
        cap4 = Text("element_to_mobject=Integer", font_size=18, color=GREY_B).next_to(d4, DOWN, buff=0.35)
        win.play(Write(d4), FadeIn(cap4), run_time=0.6)   # switch to Integer rendering (wipes out the decimals)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: IntegerMatrix —— an integer matrix =======================
```

What this code does: the three decimal matrices differ only in `num_decimal_places` inside `element_to_mobject_config` — 1 place (the default), 3 places (keeping more decimals) and 0 places (rounded display). The 0-place one is placed at the same spot as the last `element_to_mobject=Integer` one, showing that the two render identically.

<video src="assets/RTM output/13-Matrices-decimal.mp4" controls width="560"></video>

> Note: `element_to_mobject_config` is a **whole replacement**, not merged with the defaults, so when changing the number of places it is safest to write `font_size` in as well (which is what the sample does).

### `IntegerMatrix`

```python
def __init__(self, matrix: Iterable[Iterable[Any]], element_to_mobject: type[VMobject] | Callable[..., VMobject] = Integer, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `matrix` | `list \| np.ndarray` | required | numeric data |
| `element_to_mobject` | `class`/`callable` | `Integer` | element rendering class; the sample switches it to `DecimalNumber` so the elements are typeset as decimals (`Text`/`MathTex` raise on numeric elements) |
| Others | — | — | the same as `Matrix` (the sample uses `v_buff` / `h_buff`) |

#### Sample: default / switching to `DecimalNumber` / row and column spacing

```python
import os
import subprocess
import sys
import numpy as np
from real_time_manim import (
    Scene, Matrix, DecimalMatrix, IntegerMatrix, MobjectMatrix, Integer,
    get_det_text, matrix_to_tex_string, matrix_to_mobject, DecimalNumber,
    Text, Circle, Square, Triangle, Dot, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, DR, UL, MED_SMALL_BUFF,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class IntegerMatrixDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("13-IntegerMatrix", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— default: element_to_mobject=Integer ——
        i1 = IntegerMatrix([[1, 2], [3, 4]], element_to_mobject_config={"font_size": 40}).move_to(LEFT * 2.6 + UP * 0.6)
        cap1 = Text("IntegerMatrix([[...]])", font_size=18, color=GREY_B).next_to(i1, DOWN, buff=0.35)
        win.play(Write(i1), FadeIn(cap1), run_time=0.6)

        # —— element_to_mobject: switch to DecimalNumber rendering (elements typeset as decimals) ——
        # do not swap in Text/MathTex: they want strings, while the matrix elements are numbers, so Text(1)
        # raises AttributeError (measured identically on both engines).
        i2 = IntegerMatrix([[1.5, 2.5], [3.5, 4.5]], element_to_mobject=DecimalNumber,
                           element_to_mobject_config={"num_decimal_places": 1, "font_size": 40}
                           ).move_to(RIGHT * 2.6 + UP * 0.6)
        cap2 = Text("element_to_mobject=DecimalNumber", font_size=18, color=GREY_B).next_to(i2, DOWN, buff=0.35)
        win.play(Write(i2), FadeIn(cap2), run_time=0.6)

        # —— the remaining parameters are the same as Matrix: v_buff / h_buff also work ——
        i3 = IntegerMatrix([[1, 2, 3], [4, 5, 6]], v_buff=1.4, h_buff=2.2,
                           element_to_mobject_config={"font_size": 40}).move_to(DOWN * 1.9)
        cap3 = Text("v_buff=1.4  h_buff=2.2", font_size=18, color=GREY_B).next_to(i3, DOWN, buff=0.35)
        win.play(Write(i3), FadeIn(cap3), run_time=0.6)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 4: MobjectMatrix —— the elements are arbitrary Mobjects =====
```

What this code does: the left is the default (integer rendering) and the right swaps `element_to_mobject` for `DecimalNumber` with `num_decimal_places=1`, so the elements gain decimal points; the third 2×3 matrix changes `v_buff`/`h_buff`, proving that the remaining parameters are fully shared with `Matrix`.

<video src="assets/RTM output/13-Matrices-integer.mp4" controls width="560"></video>

> Note: `IntegerMatrix`'s default rendering class is `Integer` (the most natural choice for integer elements); to show decimals, do not use `IntegerMatrix`, use `DecimalMatrix` directly.

### `MobjectMatrix`

```python
def __init__(self, matrix: Iterable[Iterable[Any]], element_to_mobject: type[VMobject] | Callable[..., VMobject] = <identity>, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `matrix` | `list[list[Mobject]]` | required | each cell is a **ready-made Mobject** (`Circle`/`Square`/`Dot`…) |
| `element_to_mobject` | `callable` | the identity function (`lambda m: m`) | element conversion function; the sample gives `lambda m: m.copy().scale(0.5)` to shrink everything by half |
| Others | — | — | the same as `Matrix` (the sample uses `v_buff` / `h_buff`) |

#### Sample: placing ready-made objects / shrinking with a conversion function

```python
import os
import subprocess
import sys
import numpy as np
from real_time_manim import (
    Scene, Matrix, DecimalMatrix, IntegerMatrix, MobjectMatrix, Integer,
    get_det_text, matrix_to_tex_string, matrix_to_mobject, DecimalNumber,
    Text, Circle, Square, Triangle, Dot, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, DR, UL, MED_SMALL_BUFF,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class MobjectMatrixDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("13-MobjectMatrix", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— the default element_to_mobject is the identity function: place ready-made objects directly ——
        circles = MobjectMatrix([[Circle(radius=0.3, color=TEAL), Square(side_length=0.6, color=GREEN)],
                                 [Triangle(color=ORANGE).scale(0.4), Dot(radius=0.16, color=RED)]],
                                v_buff=1.0, h_buff=1.6).move_to(UP * 0.8)
        cap1 = Text("MobjectMatrix([[Circle, Square], [Triangle, Dot]])",
                    font_size=18, color=GREY_B).next_to(circles, DOWN, buff=0.35)
        win.play(Create(circles), FadeIn(cap1), run_time=0.9)

        # —— element_to_mobject: give it a conversion function (here it shrinks everything by half) ——
        shrunk = MobjectMatrix([[Circle(radius=0.6, color=BLUE), Square(side_length=1.2, color=GOLD)],
                                [Triangle(color=PURPLE).scale(0.8), Dot(radius=0.3, color=YELLOW)]],
                               element_to_mobject=lambda m: m.copy().scale(0.5),   # the "element_to_mobject" parameter
                               v_buff=1.0, h_buff=1.6).move_to(DOWN * 2.2)
        cap2 = Text("element_to_mobject=lambda m: m.copy().scale(0.5)",
                    font_size=18, color=GREY_B).next_to(shrunk, DOWN, buff=0.3)
        win.play(Create(shrunk), FadeIn(cap2), run_time=0.9)
        win.play(Wait(0.5))   # hold to compare the two groups
        win.close()   # close the RTM window


# ===== Sample 5: get_det_text —— a determinant title ======================
```

What this code does: the upper group places four ready-made objects straight in as matrix elements, passing nothing but the spacing. The lower group's elements are made larger first and then handed to `element_to_mobject=lambda m: m.copy().scale(0.5)`; on screen the two groups are the same size — showing that this parameter is "the conversion function for each cell's object", and can be used to scale, recolour or copy uniformly.

<video src="assets/RTM output/13-Matrices-mobject.mp4" controls width="560"></video>

> Note: inside the conversion function, call `m.copy()` before modifying; modifying the object passed in directly also changes the one the caller is holding.

### `get_det_text`

```python
def get_det_text(matrix: Matrix, determinant: int | str | None = None, background_rect: bool = False, initial_scale_factor: float = 2) -> VGroup:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `matrix` | `Matrix` | required | an already-constructed matrix object (used to read the sign and the size) |
| `determinant` | `int \| str \| None` | `None` | the determinant value; with `None` it only writes `det(...)`, and if given it writes `det(A) = value` |
| `background_rect` | `bool` | `False` | whether to pad this text with a background rectangle |
| `initial_scale_factor` | `float` | `2` | initial scale (the sample compares 1.0 / 1.4) |

#### Sample: just det / with a value / background and enlarged

```python
import os
import subprocess
import sys
import numpy as np
from real_time_manim import (
    Scene, Matrix, DecimalMatrix, IntegerMatrix, MobjectMatrix, Integer,
    get_det_text, matrix_to_tex_string, matrix_to_mobject, DecimalNumber,
    Text, Circle, Square, Triangle, Dot, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, DR, UL, MED_SMALL_BUFF,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class DetTextDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("13-get_det_text", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        m = Matrix([[1, 2], [3, 4]], element_to_mobject_config={"font_size": 40})
        win.play(Write(m), run_time=0.5)   # place the matrix first

        # —— determinant=None: only writes det(...) ——
        d0 = get_det_text(m, initial_scale_factor=1.0).next_to(m, DOWN, buff=0.5)   # the "matrix / initial_scale_factor" parameters
        win.play(FadeIn(d0), run_time=0.4)

        # —— determinant given a value: writes det(A) = value ——
        d1 = get_det_text(m, determinant=-2, initial_scale_factor=1.0).next_to(m, DOWN, buff=0.5)   # the "determinant" parameter
        win.play(FadeOut(d0), FadeIn(d1), run_time=0.4)

        # —— background_rect=True: pads this text with a black background ——
        d2 = get_det_text(m, determinant=-2, background_rect=True,
                          initial_scale_factor=1.4).next_to(m, DOWN, buff=0.5)   # the "background_rect / initial_scale_factor" parameters
        win.play(FadeOut(d1), FadeIn(d2), run_time=0.5)   # larger text with a background
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 6: matrix_to_tex_string —— converting to a LaTeX string =====
```

What this code does: after placing a 2×2 matrix, `get_det_text` is called three times — the first passes no `determinant` (only `det(...)`), the second gives `-2` (writing `det(A) = -2`), and the third gives both `background_rect=True` and a larger `initial_scale_factor`, so the text gets a background and a larger font size.

<video src="assets/RTM output/13-Matrices-dettext.mp4" controls width="560"></video>

> Note: it returns a `VGroup` (the text + an optional background block), so it can be positioned directly with `next_to(matrix, DOWN)` and can also take `FadeIn`/`Transform` as a whole.

### `matrix_to_tex_string`

```python
def matrix_to_tex_string(matrix: np.ndarray) -> str:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `matrix` | `list \| np.ndarray` | required | 2D data; returns a **bracket-free** bare-array LaTeX string |

#### Sample: converting two array sizes to strings and printing them on screen

```python
import os
import subprocess
import sys
import numpy as np
from real_time_manim import (
    Scene, Matrix, DecimalMatrix, IntegerMatrix, MobjectMatrix, Integer,
    get_det_text, matrix_to_tex_string, matrix_to_mobject, DecimalNumber,
    Text, Circle, Square, Triangle, Dot, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, DR, UL, MED_SMALL_BUFF,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class TexStringDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("13-matrix_to_tex_string", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— only one parameter: the 2D data; returns a str (a bare array, no brackets) ——
        for i, data in enumerate([np.array([[1, 2], [3, 4]]),
                                  np.array([[1, 2, 3], [4, 5, 6]])]):
            s = matrix_to_tex_string(data)   # the "matrix" parameter
            lbl = Text(s.replace(" ", ""), font_size=20, color=TEAL).move_to([0, 0.9 - i * 1.8, 0])
            cap = Text("matrix_to_tex_string(%d x %d)" % data.shape,
                       font_size=18, color=GREY_B).next_to(lbl, DOWN, buff=0.25)
            win.play(FadeIn(lbl), FadeIn(cap), run_time=0.5)   # print the string straight onto the screen
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 7: matrix_to_mobject —— converting to a MathTex object ======
```

What this code does: the 2×2 and 2×3 arrays are each converted into a LaTeX string, and the string itself is printed straight onto the screen (the caption labels the array size) — this is the low-level function to reach for when you "want to assemble LaTeX yourself", beyond `MathTex(..., tex_to_color_map=...)`.

<video src="assets/RTM output/13-Matrices-texstr.mp4" controls width="560"></video>

> Note: the returned string has **no brackets** (it is not a matrix object); if you want brackets, write `\left[` / `\right]` yourself, or just use `Matrix`.

### `matrix_to_mobject`

```python
def matrix_to_mobject(matrix: np.ndarray) -> MathTex:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `matrix` | `list \| np.ndarray` | required | 2D data; returns a `MathTex` that can go straight on screen (again without brackets) |

#### Sample: converting an integer array and a decimal array to objects

```python
import os
import subprocess
import sys
import numpy as np
from real_time_manim import (
    Scene, Matrix, DecimalMatrix, IntegerMatrix, MobjectMatrix, Integer,
    get_det_text, matrix_to_tex_string, matrix_to_mobject, DecimalNumber,
    Text, Circle, Square, Triangle, Dot, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, DR, UL, MED_SMALL_BUFF,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class TexMobjectDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("13-matrix_to_mobject", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— again the only parameter is the 2D data; returns a MathTex that can go straight on screen / take animation ——
        mob = matrix_to_mobject(np.array([[1, 2], [3, 4]]))   # the "matrix" parameter
        cap = Text("matrix_to_mobject(np.array([[1,2],[3,4]]))",
                   font_size=18, color=GREY_B).next_to(mob, DOWN, buff=0.4)
        win.play(Write(mob), FadeIn(cap), run_time=0.7)   # bare-array typesetting (no brackets)

        mob2 = matrix_to_mobject(np.array([[1.5, 2.5], [3.5, 4.5]])).next_to(mob, DOWN, buff=1.2)
        cap2 = Text("matrix_to_mobject(2 x 2 floats)", font_size=18, color=GREY_B).next_to(mob2, DOWN, buff=0.4)
        win.play(Write(mob2), FadeIn(cap2), run_time=0.7)   # decimals typeset too
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window
```

What this code does: two arrays each become a `MathTex` object and are `Write`n out — the integer one displays as-is and the decimal one is typeset by LaTeX; because they are ordinary `MathTex`, you can keep going with `set_color_by_tex`, `Transform`, and so on.

<video src="assets/RTM output/13-Matrices-texmob.mp4" controls width="560"></video>

> Note: the only difference from `matrix_to_tex_string` is whether it gives you a string or a ready-made object; neither comes with brackets, so use `Matrix` if you want brackets.

---

See also: [LaTeX](09-LaTeX.md) · [Numbers and variables](12-Numbers-and-Variables.md) · [Tables](14-Tables.md)
