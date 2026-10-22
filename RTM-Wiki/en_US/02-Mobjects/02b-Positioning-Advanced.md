# Positioning (advanced)

Arrangement, grids, enclosing and coordinate fine-tuning — placement tools that work in bulk better than `next_to`. All the methods below return `self`.

## Parameters

### align_on_border

```python
def align_on_border(direction: Vector3DLike, buff: float = 0.5) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `direction` | vector | — | direction toward the edge/corner, **need not be a unit vector**. **Accepts** edge directions such as `UP` / `LEFT` (snap to an edge) or diagonal directions such as `UL` / `DR` (snap to a corner) |
| `buff` | `float` | `0.5` | margin. The actual displacement subtracts `buff * direction`, so a non-unit direction scales the margin by component |

> **Returns**: `self`. Aligns own `direction` critical point to `sign(direction) × (frame_x_radius, frame_y_radius)` — `to_edge` / `to_corner` (see [02-Positioning](02-Positioning.md)) are two wrappers over it.

#### Sample: `align_on_border` snapping to an edge and a corner

The red square snaps to the top edge and the blue square to the bottom-right corner, both with a margin of 0.4.

```python
from real_time_manim import Scene, Square, \
    RED, BLUE, UP, DR, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class BorderDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        a = Square(color=RED, side_length=0.9)   # the square on the top edge
        b = Square(color=BLUE, side_length=0.9)   # the square at the bottom-right corner
        a.align_on_border(UP, buff=0.4)   # the critical point snaps to the upper border, margin 0.4
        b.align_on_border(DR, buff=0.4)   # the critical point snaps to the bottom-right corner
        self.add(a, b)   # add them to the scene
        win.play(FadeIn(a), FadeIn(b), run_time=0.6)   # fade in both squares
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window
```

What this code does: two same-sized squares each snap to their own spot — the red square's `direction=UP` moves its top-edge midpoint to 0.4 inside the frame's top border; the blue square's `direction=DR` snaps its bottom-right corner to the boundary in the bottom-right direction. This is exactly what `to_edge` / `to_corner` do underneath, except here the direction is given in one go instead of being split into two methods.

<video src="assets/RTM output/02b-Positioning-Advanced-border.mp4" controls width="560"></video>

> Note: the `buff * direction` implementation detail means a non-unit vector (such as `UP * 2`) doubles the margin; if you are using the direction vector only for its sign, remember to normalize. In everyday use, going straight to `to_edge` / `to_corner` is less trouble.

### set_coord / set_x / set_y / set_z

```python
def set_coord(value: float, dim: int, direction: Vector3DLike = ORIGIN) -> Self
def set_x(x: float, direction: Vector3DLike = ORIGIN) -> Self
def set_y(y: float, direction: Vector3DLike = ORIGIN) -> Self
def set_z(z: float, direction: Vector3DLike = ORIGIN) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `value` / `x` / `y` / `z` | `float` | — | target coordinate (absolute value, not a delta) |
| `dim` | `int` | — | **only** `0`=x, `1`=y, `2`=z (`set_coord` only) |
| `direction` | vector | `ORIGIN` | which critical point aims at that coordinate: center by default; `LEFT` means "set the left edge's x to this value" |

> **Returns**: `self`. `set_x` / `set_y` / `set_z` are `set_coord` with a fixed `dim`. Only one axis changes and the other stays put; handy with `get_x` when writing updaters.

#### Sample: setting coordinates axis by axis with `set_x` / `set_y` / `set_coord`

In three steps the square sets x to -3, y to 1.5, then uses `set_coord` to set x to 2.5; finally `direction=LEFT` honours only the left edge, and the z change is printed to the console.

```python
from real_time_manim import Scene, Square, \
    BLUE, LEFT, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class CoordsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.2, fill_opacity=0.6)   # blue square
        self.add(sq)   # add it to the scene
        win.play(sq.animate.set_x(-3.0), run_time=0.5)   # set_x: x set to -3, y unmoved
        win.play(sq.animate.set_y(1.5), run_time=0.5)   # set_y: y set to 1.5, x unmoved
        win.play(sq.animate.set_coord(2.5, 0), run_time=0.5)   # set_coord: dim=0, i.e. x set to 2.5
        sq.set_x(0.0, direction=LEFT)   # direction=LEFT: set the left edge's x to 0 (the center stops at 0.6)
        sq.set_z(0.5)   # set_z: change the z coordinate, invisible in a 2D frame
        print("get_z =", sq.get_z())   # verify z really became 0.5
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window
```

What this code does: a blue square has its coordinates "set" in three steps — `set_x(-3)` moves only x, `set_y(1.5)` moves only y, `set_coord(2.5, 0)` is equivalent to `set_x(2.5)`; then `set_x(0.0, direction=LEFT)` changes it to aim the **left edge**'s x at 0, so the square's center stops at 0.6 instead of 0. Finally `set_z(0.5)` changes the z axis — invisible in a 2D frame, and the console prints `get_z` to verify it really took effect.

<video src="assets/RTM output/02b-Positioning-Advanced-coords.mp4" controls width="560"></video>

> Note: these are **absolute coordinates** (`set_x(2)` = x becomes 2); don't mix them up with `shift`'s relative displacement. `direction` lets you aim by edge/corner, handy for layout such as "put the left edge on the guide line"; with nothing passed it uses the center.

### arrange

```python
def arrange(direction: Vector3DLike = RIGHT, buff: float = 0.25,
            center: bool = True, **kwargs: Any) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `direction` | vector | `RIGHT` | arrangement direction. **Accepts** `RIGHT` (a row), `DOWN` (a column), and so on |
| `buff` | `float` | `0.25` | gap between neighbours |
| `center` | `bool` | `True` | whether to move the whole group to the origin afterwards; pass `False` to keep the position |
| `**kwargs` | `Any` | — | forwarded to each `next_to` (e.g. `aligned_edge=`) |

> **Returns**: `self`. Each child `next_to` the previous one in turn; the first choice for bulk layout.

#### Sample: `arrange` in a row and a column, and `center`

Three squares first line up in a centered row, then animate into a column (spacing 0.6), and finally `center=False` arranges them back into a row in place.

```python
from real_time_manim import Scene, VGroup, Square, \
    RED, BLUE, GREEN, RIGHT, DOWN, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class ArrangeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        row = VGroup(*[Square(color=c, side_length=0.8) for c in (RED, BLUE, GREEN)])   # three squares
        row.arrange(RIGHT, buff=0.35)   # default center=True: center the whole thing
        self.add(row)   # add it to the scene
        win.play(FadeIn(row), run_time=0.5)   # fade in the row
        win.play(row.animate.arrange(DOWN, buff=0.6), run_time=0.6)   # change to a column, spacing 0.6
        win.play(row.animate.arrange(RIGHT, buff=1.0, center=False), run_time=0.6)   # center=False: don't recenter
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window
```

What this code does: three squares first line up in a row with the default parameters (`center=True`, the row moves to the middle of the frame); then `arrange(DOWN, buff=0.6)` is played and the three squares move toward one another as they change into a column; finally `arrange(RIGHT, buff=1.0, center=False)` arranges them back into a row — note that with `center=False` the row does **not** recenter but spreads in place, staying where the column was.

<video src="assets/RTM output/02b-Positioning-Advanced-arrange.mp4" controls width="560"></video>

> Note: `arrange` always lays out from the **current** child order — to fix the order, `sort` first or arrange them at construction time (see [11b-Misc-APIs](11b-Misc-APIs.md)). `**kwargs` is forwarded to the `next_to` of every adjacent pair, so `aligned_edge=DOWN` and the like can align the whole row by the bottom edge.

### arrange_in_grid

```python
def arrange_in_grid(rows: int | None = None, cols: int | None = None,
                    buff: float | tuple[float, float] = 0.25,
                    cell_alignment: Vector3DLike = ORIGIN,
                    row_alignments: str | None = None,
                    col_alignments: str | None = None,
                    row_heights: Iterable[float | None] | None = None,
                    col_widths: Iterable[float | None] | None = None,
                    flow_order: str = "rd", **kwargs: Any) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `rows` / `cols` | `int` or `None` | `None` | number of rows / columns; give only one and the other is filled in automatically, give neither and a near-square is inferred; raises `ValueError` when `rows*cols` cannot fit everything |
| `buff` | `float` or `(row, col)` tuple | `0.25` | cell spacing; the tuple form specifies row and column spacing separately |
| `cell_alignment` | vector | `ORIGIN` | alignment of an element inside its cell |
| `row_alignments` | `str` or `None` | `None` | per-row alignment: `"u"` top / `"c"` center / `"d"` bottom |
| `col_alignments` | `str` or `None` | `None` | per-column alignment: `"l"` left / `"c"` center / `"r"` right |
| `row_heights` | iterable or `None` | `None` | per-row height; `None` uses the tallest in that row |
| `col_widths` | iterable or `None` | `None` | per-column width; `None` uses the widest in that column |
| `flow_order` | `str` | `"rd"` | fill order. **Accepts** `rd`/`dr`/`ld`/`dl`/`ru`/`ur`/`lu`/`ul` (r=right, l=left, d=down, u=up) |

> **Returns**: `self`. Children are put into the grid cells one by one following the "fill order"; the color order is the fill order.

#### Sample: `arrange_in_grid` grids and `flow_order`

Six differently colored squares first arrange into 2×3 (row spacing 0.4, column spacing 0.8), then animate into 3×2 filled by column — where each color goes is the effect of `flow_order`.

```python
from real_time_manim import Scene, VGroup, Square, \
    RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class GridDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        colors = (RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE)   # six colors = the fill order
        cells = VGroup(*[Square(color=c, side_length=0.7) for c in colors])   # six squares
        cells.arrange_in_grid(rows=2, cols=3, buff=(0.4, 0.8))   # 2 rows 3 cols, row spacing 0.4, column spacing 0.8
        self.add(cells)   # add them to the scene
        win.play(FadeIn(cells), run_time=0.6)   # fade in the grid: red, orange, yellow in the first row
        win.play(cells.animate.arrange_in_grid(rows=3, cols=2, flow_order="dr"), run_time=0.7)   # 3 rows 2 cols, fill by column
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window
```

What this code does: six colored squares enter the group in the order "red, orange, yellow, green, blue, purple"; the first `arrange_in_grid(rows=2, cols=3, buff=(0.4, 0.8))` fills row-first with the default `flow_order="rd"` — red, orange, yellow in the first row; the second animates into `rows=3, cols=2, flow_order="dr"`, column-first and downward, so red and green are one column, orange and blue another, yellow and purple another. To check the fill order, watching where each color lands is the clearest way.

<video src="assets/RTM output/02b-Positioning-Advanced-grid.mp4" controls width="560"></video>

> Note:
>
> - `rows*cols` must fit all children, or it raises `ValueError` straight away.
> - When elements differ in size, fine-tune with `row_heights` / `col_widths` or `cell_alignment`, otherwise cells are sized by the largest element.
> - When `buff` is a tuple it is "(row spacing, col spacing)"; don't guess it as `(col, row)`.

### surround / replace

```python
def surround(mobject: Mobject, dim_to_match: int = 0, stretch: bool = False,
             buff: float = 0.25) -> Self
def replace(mobject: Mobject, dim_to_match: int = 0, stretch: bool = False) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | the target to enclose / refer to |
| `dim_to_match` | `int` | `0` | which dimension to match: `0` width, `1` height, `2` depth |
| `stretch` | `bool` | `False` | `False` scales uniformly to match; `True` stretches width and height independently (distorts) |
| `buff` | `float` | `0.25` | enclosure margin (`surround` only) |

> **Returns**: `self`. `surround` makes self enclose the target (same center, sized to the target plus margin along `dim_to_match`); `replace` makes self the same size and center as the target (often used as a backing panel).

#### Sample: `surround` a frame and `replace` a backing panel

A piece of text is first enclosed by a red frame with `surround`, then a blue square is stretched by `replace` into a same-sized translucent backing.

```python
from real_time_manim import Scene, Rectangle, Text, \
    RED, BLUE, YELLOW
from real_time_manim.vulkan_bind import MLWindow, Wait

class SurroundReplaceDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        txt = Text("target", font_size=36, color=YELLOW)   # the text being enclosed
        self.add(txt)   # add it to the scene
        frame = Rectangle(color=RED)   # an empty rectangle
        frame.surround(txt, buff=0.25)   # surround: enclose the text by width, margin 0.25
        self.add(frame)   # add it to the scene
        win.play(FadeIn(frame), run_time=0.5)   # fade in the frame
        panel = Rectangle(width=1.0, height=1.0, color=BLUE, fill_opacity=0.4)   # a small square
        panel.replace(txt, stretch=True)   # replace: same center, width and height stretched independently to match the text
        self.add(panel)   # add it to the scene
        win.play(FadeIn(panel), run_time=0.5)   # fade in the backing
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window
```

What this code does: after the yellow text `target` goes on screen, an empty red rectangle `surround(txt, buff=0.25)` becomes a frame enclosing the text (matching by width, uniform scaling by default); then a small blue square `replace(txt, stretch=True)` has its width and height stretched **separately** to match the text's bounding box, with the centers coinciding, becoming a translucent backing behind the text. Both methods "use someone else as a ruler to measure oneself".

<video src="assets/RTM output/02b-Positioning-Advanced-surround_replace.mp4" controls width="560"></video>

> Note:
>
> - With `stretch=False` (the default) the scaling is uniform, so `surround`ing a wide flat text gives a box much taller than the text; for a snug fit use `stretch=True` (the box distorts) or adjust with `dim_to_match=0` plus `buff`.
> - `replace` has no `buff`; for a backing panel a little larger, `replace` first and then `stretch_to_fit_width(width + 2*buff)`.

### put_start_and_end_on

```python
def put_start_and_end_on(start: Point3DLike, end: Point3DLike) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `start` | point | — | target start coordinate |
| `end` | point | — | target end coordinate |

> **Returns**: `self`. Internally it does a trio of "scale by length + rotate by the included angle + translate" to pin own start and end **exactly** onto the two points. For a closed path (start=end, such as `Circle`) it only translates to `start` and emits a warning — there is no direction to match.

#### Sample: pinning both ends with `put_start_and_end_on`

The two ends of a horizontal line are pinned exactly onto two red dots (scale + rotate + translate in one call).

```python
from real_time_manim import Scene, Line, Dot, \
    BLUE, RED, UP, DOWN, LEFT, RIGHT
from real_time_manim.vulkan_bind import MLWindow, Wait

class PutEndsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        line = Line(LEFT * 2, RIGHT * 2, color=BLUE)   # initially: a horizontal line of length 4
        p1 = Dot(color=RED, radius=0.1).move_to(LEFT * 3 + DOWN * 1.5)   # target start
        p2 = Dot(color=RED, radius=0.1).move_to(RIGHT * 1 + UP * 2)   # target end
        self.add(line, p1, p2)   # add them to the scene
        win.play(line.animate.put_start_and_end_on(p1.get_center(), p2.get_center()), run_time=0.7)   # scale + rotate + translate to pin both ends to the two points
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window
```

What this code does: a horizontal blue line of length 4, with two red dots marking the target start and end. `put_start_and_end_on(p1, p2)` does three things in one call: scales uniformly by "target length / current length", rotates about the start into the target direction, then translates so the start lands on p1 — when the animation ends the line's two ends sit exactly on the two red dots.

<video src="assets/RTM output/02b-Positioning-Advanced-put_ends.mp4" controls width="560"></video>

> Note: the order is "scale about the start → rotate about the start → translate", which is most effective for **path-like** objects (`Line`, `Arrow`, `Arc`); a closed path such as `Circle` has `get_start()==get_end()`, so it only translates and prints a `put_start_and_end_on has been called on a closed loop` warning; to resize a circle use `scale` / `surround`.

### shift_onto_screen / is_off_screen

```python
def shift_onto_screen(**kwargs: Any) -> Self
def is_off_screen() -> bool
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `**kwargs` | `Any` | — | forwarded to the internal `to_edge` (e.g. `buff=`); `is_off_screen` takes no arguments |

> **Returns**: `shift_onto_screen` returns `self`, `is_off_screen` returns `bool`. The former only pulls back **out-of-frame** edges (already-visible sides are untouched); the latter is `True` only when the object is **fully** off-frame — any visible sliver counts as `False`.

#### Sample: pulling it back on screen plus the check

The square is first moved far off-frame (`is_off_screen=True`), `shift_onto_screen` pulls it back inside the left edge, and the check result is printed again.

```python
from real_time_manim import Scene, Square, \
    RED, LEFT, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class OffScreenDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        sq = Square(color=RED, side_length=1.2)   # red square
        sq.shift(LEFT * 12)   # move it far off-frame
        print("is_off_screen =", sq.is_off_screen())   # True: fully off-frame
        self.add(sq)   # add it to the scene
        win.play(sq.animate.shift_onto_screen(buff=0.5), run_time=0.7)   # pull it back on screen, margin 0.5
        print("is_off_screen after pulling back =", sq.is_off_screen())   # False
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window
```

What this code does: the red square is first flung off-frame by `shift(LEFT * 12)` (at this point `is_off_screen = True` is printed and nothing is visible on screen); playing `shift_onto_screen(buff=0.5)` slides it back on screen — this method moves only the out-of-bounds edges, so the square stops with a margin of 0.5 from the left edge rather than jumping to the middle; after it is brought back, `is_off_screen = False` is printed again.

<video src="assets/RTM output/02b-Positioning-Advanced-off_screen.mp4" controls width="560"></video>

> Note:
>
> - `shift_onto_screen` is not a guarantee of "centered" or "fully visible" — it pulls back edge by edge **via edge midpoints**, so an oversized object may still have all four sides off-frame after being pulled back.
> - `is_off_screen` is likewise based on the four bounding-box edges.
> - They too refer to the frame (`config`), not the camera viewfinder.

### space_out_submobjects

```python
def space_out_submobjects(factor: float = 1.5, **kwargs: Any) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `factor` | `float` | `1.5` | spacing multiplier: `>1` spreads, `<1` tightens |
| `**kwargs` | `Any` | — | forwarded to the internal `scale` (e.g. `about_point=` sets the pivot for spreading) |

> **Returns**: `self`. The implementation is "scale the whole group by `factor` + scale each child by `1/factor`": child **positions** are scaled up while their **sizes** cancel out, so only the spacing changes, not the size.

#### Sample: `space_out_submobjects` spreading and tightening

Three squares almost touching are first spread 1.8× (size unchanged), then tightened back by 0.5×.

```python
from real_time_manim import Scene, VGroup, Square, \
    BLUE, RIGHT, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class SpaceOutDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        g = VGroup(*[Square(color=BLUE, side_length=0.7) for _ in range(3)])   # three squares
        g.arrange(RIGHT, buff=0.05)   # almost touching
        self.add(g)   # add it to the scene
        win.play(g.animate.space_out_submobjects(1.8), run_time=0.6)   # factor>1: only the spacing spreads, the squares don't grow
        win.play(g.animate.space_out_submobjects(0.5), run_time=0.6)   # factor<1: tighten
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window
```

What this code does: three blue squares next to one another first play `space_out_submobjects(1.8)` — with the whole group's center as the pivot, the child **positions** scale up 1.8× while their **sizes** cancel out exactly, so the squares spread apart without growing; then `factor=0.5` tightens them back. To use a corner as the pivot for spreading, pass `about_point=` and it is forwarded to the internal `scale`.

<video src="assets/RTM output/02b-Positioning-Advanced-space_out.mp4" controls width="560"></video>

> Note: the implementation scales the whole group up first and then scales each child back, so the **relative layout** between children is scaled uniformly by `factor` — spreading a row also scales up the column direction; moreover, the child's own scaling cancels only if both scalings use the same pivot, so watch the result if you add scale arguments other than `about_point`.

---

See also: [Positioning](02-Positioning.md) · [Scaling, Rotation and Stretching](04-Scaling-Rotation-and-Stretching.md)
