# Basic shapes (2): annotation dots, annular sectors, and free curves

Picking up from the arc and circle family in [Basic shapes (1)](01-Basic-Shapes.md): this page covers three groups of objects — emphasis / label dots and ellipses, pie-chart-style annular sectors and rings, and hand-drawn cubic Béziers plus polygons whose "edges are arcs between the vertices".

The ones going through the **native** path:

- `Ellipse` (a `Circle` subclass, core class already render-verified, 2026-10-11);
- `AnnotationDot` / `LabeledDot` (`Dot` subclasses, `arc.py:826/846` → native `_send_dot`);
- the annular sector family `AnnularSector` / `Sector` / `Annulus` (`Arc` / `Circle` subclasses → native `_send_arc`, with dedicated `tests/test_arc_fill.py` and `tests/test_passing_flash_and_fill.py`).

`CubicBezier` / `ArcPolygon` / `ArcPolygonFromArcs` are direct `VMobject` descendants and go through the generic fallback, but they already render correctly with this page's samples. Both samples on this page have been rendered and verified in RTM.

## Parameters

### AnnotationDot (in `01b-Basic-Shapes-Advanced-dots_ellipse.mp4`), LabeledDot (in `01b-Basic-Shapes-Advanced-dots_ellipse.mp4`), Ellipse

```python
def __init__(self, radius: float = 0.104, stroke_width: float = 5,
             stroke_color: ParsableManimColor = WHITE,
             fill_color: ParsableManimColor = BLUE,
             **kwargs: Any) -> None:  # AnnotationDot

def __init__(self, label: str | SingleStringMathTex | Text | Tex,
             radius: float | None = None, buff: float = 0.1,
             **kwargs: Any) -> None:  # LabeledDot

def __init__(self, width: float = 2, height: float = 1,
             **kwargs: Any) -> None:  # Ellipse
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `radius` | `float` | `0.104` | (`AnnotationDot`) radius — 1.3x the `Dot` default; **accepts** any positive number |
| `stroke_width` | `float` | `5` | (`AnnotationDot`) stroke width; `0` removes the white ring |
| `stroke_color` | `ManimColor` | `WHITE` | (`AnnotationDot`) stroke colour |
| `fill_color` | `ManimColor` | `BLUE` | (`AnnotationDot`) fill colour; **accepts** any colour string / `ManimColor` |
| `label` | `str \| MathTex \| Text \| Tex` | required | (`LabeledDot`) the label at the dot's centre; a string is rendered as `MathTex` automatically (math italics), so pass a `Text` object directly if you want a normal font |
| `radius` | `float \| None` | `None` | (`LabeledDot`) radius; when `None` it adapts to the label size |
| `buff` | `float` | `0.1` | (`LabeledDot`) gap between the label and the dot's edge; only applies when `radius=None` and it adapts automatically |
| `width` | `float` | `2` | (`Ellipse`) length of the horizontal axis |
| `height` | `float` | `1` | (`Ellipse`) length of the vertical axis |

> **Returns**: a dot / ellipse object (a `Dot` or `Circle` subclass). `AnnotationDot` differs from `Dot` by exactly "white stroke + blue fill + one size up"; `LabeledDot` puts `label` in the centre of the dot and scales it automatically.

#### Sample: emphasis dots, label dots, and two ellipses

From the left it first contrasts `AnnotationDot` with the default `Dot` (which one is "the emphasis dot" is obvious at a glance); in the middle it puts one `LabeledDot` whose radius adapts to its label and one with a manual `radius`; on the right it draws two ellipses, one flat and one tall, using `width` / `height`.

```python
from real_time_manim import Scene, AnnotationDot, LabeledDot, Ellipse, Dot, Text, \
    PURPLE, TEAL, YELLOW, GREY_B, UP, DOWN, Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class DotsEllipseDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01b-AnnotationDot / LabeledDot / Ellipse", font_size=30, color=YELLOW)
        title.to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— AnnotationDot: an emphasis dot with a white stroke (against the default Dot) ——
        ad = AnnotationDot().move_to([-4.2, 0.6, 0])   # default: blue fill, white stroke 5, radius 0.104 (no positional argument, move it after building)
        d = Dot([-2.7, 0.6, 0])   # for comparison: the default small white dot (radius 0.08, no stroke)
        l1 = Text("AnnotationDot vs Dot", font_size=22, color=GREY_B)
        l1.move_to([-3.45, -0.15, 0])   # centre the label below the two dots
        win.play(FadeIn(ad), FadeIn(d), run_time=0.5)   # fade in both dots together
        win.play(FadeIn(l1), run_time=0.3)   # fade in the label

        # —— LabeledDot: a dot with a label at its centre (a string renders as MathTex automatically) ——
        ld1 = LabeledDot("x").shift([0, 0.7, 0])   # radius adapts to the label
        ld2 = LabeledDot("42", radius=0.55).shift(DOWN * 1.15)   # radius given by hand
        l2 = Text("LabeledDot(label, radius)", font_size=22, color=GREY_B)
        l2.move_to([0, -2.35, 0])   # put the label below the two label dots
        win.play(FadeIn(ld1), run_time=0.5)   # a label dot with an adaptive radius
        win.play(FadeIn(ld2), run_time=0.5)   # a label dot with a manual radius
        win.play(FadeIn(l2), run_time=0.3)   # fade in the label

        # —— Ellipse: width / height, the two axis lengths ——
        e1 = Ellipse(width=4.2, height=1.6, color=PURPLE).shift([4.3, 0.9, 0])   # flat ellipse
        e2 = Ellipse(width=1.6, height=3.0, color=TEAL).shift([4.3, -1.4, 0])   # tall ellipse
        l3 = Text("Ellipse(width=, height=)", font_size=22, color=GREY_B)
        l3.move_to([4.3, -3.4, 0])   # put the label below the two ellipses
        win.play(Create(e1), run_time=0.6)   # draw the flat ellipse
        win.play(Create(e2), run_time=0.6)   # draw the tall ellipse
        win.play(FadeIn(l3), run_time=0.3)   # fade in the label
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: the frame is split into three blocks from left to right.

- On the left a blue and a white dot sit side by side: `AnnotationDot` has a blue fill and a white stroke and is one size up from the default `Dot` beside it, so it is immediately clear which is the "emphasis dot".
- In the middle, `LabeledDot("x")` with a label-adaptive radius appears first, then `LabeledDot("42")` with a manual `radius=0.55`.
- On the right, a "flat" and a "tall" ellipse are drawn one after the other, showing directly which axis `width` / `height` stretch.

<video src="assets/RTM output/01b-Basic-Shapes-Advanced-dots_ellipse.mp4" controls width="560"></video>

> Note:
>
> - A string label on `LabeledDot` goes through `MathTex` (math italics); to use a normal font (say body text) pass a `Text("label")` object directly.
> - The `AnnotationDot` constructor has **no positional argument** — the first positional argument is `radius`. Writing coordinates as `AnnotationDot([-4.2, 0.6, 0])` treats them as the radius and draws a huge strange circle at the origin (this page's sample hit that in testing); move it with `.move_to(...)` / `.shift(...)` instead.
> - `AnnotationDot`'s default blue fill can clash with other blue-ish shapes, so remember to change `fill_color=` when the figure already has a dominant colour.

### AnnularSector / Sector / Annulus (native `_send_arc`, in `01b-Basic-Shapes-Advanced-sectors.mp4`), CubicBezier / ArcPolygon / ArcPolygonFromArcs (generic fallback, in the same video)

```python
def __init__(self, inner_radius: float = 1, outer_radius: float = 2,
             angle: float = TAU / 4, start_angle: float = 0,
             fill_opacity: float = 1, stroke_width: float = 0,
             color: ParsableManimColor = WHITE,
             **kwargs: Any) -> None:  # AnnularSector

def __init__(self, radius: float = 1, **kwargs: Any) -> None:  # Sector

def __init__(self, start_anchor: Point3DLike, start_handle: Point3DLike,
             end_handle: Point3DLike, end_anchor: Point3DLike,
             **kwargs: Any) -> None:  # CubicBezier

def __init__(self, *vertices: Point3DLike, angle: float = TAU / 4,
             radius: float | None = None, arc_config: list[dict] | None = None,
             **kwargs: Any) -> None:  # ArcPolygon

def __init__(self, *arcs: Arc | ArcBetweenPoints, **kwargs: Any) -> None:  # ArcPolygonFromArcs
```

The annular sector family (`Sector` and `Annulus` both share the following parameters with `AnnularSector`):

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `inner_radius` | `float` | `1` | inner radius; `Sector` has no such parameter (it is the special case `inner_radius=0` and only takes `radius`) |
| `outer_radius` | `float` | `2` | outer radius (the same for `Annulus`); **accepts** any positive number larger than the inner radius |
| `radius` | `float` | `1` | (`Sector`) sector radius |
| `angle` | `float` | `TAU/4` (90°) | sweep angle (radians); a negative value reverses it |
| `start_angle` | `float` | `0` | start angle (radians) |
| `fill_opacity` | `float` | `1` | fill opacity; flat solid colour by default |
| `stroke_width` | `float` | `0` | stroke width; **no stroke** by default; set it yourself if you want an outline |
| `color` | `ManimColor` | `WHITE` | colour (white by default; remember to change it in chart scenes) |
| `mark_paths_closed` | `bool` | `False` | (`Annulus`) path-closed flag, **do not change** |

Hand-drawn curves and arc polygons:

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `start_anchor` / `end_anchor` | `Point3DLike` | required | (`CubicBezier`) start / end of the curve (the anchors lie on the curve) |
| `start_handle` / `end_handle` | `Point3DLike` | required | (`CubicBezier`) control handles at the start / end (these points are not on the curve, they only "pull" it) |
| `*vertices` | `Point3DLike...` | required | (`ArcPolygon`) vertex coordinates — **one group per parameter? No — every positional argument is one vertex** |
| `angle` | `float` | `TAU/4` | (`ArcPolygon`) the bend angle shared by every edge (radians) |
| `radius` | `float \| None` | `None` | (`ArcPolygon`) bend at a fixed radius; ignored once `angle` is given |
| `arc_config` | `list[dict] \| None` | `None` | (`ArcPolygon`) per-edge custom bend (one `{"radius":..., "arc_center":...}` dict per edge); pick one of this and `angle` |
| `*arcs` | `Arc \| ArcBetweenPoints...` | required | (`ArcPolygonFromArcs`) arcs that are already drawn, required to be **joined end to end** (the previous `end` == the next `start`) |

> **Returns**: a filled block / curve object. `Sector` ≡ `AnnularSector(inner_radius=0)`; `CubicBezier` inherits `VMobject`, and its endpoints can be read with `get_start()` / `get_end()`.

#### Sample: the three-piece annular sector family, a Bézier, and an arc-edged polygon

The top row has three filled shapes from left to right: an `AnnularSector` with an adjustable inner and outer radius, a pie-chart `Sector`, and a doughnut `Annulus`; the bottom row has three "lines": an S-shaped `CubicBezier` pulled from four points, an `ArcPolygon` whose three vertices are joined by edges bent `PI/6`, and an `ArcPolygonFromArcs` made from two arcs joined end to end.

```python
from real_time_manim import Scene, AnnularSector, Sector, Annulus, CubicBezier, \
    ArcPolygon, ArcPolygonFromArcs, ArcBetweenPoints, Text, \
    ORANGE, RED, GREEN, BLUE, TEAL, PURPLE, YELLOW, GREY_B, \
    UP, DOWN, LEFT, RIGHT, PI, TAU, Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class SectorsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01b-AnnularSector / Sector / Annulus / Bezier / ArcPolygon",
                     font_size=24, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— First row: three filled "annular sector / ring" blocks ——
        asec = AnnularSector(inner_radius=0.5, outer_radius=1.2, angle=2.0,
                             start_angle=PI / 2, color=ORANGE).shift(LEFT * 4.4 + UP * 0.9)   # annular sector
        cap1 = Text("AnnularSector", font_size=20, color=GREY_B).next_to(asec, DOWN, buff=0.3)
        win.play(Create(asec), FadeIn(cap1), run_time=0.6)   # draw the annular sector

        sec = Sector(radius=0.95, angle=TAU / 3, color=RED).shift(UP * 0.9)   # solid sector (one slice of a pie chart)
        cap2 = Text("Sector", font_size=20, color=GREY_B).next_to(sec, DOWN, buff=0.3)
        win.play(Create(sec), FadeIn(cap2), run_time=0.6)   # draw the solid sector

        ann = Annulus(inner_radius=0.4, outer_radius=1.0, color=GREEN).shift(RIGHT * 4.4 + UP * 0.9)   # ring (doughnut)
        cap3 = Text("Annulus", font_size=20, color=GREY_B).next_to(ann, DOWN, buff=0.3)
        win.play(Create(ann), FadeIn(cap3), run_time=0.6)   # draw the ring

        # —— Second row: a hand-drawn Bézier, and a polygon with arcs between its vertices ——
        cb = CubicBezier([-6.2, -2.6, 0], [-4.9, -0.9, 0], [-3.9, -3.5, 0], [-2.7, -1.8, 0],
                         color=PURPLE, stroke_width=6)   # two anchors + two control handles
        cap4 = Text("CubicBezier(4 pts)", font_size=20, color=GREY_B).move_to([-4.45, -3.7, 0])
        win.play(Create(cb), FadeIn(cap4), run_time=0.6)   # draw the S-shaped Bézier curve

        ap = ArcPolygon([-1.7, -2.9, 0], [0, -1.5, 0], [1.7, -2.9, 0],
                        angle=PI / 6, color=BLUE, stroke_width=6)   # three vertices, edges joined by arcs
        cap5 = Text("ArcPolygon(angle=PI/6)", font_size=20, color=GREY_B).move_to([0, -3.7, 0])
        win.play(Create(ap), FadeIn(cap5), run_time=0.6)   # draw the arc-edged triangle

        a1 = ArcBetweenPoints([2.7, -2.9, 0], [4.4, -1.6, 0], angle=-PI / 3, color=TEAL)   # the first arc, arching up
        a2 = ArcBetweenPoints([4.4, -1.6, 0], [6.1, -2.9, 0], angle=PI / 3, color=TEAL)   # the second arc, dipping down
        apa = ArcPolygonFromArcs(a1, a2)   # join the two arcs end to end into one object
        cap6 = Text("ArcPolygonFromArcs", font_size=20, color=GREY_B).move_to([4.4, -3.7, 0])
        win.play(Create(a1), run_time=0.4)   # draw the first arc
        win.play(Create(a2), run_time=0.4)   # then the second
        win.play(FadeIn(cap6), run_time=0.3)   # fade in the label
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: the top row draws three filled shapes one after another, each with a small caption.

- The orange annular sector: `inner_radius=0.5` hollows out the centre.
- The red pie-chart slice: a `Sector`, solid all the way to the centre.
- The green ring: a doughnut with an inner radius of 0.4 and an outer radius of 1.0.

The bottom row draws three "lines" one after another: first a purple S-shaped cubic Bézier pulled from four points, then an arc-edged triangle "with three vertices whose edges bend by `angle=PI/6`", and finally two `ArcBetweenPoints` (one arching up, one dipping down) joined by `ArcPolygonFromArcs` into one continuous object.

<video src="assets/RTM output/01b-Basic-Shapes-Advanced-sectors.mp4" controls width="560"></video>

> Note:
>
> - `Sector` is the sector "cut all the way to the centre"; to hollow out the centre of a ring you must use `AnnularSector`; the annular sector family defaults to `fill_opacity=1, stroke_width=0` (flat colour, no lines), so add `stroke_width=2` yourself if you want a wireframe look.
> - `ArcPolygonFromArcs` requires neighbouring arcs to be **strictly joined end to end** (the first arc's `end` at the same point as the second's `start`); being slightly off leaves a gap.
> - The order of `CubicBezier`'s four positional arguments is "start anchor → start handle → end handle → end anchor"; do not swap the anchors and handles — swapped, the curve flies outside the expected range.
> - The concavity of each `ArcPolygon` edge is decided by **the order the vertices are written in together with the sign of `angle`**: this example writes the points "top → left → right" and gets inward-concave arc edges (like a three-pointed star); changing the vertex order or the sign of `angle` flips the concavity.

---

See also: [Basic shapes](01-Basic-Shapes.md) · [Lines and arrows](02-Lines-and-Arrows.md) · [Polygons and stars](03-Polygons-and-Stars.md) · [Rectangles and special polygons](03b-Rectangles-and-Special-Polygons.md)
