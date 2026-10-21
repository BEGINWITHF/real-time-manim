# mobject

> scope: `Mobject` / `VMobject` construction & containers, placement, measurement, scale/rotate/transform, style & color, copy/derive/state, `.animate` syntax, updaters (+ tool functions), updater-driven animations, `ValueTracker`, screen-frame & banner objects, low-frequency APIs. Symbols are re-exported from `real_time_manim` (top level) unless a different import is shown.
> src: ../zh_CN/02-Mobject通用/ (01-构造与容器, 01b-构造与容器-进阶, 02-摆放位置, 02b-摆放位置-进阶, 03-测量, 04-缩放旋转与变形, 04b-缩放旋转与变形-进阶, 05-样式与颜色, 06-复制派生与状态, 07-animate语法, 08-更新器, 08b-更新器工具函数, 09-更新器动画, 10-ValueTracker, 11-屏幕框架与横幅, 11b-低频其余API)

## 0. Conventions

- `Self` = receiver's own type; almost every mutator returns `self` for chaining.
- Geometry mutators act on the whole family (`family_members_with_points()`), i.e. every descendant that owns vertices — empty containers are skipped.
- RTM deviation from ManimCE is recorded under `notes:` prefixed `RTM:`.
- `win.play(...)` = `MLWindow` per-frame playback (see `scene-camera.md`, `runtime.md`).
- Type aliases in signatures are copied verbatim from source: `Point3DLike`, `Vector3DLike`, `ParsableManimColor`, `Point3D`, `Point3D_Array`, `PathFuncType`, `MappingFunction`, `MultiMappingFunction`, `MatrixMN`.

---

## 1. Construction & containers

### `Mobject`
```python
def __init__(self, color: ParsableManimColor | list[ParsableManimColor] = WHITE,
             name: str | None = None, dim: int = 3,
             target: Mobject | None = None, z_index: float = 0) -> None:
```
| arg | type | default | meaning |
| --- | --- | --- | --- |
| `color` | color str / `ManimColor` / list | `WHITE` | accepts `"red"`, `"#ff0000"`, `RED`, `ManimColor("#83c167")`, or a list (some subclasses color each submobject from the list). Subclasses consume it in `init_colors()` |
| `name` | `str \| None` | `None` | debug name only (affects `repr`); defaults to class name |
| `dim` | `int` | `3` | vertex-coordinate dimension. Do not change; only `3` works |
| `target` | `Mobject \| None` | `None` | `.target` cache slot, filled by `generate_target()`; do not set manually |
| `z_index` | `float` | `0` | paint order; larger = on top. Only equal `z_index` falls back to add order |

- `ret`: none (constructs instance).
- `notes`:
  - These 5 kwargs pass through `**kwargs` of **every** subclass constructor (`Square`, `Text`, `Circle`, …), so any subclass accepts them.
  - `z_index` participates in RTM paint order; under `ThreeDCamera` it is re-sorted by camera depth (see README §5).
- `see`: ../zh_CN/02-Mobject通用/01-构造与容器.md

### `Group`
```python
def Group(*mobjects: Mobject, **kwargs: Any) -> None:
```
- `ret`: new `Group`; no extra methods of its own (uses `Mobject` API).
- `args`:
  - `*mobjects: Mobject` — members; accepts any type (incl. `Text`, `ImageMobject`).
  - `**kwargs: Any` — forwarded to `Mobject.__init__` (e.g. `color=`, `z_index=`).
- `notes`:
  - `VGroup` accepts only vector objects (`VMobject` subclasses); a plain `Mobject` raises `TypeError`. `Group` accepts anything.
  - Adding the same object twice is ignored (use `.copy()` for a second copy).
  - Slicing a `Group` returns a `Group`, not a `VGroup`.
- `errs`:
  - `TypeError: ...` — constructing `VGroup(<non-VMobject>)`.
- `see`: ../zh_CN/02-Mobject通用/01-构造与容器.md

### `add` / `remove` / `add_to_back` / `insert`
```python
def add(*mobjects: Mobject) -> Self
def remove(*mobjects: Mobject) -> Self
def add_to_back(*mobjects: Mobject) -> Self
def insert(index: int, mobject: Mobject) -> Self
```
| arg | type | default | meaning |
| --- | --- | --- | --- |
| `*mobjects` | `Mobject` | — | objects to add/remove. `add` ignores duplicates and prints a warning; `remove` silently ignores missing |
| `index` | `int` | — | `insert` position; negatives follow Python list rules |
| `mobject` | `Mobject` | — | object to insert |

- `ret`: `self` (chainable).
- `notes`:
  - **Render order = `submobjects` list order**: head drawn first (bottom), tail last (top).
  - `add` appends to tail (top); `add_to_back` prepends (bottom); `insert` sets position exactly.
  - `insert` does **not** de-duplicate: an already-present object gains a second reference (remove first to move it).
  - Instant, no transition; use `FadeIn`/`Write` for an animated entry.
  - If the parent is already on screen, newly added children appear automatically.
- `see`: ../zh_CN/02-Mobject通用/01-构造与容器.md

### `__getitem__` / `__iter__` / `__len__`
```python
def __getitem__(value: int | slice) -> Mobject | Group
def __iter__() -> Iterator[Mobject]
def __len__() -> int
```
- `ret`: `int` → sub-`Mobject`; `slice` → new group of the **same type** (`VGroup` slice stays `VGroup`); `len()` → child count; iteration yields direct children.
- `args`:
  - `value: int | slice` — index/slice; negatives per Python.
- `notes`:
  - Backed by `split()` (self + direct children); does **not** expand nested containers.
  - Slice returns child **references**, not copies; mutate via `.copy()` for independence.
- `see`: ../zh_CN/02-Mobject通用/01-构造与容器.md

### `get_family` / `family_members_with_points` / `split`
```python
def get_family(recurse: bool = True) -> list[Mobject]
def family_members_with_points() -> list[Mobject]
def split() -> list[Mobject]
```
- `ret`:
  - `get_family` → flat list of self + **all** descendants (depth-first, de-duplicated).
  - `family_members_with_points` → only objects that actually own vertices (containers/empty groups dropped).
  - `split` → self (if it has points) + **direct** children (basis of indexing/iteration).
- `args`:
  - `recurse: bool = True` — kept only for OpenGL signature parity; value is ignored.
- `notes`:
  - `shift`/`scale`/`rotate` operate on exactly `family_members_with_points()`.
  - `recurse=False` does not limit to one level.
- `see`: ../zh_CN/02-Mobject通用/01b-构造与容器-进阶.md

### `has_points` / `has_no_points` / `get_num_points`
```python
def has_points() -> bool
def has_no_points() -> bool
def get_num_points() -> int
```
- `ret`: `bool` / `bool` / `int`.
- `notes`:
  - Empty `Group` → `has_points()=False`, count `0`. `Square` owns vertices (16). `Text` itself has `0` points — its vertices live in glyph submobjects.
  - Total vertices of a tree: use `get_all_points().shape[0]`, not `Text.get_num_points()`.
- `see`: ../zh_CN/02-Mobject通用/01b-构造与容器-进阶.md

### `set`
```python
def set(**kwargs: Any) -> Self
```
- `ret`: `self`.
- `args`:
  - `**kwargs: Any` — `attr=value` pairs, equivalent to `mob.attr = value`; must be real attributes (`width=`, `color=`, `fill_opacity=`).
- `notes`:
  - Mainly used with `.animate`: `win.play(rect.animate.set(width=7))`.
  - No validation; a typo is a silent dynamic assignment (no visual change, no error). Check with `dir(mob)`.
  - For `.animate.set(...)` the attribute must be interpolable (numbers, colors); string attributes jump.
  - Legacy `mob.get_foo()` / `mob.set_foo(v)` still work but emit `DeprecationWarning`.
- `see`: ../zh_CN/02-Mobject通用/01b-构造与容器-进阶.md

### `set_default` (classmethod)
```python
def set_default(**kwargs: Any) -> None
```
- `ret`: `None`.
- `args`:
  - `**kwargs: Any` — `__init__` kwargs to override, e.g. `side_length=1.0`.
- `notes`:
  - Class-level global change; affects only objects constructed **after** the call.
  - Called with **no args**, restores original defaults.
  - `Square` default side length is `2`, not `1`.
- `see`: ../zh_CN/02-Mobject通用/01b-构造与容器-进阶.md

### `reset_points` / `generate_points` / `init_colors`
```python
def reset_points() -> Self
def generate_points() -> Self
def init_colors(propagate_colors: bool = True) -> Self
```
- `ret`: `self`.
- `args`:
  - `propagate_colors: bool = True` — (`init_colors`) push color down the family.
- `notes`:
  - The three construction hooks: clear `points` → generate shape → initialize style from `color`.
  - Only needed when writing custom `Mobject` subclasses.
  - `generate_points` is effective only where the subclass really overrides it: `Circle`/`Arc` generate in the hook; `Square`/`Triangle`/`Polygon` set points in `__init__`, and the base `generate_points` is a no-op (so `reset_points()` then `generate_points()` will **not** restore their shape; measured on 0.21).
  - Regenerated shapes are centered at the origin.
- `see`: ../zh_CN/02-Mobject通用/01b-构造与容器-进阶.md

---

## 2. Placement

### `shift`
```python
def shift(*vectors: Vector3DLike) -> Self
```
- `ret`: `self`.
- `args`:
  - `*vectors: Vector3DLike` — displacement(s); multiple are summed internally in one move. Accepts `RIGHT * 2`, `UP + LEFT`.
- `notes`:
  - **Relative** displacement: `shift(RIGHT * 2)` = "2 more right", not "to x=2". Calls accumulate.
  - Base method; `next_to`/`to_edge` ultimately call it.
- `see`: ../zh_CN/02-Mobject通用/02-摆放位置.md

### `move_to`
```python
def move_to(point_or_mobject: Point3DLike | Mobject,
            aligned_edge: Vector3DLike = ORIGIN,
            coor_mask: Vector3DLike = [1, 1, 1]) -> Self
```
| arg | type | default | meaning |
| --- | --- | --- | --- |
| `point_or_mobject` | point / `Mobject` | — | target point, or another object (uses its critical point) |
| `aligned_edge` | vector | `ORIGIN` | which **own** critical point aligns: `ORIGIN`=center, `UR`=top-right, `UP`=top-edge midpoint |
| `coor_mask` | vector | `[1, 1, 1]` | per-axis mask; only axes with 1 are applied |

- `ret`: `self`.
- `notes`:
  - `aligned_edge` uses the **receiver's** critical point; passing an `Mobject` makes the target point come from the other object's critical point.
  - `coor_mask` multiplies per axis, e.g. `[1,0,0]` = x only.
- `see`: ../zh_CN/02-Mobject通用/02-摆放位置.md

### `next_to`
```python
def next_to(mobject_or_point: Mobject | Point3DLike,
            direction: Vector3DLike = RIGHT, buff: float = 0.25,
            aligned_edge: Vector3DLike = ORIGIN,
            submobject_to_align: Mobject | None = None,
            index_of_submobject_to_align: int | None = None,
            coor_mask: Vector3DLike = [1, 1, 1]) -> Self
```
| arg | type | default | meaning |
| --- | --- | --- | --- |
| `mobject_or_point` | `Mobject` / point | — | reference |
| `direction` | vector | `RIGHT` | side to place on (`UP`/`DOWN`/`LEFT`/`RIGHT` and diagonals) |
| `buff` | `float` | `0.25` | gap along `direction` |
| `aligned_edge` | vector | `ORIGIN` | alignment edge; positions reference `aligned_edge+direction` critical point against own `aligned_edge-direction` point |
| `submobject_to_align` | `Mobject \| None` | `None` | align one of **own** children (parent moves as a whole) |
| `index_of_submobject_to_align` | `int \| None` | `None` | use the i-th own child; when reference is an `Mobject`, its i-th child is the target too |
| `coor_mask` | vector | `[1, 1, 1]` | per-axis mask |

- `ret`: `self`.
- `notes`:
  - `submobject_to_align` takes priority over `index_of_submobject_to_align`.
  - `index_of_submobject_to_align` uses the **same index** on both self and reference (mismatched child counts misalign).
  - `buff` is along `direction` (diagonal direction → diagonal gap).
- `see`: ../zh_CN/02-Mobject通用/02-摆放位置.md

### `to_edge` / `to_corner`
```python
def to_edge(edge: Vector3DLike = LEFT, buff: float = 0.5) -> Self
def to_corner(corner: Vector3DLike = DL, buff: float = 0.5) -> Self
```
- `ret`: `self`.
- `args`:
  - `edge: Vector3DLike = LEFT` — only `UP`/`DOWN`/`LEFT`/`RIGHT`.
  - `corner: Vector3DLike = DL` — only `UL`/`UR`/`DL`/`DR`.
  - `buff: float = 0.5` — margin.
- `notes`:
  - `to_edge` changes only the edge axis; the other axis is untouched (wraps `align_on_border`).
  - Reference is the **frame** (`config` frame width/height), not `camera.frame`; a MovingCamera push can move objects out of view.
- `see`: ../zh_CN/02-Mobject通用/02-摆放位置.md

### `center` / `align_to`
```python
def center() -> Self
def align_to(mobject_or_point: Mobject | Point3DLike,
             direction: Vector3DLike = ORIGIN) -> Self
```
- `ret`: `self`.
- `args`:
  - `mobject_or_point: Mobject | Point3DLike` — alignment target.
  - `direction: Vector3DLike = ORIGIN` — only the axes of non-zero components are adjusted (`UP`/`DOWN`→y, `LEFT`/`RIGHT`→x, `ORIGIN`→fully coincide).
- `notes`:
  - `center()` moves the center to world origin `(0,0,0)`.
  - `align_to(other, UR)` aligns both x and y.
- `see`: ../zh_CN/02-Mobject通用/02-摆放位置.md

### `align_on_border`
```python
def align_on_border(direction: Vector3DLike, buff: float = 0.5) -> Self
```
- `ret`: `self`.
- `args`:
  - `direction: Vector3DLike` — edge direction (`UP`/`LEFT`, ...) or diagonal (`UL`/`DR`, ...); need not be a unit vector.
  - `buff: float = 0.5` — margin; internally subtracts `buff * direction`, so a non-unit vector scales the margin.
- `notes`:
  - `to_edge` / `to_corner` are wrappers over this.
- `see`: ../zh_CN/02-Mobject通用/02b-摆放位置-进阶.md

### `set_coord` / `set_x` / `set_y` / `set_z`
```python
def set_coord(value: float, dim: int, direction: Vector3DLike = ORIGIN) -> Self
def set_x(x: float, direction: Vector3DLike = ORIGIN) -> Self
def set_y(y: float, direction: Vector3DLike = ORIGIN) -> Self
def set_z(z: float, direction: Vector3DLike = ORIGIN) -> Self
```
- `ret`: `self`.
- `args`:
  - `value` / `x` / `y` / `z: float` — absolute target coordinate (not a delta).
  - `dim: int` — only `0`=x, `1`=y, `2`=z (`set_coord` only).
  - `direction: Vector3DLike = ORIGIN` — which critical point hits the coordinate (default center; `LEFT` = set the left edge's x).
- `notes`:
  - `set_x`/`set_y`/`set_z` are `set_coord` with fixed `dim`.
  - Only one axis changes.
- `see`: ../zh_CN/02-Mobject通用/02b-摆放位置-进阶.md

### `arrange`
```python
def arrange(direction: Vector3DLike = RIGHT, buff: float = 0.25,
            center: bool = True, **kwargs: Any) -> Self
```
- `ret`: `self`.
- `args`:
  - `direction: Vector3DLike = RIGHT` — layout direction (`RIGHT` row, `DOWN` column, ...).
  - `buff: float = 0.25` — gap between neighbours.
  - `center: bool = True` — move whole group to origin afterwards; `False` keeps position.
  - `**kwargs: Any` — forwarded to each `next_to` (e.g. `aligned_edge=`).
- `notes`:
  - Lays out from **current** child order; fix order with `sort` first.
- `see`: ../zh_CN/02-Mobject通用/02b-摆放位置-进阶.md

### `arrange_in_grid`
```python
def arrange_in_grid(rows: int | None = None, cols: int | None = None,
                    buff: float | tuple[float, float] = 0.25,
                    cell_alignment: Vector3DLike = ORIGIN,
                    row_alignments: str | None = None,
                    col_alignments: str | None = None,
                    row_heights: Iterable[float | None] | None = None,
                    col_widths: Iterable[float | None] | None = None,
                    flow_order: str = "rd", **kwargs: Any) -> Self
```
| arg | type | default | meaning |
| --- | --- | --- | --- |
| `rows` / `cols` | `int \| None` | `None` | grid size; one given → other inferred; neither → near-square; overflow → `ValueError` |
| `buff` | `float` or `(row, col)` tuple | `0.25` | cell spacing (tuple = row, col) |
| `cell_alignment` | vector | `ORIGIN` | element alignment inside a cell |
| `row_alignments` | `str \| None` | `None` | per row: `"u"` top / `"c"` center / `"d"` bottom |
| `col_alignments` | `str \| None` | `None` | per column: `"l"` left / `"c"` center / `"r"` right |
| `row_heights` | iterable \| `None` | `None` | per-row height; `None` = tallest in that row |
| `col_widths` | iterable \| `None` | `None` | per-column width; `None` = widest in that column |
| `flow_order` | `str` | `"rd"` | fill order: `rd`/`dr`/`ld`/`dl`/`ru`/`ur`/`lu`/`ul` (r=right, l=left, d=down, u=up) |

- `ret`: `self`.
- `notes`:
  - `rows*cols` must fit all children, else `ValueError`.
  - `buff` tuple is `(row spacing, col spacing)`.
- `errs`:
  - `ValueError: ...` — not enough cells for all submobjects.
- `see`: ../zh_CN/02-Mobject通用/02b-摆放位置-进阶.md

### `surround` / `replace`
```python
def surround(mobject: Mobject, dim_to_match: int = 0, stretch: bool = False,
             buff: float = 0.25) -> Self
def replace(mobject: Mobject, dim_to_match: int = 0, stretch: bool = False) -> Self
```
- `ret`: `self`.
- `args`:
  - `mobject: Mobject` — target to enclose / reference.
  - `dim_to_match: int = 0` — `0` width, `1` height, `2` depth.
  - `stretch: bool = False` — `False` uniform scale; `True` stretch width and height independently (distorts).
  - `buff: float = 0.25` — padding (`surround` only).
- `notes`:
  - `surround` gives same center, sized to target + padding; `replace` gives same size and center (no `buff`).
  - With `stretch=False`, a wide flat target yields a box much taller than the target.
- `see`: ../zh_CN/02-Mobject通用/02b-摆放位置-进阶.md

### `put_start_and_end_on`
```python
def put_start_and_end_on(start: Point3DLike, end: Point3DLike) -> Self
```
- `ret`: `self`.
- `args`:
  - `start: Point3DLike` / `end: Point3DLike` — target endpoints.
- `notes`:
  - Internally: scale by length ratio → rotate to direction → translate; pins start/end exactly.
  - For closed paths (`get_start()==get_end()`, e.g. `Circle`) only translates to `start` and prints `put_start_and_end_on has been called on a closed loop`.
- `see`: ../zh_CN/02-Mobject通用/02b-摆放位置-进阶.md

### `shift_onto_screen` / `is_off_screen`
```python
def shift_onto_screen(**kwargs: Any) -> Self
def is_off_screen() -> bool
```
- `ret`: `shift_onto_screen` → `self`; `is_off_screen` → `bool`.
- `args`:
  - `**kwargs: Any` — forwarded to internal `to_edge` (e.g. `buff=`).
- `notes`:
  - `shift_onto_screen` pulls only the out-of-frame edges back (already-visible sides untouched); not a centering guarantee — an oversized object may still be partly off-frame.
  - `is_off_screen` is `True` only when **fully** off-frame; any visible sliver → `False`.
  - Both use the frame (`config`), not the camera frame.
- `see`: ../zh_CN/02-Mobject通用/02b-摆放位置-进阶.md

### `space_out_submobjects`
```python
def space_out_submobjects(factor: float = 1.5, **kwargs: Any) -> Self
```
- `ret`: `self`.
- `args`:
  - `factor: float = 1.5` — spacing multiplier: `>1` spreads, `<1` tightens.
  - `**kwargs: Any` — forwarded to internal `scale` (e.g. `about_point=`).
- `notes`:
  - Implementation: group `scale(factor)` + each child `scale(1/factor)` → child positions scale, sizes cancel.
  - Relative layout scales along all axes.
- `see`: ../zh_CN/02-Mobject通用/02b-摆放位置-进阶.md

---

## 3. Measurement

### `width` / `height` / `depth` (properties, read/write)
```python
mob.width / mob.height / mob.depth -> float
```
- `ret`: read → `float` (bounding-box width/height/depth; flat objects have `depth == 0`).
- `args`:
  - assignment `float` — equivalent to `scale_to_fit_width(...)` etc.: **uniform** scale to the target size; the statement returns nothing.
- `notes`:
  - Assignment is uniform (wraps `scale_to_fit_*`); for width-only change without distortion use `stretch_to_fit_width` or `stretch`.
  - Reads are bounding-box sizes — `Text` includes line-gap space.
- `see`: ../zh_CN/02-Mobject通用/03-测量.md

### `get_center` / `get_top` / `get_bottom` / `get_left` / `get_right`
```python
def get_center() -> Point3D
def get_top() -> Point3D   # get_bottom / get_left / get_right same shape
```
- `ret`: `np.ndarray`, shape `(3,)` — bounding-box center and four edge midpoints.
- `notes`:
  - These are bounding-box edge midpoints, not contour points (an angled line's `get_left()` is the box's left midpoint; endpoints use `get_start`/`get_end`).
  - Pair with `next_to(..., UP, buff=0)` for a flush fit.
- `see`: ../zh_CN/02-Mobject通用/03-测量.md

### `get_x` / `get_y` / `get_z` / `get_coord` / `get_corner` / `get_edge_center` / `get_critical_point`
```python
def get_x(direction: Vector3DLike = ORIGIN) -> float   # get_y / get_z same shape
def get_coord(dim: int, direction: Vector3DLike = ORIGIN) -> float
def get_corner(direction: Vector3DLike) -> Point3D
def get_edge_center(direction: Vector3DLike) -> Point3D
def get_critical_point(direction: Vector3DLike) -> Point3D
```
- `ret`: `get_x`/`get_y`/`get_z`/`get_coord` → `float`; the last three → `np.ndarray`.
- `args`:
  - `direction: Vector3DLike` — component **signs** select the critical point (zero component → middle value), e.g. `UR`=top-right, `DOWN`=bottom-edge midpoint. Required for `get_corner` etc.
  - `dim: int` — only `0`=x, `1`=y, `2`=z (`get_coord` only).
- `notes`:
  - `get_corner` / `get_edge_center` are semantic aliases of `get_critical_point` (same implementation).
  - `direction` uses sign only; `UR` == `UP + RIGHT`.
  - `get_z` is always `0` for flat objects.
- `see`: ../zh_CN/02-Mobject通用/03-测量.md

### `length_over_dim` / `get_all_points`
```python
def length_over_dim(dim: int) -> float
def get_all_points() -> Point3D_Array
```
- `ret`: `length_over_dim` → length along that dim (basis of `width`/`height`); empty object → `0`. `get_all_points` → array shape `(N, 3)` — self + **all** descendants' vertices concatenated depth-first (may contain duplicates).
- `args`:
  - `dim: int` — only `0` width, `1` height, `2` depth.
- `notes`:
  - Control points ≠ contour points; for a position on a curve use `point_from_proportion`.
- `see`: ../zh_CN/02-Mobject通用/03-测量.md

### `get_center_of_mass` / `get_midpoint` / `get_boundary_point` / `get_zenith` / `get_nadir` / `get_z_index_reference_point` / `get_points_defining_boundary` / `get_merged_array` / `get_extremum_along_dim` / `reduce_across_dimension`
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
| arg | type | default | meaning |
| --- | --- | --- | --- |
| `direction` | vector | — | `get_boundary_point`: farthest vertex along direction |
| `array_attr` | `str` | — | attribute name (e.g. `"points"`) to concatenate over the family |
| `points` | point array \| `None` | `None` | point set; `None` uses own points |
| `dim` | `int` | `0` | dimension |
| `key` | `int` | `0` | `1` max, `-1` min, `0` median |
| `reduce_func` | callable | — | reduction, e.g. `max` |

- `ret`: first ones → `np.ndarray` (`get_midpoint` == `point_from_proportion(0.5)`); `get_points_defining_boundary` base default == `get_all_points`, but `VMobject` returns only contour samples (circle: 16 vs 32); `get_extremum_along_dim`/`reduce_across_dimension` → `float` (`None` for empty).
- `notes`:
  - `get_center_of_mass` (vertex mean) vs `get_midpoint` (path midpoint) differ for a circle (center vs circumference).
  - `get_zenith`/`get_nadir` meaningful only for 3D.
  - Empty objects return `None` from the two stat functions — guard before arithmetic.
  - Rarely called directly (`get_top`/`length_over_dim` already wrap them).
- `see`: ../zh_CN/02-Mobject通用/03-测量.md

---

## 4. Scale / rotate / transform

### `scale`
```python
def scale(scale_factor: float, *, about_point: Point3DLike | None = None,
          about_edge: Vector3DLike | None = None) -> Self
```
- `ret`: `self`.
- `args`:
  - `scale_factor: float` — multiplier: `0<|a|<1` shrink, `>1` grow, negative flips.
  - `about_point: Point3DLike | None = None` — pivot; `None` = own center. **Keyword-only.**
  - `about_edge: Vector3DLike | None = None` — pivot edge (e.g. `DOWN` keeps bottom fixed). **Keyword-only.**
- `notes`:
  - `about_point` and `about_edge` must be passed by keyword; `about_point` wins if both given.
  - Pure geometry: stroke width does **not** scale.
- `see`: ../zh_CN/02-Mobject通用/04-缩放旋转与变形.md

### `rotate` / `rotate_about_origin`
```python
def rotate(angle: float, axis: Vector3DLike = OUT, *,
           about_point: Point3DLike | None = None,
           about_edge: Vector3DLike | None = None,
           **kwargs: Any) -> Self
def rotate_about_origin(angle: float, axis: Vector3DLike = OUT) -> Self
```
| arg | type | default | meaning |
| --- | --- | --- | --- |
| `angle` | `float` | — | radians (`PI/2` == `90 * DEGREES`) |
| `axis` | vector | `OUT` | rotation axis; default for in-plane 2D; change only for 3D |
| `about_point` | point \| `None` | `None` | pivot; `None` = own center (keyword-only) |
| `about_edge` | vector \| `None` | `None` | pivot edge (keyword-only) |
| `**kwargs` | `Any` | — | base `Mobject.rotate` ignores these; real classes (`Square`/`Circle`) use `VMobject.rotate` which has **no `**kwargs`** → extra kwarg raises `TypeError` |

- `ret`: `self`.
- `notes`:
  - `rotate_about_origin(angle, axis)` == `rotate(angle, axis, about_point=ORIGIN)` (rotate about world origin, not own center).
  - `.animate.rotate(...)` interpolates point-to-point to the rotated state (mid frames collapse), it does **not** continuously spin; use `Rotate`/`Rotating` animations for that.
  - `axis` is a 3D parameter; in 2D changing it usually has no visible effect (except `RIGHT` by 180°, i.e. a vertical flip).
- `errs`:
  - `TypeError: ...` — passing an extra kwarg to a `VMobject`-based `.rotate`.
- `see`: ../zh_CN/02-Mobject通用/04-缩放旋转与变形.md

### `flip`
```python
def flip(axis: Vector3DLike = UP, *, about_point: Point3DLike | None = None,
         about_edge: Vector3DLike | None = None) -> Self
```
- `ret`: `self`.
- `args`:
  - `axis: Vector3DLike = UP` — mirror axis (rotate 180° about it). `UP` (vertical axis) = **left-right** mirror; `RIGHT` (horizontal axis) = **up-down** mirror (counter-intuitive).
  - `about_point` / `about_edge` — keyword-only pivot; `None` = own center.
- `notes`: implementation is `rotate(PI, axis, ...)`; `axis` is the rotation axis, not the flipped edge.
- `see`: ../zh_CN/02-Mobject通用/04-缩放旋转与变形.md

### `stretch` / `stretch_about_point`
```python
def stretch(factor: float, dim: int, *, about_point: Point3DLike | None = None,
            about_edge: Vector3DLike | None = None) -> Self
def stretch_about_point(factor: float, dim: int, point: Point3DLike) -> Self
```
- `ret`: `self`.
- `args`:
  - `factor: float` — multiplier along that dim (does not preserve aspect).
  - `dim: int` — only `0`=x, `1`=y, `2`=z.
  - `about_point` / `about_edge` — keyword-only pivot; `None` = own center.
  - `point: Point3DLike` — (`stretch_about_point`) fixed point, positional form.
- `notes`:
  - `stretch_about_point(factor, dim, point)` == `stretch(factor, dim, about_point=point)`.
  - `stretch` does not preserve aspect; `dim` is a world axis (rotated objects distort).
- `see`: ../zh_CN/02-Mobject通用/04-缩放旋转与变形.md

### `rescale_to_fit`
```python
def rescale_to_fit(length: float, dim: int, stretch: bool = False, **kwargs: Any) -> Self
```
- `ret`: `self`.
- `args`:
  - `length: float` — target length.
  - `dim: int` — only `0` width, `1` height, `2` depth.
  - `stretch: bool = False` — `False` uniform scale to length; `True` stretches only this dim (distorts).
  - `**kwargs: Any` — forwarded to internal `scale`/`stretch` (e.g. `about_point=`).
- `notes`: general entry for "make one dimension length L"; the six `scale_to_fit_*`/`stretch_to_fit_*` methods are sugar over it.
- `see`: ../zh_CN/02-Mobject通用/04b-缩放旋转与变形-进阶.md

### `scale_to_fit_*` / `stretch_to_fit_*` (six)
```python
def scale_to_fit_width(width: float, **kwargs: Any) -> Self    # stretch_to_fit_width(width, ...)
def scale_to_fit_height(height: float, ...) -> Self            # stretch_to_fit_height(height, ...)
def scale_to_fit_depth(depth: float, ...) -> Self              # stretch_to_fit_depth(depth, ...)
```
- `ret`: `self`.
- `args`:
  - `width` / `height` / `depth: float` — target size.
  - `**kwargs: Any` — passthrough (e.g. `about_point=`).
- `notes`:
  - `scale_*` preserves aspect (`rescale_to_fit(..., stretch=False)`); `stretch_*` distorts (`stretch=True`).
  - `*_depth` is a safe no-op for 2D objects (`length_over_dim(2) == 0`, no division by zero).
- `see`: ../zh_CN/02-Mobject通用/04b-缩放旋转与变形-进阶.md

### `pose_at_angle`
```python
def pose_at_angle(**kwargs: Any) -> Self
```
- `ret`: `self`.
- `args`:
  - `**kwargs: Any` — forwarded to `rotate` (e.g. `about_point=`).
- `notes`: equivalent to `rotate(TAU / 14, RIGHT + UP, **kwargs)` (~25.7° about the diagonal axis); intended for a natural display angle of 3D objects.
- `see`: ../zh_CN/02-Mobject通用/04b-缩放旋转与变形-进阶.md

### `apply_function` / `apply_matrix` / `apply_complex_function` / `apply_function_to_position` / `apply_function_to_submobject_positions`
```python
def apply_function(function: MappingFunction, *, about_point: Point3DLike | None = None,
                   about_edge: Vector3DLike | None = None) -> Self
def apply_matrix(matrix: MatrixMN, *, about_point=None, about_edge=None) -> Self
def apply_complex_function(function: Callable[[complex], complex], *,
                           about_point=None, about_edge=None) -> Self
def apply_function_to_position(function: MappingFunction) -> Self
def apply_function_to_submobject_positions(function: MappingFunction) -> Self
```
- `ret`: `self`.
- `args`:
  - `function` — point-to-point map `f(point) -> point` (`apply_matrix` takes a matrix; `apply_complex_function` treats `(x, y)` as a complex number).
  - `about_point: Point3DLike | None = None` — transform pivot; default origin. **Keyword-only.**
  - `about_edge: Vector3DLike | None = None` — pivot edge. **Keyword-only.**
- `notes`:
  - First three act on **every vertex** (true deformation); the two "position" versions move only the **center** (`apply_function_to_position` = own center, `apply_function_to_submobject_positions` = each child's center), leaving shape unchanged.
  - Upstream ManimCE 0.21 bug: `VMobject.apply_function` drops `about_point`/`about_edge` (always origin) for `apply_function`/`apply_complex_function`. **RTM: fixed** — the bundled `vectorized_mobject.py` forwards the pivot, and an idempotent runtime patch in `animations/homotopy.py` also repairs the case where external `manim` was imported first. `apply_matrix` and `apply_points_function_about_point` are unaffected upstream.
- `see`: ../zh_CN/02-Mobject通用/04b-缩放旋转与变形-进阶.md

### `apply_points_function_about_point`
```python
def apply_points_function_about_point(func: MultiMappingFunction,
                                      about_point: Point3DLike | None = None,
                                      about_edge: Vector3DLike | None = None) -> Self
```
- `ret`: `self`.
- `args`:
  - `func: MultiMappingFunction` — batch map on a point array `f(points) -> points`, `points` shape `(N, 3)`.
  - `about_point: Point3DLike | None = None` — pivot.
  - `about_edge: Vector3DLike | None = None` — pivot edge.
- `notes`:
  - Internally: translate to pivot → apply `func` → translate back; common base of `scale`/`rotate`/`stretch`.
  - `func` must return the same `(N, 3)` shape; changing point count corrupts rendering.
  - Difference vs `apply_function`: batch whole array vs per-point callback.
- `see`: ../zh_CN/02-Mobject通用/04b-缩放旋转与变形-进阶.md

### `repeat` / `reverse_points`
```python
def repeat(count: int) -> Self
def reverse_points() -> Self
```
- `ret`: `self`.
- `args`:
  - `count: int` — (`repeat`) number of times to repeat the vertex sequence.
- `notes`:
  - `repeat(n)` duplicates the vertex sequence n times — appearance unchanged, point count doubles (can smooth some transitions).
  - `reverse_points()` swaps path ends — appearance usually unchanged, but `get_start`/`point_from_proportion` reverse.
  - Both act on the whole family. After `repeat`, `point_from_proportion` proportions change.
- `see`: ../zh_CN/02-Mobject通用/04b-缩放旋转与变形-进阶.md

---

## 5. Style & color

### `set_color`
```python
def set_color(color: ParsableManimColor = PURE_YELLOW, alpha: Any = None,
              family: bool = True) -> Self
```
- `ret`: `self`.
- `args`:
  - `color: ParsableManimColor = PURE_YELLOW` — accepts `"red"`, `"#ff0000"`, `RED`, `ManimColor("#83c167")`.
  - `alpha: Any = None` — exists only on the `Mobject` base signature; `VMobject.set_color` has **no** such parameter.
  - `family: bool = True` — `False` sets only self, no recursion.
- `notes`:
  - Default recurses into all children; `color=` also updates `self.color` (used later by `to_original_color`).
  - `family=False` on a container is effectively a no-op (containers aren't drawn).
  - To change opacity use `set_fill(opacity=...)` / `fade_to`.
- `errs`:
  - `TypeError: ...` — passing `alpha=` to a vector object's `set_color` (measured on 0.21).
- `see`: ../zh_CN/02-Mobject通用/05-样式与颜色.md

### `set_color_by_gradient` / `set_submobject_colors_by_gradient` / `set_colors_by_radial_gradient` / `set_submobject_colors_by_radial_gradient`
```python
def set_color_by_gradient(*colors: ParsableManimColor) -> Self
def set_submobject_colors_by_gradient(*colors: ParsableManimColor) -> Self
def set_colors_by_radial_gradient(center: Point3DLike | None = None, radius: float = 1,
                                  inner_color: ParsableManimColor = WHITE,
                                  outer_color: ParsableManimColor = BLACK) -> Self
def set_submobject_colors_by_radial_gradient(center=None, radius=1,
                                             inner_color=WHITE, outer_color=BLACK) -> Self
```
| arg | type | default | meaning |
| --- | --- | --- | --- |
| `*colors` | color | — | linear-gradient endpoint colors; ≥1, usually 2–3 |
| `center` | point \| `None` | `None` | gradient center; `None` = own center (radial only) |
| `radius` | `float` | `1` | distance to reach outer color (radial only) |
| `inner_color` / `outer_color` | color | `WHITE` / `BLACK` | radial inner/outer colors |

- `ret`: `self`.
- `notes`:
  - Distributes solid colors **per vertex-owning descendant**, not a true in-shape gradient — a single-child group shows one flat color.
  - `set_color_by_gradient` internally calls `set_submobject_colors_by_gradient`; same for the radial pair.
- `see`: ../zh_CN/02-Mobject通用/05-样式与颜色.md

### `fade_to` / `fade`
```python
def fade_to(color: ParsableManimColor, alpha: float, family: bool = True) -> Self
def fade(darkness: float = 0.5, family: bool = True) -> Self
```
- `ret`: `self`.
- `args`:
  - `color: ParsableManimColor` — target color (`fade_to` only).
  - `alpha: float` — mix ratio 0–1 (`fade_to` only).
  - `darkness: float = 0.5` — dim/fade amount (`fade` only).
  - `family: bool = True` — recurse into children.
- `notes`:
  - `fade_to` blends toward the target by `alpha` (`0.7` = 70% new color).
  - `fade`'s logic lives in `VMobject.fade` and changes **opacity, not color**; effective on vector objects, no-op on a bare `Mobject`. `get_color` stays unchanged after `fade`.
  - For a fade-out animation use `FadeOut`.
- `see`: ../zh_CN/02-Mobject通用/05-样式与颜色.md

### `get_color` / `match_color` / `to_original_color`
```python
def get_color() -> ManimColor
def match_color(mobject: Mobject) -> Self
def to_original_color() -> Self
```
- `ret`: `get_color` → `ManimColor`; the other two → `self`.
- `args`:
  - `mobject: Mobject` — reference (`match_color` only).
- `notes`:
  - `match_color` sets both the colors and `self.color` to the reference's (the old `self.color` is overwritten).
  - `to_original_color` re-pushes `self.color` down the family; real use is clearing per-submobject colors (e.g. recolored `Text` glyphs). After `match_color`, it cannot restore the old color (overwritten) — `save_state()` first if needed.
- `see`: ../zh_CN/02-Mobject通用/05-样式与颜色.md

### `set_z_index` / `set_z_index_by_z_Point3D`
```python
def set_z_index(z_index_value: float, family: bool = True) -> Self
def set_z_index_by_z_Point3D() -> Self
```
- `ret`: `self`.
- `args`:
  - `z_index_value: float` — any number, larger = on top.
  - `family: bool = True` — also set all children.
- `notes`:
  - Paint order is decided by `z_index`, independent of `add` order (only equal `z_index` falls back to add order).
  - `set_z_index_by_z_Point3D` sets `z_index` to the center's z coordinate; meaningful only in 3D (2D z is 0).
  - Instant change, no transition.
- `see`: ../zh_CN/02-Mobject通用/05-样式与颜色.md

### `add_background_rectangle` / `add_background_rectangle_to_submobjects` / `add_background_rectangle_to_family_members_with_points`
```python
def add_background_rectangle(color: ParsableManimColor | None = None,
                             opacity: float = 0.75, **kwargs: Any) -> Self
def add_background_rectangle_to_submobjects(**kwargs: Any) -> Self
def add_background_rectangle_to_family_members_with_points(**kwargs: Any) -> Self
```
- `ret`: `self`.
- `args`:
  - `color: ParsableManimColor | None = None` — background color.
  - `opacity: float = 0.75` — background opacity.
  - `**kwargs: Any` — forwarded to `BackgroundRectangle` (the two variants take this set directly).
- `notes`:
  - The backing rectangle is added as a submobject (drawn below), following the object through `shift`/`scale`.
  - Three variants: self / each direct child / each family member with points.
- `see`: ../zh_CN/02-Mobject通用/05-样式与颜色.md

---

## 6. Copy / derive / state

### `copy`
```python
def copy() -> Self
```
- `ret`: new independent object (deep copy incl. children and style). Not added to the scene automatically.
- `notes`:
  - Deep copy; updaters (if any) are copied too — `clear_updaters()` before reuse.
  - Later changes to the original do not affect the copy.
  - For "two identical, synchronized" use a reference / `VGroup` instead.
- `see`: ../zh_CN/02-Mobject通用/06-复制派生与状态.md

### `become`
```python
def become(mobject: Mobject, match_height: bool = False, match_width: bool = False,
           match_depth: bool = False, match_center: bool = False,
           stretch: bool = False) -> Self
```
- `ret`: `self`.
- `args`:
  - `mobject: Mobject` — target form.
  - `match_height` / `match_width` / `match_depth: bool = False` — keep **own** h/w/d (uniformly rescale the target).
  - `match_center: bool = False` — keep own center (otherwise position is taken from target).
  - `stretch: bool = False` — ignore the three `match_*` and stretch the target per-axis to own h/w/d (distorts).
- `notes`:
  - Instant reshape on direct call; use `.animate.become(...)` or `Transform` for a transition.
  - `stretch=True` overrides all three `match_*`.
- `see`: ../zh_CN/02-Mobject通用/06-复制派生与状态.md

### `save_state` / `restore`
```python
def save_state() -> Self
def restore() -> Self
```
- `ret`: `self`.
- `notes`:
  - `save_state` stores position/size/color/structure into `self.saved_state`; `restore` is `become(saved_state)`.
  - Reference-style snapshot (`become` semantics) — structural changes restore too.
  - Calling `restore` without a prior `save_state` raises; repeated `save_state` overwrites.
- `see`: ../zh_CN/02-Mobject通用/06-复制派生与状态.md

### `generate_target`
```python
def generate_target(use_deepcopy: bool = False) -> Self
```
- `ret`: the `self.target` snapshot itself (**not** self).
- `args`:
  - `use_deepcopy: bool = False` — `True` uses `deepcopy`; default uses `copy()`.
- `notes`:
  - Returns `self.target`; do not chain-assign it back onto the object.
  - Pair with `MoveToTarget`; the target's position/size/color/children can all be edited.
- `see`: ../zh_CN/02-Mobject通用/06-复制派生与状态.md

### `interpolate`
```python
def interpolate(mobject1: Mobject, mobject2: Mobject, alpha: float,
                path_func: PathFuncType = straight_path()) -> Self
```
- `ret`: `self`.
- `args`:
  - `mobject1` / `mobject2: Mobject` — start / end state.
  - `alpha: float` — 0 = start, 1 = end.
  - `path_func: PathFuncType = straight_path()` — interpolation path (`arc_path` family for arcs).
- `notes`:
  - Underlies `Transform`; makes self the **instant** interpolated state at `alpha`.
  - All three must have equal point counts (usually build states via `copy`); else error — `align_points` first for cross-shape.
  - `alpha` may exceed 0–1 (extrapolation), discouraged.
- `see`: ../zh_CN/02-Mobject通用/06-复制派生与状态.md

### `match_dim_size` / `match_width` / `match_height` / `match_depth`
```python
def match_dim_size(mobject: Mobject, dim: int, **kwargs: Any) -> Self
def match_width(mobject: Mobject, **kwargs: Any) -> Self
def match_height(mobject: Mobject, **kwargs: Any) -> Self
def match_depth(mobject: Mobject, **kwargs: Any) -> Self
```
- `ret`: `self`.
- `args`:
  - `mobject: Mobject` — reference.
  - `dim: int` — `match_dim_size` only: `0` width, `1` height, `2` depth.
  - `**kwargs: Any` — forwarded to `rescale_to_fit` (e.g. `stretch=True`).
- `notes`:
  - Default uniform scale to match; `stretch=True` changes only that dim.
  - `match_width` == `rescale_to_fit(ref.width, 0)`; `match_depth` is a safe no-op for 2D.
- `see`: ../zh_CN/02-Mobject通用/06-复制派生与状态.md

### `match_coord` / `match_x` / `match_y` / `match_z` / `match_points` / `align_points`
```python
def match_coord(mobject: Mobject, dim: int, direction: Vector3DLike = ORIGIN) -> Self
def match_x(mobject: Mobject, direction: Vector3DLike = ORIGIN) -> Self
def match_y(mobject: Mobject, direction: Vector3DLike = ORIGIN) -> Self
def match_z(mobject: Mobject, direction: Vector3DLike = ORIGIN) -> Self
def match_points(mobject: Mobject, copy_submobjects: bool = True) -> Self
def align_points(mobject: Mobject) -> Self
```
- `ret`: `self`.
- `args`:
  - `mobject: Mobject` — reference.
  - `dim: int` — `match_coord` only: `0`/`1`/`2`.
  - `direction: Vector3DLike = ORIGIN` — which own critical point aligns (`DOWN` = bottom edge).
  - `copy_submobjects: bool = True` — retained signature parameter.
- `notes`:
  - `match_coord` sets one dim's critical-point coordinate to the reference's (`match_x` etc. are sugar).
  - `match_points` copies the reference's **vertices** (shape and size become the reference's).
  - `align_points` only equalizes vertex **count** (precondition for `Transform` interpolation), not visible appearance.
- `see`: ../zh_CN/02-Mobject通用/06-复制派生与状态.md

---

## 7. `.animate` syntax

### `.animate` (property)
```python
def animate(**play_kwargs) -> _AnimationBuilder
```
- `ret`: `_AnimationBuilder`, turned into an animation by `Scene.play`.
- `args`:
  - `**play_kwargs: Any` — kwargs right after `.animate(...)` are **not** `Scene.play` parameters; they are `setattr` on the built animation (`run_time=`, `rate_func=`, `lag_ratio=`, ...). Must sit **between `.animate` and the method call**.
- `notes`:
  - `mob.set_fill(RED)` is instant; `mob.animate.set_fill(RED)` plays a transition. Methods chain into **one** animation.
  - One object may appear only once per `play`: write `m.animate.shift(RIGHT).rotate(PI)`, not two animations.
  - `.animate` is point-to-point linear interpolation, not a path animation; use `MoveAlongPath`/`Rotate`/`Rotating` for paths/continuous spin.
  - For continuous `ValueTracker`-driven change use an updater, not `.animate`.
  - Chained methods run in order; `run_time` is the total for the whole chain.
  - `animate.shift(2)` (method arg) and `animate(run_time=2)` (play kwarg) are completely different.
  - `lag_ratio=0.3` on an object with no submobjects is ineffective; RTM now emits an explicit `UserWarning` instead of failing silently. `RTM: explicit UserWarning`.
- `eg`:
  ```python
  win.play(sq.animate.scale(1.5).rotate(PI / 6), run_time=0.6)
  win.play(sq.animate(run_time=0.8, rate_func=there_and_back).shift(DOWN), run_time=0.8)
  ```
- `see`: ../zh_CN/02-Mobject通用/07-animate语法.md

### `override_animate` (module-level decorator)
```python
def override_animate(method: types.MethodType) -> Callable[[types.MethodType], types.MethodType]
```
- `ret`: decorator.
- `args`:
  - `method: types.MethodType` — the unbound method being overridden (defined on a `Mobject` subclass).
- `notes`:
  - The decorated method returns an `Animation`; `.animate.method(...)` plays it instead of "execute then interpolate".
  - Decorated method signature = original args + `anim_args` (the `.animate(...)` play kwargs); must return an `Animation`.
  - The overridden method **cannot** be chained with other methods in the same `.animate`.
  - Direct calls always use the original implementation.
- `see`: ../zh_CN/02-Mobject通用/07-animate语法.md

### `add_animation_override` / `animation_override_for` (classmethods)
```python
def add_animation_override(animation_class: type[Animation],
                           override_func: FunctionOverride) -> None
def animation_override_for(animation_class: type[Animation]) -> FunctionOverride | None
```
- `ret`: `add_animation_override` → `None`; `animation_override_for` → the registered function or `None`.
- `args`:
  - `animation_class: type[Animation]` — class to replace, e.g. `FadeIn`.
  - `override_func: FunctionOverride` — callable receiving the constructor args, returning the replacement animation.
- `notes`:
  - Programmatic form of `@override_animate`, keyed by animation class (not method).
  - Applies to the current class only (not inherited by subclasses).
  - Registering the same animation class twice raises `MultiAnimationOverrideException` (delete the old one first).
- `errs`:
  - `MultiAnimationOverrideException: ...` — duplicate registration.
- `see`: ../zh_CN/02-Mobject通用/07-animate语法.md

---

## 8. Updaters (Mobject methods)

### `add_updater`
```python
def add_updater(update_function: _Updater, index: int | None = None,
                call_updater: bool = False) -> Self
```
- `ret`: `self`.
- `args`:
  - `update_function: _Updater` — `f(mob)` non-time-based (once per frame); `f(mob, dt)` time-based (`dt` = seconds since last frame).
  - `index: int | None = None` — insertion position; `None` appends (sets execution order).
  - `call_updater: bool = False` — `True` runs once immediately on mount (`dt=0`).
- `notes`:
  - An object with updaters **must be `self.add(...)`-ed** to be driven (`ValueTracker` too).
  - Updaters keep running during animations.
  - Non-time-based updaters must re-read state each call — don't cache values in the args.
- `eg`:
  ```python
  sq.add_updater(lambda m, dt: m.rotate(dt * 90 * DEGREES))
  lbl.add_updater(pos, index=0, call_updater=True)
  ```
- `see`: ../zh_CN/02-Mobject通用/08-更新器.md

### `remove_updater` / `clear_updaters`
```python
def remove_updater(update_function: _Updater) -> Self
def clear_updaters(recursive: bool = True) -> Self
```
- `ret`: `self`.
- `args`:
  - `update_function: _Updater` — the **same function object** (store it in a variable).
  - `recursive: bool = True` — (`clear_updaters`) also clear all children.
- `notes`:
  - `remove_updater` removes **one** by reference; anonymous `lambda`s can't be re-specified, so keep a variable.
  - `clear_updaters` clears everything (duplicated mounts included).
- `see`: ../zh_CN/02-Mobject通用/08-更新器.md

### `suspend_updating` / `resume_updating` / `update`
```python
def suspend_updating(recursive: bool = True) -> Self
def resume_updating(recursive: bool = True) -> Self
def update(dt: float = 0, recursive: bool = True) -> Self
```
- `ret`: `self`.
- `args`:
  - `recursive: bool = True` — apply to children too.
  - `dt: float = 0` — (`update` only) seconds passed to time-based updaters.
- `notes`:
  - `suspend_updating` pauses execution but keeps functions in the list; `resume_updating` immediately runs once at `dt=0`.
  - `update(dt)` manually triggers once — normally called by the render loop; only needed outside a `Scene` (interactive scripts, tests). Skipped while suspended.
  - Typical use: `suspend_updating` during an animation to avoid updater/interpolation conflict, then `resume_updating`.
- `see`: ../zh_CN/02-Mobject通用/08-更新器.md

### `always` (property)
```python
def always.method(*args, **kwargs) -> _UpdaterBuilder
```
- `ret`: `_UpdaterBuilder` (takes effect on mount).
- `args`:
  - `*args`, `**kwargs: Any` — forwarded to the target method.
- `notes`:
  - `t.always.next_to(sq, UP)` == `t.add_updater(lambda m: m.next_to(sq, UP), call_updater=True)`; each chained method is a separate updater.
  - Arguments are evaluated **once at mount**; don't call read-only methods like `always.get_value(...)` — use `add_updater` for per-frame recomputed values.
  - Distinct from the module-level `always` function (see §8b).
- `see`: ../zh_CN/02-Mobject通用/08-更新器.md

### `get_updaters` / `get_time_based_updaters` / `has_time_based_updater` / `match_updaters`
```python
def get_updaters() -> list[_Updater]
def get_time_based_updaters() -> list[_TimeBasedUpdater]
def has_time_based_updater() -> bool
def match_updaters(mobject: Mobject) -> Self
```
- `ret`: first three → list / `bool`; `match_updaters` → `self`.
- `args`:
  - `mobject: Mobject` — (`match_updaters`) copy its updater list (own list only).
- `notes`:
  - `match_updaters` does not recurse into children; copied entries are function references (each object receives its own `mob`).
  - Use these three for debugging "is the updater attached?".
- `see`: ../zh_CN/02-Mobject通用/08-更新器.md

---

## 8b. Updater tool functions (module level)

Import from `real_time_manim` (e.g. `from real_time_manim import always_redraw`).

### `always_redraw`
```python
def always_redraw(func: Callable[[], M]) -> M
```
- `ret`: a `Mobject` with the updater attached (the first `func()` result); just `self.add(...)` it.
- `args`:
  - `func: Callable[[], M]` — zero-arg factory returning a new `Mobject`.
- `notes`:
  - Standard pattern for `ValueTracker`-driven graphics: each frame re-runs the factory and `become`s its result.
  - The factory must return a **new** object and runs every frame — avoid heavy work inside (e.g. building `Text`).
  - The returned object can also be used in `play` animations (e.g. `TransformFromCopy`).
- `see`: ../zh_CN/02-Mobject通用/08b-更新器工具函数.md

### `always` / `f_always` (module-level functions)
```python
def always(method: Callable, *args, **kwargs) -> Mobject
def f_always(method: Callable[[M], None], *arg_generators, **kwargs) -> M
```
- `ret`: the `Mobject` owning the method.
- `args`:
  - `method: Callable` — must be a method on a `Mobject` instance, else assertion fails.
  - `*args: Any` — fixed args, evaluated once at mount (`always` only).
  - `*arg_generators: Callable` — zero-arg generators called each frame, their results passed to the method (`f_always` only).
- `notes`:
  - Same name as `Mobject.always` property but a different implementation; nearly identical behavior.
  - `always` args are evaluated once; `f_always` args each frame — the only difference.
  - `method` must be a bound method (`tag.next_to`, not `Tag.next_to`); wrong input raises `AssertionError` from `assert_is_mobject_method`.
- `errs`:
  - `AssertionError: ...` — non-bound / non-`Mobject` method passed.
- `see`: ../zh_CN/02-Mobject通用/08b-更新器工具函数.md

### `always_shift` / `always_rotate`
```python
def always_shift(mobject: M, direction: Vector3DLike = RIGHT, rate: float = 0.1) -> M
def always_rotate(mobject: M, rate: float = 20 * DEGREES, **kwargs) -> M
```
- `ret`: the object.
- `args`:
  - `mobject: M` — object to move / rotate.
  - `direction: Vector3DLike = RIGHT` — translation direction (normalized; magnitude irrelevant).
  - `rate: float = 0.1` / `20 * DEGREES` — distance per second / radians per second.
  - `**kwargs: Any` — (`always_rotate`) forwarded to `Mobject.rotate` (e.g. `about_point=`).
- `notes`:
  - Each attaches a time-based updater; the object moves/rotates "unaware", without `play`, advancing with scene time. Stop with `clear_updaters()`.
  - Multiple `always_*` stack (separate updaters).
  - `always_rotate` spins about own center by default; use `about_point=` otherwise.
- `see`: ../zh_CN/02-Mobject通用/08b-更新器工具函数.md

### `assert_is_mobject_method`
```python
def assert_is_mobject_method(method) -> None
```
- `ret`: `None`.
- `notes`: input-check helper used internally by the `always*` functions; confirms the argument is a bound method on a `Mobject`.
- `see`: ../zh_CN/02-Mobject通用/08b-更新器工具函数.md

### `turn_animation_into_updater` / `cycle_animation`
```python
def turn_animation_into_updater(animation: Animation, cycle: bool = False,
                                delay: float = 0, **kwargs) -> Mobject
def cycle_animation(animation: Animation, **kwargs) -> Mobject
```
- `ret`: the `Mobject` of the animation.
- `args`:
  - `animation: Animation` — the animation to convert (**do not** `play` it).
  - `cycle: bool = False` — loop forever (`cycle_animation` is `cycle=True`).
  - `delay: float = 0` — seconds before start.
- `notes`:
  - Runs with scene time, no `play`; the updater auto-removes when finished (`cycle=True` runs forever — stop with `clear_updaters()`).
  - `delay=` can stagger several animation-updaters.
- `see`: ../zh_CN/02-Mobject通用/08b-更新器工具函数.md

---

## 9. Updater-driven animations (`Scene.play`)

Import from `real_time_manim` (e.g. `from real_time_manim import UpdateFromFunc`).

### `UpdateFromFunc`
```python
def UpdateFromFunc(mobject: Mobject, update_function: Callable[[Mobject], Any],
                   suspend_mobject_updating: bool = False, **kwargs: Any) -> Animation
```
- `ret`: `Animation`.
- `args`:
  - `mobject: Mobject` — driven object (appears in scene during the animation).
  - `update_function: Callable[[Mobject], Any]` — `f(mob)` called every frame.
  - `suspend_mobject_updating: bool = False` — suspend the object's existing updaters during the animation.
  - `**kwargs: Any` — forwarded to `Animation` (`run_time=`, `rate_func=`, ...).
- `notes`:
  - Calls `update_function(mobject)` repeatedly for the whole `play` duration; stops at `run_time` end (unlike a permanent `add_updater`).
  - The driven object is auto-added to the scene (no prior `add` needed).
- `see`: ../zh_CN/02-Mobject通用/09-更新器动画.md

### `UpdateFromAlphaFunc`
```python
def UpdateFromAlphaFunc(mobject: Mobject, update_function: Callable[[Mobject, Any], Any],
                        suspend_mobject_updating: bool = False, **kwargs: Any) -> Animation
```
- `ret`: `Animation`.
- `args`:
  - `mobject: Mobject` — driven object.
  - `update_function: Callable[[Mobject, Any], Any]` — `func(mobject, alpha)`, `alpha` is the `rate_func`-processed 0→1 progress.
  - `suspend_mobject_updating: bool = False` — suspend existing updaters during the animation.
  - `**kwargs: Any` — forwarded to `Animation`.
- `notes`:
  - Subclass of `UpdateFromFunc` for deterministic interpolation (color gradients, position maps).
  - `alpha` is already `rate_func`-processed; pass `rate_func=linear` for uniform speed.
  - The callback must be a pure function of `alpha` (else repeated frames jump).
  - For cumulative per-frame transforms (e.g. 5°/frame) use `UpdateFromFunc` + `dt` or an updater.
- `see`: ../zh_CN/02-Mobject通用/09-更新器动画.md

### `MaintainPositionRelativeTo`
```python
def MaintainPositionRelativeTo(mobject: Mobject, tracked_mobject: Mobject,
                               **kwargs: Any) -> Animation
```
- `ret`: `Animation`.
- `args`:
  - `mobject: Mobject` — object keeping its relative position.
  - `tracked_mobject: Mobject` — tracked reference.
  - `**kwargs: Any` — forwarded to `Animation`.
- `notes`:
  - Keeps `mobject`'s offset to `tracked_mobject` during the animation (offset recorded at animation start — position first, then play).
  - Binding releases when the animation ends (not permanent); for permanent tracking use `add_updater` / `always`.
- `see`: ../zh_CN/02-Mobject通用/09-更新器动画.md

---

## 10. ValueTracker

### `ValueTracker`
```python
def ValueTracker(value: float = 0, **kwargs: Any) -> None
```
- `ret`: new `ValueTracker`. Invisible value container; the value is encoded in vertex coordinates, so it can be animated with `.animate` and read by updaters.
- `args`:
  - `value: float = 0` — initial value.
  - `**kwargs: Any` — forwarded to `Mobject.__init__`.
- `notes`:
  - When driven by an updater it **must be `self.add(tracker)`**; for animated changes use `win.play(tracker.animate.set_value(...))`; direct `tracker += 1.5` changes instantly.
  - Not displayed; render the number with `DecimalNumber` + updater or `always_redraw`.
- `see`: ../zh_CN/02-Mobject通用/10-ValueTracker.md

### `get_value` / `set_value` / `increment_value`
```python
def get_value() -> float
def set_value(value: float) -> Self
def increment_value(d_value: float) -> Self
```
- `ret`: `get_value` → `float`; the other two → `self`.
- `args`:
  - `value: float` — target (`set_value` only).
  - `d_value: float` — delta, may be negative (`increment_value` only).
- `notes`:
  - `tracker += 1.5` mutates **in place** (updaters keep referencing it); `tracker = tracker + 1.5` replaces the object — the classic "number won't move" bug.
  - Arithmetic operators (`*`, `-`, `/`, `//`, `%`, `**`) return **new** `ValueTracker`s; `bool(tracker)` == `bool(get_value())`.
- `see`: ../zh_CN/02-Mobject通用/10-ValueTracker.md

### `ValueTracker.interpolate`
```python
def interpolate(mobject1: Mobject, mobject2: Mobject, alpha: float,
                path_func: PathFuncType = straight_path()) -> Self
```
- `ret`: `self`.
- `args`:
  - `mobject1` / `mobject2: Mobject` — start / end states (usually temporary `ValueTracker`s).
  - `alpha: float` — 0 = start, 1 = end.
  - `path_func: PathFuncType = straight_path()` — interpolation path.
- `notes`:
  - Overrides `Mobject.interpolate`; interpolates only the **point array** (`ValueTracker` has no color concept).
  - Instant function; for a continuous transition hand it to `Transform`.
- `see`: ../zh_CN/02-Mobject通用/10-ValueTracker.md

### `ComplexValueTracker`
```python
def ComplexValueTracker(value: float = 0, **kwargs: Any) -> None
```
- `ret`: new `ComplexValueTracker`. Tracks a **complex** parameter, stored internally as `[real, imag, 0]`; usable as a geometric position via `dot.move_to(ct.points)`. Overrides `get_value -> complex` and `set_value(value) -> Self`.
- `args`:
  - `value: complex | float = 0` — initial complex value.
- `notes`:
  - Inherited arithmetic operators are **unusable on 0.21** (`tracker * 1j` / `tracker + 1` raise `TypeError: float argument must be a string or a real number, not 'complex'`) — upstream behavior, same on both engines. `set_value`/`get_value`/`.animate` work; do complex math manually and write back with `set_value`.
- `errs`:
  - `TypeError: float() argument must be a string or a real number, not 'complex'` — arithmetic on a `ComplexValueTracker`.
- `see`: ../zh_CN/02-Mobject通用/10-ValueTracker.md

---

## 11. Screen frames & banner

### `ScreenRectangle`
```python
def ScreenRectangle(aspect_ratio: float = 16.0 / 9.0, height: float = 4,
                    **kwargs: Any) -> None
```
- `ret`: new `ScreenRectangle` (inherits all `Rectangle` methods).
- `args`:
  - `aspect_ratio: float = 16/9` — aspect ratio.
  - `height: float = 4` — height.
  - `**kwargs: Any` — forwarded to `Rectangle` (`color=`, `fill_opacity=`, ...).
- `notes`:
  - Own read/write property `aspect_ratio`: assignment auto-`stretch_to_fit_width` (changes width, keeps height); assignment is instant.
  - Represents a screen/layout region in **world** coordinates; it does not follow camera moves.
- `see`: ../zh_CN/02-Mobject通用/11-屏幕框架与横幅.md

### `FullScreenRectangle`
```python
def FullScreenRectangle(**kwargs: Any) -> None
```
- `ret`: new `FullScreenRectangle` filling the whole frame (height = `config.frame_height`).
- `args`:
  - `**kwargs: Any` — forwarded to `ScreenRectangle` (e.g. `fill_opacity=`, `color=`).
- `notes`:
  - Common as a mask / dim layer: `FullScreenRectangle(fill_opacity=0.7, color=BLACK)`.
  - Sized from frame dimensions (`frame_width`/`frame_height`); `remove` detaches instantly, animate `fill_opacity` for a fade.
- `see`: ../zh_CN/02-Mobject通用/11-屏幕框架与横幅.md

### `ManimBanner`
```python
def ManimBanner(dark_theme: bool = True)
def create(run_time: float = 2) -> AnimationGroup
def expand(run_time: float = 1.5, direction: str = "center") -> Succession
def scale(scale_factor: float, **kwargs: Any) -> Self
```
| arg | type | default | meaning |
| --- | --- | --- | --- |
| `dark_theme` | `bool` | `True` | `True` dark theme (light text), `False` light theme (dark text) |
| `run_time` | `float` | `2` / `1.5` | duration of `create` / `expand` |
| `direction` | `str` | `"center"` | `expand` icon-shift direction; only `"left"`/`"right"`/`"center"`, else `ValueError` |
| `scale_factor` | `float` | — | scale multiplier |

- `ret`: `create` → `AnimationGroup` (logo spin-in + letter `M` fade-in; an override of `Create`, so both `banner.create()` and `Create(banner)` work); `expand` → `Succession` (expands the icon-only logo into the full "manim" banner; the `anim` letter group is `add`ed only after expansion); `scale` → `Self` (overridden: also records `self.scale_factor` and scales the not-yet-mounted `anim` letter group so `expand()` spacing stays correct — **must** use this version).
- `notes`:
  - Common attributes: `M`, `circle`, `square`, `triangle`, `shapes`, `anim` (only after expansion), `font_color`, `scale_factor`.
  - Recommended order is `create` then `expand` (`expand` assumes the logo is on screen).
  - Do not bypass the overridden `scale` (e.g. `Mobject.scale(banner, ...)`) — expansion spacing will break.
- `errs`:
  - `ValueError: ...` — `expand(direction=...)` with anything other than `left`/`right`/`center`.
- `see`: ../zh_CN/02-Mobject通用/11-屏幕框架与横幅.md

---

## 11b. Low-frequency APIs

### `get_image` / `show` / `save_image`
```python
def get_image(camera: Camera | None = None) -> Image.Image
def show(camera: Camera | None = None) -> None
def save_image(name: str | None = None) -> None
```
- `ret`: `get_image` → PIL `Image`; `show` opens an image viewer; `save_image(name)` writes `name.png` under the current `video_dir`.
- `args`:
  - `camera: Camera | None = None` — custom camera.
  - `name: str | None = None` — filename without extension; defaults to the object name.
- `notes`:
  - **Broken upstream**: ManimCE 0.21 references an un-imported `Camera` inside these methods, so calling them raises `NameError` — same crash on RTM and vanilla. Unusable; get bitmaps from the render pipeline instead.
- `errs`:
  - `NameError: name 'Camera' is not defined` — calling `get_image`/`show`/`save_image`.
- `see`: ../zh_CN/02-Mobject通用/11b-低频其余API.md

### `sort` / `shuffle` / `invert`
```python
def sort(point_to_num_func: Callable[[Point3DLike], float] = lambda p: p[0],
         submob_func: Callable[[Mobject], Any] | None = None) -> Self
def shuffle(recursive: bool = False) -> Self
def invert(recursive: bool = False) -> Self
```
- `ret`: `self`.
- `args`:
  - `point_to_num_func: Callable[[Point3DLike], float] = lambda p: p[0]` — sort key from a point (`sort`).
  - `submob_func: Callable[[Mobject], Any] | None = None` — sort key from a submobject; **higher priority**.
  - `recursive: bool = False` — recurse into children.
- `notes`:
  - Reorder the `submobjects` list (affects paint order and `arrange` order): `sort` default by center x, `shuffle` random, `invert` reverse.
  - `shuffle` is not seeded — results differ run to run (seed `random` for reproducibility).
- `see`: ../zh_CN/02-Mobject通用/11b-低频其余API.md

### `apply_to_family`
```python
def apply_to_family(func: Callable[[Mobject], None]) -> Self
```
- `ret`: `self`.
- `args`:
  - `func: Callable[[Mobject], None]` — called once per descendant **with points**.
- `notes`:
  - Equivalent to `for m in v.family_members_with_points(): f(m)`; includes self when it has points. In-place; no new object.
  - For per-frame batch changes use an updater.
- `see`: ../zh_CN/02-Mobject通用/11b-低频其余API.md

### `get_start` / `get_end` / `get_start_and_end` / `get_pieces` / `point_from_proportion` / `proportion_from_point`
```python
def get_start() -> Point3D    def get_end() -> Point3D    def get_start_and_end() -> tuple
def get_pieces(n_pieces: float) -> Group
def point_from_proportion(alpha: float) -> Point3D
def proportion_from_point(point: Point3DLike) -> float
```
- `ret`:
  - `get_start` / `get_end` → first / last vertex; `get_start_and_end` → tuple.
  - `get_pieces(n)` → group of n pieces.
  - `point_from_proportion` / `proportion_from_point` → the generic "point along curve" entry points; the base class raises `NotImplementedError`, implemented by `Line`/`Arc`/`VMobject` etc.
- `args`:
  - `n_pieces: float` — number of pieces (`get_pieces` only).
  - `alpha: float` — path proportion 0–1 (`point_from_proportion` only).
  - `point: Point3DLike` — point to reverse-map (`proportion_from_point` only).
- `notes`:
  - `get_start`/`get_end` raise on point-less objects (e.g. empty `Group`) — check `has_points()` first.
  - `point_from_proportion` uses cumulative arc length; `proportion_from_point` requires the point to lie on the path.
- `errs`:
  - `NotImplementedError: ...` — base-class `point_from_proportion` / `proportion_from_point`.
  - `ValueError: does not lie on this curve` — `proportion_from_point` with an off-path point.
- `see`: ../zh_CN/02-Mobject通用/11b-低频其余API.md

### `get_mobject_class` / `get_vectorized_mobject_class` / `get_point_mobject_class`
```python
def get_mobject_class() -> type           # current renderer's Mobject base
def get_vectorized_mobject_class() -> type  # VMobject
def get_point_mobject_class() -> type     # PMobject
```
- `ret`: the class object for the current renderer.
- `notes`:
  - Return **class objects** (`Mobject` / `VMobject` / `PMobject`); they produce no visual output.
  - For Manim internals and plugin authors; ordinary animation scripts should not call them.
  - Import: `from real_time_manim import get_mobject_class, get_vectorized_mobject_class, get_point_mobject_class`.
- `see`: ../zh_CN/02-Mobject通用/11b-低频其余API.md
