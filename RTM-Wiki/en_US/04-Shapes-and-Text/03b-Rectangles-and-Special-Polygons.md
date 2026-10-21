# Polygons and stars (2): rectangles and special polygons

Picking up from [Polygons and stars (1)](03-Polygons-and-Stars.md): the rectangle family, rounded corners, cut-outs, and convex hulls. Every sample changes each of the function's **fillable parameters** once, chained together in one video for comparison.

## Parameters

### `Rectangle`

```python
def __init__(self, color: ParsableManimColor = WHITE, height: float = 2.0, width: float = 4.0, grid_xstep: float | None = None, grid_ystep: float | None = None, mark_paths_closed: bool = True, close_new_points: bool = True, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | `ManimColor` | `WHITE` | colour. **Accepts** any colour (`BLUE`, `"#33AADD"`, (r,g,b)); the sample's first rectangle changes it |
| `height` | `float` | `2.0` | height. **Accepts** any positive number; the sample's second rectangle uses `height=1.6` |
| `width` | `float` | `4.0` | width. **Accepts** any positive number; the sample's second rectangle uses `width=2.4` |
| `grid_xstep` | `float \| None` | `None` | **do not change**: filling it in hangs a group of grid-line submobjects inside the rectangle (`submobjects` gains a layer, and afterwards `set_color` / `MoveToTarget` / `Create` all behave differently from a pure rectangle). A more controllable way to get a "rectangle with a grid" is `VGroup(rectangle, hand-drawn lines)`; the sample's third rectangle fills it in only to demonstrate the effect |
| `grid_ystep` | `float \| None` | `None` | **do not change**: same as above |
| `mark_paths_closed` | `bool` | `True` | **do not change**: path-closed flag; changing it affects the fill test |
| `close_new_points` | `bool` | `True` | **do not change**: whether new points close automatically |

#### Sample: changing the colour / the width and height / adding an internal grid

Three rectangles side by side: the default 4×2, explicit `width` / `height`, and an internal grid with `grid_xstep` / `grid_ystep`. The parameter values are printed on each caption.

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Rectangle, Square, RoundedRectangle, Cutout, ConvexHull, Circle,
    Triangle, Dot, VGroup, Text,
    BLUE, GREEN, TEAL, PURPLE, ORANGE, YELLOW, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class RectangleDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("03b-Rectangle", font_size=28, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— default 4x2 ——
        r1 = Rectangle(color=BLUE)   # the color parameter: WHITE by default
        r1.move_to([-4.4, 1.4, 0])   # default width=4.0 / height=2.0
        cap1 = Text("Rectangle()  4x2", font_size=19, color=GREY_B).move_to([-4.4, 0.1, 0])
        win.play(Create(r1), FadeIn(cap1), run_time=0.6)   # draw the default rectangle + caption

        # —— width / height given explicitly ——
        r2 = Rectangle(width=2.4, height=1.6, color=GREEN)   # the "width / height" parameters
        r2.move_to([0, 1.4, 0])   # narrow and short
        cap2 = Text("width=2.4 height=1.6", font_size=19, color=GREY_B).move_to([0, 0.1, 0])
        win.play(Create(r2), FadeIn(cap2), run_time=0.6)   # draw the custom size + caption

        # —— grid_xstep / grid_ystep: draw a grid inside the rectangle ——
        r3 = Rectangle(width=3.2, height=1.8, color=ORANGE,
                       grid_xstep=0.8, grid_ystep=0.6)   # the "grid_xstep / grid_ystep" parameters
        r3.move_to([4.4, 1.4, 0])   # the interior is cut into small cells
        cap3 = Text("grid_xstep=0.8 grid_ystep=0.6", font_size=19, color=GREY_B).move_to([4.4, 0.1, 0])
        win.play(Create(r3), FadeIn(cap3), run_time=0.6)   # draw the gridded rectangle + caption
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: Square —— side_length is readable and writable ============
```

What this code does: all three rectangles are drawn with `Create`, each with a caption line stating its parameter values. The first uses only `color` (the size takes the default 4×2); the second changes `width` / `height` explicitly to 2.4/1.6, so you can see at a glance that "the width and height are exactly these two numbers"; the third gives both `grid_xstep=0.8` and `grid_ystep=0.6`, so the rectangle gains an extra layer of grid submobjects inside (which is also why the table says not to change them). `mark_paths_closed` / `close_new_points` stay at their defaults.

<video src="assets/RTM output/03b-Rectangles-and-Special-Polygons-rectangle.mp4" controls width="560"></video>

> Note: `width` / `height` are only the construction-time size; to change the size afterwards use `scale()` / `stretch()`; only `grid_*step` hangs submobjects inside the rectangle, and `get_vertices()`, `Create` and `set_color` all act on those grid lines as well.

### `Square`

```python
def __init__(self, side_length: float = 2.0, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `side_length` | `float` | `2.0` | side length. Any positive number can be passed at construction; **it is also a readable and writable attribute** — writing `sq.side_length = 2.6` after construction rescales the shape to the new side length on the spot (through `scale()`, without rebuilding the object). The sample demonstrates both |

#### Sample: passing `side_length` at construction / changing `side_length` afterwards

One defaults to 2.0, one is given 1.2 at construction, and the third writes `side_length = 2.6` directly after it is drawn.

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Rectangle, Square, RoundedRectangle, Cutout, ConvexHull, Circle,
    Triangle, Dot, VGroup, Text,
    BLUE, GREEN, TEAL, PURPLE, ORANGE, YELLOW, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class SquareDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("03b-Square", font_size=28, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        sq1 = Square(color=BLUE, fill_opacity=0.5)   # default side_length=2.0
        sq1.move_to([-3.6, 0.4, 0])
        cap1 = Text("Square()  2.0", font_size=19, color=GREY_B).move_to([-3.6, -1.5, 0])
        win.play(Create(sq1), FadeIn(cap1), run_time=0.6)   # draw the default square + caption

        sq2 = Square(side_length=1.2, color=TEAL, fill_opacity=0.5)   # the "side_length" parameter
        sq2.move_to([0, 0.4, 0])
        cap2 = Text("side_length=1.2", font_size=19, color=GREY_B).move_to([0, -1.5, 0])
        win.play(Create(sq2), FadeIn(cap2), run_time=0.6)   # draw the small square + caption

        # —— side_length is a readable and writable attribute: assigning it changes the shape on the spot ——
        sq3 = Square(color=PURPLE, fill_opacity=0.5)
        sq3.move_to([4.0, 0.4, 0])
        cap3 = Text("sq.side_length = 2.6", font_size=19, color=GREY_B).move_to([4.0, -1.5, 0])
        win.play(Create(sq3), FadeIn(cap3), run_time=0.6)   # draw it at the default size first
        sq3.side_length = 2.6   # default 2.0; assigning changes the shape immediately (no rebuild)
        win.play(Wait(0.5))   # hold after assigning so the change is visible
        win.close()   # close the RTM window


# ===== Sample 3: RoundedRectangle —— corner radius (single / four different) ==
```

What this code does: the first two squares differ only in `side_length` (the default 2.0 and 1.2), and side by side you can see that the side length is exactly that one number. The third is drawn at the default size first, and after drawing, `sq3.side_length = 2.6` is written — in the video it grows on the spot, because the setter internally does `scale()` by `value / current side length`. So both routes, "give it at construction" and "change it afterwards", can be seen clearly in one video.

<video src="assets/RTM output/03b-Rectangles-and-Special-Polygons-square.mp4" controls width="560"></video>

> Note: `side_length` reads the **actual distance between two neighbouring points**, which stays correct after a 3D rotation; writing it is equivalent to `scale(new value / old value)`, so the fill and stroke width scale proportionally too.

### `RoundedRectangle`

```python
def __init__(self, corner_radius: float | list[float] = 0.5, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `corner_radius` | `float \| list[float]` | `0.5` | corner radius. **Accepts** a single number (all four corners the same radius) or a list of length 4 (in the order top-left → top-right → bottom-right → bottom-left, one per corner); the sample demonstrates both |
| `width` / `height` | `float` | `4.0` / `2.0` | inherited from `Rectangle`; the sample gives 3.4×1.6 explicitly |

#### Sample: one radius / a different radius per corner

The top is `corner_radius=0.5` (all four corners the same), the bottom is `corner_radius=[0.05, 0.35, 0.65, 1.0]` (progressively rounder from top-left to bottom-left).

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Rectangle, Square, RoundedRectangle, Cutout, ConvexHull, Circle,
    Triangle, Dot, VGroup, Text,
    BLUE, GREEN, TEAL, PURPLE, ORANGE, YELLOW, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class RoundedDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("03b-RoundedRectangle", font_size=28, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        rr1 = RoundedRectangle(corner_radius=0.5, width=3.4, height=1.6,
                               color=TEAL, fill_opacity=0.5)   # the "corner_radius=0.5" parameter
        rr1.move_to([0, 1.3, 0])
        cap1 = Text("RoundedRectangle(corner_radius=0.5)", font_size=19, color=GREY_B).move_to([0, 0.2, 0])
        win.play(Create(rr1), FadeIn(cap1), run_time=0.6)   # all four corners the same radius + caption

        rr2 = RoundedRectangle(corner_radius=[0.05, 0.35, 0.65, 1.0],
                               width=3.4, height=1.6,
                               color=PURPLE, fill_opacity=0.5)   # the "corner_radius=[four values]" parameter
        rr2.move_to([0, -1.6, 0])
        cap2 = Text("corner_radius=[0.05, 0.35, 0.65, 1.0]", font_size=19, color=GREY_B).move_to([0, -2.7, 0])
        win.play(Create(rr2), FadeIn(cap2), run_time=0.6)   # a different radius at each corner + caption
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 4: Cutout —— punching holes out of a main shape ==============
```

What this code does: two rounded rectangles of the same 3.4×1.6, whose only difference is how `corner_radius` is written. The top is given a single 0.5, so all four corners are rounded with the same radius; the bottom is given a four-element list and the corners go from 0.05 to 1.0, progressively rounder, showing at a glance that the list order is top-left → top-right → bottom-right → bottom-left.

The rounded corners are real arcs (built by Bezier tessellation, not chamfers); the `Rectangle(..., corner_radius=0.3)` spelling is also converted into this class.

<video src="assets/RTM output/03b-Rectangles-and-Special-Polygons-rounded.mp4" controls width="560"></video>

> Note: when the radius is larger than half the width / half the height, the arcs of two neighbouring corners eat into each other and the shape degenerates into a "capsule"; to see the difference between the four corners clearly, enlarge `width` / `height` and try again.

### `Cutout`

```python
def __init__(self, main_shape: VMobject, *mobjects: VMobject, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `main_shape` | `VMobject` | required | the main shape. **Accepts** any `VMobject`; the sample passes a filled rectangle |
| `*mobjects` | `VMobject...` | required | the shapes to cut out; **accepts** any number of them; the sample cuts a round hole + a triangular hole |

#### Sample: a round hole + a triangular hole

The main rectangle is drawn first, then swapped for `Cutout(main, Circle, Triangle)` — each of the three shapes keeps its own colour / stroke (the holes are given a stroke only).

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Rectangle, Square, RoundedRectangle, Cutout, ConvexHull, Circle,
    Triangle, Dot, VGroup, Text,
    BLUE, GREEN, TEAL, PURPLE, ORANGE, YELLOW, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class CutoutDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("03b-Cutout", font_size=28, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        main = Rectangle(width=5.0, height=2.6, color=TEAL,
                         fill_opacity=0.9).move_to([-2.4, -0.4, 0])   # the main shape (with fill)
        # the "main_shape / *mobjects" parameters: every shape after this is cut out of the main shape
        cut = Cutout(main,
                     Circle(radius=0.55, color=WHITE).move_to([-4.0, -0.4, 0]),   # cut a round hole
                     Triangle(color=WHITE).scale(0.7).move_to([-1.2, -0.4, 0]))   # and cut a triangular hole
        cap = Text("Cutout(main, Circle, Triangle)", font_size=19, color=GREY_B).move_to([-2.4, -2.1, 0])
        win.play(Create(main), run_time=0.5)   # draw the main shape first
        win.play(Create(cut), FadeIn(cap), run_time=0.8)   # swap in the holed shape + caption
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 5: ConvexHull —— the convex hull of a family of points =======
```

What this code does: the filled main rectangle is drawn first, then the second step `Create(cut)` swaps in `Cutout(main, circle, triangle)` — `main_shape` is the main shape, and every shape that follows is merged into the same fill as a **reverse subpath**. In the video you can see that after the swap the rectangle's interior gains two sets of strokes, for the circle and the triangle; the number of `*mobjects` is unlimited, and the sample gives two.

<video src="assets/RTM output/03b-Rectangles-and-Special-Polygons-cutout.mp4" controls width="560"></video>

> Note: whether a hole is "hollowed out" is decided only by the fill rule, not by "where the shape is placed" — when the hole shapes are given a stroke only (`fill_opacity=0`), the main shape's fill covers the interior of the holes and it only looks like "a circle was drawn"; to make the holes actually show the background, turn the holes' `fill_opacity` on as well, or switch the whole thing to `Difference` (see [Boolean operations](05-Boolean-Operations.md)).

### `ConvexHull`

```python
def __init__(self, *points: Point3DLike, tolerance: float = 1e-05, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*points` | `array-like...` | required | the input point set. **Accepts** any number of points (lists, arrays and `Dot`s can all be mixed in); the order of the points does not matter, and interior points get dropped |
| `tolerance` | `float` | `1e-05` | **do not change**: the tolerance for the collinearity test; raising it may treat nearly-collinear points as one edge |

#### Sample: the convex hull of seven scattered points

First the seven points are drawn as yellow dots, then the minimal convex polygon from `ConvexHull(*pts)` (green, semi-transparent) is laid over them.

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Rectangle, Square, RoundedRectangle, Cutout, ConvexHull, Circle,
    Triangle, Dot, VGroup, Text,
    BLUE, GREEN, TEAL, PURPLE, ORANGE, YELLOW, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class ConvexHullDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("03b-ConvexHull", font_size=28, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        pts = [[-4.6, -1.2, 0], [-3.2, 1.4, 0], [-1.6, 0.2, 0], [-2.2, -1.6, 0],
               [-0.6, 1.0, 0], [0.4, -0.8, 0], [-1.0, 1.8, 0]]   # seven irregular points
        dots = VGroup(*[Dot(p, radius=0.07, color=YELLOW) for p in pts])   # draw the points first
        hull = ConvexHull(*pts, color=GREEN, fill_opacity=0.4)   # the "*points / tolerance" parameters
        cap = Text("ConvexHull(*points, tolerance=1e-05)", font_size=19, color=GREY_B).move_to([-2.2, -2.7, 0])
        win.play(FadeIn(dots), run_time=0.5)   # the scattered points
        win.play(FadeIn(hull), FadeIn(cap), run_time=0.8)   # the convex hull + caption
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window
```

What this code does: `pts` is seven irregular scattered points; `FadeIn(dots)` draws the points first, then `FadeIn(hull)` lays `ConvexHull(*pts)` over them — the green polygon wraps all the points exactly: the five outer points become vertices and the two in the middle are dropped inside. The order of the point set does not matter, and `tolerance` stays at its default.

<video src="assets/RTM output/03b-Rectangles-and-Special-Polygons-convexhull.mp4" controls width="560"></video>

> Note: give at least 3 points, fewer degenerates into a line segment / point; `tolerance` is the collinearity tolerance, so do not touch it unless the point count is huge and you have checked by hand.

---

See also: [Polygons and stars (1)](03-Polygons-and-Stars.md) · [Boolean operations](05-Boolean-Operations.md) · [VMobject styles](07-VMobject-Styles.md)
