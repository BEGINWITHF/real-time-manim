# geometry

> scope: 2D geometry primitives, annotation boxes, boolean ops, containers and VMobject styling in RTM (`real_time_manim`). Data model is bundled ManimCE 0.21.0; RTM only rasterizes it.
> src: `real_time_manim/manim/mobject/geometry/{arc,line,polygram,boolean_ops,tips,labeled}.py`, `.../mobject/geometry/shape_matchers.py`, `.../mobject/types/vectorized_mobject.py`; human wiki `../zh_CN/04-图形与文本/`.
> Render channels (RTM): `_send_arc` / `_send_dot` / `_send_line` / `_send_arrow` / `_send_polygon` are native; everything else falls back to generic bezier tessellation.

## Arc family

### `Arc`
```python
def __init__(self, radius: float | None = 1.0, start_angle: float = 0,
             angle: float = TAU / 4, num_components: int = 9,
             arc_center: Point3DLike = ORIGIN, **kwargs: Any) -> None
```
- `ret`: arc mobject (`Arc` → `TipableVMobject` → `VMobject`). Read-only: `get_start()`, `get_end()`, `get_center()`, `get_arc_angle()`.
- `args`:
  - `radius: float | None = 1.0` — any positive number.
  - `start_angle: float = 0` — radians; 0 = +x axis, CCW positive.
  - `angle: float = TAU/4` — sweep in radians; negative = clockwise.
  - `num_components: int = 9` — tessellation segments; **do not change** (default sufficient).
  - `arc_center: Point3DLike = ORIGIN` — arc center.
- `notes`:
  - Prefer `arc_center=` over post-hoc `shift`.
  - Inherits `TipableVMobject` → supports `add_tip()` and fill/stroke styling.
- `see`: ../zh_CN/04-图形与文本/01-基本形状.md
- `eg`:
```python
arc = Arc(radius=1.2, start_angle=0, angle=PI, color=BLUE,
          stroke_width=8, arc_center=[-4.6, -1.0, 0])
```

### `ArcBetweenPoints`
```python
def __init__(self, start: Point3DLike, end: Point3DLike,
             angle: float = TAU / 4, radius: float | None = None,
             **kwargs: Any) -> None
```
- `ret`: arc mobject.
- `args`:
  - `start` / `end: Point3DLike` — required endpoints.
  - `angle: float = TAU/4` — bend direction+magnitude. Same-height endpoints L→R: positive = CCW → downward valley; negative = CW → upward arch.
  - `radius: float | None = None` — explicit radius; `None` derives it from `angle`.
- `notes`: curve direction is fully determined by sign/magnitude of `angle`; larger `angle` (e.g. `PI`) = stronger bend.
- `see`: ../zh_CN/04-图形与文本/01-基本形状.md

### `TangentialArc`
```python
def __init__(self, line1: Line, line2: Line, radius: float,
             corner: Any = (1, 1), **kwargs: Any) -> None
```
- `ret`: corner arc at the intersection of two lines.
- `args`:
  - `line1` / `line2: Line` — required **Line objects** (intersection computed internally); NOT direction vectors.
  - `radius: float` — required, **no default**.
  - `corner: tuple[int,int] = (1, 1)` — one of `(±1, ±1)`; picks which quadrant corner of the intersection.
- `errs`:
  - `TypeError` — raised when `radius` omitted (no default).
- `see`: ../zh_CN/04-图形与文本/01-基本形状.md
- `eg`:
```python
ta = TangentialArc(ln1, ln2, radius=0.9, corner=(1, 1), color=TEAL)
```

### `CurvedArrow`
```python
def __init__(self, start_point: Point3DLike, end_point: Point3DLike,
             **kwargs: Any) -> None
```
- `ret`: arc with an arrow tip at the end.
- `args`:
  - `start_point` / `end_point: Point3DLike` — required.
  - `angle: float = TAU/4` — inherited from `ArcBetweenPoints`; bend angle.
  - `radius: float | None = None` — inherited; explicit radius.
  - `**kwargs` — passed through to arc + tip (`color`, `stroke_width`, …); tip shape via `tip_shape` (see arrow tips).
- `notes`: tips are custom curves → generic bezier fallback. For straight arrows use `Arrow`.
- `see`: ../zh_CN/04-图形与文本/01-基本形状.md · ../zh_CN/04-图形与文本/02b-箭头尖端.md

### `CurvedDoubleArrow`
```python
def __init__(self, start_point: Point3DLike, end_point: Point3DLike,
             **kwargs: Any) -> None
```
- `ret`: arc with tips at **both** ends.
- `args`: identical to `CurvedArrow`.
- `notes`: everything else identical to `CurvedArrow`.
- `see`: ../zh_CN/04-图形与文本/01-基本形状.md

## Circle / Dot family

### `Circle`
```python
def __init__(self, radius: float | None = None,
             color: ParsableManimColor = RED, **kwargs: Any) -> None
```
- `ret`: circle (`Circle` subclass of `Arc`). Methods: `surround(mobject)` (scale to enclose; ~1.2× margin), `point_at_angle(angle)`, `Circle.from_three_points(p1, p2, p3)`.
- `args`:
  - `radius: float | None = None` — `None` behaves as `1.0`; any positive number.
  - `color: ParsableManimColor = RED` — **default is RED**, not white.
- `notes`:
  - **No fill by default** — stroke only; for a solid circle call `.set_fill(color, opacity)`.
- `see`: ../zh_CN/04-图形与文本/01-基本形状.md

### `Dot`
```python
def __init__(self, point: Point3DLike = ORIGIN, radius: float = 0.08,
             stroke_width: float = 0, fill_opacity: float = 1.0,
             color: ParsableManimColor = WHITE, **kwargs: Any) -> None
```
- `ret`: filled dot.
- `args`:
  - `point: Point3DLike = ORIGIN` — center.
  - `radius: float = 0.08` — small at 1080p; annotation use `0.12`–`0.2`.
  - `stroke_width: float = 0` — no stroke by default.
  - `fill_opacity: float = 1.0` — `<1` = translucent.
  - `color: ParsableManimColor = WHITE` — fill color.
- `see`: ../zh_CN/04-图形与文本/01-基本形状.md

### `AnnotationDot`
```python
def __init__(self, radius: float = 0.104, stroke_width: float = 5,
             stroke_color: ParsableManimColor = WHITE,
             fill_color: ParsableManimColor = BLUE,
             **kwargs: Any) -> None
```
- `ret`: emphasized dot (`Dot` subclass).
- `args`:
  - `radius: float = 0.104` — any positive number (≈1.3× `Dot` default).
  - `stroke_width: float = 5` — `0` removes the white ring.
  - `stroke_color: ParsableManimColor = WHITE`.
  - `fill_color: ParsableManimColor = BLUE`.
- `notes`:
  - **No positional location arg** — the first positional param is `radius`. `AnnotationDot([-4.2, 0.6, 0])` is interpreted as a radius → huge circle at origin. Reposition with `.move_to(...)` / `.shift(...)`.
  - Default blue fill can clash with blue-dominant scenes; set `fill_color=`.
- `see`: ../zh_CN/04-图形与文本/01b-基本形状进阶.md

### `LabeledDot`
```python
def __init__(self, label: str | SingleStringMathTex | Text | Tex,
             radius: float | None = None, buff: float = 0.1,
             **kwargs: Any) -> None
```
- `ret`: dot with a centered label.
- `args`:
  - `label: str | MathTex | Text | Tex` — required. `str` renders via `MathTex` (math italic); pass a `Text` object for normal font.
  - `radius: float | None = None` — `None` = auto-size to label.
  - `buff: float = 0.1` — label↔dot-edge gap; only used when `radius=None`.
- `see`: ../zh_CN/04-图形与文本/01b-基本形状进阶.md

### `Ellipse`
```python
def __init__(self, width: float = 2, height: float = 1,
             **kwargs: Any) -> None
```
- `ret`: ellipse (`Circle` subclass; native `_send_arc`).
- `args`:
  - `width: float = 2` — horizontal axis length.
  - `height: float = 1` — vertical axis length.
- `see`: ../zh_CN/04-图形与文本/01b-基本形状进阶.md

### `AnnularSector`
```python
def __init__(self, inner_radius: float = 1, outer_radius: float = 2,
             angle: float = TAU / 4, start_angle: float = 0,
             fill_opacity: float = 1, stroke_width: float = 0,
             color: ParsableManimColor = WHITE,
             **kwargs: Any) -> None
```
- `ret`: filled ring-sector (`Arc` subclass; native `_send_arc`).
- `args`:
  - `inner_radius: float = 1` — inner radius.
  - `outer_radius: float = 2` — outer radius; any positive value > inner.
  - `angle: float = TAU/4` — sweep radians; negative reverses.
  - `start_angle: float = 0` — start radians.
  - `fill_opacity: float = 1` — solid by default.
  - `stroke_width: float = 0` — **no stroke by default**.
  - `color: ParsableManimColor = WHITE`.
- `notes`: family defaults `fill_opacity=1, stroke_width=0` (flat solid, no outline); add `stroke_width=2` for a gridded look.
- `see`: ../zh_CN/04-图形与文本/01b-基本形状进阶.md

### `Sector`
```python
def __init__(self, radius: float = 1, **kwargs: Any) -> None
```
- `ret`: solid pie slice (`AnnularSector` with `inner_radius=0`).
- `args`:
  - `radius: float = 1` — sector radius.
  - other params shared with `AnnularSector` (`angle`, `start_angle`, `fill_opacity`, `stroke_width`, `color`).
- `see`: ../zh_CN/04-图形与文本/01b-基本形状进阶.md

### `Annulus`
```python
# TODO: exact signature not printed in source. Shares AnnularSector params plus:
#   mark_paths_closed: bool = False   # do not change
def __init__(self, inner_radius: float = 1, outer_radius: float = 2, ...) -> None
```
- `ret`: donut ring.
- `args`: same table as `AnnularSector` (`inner_radius`, `outer_radius`, `angle`, `start_angle`, `fill_opacity`, `stroke_width`, `color`), plus `mark_paths_closed: bool = False` (**do not change**).
- `see`: ../zh_CN/04-图形与文本/01b-基本形状进阶.md

### `CubicBezier`
```python
def __init__(self, start_anchor: Point3DLike, start_handle: Point3DLike,
             end_handle: Point3DLike, end_anchor: Point3DLike,
             **kwargs: Any) -> None
```
- `ret`: cubic bezier curve (`VMobject` direct; **generic fallback** render). `get_start()` / `get_end()`.
- `args`:
  - `start_anchor` / `end_anchor: Point3DLike` — curve endpoints (on the curve).
  - `start_handle` / `end_handle: Point3DLike` — control handles (off-curve).
- `notes`: positional order is `start_anchor → start_handle → end_handle → end_anchor`; swapping anchor/handle throws the curve off-range.
- `see`: ../zh_CN/04-图形与文本/01b-基本形状进阶.md

### `ArcPolygon`
```python
def __init__(self, *vertices: Point3DLike, angle: float = TAU / 4,
             radius: float | None = None, arc_config: list[dict] | None = None,
             **kwargs: Any) -> None
```
- `ret`: polygon whose edges are arcs (`VMobject` direct; **generic fallback**).
- `args`:
  - `*vertices: Point3DLike...` — required; **each positional arg is one vertex**.
  - `angle: float = TAU/4` — uniform edge bend (radians).
  - `radius: float | None = None` — fixed-radius bend; overrides `angle` when set.
  - `arc_config: list[dict] | None = None` — per-edge `{"radius":..., "arc_center":...}`; alternative to `angle`.
- `notes`: concavity per edge is decided by vertex write order **and** sign of `angle`.
- `see`: ../zh_CN/04-图形与文本/01b-基本形状进阶.md

### `ArcPolygonFromArcs`
```python
def __init__(self, *arcs: Arc | ArcBetweenPoints, **kwargs: Any) -> None
```
- `ret`: single object from pre-built arcs (`VMobject` direct; **generic fallback**).
- `args`:
  - `*arcs: Arc | ArcBetweenPoints...` — required; arcs must be **strictly head-to-tail** (prev `end` == next `start`).
- `see`: ../zh_CN/04-图形与文本/01b-基本形状进阶.md

## Lines

### `Line`
```python
def __init__(self, start: Point3DLike | Mobject = [-1, 0, 0],
             end: Point3DLike | Mobject = [1, 0, 0], buff: float = 0,
             path_arc: float = 0, **kwargs: Any) -> None
```
- `ret`: line (`VMobject`). Native `_send_line`.
- `args`:
  - `start` / `end: Point3DLike | Mobject` — coords, or an `Mobject` (line snaps to it; useful for connectors).
  - `buff: float = 0` — inset at both ends.
  - `path_arc: float = 0` — bend the segment into an arc (radians); sign picks side.
- `notes`: default `buff=0` (contrast `Arrow` default `0.25`).
- `see`: ../zh_CN/04-图形与文本/02-线与箭头.md

### `DashedLine`
```python
def __init__(self, *args: Any, dash_length: float = 0.05,
             dashed_ratio: float = 0.5, **kwargs: Any) -> None
```
- `ret`: dashed line.
- `args`:
  - positional `start` / `end` — same as `Line`.
  - `dash_length: float = 0.05` — solid sub-segment length.
  - `dashed_ratio: float = 0.5` — solid fraction of one solid+gap period; `→1` = more continuous.
- `notes`: since 0.21 there is **no `num_dashes=`**; unknown kwargs are swallowed or error.
- `see`: ../zh_CN/04-图形与文本/02-线与箭头.md

### `TangentLine`
```python
def __init__(self, vmob: VMobject, alpha: float, length: float = 1,
             d_alpha: float = 1e-06, **kwargs: Any) -> None
```
- `ret`: tangent segment (`Line` subclass; native `_send_line`).
- `args`:
  - `vmob: VMobject` — required; curve to differentiate.
  - `alpha: float` — required; curve parameter ratio (0 start, 1 end; `0.5` mid). Not an x-coordinate.
  - `length: float = 1` — total tangent segment length.
  - `d_alpha: float = 1e-06` — numeric derivative step; **do not change**.
- `see`: ../zh_CN/04-图形与文本/02-线与箭头.md

### `Elbow`
```python
def __init__(self, width: float = 0.2, angle: float = 0,
             **kwargs: Any) -> None
```
- `ret`: small right-angle corner mark (`VMobject` direct; **generic fallback**).
- `args`:
  - `width: float = 0.2` — length of the two little legs.
  - `angle: float = 0` — whole-object rotation (radians); `PI/2` = 90°.
- `notes`: tiny corner glyph, not an axis.
- `see`: ../zh_CN/04-图形与文本/02-线与箭头.md

### `Arrow`
```python
def __init__(self, *args: Any, stroke_width: float = 6, buff: float = 0.25,
             max_tip_length_to_length_ratio: float = 0.25,
             max_stroke_width_to_length_ratio: float = 5,
             **kwargs: Any) -> None
```
- `ret`: line with a tip. Methods: `Arrow.scale(factor, scale_tips=True)`, `Arrow.get_normal_vector()`.
- `args`:
  - `*args` — first two positional are `start`, `end` (defaults `[-1,0,0]`, `[1,0,0]`); may be `Mobject`.
  - `stroke_width: float = 6` — shaft width.
  - `buff: float = 0.25` — end inset; **note: `Line` default is 0**. Use `buff=0` for tips flush to endpoints.
  - `max_tip_length_to_length_ratio: float = 0.25` — tip/shaft cap; **do not hand-tune**.
  - `max_stroke_width_to_length_ratio: float = 5` — width/length cap; **do not hand-tune**.
- `see`: ../zh_CN/04-图形与文本/02-线与箭头.md

### `Vector`
```python
def __init__(self, direction: array-like = RIGHT, buff: float = 0,
             **kwargs: Any) -> None
```
- `ret`: arrow (`Arrow` subclass; native `_send_arrow`). `coordinate_label(integer_labels=True, n_dim=2, color=None)` → a `Matrix` of the endpoint coords.
- `args`:
  - `direction: array-like = RIGHT` — direction/endpoint from the origin.
  - `buff: float = 0` — start inset; starts flush at origin.
- `notes`:
  - Born at the origin; move with `.shift(...)`.
  - `coordinate_label()` returns a plain `Matrix`; place it yourself with `.next_to(...)`.
  - Pitfall: the label uses the endpoint's **current world coords**, rounded per `integer_labels=True`. Shift first → labels the shifted coords.
- `see`: ../zh_CN/04-图形与文本/02-线与箭头.md

### `DoubleArrow`
```python
def __init__(self, *args: Any, **kwargs: Any) -> None
```
- `ret`: arrow with tips at both ends (`Arrow` subclass; native `_send_arrow`).
- `args`: identical to `Arrow`.
- `see`: ../zh_CN/04-图形与文本/02-线与箭头.md

## Arrow tips

### `TipableVMobject`
```python
def __init__(self, tip_length: float = 0.35,
             normal_vector: Vector3DLike = [0, 0, 1],
             tip_style: dict | None = None, **kwargs: Any) -> None
```
- `ret`: base class for anything that can carry a tip (`Line`/`Arrow`/`Arc`/`Circle` inherit it). Normally not instantiated directly.
- `args`:
  - `tip_length: float = 0.35` — tip length; overridable per `add_tip(tip_length=)`.
  - `normal_vector: Vector3DLike = [0, 0, 1]` — plane normal of the tip; **do not change**.
  - `tip_style: dict | None = None` — tip style overrides; leave `None`.
- `notes`: tips are custom curves → generic bezier fallback.
- `see`: ../zh_CN/04-图形与文本/02b-箭头尖端.md

### `TipableVMobject.add_tip`
```python
def add_tip(self, tip: ArrowTip | None = None,
            tip_shape: type[ArrowTip] | None = None,
            tip_length: float | None = None,
            tip_width: float | None = None,
            at_start: bool = False) -> Self
```
- `ret`: `self` (chainable, works with `.animate`).
- `args`:
  - `tip: ArrowTip | None = None` — a **pre-built tip instance**; mutually exclusive with `tip_shape`.
  - `tip_shape: type[ArrowTip] | None = None` — the **class itself** (no parentheses), e.g. `ArrowSquareTip`.
  - `tip_length: float | None = None` — overrides constructor `tip_length`.
  - `tip_width: float | None = None` — overrides tip width.
  - `at_start: bool = False` — `True` puts the tip at the **start** end.
- `notes`:
  - `tip=` takes an instance, `tip_shape=` takes a class: `tip_shape=ArrowSquareTip` (no parens) vs `tip=ArrowSquareTip(length=0.42)`.
  - When both constructor `tip_length` and `add_tip(tip_length=)` exist, the latter wins.
  - `Line` has no tip by default; only `Arrow` ships with one.
- `see`: ../zh_CN/04-图形与文本/02b-箭头尖端.md
- `eg`:
```python
ln2 = Line([-5.5, 0.75, 0], [0.5, 0.75, 0], color=RED, stroke_width=7, tip_length=0.6)
win.play(ln2.animate.add_tip())
tip = ln2.get_tip()
```

### `TipableVMobject.get_tip`
```python
def get_tip(self) -> VMobject
```
- `ret`: the tip object (**no parameters** — `get_tip(0)` is wrong). With two tips, returns the end one. Use `get_tips()` for all (insertion order).
- `see`: ../zh_CN/04-图形与文本/02b-箭头尖端.md

### Tip shapes (`tip_shape` / `tip=` values)
```python
StealthTip(fill_opacity=1, stroke_width=3, length=0.175, start_angle=PI, **kwargs)
ArrowTriangleTip(fill_opacity=0, stroke_width=3, length=0.35, width=0.35, start_angle=PI, **kwargs)
ArrowTriangleFilledTip(fill_opacity=1, stroke_width=0, **kwargs)
ArrowCircleTip(fill_opacity=0, stroke_width=3, length=0.35, start_angle=PI, **kwargs)
ArrowCircleFilledTip(fill_opacity=1, stroke_width=0, **kwargs)
ArrowSquareTip(fill_opacity=0, stroke_width=3, length=0.35, start_angle=PI, **kwargs)
ArrowSquareFilledTip(fill_opacity=1, stroke_width=0, **kwargs)
```
- `ret`: `ArrowTip` subclass (`ArrowTip` → `VMobject`). Seven shapes, hollow/solid in pairs.
- `args`:
  - `fill_opacity: float` — hollow `0` / solid `1`; `StealthTip` is **solid (`1`)** by default.
  - `stroke_width: float` — hollow `3` / solid `0`.
  - `length: float = 0.35` — tip length; `StealthTip` `0.175`. Filled variants accept it via `**kwargs` (`ArrowTriangleFilledTip(length=0.5)` works).
  - `width: float = 0.35` — only listed on `ArrowTriangleTip`; others are length==width or via `**kwargs`.
  - `start_angle: float = PI` — tip orientation; **do not change**.
- `notes`: `StealthTip` has no hollow counterpart and is short/solid. `tip_shape=` takes a class, not an instance.
- `see`: ../zh_CN/04-图形与文本/02b-箭头尖端.md

## Polygrams / polygons

### `Polygram`
```python
def __init__(self, *vertex_groups: ArrayLike, color: ManimColor = BLUE,
             **kwargs: Any) -> None
```
- `ret`: closed polygon. Methods: `get_vertices()`, `round_corners(...)`.
- `args`:
  - `*vertex_groups: array-like...` — **each positional arg = one vertex group** (a list of points): `Polygram([p1, p2, p3, p4])`.
  - `color: ManimColor = BLUE`.
- `errs`:
  - `IndexError` — passing single points as separate args (`Polygram(p1, p2, ...)`) → use `Polygon` instead.
- `see`: ../zh_CN/04-图形与文本/03-多边形与星形.md

### `Polygon`
```python
def __init__(self, *vertices: ArrayLike, **kwargs: Any) -> None
```
- `ret`: closed polygon (auto-closed).
- `args`:
  - `*vertices: array-like...` — one positional per vertex; `[x, y]` auto-pads z=0.
- `notes`: vertex order determines edge connectivity.
- `see`: ../zh_CN/04-图形与文本/03-多边形与星形.md

### `RegularPolygon`
```python
def __init__(self, n: int = 6, **kwargs: Any) -> None
```
- `ret`: regular polygon.
- `args`:
  - `n: int = 6` — side count; ≥3.
  - `radius: float = 1` — circumradius (inherited).
  - `start_angle: float | None = None` — auto-chosen when `None`.
- `notes`: `radius` default 1 is small; scale up as needed.
- `see`: ../zh_CN/04-图形与文本/03-多边形与星形.md

### `Triangle`
```python
def __init__(self, **kwargs: Any) -> None
```
- `ret`: equilateral triangle ≡ `RegularPolygon(n=3)`.
- `args`: `radius: float = 1`, `start_angle: float | None = None`.
- `see`: ../zh_CN/04-图形与文本/03-多边形与星形.md

### `RegularPolygram`
```python
def __init__(self, num_vertices: int, *, density: int = 2, radius: float = 1,
             start_angle: float | None = None, **kwargs: Any) -> None
```
- `ret`: star/polygram wireframe. Common generator for `RegularPolygon` and `Star`. `get_vertices()` applies.
- `args`:
  - `num_vertices: int` — required; ≥3.
  - `density: int = 2` — connect every `density`-th vertex; `1` = regular polygon, `2` = pentagram wireframe.
  - `radius: float = 1` — circumradius.
  - `start_angle: float | None = None`.
- `notes`: `density=1` degenerates to a plain regular polygon. With `Create` it draws in vertex order (crossing stars show "threading" — normal).
- `see`: ../zh_CN/04-图形与文本/03-多边形与星形.md

### `Star`
```python
def __init__(self, n: int = 5, *, outer_radius: float = 1,
             inner_radius: float | None = None, density: int = 2,
             start_angle: float = TAU / 4, **kwargs: Any) -> None
```
- `ret`: star (`Polygon` subclass; **native `_send_polygon`** — a `Star` is one group of `2*n` vertices, not a bezier fallback).
- `args`:
  - `n: int = 5` — point count; ≥3.
  - `outer_radius: float = 1` — outer vertex radius.
  - `inner_radius: float | None = None` — inner radius; `None` derives it from `density` (standard proportions).
  - `density: int = 2` — only used when `inner_radius=None`; `inner_radius` wins if both given.
  - `start_angle: float = TAU/4` — rotation; default puts one point up.
- `see`: ../zh_CN/04-图形与文本/03-多边形与星形.md

### `Polygram.round_corners`
```python
def round_corners(self, radius: float = 0.5,
                  evenly_distribute_anchors: bool = False,
                  components_per_rounded_corner: int = 2) -> Self
```
- `ret`: `self` (chainable — callable at the end of a constructor chain).
- `args`:
  - `radius: float = 0.5` — corner radius; valid `0` … half the shortest edge.
  - `evenly_distribute_anchors: bool = False` — **do not change**.
  - `components_per_rounded_corner: int = 2` — **do not change**.
- `notes`: radius beyond half the shortest edge eats the edge and deforms the shape. Corners are real arcs (bezier-tessellated, not chamfers).
- `see`: ../zh_CN/04-图形与文本/03-多边形与星形.md
- `eg`:
```python
t1 = Polygon([-5.9, -0.7, 0], [-3.3, -0.7, 0], [-3.7, -2.5, 0],
             [-5.5, -2.5, 0], color=ORANGE, fill_opacity=0.55).round_corners(0.15)
```

### `Rectangle`
```python
def __init__(self, color: ParsableManimColor = WHITE, height: float = 2.0, width: float = 4.0, grid_xstep: float | None = None, grid_ystep: float | None = None, mark_paths_closed: bool = True, close_new_points: bool = True, **kwargs) -> None
```
- `ret`: rectangle.
- `args`:
  - `color: ParsableManimColor = WHITE`.
  - `height: float = 2.0` — any positive number.
  - `width: float = 4.0` — any positive number.
  - `grid_xstep: float | None = None` — **do not change**; adds a sub-mobject grid layer (changes `submobjects`, affecting `set_color`/`MoveToTarget`/`Create`). Prefer `VGroup(rect, hand-drawn lines)`.
  - `grid_ystep: float | None = None` — same caveat.
  - `mark_paths_closed: bool = True` — **do not change** (fill determination).
  - `close_new_points: bool = True` — **do not change**.
- `notes`: `width`/`height` are construction-time only; resize later with `scale()`/`stretch()`. `Rectangle(..., corner_radius=0.3)` converts to `RoundedRectangle`.
- `see`: ../zh_CN/04-图形与文本/03b-矩形与特殊多边形.md

### `Square`
```python
def __init__(self, side_length: float = 2.0, **kwargs) -> None
```
- `ret`: square.
- `args`:
  - `side_length: float = 2.0` — construction-time size **and a read/write property**. Writing `sq.side_length = 2.6` immediately rescales (internally `scale(new/old)`).
- `notes`: read = actual distance between adjacent vertices (still correct after 3D rotation); write = `scale(new/old)`, so fill and stroke width scale proportionally too.
- `see`: ../zh_CN/04-图形与文本/03b-矩形与特殊多边形.md

### `RoundedRectangle`
```python
def __init__(self, corner_radius: float | list[float] = 0.5, **kwargs) -> None
```
- `ret`: rounded rectangle.
- `args`:
  - `corner_radius: float | list[float] = 0.5` — one number (all corners) or a length-4 list in order **top-left → top-right → bottom-right → bottom-left**.
  - `width: float = 4.0` / `height: float = 2.0` — inherited from `Rectangle`.
- `notes`: radius > half width/height makes adjacent arcs consume each other → capsule.
- `see`: ../zh_CN/04-图形与文本/03b-矩形与特殊多边形.md

### `Cutout`
```python
def __init__(self, main_shape: VMobject, *mobjects: VMobject, **kwargs) -> None
```
- `ret`: `main_shape` with the extra shapes added as reverse sub-paths in the same fill.
- `args`:
  - `main_shape: VMobject` — required; any `VMobject`.
  - `*mobjects: VMobject...` — required; any number of shapes to cut.
- `notes`: hole "transparency" is decided by the fill rule, not placement. If a hole shape has only stroke (`fill_opacity=0`), the main fill covers it (looks like just a ring drawn). For real holes enable the hole's `fill_opacity`, or use `Difference`.
- `see`: ../zh_CN/04-图形与文本/03b-矩形与特殊多边形.md · ../zh_CN/04-图形与文本/05-布尔运算.md

### `ConvexHull`
```python
def __init__(self, *points: Point3DLike, tolerance: float = 1e-05, **kwargs) -> None
```
- `ret`: minimum convex polygon around the input points.
- `args`:
  - `*points: array-like...` — required; any number (lists, arrays, `Dot`s mixed). Order irrelevant; interior points dropped.
  - `tolerance: float = 1e-05` — collinearity tolerance; **do not change**.
- `notes`: give ≥3 points; fewer degenerates to a segment/point.
- `see`: ../zh_CN/04-图形与文本/03b-矩形与特殊多边形.md

## Angles & annotation boxes

### `Angle`
```python
def __init__(self, line1: Line, line2: Line, radius: float | None = None, quadrant: AngleQuadrant = (1, 1), other_angle: bool = False, dot: bool = False, dot_radius: float | None = None, dot_distance: float = 0.55, dot_color: ParsableManimColor = WHITE, elbow: bool = False, **kwargs) -> None
```
- `ret`: angle mark.
- `args`:
  - `line1` / `line2: Line` — required; any `Line`/`Arrow`. One object can only be marked once — pass copies for a second mark.
  - `radius: float | None = None` — mark-arc radius; auto-derived from the two edges when omitted.
  - `quadrant: tuple[int,int] = (1, 1)` — one of `(1,1)`/`(-1,1)`/`(1,-1)`/`(-1,-1)`.
  - `other_angle: bool = False` — draw the reflex (other-side) angle.
  - `dot: bool = False` — add a dot inside the arc.
  - `dot_radius: float | None = None` — defaults to 1/10 of the arc radius.
  - `dot_distance: float = 0.55` — 0 at vertex, 1 on the arc.
  - `dot_color: ParsableManimColor = WHITE`.
  - `elbow: bool = False` — use a right-angle elbow instead of an arc.
- `errs`:
  - `Angle.get_value(degrees=False)` — **do not use**: upstream ManimCE 0.21 bug (`Angle` has no `angle_value` attribute; both engines crash). Read the angle as the difference of the two edges' `get_angle()`.
- `notes`: `quadrant` (which quadrant) and `other_angle` (complement side) are independent; combine for full coverage.
- `see`: ../zh_CN/04-图形与文本/04-角度与标注框.md

### `Angle.from_three_points`
```python
@classmethod
def from_three_points(cls, A: Point3DLike, B: Point3DLike, C: Point3DLike, **kwargs) -> Angle
```
- `ret`: `Angle` at vertex B.
- `args`:
  - `A: Point3DLike` — endpoint of edge 1 (not the vertex).
  - `B: Point3DLike` — **vertex**; edges are B→A and B→C.
  - `C: Point3DLike` — endpoint of edge 2.
  - `**kwargs` — same as `Angle`.
- `see`: ../zh_CN/04-图形与文本/04-角度与标注框.md

### `RightAngle`
```python
def __init__(self, line1: Line, line2: Line, length: float | None = None, **kwargs) -> None
```
- `ret`: right-angle mark (shorthand for `Angle(..., elbow=True)`).
- `args`:
  - `line1` / `line2: Line` — required.
  - `length: float | None = None` — side length of the little square; auto-derived when `None`.
  - `**kwargs` — color etc.
- `notes`: `length` is the leg length (not radius); too large exceeds the edges themselves.
- `see`: ../zh_CN/04-图形与文本/04-角度与标注框.md

### `SurroundingRectangle`
```python
def __init__(self, *mobjects: Mobject, color: ParsableManimColor = PURE_YELLOW, buff: float | tuple[float, float] = SMALL_BUFF, corner_radius: float = 0.0, **kwargs) -> None
```
- `ret`: stroke-only box around the objects.
- `args`:
  - `*mobjects: Mobject...` — required; multiple → combined bounding box.
  - `color: ParsableManimColor = PURE_YELLOW`.
  - `buff: float | tuple[float,float] = SMALL_BUFF` (0.1) — gap; `(h, v)` tuple supported.
  - `corner_radius: float = 0.0` — 0 = sharp corners.
- `notes`: stroke only, so it does not occlude content; to occlude use `z_index` or `BackgroundRectangle`.
- `see`: ../zh_CN/04-图形与文本/04-角度与标注框.md

### `BackgroundRectangle`
```python
def __init__(self, *mobjects: Mobject, color: ParsableManimColor | None = None, stroke_width: float = 0, stroke_opacity: float = 0, fill_opacity: float = 0.75, buff: float | tuple[float, float] = 0, **kwargs) -> None
```
- `ret`: filled background block behind the objects.
- `args`:
  - `*mobjects: Mobject...` — required; combined bounding box.
  - `color: ParsableManimColor | None = None` — `None` treated as black.
  - `stroke_width: float = 0`.
  - `stroke_opacity: float = 0`.
  - `fill_opacity: float = 0.75` — 0.75 shows 25% background.
  - `buff: float | tuple[float,float] = 0` — extra margin.
- `notes`: a separate mobject; ordering (`add` order / `z_index`) decides whether it covers existing content. Black default is nearly invisible on a pure-black background — intended for dark scenes to raise readability.
- `see`: ../zh_CN/04-图形与文本/04-角度与标注框.md

### `Cross`
```python
def __init__(self, mobject: Mobject | None = None, stroke_color: ParsableManimColor = RED, stroke_width: float = 6.0, scale_factor: float = 1.0, **kwargs) -> None
```
- `ret`: cross mark.
- `args`:
  - `mobject: Mobject | None = None` — the crossed object; position and size follow it. `None` = default-size cross.
  - `stroke_color: ParsableManimColor = RED`.
  - `stroke_width: float = 6.0`.
  - `scale_factor: float = 1.0` — relative to the crossed object (not absolute length).
- `see`: ../zh_CN/04-图形与文本/04-角度与标注框.md

### `Underline`
```python
def __init__(self, mobject: Mobject, buff: float = SMALL_BUFF, **kwargs) -> None
```
- `ret`: underline line (length = object width automatically).
- `args`:
  - `mobject: Mobject` — required.
  - `buff: float = SMALL_BUFF` (0.1) — vertical gap.
  - `**kwargs` — `color=`, `stroke_width=` pass through.
- `see`: ../zh_CN/04-图形与文本/04-角度与标注框.md

## Labels

### `Label`
```python
def __init__(self, label: str | ManimTextLabel, label_config: dict | None = None, box_config: dict | None = None, frame_config: dict | None = None, **kwargs) -> None
```
- `ret`: `VGroup` of frame + box + text (three layers); whole thing is `.scale()`/`.move_to()`-able.
- `args`:
  - `label: str | MathTex | Text | Typst` — required. `str` renders via `MathTex`.
  - `label_config: dict | None = None` — passed to the label; **string labels only** (defaults `color=WHITE`, `font_size=48`).
  - `box_config: dict | None = None` — background box config, e.g. `{"color": TEAL, "fill_opacity": 0.8}`.
  - `frame_config: dict | None = None` — outer frame config, e.g. `{"color": ORANGE, "stroke_width": 6}`.
- `notes`: `label_config`/`box_config`/`frame_config` are **only used when `label` is a `str`**. Passing an existing `Text`/`MathTex` object ignores all three dicts (the object's own style wins).
- `see`: ../zh_CN/04-图形与文本/04b-带标签标注.md

### `LabeledLine`
```python
def __init__(self, label: str | ManimTextLabel, label_position: float = 0.5, label_config: dict | None = None, box_config: dict | None = None, frame_config: dict | None = None, *args, **kwargs) -> None
```
- `ret`: line with a label.
- `args`:
  - `label: str | MathTex | Text | Typst` — required; `str` via `MathTex`.
  - `label_position: float = 0.5` — ratio along the line (0 start … 1 end).
  - `label_config` / `box_config` / `frame_config: dict | None = None` — string-label only (as `Label`).
  - `*args` / `**kwargs` — remaining args go to `Line`.
- `notes`:
  - **`start`/`end` must be keyword args**: `LabeledLine("3cm", start=..., end=...)`. The first 5 positional params are consumed by `label`/`label_position`/`label_config`/`box_config`/`frame_config`, so positional 2–6 shift everything (upstream bug).
  - `label_position=0`/`1` puts the label on the endpoint.
- `see`: ../zh_CN/04-图形与文本/04b-带标签标注.md

### `LabeledArrow`
```python
def __init__(self, *args, **kwargs) -> None   # forwards to LabeledLine / Arrow; same signature as LabeledLine
```
- `ret`: arrow with a label.
- `args`: identical to `LabeledLine` (`label`/`label_position`/`*_config`), with `start`/`end` **keyword-required**; extra kwargs go to `Arrow`.
- `notes`: the arrow head consumes line length, so the label appears slightly further along than on `LabeledLine` at the same `label_position`.
- `see`: ../zh_CN/04-图形与文本/04b-带标签标注.md

### `LabeledPolygram`
```python
def __init__(self, *vertex_groups: Point3DLike_Array, label: str | ManimTextLabel, precision: float = 0.01, label_config: dict | None = None, box_config: dict | None = None, frame_config: dict | None = None, **kwargs) -> None
```
- `ret`: polygram with one label at the "pole of inaccessibility".
- `args`:
  - `*vertex_groups: array-like...` — required; **each group must be a full ring**: `LabeledPolygram([v1, v2, v3], label=...)`.
  - `label: str | Mobject` — required.
  - `precision: float = 0.01` — PolyLabel search precision; must match the figure scale (units-scale figures: default; figures spanning 1e4 units: 1–10).
  - `label_config` / `box_config` / `frame_config: dict | None = None` — string-label only.
- `errs`:
  - `IndexError: too many indices for array: array is 1-dimensional, but 2 were indexed` — passing individual points as separate positional args instead of one ring per group.
- `notes`: only **one** label; with multiple rings it is placed in the largest ring by area. Open rings auto-close.
- `see`: ../zh_CN/04-图形与文本/04b-带标签标注.md

## Boolean ops

> All four return a **brand-new** `VMobject`; inputs are not mutated. `**kwargs` (style) apply to the result. Inputs must be closed/fillable (`Circle`/`Square`/`Polygon`; not `Line`).

### `Union`
```python
def __init__(self, *vmobjects: VMobject, **kwargs) -> None
```
- `ret`: new `VMobject` = merged outline; overlaps keep a single contour.
- `args`:
  - `*vmobjects: VMobject...` — required; ≥2.
  - `**kwargs` — result style (`color=GOLD, stroke_width=6`, then `.set_fill(GOLD, 0.85)`).
- `see`: ../zh_CN/04-图形与文本/05-布尔运算.md

### `Difference`
```python
def __init__(self, subject: VMobject, clip: VMobject, **kwargs) -> None
```
- `ret`: new `VMobject` = `subject` minus the `clip` overlap. **Directional** — swapping args changes the result.
- `args`:
  - `subject: VMobject` — required; the shape being reduced.
  - `clip: VMobject` — required; the shape subtracted.
  - `**kwargs` — result style.
- `notes`: a single boolean subtraction, no automatic ring. A ring appears naturally when `clip` lies fully inside `subject`.
- `see`: ../zh_CN/04-图形与文本/05-布尔运算.md

### `Intersection`
```python
def __init__(self, *vmobjects: VMobject, **kwargs) -> None
```
- `ret`: new `VMobject` = common overlap region.
- `args`:
  - `*vmobjects: VMobject...` — required; ≥2.
  - `**kwargs` — result style.
- `notes`: fully disjoint inputs → an **empty object**: still a `VMobject`, just no visible points. Not a render failure.
- `see`: ../zh_CN/04-图形与文本/05-布尔运算.md

### `Exclusion`
```python
def __init__(self, subject: VMobject, clip: VMobject, **kwargs) -> None
```
- `ret`: new `VMobject` = symmetric difference (XOR): non-overlapping parts kept, overlap hollowed.
- `args`:
  - `subject: VMobject` — required.
  - `clip: VMobject` — required.
  - `**kwargs` — result style.
- `notes`: complementary to `Union`. Common "hollow highlight" pattern: draw `Union`, then overlay `Exclusion`.
- `see`: ../zh_CN/04-图形与文本/05-布尔运算.md

## Containers & grouping

### `VGroup`
```python
def __init__(self, *vmobjects: VMobject, **kwargs) -> None
```
- `ret`: container of vector objects.
- `args`:
  - `*vmobjects: VMobject...` — may be empty (add later).
- `errs`:
  - `TypeError: Only values of type VMobject can be added as submobjects of ...` — adding a non-`VMobject` (e.g. `ImageMobject`). Use `Group` instead.
- `notes`:
  - Methods: `add(*vmobjects)`, `remove(*vmobjects)`, `arrange(direction, buff)`, `shift(...)`, indexing `vg[i]` (`-1` = last), whole-group styles (`set_color_by_gradient` etc. apply to all children).
  - `arrange` re-lays-out the **entire** group, so re-`arrange` after `add`.
  - Whole-group styles change style only, not relative positions.
- `see`: ../zh_CN/04-图形与文本/06-容器与组合.md

### `Group`
```python
# TODO: exact signature not printed in source.
def __init__(self, *mobjects: Mobject, **kwargs) -> None
```
- `ret`: general container, **not type-limited** (holds `ImageMobject` etc. alongside shapes).
- `notes`: use when `VGroup` would raise `TypeError` on non-vector children.
- `see`: ../zh_CN/04-图形与文本/06-容器与组合.md

### `VGroup.arrange` / `VDict.arrange`
```python
arrange(self, direction: Vector3DLike = RIGHT, buff: float = DEFAULT_MOBJECT_TO_MOBJECT_BUFFER, ...) -> Self
```
- `ret`: `self` (chainable).
- `args`: `direction` (e.g. `RIGHT`, `DOWN`, `DR`), `buff` (spacing). Exact remaining params not printed in source — TODO.
- `see`: ../zh_CN/04-图形与文本/06-容器与组合.md

### `VDict`
```python
def __init__(self, mapping_or_iterable: Mapping[Hashable, VMobject] | Iterable[tuple[Hashable, VMobject]] = {}, show_keys: bool = False, **kwargs) -> None
```
- `ret`: keyed container.
- `args`:
  - `mapping_or_iterable: dict | iterable = {}` — dict or `[("key", mob), ...]` list.
  - `show_keys: bool = False` — render each key as text next to its child.
- `errs`:
  - `KeyError: 2` — indexing by integer. `VDict` is a dict, not a list; use `vd["c"]`.
- `notes`:
  - Methods: `add(mapping)`, `remove(key)`, `add_key_value_pair(key, value)`, `get_all_submobjects`.
  - `show_keys=True` key texts are submobjects too — they get `arrange`d/`shift`ed and counted by `get_all_submobjects()`.
- `see`: ../zh_CN/04-图形与文本/06-容器与组合.md

### `DashedVMobject`
```python
def __init__(self, vmobject: VMobject, num_dashes: int = 15, dashed_ratio: float = 0.5, dash_offset: float = 0, color: ManimColor = WHITE, equal_lengths: bool = True, **kwargs) -> None
```
- `ret`: dashed version of any `VMobject`.
- `args`:
  - `vmobject: VMobject` — required; any object (line, circle, rect, curve).
  - `num_dashes: int = 15`.
  - `dashed_ratio: float = 0.5` — solid fraction; `0.1` ≈ dotted.
  - `dash_offset: float = 0` — start offset along the path.
  - `color: ManimColor = WHITE`.
  - `equal_lengths: bool = True` — `False` splits by arc-length ratio (long segments longer); visible only on non-uniform paths (ellipse/curve).
- `see`: ../zh_CN/04-图形与文本/06-容器与组合.md

### `VectorizedPoint`
```python
def __init__(self, location: Point3DLike = ORIGIN, color: ManimColor = BLACK, fill_opacity: float = 0, stroke_width: float = 0, artificial_width: float = 0.01, artificial_height: float = 0.01, **kwargs) -> None
```
- `ret`: invisible anchor point. Methods: `get_location()`, `set_location(new_loc)`.
- `args`:
  - `location: Point3DLike = ORIGIN`.
  - `color: ManimColor = BLACK`.
  - `fill_opacity: float = 0` — set `1.0` to make it a visible dot.
  - `stroke_width: float = 0`.
  - `artificial_width: float = 0.01` — **reported** width (affects `p.width` and alignment math, not drawn size).
  - `artificial_height: float = 0.01` — reported height.
- `notes`: default is invisible with a 0.01 report size — it will not push spacing in an `arrange`; enlarge `artificial_width/height` for that.
- `see`: ../zh_CN/04-图形与文本/06-容器与组合.md

### `CurvesAsSubmobjects`
```python
def __init__(self, vmobject: VMobject, **kwargs) -> None
```
- `ret`: container with one child per sub-curve of the source.
- `args`:
  - `vmobject: VMobject` — required; child count = source's sub-curve count (a `Circle` → 8 bezier segments; a `Star` → 10 lines).
- `notes`: children are the **original curve segments**, now independent — shifting them all scatters the shape (the usual "per-segment fly/highlight" effect).
- `see`: ../zh_CN/04-图形与文本/06-容器与组合.md

## VMobject style

> All methods live on `VMobject` and apply to every shape/text/matrix/table. RTM status: `set_fill`/`set_stroke`/`set_color` core classes render-verified; multi-stop gradients and sheen work (native linear gradient from first→last stop); only `background_image` texture fill is not wired.

### `VMobject` (constructor style kwargs)
```python
VMobject(fill_color=None, fill_opacity=0.0, stroke_color=None, stroke_opacity=1.0, stroke_width=4, background_stroke_color=BLACK, background_stroke_opacity=1.0, background_stroke_width=0, sheen_factor=0.0, joint_type=None, sheen_direction=UL, close_new_points=False, cap_style=CapStyleType.AUTO, **kwargs)
```
- `ret`: n/a (constructor signature shared by all vector classes).
- `args`:
  - `fill_color: ManimColor = None`, `fill_opacity: float = 0.0` (no fill by default).
  - `stroke_color: ManimColor = None`, `stroke_opacity: float = 1.0`.
  - `stroke_width: float = 4` (global `DEFAULT_STROKE_WIDTH = 4`).
  - `background_stroke_color: ManimColor = BLACK`, `background_stroke_opacity: float = 1.0`, `background_stroke_width: float = 0`.
  - `sheen_factor: float = 0.0`, `sheen_direction: array-like = UL`.
  - `joint_type: str | None = None` — `round`/`miter`/`bevel`.
  - `close_new_points: bool = False`.
  - `cap_style: int | str = CapStyleType.AUTO` — `round`/`square`/`projecting`.
- `see`: ../zh_CN/04-图形与文本/07-VMobject样式.md

### `VMobject.set_fill`
```python
set_fill(self, color=None, opacity=None, family=True)
```
- `ret`: `self`.
- `args`:
  - `color: ManimColor | list | None = None` — accepts a color list for multi-color fill.
  - `opacity: float | None = None` — `None` leaves opacity unchanged (0–1).
  - `family: bool = True` — apply to submobjects.
- `notes`: read back with `get_fill_color()`, `get_fill_opacity()`.
- `see`: ../zh_CN/04-图形与文本/07-VMobject样式.md

### `VMobject.set_stroke`
```python
set_stroke(self, color=None, width=None, opacity=None, background=False, family=True)
```
- `ret`: `self`.
- `args`:
  - `color: ManimColor | None = None`.
  - `width: float | None = None`.
  - `opacity: float | None = None`.
  - `background: bool = False` — modify the background stroke channel instead.
  - `family: bool = True`.
- `notes`: to scale without widening the stroke, `mob.scale(2, scale_stroke=True)` semantics — see source; read back with `get_stroke_width()`, `get_stroke_color()`, `get_stroke_opacity()`.
- `see`: ../zh_CN/04-图形与文本/07-VMobject样式.md

### `VMobject.set_style`
```python
set_style(self, fill_color=None, fill_opacity=None, stroke_color=None, stroke_width=None, stroke_opacity=None, background_stroke_color=None, background_stroke_width=None, background_stroke_opacity=None, sheen_factor=None, sheen_direction=None, background_image=None, family=True)
```
- `ret`: `self`.
- `args`: all `None` by default → `None` means "keep current value".
  - fill: `fill_color`, `fill_opacity`.
  - stroke: `stroke_color`, `stroke_width`, `stroke_opacity`.
  - background stroke: `background_stroke_color`, `background_stroke_width`, `background_stroke_opacity`.
  - sheen: `sheen_factor`, `sheen_direction`.
  - `background_image: str | None = None` — **RTM Vulkan path does not wire it; no visual effect**.
  - `family: bool = True`.
- `notes`: combined `set_fill` + `set_stroke` + sheen. Multi-stop gradient fill is honored — RTM takes the first/last stop and runs a native linear gradient (not averaged to a single color). Read back with `get_style(simple=False)`, `match_style(vmobject, family=True)`.
- `see`: ../zh_CN/04-图形与文本/07-VMobject样式.md

### `VMobject.set_color`
```python
set_color(self, color, family=True)
```
- `ret`: `self`.
- `args`:
  - `color: ManimColor` — required.
  - `family: bool = True`.
- `notes`: convenience entry that hits fill + stroke at once (most visible on `Text`/`Dot`). Read back with `get_color()`.
- `see`: ../zh_CN/04-图形与文本/07-VMobject样式.md

### `VMobject.set_color_by_gradient`
```python
# TODO: exact signature not printed in source; observed call form:
#   vg.set_color_by_gradient(BLUE, PURPLE)          # whole VGroup
#   cs2.set_color_by_gradient(ORANGE, PURPLE)       # per-segment container
def set_color_by_gradient(self, *colors, family=True) -> Self
```
- `ret`: `self` (used with `.animate`).
- `args`: one or more colors; applies across all submobjects (whole-group gradient).
- `see`: ../zh_CN/04-图形与文本/06-容器与组合.md

### `VMobject.set_opacity`
```python
def set_opacity(self, opacity: float, family: bool = True) -> Self
```
- `ret`: `self`.
- `args`:
  - `opacity: float` — required; 0–1. Changes fill **and** stroke together.
  - `family: bool = True` — `True` lowers container + children; `False` changes only the container (children keep their own opacity).
- `notes`: the difference from `set_fill(color, 0.3)` is that this hits both channels. `family` is only observable on containers (`VGroup`/`Text`).
- `see`: ../zh_CN/04-图形与文本/07b-VMobject样式进阶.md

### `VMobject.set_sheen`
```python
def set_sheen(self, factor: float, direction: Vector3DLike | None = None, family: bool = True) -> Self
```
- `ret`: `self`.
- `args`:
  - `factor: float` — required; 0 = off (flat color), typical 0.2–1.5.
  - `direction: Vector3DLike | None = None` — gradient direction; `None` keeps existing `sheen_direction`.
  - `family: bool = True`.
- `notes`: sheen is a **fill** gradient (stroke not involved). `direction` is where the gradient points, so the highlight is at the **opposite** end (`UP` → bright top, dark bottom).
- `see`: ../zh_CN/04-图形与文本/07b-VMobject样式进阶.md

### `VMobject.set_sheen_direction`
```python
def set_sheen_direction(self, direction: Vector3DLike, family: bool = True) -> Self
```
- `ret`: `self`.
- `args`: `direction` (required), `family: bool = True`.
- `notes`: changes direction only; strength keeps the last `factor`.
- `see`: ../zh_CN/04-图形与文本/07b-VMobject样式进阶.md

### `VMobject.make_smooth`
```python
def make_smooth(self) -> Self
```
- `ret`: `self` (in-place; chainable). No params. Equivalent to `change_anchor_mode("smooth")`; turns polyline corners into smooth anchors.
- `notes`: to keep the original, `poly.copy().make_smooth()`.
- `see`: ../zh_CN/04-图形与文本/07b-VMobject样式进阶.md

### `VMobject.make_jagged`
```python
def make_jagged(self) -> Self
```
- `ret`: `self` (in-place). No params. Inverse of `make_smooth`; equivalent to `change_anchor_mode("jagged")`.
- `notes`: result is still a `VMobject` and still fillable, just no longer curved.
- `see`: ../zh_CN/04-图形与文本/07b-VMobject样式进阶.md

### `VMobject.pointwise_become_partial`
```python
def pointwise_become_partial(self, vmobject: VMobject, a: float, b: float) -> Self
```
- `ret`: `self`, now holding the sliced path.
- `args`:
  - `vmobject: VMobject` — required; source path.
  - `a: float` — required; start ratio 0–1.
  - `b: float` — required; end ratio; `[0, 1]` = whole path.
- `notes`: `a > b` does not error but yields a reversed/empty path; `a == b` degenerates to a point. Underlies "show only a segment" effects (e.g. passing flash): keep `b - a` fixed and slide the window.
- `see`: ../zh_CN/04-图形与文本/07b-VMobject样式进阶.md

### `VMobject.get_stroke_width`
```python
def get_stroke_width(self, background: bool = False) -> float
```
- `ret`: `float`.
- `args`:
  - `background: bool = False` — `False` = current stroke width; `True` = background stroke width (0 if never set).
- `notes`: returns the value given at construction/`set_stroke` — does **not** change with `scale()`; multiply by the scale factor yourself for width compensation.
- `see`: ../zh_CN/04-图形与文本/07b-VMobject样式进阶.md

### `VMobject.set_cap_style`
```python
def set_cap_style(self, cap_style: CapStyleType) -> Self
```
- `ret`: `self`.
- `args`:
  - `cap_style: CapStyleType` — required; `CapStyleType.ROUND` / `BUTT` / `SQUARE` / `AUTO`.
- `notes`: a **stroke** property, affects only open-path ends; closed paths (circle, rectangle) have no ends → no visible effect. `SQUARE` extends half the stroke width past each end.
- `see`: ../zh_CN/04-图形与文本/07b-VMobject样式进阶.md

### `VMobject.change_anchor_mode`
```python
def change_anchor_mode(self, mode: Literal["jagged", "smooth"]) -> Self
```
- `ret`: `self`.
- `args`:
  - `mode: str` — only `"smooth"` or `"jagged"`; the underlying switch for `make_smooth`/`make_jagged`.
- `errs`:
  - `ValueError` — passing any other string (e.g. the old `"corners"`).
- `see`: ../zh_CN/04-图形与文本/07b-VMobject样式进阶.md

### `VMobject.apply_function`
```python
def apply_function(self, function: MappingFunction, *, about_point: Point3DLike | None = None, about_edge: Vector3DLike | None = None) -> Self
```
- `ret`: `self`.
- `args`:
  - `function: callable` — required; takes a point, returns a new `[x, y, z]`. Gets **absolute** coordinates (not relative to the object center).
  - `about_point: Point3DLike | None = None` — **upstream-ignored**: ManimCE 0.21 `apply_function` does not read it; passing or omitting gives the same result. **RTM honors the reference point → the two engines render differently.** Do not rely on it.
  - `about_edge: Vector3DLike | None = None` — same upstream behavior.
- `notes`: because coordinates are absolute, `p * 1.5` pushes the object away from the origin; for in-place scaling write `center + (p - center) * 1.5` (precompute `center`).
- `see`: ../zh_CN/04-图形与文本/07b-VMobject样式进阶.md
- `eg`:
```python
a.apply_function(lambda p: p + 0.35 * np.sin(p[1] * PI) * RIGHT)
b.apply_function(lambda p: p * 1.5)
d.apply_function(lambda p: p * [1.0, 0.5, 1.0])
```

## Cross-cutting notes

- **RTM vs CE**:
  - `background_image` (texture fill) is not wired on the Vulkan path.
  - `apply_function` `about_point`/`about_edge`: RTM honors them, CE 0.21 ignores them → engines diverge.
  - `Angle.get_value()` crashes on both engines (upstream bug).
  - Multi-stop gradient fill: RTM uses first/last stop as a native linear gradient.
- **Native vs fallback**: `_send_arc` (Arc/Circle/Ellipse/Sector/Annulus), `_send_dot` (Dot/AnnotationDot/LabeledDot), `_send_line` (Line/DashedLine/TangentLine), `_send_arrow` (Arrow/Vector/DoubleArrow), `_send_polygon` (Polygram/Polygon/Triangle/Star). Fallback (correct but generic bezier): tips, `Elbow`, `CubicBezier`, `ArcPolygon`, `ArcPolygonFromArcs`.
- **Default color traps**: `Circle` default `RED`, no fill; `Dot` default `WHITE`, `radius=0.08`; `AnnularSector` family default `WHITE`, `stroke_width=0`.
