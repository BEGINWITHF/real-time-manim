# Table methods

The four instance methods of [Tables](14-Tables.md): adding a highlight block to a cell, taking a cell out, getting an "already highlighted" background block, and the table's own arranged entrance animation. One sample per method.

> **The position `pos` is `(row, column)`, 1-based**: `(1, 1)` is the top-left cell — unlike Python indexing (which starts at 0), all four methods use this same coordinate system.

## Parameters

### `Table.add_highlighted_cell`

```python
def add_highlighted_cell(self, pos: Sequence[int] = (1, 1), color: ParsableManimColor = YELLOW, **kwargs) -> Self:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `pos` | `Sequence[int]` | `(1, 1)` | the cell position `(row, column)`, 1-based; the sample adds one at `(1, 2)` and one at `(2, 1)` |
| `color` | `ManimColor` | `YELLOW` | highlight block colour; the sample uses `YELLOW` / `BLUE` |
| `**kwargs` | `Any` | — | passed on to the background block (`BackgroundRectangle`); the sample uses `fill_opacity=0.4` |

Adds a **background highlight** to the table in place and returns the table itself (so it can be chained); the highlight block then transforms along with the table.

#### Sample: two cells, two colours, adding `fill_opacity`

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Table, Text, Rectangle, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class HighlightDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("14b-add_highlighted_cell", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        t = Table([["a", "b"], ["c", "d"]], include_outer_lines=True,
                  element_to_mobject=Text, element_to_mobject_config={"font_size": 34})
        t.scale(0.9).move_to([0, 0.6, 0])
        win.play(Write(t), FadeIn(cap("Table([[a,b],[c,d]])", t)), run_time=0.7)

        # —— pos locates with (row, column) (1-based), color is the highlight block's colour ——
        t.add_highlighted_cell((1, 2), color=YELLOW)   # the "pos / color" parameters
        win.play(Write(t), run_time=0.5)
        c1 = Text("add_highlighted_cell((1, 2), YELLOW)",
                  font_size=18, color=GREY_B).move_to([0, -1.5, 0])
        win.play(FadeIn(c1), run_time=0.4)

        # —— **kwargs is passed on to the background block (e.g. fill_opacity) ——
        t.add_highlighted_cell((2, 1), color=BLUE, fill_opacity=0.4)   # the "**kwargs" parameter
        win.play(Write(t), run_time=0.5)
        newc = Text("add_highlighted_cell((2, 1), BLUE, fill_opacity=0.4)",
                    font_size=18, color=GREY_B).move_to([0, -2.1, 0])
        win.play(FadeIn(newc), run_time=0.4)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: get_cell / get_highlighted_cell —— taking a cell out =====
```

What this code does: it places a 2×2 table first, then `add_highlighted_cell((1, 2), color=YELLOW)` highlights the top-right cell. Then `add_highlighted_cell((2, 1), color=BLUE, fill_opacity=0.4)` highlights the bottom-left cell and makes it semi-transparent — `**kwargs` lands straight on the background block.

<video src="assets/RTM output/14b-Table-Methods-highlight.mp4" controls width="560"></video>

> Note: the highlight block is a **subobject of the table**, so a later `scale`/`shift`/`set_row_colors` on the table moves it along; calling it repeatedly on the same cell stacks a new background block (it does not replace the old one).

### `Table.get_cell`

```python
def get_cell(self, pos: Sequence[int] = (1, 1), **kwargs) -> Polygon:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `pos` | `Sequence[int]` | `(1, 1)` | the cell position `(row, column)`, 1-based; the sample uses `(1, 2)` |
| `**kwargs` | `Any` | — | passed to the returned `Polygon` (e.g. `color=`, `fill_opacity=`) |

Returns the cell's **polygon** (`Polygon`), which can be coloured or animated on its own — good for "highlighting just this cell's border/fill".

#### Sample: taking a cell out and colouring it on its own

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Table, Text, Rectangle, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class GetCellDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("14b-get_cell / get_highlighted_cell", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        t = Table([["1", "2"], ["3", "4"]], include_outer_lines=True,
                  element_to_mobject=Text, element_to_mobject_config={"font_size": 34})
        t.scale(0.9).move_to([0, 0.6, 0])
        win.play(Write(t), FadeIn(cap("Table([[1,2],[3,4]])", t)), run_time=0.7)

        # —— get_cell: get the cell polygon and change its style on its own ——
        cell = t.get_cell((1, 2))   # the "pos" parameter
        win.play(cell.animate.set_fill(RED, 0.45), run_time=0.6)
        c1 = Text("get_cell((1, 2)) -> Polygon",
                  font_size=18, color=GREY_B).move_to([0, -1.5, 0])
        win.play(FadeIn(c1), run_time=0.4)

        # —— get_highlighted_cell: get the "already highlighted" background block directly ——
        hl = t.get_highlighted_cell((2, 2), color=TEAL)   # the "pos / color" parameters
        win.play(FadeIn(hl), run_time=0.5)
        newc = Text("get_highlighted_cell((2, 2), TEAL)",
                    font_size=18, color=GREY_B).move_to([0, -2.1, 0])
        win.play(FadeIn(newc), run_time=0.4)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: create —— the table's arranged entrance animation ========
```

What this code does: it builds a 2×2 table, `cell = t.get_cell((1, 2))` takes out the top-right cell's polygon, and `cell.animate.set_fill(RED, 0.45)` paints only that cell red. Then `get_highlighted_cell((2, 2), TEAL)` gets the bottom-right cell's background block directly and fades it in.

<video src="assets/RTM output/14b-Table-Methods-getcell.mp4" controls width="560"></video>

> Note: `get_cell` returns the **cell polygon** (with a visible stroke), which is not the same thing as `get_highlighted_cell`'s **background rectangle**; for "a cell with a background colour" the latter is easier (it handles `BackgroundRectangle`'s `buff`/`fill_opacity` for you).

### `Table.get_highlighted_cell`

```python
def get_highlighted_cell(self, pos: Sequence[int] = (1, 1), color: ParsableManimColor = YELLOW, **kwargs) -> BackgroundRectangle:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `pos` | `Sequence[int]` | `(1, 1)` | the cell position `(row, column)`, 1-based; the sample uses `(2, 2)` |
| `color` | `ManimColor` | `YELLOW` | background block colour; the sample uses `TEAL` |
| `**kwargs` | `Any` | — | passed to `BackgroundRectangle` (e.g. `fill_opacity=`, `buff=`) |

Returns a **background rectangle** object (it does not add itself to the table; `FadeIn`/`add` it yourself), good when you want to get hold of it first and decide when to show it.

#### Sample: taking the background block and fading it in

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Table, Text, Rectangle, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class GetCellDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("14b-get_cell / get_highlighted_cell", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        t = Table([["1", "2"], ["3", "4"]], include_outer_lines=True,
                  element_to_mobject=Text, element_to_mobject_config={"font_size": 34})
        t.scale(0.9).move_to([0, 0.6, 0])
        win.play(Write(t), FadeIn(cap("Table([[1,2],[3,4]])", t)), run_time=0.7)

        # —— get_cell: get the cell polygon and change its style on its own ——
        cell = t.get_cell((1, 2))   # the "pos" parameter
        win.play(cell.animate.set_fill(RED, 0.45), run_time=0.6)
        c1 = Text("get_cell((1, 2)) -> Polygon",
                  font_size=18, color=GREY_B).move_to([0, -1.5, 0])
        win.play(FadeIn(c1), run_time=0.4)

        # —— get_highlighted_cell: get the "already highlighted" background block directly ——
        hl = t.get_highlighted_cell((2, 2), color=TEAL)   # the "pos / color" parameters
        win.play(FadeIn(hl), run_time=0.5)
        newc = Text("get_highlighted_cell((2, 2), TEAL)",
                    font_size=18, color=GREY_B).move_to([0, -2.1, 0])
        win.play(FadeIn(newc), run_time=0.4)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: create —— the table's arranged entrance animation ========
```

What this code does: the second half of the same scene as the previous entry — `hl = t.get_highlighted_cell((2, 2), color=TEAL)` gets the bottom-right cell's background block, then `win.play(FadeIn(hl))` makes it appear. Because what it returns is an ordinary mobject, you can also `hl.set_opacity(0)` first and animate later.

<video src="assets/RTM output/14b-Table-Methods-getcell.mp4" controls width="560"></video>

> Note: the object it returns is **not** added to the table automatically — to make the highlight transform along with the table, do `t.add(hl)`; to just show it temporarily, `FadeIn` it directly.

### `Table.create`

```python
def create(self, lag_ratio: float = 1, line_animation: Callable[[VMobject | VGroup], Animation] = Create, label_animation: Callable[[VMobject | VGroup], Animation] = Write, element_animation: Callable[[VMobject | VGroup], Animation] = Create, entry_animation: Callable[[VMobject | VGroup], Animation] = FadeIn, **kwargs) -> AnimationGroup:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `lag_ratio` | `float` | `1` | the lag ratio between the groups (lines / labels / cells); the sample's `0.15` makes them appear almost simultaneously |
| `line_animation` | `class` | `Create` | the entrance animation for the grid lines; the sample switches it to `Write` |
| `label_animation` | `class` | `Write` | the entrance animation for the row and column labels |
| `element_animation` | `class` | `Create` | the entrance animation for the cell content |
| `entry_animation` | `class` | `FadeIn` | the animation for the whole-cell entries |
| `**kwargs` | `Any` | — | passed to the internal `AnimationGroup` (e.g. `run_time=`) |

Returns an **`AnimationGroup`** to hand straight to `win.play(...)` — it gives more of a "lines first, then the writing" sense of layering than `Create(table)`.

#### Sample: the default `create()` and `create(lag_ratio=0.15, line_animation=Write)`

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Table, Text, Rectangle, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class CreateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("14b-Table.create", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— default create(): lines Create, labels Write, elements Create, entries FadeIn ——
        t1 = Table([["a", "b"], ["c", "d"]], include_outer_lines=True,
                   element_to_mobject=Text, element_to_mobject_config={"font_size": 32})
        t1.scale(0.8).move_to([0, 0.8, 0])
        win.play(t1.create(), FadeIn(cap("create() (default animation)", t1)), run_time=1.2)

        # —— lag_ratio / line_animation / label_animation can be replaced ——
        t2 = Table([["1", "2"], ["3", "4"]], include_outer_lines=True,
                   element_to_mobject=Text, element_to_mobject_config={"font_size": 32})
        t2.scale(0.8).move_to([0, -1.8, 0])
        win.play(FadeOut(t1),
                 t2.create(lag_ratio=0.15, line_animation=Write),   # the "lag_ratio / line_animation" parameters
                 FadeIn(cap("create(lag_ratio=0.15, line_animation=Write)", t2)), run_time=1.2)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window
```

What this code does: the first table is simply `win.play(t1.create())`, showing the default "lines → labels → cells" order. The second table switches to `t2.create(lag_ratio=0.15, line_animation=Write)` — with `lag_ratio` turned down the groups start almost at the same time, and the lines get the written feel of `Write`; the contrast between the two is very clear.

<video src="assets/RTM output/14b-Table-Methods-create.mp4" controls width="560"></video>

> Note: `create()` returns an **animation group**, not the table itself — the table object still has to be built first (do not `add` the table to the scene before `win.play`, or it will appear twice).

---

See also: [Tables](14-Tables.md) · [Matrices](13-Matrices.md) · [Text](08-Text.md)
