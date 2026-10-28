# 3D

> scope: 3D primitives (`ThreeDVMobject`/`Cube`/`Prism`/`Dot3D`/`Line3D`/`Arrow3D`/`Cone`/`Cylinder`), parametric surfaces (`Surface`/`Sphere`/`Torus` + `set_fill_by_checkerboard`/`set_fill_by_value`), polyhedra (`Polyhedron`/platonic solids/`ConvexHull3D`), and the `three_d_utils` module functions. Data model is bundled ManimCE 0.21.0; RTM rasterizes it via Vulkan.
> src: `real_time_manim/manim/mobject/three_d/{three_dimensions,polyhedra,three_d_utils}.py`, `.../camera/three_d_camera.py`, `.../scene/three_d_scene.py`; RTM shading `real_time_manim/render/util.py`, `.../camera_state.py`, `.../window/paint_order.py`; human wiki `../zh_CN/06-三维/`.

## How to view 3D in RTM (read first)

- 3D mobjects only look 3D inside a `ThreeDScene` with a non-head-on camera. A `Scene` (2D `Camera`) draws them flattened; a `ThreeDScene` at the default head-on view (`phi=0`, `theta=0`) also looks flat.
- Set the view with `self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)` (instant, one frame) before `win.play(Wait(...))`. See `scene-camera.md` for `set_camera_orientation`/`move_camera`/`ThreeDCamera` args.
- **RTM wiring requirement**: `self.move_camera(...)` internally calls `self.play`. In RTM the scene's `play` is not the window's, so you must write `self.play = win.play` once in `construct()` or the camera will not move. `set_camera_orientation` does not need it.
- `win.play(Create(x))` and `.animate` builders are played directly through `win.play` and do **not** need the `self.play = win.play` wiring.
- Pin titles/labels with `self.add_fixed_in_frame_mobjects(title)` (pins position + orientation, and adds to the scene) or `self.add_fixed_orientation_mobjects(label)` (orientation only, stays in 3D). See `scene-camera.md`.
- **Surface-subclass color caveat (shared with CE)**: `Cone`/`Cylinder`/`Sphere`/`Torus`/`Surface` swallow a `color=` constructor kwarg — `Mobject.__init__` applies it, then the checkerboard faces overwrite it. Color them after construction: `obj.set_color(GREEN)`, or pass `checkerboard_colors=False, fill_color=...`.
- Shading model (RTM): a face is lit only when the active camera is a 3D camera (a camera rotation is set), `shade_in_3d` is `True` on the mobject, and the camera has a `light_source`. RTM reproduces CE's per-face shading natively; with no 3D camera or `shade_in_3d=False` every face is a flat color.
- Paint order (RTM): under `ThreeDCamera`, mobjects are re-sorted by camera-space depth (not document order); `z_index` still participates first. Explicit `MeshBatch` geometry bypasses this sort and uses the native depth buffer instead (see below).

## Primitives

### `ThreeDVMobject`
```python
def __init__(self, shade_in_3d: bool = True, **kwargs: Any) -> None:
```
- `ret`: `VMobject` variant; base class of every 3D vector face (each `Surface` face is a `ThreeDVMobject`). Rarely constructed directly.
- `args`:
  - `shade_in_3d: bool = True` — participate in 3D lighting. `False` → ordinary flat shading (all faces equal brightness, no 3D form).
  - `**kwargs: Any` — forwarded to `VMobject.__init__` (`stroke_width`, `fill_color`, …).
- `notes`:
  - This is where the "lit front / dark side" look comes from; the shading is applied by RTM only under a 3D camera (see preamble).
- `see`: ../zh_CN/06-三维/01-三维基本体.md

### `Cube`
```python
def __init__(self, side_length: float = 2, fill_opacity: float = 0.75, fill_color: ParsableManimColor = BLUE, stroke_width: float = 0, **kwargs: Any) -> None:
```
- `ret`: `Cube` (`VGroup`) — 6 `Square` faces.

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `side_length` | `float` | `2` | edge length; any positive number |
| `fill_opacity` | `float` | `0.75` | 0–1; <1 lets back faces show through |
| `fill_color` | `ParsableManimColor` | `BLUE` | any color constant or hex |
| `stroke_width` | `float` | `0` | face stroke width; any non-negative; default = no stroke |
| `**kwargs` | `Any` | — | forwarded to `VGroup`/`Mobject` |

- `notes`:
  - Faces are `Square`s with `shade_in_3d=True`; index them `cube[i]` for a single face (see 3D utils).
  - `fill_color=` **does** work here (faces are `Square`/`Polygon`, not `Surface`); contrast the Surface-subclass caveat.
- `see`: ../zh_CN/06-三维/01-三维基本体.md
- `eg`:
```python
a = Cube(side_length=2)                                       # translucent blue
b = Cube(side_length=1.2, fill_color=GREEN, fill_opacity=1.0, stroke_width=6)
```

### `Prism`
```python
def __init__(self, dimensions: Vector3DLike = [3, 2, 1], **kwargs: Any) -> None:
```
- `ret`: `Prism` (`Cube` subclass) — rectangular cuboid.
- `args`:
  - `dimensions: Vector3DLike = [3, 2, 1]` — side lengths `[x, y, z]` (z is vertical); any three positive numbers.
  - `**kwargs: Any` — same as `Cube` (`fill_color`, `fill_opacity`, `stroke_width`, …).
- `notes`: implemented as `Cube` rescaled per axis (`rescale_to_fit(value, dim, stretch=True)`); `[1, 1, 1]` equals a unit `Cube`.
- `see`: ../zh_CN/06-三维/01-三维基本体.md

### `Dot3D`
```python
def __init__(self, point: Point3D = ORIGIN, radius: float = DEFAULT_DOT_RADIUS, color: ParsableManimColor = WHITE, resolution: int | tuple[int, int] | None = (8, 8), **kwargs: Any) -> None:
```
- `ret`: `Dot3D` (`Sphere` subclass) — low-res sphere marking a point (3D analogue of `Dot`).
- `args`:
  - `point: Point3D = ORIGIN` — center; `[x, y, z]` or a direction vector like `UR`.
  - `radius: float = DEFAULT_DOT_RADIUS` — `DEFAULT_DOT_RADIUS = 0.08` (very small; enlarge for demos).
  - `color: ParsableManimColor = WHITE` — applied via `self.set_color(color)` internally (so it **does** work, unlike raw `Sphere`).
  - `resolution: int | tuple[int, int] | None = (8, 8)` — u/v samples; lower = faceted/faster.
  - `**kwargs: Any` — forwarded to `Sphere`.
- `notes`: constructor calls `super().__init__(center=point, ...)` then `self.set_color(color)`; this is the documented workaround for the Surface `color=` caveat.
- `see`: ../zh_CN/06-三维/01-三维基本体.md

### `Line3D`
```python
def __init__(self, start: Point3DLike = LEFT, end: Point3DLike = RIGHT, thickness: float = 0.02, color: ParsableManimColor | None = None, resolution: int | tuple[int, int] = 24, **kwargs: Any) -> None:
```
- `ret`: `Line3D` (`Cylinder` subclass) — a cylinder used as a 3D "line".

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `start` | `Point3DLike` or `Mobject` | `LEFT` | start point; a `Mobject` uses its center (or boundary point) |
| `end` | `Point3DLike` or `Mobject` | `RIGHT` | end point |
| `thickness` | `float` | `0.02` | cylinder radius (line thickness); any positive |
| `color` | `ParsableManimColor \| None` | `None` | `None` keeps default white (`set_color` is only called when not `None`) |
| `resolution` | `int \| tuple[int, int]` | `24` | int = sample count (becomes `(2, n)`); tuple `(u, v)` also controls checkerboard count |
| `**kwargs` | `Any` | — | forwarded to `Cylinder` (`stroke_width`, `fill_opacity`, …) |

- `ret` (methods): `get_start() -> Point3D`, `get_end() -> Point3D` return the resolved endpoints.
- `notes`:
  - RTM: `Create(line3d)` works (drawn segment-by-segment) and is played via `win.play`, so it does **not** need `self.play = win.play`.
  - Default `thickness=0.02` is thin; enlarge (e.g. `0.06`) to see it.
- `see`: ../zh_CN/06-三维/01b-三维基本体进阶.md

### `Line3D.parallel_to` / `Line3D.perpendicular_to`
```python
@classmethod
def parallel_to(cls, line: Line3D, point: Point3DLike = ORIGIN, length: float = 5, **kwargs: Any) -> Line3D:
@classmethod
def perpendicular_to(cls, line: Line3D, point: Point3DLike = ORIGIN, length: float = 5, **kwargs: Any) -> Line3D:
```
- `ret`: a new `Line3D` centered on `point`.
- `args`:
  - `line: Line3D` — reference line.
  - `point: Point3DLike = ORIGIN` — point the new line passes through.
  - `length: float = 5` — length of the new line.
  - `**kwargs: Any` — forwarded to the class constructor (e.g. `color`, `thickness`).
- `errs`:
  - `ValueError: "Could not find the perpendicular."` — `perpendicular_to` when `cross(line.vect, point - line.start)` is zero (e.g. `point` lies on `line`) → pick a point off the line.
- `see`: ../zh_CN/06-三维/01b-三维基本体进阶.md
- `eg`:
```python
line = Line3D(start=[-2, -1, 0], end=[2, 1, 1.5], thickness=0.06, color=YELLOW)
para = Line3D.parallel_to(line, point=[-1, -2.5, 0], length=4)
perp = Line3D.perpendicular_to(line, point=[2, -2, 0.75], length=3)
```

### `Arrow3D`
```python
def __init__(self, start: Point3DLike = LEFT, end: Point3DLike = RIGHT, thickness: float = 0.02, height: float = 0.3, base_radius: float = 0.08, color: ParsableManimColor = WHITE, resolution: int | tuple[int, int] = 24, **kwargs: Any) -> None:
```
- `ret`: `Arrow3D` (`Line3D` subclass) — cylindrical shaft + conical tip.

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `start` | `Point3DLike` | `LEFT` | start point |
| `end` | `Point3DLike` | `RIGHT` | end point (**arrow-tip** location) |
| `thickness` | `float` | `0.02` | shaft radius |
| `height` | `float` | `0.3` | cone height; any positive |
| `base_radius` | `float` | `0.08` | cone base radius |
| `color` | `ParsableManimColor` | `WHITE` | whole-arrow color |
| `resolution` | `int \| tuple[int, int]` | `24` | shaft samples |
| `**kwargs` | `Any` | — | forwarded to `Line3D`/`Cone` |

- `ret` (method): `get_end() -> np.ndarray` — center of `end_point` (the tip coordinate).
- `notes`: `end` is the **tip**; the cone base is placed at `end` and the apex extends `height` beyond it. To point "from A to B" pass `end=B`.
- `see`: ../zh_CN/06-三维/01b-三维基本体进阶.md
- `eg`:
```python
a = Arrow3D(start=[-2, -1, 0], end=[1.5, 0.5, 1.5])
b = Arrow3D(start=[0, -2.5, 0], end=[-1.5, -2.5, 2], color=RED,
            thickness=0.08, height=0.6, base_radius=0.18)
tip = a.get_end()
```

### `Cone`
```python
def __init__(self, base_radius: float = 1, height: float = 1, direction: Vector3DLike = Z_AXIS, show_base: bool = False, v_range: tuple[float, float] = (0, TAU), u_min: float = 0, checkerboard_colors: Iterable[ParsableManimColor] | Literal[False] = False, **kwargs: Any) -> None:
```
- `ret`: `Cone` (`Surface` subclass) — apex along `direction`.

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `base_radius` | `float` | `1` | base radius; any positive |
| `height` | `float` | `1` | base-to-apex height |
| `direction` | `Vector3DLike` | `Z_AXIS` | apex direction (cone is rotated onto it); `RIGHT` lays it sideways |
| `show_base` | `bool` | `False` | draw the base disk (`Circle`) |
| `v_range` | `tuple[float, float]` | `(0, TAU)` | azimuth range; e.g. `(0, PI)` = half cone (open) |
| `u_min` | `float` | `0` | radius at the apex; `>0` truncates the apex into a frustum |
| `checkerboard_colors` | `Iterable[...] \| False` | `False` | checkerboard colors; `False` = flat fill |
| `**kwargs` | `Any` | — | forwarded to `Surface` (`fill_color`, `resolution`, …) |

- `ret` (methods): `get_start() -> Point3D` (base center), `get_end() -> Point3D` (apex); `set_direction(direction) -> Self`, `get_direction() -> Vector3D`.
- `notes`:
  - `u_range` is set internally to `(u_min, sqrt(base_radius**2 + height**2))`; `v_range` stays the azimuth.
  - Color caveat applies: `Cone(..., color=GREEN)` is swallowed → use `.set_color(GREEN)` or `checkerboard_colors=False, fill_color=...`.
  - `direction=Z_AXIS` default; `u_min>0` leaves an open radius-`u_min` hole at the top.
- `see`: ../zh_CN/06-三维/01b-三维基本体进阶.md
- `eg`:
```python
a = Cone(base_radius=1, height=2, show_base=True)
b = Cone(base_radius=1, height=2, u_min=0.5, v_range=(0, PI))
b.set_color(GREEN)
```

### `Cylinder`
```python
def __init__(self, radius: float = 1, height: float = 2, direction: Vector3DLike = Z_AXIS, v_range: tuple[float, float] = (0, TAU), show_ends: bool = True, resolution: int | tuple[int, int] = (24, 24), **kwargs: Any) -> None:
```
- `ret`: `Cylinder` (`Surface` subclass; base class of `Line3D`) — cylinder with central axis `direction`.

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `radius` | `float` | `1` | radius |
| `height` | `float` | `2` | length along the axis |
| `direction` | `Vector3DLike` | `Z_AXIS` | central-axis direction; `RIGHT` lays it horizontal |
| `v_range` | `tuple[float, float]` | `(0, TAU)` | azimuth range; `(0, PI)` = half shell (open) |
| `show_ends` | `bool` | `True` | draw top/bottom caps (`Circle`s) |
| `resolution` | `int \| tuple[int, int]` | `(24, 24)` | sample resolution |
| `**kwargs` | `Any` | — | forwarded to `Surface` |

- `ret` (methods): `add_bases() -> Self` (adds `base_top`/`base_bottom`), `set_direction(direction) -> Self`, `get_direction() -> np.ndarray`.
- `notes`:
  - `height` is measured along `direction`; with `direction=RIGHT` it is along x, not vertical.
  - Color caveat applies (`.set_color(...)`).
- `see`: ../zh_CN/06-三维/01b-三维基本体进阶.md
- `eg`:
```python
b = Cylinder(radius=0.8, height=2.5, show_ends=False, v_range=(0, PI), direction=RIGHT)
b.set_color(RED)
```

## Surfaces

### `Surface`
```python
def __init__(self, func: Callable[[float, float], np.ndarray], u_range: tuple[float, float] = (0, 1), v_range: tuple[float, float] = (0, 1), resolution: int | Sequence[int] = 32, surface_piece_config: dict = {}, fill_color: ParsableManimColor = BLUE_D, fill_opacity: float = 1.0, checkerboard_colors: Iterable[ParsableManimColor] | Literal[False] = [BLUE_D, BLUE_E], stroke_color: ParsableManimColor = LIGHT_GREY, stroke_width: float = 0.5, should_make_jagged: bool = False, pre_function_handle_to_anchor_scale_factor: float = 0.00001, **kwargs: Any) -> None:
```
- `ret`: `Surface` (`VGroup`) — checkerboard-tiled parametric surface.

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `func` | `Callable[[float, float], np.ndarray]` | required | `func(u, v) -> (x, y, z)`; with axes usually `lambda u, v: axes.c2p(...)` |
| `u_range` | `tuple[float, float]` | `(0, 1)` | u interval |
| `v_range` | `tuple[float, float]` | `(0, 1)` | v interval |
| `resolution` | `int \| Sequence[int]` | `32` | int sets both; `(u_res, v_res)` sets each. **Cost = `u_res × v_res` faces**; avoid large values |
| `surface_piece_config` | `dict` | `{}` | extra per-face config |
| `fill_color` | `ParsableManimColor` | `BLUE_D` | face fill (overridden by `checkerboard_colors`) |
| `fill_opacity` | `float` | `1.0` | opacity |
| `checkerboard_colors` | `Iterable[...] \| False` | `[BLUE_D, BLUE_E]` | alternating colors; `False` disables checkerboard |
| `stroke_color` | `ParsableManimColor` | `LIGHT_GREY` | per-face stroke color |
| `stroke_width` | `float` | `0.5` | stroke width |
| `should_make_jagged` | `bool` | `False` | switch Bézier anchors from smooth to jagged |
| `pre_function_handle_to_anchor_scale_factor` | `float` | `0.00001` | anchor scale factor (leave alone) |
| `**kwargs` | `Any` | — | forwarded to `VGroup`; **`color=` is swallowed** (see notes) |

- `ret` (method): `func(u, v) -> np.ndarray` returns the stored function's value.
- `notes`:
  - Face count is `u_res × v_res`; the first render-cost lever. Example surfaces at `(16, 8)` are enough to read structure; default `32` = 1024 faces is noticeably slower.
  - **`color=` does not work** (shared with CE): `Mobject.__init__` applies `color=`, then the checkerboard faces overwrite it. Use `set_fill_by_checkerboard(...)` / `.set_fill(...)` / `.set_color(...)`.
  - Each face is a `ThreeDVMobject` with `u_index`/`v_index`/`u1`/`u2`/`v1`/`v2` attributes; `self.list_of_faces` holds them.
- `see`: ../zh_CN/06-三维/02-三维表面.md
- `eg`:
```python
import numpy as np
surf = Surface(lambda u, v: [v * np.cos(u), v * np.sin(u), u * 0.5],
               u_range=(0, TAU), v_range=(0.3, 1.8), resolution=(16, 8))
```

### `Surface.set_fill_by_checkerboard`
```python
def set_fill_by_checkerboard(self, *colors: ParsableManimColor, opacity: float | None = None) -> Self:
```
- `ret`: `Self` (the same `Surface`, for chaining).
- `args`:
  - `*colors: ParsableManimColor` — 2+ colors; face `(u_index + v_index) % len(colors)` picks the color.
  - `opacity: float | None = None` — `None` leaves each face's opacity unchanged.
- `notes`: recolors in place; the standard way to color a `Surface` (the `color=` kwarg is swallowed).
- `see`: ../zh_CN/06-三维/02-三维表面.md
- `eg`:
```python
surf.set_fill_by_checkerboard([GREEN, YELLOW], opacity=0.85)
```

### `Surface.set_fill_by_value`
```python
def set_fill_by_value(self, axes: ThreeDAxes, colorscale: Iterable[ParsableManimColor] | Iterable[tuple[ParsableManimColor, float]] | None = None, axis: int = 2, **kwargs: Any) -> Self:
```
- `ret`: `Self` (the same `Surface`, for chaining).
- `args`:
  - `axes: ThreeDAxes` — required; maps face points back to data coordinates.
  - `colorscale: Iterable[color] \| Iterable[(color, pivot)] \| None = None` — colors low→high; tuple form sets explicit pivots. `None` triggers a warning and no-op.
  - `axis: int = 2` — which axis value drives the color: `0=x`, `1=y`, `2=z`.
  - `**kwargs: Any` — `colors` is an alias for `colorscale`; passing both (or extra keys) raises.
- `errs`:
  - `ValueError: "Unsupported keyword argument(s): <keys>"` — extra kwargs passed alongside `colors` → pass only one of `colorscale`/`colors`.
  - (warning, not error) `"The value passed to the colorscale keyword argument was None, the surface fill color has not been changed"` — `colorscale=None` → provide a colorscale.
- `notes`: colors by data value; needs a `ThreeDAxes` to invert the projection (advanced usage, not demoed in the human wiki).
- `see`: ../zh_CN/06-三维/02-三维表面.md

### `Sphere`
```python
def __init__(self, center: Point3DLike = ORIGIN, radius: float = 1, resolution: int | Sequence[int] | None = None, u_range: tuple[float, float] = (0, TAU), v_range: tuple[float, float] = (0, PI), **kwargs: Any) -> None:
```
- `ret`: `Sphere` (`Surface` subclass) — standard sphere.

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `center` | `Point3DLike` | `ORIGIN` | center |
| `radius` | `float` | `1` | radius |
| `resolution` | `int \| Sequence[int] \| None` | `None` | `None` → `(24, 12)` (cairo branch; RTM uses this renderer branch). Avoid large values |
| `u_range` | `tuple[float, float]` | `(0, TAU)` | azimuth range |
| `v_range` | `tuple[float, float]` | `(0, PI)` | polar range; `0` = north pole. `(0, PI/2)` = upper hemisphere |
| `**kwargs` | `Any` | — | forwarded to `Surface`; **`color=` does not work** → `.set_color(...)` |

- `notes`:
  - `v_range=(0, PI/2)` = upper hemisphere, `(PI/2, PI)` = lower hemisphere.
  - `Dot3D` colors itself with `set_color` internally, bypassing the `color=` caveat.
- `see`: ../zh_CN/06-三维/02-三维表面.md
- `eg`:
```python
full = Sphere(radius=1, resolution=(24, 12))
half = Sphere(radius=1, resolution=(24, 12), v_range=(0, PI / 2))
half.set_color(RED)
```

### `Torus`
```python
def __init__(self, major_radius: float = 3, minor_radius: float = 1, u_range: tuple[float, float] = (0, TAU), v_range: tuple[float, float] = (0, TAU), resolution: int | tuple[int, int] | None = None, **kwargs: Any) -> None:
```
- `ret`: `Torus` (`Surface` subclass) — ring (donut).

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `major_radius` | `float` | `3` | ring radius (default is wider than the frame) |
| `minor_radius` | `float` | `1` | tube radius |
| `u_range` | `tuple[float, float]` | `(0, TAU)` | angle around the ring (truncate → bent tube segment) |
| `v_range` | `tuple[float, float]` | `(0, TAU)` | angle around the tube (`(0, PI)` → half tube, sliced open) |
| `resolution` | `int \| tuple[int, int] \| None` | `None` | `None` → `(24, 24)` (cairo branch). Avoid large values |
| `**kwargs` | `Any` | — | forwarded to `Surface`; **`color=` does not work** → `.set_color(...)` |

- `notes`: `u` = around the ring, `v` = around the tube; do not swap. Stored as `self.R` / `self.r`.
- `see`: ../zh_CN/06-三维/02-三维表面.md

## Depth mesh (`MeshBatch`)

`real_time_manim.mesh.MeshBatch` — explicit depth-tested quads, exported from
`real_time_manim`. Use it when painter order cannot resolve self-occlusion
(cells of one surface, a rim crossing the surface, folded sheets).

```python
class MeshBatch:
    def __init__(self)
    def append(self, quads, colors) -> Self
    def build_vertices(self, viewport, width, height) -> tuple[int, ctypes pointer] | None
```

- `quads`: `(Q, 4, 3)` float, four corners in world coordinates.
- `colors`: `(Q, 4, 4)` float, RGBA per corner in 0–1.
- Attach with `win.set_mesh(mesh)`; detach with `win.clear_mesh()` or
  `win.set_mesh(None)`. `sync()` calls `build_vertices` once per frame and
  hands the result to native `AddMesh(vertex_count, x,y,z,rgba)`.
- Native side: depth-tested mesh pipeline over a `D32_SFLOAT` attachment; the
  mesh is recorded **before** the painter primitives, so 2D overlays stay on
  top regardless of 3D depth.
- Limits: quads only, `MAX_MESH_VERTS = 262144` vertices (~43690 quads), one
  batch per frame (`AddMesh` overwrites, it does not append), no per-pixel
  transparency sort, CPU re-projection every frame.

### Automatic depth (`RTM_AUTO_DEPTH=1`)

Opt-in prototype (2.0.3) that routes eligible `Surface` roots through the same
depth buffer with no scene-code change.

- Eligibility is checked per frame: 3D camera, top-level `Surface`, every face
  opaque and `shade_in_3d=False`, stroke invisible or equal to fill, no other
  lit 3D geometry, no manual `win._mesh`.
- One failed condition falls back to the painter for the **whole frame**;
  partial routing would break cross-object ordering.
- It fixes occlusion only. Per-face `set_fill` / `set_stroke` in the scene still
  runs in Python; a 3888-face surface updated per frame stayed slow in
  measurement. Use batched array writes for speed.
- `RTM_AUTO_DEPTH_DEBUG=1` prints `[auto-depth] roots=... verts=...`.
- Windows tested; macOS `AddMesh` exists but was not built/tested.

## Polyhedra

All polyhedra subclass `Polyhedron` (`VGroup`): `.faces` is a `VGroup` of `Polygon`s, `.graph` is a `Graph` whose vertices are `Dot3D`. An updater links them — moving `polyhedron.graph[v]` deforms the solid.

### `Polyhedron`
```python
def __init__(self, vertex_coords: Point3DLike_Array, faces_list: list[list[int]], faces_config: dict[str, str | int | float | bool] = {}, graph_config: dict[str, Any] = {}) -> None:
```
- `ret`: `Polyhedron` (`VGroup`) — convex polyhedron from a vertex table + face-index table (OFF-style).

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `vertex_coords` | `Point3DLike_Array` | required | vertex coordinates; list index = vertex number |
| `faces_list` | `list[list[int]]` | required | each face = vertex indices, auto-closed first↔last |
| `faces_config` | `dict` | `{}` | `Polygon` params; defaults injected: `{"fill_opacity": 0.5, "shade_in_3d": True}` |
| `graph_config` | `dict` | `{}` | `Graph` params; defaults injected: `{"vertex_type": Dot3D, "edge_config": {"stroke_opacity": 0}}` |

- `ret` (attributes): `.faces` (`VGroup` of `Polygon`), `.graph` (`Graph`), `.layout` (`dict[int, coords]`), `.edges` (`list[tuple[int, int]]`).
- `notes`:
  - `faces_list` indices refer to `vertex_coords` order; wrong indices give self-intersecting faces.
  - `fill_color` goes through `faces_config` (a `Polygon` param), **not** the Surface `set_color` path.
  - Edge strokes are off by default (`stroke_opacity: 0`), so only vertices and faces show.
  - RTM: `.animate` builders (e.g. `pyramid.graph[4].animate.shift(...)`) are played via `win.play` and do not need `self.play = win.play`.
- `see`: ../zh_CN/06-三维/03-多面体.md
- `eg`:
```python
pyramid = Polyhedron(
    vertex_coords=[[1, 1, 0], [1, -1, 0], [-1, -1, 0], [-1, 1, 0], [0, 0, 2]],
    faces_list=[[0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4], [0, 1, 2, 3]],
    faces_config={"fill_opacity": 0.6, "fill_color": BLUE})
pyramid.faces[2].set_color(YELLOW)
pyramid.graph[4].set_color(RED)
```

### `Tetrahedron` / `Octahedron` / `Icosahedron` / `Dodecahedron`
```python
def __init__(self, edge_length: float = 1, **kwargs: Any) -> None:
```
- `ret`: a `Polyhedron` preset — 4 / 8 / 20 / 12 faces respectively. Same `.graph` / `.faces` access and vertex deformation.
- `args`:
  - `edge_length: float = 1` — edge length.
  - `**kwargs: Any` — forwarded to `Polyhedron` (`faces_config`, `graph_config`, …).
- `notes`: at equal `edge_length` the four solids differ a lot in visual size (different vertex counts); the wiki sample decreases `edge_length` to balance them.
- `see`: ../zh_CN/06-三维/03-多面体.md
- `eg`:
```python
solids = VGroup(Tetrahedron(edge_length=1), Octahedron(edge_length=1),
                Icosahedron(edge_length=0.9), Dodecahedron(edge_length=0.7)).arrange(RIGHT, buff=1.2)
solids[1].graph[0].set_color(RED)
solids[1].faces[2].set_color(YELLOW)
```

### `ConvexHull3D`
```python
def __init__(self, *points: Point3D, tolerance: float = 1e-5, **kwargs: Any) -> None:
```
- `ret`: `ConvexHull3D` (`Polyhedron` subclass) — convex hull of a point set (vertices + faces + edges computed).
- `args`:
  - `*points: Point3D` — the points (**positional args**, not a list): `ConvexHull3D(*pts)`.
  - `tolerance: float = 1e-5` — quickhull numeric tolerance.
  - `**kwargs: Any` — forwarded to `Polyhedron` (`faces_config`, `graph_config`, …).
- `notes`: with fewer than 4 points, or all points coplanar, the hull degenerates (no volume). Leave `tolerance` at default unless the point set is numerically ill-conditioned.
- `see`: ../zh_CN/06-三维/03-多面体.md
- `eg`:
```python
pts = [[1.9, 0.4, -1.5], [-0.9, 1.2, 0.6], [0.4, 0.4, -1.8],
       [-1.5, -0.8, -0.5], [0.8, -1.4, 0.9], [-0.2, 0.1, 2.0]]
hull = ConvexHull3D(*pts, faces_config={"fill_opacity": 0.4, "fill_color": GREEN})
dots = VGroup(*[Dot3D(p, radius=0.08, color=RED) for p in pts])
```

## 3D utility functions (`three_d_utils`)

Pure computations over a **single 3D face** (`VMobject`). Passing a `VGroup` shell (`Cube`, `Sphere`, …) degenerates: corners fall back to `ORIGIN`, normals fall back to `UP`. Take a sub-face first (`cube[i]`). All importable from `real_time_manim` (or `manim`).

### `get_3d_vmob_start_corner` / `get_3d_vmob_end_corner`
```python
def get_3d_vmob_start_corner(vmob: VMobject) -> Point3D:
def get_3d_vmob_end_corner(vmob: VMobject) -> Point3D:
```
- `ret`: `Point3D` (`np.ndarray`) — start corner (`points[0]`) / end corner (`points[((len(points)-1)//6)*3]`).
- `args`: `vmob: VMobject` — one 3D face, not a `VGroup` shell.
- `notes`: empty `vmob` → returns `ORIGIN`.
- `see`: ../zh_CN/06-三维/04-三维工具函数.md

### `get_3d_vmob_gradient_start_and_end_points`
```python
def get_3d_vmob_gradient_start_and_end_points(vmob: VMobject) -> tuple[Point3D, Point3D]:
```
- `ret`: `(Point3D, Point3D)` — equals `(get_3d_vmob_start_corner(vmob), get_3d_vmob_end_corner(vmob))`; convenience entry for start↔end gradient shading (`set_stroke`/`set_fill`).
- `notes`: the two points are identical to the start/end corners (`g0 == p0`).
- `see`: ../zh_CN/06-三维/04-三维工具函数.md

### `get_3d_vmob_start_corner_index` / `get_3d_vmob_end_corner_index`
```python
def get_3d_vmob_start_corner_index(vmob: VMobject) -> Literal[0]:
def get_3d_vmob_end_corner_index(vmob: VMobject) -> int:
```
- `ret`: `int` — start index is **always `0`**; end index is `((len(vmob.points) - 1) // 6) * 3`.
- `notes`: the end index is an index into the `points` array, **not** a face/vertex number — do not use it as `faces[...]`. `get_3d_vmob_start_corner_index` has no inputs to vary (always `0`).
- `see`: ../zh_CN/06-三维/04-三维工具函数.md

### `get_3d_vmob_unit_normal` / `get_3d_vmob_start_corner_unit_normal` / `get_3d_vmob_end_corner_unit_normal`
```python
def get_3d_vmob_unit_normal(vmob: VMobject, point_index: int) -> Vector3D:
def get_3d_vmob_start_corner_unit_normal(vmob: VMobject) -> Vector3D:
def get_3d_vmob_end_corner_unit_normal(vmob: VMobject) -> Vector3D:
```
- `ret`: `Vector3D` — unit normal at the given anchor (`np.ndarray`).
- `args`:
  - `vmob: VMobject` — one 3D face.
  - `point_index: int` — `get_3d_vmob_unit_normal` only: index into the `points` array (same array as `face.points[i]`).
- `notes`:
  - The `start`/`end` wrappers are `get_3d_vmob_unit_normal` at index `0` / end-corner index.
  - Normal comes from the face's 3D shading normal; falls back to `UP` when `vmob` has ≤2 anchors or the normal is zero-length.
  - Out-of-range or odd (Bézier-control) indices may give geometrically meaningless normals; a planar face has a nearly constant normal at start/mid/end (use a curved surface to see variation).
- `see`: ../zh_CN/06-三维/04-三维工具函数.md
- `eg`:
```python
face = Cube(side_length=2)[1]
end_idx = get_3d_vmob_end_corner_index(face)
for i in [0, end_idx // 2, end_idx]:
    p = face.points[i]
    n = get_3d_vmob_unit_normal(face, i)
    arrows.add(Arrow3D(p, p + 0.7 * n, color=GREEN, thickness=0.05))
```

## Cross-links

- `see`: ../zh_CN/06-三维/README.md · ../zh_CN/06-三维/01-三维基本体.md · ../zh_CN/06-三维/01b-三维基本体进阶.md · ../zh_CN/06-三维/02-三维表面.md · ../zh_CN/06-三维/03-多面体.md · ../zh_CN/06-三维/04-三维工具函数.md
- Related agent files: `scene-camera.md` (`ThreeDScene`, `ThreeDCamera`, `set_camera_orientation`/`move_camera`, fixed-in-frame), `coords-charts.md` (`ThreeDAxes`), `runtime.md` (`MLWindow`, `win.play`, recording).
