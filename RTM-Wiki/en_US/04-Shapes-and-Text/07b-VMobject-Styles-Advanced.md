# VMobject styles (2): opacity, sheen and path handling

Picking up from [VMobject styles (1)](07-VMobject-Styles.md): the remaining `VMobject` style methods — opacity, sheen gradients, path smoothing/trimming, end-cap styles and so on. Each method gets one sample, and each sample changes all of that method's **fillable parameters** once.

## Parameters

### `VMobject.set_opacity`

```python
def set_opacity(self, opacity: float, family: bool = True) -> Self:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `opacity` | `float` | required | 0 to 1. **Accepts** any number from 0 to 1; it changes fill and stroke at the same time (the sample compares 0.25 / 0.6 / 1.0) |
| `family` | `bool` | `True` | whether to change submobjects too. With `True` the container and its submobjects all go down; with `False` only the container itself changes and the submobjects keep their own opacity (the sample compares the two side by side) |

#### Sample: three opacity levels + the two values of `family`

```python
import os
import subprocess
import sys
import numpy as np
from real_time_manim import (
    Scene, Square, Circle, Polygon, Line, Dot, Triangle, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class OpacityDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("07b-set_opacity", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— three opacity levels: 0.25 / 0.6 / 1.0 (1.0 if you do not call it) ——
        for i, op in enumerate([0.25, 0.6, 1.0]):
            sq = Square(side_length=1.3, color=BLUE).set_fill(BLUE, 0.9)
            sq.move_to([-4.0 + i * 1.8, 1.3, 0])
            sq.set_opacity(op)   # the "opacity" parameter: fill and stroke change together
            cap = Text("opacity=%.2f" % op, font_size=18, color=GREY_B).next_to(sq, DOWN, buff=0.2)
            win.play(Create(sq), FadeIn(cap), run_time=0.45)   # draw one by one + caption

        # —— family: on the same VGroup, True changes the submobjects too, False changes only the container ——
        g1 = VGroup(Square(side_length=0.9, color=GREEN).set_fill(GREEN, 0.9),
                    Circle(radius=0.5, color=GREEN).set_fill(GREEN, 0.9))
        g1.arrange(RIGHT, buff=0.3).move_to([-2.6, -1.4, 0])
        g1.set_opacity(0.3, family=True)   # the "family=True" parameter: container and submobjects go down together
        cap1 = Text("family=True", font_size=18, color=GREY_B).next_to(g1, DOWN, buff=0.2)
        win.play(FadeIn(g1), FadeIn(cap1), run_time=0.5)   # both submobjects fade

        g2 = VGroup(Square(side_length=0.9, color=ORANGE).set_fill(ORANGE, 0.9),
                    Circle(radius=0.5, color=ORANGE).set_fill(ORANGE, 0.9))
        g2.arrange(RIGHT, buff=0.3).move_to([2.6, -1.4, 0])
        g2.set_opacity(0.3, family=False)   # the "family=False" parameter: only the container changes
        cap2 = Text("family=False", font_size=18, color=GREY_B).next_to(g2, DOWN, buff=0.2)
        win.play(FadeIn(g2), FadeIn(cap2), run_time=0.5)   # the submobjects keep their own 0.9
        win.play(Wait(0.5))   # hold to compare the two groups
        win.close()   # close the RTM window


# ===== Sample 2: set_sheen / set_sheen_direction —— the sheen gradient =======
```

What this code does: the three squares in the first row get `opacity` 0.25 / 0.6 / 1.0, so the further right the more solid.

The two `VGroup`s below (a square + a circle) both use 0.3, and the only difference is `family`: on the left `True` fades the submobjects too; on the right `False` changes only the container itself, and the two submobjects keep their own 0.9, so they still look solid.

<video src="assets/RTM output/07b-VMobject-Styles-Advanced-opacity.mp4" controls width="560"></video>

> Note: `set_opacity` changes fill and stroke **at the same time**, which is what distinguishes it from `set_fill(BLUE, 0.3)`. On a leaf object `family` makes no visible difference; only on a container (`VGroup`/`Text`) can the two values be told apart.

### `VMobject.set_sheen`

```python
def set_sheen(self, factor: float, direction: Vector3DLike | None = None, family: bool = True) -> Self:
def set_sheen_direction(self, direction: Vector3DLike, family: bool = True) -> Self:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `factor` | `float` | required | sheen strength. 0 turns it off (back to a flat colour); 0.2 to 1.5 is the common range; the sample uses 0.0 / 0.6 / 1.5 |
| `direction` | `array-like \| None` | `None` | gradient direction; when omitted it reuses the object's existing `sheen_direction`; the sample uses `UP` / `RIGHT` once each |
| `family` | `bool` | `True` | whether to apply it to submobjects |
| `set_sheen_direction(direction, family=True)` | method | — | change only the direction, reusing the last `factor` for the strength (the sample calls `set_sheen(1.0, UP)` first and then changes the direction to `DOWN`) |

#### Sample: three strength levels + two directions + changing the direction on its own

```python
import os
import subprocess
import sys
import numpy as np
from real_time_manim import (
    Scene, Square, Circle, Polygon, Line, Dot, Triangle, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class SheenDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("07b-set_sheen", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— three levels of factor ——
        for i, f in enumerate([0.0, 0.6, 1.5]):
            sq = Square(side_length=1.2, color=BLUE).set_fill(BLUE, 1.0)
            sq.move_to([-4.0 + i * 1.7, 1.3, 0])
            sq.set_sheen(f, direction=UP)   # the "factor / direction=UP" parameters
            cap = Text("factor=%.1f" % f, font_size=18, color=GREY_B).next_to(sq, DOWN, buff=0.2)
            win.play(Create(sq), FadeIn(cap), run_time=0.45)   # 0 turns it off / 0.6 / 1.5

        # —— direction switched to RIGHT, so the sheen goes from left to right ——
        sq2 = Square(side_length=1.2, color=TEAL).set_fill(TEAL, 1.0).move_to([1.4, -1.2, 0])
        sq2.set_sheen(1.0, direction=RIGHT)   # the "direction=RIGHT" parameter
        cap2 = Text("direction=RIGHT", font_size=18, color=GREY_B).next_to(sq2, DOWN, buff=0.2)
        win.play(Create(sq2), FadeIn(cap2), run_time=0.5)

        # —— set_sheen_direction: change only the direction, reusing the last factor for the strength ——
        sq3 = Square(side_length=1.2, color=PURPLE).set_fill(PURPLE, 1.0).move_to([4.4, -1.2, 0])
        sq3.set_sheen(1.0, direction=UP)   # use UP first
        sq3.set_sheen_direction(DOWN)   # then change only the direction (family defaults to True)
        cap3 = Text("set_sheen_direction(DOWN)", font_size=18, color=GREY_B).next_to(sq3, DOWN, buff=0.2)
        win.play(Create(sq3), FadeIn(cap3), run_time=0.5)
        win.play(Wait(0.5))   # hold to see the gradient direction
        win.close()   # close the RTM window


# ===== Sample 3: make_smooth —— turning a polyline into a smooth curve ======
```

What this code does: the three blue squares above differ only in `factor` — 0 is a flat colour, 0.6 has a faint highlight, and 1.5 turns almost into a white-to-blue gradient.

The two below demonstrate the direction on their own: the teal square with `direction=RIGHT` becomes a left-to-right gradient; the purple square calls `set_sheen(1.0, UP)` first and then flips the direction with `set_sheen_direction(DOWN)`, without passing the strength again.

<video src="assets/RTM output/07b-VMobject-Styles-Advanced-sheen.mp4" controls width="560"></video>

> Note: the sheen is a gradient of the **fill**; the stroke does not take part. `direction` gives the gradient's heading (the highlight is at the **opposite** end), so `UP` looks like "bright at the top, dark towards the bottom". Multi-stop custom gradient colours can be drawn too (the engine takes the first and last stops and runs a native linear gradient).

### `VMobject.make_smooth`

```python
def make_smooth(self) -> Self:
```

No parameters; call it directly on an object. It turns the current path's corner points into smooth anchors (equivalent to `change_anchor_mode("smooth")`), for "turning a polyline into a curve".

#### Sample: the same polyline, untouched and smoothed, side by side

```python
import os
import subprocess
import sys
import numpy as np
from real_time_manim import (
    Scene, Square, Circle, Polygon, Line, Dot, Triangle, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class MakeSmoothDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("07b-make_smooth", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        verts = [[-3.2, 1.0, 0], [-1.6, -0.6, 0], [-0.2, 1.2, 0], [1.4, -0.4, 0]]   # the polyline's vertices
        raw = Polygon(*verts, color=GREY_B, stroke_width=5)   # untouched (with corners)
        smoothed = Polygon(*verts, color=GREEN, stroke_width=5)   # the copy to be smoothed
        smoothed.make_smooth()   # turn the corner points into smooth anchors: the polyline becomes a curve
        raw.shift(DOWN * 1.4)   # above: untouched
        smoothed.shift(DOWN * 1.4)
        cap1 = Text("jagged (raw)", font_size=20, color=GREY_B).next_to(raw, UP, buff=0.25)
        cap2 = Text("make_smooth()", font_size=20, color=GREEN).next_to(smoothed, UP, buff=0.25)
        win.play(Create(raw), FadeIn(cap1), run_time=0.6)   # look at the polyline first
        win.play(Create(smoothed), FadeIn(cap2), run_time=0.6)   # then the same path after smoothing
        win.play(Wait(0.5))   # hold to compare
        win.close()   # close the RTM window


# ===== Sample 4: make_jagged —— turning a smooth curve back into a polyline ===
```

What this code does: the same set of vertices is drawn twice — the grey one keeps its corners and the green one calls `make_smooth()`. The two paths are drawn one after the other, and the green one bulges into arcs at every original corner: that is "turning a polyline into a curve"; the number and position of the vertices are unchanged, and only the anchor mode differs.

<video src="assets/RTM output/07b-VMobject-Styles-Advanced-smooth.mp4" controls width="560"></video>

> Note: `make_smooth()` changes the object **in place** (it returns `self`, so it is chainable); to keep the original polyline, do `poly.copy().make_smooth()`.

### `VMobject.make_jagged`

```python
def make_jagged(self) -> Self:
```

No parameters. The inverse of `make_smooth()`: it turns smooth anchors back into corners (equivalent to `change_anchor_mode("jagged")`).

#### Sample: the same circle, untouched and in its "polyline version"

```python
import os
import subprocess
import sys
import numpy as np
from real_time_manim import (
    Scene, Square, Circle, Polygon, Line, Dot, Triangle, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class MakeJaggedDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("07b-make_jagged", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        circle = Circle(radius=1.2, color=BLUE).set_fill(BLUE, 0.3)   # a circle is smooth to begin with
        circle.move_to(LEFT * 2.2 + DOWN * 0.6)
        jagged = Circle(radius=1.2, color=ORANGE).set_fill(ORANGE, 0.3)
        jagged.make_jagged()   # turn the smooth anchors back into corners: the circle becomes a polygon
        jagged.move_to(RIGHT * 2.2 + DOWN * 0.6)
        cap1 = Text("Circle (smooth)", font_size=20, color=BLUE).next_to(circle, UP, buff=0.25)
        cap2 = Text("make_jagged()", font_size=20, color=ORANGE).next_to(jagged, UP, buff=0.25)
        win.play(Create(circle), FadeIn(cap1), run_time=0.6)   # look at the circle first
        win.play(Create(jagged), FadeIn(cap2), run_time=0.6)   # then the same-radius "polyline circle"
        win.play(Wait(0.5))   # hold to compare
        win.close()   # close the RTM window


# ===== Sample 5: pointwise_become_partial —— trimming a stretch along a path ===
```

What this code does: two circles of the same radius; after the right-hand one calls `make_jagged()` its outline becomes a polygon (the point count is unchanged and the segments no longer transition smoothly), which immediately shows that it switches the anchor mode on the same set of points rather than really rebuilding a polygon.

<video src="assets/RTM output/07b-VMobject-Styles-Advanced-jagged.mp4" controls width="560"></video>

> Note: after `make_jagged` the object is still a VMobject and still fillable, only its outline is no longer a curve; to restore the curve, call `make_smooth()` again.

### `VMobject.pointwise_become_partial`

```python
def pointwise_become_partial(self, vmobject: VMobject, a: float, b: float) -> Self:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `vmobject` | `VMobject` | required | the source object (its path is read) |
| `a` | `float` | required | start ratio 0 to 1 (along the path) |
| `b` | `float` | required | end ratio 0 to 1; `[0, 1]` is the whole path |

#### Sample: four quarter segments + the whole path

```python
import os
import subprocess
import sys
import numpy as np
from real_time_manim import (
    Scene, Square, Circle, Polygon, Line, Dot, Triangle, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class PartialDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("07b-pointwise_become_partial", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— the same circle, trimming one [a, b] stretch at a time, four times ——
        spans = [(0.0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.0)]   # the "a / b" parameters
        for i, (a, b) in enumerate(spans):
            src = Circle(radius=0.9, color=TEAL, stroke_width=6)   # the source object
            part = Circle(radius=0.9)   # the object that receives the trimmed result
            part.pointwise_become_partial(src, a, b)   # the "vmobject / a / b" parameters
            part.set_stroke(TEAL, 6)
            part.move_to([-4.0 + i * 2.2, 1.2, 0])
            cap = Text("[%.2f, %.2f]" % (a, b), font_size=18, color=GREY_B).next_to(part, DOWN, buff=0.25)
            win.play(Create(part), FadeIn(cap), run_time=0.45)   # four quarter arcs

        # —— [0, 1] is the whole path (the same length as the source object) ——
        src = Circle(radius=0.9, color=GOLD, stroke_width=6)
        whole = Circle(radius=0.9)
        whole.pointwise_become_partial(src, 0, 1)   # a=0, b=1: the whole path
        whole.set_stroke(GOLD, 6).move_to([-1.0, -1.4, 0])
        cap = Text("[0, 1] = whole path", font_size=18, color=GREY_B).next_to(whole, DOWN, buff=0.25)
        win.play(Create(whole), FadeIn(cap), run_time=0.5)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 6: get_stroke_width —— reading the current stroke width =======
```

What this code does: a circle of the same radius is the source, and four "receiving objects" each call `pointwise_become_partial(src, a, b)`, so each gets only a quarter arc, with its own `[a, b]` on the caption. The last one, `[0, 1]`, gets the whole path, with an arc length identical to the source object — this is the underlying method behind "reveal only a stretch" effects such as `ShowPassingFlash`.

<video src="assets/RTM output/07b-VMobject-Styles-Advanced-partial.mp4" controls width="560"></video>

> Note: `a > b` does not raise, but what you get is a reversed (empty / backwards) path; `a == b` degenerates to a point. When actually doing a sweep effect you usually keep `b - a` fixed and slide that window along.

### `VMobject.get_stroke_width`

```python
def get_stroke_width(self, background: bool = False) -> float:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `background` | `bool` | `False` | `False` reads the current stroke width; `True` reads the background stroke width (0 if it has never been set) |

Returns a `float`.

#### Sample: read the stroke width → change it → read it again

```python
import os
import subprocess
import sys
import numpy as np
from real_time_manim import (
    Scene, Square, Circle, Polygon, Line, Dot, Triangle, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class GetWidthDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("07b-get_stroke_width", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        ln = Line([-4.4, 1.0, 0], [-0.4, 1.0, 0], color=BLUE, stroke_width=4)   # the initial stroke width is 4
        info = Text("get_stroke_width() = %.1f" % ln.get_stroke_width(), font_size=24, color=WHITE)
        info.next_to(ln, DOWN, buff=0.4)
        win.play(Create(ln), FadeIn(info), run_time=0.5)   # the readout is 4.0

        ln.set_stroke(width=14)   # change the stroke width
        info.become(Text("after set_stroke(width=14) = %.1f" % ln.get_stroke_width(),
                         font_size=24, color=WHITE).next_to(ln, DOWN, buff=0.4))
        win.play(Create(ln), run_time=0.4)   # the line gets thicker
        win.play(FadeIn(info), run_time=0.3)   # the readout becomes 14.0

        # —— background=True: it reads the "background stroke width" (0 by default, and 0 if it has never been set) ——
        info2 = Text("get_stroke_width(background=True) = %.1f" % ln.get_stroke_width(background=True),
                     font_size=24, color=ORANGE).next_to(info, DOWN, buff=0.25)
        win.play(FadeIn(info2), run_time=0.4)   # the "background=True" parameter
        win.play(Wait(0.5))   # hold to see the readouts
        win.close()   # close the RTM window


# ===== Sample 7: set_cap_style —— the three line end-cap styles ============
```

What this code does: first a line is drawn with `stroke_width=4` and the `get_stroke_width()` readout is put on the caption (4.0); then `set_stroke(width=14)` thickens the line and the same readout becomes 14.0; the last line shows the `background=True` readout — that is the "background stroke" channel, which this object has never set, so it is 0.0.

<video src="assets/RTM output/07b-VMobject-Styles-Advanced-strokewidth.mp4" controls width="560"></video>

> Note: the readout is exactly the value you gave at construction / in `set_stroke` (it does not change with `scale()`), so when using it to compensate for stroke width you must multiply by the scale factor yourself.

### `VMobject.set_cap_style`

```python
def set_cap_style(self, cap_style: CapStyleType) -> Self:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `cap_style` | `CapStyleType` | required | the line end-cap style. Accepted values are `CapStyleType.ROUND` (round) / `BUTT` (flat, stopping exactly at the endpoint) / `SQUARE` (square, extending half the stroke width past each end) / `AUTO` (follow the stroke default) |

#### Sample: three end-cap styles, only visible on a thick line

```python
import os
import subprocess
import sys
import numpy as np
from real_time_manim import (
    Scene, Square, Circle, Polygon, Line, Dot, Triangle, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class CapStyleDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("07b-set_cap_style", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        from manim import CapStyleType   # the enum of the three end-cap styles
        styles = [("ROUND", CapStyleType.ROUND), ("BUTT", CapStyleType.BUTT),
                  ("SQUARE", CapStyleType.SQUARE)]   # the "cap_style" parameter
        for i, (name, style) in enumerate(styles):
            ln = Line([-4.4, 1.4 - i * 1.5, 0], [-1.2, 1.4 - i * 1.5, 0],
                      color=TEAL, stroke_width=40)   # only a thick line makes the end caps visible
            ln.set_cap_style(style)   # the "cap_style=CapStyleType.%s" parameter % name
            cap = Text("CapStyleType.%s" % name, font_size=20, color=GREY_B).next_to(ln, RIGHT, buff=0.4)
            win.play(Create(ln), FadeIn(cap), run_time=0.5)   # the three end caps appear in turn
        win.play(Wait(0.5))   # hold to compare
        win.close()   # close the RTM window


# ===== Sample 8: change_anchor_mode —— the two modes, smooth / jagged ======
```

What this code does: three lines of the same length and thickness (`stroke_width=40`) are set to `ROUND` / `BUTT` / `SQUARE` from top to bottom: the round cap bulges into a semicircle at both ends, the flat cap stops exactly at the endpoint, and the square cap extends half the stroke width past each side (so it looks the longest). With a thin line these three are almost indistinguishable, so a thick line is needed to demonstrate them.

<video src="assets/RTM output/07b-VMobject-Styles-Advanced-capstyle.mp4" controls width="560"></video>

> Note: it is a **stroke** property and only affects the two ends of an open path; a closed path (a circle, a rectangle) has no endpoints, so setting it makes no visible difference.

### `VMobject.change_anchor_mode`

```python
def change_anchor_mode(self, mode: Literal["jagged", "smooth"]) -> Self:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mode` | `str` | required | accepts only the two values `"smooth"` (smooth) and `"jagged"` (corner), which are exactly the underlying switch behind `make_smooth`/`make_jagged` |

#### Sample: the same set of vertices in smooth mode and in corner mode

```python
import os
import subprocess
import sys
import numpy as np
from real_time_manim import (
    Scene, Square, Circle, Polygon, Line, Dot, Triangle, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class AnchorModeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("07b-change_anchor_mode", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        verts = [[-3.0, 0.8, 0], [-1.4, -0.8, 0], [0.2, 1.0, 0], [1.8, -0.6, 0]]
        smooth = Polygon(*verts, color=GREEN, stroke_width=5)
        smooth.change_anchor_mode("smooth")   # the "mode="smooth"" parameter
        smooth.shift(UP * 0.9 + LEFT * 1.4)
        jagged = Polygon(*verts, color=ORANGE, stroke_width=5)
        jagged.change_anchor_mode("jagged")   # the "mode="jagged"" parameter
        jagged.shift(DOWN * 1.2 + LEFT * 1.4)
        cap1 = Text('mode="smooth"', font_size=20, color=GREEN).next_to(smooth, RIGHT, buff=0.4)
        cap2 = Text('mode="jagged"', font_size=20, color=ORANGE).next_to(jagged, RIGHT, buff=0.4)
        win.play(Create(smooth), FadeIn(cap1), run_time=0.6)   # the smooth mode
        win.play(Create(jagged), FadeIn(cap2), run_time=0.6)   # the corner mode
        win.play(Wait(0.5))   # hold to compare
        win.close()   # close the RTM window


# ===== Sample 9: apply_function —— custom deformation and the about point ===
```

What this code does: the same set of vertices is drawn twice, one with `change_anchor_mode("smooth")` and one with `"jagged"`, the two modes one above the other — the green one is curved at the corners and the orange one has hard corners; `make_smooth()` / `make_jagged()` are just wrappers around these two values.

<video src="assets/RTM output/07b-VMobject-Styles-Advanced-anchor.mp4" controls width="560"></video>

> Note: `mode` accepts only the two strings `"smooth"`/`"jagged"` (the `"corners"` written in early docs is wrong and raises `ValueError`).

### `VMobject.apply_function` (`about_point` / `about_edge` have no effect upstream)

```python
def apply_function(self, function: MappingFunction, *, about_point: Point3DLike | None = None, about_edge: Vector3DLike | None = None) -> Self:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `function` | `callable` | required | a function that takes a point and returns a new point; **accepts** any per-point mapping (the sample gives four: a wave, a scale, a scale + translate, and squashing only y) |
| `about_point` | `array-like \| None` | `None` | **do not count on it**: ManimCE 0.21's `apply_function` does not read this parameter — passing it or not gives exactly the same result (in testing, all four variants end up centred at the same place), while RTM transforms about the reference point, so **the two engines draw differently**, which is why the sample does not demonstrate it |
| `about_edge` | `array-like \| None` | `None` | same as above (also ignored upstream) |

#### Sample: four per-point mappings

```python
import os
import subprocess
import sys
import numpy as np
from real_time_manim import (
    Scene, Square, Circle, Polygon, Line, Dot, Triangle, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class ApplyFunctionDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("07b-apply_function", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— per-point distortion: a sine wave changing x ——
        wave = lambda p: p + 0.35 * np.sin(p[1] * PI) * RIGHT   # the "function" parameter: change x point by point
        a = Square(side_length=1.6, color=BLUE).set_fill(BLUE, 0.6).move_to([-3.6, 1.2, 0])
        a.apply_function(wave)   # the "function" parameter
        cap1 = Text("apply_function(wave)", font_size=18, color=GREY_B).next_to(a, DOWN, buff=0.25)
        win.play(Create(a), FadeIn(cap1), run_time=0.5)   # the square is twisted into a wavy edge

        # —— scale everything up: p * 1.5 ——
        b = Square(side_length=1.2, color=GREEN).set_fill(GREEN, 0.6).move_to([1.2, 1.2, 0])
        b.apply_function(lambda p: p * 1.5)   # the "function" parameter: a uniform scale
        cap2 = Text("function = p * 1.5", font_size=18, color=GREY_B).next_to(b, DOWN, buff=0.25)
        win.play(Create(b), FadeIn(cap2), run_time=0.5)   # the whole square gets bigger

        # —— scale + translate: p * 0.8 + UP * 0.4 ——
        c = Square(side_length=1.2, color=RED).set_fill(RED, 0.6).move_to([1.2, -1.4, 0])
        c.apply_function(lambda p: p * 0.8 + UP * 0.4)   # the "function" parameter: scale and then shift the whole thing up
        cap3 = Text("function = p * 0.8 + UP * 0.4", font_size=18, color=GREY_B).next_to(c, DOWN, buff=0.25)
        win.play(Create(c), FadeIn(cap3), run_time=0.5)   # shrunk and moved up

        # —— change only one coordinate: squash y ——
        d = Square(side_length=1.2, color=PURPLE).set_fill(PURPLE, 0.6).move_to([4.2, -1.4, 0])
        d.apply_function(lambda p: p * [1.0, 0.5, 1.0])   # the "function" parameter: squash y only
        cap4 = Text("function = p * [1, 0.5, 1]", font_size=18, color=GREY_B).next_to(d, DOWN, buff=0.25)
        win.play(Create(d), FadeIn(cap4), run_time=0.5)   # the square is squashed
        win.play(Wait(0.5))   # hold to compare
        win.close()   # close the RTM window
```

What this code does: each of the four squares is given one `function`.

- The sine wave twists the vertical edges into a wave;
- `p * 1.5` scales everything up;
- `p * 0.8 + UP * 0.4` shrinks it and moves it up;
- `p * [1, 0.5, 1]` squashes only y to half.

All four write the new coordinates point by point, so the square genuinely deforms (it is not a whole-object translation), and `function` must return three numbers `[x, y, z]`.

<video src="assets/RTM output/07b-VMobject-Styles-Advanced-applyfunc.mp4" controls width="560"></video>

> Note: `function` receives **absolute coordinates** (not coordinates relative to the object's centre), so `p * 1.5` pushes the object away from the origin — to scale it in place you must write `center + (p - center) * 1.5` yourself (compute `center` first and store it in a variable).

---

See also: [VMobject styles (1)](07-VMobject-Styles.md) · [Basic shapes](01-Basic-Shapes.md) · [Lines and arrows](02-Lines-and-Arrows.md)
