# Probability and sample space SampleSpace

RTM uses the generic vector fallback renderer (verified by real render on 2026-10-11; the fallback draws correctly). In practice section 9 of the handbook has only one entry, `SampleSpace` (other probability mobjects such as `Tree` and `Bayes` are not included).

## SampleSpace

`SampleSpace(height=3, width=3, fill_color=DARK_GREY, fill_opacity=1, stroke_width=0.5, stroke_color=LIGHT_GREY, default_label_scale_val=1)`

A 2D rectangular "sample space" block (the box used in probability videos); it can be split horizontally / vertically into sub-blocks by a probability list, with braces and text labels. It is a `Rectangle` subclass, and `sample_space[i]` indexes the i-th block.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `height` / `width` | `float` | `3` / `3` | size |
| `fill_color` | `ParsableManimColor` | `DARK_GREY` | fill color |
| `fill_opacity` | `float` | `1` | opacity |
| `stroke_width` | `float` | `0.5` | stroke width |
| `stroke_color` | `ParsableManimColor` | `LIGHT_GREY` | stroke color |
| `default_label_scale_val` | `float` | `1` | label scale factor |

## Method overview

| Method | Signature | Frequency | Purpose |
| --- | --- | --- | --- |
| `add_title` | `(title="Sample space", buff=0.25) -> None` | 🟡 | adds a `Tex` title above (too wide is auto-shrunk to the box width) |
| `divide_horizontally` | `(*args, **kwargs) -> None` | 🟡 | split horizontally; the result is stored in `horizontal_parts` and `add`-ed to itself |
| `divide_vertically` | `(*args, **kwargs) -> None` | 🟡 | split vertically; the result is stored in `vertical_parts` |
| `get_horizontal_division` | `(p_list, colors=[GREEN_E, BLUE_E], vect=DOWN) -> VGroup` | ⚪ | only generates the horizontal pieces without adding them |
| `get_vertical_division` | `(p_list, colors=[MAROON_B, YELLOW], vect=RIGHT) -> VGroup` | ⚪ | only generates the vertical pieces without adding them |
| `get_division_along_dimension` | `(p_list, dim, colors, vect) -> VGroup` | ⚪ | generic split (`dim`: 0=vertical, 1=horizontal) |
| `complete_p_list` | `(p_list) -> list[float]` | ⚪ | fills in the remainder automatically when the probabilities sum to less than 1 |
| `add_label` | `(label) -> None` | ⚪ | records a label string in `self.label` (does not create a mobject) |
| `get_side_braces_and_labels` | `(labels, direction=LEFT, **kwargs) -> VGroup` | not supported | adds braces and labels to `horizontal_parts`. **Upstream manim 0.21 has a bug; calling it crashes** (see below) |
| `get_top_braces_and_labels` | `(labels, **kwargs) -> VGroup` | not supported | same as above (adds braces to the top of `vertical_parts`) |
| `get_bottom_braces_and_labels` | `(labels, **kwargs) -> VGroup` | not supported | same as above (bottom) |
| `get_subdivision_braces_and_labels` | `(parts, labels, direction, buff=0.1, min_num_quads=1) -> VGroup` | not supported | the generic version of the three; it is the cause of the crash (see below) |

> **All four "braces + labels" helpers above are unusable in manim 0.21** (identical in both engines):
> `get_subdivision_braces_and_labels` passes `min_num_quads` through to `Brace(...)`
> (`manim/mobject/graphing/probability.py:159`), but 0.21's `Brace` no longer has that formal parameter,
> so it raises `TypeError: Mobject.__init__() got an unexpected keyword argument 'min_num_quads'`.
> To get brace labels, **do it yourself with `Brace(part, direction)` + `brace.get_text(...)`**, which is exactly what this page's samples do.
| `add_braces_and_labels` | `() -> None` | ⚪ | merges the already-generated braces and labels into itself |

## Parameters (for splitting)

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `p_list` | `float \| Iterable[float]` | required | share of each block (auto-fills `1-sum` when the sum < 1) |
| `colors` | `Sequence[ParsableManimColor]` | see method table | color scheme (a `color_gradient` is applied) |
| `vect` | `Vector3D` | see method table | direction of the split/labels |
| `labels` | `list[str \| VMobject]` | required | label of each block |
| `buff` | `float` | `0.1` | brace buff |
| `min_num_quads` | `int` | `1` | number of brace subdivision segments |

## Sample 1: `divide_vertically` + brace labels

`divide_vertically(p_list, colors, vect)` splits the box vertically into several blocks by a probability list; the result is stored in `poly.vertical_parts` and `add`-ed to itself; `poly[i]` also indexes the i-th block directly. The sample splits into three blocks 0.37 / 0.13 / 0.50, then attaches a `Brace` + value label to the first and last blocks.

```python
import numpy as np
from real_time_manim import (
    BLACK, BLUE_E, Brace, Create, DOWN, FadeIn, GRAY, GREEN_E, GREY_B, LEFT,
    RIGHT, SampleSpace, Scene, Text, UP, WHITE, YELLOW, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class VerticalDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("09-SampleSpace", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        poly = SampleSpace(width=2, height=2, stroke_width=5, fill_opacity=0.1)   #the sample-space box
        poly.divide_vertically(   #"divide_vertically": split vertically by a probability list
            p_list=np.array([0.37, 0.13, 0.5]),   #parameter "p_list": share of each block (auto-fills the remainder when the sum is under 1)
            colors=[BLACK, WHITE, GRAY],   #parameter "colors": color scheme (a gradient is applied automatically)
            vect=RIGHT)   #parameter "vect": split direction
        poly.add_title("Sample space")   #"add_title": title above the box
        win.play(Create(poly), run_time=0.8)   #draw the box and the split blocks
        win.play(Wait(0.5))   #wait 0.5s

        b0 = Brace(poly.vertical_parts[0], LEFT)   #attach a brace on the left of block 0
        t0 = b0.get_text("0.37")   #"get_text": the label next to the brace
        b2 = Brace(poly.vertical_parts[2], RIGHT)   #attach one on the right of the rightmost block
        t2 = b2.get_text("0.50")
        win.play(FadeIn(b0), FadeIn(t0), run_time=0.4)   #the two labels fade in one after another
        win.play(FadeIn(b2), FadeIn(t2), run_time=0.4)
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window
```

What this code does:

- `divide_vertically` divides the width according to the ratios in `p_list`; `colors` has only 3 entries → one color per block (with more than 3 blocks it interpolates with `color_gradient`).
- `add_title` writes a title above the box with `Tex` (too wide is auto-shrunk to the box width).
- The braces are standard `Brace`s attached to the left / right of `vertical_parts[i]`, and `get_text` gives the label line beside them.

<video src="assets/RTM output/09-Probability-and-SampleSpace-basic.mp4" controls width="560"></video>

> Note:
>
> - `add_title` uses `Tex(title)` internally, so **do not put `_` in the title** (math-mode subscript, raises `Missing $ inserted`); to get an underscore, escape it or use `Text` instead.
> - As long as the sum of `p_list` is ≤1, `complete_p_list` fills the shortfall into the last block automatically.

## Sample 2: `divide_horizontally` + auto-filling the shortfall

`divide_horizontally` is the horizontal version of the same logic; the result is stored in `grid.horizontal_parts`. The sample gives only `[0.4, 0.25]`; the remaining 0.35 is filled in as a third block automatically.

```python
import numpy as np
from real_time_manim import (
    BLACK, BLUE_E, Brace, Create, DOWN, FadeIn, GRAY, GREEN_E, GREY_B, LEFT,
    RIGHT, SampleSpace, Scene, Text, UP, WHITE, YELLOW, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class HorizontalDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("09-divide_horizontally", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        grid = SampleSpace(height=2.5, width=3, fill_opacity=0.6)   #a flatter sample space
        grid.divide_horizontally(   #"divide_horizontally": split horizontally by a probability list
            p_list=[0.4, 0.25],   #only two blocks = 0.65; the remaining 0.35 is filled in as a third block by complete_p_list
            colors=[GREEN_E, BLUE_E],
            vect=DOWN)   #parameter "vect": split direction
        grid.add_title("horizontal division")   #the title states the split method (do not put `_` in the Tex)
        win.play(Create(grid), run_time=0.8)   #draw the three blocks
        win.play(Wait(0.5))   #wait 0.5s

        labels = ["0.40", "0.25", "0.35"]
        braces = [Brace(grid.horizontal_parts[i], LEFT) for i in range(3)]   #one brace on the left of each row
        texts = [braces[i].get_text(labels[i]) for i in range(3)]
        win.play(*[FadeIn(b) for b in braces], run_time=0.4)   #the three braces fade in together
        win.play(*[FadeIn(t) for t in texts], run_time=0.4)   #the three labels fade in together
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window
```

What this code does: after a horizontal split, `horizontal_parts` are arranged from top to bottom; `colors=[GREEN_E, BLUE_E]` gives only two colors → the three blocks are colored with a gradient. `complete_p_list` fills the part under 1 into the end, so the third block's label is the automatically computed `0.35`.

<video src="assets/RTM output/09-Probability-and-SampleSpace-horizontal.mp4" controls width="560"></video>

> Note:
>
> - `horizontal_parts[i]` is a **sub-block mobject**, so you can `Brace` / color / animate it directly.
> - `parts.braces` and `parts.labels` are only written when you go through those four helpers (broken in 0.21).

See also: [Bar chart BarChart](08-BarChart.md) · [Containers and grouping](../04-Shapes-and-Text/06-Containers-and-Grouping.md) · [Boolean operations](../04-Shapes-and-Text/05-Boolean-Operations.md)
