# Measurement: reading sizes and positions

Reading bounding-box sizes and the coordinates of the various critical points — the basis of placement, alignment and writing updaters. They are all read-only queries (except the three properties such as `width`), and change no object state.

## Parameters

### width / height / depth (properties, read/write)

```python
mob.width / mob.height / mob.depth -> float
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| (read) | `float` | — | returns the bounding box's width / height / depth; `depth` is `0` for a flat object |
| (assign) | `float` | — | assignment is equivalent to `scale_to_fit_width(...)` etc. — a **uniform** scale to the target size; the statement returns nothing |

> **Returns**: reading gives a `float`. For "width becomes x without distortion" use `stretch_to_fit_width` (see [04b-Scaling-Rotation-and-Stretching-Advanced](04b-Scaling-Rotation-and-Stretching-Advanced.md)).

#### Sample: reading and assigning

A 4×2 rectangle: first the three sizes are printed, then `width` is assigned 2.0 (height scales uniformly to 1.0), then `height` is assigned 3.0 (width scales uniformly to 6.0).

```python
from real_time_manim import Scene, Rectangle, \
    BLUE
from real_time_manim.vulkan_bind import MLWindow, Wait

class SizeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        rect = Rectangle(width=4.0, height=2.0, color=BLUE, fill_opacity=0.4)   # a 4×2 rectangle
        self.add(rect)   # add it to the scene
        print("initial: width =", rect.width, "height =", rect.height, "depth =", rect.depth)   # 4.0 2.0 0.0
        win.play(rect.animate.set(width=2.0), run_time=0.6)   # assigning "width" = a uniform scale
        print("after width=2.0: width =", rect.width, "height =", rect.height)   # 2.0 1.0: the height scales uniformly too
        win.play(rect.animate.set(height=3.0), run_time=0.6)   # assigning "height": uniform scale up
        print("after height=3.0: width =", rect.width, "height =", rect.height)   # 6.0 3.0
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window
```

What this code does: a 4×2 rectangle goes on screen, first printing `width=4.0 height=2.0 depth=0.0`; playing `set(width=2.0)` makes the width 2 — note that the height scales **uniformly** to 1.0, so the aspect ratio is unchanged; then playing `set(height=3.0)` makes the width grow to 6.0 along with it. The two console lines are the evidence that "assignment is a uniform scale".

<video src="assets/RTM output/03-Measurement-size.mp4" controls width="560"></video>

> Note: assigning a property is a **uniform** scale (it goes through `scale_to_fit_*` underneath); to widen only, without changing the height, use `stretch_to_fit_width` or `stretch`. Reads always give the bounding-box size — `Text` measures the line-gap space in as well, so watch out when doing a snug layout.

### get_center / get_top / get_bottom / get_left / get_right

```python
def get_center() -> Point3D
def get_top() -> Point3D   # get_bottom / get_left / get_right same shape
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| (all take no arguments) | — | — | — |

> **Returns**: `np.ndarray`, shape `(3,)`. The coordinates of the bounding-box center and the four edge midpoints respectively; pair with `next_to(..., UP, buff=0)` for a flush fit.

#### Sample: marking the center and the four edge midpoints

A 2.4-by-2.4 square; five red dots mark `get_center` / `get_top` / `get_bottom` / `get_left` / `get_right`, and the coordinates are printed as well.

```python
from real_time_manim import Scene, VGroup, Square, Dot, \
    BLUE, RED, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class EdgesDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=2.4, fill_opacity=0.4)   # a 2.4-by-2.4 square
        self.add(sq)   # add it to the scene
        marks = VGroup()   # critical-point markers
        for name, p in (
            ("center", sq.get_center()),
            ("top", sq.get_top()),
            ("bottom", sq.get_bottom()),
            ("left", sq.get_left()),
            ("right", sq.get_right()),
        ):   # the center and the four edge midpoints
            marks.add(Dot(color=RED, radius=0.08).move_to(p))   # drop a red dot on the critical point
            print(name, "=", p.round(2))   # print the coordinate to verify
        self.add(marks)   # add the markers to the scene
        win.play(FadeIn(marks), run_time=0.5)   # fade in the five red dots
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window
```

What this code does: a red dot is dropped on each of the 2.4-by-2.4 square's five critical points — the middle, the top-edge midpoint, the bottom-edge midpoint, the left-edge midpoint and the right-edge midpoint — so which position each method returns is plain at a glance; the console prints the coordinates as well (e.g. `top = [0. 1.2 0.]`), confirming the frame.

<video src="assets/RTM output/03-Measurement-edges.mp4" controls width="560"></video>

> Note: these are the **bounding box**'s edge midpoints, not points on the shape's contour — for a circle `get_top()` is the tangent point at the very top, which is fine, but for an angled line `get_left()` is the box's left midpoint rather than the line's left endpoint (use `get_start` / `get_end` for endpoints, see [11b-Misc-APIs](11b-Misc-APIs.md)).

### get_x / get_y / get_z / get_coord / get_corner / get_edge_center / get_critical_point

```python
def get_x(direction: Vector3DLike = ORIGIN) -> float   # get_y / get_z same shape
def get_coord(dim: int, direction: Vector3DLike = ORIGIN) -> float
def get_corner(direction: Vector3DLike) -> Point3D
def get_edge_center(direction: Vector3DLike) -> Point3D
def get_critical_point(direction: Vector3DLike) -> Point3D
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `direction` | vector | `ORIGIN` (required for `get_corner` etc.) | the component **signs** select the critical point (a zero component takes the middle value), e.g. `UR`=top-right corner, `DOWN`=bottom-edge midpoint |
| `dim` | `int` | — | **only** `0`=x, `1`=y, `2`=z (`get_coord` only) |

> **Returns**: `get_x` / `get_y` / `get_z` / `get_coord` return `float`; the last three return `np.ndarray`. `get_corner` / `get_edge_center` are semantic aliases of `get_critical_point` (same implementation); `get_coord` is the general version of `get_x` / `get_y` / `get_z`. The single-component reads such as `get_x()` are the most common when writing updaters.

#### Sample: reading single coordinates and corner points

A square moved right by 1.5: it prints `get_x` / `get_x(LEFT)` / `get_y` / `get_z` / `get_coord`, then drops red dots on `get_corner(UR)` / `get_edge_center(DOWN)` / `get_critical_point(LEFT)`.

```python
from real_time_manim import Scene, VGroup, Square, Dot, \
    GREEN, RED, UR, DOWN, LEFT, RIGHT, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class CoordsGetDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        sq = Square(color=GREEN, side_length=2.0).shift(RIGHT * 1.5)   # a square moved right by 1.5
        self.add(sq)   # add it to the scene
        print("get_x =", sq.get_x(), "| get_x(LEFT) =", sq.get_x(direction=LEFT))   # 1.5 0.5
        print("get_y =", sq.get_y(), "| get_z =", sq.get_z())   # 0.0 0.0
        print("get_coord(0, UR) =", sq.get_coord(0, UR))   # the x of the UR corner
        marks = VGroup()   # critical-point markers
        for name, p in (
            ("corner(UR)", sq.get_corner(UR)),
            ("edge_center(DOWN)", sq.get_edge_center(DOWN)),
            ("critical_point(LEFT)", sq.get_critical_point(LEFT)),
        ):   # corner / edge midpoint / general critical point
            marks.add(Dot(color=RED, radius=0.08).move_to(p))   # drop a red dot on the critical point
            print(name, "=", p.round(2))   # print the coordinate to verify
        self.add(marks)   # add the markers to the scene
        win.play(FadeIn(marks), run_time=0.5)   # fade in the red dots
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window
```

What this code does: a square of side 2 is moved right by 1.5, so its center is at x=1.5 and its left edge at x=0.5 — `get_x()` with no argument reads the center, `get_x(direction=LEFT)` reads the left edge, exactly the read-back version of `set_x(..., direction=...)`. Then three red dots land on the top-right corner, the bottom-edge midpoint and the left-edge midpoint, with `get_corner` / `get_edge_center` / `get_critical_point` each in its place; `get_coord(0, UR)` is equivalent to `get_x(UR)`, printed to verify.

<video src="assets/RTM output/03-Measurement-coords.mp4" controls width="560"></video>

> Note: `direction` looks at the sign only, not the magnitude; `UR` and `UP + RIGHT` are the same thing; `get_critical_point` is the underlying general version, and `get_corner` / `get_edge_center` are just memorable aliases with no performance difference. `get_z` is always 0 for flat objects and is only useful in a 3D scene.

### length_over_dim / get_all_points

```python
def length_over_dim(dim: int) -> float
def get_all_points() -> Point3D_Array
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `dim` | `int` | — | **only** `0` width, `1` height, `2` depth |

> **Returns**: `length_over_dim` returns the length along that dimension (the underlying implementation of `width` / `height`), and `0` for an empty object; `get_all_points` returns an array of shape `(N, 3)` — self's and **all descendants'** vertices concatenated depth-first, possibly with duplicates.

#### Sample: dimension lengths and the point cloud

A circle of radius 1.2: it prints the three dimension lengths (2.4 / 2.4 / 0.0), then drops a small red dot on each of `get_all_points()`'s 32 vertices — the distribution of the Bézier control points is plain to see.

```python
from real_time_manim import Scene, VGroup, Circle, Dot, \
    YELLOW, RED, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class MeasurePointsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        circ = Circle(radius=1.2, color=YELLOW)   # a circle of radius 1.2
        self.add(circ)   # add it to the scene
        print("length_over_dim(0/1/2) =", [float(circ.length_over_dim(i)) for i in range(3)])   # 2.4 2.4 0.0
        pts = circ.get_all_points()   # all vertices of self and every descendant
        print("get_all_points =", pts.shape)   # (32, 3)
        cloud = VGroup(*[Dot(color=RED, radius=0.03).move_to(p) for p in pts])   # a small red dot on each vertex
        self.add(cloud)   # add the point cloud to the scene
        win.play(FadeIn(cloud), run_time=0.6)   # fade in the point cloud: the Bézier control points
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window
```

What this code does: for a circle of radius 1.2, `length_over_dim` over the three dimensions is width 2.4, height 2.4, depth 0.0 (a flat object); `get_all_points()` pulls out all 32 of the circle's Bézier control points (shape `(32, 3)`), and a small red dot is dropped on each — on screen you can see the anchors land on the circle while the handles sit slightly outside it, which is what "vertices" really means.

<video src="assets/RTM output/03-Measurement-points.mp4" controls width="560"></video>

> Note: `get_all_points` concatenates the vertices of the **whole family tree** (including children), so N grows large when objects are deeply nested; if you just want to measure size, use `width` / `length_over_dim` rather than computing a bounding box from the array. Control points ≠ points on the stroke; to get a position on a curve use `point_from_proportion` (see [11b-Misc-APIs](11b-Misc-APIs.md)).

### Center of mass, the boundary-point family, and low-level stats

```python
def get_center_of_mass() -> Point3D   # vertex mean
def get_midpoint() -> Point3D          # point at path 50%
def get_boundary_point(direction: Vector3DLike) -> Point3D
def get_zenith() / get_nadir() -> Point3D   # OUT / IN face center in 3D
def get_z_index_reference_point() -> Point3D
def get_points_defining_boundary() -> Point3D_Array
def get_merged_array(array_attr: str) -> np.ndarray
def get_extremum_along_dim(points=None, dim=0, key=0) -> float
def reduce_across_dimension(reduce_func, dim) -> float | None
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `direction` | vector | — | `get_boundary_point` only: the farthest vertex along the direction |
| `array_attr` | `str` | — | attribute-name string, e.g. `"points"`, concatenating that array over the family tree |
| `points` | point array or `None` | `None` | the point set to use; `None` uses own points |
| `dim` | `int` | `0` | dimension |
| `key` | `int` | `0` | `1` max, `-1` min, `0` median |
| `reduce_func` | callable | — | reduction function, e.g. `max` |

> **Returns**: the first few return `np.ndarray` (`get_midpoint` equals `point_from_proportion(0.5)`); `get_points_defining_boundary` defaults to the same as `get_all_points` on the base class, while the `VMobject` family takes only contour sample points (a circle measures 16 vs 32 in total); `get_extremum_along_dim` / `reduce_across_dimension` return `float` (`None` for an empty object). **Most users never need to call these directly** (`get_top` / `length_over_dim` already wrap them).

#### Sample: center of mass, boundary points and stats

A circle of radius 1.4: five red dots mark the vertex mean, the path midpoint, the farthest point in the UR direction, the zenith and the sorting reference point; then the values of `get_extremum_along_dim` / `reduce_across_dimension` / `get_merged_array` / `get_points_defining_boundary` are printed to the console.

```python
from real_time_manim import Scene, VGroup, Circle, Dot, \
    BLUE, RED, UR, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class StatsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        c = Circle(radius=1.4, color=BLUE)   # a circle of radius 1.4
        self.add(c)   # add it to the scene
        marks = VGroup()   # critical-point markers
        for name, p in (
            ("center_of_mass", c.get_center_of_mass()),
            ("midpoint", c.get_midpoint()),
            ("boundary_point(UR)", c.get_boundary_point(UR)),
            ("zenith", c.get_zenith()),
            ("z_index_ref", c.get_z_index_reference_point()),
        ):   # center of mass and the boundary-point family (the zenith of a flat object falls on the center)
            marks.add(Dot(color=RED, radius=0.07).move_to(p))   # drop a red dot on the critical point
            print(name, "=", p.round(2))   # print the coordinate to verify
        self.add(marks)   # add the markers to the scene
        print("get_extremum_along_dim(key=1/-1) =", c.get_extremum_along_dim(dim=0, key=1), c.get_extremum_along_dim(dim=0, key=-1))   # rightmost / leftmost x
        print("reduce_across_dimension(max, 0) =", c.reduce_across_dimension(max, 0))   # reduce max over x
        print("get_merged_array('points') =", c.get_merged_array("points").shape)   # concatenation of the family's vertices
        print("get_points_defining_boundary =", c.get_points_defining_boundary().shape)   # contour sample points
        win.play(FadeIn(marks), run_time=0.5)   # fade in the red dots
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window
```

What this code does: five red dots are dropped on a circle of radius 1.4 — `get_center_of_mass` (the vertex mean, landing on the circle's center), `get_midpoint` (the point at path 50%, landing on the **circumference**, different from the former!), `get_boundary_point(UR)` (the farthest vertex in the UR direction), `get_zenith` (a flat object has no z thickness, so it lands on the center) and `get_z_index_reference_point` (the sorting reference point, also the center). The console then prints four low-level stats: the rightmost/leftmost x, the max reduced over x, the family-concatenation shape of the `points` array (32, 3), and the contour sample-point shape (16, 3).

<video src="assets/RTM output/03-Measurement-stats.mp4" controls width="560"></video>

> Note:
>
> - `get_center_of_mass` is the **vertex mean** and `get_midpoint` is the **path midpoint**; for a circle one is at the center and the other on the circumference, so don't mix them up.
> - `get_zenith` / `get_nadir` are only meaningful for 3D objects.
> - `get_extremum_along_dim` / `reduce_across_dimension` are what back methods such as `get_top`; they return `None` rather than 0 for an empty object, so guard against empties before using them in arithmetic.

---

See also: [Positioning](02-Positioning.md) · [Updaters](08-Updaters.md)
