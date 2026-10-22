# Scaling, Rotation and Stretching (Advanced)

Fitting to a target size and per-point custom transforms — size a mobject by a metric such as "width = 7", or apply your own mapping to every vertex. All the methods below return `self`.

## Parameters

### rescale_to_fit

```python
def rescale_to_fit(length: float, dim: int, stretch: bool = False, **kwargs: Any) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `length` | `float` | — | target length |
| `dim` | `int` | — | **only** `0`=width, `1`=height, `2`=depth |
| `stretch` | `bool` | `False` | `False` scales proportionally to that length; `True` stretches only this dimension to that length (distorts) |
| `**kwargs` | `Any` | — | passed through to the underlying `scale` / `stretch` (such as `about_point=`) |

> **Returns**: self. This is the general entry point for "**the length of one dimension**" — the six `scale_to_fit_*` / `stretch_to_fit_*` methods are all sugar for it.

#### Sample: `rescale_to_fit` proportional vs. stretched

A 1×1 square first has its width set to 4 (`stretch=False`, proportional, so the height becomes 4 too), then its height forced to 1 (`stretch=True`, width stays 4).

```python
from real_time_manim import Scene, Square, \
    BLUE
from real_time_manim.vulkan_bind import MLWindow, Wait

class RescaleDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.0, fill_opacity=0.5)   #a 1×1 square
        self.add(sq)   #add to the scene
        win.play(sq.animate.rescale_to_fit(4.0, 0), run_time=0.6)   #set width to 4.0: stretch=False, proportional
        print("after proportional: width =", round(sq.width, 2), "height =", round(sq.height, 2))   #4.0 4.0
        win.play(sq.animate.rescale_to_fit(1.0, 1, stretch=True), run_time=0.6)   #force height to 1.0: squash only this dimension
        print("after stretch: width =", round(sq.width, 2), "height =", round(sq.height, 2))   #4.0 1.0
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: a 1×1 square first calls `rescale_to_fit(4.0, 0)` — `dim=0` means a target width of 4, and `stretch=False` so it scales proportionally, turning the square into a big 4×4 square (console `4.0 4.0`); then `rescale_to_fit(1.0, 1, stretch=True)` — `dim=1` targets height 1, `stretch=True` squashes only that dimension, giving a flat 4×1 bar (console `4.0 1.0`).

<video src="assets/RTM output/04b-Scaling-Rotation-and-Stretching-Advanced-rescale.mp4" controls width="560"></video>

> Note: with `stretch=False` (the default) the scaling is proportional along that dimension and the other two follow; `dim=2` (depth) has no effect on flat objects and is only used in 3D. For the everyday "make the width 5", writing `stretch_to_fit_width(5)` or `scale_to_fit_width(5)` directly is handier — see the next section.

### scale_to_fit_* / stretch_to_fit_* (six of them)

```python
def scale_to_fit_width(width: float, **kwargs: Any) -> Self    # stretch_to_fit_width(width, ...)
def scale_to_fit_height(height: float, ...) -> Self            # stretch_to_fit_height(height, ...)
def scale_to_fit_depth(depth: float, ...) -> Self              # stretch_to_fit_depth(depth, ...)
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `width` / `height` / `depth` | `float` | — | target size |
| `**kwargs` | `Any` | — | passed through (such as `about_point=`) |

> **Returns**: self. **`scale_*` preserves the aspect ratio** (equivalent to `rescale_to_fit(..., stretch=False)`), while **`stretch_*` distorts** (adjusts only that dimension, equivalent to `stretch=True`). `*_depth` is a safe no-op for 2D objects.

#### Sample: `scale_to_fit` vs `stretch_to_fit`

Two 1×1 rectangles: the left one uses `scale_to_fit_*` (proportional; the second call cancels the first back to 1×1), the right one uses `stretch_to_fit_*` (distorting; ends at 3×1).

```python
from real_time_manim import Scene, Rectangle, \
    BLUE, RED, UP, LEFT, RIGHT
from real_time_manim.vulkan_bind import MLWindow, Wait

class FitDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        a = Rectangle(width=1.0, height=1.0, color=BLUE, fill_opacity=0.4)   #left: the pair that keeps the aspect ratio
        a.shift(LEFT * 4.0 + UP * 1.4)
        b = Rectangle(width=1.0, height=1.0, color=RED, fill_opacity=0.4)   #right: the pair that distorts
        b.shift(RIGHT * 4.0 + UP * 1.4)
        self.add(a, b)   #add to the scene
        win.play(a.animate.scale_to_fit_width(3.0), run_time=0.6)   #proportional: width 3 makes the height 3 too
        a.scale_to_fit_height(1.0)   #proportional: set height to 1, width comes back to 1 as well
        print("after scale_to_fit:", round(a.width, 2), round(a.height, 2))   #1.0 1.0
        win.play(b.animate.stretch_to_fit_width(3.0), run_time=0.6)   #stretch the width only, height unchanged
        b.stretch_to_fit_height(1.0)   #squash the height only
        print("after stretch_to_fit:", round(b.width, 2), round(b.height, 2))   #3.0 1.0
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: two 1×1 rectangles side by side go through the same two "size-to-fit" calls for comparison. The blue one on the left uses `scale_to_fit_*`: setting the width to 3 makes it 3×3 because the **aspect ratio is preserved**, and then setting the height to 1 shrinks the whole thing back to 1×1; the red one on the right uses `stretch_to_fit_*`: setting the width to 3 stretches only the width (a flat 3×1 bar), and setting the height to 1 leaves it as it already was. The console prints `1.0 1.0` and `3.0 1.0` — one preserves the ratio, the other preserves a single dimension.

<video src="assets/RTM output/04b-Scaling-Rotation-and-Stretching-Advanced-fit.mp4" controls width="560"></video>

> Note: the two families' **names differ by a single letter**, and a typo distorts your object: use `scale_to_fit_*` to keep the shape, `stretch_to_fit_*` to control one dimension precisely. `*_depth` is safe for 2D objects (`length_over_dim(2)` is 0, so no division by zero — a tested no-op).

### pose_at_angle

```python
def pose_at_angle(**kwargs: Any) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `**kwargs` | `Any` | — | passed through to `rotate` (such as `about_point=`) |

> **Returns**: self. Equivalent to `rotate(TAU / 14, RIGHT + UP, **kwargs)` — a rotation of 360°/14 ≈ 25.7° around the diagonal axis, the "natural display angle" for 3D objects.

#### Sample: posing with `pose_at_angle`

A triangle posed at 25.7° around the diagonal axis (its bounding box shrinks after the oblique projection); the grey triangle on the right stays put as a reference.

```python
from real_time_manim import Scene, Triangle, \
    YELLOW, GREY, RIGHT, UP
from real_time_manim.vulkan_bind import MLWindow, Wait

class PoseDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        tri = Triangle(color=YELLOW, fill_opacity=0.4).scale(1.2)   #the triangle being posed
        flat = Triangle(color=GREY, fill_opacity=0.3).shift(RIGHT * 3.2)   #the unposed reference
        self.add(tri, flat)   #add to the scene
        print("before pose: width =", round(tri.width, 2))   #width before posing
        win.play(tri.animate.pose_at_angle(), run_time=0.7)   #equivalent to rotate(TAU/14, RIGHT + UP)
        print("after pose: width =", round(tri.width, 2), "height =", round(tri.height, 2))   #smaller after the oblique projection
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: the yellow triangle plays `pose_at_angle()` — a 25.7° rotation around the `RIGHT + UP` diagonal axis, which tips the object over and shows up on a 2D canvas as an oblique squash; the console prints a width shrinking from 2.08 to 1.98. The grey triangle on the right stays as it is for comparison, and the difference between the two outlines on screen is exactly this angle.

<video src="assets/RTM output/04b-Scaling-Rotation-and-Stretching-Advanced-pose.mp4" controls width="560"></video>

> Note: the name is a bit misleading — it only "looks good under a 3D viewpoint". On a 2D canvas it just squashes the object obliquely; its real purpose is giving 3D objects such as cubes and spheres a default angle. The axis is `RIGHT + UP` (the upper-right diagonal) and the angle is fixed at `TAU / 14`; to change the angle, use `rotate` directly.

### apply_function / apply_matrix / apply_complex_function (and the two position variants)

```python
def apply_function(function: MappingFunction, *, about_point: Point3DLike | None = None,
                   about_edge: Vector3DLike | None = None) -> Self
def apply_matrix(matrix: MatrixMN, *, about_point=None, about_edge=None) -> Self
def apply_complex_function(function: Callable[[complex], complex], *,
                           about_point=None, about_edge=None) -> Self
def apply_function_to_position(function: MappingFunction) -> Self
def apply_function_to_submobject_positions(function: MappingFunction) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `function` | callable | — | a point-to-point mapping `f(point) -> point` (`apply_matrix` takes a matrix; `apply_complex_function` treats `(x, y)` as a complex number) |
| `about_point` | point or `None` (keyword) | `None` | the transform's reference point; if omitted it defaults to **the origin**. Plain ManimCE 0.21's `VMobject.apply_function` / `apply_complex_function` **silently ignore** it (an upstream bug); inside an RTM process it **is honoured** (the embedded copy forwards it plus a runtime patch in `homotopy.py` — see the note). The samples all deform about the origin so that they compare frame by frame with unpatched CE |
| `about_edge` | vector or `None` (keyword) | `None` | the transform's reference edge |

> **Returns**: self. The first three act on **every vertex** (a true deformation); the last two only move **centres** (`apply_function_to_position` moves the mobject's own centre, `apply_function_to_submobject_positions` moves each submobject's centre) and do not change the shape.

#### Sample: five per-point / position transforms

Three circles demonstrate, in turn, a per-point shear (`apply_function`), a matrix shear (`apply_matrix`) and a complex mapping (`apply_complex_function`) — **all deforming about the origin** and then moved away; the two dots below demonstrate the two position variants that only move the centre.

```python
import numpy as np

from real_time_manim import Scene, Circle, Dot, VGroup, \
    BLUE, RED, GREEN, YELLOW, TEAL, UP, DOWN, LEFT, RIGHT
from real_time_manim.vulkan_bind import MLWindow, Wait

class ApplyDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        c1 = Circle(radius=0.8, color=BLUE, fill_opacity=0.4)   #first circle: deform at the origin first
        self.add(c1)   #add to the scene
        win.play(c1.animate.apply_function(
            lambda p: np.array([p[0], p[1] + 0.55 * p[0], p[2]])), run_time=0.6)   #per-point mapping: y rises with x = a shear
        win.play(c1.animate.move_to(LEFT * 4.2 + UP * 1.4), run_time=0.4)   #after deforming, move it to the upper left
        c2 = Circle(radius=0.8, color=RED, fill_opacity=0.4)   #second circle: also at the origin first
        self.add(c2)   #add to the scene
        win.play(c2.animate.apply_matrix(
            np.array([[1.0, 0.45, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])), run_time=0.6)   #linear transform: shear
        win.play(c2.animate.move_to(UP * 1.4), run_time=0.4)   #after deforming, move it to the top centre
        c3 = Circle(radius=0.8, color=GREEN, fill_opacity=0.4)   #third circle: also at the origin first
        self.add(c3)   #add to the scene
        win.play(c3.animate.apply_complex_function(
            lambda z: np.exp(z) * 0.5), run_time=0.6)   #complex mapping: the circle becomes a bean shape
        win.play(c3.animate.move_to(RIGHT * 4.2 + UP * 1.4), run_time=0.4)   #after deforming, move it to the upper right
        d1 = Dot(color=YELLOW, radius=0.13).shift(LEFT * 3.0 + DOWN * 1.6)   #a dot whose centre alone moves
        self.add(d1)   #add to the scene
        win.play(d1.animate.apply_function_to_position(lambda p: p + RIGHT * 1.6), run_time=0.5)   #move only its own centre
        pair = VGroup(Dot(color=TEAL, radius=0.13), Dot(color=TEAL, radius=0.13))   #two submobjects
        pair.arrange(RIGHT, buff=0.4).shift(RIGHT * 1.2 + DOWN * 1.6)
        self.add(pair)   #add to the scene
        win.play(pair.animate.apply_function_to_submobject_positions(lambda p: p + UP * 0.8), run_time=0.5)   #shift each submobject's centre by its own amount
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: all three circles **deform at the origin first, then move away** — the blue circle's `apply_function` raises each point's y by its x (the circle skews into a shear), the red circle's `apply_matrix` shears with a 3×3 matrix (the same skew, written more mathematically), and the green circle's `apply_complex_function` treats `(x, y)` as a complex number and applies the mapping `0.5·e^{z}` (the circle becomes a bean shape); each is then placed at the upper left / top centre / upper right with a single `move_to`. In the bottom row the yellow dot's `apply_function_to_position` only translates its own centre (a dot has no shape to deform), and the teal pair uses `apply_function_to_submobject_positions` to move each submobject's centre up by 0.8 while keeping the spacing.

<video src="assets/RTM output/04b-Scaling-Rotation-and-Stretching-Advanced-apply.mp4" controls width="560"></video>

> Note: **an upstream bug in plain ManimCE 0.21; fixed on the RTM side**.
>
> The implementation of `VMobject.apply_function` drops `about_point` / `about_edge` (it only calls `super.apply_function(function)` internally), so **in plain CE** `apply_function` and `apply_complex_function` on vector objects such as `Circle` / `Square` / `Text` **do not take effect even if you pass `about_point`** — they always use the origin (in tests the object gets flung away entirely); `apply_matrix` and `apply_points_function_about_point` are unaffected and honour the reference point normally.
>
> **In an RTM process this does not hold**: the embedded copy `real_time_manim/manim/mobject/types/vectorized_mobject.py` already forwards the reference point to `super`, and the idempotent runtime patch in `animations/homotopy.py` also fixes the case where an **external manim was imported first**, so under RTM `apply_function(about_point=)` is honoured. The samples keep the workaround of "**move the object to the origin, then deform**" only so that they compare frame by frame with unpatched CE.
>
> The two "position" functions change the centre **instantly**; you only get a transition in combination with `.animate`. They do not change the shape — to change the shape, use the first three.

### apply_points_function_about_point

```python
def apply_points_function_about_point(func: MultiMappingFunction,
                                      about_point: Point3DLike | None = None,
                                      about_edge: Vector3DLike | None = None) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `func` | callable | — | a function that processes a **point array** in bulk: `f(points) -> points`, where `points` has shape `(N, 3)` |
| `about_point` | point or `None` | `None` | the transform's reference point |
| `about_edge` | vector or `None` | `None` | the transform's reference edge |

> **Returns**: self. Internally it takes three steps — "translate to the reference point → apply `func` → translate back" — and is the **shared foundation** of almost every geometric transform such as `scale` / `rotate` / `stretch`. Day to day, `scale` / `rotate` are enough; touch it directly only when you need to change a whole block of points at once.

#### Sample: processing a point array in bulk

A horizontal line first multiplies its point array by 1.6 about its own centre (scaling the whole thing up), then translates the whole thing down by 1.4.

```python
import numpy as np

from real_time_manim import Scene, Line, \
    BLUE, UP, ORIGIN
from real_time_manim.vulkan_bind import MLWindow, Wait

class PointsFuncDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        ln = Line(LEFT * 1.5, RIGHT * 1.5, color=BLUE)   #a horizontal segment
        ln.shift(UP * 1.5)
        self.add(ln)   #add to the scene
        win.play(ln.animate.apply_points_function_about_point(
            lambda pts: pts * 1.6, about_point=ln.get_center()), run_time=0.6)   #process points in bulk: scale 1.6 about the centre
        win.play(ln.animate.apply_points_function_about_point(
            lambda pts: pts + np.array([0.0, -1.4, 0.0]), about_point=ORIGIN), run_time=0.6)   #bulk translate: shift the whole thing down
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: a horizontal line first calls `apply_points_function_about_point(lambda pts: pts * 1.6, about_point=center)` — multiplying the **whole point array** (shape `(N, 3)`) by 1.6; since the reference point is the line's own centre, the effect is a proportional scale about that centre. The second call passes `lambda pts: pts + [0, -1.4, 0]` to shift the whole block of points down by 1.4 (translation is insensitive to the reference point). `func` receives the entire array at once, computing all points in one go — faster than a per-point loop over `f(point)`.

<video src="assets/RTM output/04b-Scaling-Rotation-and-Stretching-Advanced-points_func.mp4" controls width="560"></video>

> Note: `func` takes and returns an `(N, 3)` array and **must return the same shape**; changing the number of points garbles rendering. Its difference from `apply_function` is "the whole block of points at once" vs. "a per-point callback" — the former is smoother for whole-object scaling/translation, the latter for computing from each point's position. For a "custom transform", prefer the off-the-shelf methods `scale` / `stretch` first.

### repeat / reverse_points

```python
def repeat(count: int) -> Self
def reverse_points() -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `count` | `int` | — | how many times the vertex sequence is repeated (`repeat` only) |

> **Returns**: self. `repeat(n)` copies the vertex sequence n times as-is — **the appearance is unchanged** while the point count doubles, which can make some transition animations smoother; `reverse_points()` swaps the start and end of the path (usually leaving the appearance unchanged too, but `get_start` / `point_from_proportion` all flip). Both act on the whole family tree.

#### Sample: `reverse_points` flips direction, `repeat` doubles the point count

An open arc: a red dot marks the 25% point of the path, and after `reverse_points()` it jumps to the other end of the arc as the direction flips; then `repeat(2)` takes the point count from 32 to 64.

```python
from real_time_manim import Scene, Arc, Dot, \
    YELLOW, RED, TAU
from real_time_manim.vulkan_bind import MLWindow, Wait

class RepeatRevDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        arc = Arc(radius=1.5, start_angle=0, angle=TAU * 0.7, color=YELLOW)   #an open arc: start and end clearly distinct
        mark = Dot(color=RED, radius=0.09).move_to(arc.point_from_proportion(0.25))   #a marker at 25% of the path
        self.add(arc, mark)   #add to the scene
        arc.reverse_points()   #reverse the path direction: start and end swap (the arc's appearance is unchanged)
        win.play(mark.animate.move_to(arc.point_from_proportion(0.25)), run_time=0.5)   #the 25% point jumps to the other end with the direction
        print("points before repeat =", len(arc.points))   #the point count after the reversal
        arc.repeat(2)   #repeat the vertex sequence twice: the appearance is unchanged
        print("points after repeat =", len(arc.points))   #doubled
        win.play(Wait(0.5))   #wait 0.5s
        win.close()   #close the RTM window
```

What this code does: on a 252° yellow arc, the red dot marks the position "25% of the way from the start" (the upper right of the arc). `reverse_points()` swaps the path's start and end — the arc's shape does not change at all, but "25%" now counts from the **new start** (the old end), so the red dot jumps to the lower left of the arc: visual proof of the direction change. Then `repeat(2)` pastes the vertex sequence again as-is, the arc looks identical, and the console prints the point count going from 32 to 64.

<video src="assets/RTM output/04b-Scaling-Rotation-and-Stretching-Advanced-repeat_rev.mp4" controls width="560"></video>

> Note: `repeat` / `reverse_points` change the **point sequence**, not the appearance, so do not expect the picture to change (the samples verify it by printing the point count and the dot's position). After a reversal `get_start()` / `get_end()` swap, and `point_from_proportion` / `proportion_from_point`, which depend on the path direction, all compute along the new direction; after `repeat` the meaning of the proportion passed to `point_from_proportion` changes as well (the path is now doubled), so remember not to keep using old proportions as anchors.

---

See also: [Scaling, Rotation and Stretching](04-Scaling-Rotation-and-Stretching.md) | [Measurement](03-Measurement.md)
