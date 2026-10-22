# Lines and arrows (1): line segments, dashed lines, and arrows

"Lines" and "arrows" are two kinds of basic building block: the `Line` family (straight lines, curved lines, dashed lines, tangents, right-angle elbows) and the `Arrow` family (single- / double-headed arrows, vectors). These classes are all defined in `mobject/geometry/line.py` and all take fill and stroke styles (see [VMobject styles](07-VMobject-Styles.md)); arrows can also change their tip shape (see [Arrow tips](02b-Arrow-Tips.md)).

On the render path:

- `Line` / `DashedLine` / `Arrow` use the native path (core classes already render-verified, 2026-10-11);
- `TangentLine` (`line.py:413`, a `Line` subclass) uses native `_send_line` (`paint.py:996`);
- `Vector` / `DoubleArrow` (`line.py:714/819`, `Arrow` subclasses) use native `_send_arrow` (`paint.py:967`; `DoubleArrow` also has a dedicated `tests/test_double_arrow.py`);
- only `Elbow` (`line.py:465`, a direct `VMobject` descendant) falls to the generic fallback.

All four have been rendered and verified with the two samples.

## Parameters

### Line, DashedLine, TangentLine (in `02-Lines-and-Arrows-lines.mp4`), Elbow (in `02-Lines-and-Arrows-lines.mp4`, generic fallback)

```python
def __init__(self, start: Point3DLike | Mobject = [-1, 0, 0],
             end: Point3DLike | Mobject = [1, 0, 0], buff: float = 0,
             path_arc: float = 0, **kwargs: Any) -> None:  # Line

def __init__(self, *args: Any, dash_length: float = 0.05,
             dashed_ratio: float = 0.5, **kwargs: Any) -> None:  # DashedLine

def __init__(self, vmob: VMobject, alpha: float, length: float = 1,
             d_alpha: float = 1e-06, **kwargs: Any) -> None:  # TangentLine

def __init__(self, width: float = 0.2, angle: float = 0,
             **kwargs: Any) -> None:  # Elbow
```

Line segments and dashed lines (`DashedLine`'s positional arguments are the same as `Line`'s):

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `start` / `end` | `Point3DLike \| Mobject` | `[-1,0,0]` / `[1,0,0]` | start / end; **accepts** coordinates, and also a `Mobject` (the line attaches to the object automatically) |
| `buff` | `float` | `0` | inset at both ends |
| `path_arc` | `float` | `0` | angle (radians) that bends the segment into an arc; `0` is a straight line, and the sign controls the bend direction |
| `dash_length` | `float` | `0.05` | (`DashedLine`) length of each solid dash |
| `dashed_ratio` | `float` | `0.5` | (`DashedLine`) the **solid fraction of a "dash + gap" period**: `0.5` makes dashes and gaps equal, and the closer to 1 the more continuous it looks |

> **Line / DashedLine returns**: a line object (`Line` inherits `VMobject`). Since 0.21 `DashedLine` has only the two dash parameters above — there is no `num_dashes=` (do not copy old references, it either gets swallowed by `**kwargs` or raises).

Tangents and right angles:

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `vmob` | `VMobject` | required | (`TangentLine`) the curve whose tangent is taken (any `VMobject` works) |
| `alpha` | `float` | required | (`TangentLine`) position ratio along the curve; `0` is the start, `1` the end, the midpoint is `0.5` |
| `length` | `float` | `1` | (`TangentLine`) total length of the tangent segment |
| `d_alpha` | `float` | `1e-06` | (`TangentLine`) numerical-differentiation step; **do not change** |
| `width` | `float` | `0.2` | (`Elbow`) length of the two short segments |
| `angle` | `float` | `0` | (`Elbow`) overall rotation (radians); `PI/2` rotates it 90° to change the orientation |

> **TangentLine / Elbow returns**: a straight-segment object.

#### Sample: straight, curved, dashed, plus a tangent and a right angle

The left column has four lines from top to bottom: the default straight line, an arc bent out of the same endpoints with `path_arc=0.6`, and a teal dashed line with `dash_length=0.15`; on the upper right an arc carries a red tangent at its midpoint, and on the lower right two `Elbow`s are drawn with `angle=0` and `angle=PI/2`.

```python
from real_time_manim import Scene, Line, DashedLine, TangentLine, Elbow, Arc, Text, \
    BLUE, YELLOW, ORANGE, TEAL, GREEN, RED, GREY_B, UP, DOWN, PI, \
    Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class LinesDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02-Line / DashedLine / TangentLine / Elbow", font_size=28, color=YELLOW)
        title.to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— Line: start and end + path_arc bends the "straight line" ——
        ln = Line([-5.6, 2.2, 0], [0.4, 2.2, 0], stroke_width=6, color=YELLOW)   # default path_arc=0: straight
        c1 = Text("Line(start, end)", font_size=22, color=GREY_B).next_to(ln, DOWN, buff=0.15)
        win.play(Create(ln), FadeIn(c1), run_time=0.6)   # draw the straight line + caption

        ln2 = Line([-5.6, 0.9, 0], [0.4, 0.9, 0], path_arc=0.6, stroke_width=6, color=ORANGE)   # same endpoints, path_arc≠0 bends it into an arc
        c2 = Text("Line(path_arc=0.6)", font_size=22, color=GREY_B).next_to(ln2, DOWN, buff=0.15)
        win.play(Create(ln2), FadeIn(c2), run_time=0.6)   # draw the arc + caption

        # —— DashedLine: dash_length / dashed_ratio ——
        dl = DashedLine([-5.6, -0.7, 0], [0.4, -0.7, 0], dash_length=0.15,
                       dashed_ratio=0.55, color=TEAL, stroke_width=5)   # dash 0.15, solid fraction 0.55
        c3 = Text("DashedLine(dash_length=0.15)", font_size=22, color=GREY_B).next_to(dl, DOWN, buff=0.15)
        win.play(Create(dl), FadeIn(c3), run_time=0.6)   # draw the dashed line + caption

        # —— TangentLine: the tangent to the curve at alpha ——
        arc = Arc(radius=1.0, start_angle=-PI / 3, angle=2 * PI / 3, color=BLUE, stroke_width=6)
        arc.shift([4.6, 1.9, 0])   # put an arc in the top right
        tl = TangentLine(arc, 0.5, length=2.4, color=RED, stroke_width=6)   # the tangent at the arc's midpoint (alpha=0.5)
        c4 = Text("TangentLine(arc, 0.5)", font_size=22, color=GREY_B).move_to([4.6, 0.3, 0])   # below the tangent
        win.play(Create(arc), run_time=0.5)   # draw the arc first
        win.play(Create(tl), FadeIn(c4), run_time=0.6)   # then the tangent + caption

        # —— Elbow: a right-angle corner (angle turns the direction) ——
        e1 = Elbow(width=0.5, angle=0, color=GREEN, stroke_width=6).shift([3.8, -1.9, 0])   # original orientation
        e2 = Elbow(width=0.5, angle=PI / 2, color=GREEN, stroke_width=6).shift([5.4, -1.9, 0])   # rotated 90°
        c5 = Text("Elbow(angle=0 / PI/2)", font_size=22, color=GREY_B).move_to([4.6, -2.9, 0])
        win.play(FadeIn(e1), FadeIn(e2), run_time=0.5)   # both corners appear together
        win.play(FadeIn(c5), run_time=0.3)   # fade in the caption
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: the frame is split into three blocks.

- The three lines in the left column share one pair of endpoints: the first uses the defaults (a straight yellow line), the second only adds `path_arc=0.6` and bends into an orange arc, and the third, a `DashedLine`, pulls a teal dashed line with `dash_length=0.15`.
- On the upper right a blue arc is drawn first, then a red tangent 2.4 long is generated at the midpoint of the arc (`alpha=0.5`).
- On the lower right, two right-angle elbows — one at the original orientation and one rotated 90° — contrast the effect of `angle` directly.

<video src="assets/RTM output/02-Lines-and-Arrows-lines.mp4" controls width="560"></video>

> Note:
>
> - When `start` / `end` are given a `Mobject`, the line attaches to the object (very common for "connector lines").
> - The bend direction of `path_arc` is decided by the sign — positive and negative bend to opposite sides.
> - `TangentLine`'s `alpha` is a **curve-parameter ratio**, not an x coordinate — when the curve wanders far, the "midpoint" is not necessarily the geometric midpoint.
> - `Elbow` is only 0.2 long by default; it is a small corner mark, not a coordinate axis.

### Arrow, Vector (in `02-Lines-and-Arrows-arrows.mp4`), DoubleArrow (in `02-Lines-and-Arrows-arrows.mp4`, dedicated `tests/test_double_arrow.py`)

```python
def __init__(self, *args: Any, stroke_width: float = 6, buff: float = 0.25,
             max_tip_length_to_length_ratio: float = 0.25,
             max_stroke_width_to_length_ratio: float = 5,
             **kwargs: Any) -> None:  # Arrow

def __init__(self, direction: array-like = RIGHT, buff: float = 0,
             **kwargs: Any) -> None:  # Vector

def __init__(self, *args: Any, **kwargs: Any) -> None:  # DoubleArrow
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*args` | — | `[-1,0,0]`, `[1,0,0]` | (`Arrow` / `DoubleArrow`) the first two positional arguments are `start` and `end`, i.e. `Arrow(LEFT*2, RIGHT*2)`; a `Mobject` also works |
| `stroke_width` | `float` | `6` | line width (including the shaft) |
| `buff` | `float` | `0.25` | inset at both ends — note `Arrow`'s default is **0.25** (`Line`'s is 0), so the tip stops fully inside the endpoint |
| `max_tip_length_to_length_ratio` | `float` | `0.25` | upper bound on tip length / arrow length; the shorter the arrow the more the tip shrinks automatically, **do not tune it by hand** |
| `max_stroke_width_to_length_ratio` | `float` | `5` | upper bound on stroke width / arrow length, so a short arrow does not turn into a "fat lump"; **do not tune it by hand** |
| `direction` | `array-like` | `RIGHT` | (`Vector`) direction / end coordinates pointing from the origin |
| `buff` | `float` | `0` | (`Vector`) start inset; by default it starts right at the origin |

> **Returns**: a line with an arrow tip. Common methods: `Arrow.scale(factor, scale_tips=True)` (whether the tip scales along with it), `Arrow.get_normal_vector()`; `Vector.coordinate_label(integer_labels=True, n_dim=2, color=None)` returns a label of the end coordinates (a `Matrix`). `DoubleArrow` takes exactly the same parameters as `Arrow`, it just has a tip at both ends.

#### Sample: a regular arrow, a short thick arrow, a double-headed one, and a vector coordinate label

Four groups of arrows:

- a blue `Arrow` of regular length;
- a red arrow that is short and thick — the `max_*_ratio` caps shrink the tip and clamp the stroke width automatically, so head and body stay in proportion;
- a purple `DoubleArrow` showing a dimension line;
- two `Vector`s below, the right one labelling `(2, 1)` next to its endpoint with `coordinate_label()`.

```python
from real_time_manim import Scene, Arrow, Vector, DoubleArrow, Text, \
    BLUE, RED, GREEN, TEAL, PURPLE, YELLOW, WHITE, GREY_B, UP, DOWN, UR, \
    Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class ArrowsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02-Arrow / Vector / DoubleArrow", font_size=30, color=YELLOW)
        title.to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— Arrow: the ratios are controlled automatically, a short line never looks top-heavy ——
        a1 = Arrow([-5.6, 2.0, 0], [0.6, 2.0, 0], color=BLUE, buff=0)   # regular length
        c1 = Text("Arrow(start, end, buff=0)", font_size=22, color=GREY_B).next_to(a1, DOWN, buff=0.15)
        win.play(Create(a1), FadeIn(c1), run_time=0.7)   # draw the regular arrow + caption

        a2 = Arrow([-5.6, 0.6, 0], [-2.4, 0.6, 0], color=RED, buff=0, stroke_width=14)   # short and thick: the tip ratio is capped automatically
        c2 = Text("short arrow + stroke_width=14", font_size=22, color=GREY_B).next_to(a2, DOWN, buff=0.15)
        win.play(Create(a2), FadeIn(c2), run_time=0.7)   # draw the short thick arrow + caption

        # —— DoubleArrow: a tip at both ends ——
        da = DoubleArrow([3.4, 2.0, 0], [6.6, 2.0, 0], color=PURPLE, buff=0)   # double-headed (a dimension line, moved right to make room for the coordinate label)
        c3 = Text("DoubleArrow", font_size=22, color=GREY_B).next_to(da, DOWN, buff=0.15)
        win.play(Create(da), FadeIn(c3), run_time=0.7)   # draw the double-headed arrow + caption

        # —— Vector: starts at the origin + coordinate_label labels the coordinates ——
        v = Vector([2.4, 1.4, 0], color=GREEN).shift([-4.8, -1.7, 0])   # direction vector (from the "origin" towards direction)
        c4 = Text("Vector([2.4, 1.4])", font_size=22, color=GREY_B).move_to([-4.4, -3.0, 0])
        win.play(Create(v), FadeIn(c4), run_time=0.7)   # draw the vector + caption

        v2 = Vector([2, 1, 0], color=TEAL)   # put it at the origin: coordinate_label rounds the endpoint's world coordinates
        lab = v2.coordinate_label(color=WHITE).next_to(v2.get_end(), UR, buff=0.2)   # label (2, 1) next to the endpoint
        c5 = Text("coordinate_label()", font_size=22, color=GREY_B).move_to([1.4, -0.9, 0])
        win.play(Create(v2), run_time=0.5)   # draw the vector
        win.play(FadeIn(lab), FadeIn(c5), run_time=0.5)   # the coordinate label + caption
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: four groups of arrows appear one after another.

- The first row is a blue regular arrow (`buff=0` makes the tip line up with the endpoint).
- The second row's red arrow is only 3.2 long yet is given `stroke_width=14` — the `max_*_ratio` caps shrink the tip and clamp the stroke width automatically, so it still looks balanced.
- The purple `DoubleArrow` at the upper right has a tip at both ends and is the standard way to annotate a "distance between two points".
- Of the two `Vector`s below, the second places a `(2, 1)` coordinate label next to its arrow tip with `coordinate_label()`.

<video src="assets/RTM output/02-Lines-and-Arrows-arrows.mp4" controls width="560"></video>

> Note:
>
> - `Arrow`'s `buff` defaults to **0.25** (`Line`'s is 0); to have the tip press exactly to the endpoint, write `buff=0` explicitly.
> - The two `max_*_ratio` parameters are "fool-proofing" — they are the only reason a short thick arrow is not deformed, so **do not** reduce them.
> - `Vector` is born at the origin with `buff=0`; to move it, use `.shift(...)`; `coordinate_label()` returns an ordinary `Matrix`, so you place it yourself with `.next_to(...)` (which is what the sample does).
> - **Gotcha**: `coordinate_label()` labels the **endpoint's current world coordinates** and rounds them because `integer_labels=True` — the sample deliberately puts the vector at the origin so the endpoint is exactly `(2,1)`; if you `.shift(...)` before labelling, what gets labelled is the shifted coordinate (in testing this page once labelled `(5, -2)` after `shift([2.8,-2.6])`).

---

See also: [Arrow tips](02b-Arrow-Tips.md) · [Angles and callout boxes](04-Angles-and-Callout-Boxes.md) · [VMobject styles](07-VMobject-Styles.md)
