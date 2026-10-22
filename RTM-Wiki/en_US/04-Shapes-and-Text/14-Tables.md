# Tables

Generates a ruled table from a 2D list; defined in `mobject/table.py`. One sample per class, and the `Table` sample cycles through **all of its constructor parameters**; `MathTable` / `MobjectTable` / `IntegerTable` / `DecimalTable` used to be "not filmed separately" and have now been added.

> **The cell rendering class decides "what can go in"**:
>
> - `Table` defaults to `Paragraph` (plain text)
> - `MathTable` defaults to `MathTex` (goes through LaTeX)
> - `MobjectTable` defaults to the identity function (place ready-made objects directly)
> - `IntegerTable`/`DecimalTable` default to `Integer`/`DecimalNumber` (**numbers**)
>
> If an element's type does not match the rendering class it raises an error (a numeric element handed to `Text`/`MathTex` raises `AttributeError`, the same trap as in [Matrices](13-Matrices.md)).
>
> **`Table` inherits from `VGroup`**: so every general `VGroup` technique (`arrange`, `scale`, colouring the whole thing, subscript indexing) works; see [Table methods](14b-Table-Methods.md) for the three table-specific methods `get_cell` / `add_highlighted_cell` / `create`.

## Parameters

### `Table`

```python
def __init__(self, table: Iterable[Iterable[Any]], row_labels: Iterable[VMobject] | None = None, col_labels: Iterable[VMobject] | None = None, top_left_entry: VMobject | None = None, v_buff: float = 0.8, h_buff: float = 1.3, include_outer_lines: bool = False, include_inner_lines: bool = True, add_background_rectangles_to_entries: bool = False, entries_background_color: ManimColor = BLACK, include_background_rectangle: bool = False, background_rectangle_color: ManimColor = BLACK, element_to_mobject: type[VMobject] | Callable[..., VMobject] = Paragraph, element_to_mobject_config: dict = {}, arrange_in_grid_config: dict = {}, line_config: dict = {}, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `table` | `list[list]` | required | 2D content (the elements must be acceptable to `element_to_mobject`) |
| `row_labels` | `list[Mobject] \| None` | `None` | row labels (the sample gives two `Text`s) |
| `col_labels` | `list[Mobject] \| None` | `None` | column labels |
| `top_left_entry` | `Mobject \| None` | `None` | the top-left cell; **only usable when both row and column labels are given** |
| `v_buff` | `float` | `0.8` | row spacing; the sample uses `1.6` |
| `h_buff` | `float` | `1.3` | column spacing; the sample uses `2.6` |
| `include_outer_lines` | `bool` | `False` | whether to draw the outermost frame lines; the sample compares it in combination with `include_inner_lines` |
| `include_inner_lines` | `bool` | `True` | whether to draw the inner grid lines |
| `add_background_rectangles_to_entries` | `bool` | `False` | add a background to **every cell** |
| `entries_background_color` | `ManimColor` | `BLACK` | per-cell background colour; the sample uses `TEAL` |
| `include_background_rectangle` | `bool` | `False` | add one background for the **whole table** |
| `background_rectangle_color` | `ManimColor` | `BLACK` | whole-table background colour; the sample uses `GREEN` |
| `element_to_mobject` | `class`/`callable` | `Paragraph` | cell rendering class; the sample switches it to `Text` |
| `element_to_mobject_config` | `dict` | `{}` | the config passed to the rendering class (e.g. `{"font_size": 34}`) |
| `arrange_in_grid_config` | `dict` | `{}` | grid arrangement config; the sample uses `{"cell_alignment": UP}` |
| `line_config` | `dict` | `{}` | line style; the sample uses `{"stroke_width": 4, "color": YELLOW}` |

Methods: `get_rows()` / `get_columns()` / `get_entries()` (return the substructures), `get_horizontal_lines()` / `get_vertical_lines()` (return the line objects), `set_row_colors(*colors)` / `set_column_colors(*colors)` (colour by row/column), `add_background_to_entries(color)` (add a background to every cell afterwards).

#### Sample: cycling through the 15 constructor parameters + six methods

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Table, MathTable, MobjectTable, IntegerTable, DecimalTable, Integer,
    DecimalNumber, Text, MathTex, Square, Circle, Dot, Arrow, Star, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class TableDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("14-Table", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        stage = VGroup()   # the current section's table + caption: fade out the previous section first so nothing overlaps
        def show(mob, capt, t=0.6):
            nonlocal stage
            c = Text(capt, font_size=18, color=GREY_B).next_to(mob, DOWN, buff=0.3)
            if len(stage):
                win.play(FadeOut(stage), run_time=0.2)
            win.play(Write(mob), FadeIn(c), run_time=t)
            stage = VGroup(mob, c)

        # —— default: only the inner grid lines are drawn, cells are rendered with Paragraph ——
        t1 = Table([["a", "b"], ["c", "d"]], element_to_mobject=Text,
                   element_to_mobject_config={"font_size": 34})   # the "table" parameter
        t1.scale(0.8).move_to([0, 0.6, 0])
        show(t1, "Table([[a,b],[c,d]])")

        # —— include_outer_lines / include_inner_lines: outer frame and inner lines ——
        t2 = Table([["a", "b"], ["c", "d"]], include_outer_lines=True, include_inner_lines=False,
                   element_to_mobject=Text, element_to_mobject_config={"font_size": 34})
        t2.scale(0.8).move_to([0, 0.6, 0])   # the "include_outer_lines / include_inner_lines" parameters
        show(t2, "outer=True inner=False")

        # —— line_config: line style ——
        t3 = Table([["a", "b"], ["c", "d"]], include_outer_lines=True,
                   line_config={"stroke_width": 4, "color": YELLOW},   # the "line_config" parameter
                   element_to_mobject=Text, element_to_mobject_config={"font_size": 34})
        t3.scale(0.8).move_to([0, 0.6, 0])
        show(t3, "line_config=thick yellow")

        # —— row_labels / col_labels / top_left_entry ——
        t4 = Table([["1", "2"], ["3", "4"]],
                   row_labels=[Text("R1", font_size=28), Text("R2", font_size=28)],   # the "row_labels" parameter
                   col_labels=[Text("C1", font_size=28), Text("C2", font_size=28)],   # the "col_labels" parameter
                   top_left_entry=Text("T", font_size=28, color=TEAL),   # the "top_left_entry" parameter
                   include_outer_lines=True,
                   element_to_mobject=Text, element_to_mobject_config={"font_size": 32})
        t4.scale(0.85).move_to([0, 0.4, 0])
        show(t4, "row/col_labels + top_left_entry", t=0.7)

        # —— v_buff / h_buff + arrange_in_grid_config ——
        t5 = Table([["a", "b"], ["c", "d"]], v_buff=1.6, h_buff=2.6,   # the "v_buff / h_buff" parameters
                   arrange_in_grid_config={"cell_alignment": UP},   # the "arrange_in_grid_config" parameter
                   include_outer_lines=True,
                   element_to_mobject=Text, element_to_mobject_config={"font_size": 32})
        t5.scale(0.7).move_to([0, 0.4, 0])
        show(t5, "v_buff/h_buff/cell_alignment", t=0.7)

        # —— two kinds of background: per-cell background + whole-table background ——
        t6 = Table([["a", "b"], ["c", "d"]], include_outer_lines=True,
                   add_background_rectangles_to_entries=True,   # the "add_background_rectangles_to_entries / entries_background_color" parameters
                   entries_background_color=TEAL,
                   element_to_mobject=Text, element_to_mobject_config={"font_size": 32}).scale(0.7).move_to([0, 0.4, 0])
        show(t6, "per-cell bg TEAL")

        # —— include_background_rectangle + background_rectangle_color ——
        t7 = Table([["a", "b"], ["c", "d"]], include_outer_lines=True,
                   include_background_rectangle=True,   # the "include_background_rectangle / background_rectangle_color" parameters
                   background_rectangle_color=GREEN,
                   element_to_mobject=Text, element_to_mobject_config={"font_size": 32}).scale(0.8).move_to([-2.6, 0.2, 0])
        win.play(FadeOut(stage), run_time=0.2)
        win.play(Write(t7), FadeIn(Text("whole-table bg GREEN", font_size=18, color=GREY_B).next_to(t7, DOWN, buff=0.3)), run_time=0.6)

        # —— methods: reading rows/columns/cells, colouring rows and columns, frame and inner segments, adding a background afterwards ——
        info = VGroup(
            Text("rows=%d cols=%d entries=%d" % (len(t7.get_rows()), len(t7.get_columns()), len(t7.get_entries())), font_size=18, color=GREY_B),   # the "get_rows / get_columns / get_entries" methods
            Text("h_lines=%d v_lines=%d" % (len(t7.get_horizontal_lines()), len(t7.get_vertical_lines())), font_size=18, color=GREY_B),   # the "get_horizontal_lines / get_vertical_lines" methods
        ).arrange(DOWN, buff=0.12).move_to([2.6, 0.6, 0])
        win.play(FadeIn(info), run_time=0.5)
        c7 = Text("set_column_colors(RED, BLUE)", font_size=18, color=GREY_B).next_to(t7, DOWN, buff=0.85)
        win.play(FadeIn(c7), run_time=0.3)
        t7.set_column_colors(RED, BLUE)   # the "set_column_colors(*colors)" method
        win.play(Write(t7), run_time=0.4)
        c7.become(Text("set_row_colors(ORANGE, PURPLE)", font_size=18, color=GREY_B).next_to(t7, DOWN, buff=0.85))
        t7.set_row_colors(ORANGE, PURPLE)   # the "set_row_colors(*colors)" method
        win.play(Write(t7), run_time=0.4)
        c7.become(Text("add_background_to_entries(TEAL)", font_size=18, color=GREY_B).next_to(t7, DOWN, buff=0.85))
        t7.add_background_to_entries(TEAL)   # the "add_background_to_entries(color)" method
        win.play(Write(t7), run_time=0.5)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: MathTable —— a formula table =============================
```

What this code does: it swaps one parameter or one group of parameters at a time, each section with a caption line.

- Default: only the inner grid lines, cells go through `Paragraph`.
- `include_outer_lines=True` + `include_inner_lines=False`: only the outer frame.
- `line_config` changed to thick yellow lines.
- `row_labels`/`col_labels`/`top_left_entry` given together.
- `v_buff`/`h_buff` pulled apart, plus `arrange_in_grid_config={"cell_alignment": UP}`.
- "Per-cell background `TEAL`" demonstrated.
- "Whole-table background `GREEN`" demonstrated.
- The last section runs the methods: the counts from `get_rows/get_columns/get_entries` and `get_horizontal_lines/get_vertical_lines` are printed as readings, then `set_column_colors`, `set_row_colors` and `add_background_to_entries(TEAL)` in turn.

<video src="assets/RTM output/14-Tables-table.mp4" controls width="560"></video>

> Note: `top_left_entry` is only shown when **both** row labels and column labels are given (the table has to leave room for it in the top-left corner); `set_row_colors`/`set_column_colors` are "brush colour by row/column", and a later call overwrites an earlier one's colour on the same cells.

### `MathTable`

```python
def __init__(self, table: Iterable[Iterable[str]], element_to_mobject: type[SingleStringMathTex] = MathTex, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `table` | `list[list[str]]` | required | cell text (goes through LaTeX math mode, so `r"\frac{a}{b}"` can be written directly) |
| `element_to_mobject` | `class` | `MathTex` | cell rendering class; the sample switches it to `Text` (changing to ordinary text typesetting) |
| Others | — | — | exactly the same as `Table` (the sample uses labels, `line_config`, `v_buff`/`h_buff`, a per-cell background) |

#### Sample: formula cells / switched to `Text` / labels + line style + spacing + background

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Table, MathTable, MobjectTable, IntegerTable, DecimalTable, Integer,
    DecimalNumber, Text, MathTex, Square, Circle, Dot, Arrow, Star, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class MathTableDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("14-MathTable", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— default: cells are rendered with MathTex (LaTeX math mode) ——
        mt = MathTable([[r"x^2", r"\sqrt{y}"], [r"\frac{a}{b}", r"\sum_{i=1}^{n} i"]],
                       include_outer_lines=True)   # the "table" parameter
        mt.scale(0.9).move_to([-3.4, 1.0, 0])
        win.play(Write(mt), FadeIn(Text("MathTable (LaTeX cells)", font_size=18, color=GREY_B).next_to(mt, DOWN, buff=0.35)), run_time=0.8)

        # —— element_to_mobject: switch to Text (only meaningful for cells that can be read as text) ——
        mt2 = MathTable([["x", "y"], ["a", "b"]],
                        element_to_mobject=Text,   # the "element_to_mobject" parameter
                        include_outer_lines=True)
        mt2.scale(0.9).move_to([3.0, 1.0, 0])
        win.play(Write(mt2), FadeIn(Text("element_to_mobject=Text", font_size=18, color=GREY_B).next_to(mt2, DOWN, buff=0.35)), run_time=0.7)

        # —— the remaining parameters are the same as Table: labels, lines, spacing, background ——
        self.clear()   # clear the stage: take away the previous section's table and caption together
        self.add(title)
        mt3 = MathTable([[r"1", r"2"], [r"3", r"4"]],
                        row_labels=[MathTex(r"i"), MathTex(r"j")],
                        col_labels=[MathTex(r"a"), MathTex(r"b")],
                        top_left_entry=MathTex(r"\times"),
                        include_outer_lines=True, include_inner_lines=True,
                        line_config={"stroke_width": 3, "color": ORANGE},
                        v_buff=1.0, h_buff=1.6,
                        add_background_rectangles_to_entries=True,
                        entries_background_color=BLUE)
        mt3.scale(0.8).move_to([0, -2.0, 0])
        win.play(Write(mt3), FadeIn(Text("labels + line style + spacing + per-cell bg", font_size=18, color=GREY_B).move_to([0, -3.6, 0])), run_time=0.8)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: MobjectTable —— shapes in the cells =====================
```

What this code does: three blocks.

- On the left, four formulas are rendered with `MathTex` (`x^2`, `\sqrt{y}`, `\frac{a}{b}`, `\sum`), showing the typesetting of LaTeX math mode.
- On the right, `element_to_mobject` is switched to `Text`, and the same cell content is typeset as ordinary text.
- The bottom one is a full configuration: row and column labels + `top_left_entry` all with `MathTex`, a thick orange `line_config`, `v_buff`/`h_buff` pulled apart, and a `BLUE` per-cell background.

<video src="assets/RTM output/14-Tables-mathtable.mp4" controls width="560"></video>

> Note: `MathTable`'s cell strings **must be valid LaTeX** (an unescaped underscore, `%`, etc. fails to compile); to put in ordinary text, use `Text` or `element_to_mobject=Text`.

### `MobjectTable`

```python
def __init__(self, table: Iterable[Iterable[Mobject]], element_to_mobject: Callable = <identity>, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `table` | `list[list[Mobject]]` | required | each cell is a ready-made Mobject (`Circle`, `Square`, `Text`…) |
| `element_to_mobject` | `callable` | the identity function | element conversion function; the sample gives `lambda m: m.copy().scale(0.5)` to shrink uniformly |
| Others | — | — | the same as `Table` (the sample uses `v_buff`/`h_buff`/`line_config`) |

#### Sample: placing ready-made objects / shrinking with a conversion function / mixing shapes and text

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Table, MathTable, MobjectTable, IntegerTable, DecimalTable, Integer,
    DecimalNumber, Text, MathTex, Square, Circle, Dot, Arrow, Star, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class MobjectTableDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("14-MobjectTable", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— the default element_to_mobject is the identity function: place ready-made objects directly ——
        m1 = MobjectTable([[Circle(radius=0.3, color=BLUE), Square(side_length=0.6, color=GREEN)],
                           [Dot(radius=0.16, color=RED), Star(color=ORANGE).scale(0.35)]],
                          include_outer_lines=True)   # the "table" parameter
        m1.scale(0.9).move_to([-3.4, 1.0, 0])
        win.play(Create(m1), FadeIn(Text("MobjectTable([[Circle, Square], …])", font_size=18, color=GREY_B).next_to(m1, DOWN, buff=0.35)), run_time=0.9)

        # —— element_to_mobject: a uniform conversion (here every object is shrunk by half) ——
        m2 = MobjectTable([[Circle(radius=0.6, color=TEAL), Square(side_length=1.2, color=GOLD)],
                           [Dot(radius=0.3, color=PURPLE), Star(color=YELLOW).scale(0.7)]],
                          element_to_mobject=lambda m: m.copy().scale(0.5),   # the "element_to_mobject" parameter
                          include_outer_lines=True, v_buff=1.2, h_buff=1.6)
        m2.scale(0.9).move_to([2.8, 1.0, 0])
        win.play(Create(m2), FadeIn(Text("element_to_mobject=lambda m: m.copy().scale(0.5)", font_size=18, color=GREY_B).next_to(m2, DOWN, buff=0.35)), run_time=0.9)

        # —— shapes + text mixed: one cell an object, one cell text ——
        self.clear()   # clear the stage: take away the previous section's table and caption together
        self.add(title)
        m3 = MobjectTable([[Text("circle", font_size=30, color=BLUE), Circle(radius=0.28, color=BLUE)],
                           [Text("square", font_size=30, color=GREEN), Square(side_length=0.55, color=GREEN)]],
                          include_outer_lines=True, v_buff=1.0, h_buff=1.4,
                          line_config={"stroke_width": 3, "color": GREY_B})
        m3.scale(0.9).move_to([0, -2.0, 0])
        win.play(Create(m3), FadeIn(Text("shapes and text mixed", font_size=18, color=GREY_B).next_to(m3, DOWN, buff=0.35)), run_time=0.9)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 4: IntegerTable —— an integer table ========================
```

What this code does: three blocks.

- On the left four shapes are placed directly (circle, square, dot, star).
- On the right the elements are made larger first and then handed to `element_to_mobject=lambda m: m.copy().scale(0.5)`; on screen the two groups are the same size, showing that this parameter is "the conversion function for each cell's object".
- The bottom one mixes text and shapes in the same table, one cell text and one cell shape.

<video src="assets/RTM output/14-Tables-mobjecttable.mp4" controls width="560"></video>

> Note: inside the conversion function, call `m.copy()` before modifying; modifying the object passed in directly also changes the one the caller is holding. The table's lines are **separate objects** and do not scale along with the cells.

### `IntegerTable`

```python
def __init__(self, table: Iterable[Iterable[int]], element_to_mobject: type[Integer] = Integer, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `table` | `list[list[int]]` | required | integer data |
| `element_to_mobject` | `class` | `Integer` | cell rendering class; the sample switches it to `DecimalNumber` (numeric elements are accepted, with `num_decimal_places=0`) |
| Others | — | — | the same as `Table` (the sample uses row and column labels + `color`) |

#### Sample: default / switching to `DecimalNumber` / labelled and coloured

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Table, MathTable, MobjectTable, IntegerTable, DecimalTable, Integer,
    DecimalNumber, Text, MathTex, Square, Circle, Dot, Arrow, Star, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class IntegerTableDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("14-IntegerTable", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— default: cells are rendered with Integer ——
        it = IntegerTable([[1, 2, 3], [4, 5, 6]], include_outer_lines=True)   # the "table" parameter
        it.scale(0.9).move_to([-3.2, 1.0, 0])
        win.play(Write(it), FadeIn(Text("IntegerTable([[1,2,3],[4,5,6]])", font_size=18, color=GREY_B).next_to(it, DOWN, buff=0.35)), run_time=0.8)

        # —— element_to_mobject: switch to DecimalNumber (any numeric element is accepted) ——
        it2 = IntegerTable([[7, 8], [9, 10]], element_to_mobject=DecimalNumber,
                           element_to_mobject_config={"num_decimal_places": 0},   # the "element_to_mobject / config" parameters
                           include_outer_lines=True)
        it2.scale(0.9).move_to([2.4, 1.0, 0])
        win.play(Write(it2), FadeIn(Text("element_to_mobject=DecimalNumber", font_size=18, color=GREY_B).next_to(it2, DOWN, buff=0.35)), run_time=0.8)

        # —— the remaining parameters are the same as Table: row and column labels + colour ——
        self.clear()   # clear the stage: take away the previous section's table and caption together
        self.add(title)
        it3 = IntegerTable([[10, 20], [30, 40]],
                           row_labels=[Text("r1", font_size=26), Text("r2", font_size=26)],
                           col_labels=[Text("c1", font_size=26), Text("c2", font_size=26)],
                           include_outer_lines=True, v_buff=1.2, h_buff=2.0,
                           color=TEAL)
        it3.scale(0.85).move_to([0, -2.0, 0])
        win.play(Write(it3), FadeIn(Text("labels + color=TEAL", font_size=18, color=GREY_B).move_to([0, -3.6, 0])), run_time=0.8)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 5: DecimalTable —— a decimal table =========================
```

What this code does: three blocks.

- On the left, a 2×3 integer table rendered with the default `Integer`.
- On the right it is switched to `DecimalNumber` with `element_to_mobject_config={"num_decimal_places": 0}`, visually identical to the integer version, proving the two are equivalent.
- The bottom one adds row and column labels, pulls `v_buff`/`h_buff` apart, and gives the whole table `color=TEAL`.

<video src="assets/RTM output/14-Tables-integertable.mp4" controls width="560"></video>

> Note: do not switch numeric elements to `Text`/`MathTex` (they want strings); switch to another number class instead; `color` acts on the cells and the grid lines at the same time.

### `DecimalTable`

```python
def __init__(self, table: Iterable[Iterable[float]], element_to_mobject: type[DecimalNumber] = DecimalNumber, element_to_mobject_config: dict = {"num_decimal_places": 1}, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `table` | `list[list[float]]` | required | decimal data |
| `element_to_mobject` | `class` | `DecimalNumber` | cell rendering class; the sample switches it to `Integer` (rounded display) |
| `element_to_mobject_config` | `dict` | `{"num_decimal_places": 1}` | cell config; the sample uses 3 decimal places and `{"font_size": 40}` |
| Others | — | — | the same as `Table` |

#### Sample: default 1 place / 3 places / switching to `Integer`

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Table, MathTable, MobjectTable, IntegerTable, DecimalTable, Integer,
    DecimalNumber, Text, MathTex, Square, Circle, Dot, Arrow, Star, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class DecimalTableDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("14-DecimalTable", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— default num_decimal_places=1 ——
        dt = DecimalTable([[1.25, 3.5], [7.75, 9.0]], include_outer_lines=True)   # the "table" parameter
        dt.scale(0.9).move_to([-3.2, 1.0, 0])
        win.play(Write(dt), FadeIn(Text("default 1 decimal", font_size=18, color=GREY_B).next_to(dt, DOWN, buff=0.35)), run_time=0.8)

        # —— element_to_mobject_config: 3 decimal places ——
        dt2 = DecimalTable([[1.2345, 3.4567], [5.6789, 7.891]],
                           element_to_mobject_config={"num_decimal_places": 3},   # the "element_to_mobject_config" parameter
                           include_outer_lines=True)
        dt2.scale(0.9).move_to([2.4, 1.0, 0])
        win.play(Write(dt2), FadeIn(Text("num_decimal_places=3", font_size=18, color=GREY_B).next_to(dt2, DOWN, buff=0.35)), run_time=0.8)

        # —— element_to_mobject: switch to Integer (any numeric element is accepted; here it rounds) ——
        self.clear()   # clear the stage: take away the previous section's table and caption together
        self.add(title)
        dt3 = DecimalTable([[1.25, 3.5], [7.75, 9.0]], element_to_mobject=Integer,
                           element_to_mobject_config={"font_size": 40},   # the "element_to_mobject" parameter
                           include_outer_lines=True)
        dt3.scale(0.9).move_to([0, -2.0, 0])
        win.play(Write(dt3), FadeIn(Text("element_to_mobject=Integer", font_size=18, color=GREY_B).next_to(dt3, DOWN, buff=0.35)), run_time=0.8)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window
```

What this code does: three blocks.

- On the left, the default 1 decimal place.
- On the right `element_to_mobject_config` is changed to `{"num_decimal_places": 3}`, and the data keeps more places.
- The bottom one switches `element_to_mobject` to `Integer` with `{"font_size": 40}`, so the cells become rounded — showing that this table class only decides "how numbers are rendered by default".

<video src="assets/RTM output/14-Tables-decimaltable.mp4" controls width="560"></video>

> Note: `element_to_mobject_config` is a **whole replacement** (not merged with the defaults), so when changing the number of places it is safest to write `font_size` in as well (which is what the sample does).

---

See also: [Table methods](14b-Table-Methods.md) · [Matrices](13-Matrices.md) · [Text](08-Text.md)
