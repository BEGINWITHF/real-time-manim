# Angles and callout boxes (1): angles and highlight boxes

`Angle`/`RightAngle` live in `line.py`, the callout-box classes in `shape_matchers.py`. Every sample changes each of the function's **fillable parameters** once, chained together in one video for comparison.

## Parameters

### `Angle`

```python
def __init__(self, line1: Line, line2: Line, radius: float | None = None, quadrant: AngleQuadrant = (1, 1), other_angle: bool = False, dot: bool = False, dot_radius: float | None = None, dot_distance: float = 0.55, dot_color: ParsableManimColor = WHITE, elbow: bool = False, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `line1` | `Line` | required | the first side. **Accepts** any `Line`/`Arrow` (in the sample both sides start from the same point) |
| `line2` | `Line` | required | the second side. One object can only be used to mark one angle; to mark two angles, pass two copies |
| `radius` | `float \| None` | `None` | radius of the marking arc. **Accepts** any positive number; when omitted it is derived from the two sides (the sample uses 0.45 to 1.5 across three cases) |
| `quadrant` | `tuple[int, int]` | `(1, 1)` | pick one of four quadrants: `(1,1)` / `(-1,1)` / `(1,-1)` / `(-1,-1)`; the sample draws all four |
| `other_angle` | `bool` | `False` | draw the other side (the reflex angle). The sample gives the big red arc for `True` |
| `dot` | `bool` | `False` | add a dot inside the arc (to indicate the "size of the angle") |
| `dot_radius` | `float \| None` | `None` | dot radius; when omitted it is 1/10 of the arc radius |
| `dot_distance` | `float` | `0.55` | relative dot position: 0 at the vertex, 1 on the arc |
| `dot_color` | `ManimColor` | `WHITE` | dot colour (the sample uses a yellow dot) |
| `elbow` | `bool` | `False` | use a right-angle elbow instead of an arc (the easiest way to draw a right angle) |
| `get_value(degrees=False)` | method | — | **do not use**: an upstream bug in ManimCE 0.21 — `Angle` has no `angle_value` attribute, so both engines crash. To read the angle, use the difference of the two sides' `get_angle()` (which is exactly what the sample's last block does) |

#### Sample: radius / four quadrants / reflex angle / dot / right-angle elbow

Four `quadrant` values in one row, then `other_angle=True`, the `dot` family, and `elbow=True` in turn, each cell with a parameter caption.

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Line, Arrow, Dot, Square, Circle, Triangle, Text, VGroup,
    Angle, RightAngle, SurroundingRectangle, BackgroundRectangle, Cross, Underline,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class AngleDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("04-Angle", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— four quadrant values: the same angle, the marking arc drawn in a different quadrant ——
        quads = [(1, 1), (-1, 1), (1, -1), (-1, -1)]   # the "quadrant" parameter
        for i, q in enumerate(quads):
            l1 = Line(ORIGIN, RIGHT * 1.6)   # the "line1" parameter
            l2 = Line(ORIGIN, UP * 1.6)   # the "line2" parameter
            ang = Angle(l1, l2, radius=0.45, quadrant=q, color=ORANGE)   # the "radius / quadrant" parameters
            grp = VGroup(l1, l2, ang).move_to([-4.3 + i * 2.6, 1.5, 0])
            cap = Text("quadrant=%s" % (q,), font_size=18, color=GREY_B).next_to(grp, DOWN, buff=0.25)
            win.play(Create(grp), FadeIn(cap), run_time=0.5)   # draw the angles one by one + quadrant captions

        # —— other_angle (the reflex angle) + the dot family: add a dot inside the arc and change its radius/position/colour ——
        l1 = Line(ORIGIN, RIGHT * 1.6)
        l2 = Line(ORIGIN, UP * 1.6)
        big = Angle(l1, l2, radius=1.5, other_angle=True, color=RED)   # the "other_angle=True" parameter
        grp = VGroup(l1, l2, big).move_to([-1.4, -1.6, 0])
        cap = Text("other_angle=True", font_size=18, color=GREY_B).next_to(grp, DOWN, buff=0.25)
        win.play(Create(grp), FadeIn(cap), run_time=0.5)   # reflex angle + caption

        l1b = Line(ORIGIN, RIGHT * 1.6)   # another copy of the second side (one object can only mark one angle)
        l2b = Line(ORIGIN, UP * 1.6)
        marked = Angle(l1b, l2b, radius=1.0, dot=True, dot_radius=0.12,
                       dot_distance=0.75, dot_color=YELLOW, color=TEAL)   # the "dot / dot_radius / dot_distance / dot_color" parameters
        grp2 = VGroup(l1b, l2b, marked).move_to([1.6, -1.6, 0])
        cap2 = Text("dot=True dot_distance=0.75", font_size=18, color=GREY_B).next_to(grp2, DOWN, buff=0.25)
        win.play(Create(grp2), FadeIn(cap2), run_time=0.5)   # with a dot + caption

        # —— elbow=True: use a right-angle elbow instead of an arc; get_value() reads out the angle value ——
        l1c = Line(ORIGIN, RIGHT * 1.6)
        l2c = Line(ORIGIN, UP * 1.6)
        elbow = Angle(l1c, l2c, radius=0.6, elbow=True, color=PURPLE)   # the "elbow=True" parameter
        grp3 = VGroup(l1c, l2c, elbow).move_to([4.4, -1.6, 0])
        # get_value() is broken upstream in ManimCE 0.21 (Angle has no angle_value attribute,
        # both engines crash), so here we read the same value from the difference of the two sides' direction angles
        deg = (l2c.get_angle() - l1c.get_angle()) % (2 * PI)
        cap3 = Text("elbow=True (%.1f deg)" % (deg / PI * 180),
                    font_size=18, color=GREY_B).next_to(grp3, DOWN, buff=0.25)   # the difference of the two direction angles = 90.0
        win.play(Create(grp3), FadeIn(cap3), run_time=0.6)   # elbow + angle readout
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: Angle.from_three_points —— an angle from three points ======
```

What this code does: the first row is four groups with the same two sides, changing only `quadrant`, so the marking arcs of the four quadrants appear one after another — a glance shows that this parameter picks "which side the arc is drawn on". After that:

- `other_angle=True` draws the red reflex angle on the other side;
- `dot=True`+`dot_radius`+`dot_distance`+`dot_color` place a dot inside the arc whose position, size and colour are all adjustable;
- last, `elbow=True` swaps the arc for a right-angle elbow and reads `90.0` from the difference of the two sides' direction angles onto the caption (`get_value()` itself is broken upstream, see the parameter table).

<video src="assets/RTM output/04-Angles-and-Callout-Boxes-angle.mp4" controls width="560"></video>

> Note: when `radius` is omitted it is derived from the two sides; with very short sides the marking arc sticks to the vertex, so pass it explicitly if you want a fixed size; `quadrant` and `other_angle` are two different things — the former picks the quadrant, the latter picks "the supplementary-angle side", and using them together covers every way of drawing the four directions.

### `Angle.from_three_points`

```python
@classmethod
def from_three_points(cls, A: Point3DLike, B: Point3DLike, C: Point3DLike, **kwargs) -> Angle:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `A` | `Point3DLike` | required | end point of the first side (not the vertex) |
| `B` | `Point3DLike` | required | the **vertex**: the angle is marked at B, and the two sides are B→A and B→C |
| `C` | `Point3DLike` | required | end point of the second side |
| `**kwargs` | — | — | the remaining parameters are the same as `Angle` (the sample gives `radius=0.7, color=GOLD`) |

#### Sample: marking an angle from three points

Three white dots place A/B/C on screen and the angle is marked at the middle point B — you do not need to draw a `Line` first.

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Line, Arrow, Dot, Square, Circle, Triangle, Text, VGroup,
    Angle, RightAngle, SurroundingRectangle, BackgroundRectangle, Cross, Underline,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class AngleThreePointsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("04-Angle.from_three_points", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        a = ORIGIN + LEFT * 2.2 + DOWN * 1.2   # the "A" parameter: start point
        b = ORIGIN + LEFT * 0.2 + DOWN * 1.2   # the "B" parameter: vertex
        c = ORIGIN + RIGHT * 0.6 + UP * 0.8   # the "C" parameter: end point
        dots = VGroup(Dot(a, radius=0.07, color=WHITE), Dot(b, radius=0.07, color=WHITE),
                      Dot(c, radius=0.07, color=WHITE))   # mark the three vertices with small dots
        ang = Angle.from_three_points(a, b, c, radius=0.7, color=GOLD)   # an angle from three points (B is the vertex)
        cap = Text("Angle.from_three_points(A, B, C)", font_size=20, color=GREY_B).to_edge(DOWN, buff=1.0)
        win.play(FadeIn(dots), run_time=0.4)   # show the dots first
        win.play(Create(ang), FadeIn(cap), run_time=0.7)   # then draw the angle
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: RightAngle —— length and colour of the right-angle mark =====
```

What this code does: `a`/`b`/`c` are three screen coordinates; first `FadeIn(dots)` draws the three points (so you can check the positions), then `Angle.from_three_points(a, b, c, radius=0.7, color=GOLD)` — note the **angle is marked at the middle point B**, with the two sides being B→A and B→C. `**kwargs` is exactly the same as for `Angle`, so radius, colour, `dot` and the like all still work.

<video src="assets/RTM output/04-Angles-and-Callout-Boxes-angle3p.mp4" controls width="560"></video>

> Note: the order of the three points is A (a point on one side) → B (the vertex) → C (a point on the other side), so put the vertex in the middle; swap the order and the angle is marked at a different point, which the picture shows immediately.

### `RightAngle`

```python
def __init__(self, line1: Line, line2: Line, length: float | None = None, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `line1` | `Line` | required | the first side |
| `line2` | `Line` | required | the second side |
| `length` | `float \| None` | `None` | side length of the small square corner. **Accepts** any positive number; when omitted it is derived from the two sides (the sample uses 0.25 / 0.6 / omitted) |
| `**kwargs` | — | — | common parameters such as colour (the sample uses red/green/blue) |

#### Sample: a small square corner of 0.25 / 0.6 / default

Three identical right angles changing only `length` and the colour: `0.25`, `0.6`, and not passing it (automatic).

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Line, Arrow, Dot, Square, Circle, Triangle, Text, VGroup,
    Angle, RightAngle, SurroundingRectangle, BackgroundRectangle, Cross, Underline,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class RightAngleDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("04-RightAngle", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— length given explicitly as 0.25 / 0.6, with different colours ——
        l1 = Line(ORIGIN, RIGHT * 1.6)
        l2 = Line(ORIGIN, UP * 1.6)
        small = RightAngle(l1, l2, length=0.25, color=RED)   # the "length=0.25" parameter
        grp = VGroup(l1, l2, small).move_to([-2.6, 0.8, 0])
        cap = Text("length=0.25", font_size=18, color=GREY_B).next_to(grp, DOWN, buff=0.25)
        win.play(Create(grp), FadeIn(cap), run_time=0.5)   # small right-angle mark + caption

        l3 = Line(ORIGIN, RIGHT * 1.6)
        l4 = Line(ORIGIN, UP * 1.6)
        big = RightAngle(l3, l4, length=0.6, color=GREEN)   # the "length=0.6" parameter
        grp2 = VGroup(l3, l4, big).move_to([1.2, 0.8, 0])
        cap2 = Text("length=0.6", font_size=18, color=GREY_B).next_to(grp2, DOWN, buff=0.25)
        win.play(Create(grp2), FadeIn(cap2), run_time=0.5)   # large right-angle mark + caption

        # —— length omitted: derived from the two sides ——
        l5 = Line(ORIGIN, RIGHT * 1.6)
        l6 = Line(ORIGIN, UP * 1.6)
        auto = RightAngle(l5, l6, color=BLUE)   # do not pass length (default None)
        grp3 = VGroup(l5, l6, auto).move_to([4.6, 0.8, 0])
        cap3 = Text("length=None (auto)", font_size=18, color=GREY_B).next_to(grp3, DOWN, buff=0.25)
        win.play(Create(grp3), FadeIn(cap3), run_time=0.5)   # automatic length + caption
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 4: SurroundingRectangle —— colour / buff / corner radius ======
```

What this code does: three right angles side by side; `length` goes from 0.25 to 0.6 to omitted, and the small square corner grows with the parameter and finally takes a size derived from the two sides; the colours are red/green/blue, to confirm `**kwargs` also works as usual. It is shorthand for `Angle(..., elbow=True)`, and drawing a right angle this way is less trouble than hand-tuning the arc radius.

<video src="assets/RTM output/04-Angles-and-Callout-Boxes-rightangle.mp4" controls width="560"></video>

> Note: `length` is the **side length** of the two short edges of the square corner (not a radius); make it too large and it exceeds the length of the two sides themselves, so it looks like it "wraps" the angle; when the two sides are especially short, pass a smaller explicit value.

### `SurroundingRectangle`

```python
def __init__(self, *mobjects: Mobject, color: ParsableManimColor = PURE_YELLOW, buff: float | tuple[float, float] = SMALL_BUFF, corner_radius: float = 0.0, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*mobjects` | `Mobject...` | required | the objects to frame; **accepts** any number; with several objects it takes the **overall bounding box** (the sample gives one and two once each) |
| `color` | `ManimColor` | `PURE_YELLOW` | frame colour (the sample uses red/teal once each) |
| `buff` | `float \| tuple[float, float]` | `SMALL_BUFF` (0.1) | distance from the object; you can also pass a `(horizontal, vertical)` pair |
| `corner_radius` | `float` | `0.0` | corner radius; 0 means sharp corners |

#### Sample: a single object / a large buff with rounded corners / two objects

Left to right: the default frame, `buff=0.45` plus rounded corners, and "framing two objects together" (the overall bounding box).

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Line, Arrow, Dot, Square, Circle, Triangle, Text, VGroup,
    Angle, RightAngle, SurroundingRectangle, BackgroundRectangle, Cross, Underline,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class SurroundingDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("04-SurroundingRectangle", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— a single object: default bright yellow, buff 0.1, no rounded corners ——
        sq = Square(side_length=1.4, color=BLUE, fill_opacity=0.5).move_to([-3.4, 1.2, 0])
        f1 = SurroundingRectangle(sq)   # the "*mobjects" parameter with only one object
        cap = Text("SurroundingRectangle(sq)", font_size=18, color=GREY_B).next_to(VGroup(sq, f1), DOWN, buff=0.25)
        win.play(Create(sq), run_time=0.4)   # draw the framed object first
        win.play(Create(f1), FadeIn(cap), run_time=0.5)   # then add the default frame + caption

        # —— a larger buff + rounded corners + a different colour ——
        ci = Circle(radius=0.7, color=GREEN, fill_opacity=0.5).move_to([0, 1.2, 0])
        f2 = SurroundingRectangle(ci, color=RED, buff=0.45, corner_radius=0.25)   # the "color / buff / corner_radius" parameters
        cap2 = Text("buff=0.45 corner_radius=0.25", font_size=18, color=GREY_B).next_to(VGroup(ci, f2), DOWN, buff=0.25)
        win.play(Create(ci), run_time=0.4)
        win.play(Create(f2), FadeIn(cap2), run_time=0.5)   # a wide, rounded frame + caption

        # —— several objects: take the overall bounding box ——
        tri = Triangle(color=PURPLE, fill_opacity=0.5).scale(0.6).move_to([3.0, 1.0, 0])
        dot = Dot(point=[4.6, 1.8, 0], radius=0.1, color=ORANGE)
        f3 = SurroundingRectangle(tri, dot, color=TEAL, buff=0.2)   # the "*mobjects" parameter with two objects: the overall bounding box
        cap3 = Text("SurroundingRectangle(tri, dot)", font_size=18, color=GREY_B).next_to(VGroup(tri, dot, f3), DOWN, buff=0.25)
        win.play(Create(tri), FadeIn(dot), run_time=0.4)
        win.play(Create(f3), FadeIn(cap3), run_time=0.5)   # overall bounding box + caption
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 5: BackgroundRectangle —— backdrop / stroke / opacity / buff ===
```

What this code does: three frames appear in turn.

- The first passes nothing and gets the default bright yellow, buff 0.1, sharp corners.
- The second raises `buff` to 0.45, sets `corner_radius` to 0.25 and switches to red, so the frame is clearly farther from the object and has rounded corners.
- The third passes two objects at once (a triangle + a dot) and the frame encloses both — however many objects `*mobjects` collects, that is the overall bounding box it uses.

<video src="assets/RTM output/04-Angles-and-Callout-Boxes-surrounding.mp4" controls width="560"></video>

> Note: `buff` can also be a `(horizontal, vertical)` pair to tune the two directions separately; the frame draws only a stroke (no fill), so overlaying it on an object does not block the content — if you really want to block, pair it with `z_index` or switch to `BackgroundRectangle`.

### `BackgroundRectangle`

```python
def __init__(self, *mobjects: Mobject, color: ParsableManimColor | None = None, stroke_width: float = 0, stroke_opacity: float = 0, fill_opacity: float = 0.75, buff: float | tuple[float, float] = 0, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*mobjects` | `Mobject...` | required | the objects to back; several are allowed (backed as one bounding box) |
| `color` | `ManimColor \| None` | `None` (treated as black) | backdrop colour; when omitted it is a black backdrop, good for improving readability over a dark picture |
| `stroke_width` | `float` | `0` | stroke width of the backdrop block; 0 means no stroke |
| `stroke_opacity` | `float` | `0` | stroke opacity |
| `fill_opacity` | `float` | `0.75` | fill opacity; 0.75 = 25% of the background shows through |
| `buff` | `float \| tuple[float, float]` | `0` | how much bigger than the object it is |

#### Sample: the default black backdrop / a tinted one with a stroke / a larger buff

Three backdrops: the default (75% black), a purple one with a stroke that is semi-transparent, and a teal one with a larger `buff`, a ring bigger than the text.

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Line, Arrow, Dot, Square, Circle, Triangle, Text, VGroup,
    Angle, RightAngle, SurroundingRectangle, BackgroundRectangle, Cross, Underline,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class BackgroundDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("04-BackgroundRectangle", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— default: a 75% opaque black backdrop under white text ——
        t1 = Text("readable", font_size=34, color=WHITE).move_to([-3.0, 1.2, 0])
        b1 = BackgroundRectangle(t1)   # default parameter values: color=None (treated as black), fill_opacity=0.75, buff=0
        win.play(FadeIn(b1), run_time=0.4)   # lay the backdrop first
        win.play(FadeIn(t1), run_time=0.4)   # then add the text

        # —— change the colour + add a stroke + tune the opacity ——
        t2 = Text("tinted", font_size=34, color=WHITE).move_to([1.4, 1.2, 0])
        b2 = BackgroundRectangle(t2, color=PURPLE, stroke_width=4, stroke_opacity=1,
                                 fill_opacity=0.5)   # the "color / stroke_width / stroke_opacity / fill_opacity" parameters
        win.play(FadeIn(b2), run_time=0.4)
        win.play(FadeIn(t2), run_time=0.4)

        # —— a larger buff: the backdrop is a ring bigger than the text ——
        t3 = Text("padded", font_size=34, color=WHITE).move_to([-1.0, -1.4, 0])
        b3 = BackgroundRectangle(t3, color=TEAL, fill_opacity=0.9, buff=0.35)   # the "buff=0.35" parameter
        cap = Text("buff=0.35", font_size=18, color=GREY_B).next_to(VGroup(t3, b3), DOWN, buff=0.25)
        win.play(FadeIn(b3), FadeIn(cap), run_time=0.4)
        win.play(FadeIn(t3), run_time=0.4)   # the backdrop is a ring bigger than the text
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 6: Cross / Underline —— two ways to negate ====================
```

What this code does: each block is "first `FadeIn` the backdrop block, then `FadeIn` the text", and that order is the stacking order.

- The first passes nothing: a 75% opaque black backdrop (not necessarily visible on a dark picture, but obvious once you switch to a lighter colour or add a stroke).
- The second switches to purple, adds a 4px stroke and drops the fill to 0.5.
- The third sets `buff` to 0.35, so the backdrop block is a ring bigger than the text on all sides.

<video src="assets/RTM output/04-Angles-and-Callout-Boxes-background.mp4" controls width="560"></video>

> Note: the backdrop is an **independent mobject**, so to cover something already in the scene you must make it sort later (`add` order or `z_index`); the default `color=None` is treated as black and is almost invisible on a pure black background — which is exactly its "improve readability" use on a dark picture.

### `Cross` / `Underline`

```python
def __init__(self, mobject: Mobject | None = None, stroke_color: ParsableManimColor = RED, stroke_width: float = 6.0, scale_factor: float = 1.0, **kwargs) -> None:   # Cross
def __init__(self, mobject: Mobject, buff: float = SMALL_BUFF, **kwargs) -> None:                                                                                     # Underline
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `Cross.mobject` | `Mobject \| None` | `None` | the object to cross out: the cross's position and size follow it; when omitted you get a cross of the default size |
| `Cross.stroke_color` | `ManimColor` | `RED` | colour of the cross |
| `Cross.stroke_width` | `float` | `6.0` | stroke width |
| `Cross.scale_factor` | `float` | `1.0` | scale relative to the crossed-out object |
| `Underline.mobject` | `Mobject` | required | the object to underline: the line length automatically equals its width |
| `Underline.buff` | `float` | `SMALL_BUFF` (0.1) | vertical distance from the object |

#### Sample: colour / width / scale of the cross + two underline buffs

Two crosses on the left (default vs a thick yellow one scaled 1.4x), two underlines on the right (tight against the text vs far from it).

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Line, Arrow, Dot, Square, Circle, Triangle, Text, VGroup,
    Angle, RightAngle, SurroundingRectangle, BackgroundRectangle, Cross, Underline,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class CrossUnderlineDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("04-Cross / Underline", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— Cross: position and size are decided by the crossed-out object ——
        sq = Square(side_length=1.2, color=BLUE, fill_opacity=0.5).move_to([-3.4, 0.6, 0])
        x1 = Cross(sq)   # the "mobject=sq" parameter: the cross sits on the square and its size follows the square
        cap1 = Text("Cross(sq)", font_size=18, color=GREY_B).next_to(VGroup(sq, x1), DOWN, buff=0.25)
        win.play(Create(sq), run_time=0.4)
        win.play(Create(x1), FadeIn(cap1), run_time=0.5)

        # —— a different colour / width / scale ——
        ci = Circle(radius=0.6, color=GREEN, fill_opacity=0.5).move_to([0, 0.6, 0])
        x2 = Cross(ci, stroke_color=YELLOW, stroke_width=14, scale_factor=1.4)   # the "stroke_color / stroke_width / scale_factor" parameters
        cap2 = Text("stroke_width=14 scale_factor=1.4", font_size=18, color=GREY_B).next_to(VGroup(ci, x2), DOWN, buff=0.25)
        win.play(Create(ci), run_time=0.4)
        win.play(Create(x2), FadeIn(cap2), run_time=0.5)

        # —— Underline: give only the width and buff (the length follows the object's width) ——
        t = Text("underlined", font_size=34, color=WHITE).move_to([3.4, 0.6, 0])
        u1 = Underline(t, buff=0.08, color=RED)   # the "buff=0.08" parameter
        cap3 = Text("Underline(t, buff=0.08)", font_size=18, color=GREY_B).next_to(VGroup(t, u1), DOWN, buff=0.35)
        win.play(FadeIn(t), run_time=0.4)
        win.play(Create(u1), FadeIn(cap3), run_time=0.5)

        t2 = Text("loose", font_size=34, color=WHITE).move_to([3.4, -1.6, 0])
        u2 = Underline(t2, buff=0.5, color=ORANGE)   # the "buff=0.5" parameter: farther from the text
        cap4 = Text("buff=0.5", font_size=18, color=GREY_B).next_to(VGroup(t2, u2), DOWN, buff=0.35)
        win.play(FadeIn(t2), run_time=0.4)
        win.play(Create(u2), FadeIn(cap4), run_time=0.5)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window
```

What this code does: the cross of `Cross(sq)` automatically fills the square; the second cross switches to yellow with stroke width 14 and `scale_factor=1.4`, clearly bigger and thicker than the circle. `Underline` takes only the object and `buff` — the line length always equals the object's width, so `buff=0.08` hugs the text and `buff=0.5` sits far from it; side by side the two make the buff parameter obvious at a glance.

<video src="assets/RTM output/04-Angles-and-Callout-Boxes-cross.mp4" controls width="560"></video>

> Note: `Cross`'s `scale_factor` is relative to the size of the **crossed-out object**, not an absolute length; to change `Underline`'s colour/width just go through `**kwargs` (`color=`, `stroke_width=`) and leave the length alone.

---

See also: [Angles and callout boxes (2)](04b-Labeled-Annotations.md) · [Lines and arrows](02-Lines-and-Arrows.md) · [VMobject styles](07-VMobject-Styles.md)
