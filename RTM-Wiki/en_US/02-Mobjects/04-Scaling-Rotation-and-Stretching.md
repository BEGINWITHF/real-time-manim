# Scaling, rotation and stretching

Scale an object uniformly, rotate it, mirror it and stretch it along one dimension. All the methods below return `self` and can be chained.

## Parameters

### scale

```python
def scale(scale_factor: float, *, about_point: Point3DLike | None = None,
          about_edge: Vector3DLike | None = None) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `scale_factor` | `float` | — | scaling factor. **Accepts** `0<\|a\|<1` to shrink, `>1` to grow, and a **negative value flips** |
| `about_point` | point or `None` (keyword) | `None` | which point to scale about; `None` uses own center |
| `about_edge` | vector or `None` (keyword) | `None` | which edge to scale about (e.g. `DOWN` keeps the bottom edge fixed) |

> **Returns**: `self`. `about_point` / `about_edge` **must be passed by keyword**; when both are given, `about_point` wins.

#### Sample: three pivots for `scale`

The blue square is first scaled up 1.6× about its own center, then scaled down about a red dot (the dot stays put), and finally scaled up about the bottom edge (the bottom edge stays fixed).

```python
from real_time_manim import Scene, Square, Dot, \
    BLUE, RED, UP, DOWN, RIGHT
from real_time_manim.vulkan_bind import MLWindow, Wait

class ScaleDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.6, fill_opacity=0.5)   # blue square
        anchor = Dot(color=RED, radius=0.08).move_to(RIGHT * 2.5)   # marker for the scaling pivot
        self.add(sq, anchor)   # add them to the scene
        win.play(sq.animate.scale(1.6), run_time=0.6)   # by default scales up about its own center
        win.play(sq.animate.scale(0.6, about_point=RIGHT * 2.5), run_time=0.6)   # scale about the red dot: the dot's position is unchanged
        win.play(sq.animate.scale(1.8, about_edge=DOWN), run_time=0.6)   # scale about the bottom edge: the bottom edge stays fixed
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window
```

What this code does: the blue square is scaled in three steps, and the red dot is a visual marker for the "pivot".

- The first step adds no arguments and scales up 1.6× about **its own center**.
- The second, `about_point=RIGHT * 2.5`, scales down 0.6× about the red dot — the dot never moves and the square shrinks toward it.
- The third, `about_edge=DOWN`, scales up 1.8× about the bottom edge, so the bottom edge stays pinned and the square grows upward.

The difference between the three pivots is plain on screen.

<video src="assets/RTM output/04-Scaling-Rotation-and-Stretching-scale.mp4" controls width="560"></video>

> Note: a negative `scale_factor` does "scale + flip", effectively scaling in the negative direction; generally `flip` is more direct if you want a flip. `scale` is a pure geometric transform, so the stroke width does **not** get thicker with it (to scale the line width too, use something like `scale_stroke` or adjust `stroke_width` afterwards).

### rotate / rotate_about_origin

```python
def rotate(angle: float, axis: Vector3DLike = OUT, *,
           about_point: Point3DLike | None = None,
           about_edge: Vector3DLike | None = None,
           **kwargs: Any) -> Self
def rotate_about_origin(angle: float, axis: Vector3DLike = OUT) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `angle` | `float` | — | radians. **Accepts** `PI / 2`, `90 * DEGREES` (the two are equivalent) |
| `axis` | vector | `OUT` | rotation-axis direction; in-plane 2D rotation uses the default `OUT`, and you only change the axis for a **3D rotation** |
| `about_point` | point or `None` (keyword) | `None` | which point to rotate about; `None` uses own center |
| `about_edge` | vector or `None` (keyword) | `None` | which edge to rotate about |
| `**kwargs` | `Any` | — | the base `Mobject.rotate` ignores these keywords; but real classes such as `Square`/`Circle` go through `VMobject.rotate`, which has **no `**kwargs` parameter**, so one extra kwarg raises `TypeError` immediately |

> **Returns**: `self`. `rotate_about_origin(angle, axis)` is equivalent to `rotate(angle, axis, about_point=ORIGIN)` — rotating about the **scene origin** rather than own center.

#### Sample: the difference between `rotate` and the `Rotate` animation

The rectangle first turns 90° with `animate.rotate` (note this is interpolation, not a continuous turn), then turns 60° about a given point, then turns 180° continuously with the `Rotate` animation, and finally turns 90° about the origin with `rotate_about_origin`.

```python
from real_time_manim import Scene, Rectangle, \
    GREEN, UP, LEFT, DEGREES, FadeIn, Rotate
from real_time_manim.vulkan_bind import MLWindow, Wait

class RotateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        rect = Rectangle(width=2.4, height=1.0, color=GREEN, fill_opacity=0.5)   # a rectangle: easy to see when it turns
        self.add(rect)   # add it to the scene
        win.play(rect.animate.rotate(90 * DEGREES), run_time=0.6)   # turn 90° about its own center (radians = 90*DEGREES)
        win.play(rect.animate.rotate(60 * DEGREES, about_point=LEFT * 2), run_time=0.6)   # turn about a given point
        win.play(Rotate(rect, angle=180 * DEGREES), run_time=0.8)   # "animate.rotate" only interpolates; for a continuous turn use the Rotate animation
        win.play(rect.animate.rotate_about_origin(90 * DEGREES), run_time=0.6)   # rotate about the scene origin (0, 0, 0)
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window
```

What this code does: the green rectangle goes through four steps.

- `animate.rotate(90°)` turns about its own center (what you see on screen is a "fade across" interpolation, with the intermediate frames squashed, not a turn through the motion!).
- `about_point=LEFT * 2` makes it turn 60° about the point on the left, sweeping out a fan.
- `Rotate(rect, angle=180°)` is an **animation class**, and it turns continuously through half a circle on screen.
- Finally `rotate_about_origin(90°)` makes it revolve 90° about the origin at the middle of the frame.

<video src="assets/RTM output/04-Scaling-Rotation-and-Stretching-rotate.mp4" controls width="560"></video>

> Note: `.animate.rotate(...)` only **interpolates to the rotated state** (a point-to-point linear transition, with intermediate frames collapsing), it does not spin continuously by angle; for a real spin use the `Rotate` / `Rotating` animation classes. `axis` is a 3D parameter, and changing it in 2D usually has no visible effect (an exception is 180° about the `RIGHT` axis, which equals an up-down mirror, see `flip`).

### flip

```python
def flip(axis: Vector3DLike = UP, *, about_point: Point3DLike | None = None,
         about_edge: Vector3DLike | None = None) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `axis` | vector | `UP` | mirror axis (rotate 180° about it). `UP` (vertical axis) = **left-right** mirror, `RIGHT` (horizontal axis) = **up-down** mirror — counter-intuitive |
| `about_point` | point or `None` (keyword) | `None` | mirror pivot; `None` uses own center |
| `about_edge` | vector or `None` (keyword) | `None` | mirror pivot edge |

> **Returns**: `self`. The implementation is just `rotate(PI, axis, ...)` — rotate 180° about `axis`, so `axis` is the **rotation axis**, not "the edge to flip".

#### Sample: the direction of `flip`'s two axes

A line high on the right and low on the left: `axis=UP` flips it to high-left/low-right (a left-right mirror), then `axis=RIGHT, about_point=RIGHT * 2` flips it back to high-right/low-left (an up-down mirror about a pivot on the right).

```python
from real_time_manim import Scene, Line, \
    YELLOW, UP, LEFT, RIGHT
from real_time_manim.vulkan_bind import MLWindow, Wait

class FlipDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        s = Line(LEFT * 2, RIGHT * 2 + UP * 1.2, color=YELLOW)   # a line high on the right and low on the left: a mirror is easy to see
        self.add(s)   # add it to the scene
        win.play(s.animate.flip(axis=UP), run_time=0.6)   # turn 180° about the vertical axis = a left-right mirror
        win.play(s.animate.flip(axis=RIGHT, about_point=RIGHT * 2), run_time=0.6)   # turn 180° about the horizontal axis = an up-down mirror, pivot on the right
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window
```

What this code does: a yellow line high on the right and low on the left serves as an "arrow" — `flip(axis=UP)` flips it 180° about the vertical axis and the line becomes high-left/low-right (**left-right** swapped); then `flip(axis=RIGHT, about_point=RIGHT * 2)` flips it 180° about the horizontal axis with the pivot on the right, so the line flips back to high-right/low-left, but the whole line is offset to the right because the pivot is on the right. The two steps make "axis is the rotation axis" plain.

<video src="assets/RTM output/04-Scaling-Rotation-and-Stretching-flip.mp4" controls width="560"></video>

> Note: `axis=UP` is a **left-right** mirror and `axis=RIGHT` is an **up-down** mirror — don't read it as "whichever edge `axis` points at is the one that flips"; it is the rotation axis (turning half a circle about a vertical axis naturally swaps left and right). To give text a reflection (flip it vertically) use `flip(axis=RIGHT)`.

### stretch / stretch_about_point

```python
def stretch(factor: float, dim: int, *, about_point: Point3DLike | None = None,
            about_edge: Vector3DLike | None = None) -> Self
def stretch_about_point(factor: float, dim: int, point: Point3DLike) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `factor` | `float` | — | stretch factor along that direction (does not preserve the aspect ratio) |
| `dim` | `int` | — | **only** `0`=x, `1`=y, `2`=z |
| `about_point` | point or `None` (keyword) | `None` | reference point; `None` uses own center |
| `about_edge` | vector or `None` (keyword) | `None` | reference edge |
| `point` | point | — | `stretch_about_point` only: the point that stays fixed (positional-argument form) |

> **Returns**: `self`. `stretch_about_point(factor, dim, point)` is the positional-argument form of `stretch(factor, dim, about_point=point)`. It is what backs methods such as `stretch_to_fit_width`.

#### Sample: single-dimension stretching with `stretch`

The purple square is first stretched 2.2× horizontally, then squashed to half vertically about the origin, and finally stretched to the right with `stretch_about_point`, keeping the left end fixed.

```python
from real_time_manim import Scene, Square, \
    PURPLE, UP, DOWN, ORIGIN
from real_time_manim.vulkan_bind import MLWindow, Wait

class StretchDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        sq = Square(color=PURPLE, side_length=1.4, fill_opacity=0.5)   # purple square
        self.add(sq)   # add it to the scene
        win.play(sq.animate.stretch(2.2, 0), run_time=0.6)   # stretch horizontally only: dim=0
        win.play(sq.animate.stretch(0.5, 1, about_point=ORIGIN), run_time=0.6)   # dim=1 squash, about the origin
        win.play(sq.animate.stretch_about_point(1.8, 0, sq.get_left()), run_time=0.6)   # stretch right, left end fixed
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window
```

What this code does: the purple square is stretched one dimension at a time — `stretch(2.2, 0)` scales up 2.2× in x only (becoming a flat bar); `stretch(0.5, 1, about_point=ORIGIN)` squashes it to half in y, with the **origin** as the pivot (the square's bottom edge comes up); `stretch_about_point(1.8, 0, sq.get_left())` uses the left edge as the fixed point and stretches to the right, pinning the square's left end in place. Only one dimension moves throughout and the other stays perfectly still — that is the essential difference from `scale`.

<video src="assets/RTM output/04-Scaling-Rotation-and-Stretching-stretch.mp4" controls width="560"></video>

> Note: `stretch` **does not preserve the aspect ratio**, `scale` does; for target-size adjustments such as "width becomes 5" use `stretch_to_fit_width` / `scale_to_fit_width` (see [04b-Scaling-Rotation-and-Stretching-Advanced](04b-Scaling-Rotation-and-Stretching-Advanced.md)). `dim` is an absolute axis (`0`/`1`/`2`), so stretching a rotated object still pulls along the world-coordinate axis and distorts it.

---

See also: [Scaling, Rotation and Stretching (advanced)](04b-Scaling-Rotation-and-Stretching-Advanced.md) · [Positioning](02-Positioning.md)
