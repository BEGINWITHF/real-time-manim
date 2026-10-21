# Basic shapes (1): arcs, circles, and dots

This section covers the most basic batch of shapes in geometry: the arc family (`Arc` / `ArcBetweenPoints` / `TangentialArc`), the curved arrow between two points, and circles and filled dots.

These classes are all defined in `mobject/geometry/arc.py`, with the inheritance chain `Arc → TipableVMobject → VMobject`. So they can take an arrow tip out of the box (see [Arrow tips](02b-Arrow-Tips.md)), and they can take fill and stroke styles too (see [VMobject styles](07-VMobject-Styles.md)).

All three samples on this page have been rendered and verified in RTM.

## Parameters

### Arc, ArcBetweenPoints (in `01-Basic-Shapes-arc.mp4`), TangentialArc (in `01-Basic-Shapes-arc.mp4`)

```python
def __init__(self, radius: float | None = 1.0, start_angle: float = 0,
             angle: float = TAU / 4, num_components: int = 9,
             arc_center: Point3DLike = ORIGIN, **kwargs: Any) -> None:  # Arc

def __init__(self, start: Point3DLike, end: Point3DLike,
             angle: float = TAU / 4, radius: float | None = None,
             **kwargs: Any) -> None:  # ArcBetweenPoints

def __init__(self, line1: Line, line2: Line, radius: float,
             corner: Any = (1, 1), **kwargs: Any) -> None:  # TangentialArc
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `radius` | `float \| None` | `1.0` (`Arc`) | arc radius, any positive number; in `ArcBetweenPoints` it defaults to `None` (derived from `angle`) |
| `start_angle` | `float` | `0` | (`Arc`) start angle (radians): 0 is straight right, counter-clockwise is positive |
| `angle` | `float` | `TAU/4` (90°) | sweep angle (radians): negative goes clockwise; `ArcBetweenPoints` / `TangentialArc` use it to control the bend direction and size |
| `num_components` | `int` | `9` | (`Arc`) number of segments in the arc, larger is smoother; **do not change**, the default is already enough |
| `arc_center` | `Point3DLike` | `ORIGIN` | (`Arc`) centre coordinates |
| `start` / `end` | `Point3DLike` | required | (`ArcBetweenPoints`) coordinates of the arc's two endpoints |
| `line1` / `line2` | `Line` | required | (`TangentialArc`) the two **line objects** that take part in the intersection (the intersection is computed internally to fix the arc centre), not direction vectors |
| `radius` | `float` | required | (`TangentialArc`) corner arc radius, **no default, you must pass it** |
| `corner` | `tuple[int,int]` | `(1, 1)` | (`TangentialArc`) pick one of `(±1, ±1)`, choosing the corner in one of the intersection's four quadrants |

> **Returns**: an arc object (an `Arc` subclass). Common read-only methods: `get_start()` / `get_end()` / `get_center()` (`Arc`), `get_arc_angle()` (the actual sweep angle).

#### Sample: three arcs in a row

Draw three arc classes in one video:

- `Arc` uses `arc_center` to fix the centre directly, sweeps out an upper half circle, and dots the centre position.
- `ArcBetweenPoints` uses a pair of positive / negative `angle` values to show "which way it bends".
- `TangentialArc` first draws two intersecting dashed lines, then builds a corner arc at the intersection.

```python
from real_time_manim import Scene, Arc, ArcBetweenPoints, TangentialArc, DashedLine, \
    Dot, Text, BLUE, GREEN, ORANGE, TEAL, YELLOW, GREY_B, UP, DOWN, PI, \
    Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class ArcDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-Arc family", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— Arc: radius / start_angle / angle / arc_center ——
        arc = Arc(radius=1.2, start_angle=0, angle=PI, color=BLUE, stroke_width=8,
                  arc_center=[-4.6, -1.0, 0])   # radius 1.2, sweeping 180° counter-clockwise from straight right
        cdot = Dot([-4.6, -1.0, 0], radius=0.06, color=YELLOW)   # centre dot = arc_center
        l1 = Text("Arc(angle=PI)", font_size=24, color=GREY_B)   # label for the arc
        l1.next_to(arc, DOWN, buff=0.3)   # place it right below the arc
        win.play(Create(arc), FadeIn(cdot), run_time=0.8)   # draw the arc and dot the centre
        win.play(FadeIn(l1), run_time=0.3)   # fade in the label

        # —— ArcBetweenPoints: angle controls the bend direction and size ——
        ab1 = ArcBetweenPoints([-1.7, -0.3, 0], [1.7, -0.3, 0], angle=PI / 2,
                               color=GREEN, stroke_width=8)   # positive angle (counter-clockwise): dips down into a valley
        ab2 = ArcBetweenPoints([-1.7, -2.1, 0], [1.7, -2.1, 0], angle=-PI / 2,
                               color=ORANGE, stroke_width=8)   # negative angle (clockwise): arches up into a hill
        lu = Text("angle=+PI/2", font_size=24, color=GREY_B).next_to(ab1, UP, buff=0.15)
        ld = Text("angle=-PI/2", font_size=24, color=GREY_B).next_to(ab2, DOWN, buff=0.15)
        win.play(Create(ab1), FadeIn(lu), run_time=0.7)   # positive-angle arc + top label
        win.play(Create(ab2), FadeIn(ld), run_time=0.7)   # negative-angle arc + bottom label

        # —— TangentialArc: corner arc for two intersecting lines (corner picks the quadrant) ——
        ln1 = DashedLine([3.1, -1.0, 0], [6.1, -1.0, 0], color=GREY_B)   # horizontal line that takes part in the intersection
        ln2 = DashedLine([4.6, -2.7, 0], [4.6, 0.7, 0], color=GREY_B)   # vertical line that takes part in the intersection
        ta = TangentialArc(ln1, ln2, radius=0.9, corner=(1, 1), color=TEAL)   # corner arc at the intersection
        lt = Text("TangentialArc(corner=(1,1))", font_size=22, color=GREY_B)
        lt.next_to(ln1, DOWN, buff=0.25)   # place it below the horizontal dashed line so it does not overlap the helper lines
        win.play(Create(ln1), Create(ln2), run_time=0.6)   # draw the two helper lines first
        win.play(Create(ta), FadeIn(lt), run_time=0.7)   # then the corner arc + label
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: it draws three kinds of arc one after another on the frame.

- On the left, `Arc` is given the centre `arc_center=[-4.6, -1.0, 0]`, a radius of 1.2 and a sweep of `PI`, drawing an upper half circle and dotting the centre in yellow.
- In the middle, a pair of `ArcBetweenPoints` share their endpoints while `angle` is positive on one and negative on the other: the positive angle walks counter-clockwise from the start, giving a "valley" that is high at both ends and low in the middle; the negative angle walks clockwise, giving a "hill" that is high in the middle and low at the ends.
- On the right, two intersecting grey dashed lines are drawn first, then `TangentialArc` builds a corner arc of radius 0.9 at the intersection.

<video src="assets/RTM output/01-Basic-Shapes-arc.mp4" controls width="560"></video>

> Note:
>
> - `TangentialArc` takes two **`Line` objects** (it computes the intersection internally to fix the arc centre); do not pass direction vectors. Its `radius` has no default, and forgetting it is an immediate `TypeError`.
> - To draw `Arc` somewhere else, `arc_center=` is more intuitive than drawing it and then `shift`-ing.
> - The bend rule for `ArcBetweenPoints`: with the two endpoints at the same height and viewed left to right, a positive `angle` walks counter-clockwise and gives a "valley below", while a negative `angle` walks clockwise and gives a "hill above".

### CurvedArrow (in `01-Basic-Shapes-curved.mp4`), CurvedDoubleArrow (in `01-Basic-Shapes-curved.mp4`)

```python
def __init__(self, start_point: Point3DLike, end_point: Point3DLike,
             **kwargs: Any) -> None:  # CurvedArrow / CurvedDoubleArrow
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `start_point` / `end_point` | `Point3DLike` | required | start / end of the curved arrow |
| `angle` | `float` | `TAU/4` | (inherited from `ArcBetweenPoints`) bend angle: positive = counter-clockwise arch, negative = bend the other way |
| `radius` | `float \| None` | `None` | (inherited) explicit radius; `None` derives it from `angle` |
| `**kwargs` | — | — | everything else forwards to the arc and the tip: `color`, `stroke_width`, …; to change the tip shape see [Arrow tips](02b-Arrow-Tips.md) |

> **Returns**: an arc object with an arrow tip. `CurvedDoubleArrow` has a tip at both ends and is otherwise exactly the same as `CurvedArrow`.

#### Sample: single-headed and double-headed curved arrows

Three curved arrows side by side: the default bend (positive `angle`, dipping down into a valley), a negative `angle` bending the other way (arching up into a hill), and a `CurvedDoubleArrow` with a tip at both ends.

```python
from real_time_manim import Scene, CurvedArrow, CurvedDoubleArrow, Text, \
    BLUE, RED, GREEN, YELLOW, GREY_B, UP, TAU, Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class CurvedArrowDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-CurvedArrow / CurvedDoubleArrow", font_size=32, color=YELLOW)
        title.to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        ca1 = CurvedArrow([-3.2, 1.4, 0], [3.2, 1.4, 0], color=BLUE, stroke_width=6)   # default angle=TAU/4: dips down into a valley
        l1 = Text("CurvedArrow (default angle)", font_size=24, color=GREY_B)
        l1.next_to(ca1, UP, buff=0.1)   # put the label above the arrow
        win.play(Create(ca1), FadeIn(l1), run_time=0.8)   # draw the default-bend curved arrow

        ca2 = CurvedArrow([-3.2, -0.4, 0], [3.2, -0.4, 0], angle=-TAU / 4,
                          color=GREEN, stroke_width=6)   # negative angle: the bend flips (arches up into a hill)
        l2 = Text("CurvedArrow(angle=-TAU/4)", font_size=24, color=GREY_B)
        l2.next_to(ca2, DOWN, buff=0.15)   # put the label below (the curve is high in the middle, low at the ends)
        win.play(Create(ca2), FadeIn(l2), run_time=0.8)   # draw the reverse-bend curved arrow

        cda = CurvedDoubleArrow([-3.2, -2.3, 0], [3.2, -2.3, 0], color=RED, stroke_width=6)   # a tip at both ends
        l3 = Text("CurvedDoubleArrow", font_size=24, color=GREY_B)
        l3.next_to(cda, UP, buff=0.2)   # put the label inside the valley (the concave side, so it stays on screen)
        win.play(Create(cda), FadeIn(l3), run_time=0.8)   # draw the double-headed curved arrow
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: three curved arrows are laid out from top to bottom.

- The first uses the defaults (`angle=TAU/4`, walking counter-clockwise), dipping down into a "valley" between the two endpoints.
- The second passes `angle=-TAU/4`: same endpoints, but the bend flips and it arches up into a "hill".
- The third, `CurvedDoubleArrow`, has the same shape as the first but with an extra arrow tip at each end to mean a "two-way relation"; its label sits in the concave side of the valley.

<video src="assets/RTM output/01-Basic-Shapes-curved.mp4" controls width="560"></video>

> Note: for a straight arrow use `Arrow` (see [Lines and arrows](02-Lines-and-Arrows.md)); `CurvedArrow` is the "with curvature" version, and the bend is decided only by the sign and size of `angle`. To make the bend more obvious, raise `angle` (say `PI`), or pass `radius` directly.

### Circle, Dot

```python
def __init__(self, radius: float | None = None,
             color: ParsableManimColor = RED, **kwargs: Any) -> None:  # Circle

def __init__(self, point: Point3DLike = ORIGIN, radius: float = 0.08,
             stroke_width: float = 0, fill_opacity: float = 1.0,
             color: ParsableManimColor = WHITE, **kwargs: Any) -> None:  # Dot
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `radius` | `float \| None` | `None` (treated as `1.0`) | (`Circle`) radius; any positive number |
| `color` | `ManimColor` | `RED` | (`Circle`) stroke colour — note the default is **red** and there is **no fill** by default |
| `point` | `Point3DLike` | `ORIGIN` | (`Dot`) centre of the dot |
| `radius` | `float` | `0.08` | (`Dot`) radius; `0.12` ~ `0.2` is common for annotations |
| `stroke_width` | `float` | `0` | (`Dot`) stroke width; no stroke by default |
| `fill_opacity` | `float` | `1.0` | (`Dot`) fill opacity; `<1` gives a semi-transparent dot |
| `color` | `ManimColor` | `WHITE` | (`Dot`) fill colour |

> **Returns**: a circle / dot object. Common `Circle` methods: `surround(mobject)` (scale it until it encloses any object), `point_at_angle(angle)` (take a point on the circle), `Circle.from_three_points(p1, p2, p3)` (the circle through three points).

#### Sample: `surround` and point-picking on a circle, the default red circle, and three dots

On the left a small circle `animate.surround()`s a square and a yellow dot is pinned at 45° on the circle; in the middle a bare `Circle()` shows "default radius 1, red stroke"; on the right three `Dot`s demonstrate the default style, a scaled and recoloured one, and a semi-transparent one.

```python
from real_time_manim import Scene, Circle, Dot, Square, Text, GREEN, BLUE, \
    YELLOW, ORANGE, TEAL, GREY_B, UP, DOWN, LEFT, RIGHT, DEGREES, \
    Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class CircleDotDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-Circle / Dot", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— Circle.surround(): scale a circle until it encloses any object ——
        sq = Square(side_length=1.3, color=GREEN, fill_opacity=0.4).shift(LEFT * 4.2)   # the square to be enclosed
        cir = Circle(radius=0.55, color=BLUE, stroke_width=7).shift(LEFT * 4.2 + UP * 1.7)   # the circle starts out not enclosing it
        l1 = Text("Circle.surround()", font_size=24, color=GREY_B)
        l1.next_to(sq, DOWN, buff=0.5)   # put the label below the square
        self.add(sq)   # add the square to the scene statically first
        win.play(FadeIn(cir), run_time=0.5)   # first see the small circle that encloses nothing
        win.play(cir.animate.surround(sq), run_time=0.8)   # the circle moves and scales until it just encloses the square (1.2x margin)
        win.play(FadeIn(l1), run_time=0.3)   # fade in the label
        pdot = Dot(cir.point_at_angle(45 * DEGREES), radius=0.07, color=YELLOW)   # take a point at 45° on the circle
        win.play(FadeIn(pdot), run_time=0.3)   # dot that point on the circle

        # —— Circle defaults: radius=None means 1, color=RED ——
        red_c = Circle().shift(RIGHT * 3.0)   # default: radius 1, red stroke
        l2 = Text("Circle() default: r=1, RED", font_size=24, color=GREY_B)
        l2.next_to(red_c, DOWN, buff=0.35)   # put the label below the red circle
        win.play(Create(red_c), FadeIn(l2), run_time=0.7)   # draw the default red circle

        # —— Dot: point / radius / color / fill_opacity ——
        d1 = Dot(point=[0.6, -2.5, 0])   # default: radius 0.08, filled white
        d2 = Dot(point=[2.2, -2.5, 0], radius=0.2, color=ORANGE)   # a bigger orange dot
        d3 = Dot(point=[3.8, -2.5, 0], radius=0.12, color=TEAL, fill_opacity=0.5)   # a semi-transparent teal dot
        l3 = Text("Dot(radius=...)", font_size=24, color=GREY_B)
        l3.next_to(d2, DOWN, buff=0.4)   # put the label below the middle dot (clear of the red circle's label)
        win.play(FadeIn(d1), FadeIn(d2), FadeIn(d3), run_time=0.5)   # fade in all three dots together
        win.play(FadeIn(l3), run_time=0.3)   # fade in the label
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: the frame is split into three blocks from left to right.

- On the left the square enters first, a small circle that "encloses nothing" appears from above, then `surround()` moves and scales the circle until it just encloses the square (leaving the default 1.2x margin); `point_at_angle(45°)` then dots the circumference in yellow.
- The middle `Circle()` passes no arguments at all, showing the default look of "radius 1, red stroke, no fill".
- On the right, three dots go from left to right: the default white dot, a bigger recoloured orange dot, and a semi-transparent teal dot.

<video src="assets/RTM output/01-Basic-Shapes-circle_dot.mp4" controls width="560"></video>

> Note:
>
> - `Circle` has **no fill** by default, only a stroke; for a filled circle, call `.set_fill(colour, opacity)` yourself.
> - `Circle`'s default colour is **red**, so do not mistake it for "white by default".
> - `Dot`'s default radius is only 0.08, tiny on a 1080p frame; for endpoints and node annotations start from `radius=0.12`.

---

See also: [Basic shapes advanced](01b-Basic-Shapes-Advanced.md) · [Lines and arrows](02-Lines-and-Arrows.md) · [Polygons and stars](03-Polygons-and-Stars.md) · [VMobject styles](07-VMobject-Styles.md)
