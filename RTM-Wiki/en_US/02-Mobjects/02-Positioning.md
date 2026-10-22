# Positioning

Put an object where you want it in the frame: translate, align, snap to an edge, snap to a corner. All the methods below return `self` and can be chained.

## Parameters

### shift

```python
def shift(*vectors: Vector3DLike) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*vectors` | `np.ndarray` / coordinate tuple | — | displacement vector(s). **Accepts** combinations of vector constants such as `RIGHT * 2`, `UP + LEFT`; **takes several**, summed internally into one move |

> **Returns**: `self`. Acts on itself and all children (what actually moves is the set of vertices in `family_members_with_points()`). This is the most basic placement method; `next_to` / `to_edge` and the rest ultimately land on it.

#### Sample: `shift` with one vector and with several

The square first moves right along one vector, then is given two vectors at once (summed internally to move left 4 and up 1.2), and finally is translated one step instantly without `animate`.

```python
from real_time_manim import Scene, Square, \
    BLUE, UP, DOWN, LEFT, RIGHT
from real_time_manim.vulkan_bind import MLWindow, Wait

class ShiftDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.4, fill_opacity=0.6)   # blue square
        self.add(sq)   # add it to the scene
        win.play(sq.animate.shift(RIGHT * 2.0), run_time=0.5)   # translate along one vector: right 2
        win.play(sq.animate.shift(UP * 1.2, LEFT * 4.0), run_time=0.6)   # several vectors: summed internally, moving left 4 and up 1.2
        sq.shift(DOWN * 2.4, RIGHT * 1.2)   # without "animate" the move is instant: down 2.4 + right 1.2
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window
```

What this code does: a blue square first slides smoothly right along `RIGHT * 2`; then `shift(UP * 1.2, LEFT * 4.0)` passes two vectors at once and adds them internally (equal to `LEFT * 4 + UP * 1.2`) before moving; the last step has no `.animate`, an instant direct translation. Each step starts where the previous one ended — `shift` is relative movement, so repeated calls accumulate.

<video src="assets/RTM output/02-Positioning-shift.mp4" controls width="560"></video>

> Note: `shift` is a **relative** amount: `shift(RIGHT * 2)` means "2 more to the right", not "to x=2"; for absolute coordinates use `move_to` or `set_x` / `set_y`. Several vector arguments are equivalent to one vector `a + b`; pick whichever reads better.

### move_to

```python
def move_to(point_or_mobject: Point3DLike | Mobject,
            aligned_edge: Vector3DLike = ORIGIN,
            coor_mask: Vector3DLike = [1, 1, 1]) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `point_or_mobject` | point coordinates / `Mobject` | — | target point. **Accepts** coordinates such as `[2, 1, 0]`, `RIGHT * 2`, or another object (uses its critical point) |
| `aligned_edge` | vector | `ORIGIN` | which **own** critical point aligns: `ORIGIN`=center, `UR`=top-right corner, `UP`=top-edge midpoint, … |
| `coor_mask` | vector | `[1, 1, 1]` | only axes whose mask is 1 take effect. **Accepts** things such as `np.array([1, 0, 0])` (align x only) |

> **Returns**: `self`. The general entry for "align to something": move the critical point at `aligned_edge` of self to the target point, then filter out the axes you do not want to move with `coor_mask`.

#### Sample: three ways to align with `move_to`

The square aims at a target point in the upper left: first the default center-to-center, then aligning its top-right corner to a top-right target point, and finally `coor_mask` aligning only x while y stays put.

```python
import numpy as np

from real_time_manim import Scene, Square, Dot, \
    RED, YELLOW, UP, DOWN, LEFT, RIGHT, UR
from real_time_manim.vulkan_bind import MLWindow, Wait

class MoveToDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        dot = Dot(color=YELLOW, radius=0.12)   # target point
        dot.move_to(LEFT * 3.0 + UP * 1.6)   # put the target point in the upper left
        sq = Square(color=RED, side_length=1.2, fill_opacity=0.6)   # the square to move
        self.add(dot, sq)   # add both to the scene
        win.play(sq.animate.move_to(dot), run_time=0.6)   # default center-to-center
        win.play(sq.animate.move_to(RIGHT * 3.0 + UP * 1.6, aligned_edge=UR), run_time=0.6)   # align its own top-right corner to the target point
        win.play(sq.animate.move_to(RIGHT * 3.0 + DOWN * 1.8, coor_mask=np.array([1, 0, 0])), run_time=0.6)   # align x only, y stays put
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window
```

What this code does: a small yellow dot is placed in the upper left of the frame as the target, and the red square moves in three steps. The first, `move_to(dot)`, adds nothing, so the square's **center** goes to the target point; the second, `aligned_edge=UR`, aligns the square's **top-right corner** to a top-right target point instead, so the square sits down-left of the target point; the third, `coor_mask=np.array([1, 0, 0])`, masks the y axis, so although the target point is below, the square only moves in x and keeps its height.

<video src="assets/RTM output/02-Positioning-move_to.mp4" controls width="560"></video>

> Note: `aligned_edge` uses **own** critical point (`UR` = place its own top-right corner on the target), and it is only when an `Mobject` is passed that the other object's critical point is used. `coor_mask` is a per-axis multiplier mask; `[1, 0, 0]` means "x only", handy for effects such as "x follows, y stays put".

### next_to

```python
def next_to(mobject_or_point: Mobject | Point3DLike,
            direction: Vector3DLike = RIGHT, buff: float = 0.25,
            aligned_edge: Vector3DLike = ORIGIN,
            submobject_to_align: Mobject | None = None,
            index_of_submobject_to_align: int | None = None,
            coor_mask: Vector3DLike = [1, 1, 1]) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject_or_point` | `Mobject` / point coordinates | — | the reference. **Accepts** another object or a point |
| `direction` | vector | `RIGHT` | which side of the reference to sit on. **Accepts** `UP` / `DOWN` / `LEFT` / `RIGHT` and diagonal directions |
| `buff` | `float` | `0.25` | the gap between the two |
| `aligned_edge` | vector | `ORIGIN` | which own critical point to attach with. The points matched are "the reference's `aligned_edge+direction` critical point" against "own `aligned_edge-direction` critical point" — e.g. `aligned_edge=DOWN` + `direction=RIGHT` puts own bottom-left corner against the reference's bottom-right corner (bottom edges aligned) |
| `submobject_to_align` | `Mobject` or `None` | `None` | name one of **own** children to align with; the parent translates as a whole |
| `index_of_submobject_to_align` | `int` or `None` | `None` | align with "own i-th child" by index; when the reference is an `Mobject`, its i-th child is **also** taken as the target |
| `coor_mask` | vector | `[1, 1, 1]` | only axes whose mask is 1 take effect |

> **Returns**: `self`. The most common method for labels and layout: internally it computes the displacement as "reference critical point - own critical point + buff×direction" and hands it to `shift`.

#### Sample: direction, gap and alignment with `next_to`

A blue square sits in the middle, and each side demonstrates one kind of alignment: the right neighbor gets `buff=0.3` (vertically centered), the top neighbor `direction=UP` (horizontally centered), and another right neighbor uses `aligned_edge=DOWN` to show bottom-edge alignment. The group on the left uses `submobject_to_align` to attach by its second child; the bottom demonstrates `index_of_submobject_to_align`, taking a child on both sides at the same index.

```python
from real_time_manim import Scene, Square, VGroup, \
    BLUE, RED, GREEN, PURPLE, ORANGE, TEAL, YELLOW, WHITE, \
    UP, DOWN, LEFT, RIGHT, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class NextToDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        box = Square(color=BLUE, side_length=1.6, fill_opacity=0.6)   # the reference
        self.add(box)   # add it to the scene
        right = Square(color=RED, side_length=0.8).next_to(box, RIGHT, buff=0.3)   # direction / buff: vertically centered on the right
        up = Square(color=GREEN, side_length=0.8).next_to(box, UP, buff=0.2)   # direction=UP: horizontally centered above
        low = Square(color=ORANGE, side_length=0.8).next_to(box, RIGHT, buff=1.2, aligned_edge=DOWN)   # aligned_edge=DOWN: bottom edges aligned, not vertically centered
        duo = VGroup(Square(color=PURPLE, side_length=0.5), Square(color=TEAL, side_length=0.5))   # two small squares as one group
        duo.arrange(DOWN, buff=0.2)   # stack them vertically
        duo.next_to(box, LEFT, buff=0.3, submobject_to_align=duo[1])   # attach by its own second child
        self.add(right, up, low, duo)   # add the four neighbors to the scene
        win.play(FadeIn(right), FadeIn(up), run_time=0.5)   # fade in the right and top neighbors
        win.play(FadeIn(low), FadeIn(duo), run_time=0.5)   # fade in the bottom-aligned one and the left group
        ref = VGroup(Square(color=TEAL, side_length=0.6), Square(color=TEAL, side_length=0.6))   # reference group: two children
        ref.arrange(RIGHT, buff=0.2).shift(DOWN * 2.3)   # put it at the bottom
        self.add(ref)   # add it to the scene
        tag = VGroup(Square(color=YELLOW, side_length=0.3), Square(color=WHITE, side_length=0.3))   # two-part marker
        tag.arrange(RIGHT, buff=0.1)   # line them up in a row
        tag.next_to(ref, UP, buff=0.25, index_of_submobject_to_align=1)   # both self and the reference align by their 2nd child
        self.add(tag)   # add it to the scene
        win.play(FadeIn(ref), FadeIn(tag), run_time=0.5)   # fade in the reference group and the marker
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window
```

What this code does: a blue square goes in the middle as the reference, and the parameters of `next_to` are demonstrated all around it.

- The red square on the right is given only `direction` and `buff`, and is vertically centered with the reference.
- The green square above has `direction=UP` and is horizontally centered.
- The orange square also snaps to the right but is given `aligned_edge=DOWN`, so its **bottom edge** is aligned with the reference instead of being vertically centered.
- The left group of two small squares uses `submobject_to_align=duo[1]`, attaching by its **second child**, and the whole group shifts left with it.

The reference group at the bottom has two children, and `index_of_submobject_to_align=1` makes both the marker group and the reference take their 2nd child for the match, so the yellow-white marker sits right above the reference group's right half.

<video src="assets/RTM output/02-Positioning-next_to.mp4" controls width="560"></video>

> Note:
>
> - `aligned_edge` is not as simple as "which corner of self attaches" — the actual points matched are the reference's `aligned_edge+direction` and self's `aligned_edge-direction`, so the direction takes part; work through that formula before writing it or the result is off.
> - `submobject_to_align` takes priority over `index_of_submobject_to_align`.
> - `index_of_submobject_to_align` uses the **same index** on both self and the reference, so mismatched child counts easily pick the wrong slot.
> - `buff` is the gap along `direction`; when the direction is a diagonal, the gap is measured along the diagonal too.

### to_edge / to_corner

```python
def to_edge(edge: Vector3DLike = LEFT, buff: float = 0.5) -> Self
def to_corner(corner: Vector3DLike = DL, buff: float = 0.5) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `edge` | vector | `LEFT` | **only** `UP` / `DOWN` / `LEFT` / `RIGHT` are accepted |
| `corner` | vector | `DL` | **only** `UL` / `UR` / `DL` / `DR` are accepted |
| `buff` | `float` | `0.5` | margin from the edge/corner |

> **Returns**: `self`. `to_edge` changes only the coordinate of the edge's axis, leaving the other axis untouched (internally it is `align_on_border`, see [02b-Positioning-Advanced](02b-Positioning-Advanced.md)).

#### Sample: snapping to edges and corners with `to_edge` / `to_corner`

Four small squares snap to the top, bottom and left edges and to the top-right corner; the one snapping left is raised 1.2 first, to verify that its y coordinate is not changed.

```python
from real_time_manim import Scene, Square, ScreenRectangle, \
    RED, BLUE, GREEN, YELLOW, GREY, UP, LEFT, DOWN, UR, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class EdgeCornerDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        frame = ScreenRectangle(height=6.8, color=GREY)   # a hint at the frame border
        self.add(frame)   # add it to the scene
        top = Square(color=RED, side_length=0.9)   # the square on the top edge
        bottom = Square(color=BLUE, side_length=0.9)   # the square on the bottom edge
        side = Square(color=GREEN, side_length=0.9)   # the square on the left edge
        corner = Square(color=YELLOW, side_length=0.9)   # the square at the top-right corner
        top.to_edge(UP, buff=0.3)   # snap to the top edge, margin 0.3
        bottom.to_edge(DOWN, buff=0.3)   # snap to the bottom edge
        side.shift(UP * 1.2)   # raise it a little first
        side.to_edge(LEFT, buff=0.3)   # snap to the left edge: the y coordinate is unaffected
        corner.to_corner(UR, buff=0.5)   # snap to the top-right corner, margin 0.5
        self.add(top, bottom, side, corner)   # add them all to the scene
        win.play(FadeIn(top), FadeIn(bottom), FadeIn(side), FadeIn(corner), run_time=0.6)   # fade in the four squares
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window
```

What this code does: a grey `ScreenRectangle` is drawn to hint at the frame border (what the squares actually snap to is the whole frame's edge, not this box), then the four small squares take their places — red on the top edge, blue on the bottom edge, yellow at the top-right corner, each offset by the margin; the green one is **raised 1.2 first** and then `to_edge(LEFT)`, and you can see it keeps its raised height after snapping to the left, proving that `to_edge` moves only the edge's axis.

<video src="assets/RTM output/02-Positioning-edge_corner.mp4" controls width="560"></video>

> Note: edge snapping refers to the **frame** (`config`'s frame width/height), not to a viewfinder such as `self.camera.frame` — when a MovingCamera pushes the shot, edge-snapped objects are pinned to the world-coordinate screen and can leave the frame as the camera moves. For a "pinned to the screen" effect you have to attach them to the camera frame (see [01-MovingCameraScene](../01-Scenes-and-Cameras/Special-Scenes/01-MovingCameraScene.md)).

### center / align_to

```python
def center() -> Self
def align_to(mobject_or_point: Mobject | Point3DLike,
             direction: Vector3DLike = ORIGIN) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| (`center` takes no arguments) | — | — | moves the center to the origin `(0, 0, 0)` |
| `mobject_or_point` | `Mobject` / point coordinates | — | alignment target |
| `direction` | vector | `ORIGIN` | only the axes of this direction's **non-zero components** are adjusted: `UP`/`DOWN` align y, `LEFT`/`RIGHT` align x, `ORIGIN` fully coincides |

> **Returns**: `self`. `align_to` is "flush along the given direction": `mob1.align_to(mob2, UP)` makes their top edges flush, moving only the y axis.

#### Sample: recentering with `center` and flushing with `align_to`

The blue square returns from the upper left to the origin; the yellow square becomes flush with the big red square's top edge via `align_to(big, UP)`, keeping its x coordinate unchanged.

```python
from real_time_manim import Scene, Square, \
    BLUE, RED, YELLOW, UP, LEFT, RIGHT
from real_time_manim.vulkan_bind import MLWindow, Wait

class CenterAlignDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.2, fill_opacity=0.6)   # blue square
        sq.shift(LEFT * 3.2 + UP * 1.4)   # move it to the upper left first
        self.add(sq)   # add it to the scene
        win.play(sq.animate.center(), run_time=0.6)   # center: back to the origin (0, 0, 0)
        big = Square(color=RED, side_length=2.0, fill_opacity=0.4)   # the big reference square
        big.shift(RIGHT * 3.2)   # put it on the right
        small = Square(color=YELLOW, side_length=1.0)   # the small square to align
        small.shift(RIGHT * 3.2 + UP * 1.8)   # place it a little higher first
        self.add(big, small)   # add them to the scene
        win.play(small.animate.align_to(big, UP), run_time=0.6)   # align_to: top edges flush, x unmoved
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window
```

What this code does: it first moves the blue square to the upper left, then plays `center()` to send it back to the middle of the frame — wherever it was, `center` zeroes it in one step. The big red square and the small yellow square on the right start at different heights, and `align_to(big, UP)` adjusts only the small square's y to be flush with the big square's top edge, leaving x completely untouched; that is the difference between `align_to` and `move_to`: it moves only the axes that are non-zero in `direction`.

<video src="assets/RTM output/02-Positioning-center_align.mp4" controls width="560"></video>

> Note: `center()` means **the middle of the frame**, not "its own center" — an object's own center is always its own center and needs no moving. To align several axes with `align_to`, pass a diagonal direction, e.g. `align_to(other, UR)` flushes both x and y at the top-right corner.

---

See also: [Positioning (advanced)](02b-Positioning-Advanced.md) · [Measurement](03-Measurement.md)
